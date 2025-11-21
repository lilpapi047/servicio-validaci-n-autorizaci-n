from datetime import date, datetime, timezone
from sqlalchemy.orm import Session
from . import models


def compute_age_years(dob: date, on_day: date) -> int:
    y = on_day.year - dob.year
    if (on_day.month, on_day.day) < (dob.month, dob.day):
        y -= 1
    return y


def user_is_banned(db: Session, user_id: int) -> bool:
    """
    True si el usuario tiene un baneo de asistencia activo.
    """
    q = (
        db.query(models.AttendanceBan)
        .filter(
            models.AttendanceBan.user_id == user_id,
            models.AttendanceBan.active.is_(True),
        )
    )
    return db.query(q.exists()).scalar()


def user_has_open_raffle(db: Session, user_id: int, match_id: int) -> bool:
    """
    True si el usuario ya tiene una asignación de rifa pendiente o reclamada
    para este partido y todavía no ha expirado.
    """
    now = datetime.now(timezone.utc)
    q = (
        db.query(models.RaffleAssignment)
        .filter(
            models.RaffleAssignment.user_id == user_id,
            models.RaffleAssignment.match_id == match_id,
            models.RaffleAssignment.status.in_(["pending", "claimed"]),
            models.RaffleAssignment.expires_at > now,
        )
    )
    return db.query(q.exists()).scalar()


def _load_active_criteria(db: Session) -> dict[str, models.EligibilityCriterion]:
    """
    Devuelve un dict {key: EligibilityCriterion} solo para criterios activos.
    """
    rows = (
        db.query(models.EligibilityCriterion)
        .filter(models.EligibilityCriterion.active.is_(True))
        .all()
    )
    return {c.key: c for c in rows}


def evaluate_eligibility(
    db: Session,
    user: models.User,
    match: models.Match,
    default_min_age_years: int,
) -> tuple[bool, list[str]]:
    """
    Evalúa todos los criterios activos contra un usuario + partido.
    Retorna (eligible: bool, reasons: list[str]).
    """
    criteria = _load_active_criteria(db)
    reasons: list[str] = []

    # 1) email_verified
    c_email = criteria.get("email_verified")
    if c_email:
        if not user.is_verified or user.email_verified_at is None:
            reasons.append("User email is not verified")

    # 2) not_banned
    c_not_banned = criteria.get("not_banned")
    if c_not_banned:
        if user_is_banned(db, user.id):
            reasons.append("User is banned from attending")

    # 3) no_open_raffle
    c_no_open_raffle = criteria.get("no_open_raffle")
    if c_no_open_raffle:
        if user_has_open_raffle(db, user.id, match.id):
            reasons.append(
                "User already has a pending or claimed raffle assignment for this match"
            )

    # 4) min_age
    c_min_age = criteria.get("min_age")
    if c_min_age:
        min_age_years = c_min_age.value_int or default_min_age_years
    else:
        min_age_years = default_min_age_years

    kickoff_day = match.kickoff_at.date()
    if user.date_of_birth is None:
        reasons.append("Missing date of birth")
    else:
        age = compute_age_years(user.date_of_birth, kickoff_day)
        if age < int(min_age_years):
            reasons.append(
                f"User must be at least {min_age_years} years old on match day"
            )

    return (len(reasons) == 0, reasons)
