from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Response
from sqlalchemy.orm import Session
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, AnyUrl
from datetime import datetime, timedelta, timezone
import os, secrets, random

from ..database import get_db
from .. import models
from ..notifications import send_email_mailtrap
from ..eligibility_rules import evaluate_eligibility 
from .criteria import require_admin

router = APIRouter()

PURCHASE_BASE_URL = os.getenv("PURCHASE_BASE_URL", "https://tickets.example.com/checkout")  # <-- CAMBIAR EN SPRINT2
ASSIGNMENT_TTL_HOURS = int(os.getenv("ASSIGNMENT_TTL_HOURS", "72"))
MIN_ELIGIBILITY_AGE = int(os.getenv("MIN_ELIGIBILITY_AGE", "18"))


class AssignmentOut(BaseModel):
    id: int
    user_id: int
    match_id: int
    status: str
    expires_at: datetime
    purchase_link: AnyUrl

class RaffleRunRequest(BaseModel):
    match_id: int
    num_winners: int = 100

class RaffleRunResult(BaseModel):
    match_id: int
    total_eligible: int
    winners: list[int]

def expire_past_due(db: Session) -> int:

    now = datetime.now(timezone.utc)
    stmt = (
        update(models.RaffleAssignment)
        .where(models.RaffleAssignment.status == "pending")
        .where(models.RaffleAssignment.expires_at < now)
        .values(status="expired")
    )
    res = db.execute(stmt)
    db.commit()
    return res.rowcount or 0

def enqueue_email(tasks: BackgroundTasks, to: str, subject: str, body: str):
    
    def _send():
        try:
            send_email_mailtrap(to, subject, body)
        except Exception as e:
            print(f"Email send failed for {to}: {e}")
    tasks.add_task(_send)

@router.get("/ping")
def ping():
    return {"raffle": "ready"}

@router.post("/assign", status_code=201, response_model=AssignmentOut)
def create_assignment(
    user_id: int,
    match_id: int,
    tasks: BackgroundTasks,
    response: Response,
    db: Session = Depends(get_db),
):
    
    expire_past_due(db)

    # Validacion
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(404, "User not found")

    match = db.get(models.Match, match_id)
    if not match:
        raise HTTPException(404, "Match not found")
    
    
    ok, reasons = evaluate_eligibility(db, user, match, MIN_ELIGIBILITY_AGE)
    if not ok:
        raise HTTPException(status_code=400, detail={"eligible": False, "reasons": reasons})

    # Generar rifa
    token = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    expires = now + timedelta(hours=ASSIGNMENT_TTL_HOURS)

    assignment = models.RaffleAssignment(
        user_id=user_id,
        match_id=match_id,
        token=token,
        status="pending",
        created_at=now,
        expires_at=expires,
    )

    try:
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
    except IntegrityError:
        db.rollback()
        # Multiple peticion para rifa
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "User already has an open/claimed assignment for this match",
        )

    # Notificar con link de compra
    purchase_link = f"{PURCHASE_BASE_URL}?token={token}"
    if user.email:
        subject = "¡Fuiste seleccionado para comprar tu boleto!"
        body = (
            f"Hola,\n\nHas sido seleccionado en la rifa.\n"
            f"Tienes {ASSIGNMENT_TTL_HOURS} horas para completar tu compra:\n{purchase_link}\n\n"
            f"Después de ese tiempo, la oportunidad expirará automáticamente."
        )
        enqueue_email(tasks, user.email, subject, body)

    
    response.headers["Location"] = purchase_link

    return AssignmentOut(
        id=assignment.id,
        user_id=assignment.user_id,
        match_id=assignment.match_id,
        status=assignment.status,
        expires_at=assignment.expires_at,
        purchase_link=purchase_link,
    )

@router.post(
    "/run",
    response_model=RaffleRunResult,
    dependencies=[Depends(require_admin)],
)
def run_raffle(
    body: RaffleRunRequest,
    tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    # 1) Marcar como expiradas las asignaciones vencidas
    expire_past_due(db)

    # 2) Validar que el partido exista
    match = db.get(models.Match, body.match_id)
    if not match:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Match not found")

    # 3) Tomar todos los usuarios candidatos (Posible agregar mas filtro)
    users = db.query(models.User).all()

    eligible_users: list[models.User] = []
    for user in users:
        ok, reasons = evaluate_eligibility(db, user, match, MIN_ELIGIBILITY_AGE)
        if ok:
            eligible_users.append(user)

    if not eligible_users:
        return RaffleRunResult(
            match_id=match.id,
            total_eligible=0,
            winners=[],
        )

    # 4) Escoger ganadores al azar
    if body.num_winners >= len(eligible_users):
        winners = eligible_users
    else:
        winners = random.sample(eligible_users, body.num_winners)

    # 5) Crear asignaciones sólo para los ganadores
    now = datetime.now(timezone.utc)
    expires = now + timedelta(hours=ASSIGNMENT_TTL_HOURS)

    winner_ids: list[int] = []

    for user in winners:
        token = secrets.token_urlsafe(32)
        assignment = models.RaffleAssignment(
            user_id=user.id,
            match_id=match.id,
            token=token,
            status="pending",
            created_at=now,
            expires_at=expires,
        )
        db.add(assignment)
        winner_ids.append(user.id)

        # Email con link de compra
        if user.email:
            purchase_link = f"{PURCHASE_BASE_URL}?token={token}"
            subject = "¡Fuiste seleccionado para comprar tu boleto!"
            body_email = (
                "Hola,\n\nHas sido seleccionado en la rifa.\n"
                f"Tienes {ASSIGNMENT_TTL_HOURS} horas para completar tu compra:\n{purchase_link}\n\n"
                "Después de ese tiempo, la oportunidad expirará automáticamente."
            )
            enqueue_email(tasks, user.email, subject, body_email)

# --- Registrar en audit_log que se corrió la rifa ---
    actor = "admin_token"  # o algo más específico si luego identificas admins
    action = "raffle_run"
    entity = "match"
    entity_id = str(match.id)

    log_entry = models.AuditLog(
        actor=actor,
        action=action,
        entity=entity,
        entity_id=entity_id,
    )
    db.add(log_entry)
    db.commit()

    return RaffleRunResult(
        match_id=match.id,
        total_eligible=len(eligible_users),
        winners=winner_ids,
    )

@router.post("/expire-past-due")
def force_expire(db: Session = Depends(get_db)):

    count = expire_past_due(db)
    return {"expired": count}

class RaffleAuditEntry(BaseModel):
    id: int
    actor: str
    action: str
    entity: str
    entity_id: str
    at: datetime


@router.get(
    "/audit",
    response_model=list[RaffleAuditEntry],
    dependencies=[Depends(require_admin)],
)
def get_raffle_audit(
    limit: int = 50,
    db: Session = Depends(get_db),
):
    rows = (
        db.query(models.AuditLog)
        .filter(models.AuditLog.action == "raffle_run")
        .order_by(models.AuditLog.at.desc())
        .limit(limit)
        .all()
    )
    return rows