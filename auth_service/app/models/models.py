from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP, Text, Date, CHAR, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from auth_service.app.database import Base

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    hash_pwd = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    date_of_birth = Column(Date)
    country_code = Column(CHAR(2))
    phone = Column(String)
    email_verified_at = Column(TIMESTAMP(timezone=True))


class Match(Base):
    __tablename__ = "match"
    id = Column(Integer, primary_key=True, index=True)
    stadium_id = Column(Integer, nullable=False)
    home_team_id = Column(Integer, nullable=False)
    away_team_id = Column(Integer, nullable=False)
    phase_id = Column(Integer, nullable=False)
    kickoff_at = Column(TIMESTAMP(timezone=True), nullable=False)

class RaffleAssignment(Base):
    __tablename__ = "raffle_assignment"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    match_id = Column(Integer, ForeignKey("match.id"), nullable=False)
    token = Column(String, unique=True, nullable=False)
    status = Column(String, nullable=False)  # pending | expired | claimed
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False)

class AttendanceBan(Base):
    __tablename__ = "attendance_ban"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    reason = Column(Text)
    active = Column(Boolean, default=True, nullable=False)
    until = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

class EmailVerification(Base):
    __tablename__ = "email_verification"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    token = Column(String, unique=True, nullable=False)
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False)
    consumed_at = Column(TIMESTAMP(timezone=True))