from sqlalchemy import (
    Column,
    Integer,
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
# USER MODEL
# ============================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)

    # Campo de contraseña que usa el servicio (hash_pwd)
    hash_pwd = Column(String, nullable=False)

    # Datos personales
    first_name = Column(String)
    last_name = Column(String)
    date_of_birth = Column(Date)
    country_code = Column(CHAR(2))
    phone = Column(String)

    # Account verification
    is_verified = Column(Boolean, default=False, nullable=False)
    email_verified_at = Column(TIMESTAMP(timezone=True))

    # 2FA
    is_2fa_enabled = Column(Boolean, default=False)
    twofa_secret = Column(String, nullable=True)

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships (opcionales, pero útiles)
    raffle_assignments = relationship(
        "RaffleAssignment",
        back_populates="user",
        cascade="all, delete-orphan",
    )
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


# ============================================================
# MATCH (PARTIDOS)
# ============================================================

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    stadium_id = Column(Integer, nullable=False)
    home_team_id = Column(Integer, nullable=False)
    away_team_id = Column(Integer, nullable=False)
    phase_id = Column(Integer, nullable=False)
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
    __tablename__ = "raffle_assignments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)

    token = Column(String, unique=True, nullable=False)
    status = Column(String, nullable=False)  # pending | expired | claimed

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False)

    user = relationship("User", back_populates="raffle_assignments")
    match = relationship("Match", back_populates="raffle_assignments")


# ============================================================
# ATTENDANCE BAN (BANEOS)
# ============================================================

class AttendanceBan(Base):
    __tablename__ = "attendance_bans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    reason = Column(Text)
    active = Column(Boolean, default=True, nullable=False)
    until = Column(TIMESTAMP(timezone=True))

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user = relationship("User", back_populates="attendance_bans")


# ============================================================
# EMAIL VERIFICATION (TOKENS DE VERIFICACIÓN)
# ============================================================

class EmailVerification(Base):
    __tablename__ = "email_verifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, nullable=False)
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False)
    consumed_at = Column(TIMESTAMP(timezone=True))

    user = relationship("User", back_populates="email_verifications")


# ============================================================
# ELIGIBILITY CRITERIA (REGLAS DEL SISTEMA)
# ============================================================

class EligibilityCriterion(Base):
    __tablename__ = "eligibility_criteria"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    active = Column(Boolean, default=True, nullable=False)
    value_int = Column(Integer)

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    audits = relationship(
        "EligibilityAudit",
        back_populates="criterion",
        cascade="all, delete-orphan",
    )


# ============================================================
# ELIGIBILITY AUDIT (REGISTRO DE CAMBIOS)
# ============================================================

class EligibilityAudit(Base):
    __tablename__ = "eligibility_audits"

    id = Column(Integer, primary_key=True, index=True)
    actor = Column(String, nullable=False)
    action = Column(String, nullable=False)
    criterion_id = Column(
        Integer,
        ForeignKey("eligibility_criteria.id"),
        nullable=False,
    )
    before_json = Column(Text)
    after_json = Column(Text)
    at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    criterion = relationship("EligibilityCriterion", back_populates="audits")
