from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from services.auth_service.database import get_db
from services.auth_service import models
from services.auth_service import security
from services.auth_service.api.schemas import userCreate as schemas

router = APIRouter()

@router.post("/register", response_model=schemas.UserOut)
def register_user(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = models.User(
        email=payload.email,
        hash_pwd=security.get_password_hash(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
        date_of_birth=payload.date_of_birth,
        country_code=payload.country_code.upper() if payload.country_code else None,
        phone=payload.phone,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user