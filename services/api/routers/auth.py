from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from services.api.database import get_db
from services.api import models
from services.api.schemas.user import UserCreate, UserOut

router = APIRouter()
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/signup", response_model=UserOut)
def signup(payload: UserCreate, db: Session = Depends(get_db)):
    # Revisar duplicidad de email.
    existing = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing:
        # El test acepta 400 o 409 para duplicidad
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    # Creacion de Usuario
    user = models.User(
        email=payload.email,
        hash_pwd=pwd.hash(payload.password),
        is_verified=False,  
        first_name=payload.first_name,
        last_name=payload.last_name,
        date_of_birth=payload.date_of_birth,
        country_code=(payload.country_code or None),
        phone=payload.phone,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user  
