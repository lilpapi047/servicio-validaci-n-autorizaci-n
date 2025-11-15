from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Response
from sqlalchemy.orm import Session
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, AnyUrl
from datetime import datetime, timedelta, timezone
import os, secrets

from ..database import get_db
from .. import models
from ..notifications import send_email_mailtrap
from ..services.eligibility_rules import evaluate_eligibility 

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

@router.post("/expire-past-due")
def force_expire(db: Session = Depends(get_db)):

    count = expire_past_due(db)
    return {"expired": count}