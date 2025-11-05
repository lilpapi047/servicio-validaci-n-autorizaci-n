from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base  


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False)
    is_2fa_enabled = Column(Boolean, default=False)
    twofa_secret = Column(String, nullable=True)
