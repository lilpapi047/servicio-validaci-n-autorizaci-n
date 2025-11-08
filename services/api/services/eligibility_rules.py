from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import or_
from sqlalchemy.sql import func
from .. import models

def compute_age_years(dob: date, on_day: date) -> int:
    years = on_day.year - dob.year
    if (on_day.month, on_day.day) < (dob.month, dob.day):
        years -= 1
    return years

def user_is_banned(db: Session, user_id: int) -> bool:
    # Baneo
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

def evaluate_eligibility(
    db: Session,
    user: models.User,
    match: models.Match,
    min_age_years: int,
) -> tuple[bool, list[str]]:
    """Return (ok, reasons)."""
    reasons: list[str] = []

    # Verificar Email
    if not bool(getattr(user, "is_verified", False)):
        reasons.append("Email not verified")

    # Verificar Baneo
    if user_is_banned(db, user.id):
        reasons.append("User is banned from attending")

    # Duplicidad de seleccion
    if user_has_open_raffle(db, user.id, match.id):
        reasons.append("User already has a pending/claimed raffle assignment for this match")

    # Verificar Edad
    kickoff_day = match.kickoff_at.date()
    if user.date_of_birth is None:
        reasons.append("Missing date of birth")
    else:
        if compute_age_years(user.date_of_birth, kickoff_day) < int(min_age_years):
            reasons.append(f"User must be at least {min_age_years} on match day")

    return (len(reasons) == 0, reasons)
