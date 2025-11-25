# services/api/models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Text
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hash_pwd = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False)
    twofa_secret = Column(String, nullable=True)
    is_2fa_enabled = Column(Boolean, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    country_code = Column(String(2), nullable=True)
    phone = Column(String, nullable=True)
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    stadium_id = Column(Integer, nullable=False)
    home_team_id = Column(Integer, nullable=False)
    away_team_id = Column(Integer, nullable=False)
    phase_id = Column(Integer, nullable=False)
    kickoff_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())