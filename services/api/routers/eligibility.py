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
    # integer age on date `on`
    years = on.year - dob.year
    if (on.month, on.day) < (dob.month, dob.day):
        years -= 1
    return years

def user_is_banned(db: Session, user_id: int) -> bool:
    # active = TRUE  AND  (until IS NULL OR until > now())
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
    # Load user & match
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    match = db.get(models.Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    reasons: list[str] = []

    # Email verified
    if not user.is_verified:
        reasons.append("Email not verified")

    # Banned?
    if user_is_banned(db, user_id):
        reasons.append("User is banned from attending")

    # Already selected for this match?
    if user_has_open_raffle(db, user_id, match_id):
        reasons.append("User already has a pending/claimed raffle assignment for this match")

    # Age ≥ 18 on the match day
    if user.date_of_birth is None:
        reasons.append("Missing date of birth")
    else:
        kickoff_day = match.kickoff_at.date()
        age = compute_age_years(user.date_of_birth, kickoff_day)
        if age < 18:
            reasons.append("User must be at least 18 on match day")

    return EligibilityResponse(eligible=(len(reasons) == 0), reasons=reasons)