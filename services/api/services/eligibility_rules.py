from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import or_
from sqlalchemy.sql import func
import os
from .. import models

def compute_age_years(dob: date, on_day: date) -> int:
    years = on_day.year - dob.year
    if (on_day.month, on_day.day) < (dob.month, dob.day):
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

#DBDC

DEFAULT_MIN_AGE = int(os.getenv("MIN_ELIGIBILITY_AGE", "18"))

_CRIT_KEYS = {
    "email_verified",
    "not_banned",
    "no_open_raffle",
    "min_age",
}

def _load_active_criteria(db: Session) -> dict[str, models.EligibilityCriterion]:
    """
    Returns a dict of active criteria keyed by 'key'.
    If the table doesn't exist yet, returns an empty dict.
    """
    try:
        rows = (
            db.query(models.EligibilityCriterion)
            .filter(models.EligibilityCriterion.active.is_(True))
            .all()
        )
        return {r.key: r for r in rows if r.key in _CRIT_KEYS}
    except Exception:
        # No hay tabla → fallback a defaults
        return {}

def _resolve_min_age(crit: dict[str, "models.EligibilityCriterion"], fallback: int) -> int:
    row = crit.get("min_age")
    if row and row.value_int is not None:
        return int(row.value_int)
    return int(fallback)


def evaluate_eligibility(
    db: Session,
    user: models.User,
    match: models.Match,
    min_age_years: int | None = None,
) -> tuple[bool, list[str]]:
    """
    Return (ok, reasons).
    If eligibility_criterion exists, only active criteria are enforced and min_age comes from DB.
    If not, we fall back to classic hardcoded checks and provided/env min_age.
    """
    reasons: list[str] = []

    # Se cargan los criterios activos
    crit = _load_active_criteria(db)
    using_db_criteria = bool(crit)

    
    effective_min_age = _resolve_min_age(crit, min_age_years or DEFAULT_MIN_AGE)

    # Verificar Email
    if (using_db_criteria and "email_verified" in crit) or (not using_db_criteria):
        if not bool(getattr(user, "is_verified", False)):
            reasons.append("Email not verified")

    # Verifica Baneo
    if (using_db_criteria and "not_banned" in crit) or (not using_db_criteria):
        if user_is_banned(db, user.id):
            reasons.append("User is banned from attending")

    # Rifa pendiente o ya aceptado
    if (using_db_criteria and "no_open_raffle" in crit) or (not using_db_criteria):
        if user_has_open_raffle(db, user.id, match.id):
            reasons.append("User already has a pending/claimed raffle assignment for this match")

    # Edad minima
    if (using_db_criteria and "min_age" in crit) or (not using_db_criteria):
        kickoff_day = match.kickoff_at.date()
        if user.date_of_birth is None:
            reasons.append("Missing date of birth")
        else:
            if compute_age_years(user.date_of_birth, kickoff_day) < effective_min_age:
                reasons.append(f"User must be at least {effective_min_age} on match day")

    return (len(reasons) == 0, reasons)
