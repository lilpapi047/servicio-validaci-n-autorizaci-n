from datetime import date
from sqlalchemy.orm import Session
from app import models

def compute_age_years(dob: date, on_day: date) -> int:
    y = on_day.year - dob.year
    if (on_day.month, on_day.day) < (dob.month, dob.day):
        y -= 1
    return y

def user_is_banned(db: Session, user_id: int) -> bool:
    # adjust model/table names to your schema
    q = (
        db.query(models.Ban)
        .filter(models.Ban.user_id == user_id, models.Ban.active.is_(True))
    )
    return db.query(q.exists()).scalar()

def user_has_open_raffle(db: Session, user_id: int, match_id: int) -> bool:
    q = (
        db.query(models.RaffleAssignment)
        .filter(models.RaffleAssignment.user_id == user_id,
                models.RaffleAssignment.match_id == match_id,
                models.RaffleAssignment.status.in_(["pending", "claimed"]))
    )
    return db.query(q.exists()).scalar()

def evaluate_eligibility(
    db: Session,
    user: models.User,
    match: models.Match,
    min_age_years: int = 18,
) -> tuple[bool, list[str]]:
    reasons: list[str] = []

    # 1) email verified (be defensive with field name)
    is_verified = getattr(user, "is_verified", None)
    if is_verified is None:
        # if your model uses another flag name, try it too
        is_verified = getattr(user, "email_verified", False)
    if not bool(is_verified):
        reasons.append("Email not verified")

    # 2) banned?
    if user_is_banned(db, user.id):
        reasons.append("User is banned from attending")

    # 3) open assignment for this match?
    if user_has_open_raffle(db, user.id, match.id):
        reasons.append("User already has a pending/claimed raffle assignment for this match")

    # 4) age
    kickoff_day = match.kickoff_at.date()
    if user.date_of_birth is None:
        reasons.append("Missing date of birth")
    else:
        if compute_age_years(user.date_of_birth, kickoff_day) < int(min_age_years):
            reasons.append(f"User must be at least {min_age_years} on match day")

    return (len(reasons) == 0, reasons)
