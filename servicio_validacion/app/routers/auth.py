from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timedelta
from app.database import get_db
from app.models.user import User
from app.services.email_service import send_verification_email
from shared.config import settings
import pyotp

router = APIRouter(prefix="/auth", tags=["Autenticación"])

# Envío del correo de verificación

@router.post("/verify/send")
def send_verification(user_email: str, db: Session = Depends(get_db)):
 
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Crear token JWT con expiración de 24 horas
    token_data = {
        "sub": user.email,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    token = jwt.encode(token_data, settings.SECRET_KEY, algorithm="HS256")

    # Enviar correo con enlace
    send_verification_email(user.email, token)
    return {"message": "Correo de verificación enviado exitosamente"}


# Verificación del enlace (token)

@router.get("/verify")
def verify_account(token: str, db: Session = Depends(get_db)):

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=400, detail="Token inválido")

        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        user.is_verified = True
        db.commit()
        return {"message": "Cuenta verificada exitosamente"}
    except JWTError:
        raise HTTPException(status_code=400, detail="Token inválido o expirado")



# Habilitar el segundo factor de autenticación (2FA)

@router.post("/2fa/enable")
def enable_2fa(user_email: str, db: Session = Depends(get_db)):
    
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    secret = pyotp.random_base32()
    user.twofa_secret = secret
    db.commit()

    # Crear URI compatible con apps de autenticación 
    otp_uri = pyotp.totp.TOTP(secret).provisioning_uri(name=user.email, issuer_name="TuApp")
    return {
        "message": "2FA habilitado correctamente",
        "otpauth_url": otp_uri
    }

# Verificar código 2FA ingresado por el usuario

@router.post("/2fa/verify")
def verify_2fa(user_email: str, code: str, db: Session = Depends(get_db)):
    
    user = db.query(User).filter(User.email == user_email).first()
    if not user or not user.twofa_secret:
        raise HTTPException(status_code=400, detail="2FA no configurado")

    totp = pyotp.TOTP(user.twofa_secret)
    if not totp.verify(code):
        raise HTTPException(status_code=400, detail="Código 2FA inválido o expirado")

    user.is_2fa_enabled = True
    db.commit()
    return {"message": "Autenticación de dos factores activada correctamente"}
