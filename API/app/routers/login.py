from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import timedelta
from ..database import get_db
from .. import models, security
from ..schemas import user as user_schema, token as token_schema
from shared.config import settings

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=token_schema.Token)
def login_user(payload: user_schema.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()

    if not user or not security.verify_password(payload.password, user.hash_pwd):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = security.create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}