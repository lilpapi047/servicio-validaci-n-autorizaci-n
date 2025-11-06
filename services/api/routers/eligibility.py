from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import date
from ..database import get_db
from .. import models
from sqlalchemy import or_
from sqlalchemy.sql import func

router = APIRouter()

class EligibilityResponse(BaseModel):
    eligible: bool
    reasons: list[str]

def compute_age_years(dob: date, on: date) -> int:
    years = on.year - dob.year
    if (on.month, on.day) < (dob.month, dob.day):
        years -= 1
    return years

def user_is_banned(db: Session, user_id: int) -> bool:

    return db.query(models.AttendanceBan).filter(
        models.AttendanceBan.user_id == user_id,
        models.AttendanceBan.active.is_(True),
        or_(models.AttendanceBan.until.is_(None),
            models.AttendanceBan.until > func.now())
    ).first() is not None

def user_has_open_raffle(db: Session, user_id: int, match_id: int) -> bool:
    return db.query(models.RaffleAssignment).filter(
        models.RaffleAssignment.user_id == user_id,
        models.RaffleAssignment.match_id == match_id,
        models.RaffleAssignment.status.in_(["pending", "claimed"])
    ).first() is not None

@router.get("/eligibility", response_model=EligibilityResponse)
def check_eligibility(
    user_id: int = Query(..., ge=1),
    match_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
):
    # Cargar Usuario (required)
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Intentar obtener un Match, pero evitar un 404 si no se encuentra
    match = db.get(models.Match, match_id)
    kickoff_day: date = match.kickoff_at.date() if match else date.today()

    reasons: list[str] = []

    # El email fue verificado
    if not user.is_verified:
        reasons.append("Email not verified")

    # Revisar Baneo
    if user_is_banned(db, user_id):
        reasons.append("User is banned from attending")

    # Revisar si ya fue seleccionado
    if user_has_open_raffle(db, user_id, match_id):
        reasons.append("User already has a pending/claimed raffle assignment for this match")

    # Age ≥ 18 
    if user.date_of_birth is None:
        reasons.append("Missing date of birth")
    else:
        if compute_age_years(user.date_of_birth, kickoff_day) < 18:
            reasons.append("User must be at least 18 on match day")

    return EligibilityResponse(eligible=(len(reasons) == 0), reasons=reasons)
