from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr, constr
from sqlalchemy.orm import Session
from datetime import date, datetime, timezone
from ..database import get_db
from .. import models

router = APIRouter()

class SignUp(BaseModel):
    email: EmailStr
    password: constr(min_length=8)
    first_name: str | None = None
    last_name: str | None = None
    date_of_birth: date | None = None
    country_code: constr(min_length=2, max_length=2) | None = None
    phone: str | None = None

def fake_hash(pw: str) -> str:
    # TODO: replace with passlib.hash.bcrypt
    return "hashed__" + pw

@router.post("/signup")
def signup(payload: SignUp, db: Session = Depends(get_db)):
    # Check duplicate email
    existing = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    u = models.User(
        email=payload.email,
        hash_pwd=fake_hash(payload.password),
        is_verified=False,
        first_name=payload.first_name,
        last_name=payload.last_name,
        date_of_birth=payload.date_of_birth,
        country_code=payload.country_code.upper() if payload.country_code else None,
        phone=payload.phone,
    )
    
    db.add(u)
    db.commit()
    db.refresh(u)
    return {"id": u.id, "email": u.email}