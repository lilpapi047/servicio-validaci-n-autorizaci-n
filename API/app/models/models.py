from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    Boolean,
    ForeignKey,
    TIMESTAMP,
    Text,
    Date,
    CHAR,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


# ============================================================
# USER
# ============================================================


class User(Base):
    __tablename__ = "user"  # ← singular table

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(Text, unique=True, nullable=False, index=True)
    hash_pwd = Column(Text, nullable=False)

    # Datos personales
    first_name = Column(Text)
    last_name = Column(Text)
    date_of_birth = Column(Date)
    country_code = Column(CHAR(2))
    phone = Column(Text)

    # Verificación / 2FA
    is_verified = Column(Boolean, nullable=False, default=False)
    email_verified_at = Column(TIMESTAMP(timezone=True))
    twofa_secret = Column(Text)
    is_2fa_enabled = Column(Boolean, default=False)

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relaciones
    attendance_bans = relationship(
        "AttendanceBan",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    email_verifications = relationship(
        "EmailVerification",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    raffle_assignments = relationship(
        "RaffleAssignment",
        back_populates="user",
        cascade="all, delete-orphan",
    )


# ============================================================
# MATCH (PARTIDOS)
# ============================================================


class Match(Base):
    __tablename__ = "match"  # ← singular

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    stadium_id = Column(BigInteger, nullable=False)
    home_team_id = Column(BigInteger, nullable=False)
    away_team_id = Column(BigInteger, nullable=False)
    phase_id = Column(BigInteger, nullable=False)
    kickoff_at = Column(TIMESTAMP(timezone=True), nullable=False)

    raffle_assignments = relationship(
        "RaffleAssignment",
        back_populates="match",
        cascade="all, delete-orphan",
    )


# ============================================================
# RAFFLE ASSIGNMENT (OPORTUNIDADES DE COMPRA)
# ============================================================


class RaffleAssignment(Base):
    __tablename__ = "raffle_assignment"  # ← singular

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    match_id = Column(Integer, ForeignKey("match.id"), nullable=False)
    token = Column(Text, unique=True, nullable=False, index=True)
    status = Column(String, nullable=False)  # 'pending', 'claimed', 'expired', etc.
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False)

    user = relationship("User", back_populates="raffle_assignments")
    match = relationship("Match", back_populates="raffle_assignments")


# ============================================================
# ATTENDANCE BANS
# ============================================================


class AttendanceBan(Base):
    __tablename__ = "attendance_ban"  # ← singular

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    reason = Column(Text)
    active = Column(Boolean, nullable=False, default=True)
    until = Column(TIMESTAMP(timezone=True))
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user = relationship("User", back_populates="attendance_bans")


# ============================================================
# EMAIL VERIFICATION TOKENS
# ============================================================


class EmailVerification(Base):
    __tablename__ = "email_verification"  # ← singular

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    token = Column(Text, nullable=False, unique=True, index=True)
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False)
    consumed_at = Column(TIMESTAMP(timezone=True))

    user = relationship("User", back_populates="email_verifications")


# ============================================================
# ELIGIBILITY CRITERIA
# ============================================================


class EligibilityCriterion(Base):
    __tablename__ = "eligibility_criterion"  # ← **esta es la que ya tiene tus datos**

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    key = Column(Text, unique=True, nullable=False)
    name = Column(Text, nullable=False)
    description = Column(Text)
    active = Column(Boolean, nullable=False, default=True)
    value_int = Column(Integer)

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    audits = relationship(
        "EligibilityAudit",
        back_populates="criterion",
        cascade="all, delete-orphan",
    )


# ============================================================
# ELIGIBILITY AUDIT
# ============================================================


class EligibilityAudit(Base):
    __tablename__ = "eligibility_audit"  # ← singular

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    actor = Column(Text, nullable=False)
    action = Column(Text, nullable=False)
    criterion_id = Column(Integer, ForeignKey("eligibility_criterion.id", ondelete="CASCADE"), nullable=False)
    before_json = Column(Text)
    after_json = Column(Text)
    at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    criterion = relationship("EligibilityCriterion", back_populates="audits")

class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    actor = Column(Text, nullable=False)
    action = Column(Text, nullable=False)
    entity = Column(Text, nullable=False)
    entity_id = Column(Text, nullable=False)
    at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )