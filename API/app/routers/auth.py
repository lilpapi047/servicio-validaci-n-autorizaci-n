from datetime import datetime, timedelta
import re

from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt, JWTError
from sqlalchemy.orm import Session
import pyotp

from ..database import get_db
from .. import security
from ..models import User
from ..schemas.user import UserCreate, UserRegister, UserOut, ResendVerificationRequest
from ..services.email_service import send_verification_email
from shared.config import settings

# ⚠️ IMPORTANT:
# main.py should include this router WITHOUT an extra prefix:
#   app.include_router(auth.router)
# because this router already has prefix="/auth"
router = APIRouter(prefix="/auth", tags=["auth"])

# -----------------------------
# Helper común para crear usuarios
# -----------------------------
def _create_user(payload: UserCreate | UserRegister, db: Session) -> User:
    """
    Crea un usuario nuevo en la base de datos:
    - Verifica duplicidad de email.
    - Hashea la contraseña.
    - Marca is_verified=False por defecto.
    """
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Validación básica de contraseña (por si el esquema no lo hizo)
    if (
        len(payload.password) < 8
        or not re.search(r"[A-Z]", payload.password)
        or not re.search(r"\d", payload.password)
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe tener al menos 8 caracteres, una mayúscula y un número.",
        )

    user = User(
        email=payload.email,
        hash_pwd=security.get_password_hash(payload.password),
        is_verified=False,  # ✅ new user is not verified
        first_name=getattr(payload, "first_name", None),
        last_name=getattr(payload, "last_name", None),
        date_of_birth=getattr(payload, "date_of_birth", None),
        country_code=(getattr(payload, "country_code", None) or None),
        phone=getattr(payload, "phone", None),
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ==============================
# Signup básico (para tests / API interna)
# ==============================
@router.post("/signup", response_model=UserOut)
def signup(payload: UserCreate, db: Session = Depends(get_db)) -> UserOut:
    """
    Crea un usuario y devuelve el objeto.
    No envía correo, pensado para flujos internos / tests.
    """
    user = _create_user(payload, db)
    return user  # ✅ FastAPI serializa usando UserOut (incluye is_verified)


# ==============================
# Registro con correo de verificación
# ==============================
@router.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario y envía correo de verificación con token JWT.
    """
    created_user = _create_user(user, db)

    token_data = {
        "sub": created_user.email,
        "exp": datetime.utcnow() + timedelta(hours=24),
    }
    token = jwt.encode(token_data, settings.SECRET_KEY, algorithm=settings.algorithm)

    send_verification_email(created_user.email, token)

    return {
        "message": "Usuario registrado exitosamente. Se envió un correo de verificación."
    }


# ==============================
# Verificar correo (token enviado por email)
# ==============================

@router.get("/verify")
def verify_email(token: str, db: Session = Depends(get_db)):
    """
    Endpoint called when the user clicks the email link.
    - Decodes the JWT token
    - Finds the user
    - Marks account as verified
    - Redirects to frontend login with a flag
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.algorithm],
        )
        email: str | None = payload.get("sub")
        if email is None:
            # token sin email
            raise JWTError("No sub in token")

    except JWTError:
        # Token inválido o expirado → redirige con error
        return RedirectResponse(
            f"{settings.frontend_url}/login?verified=0&reason=invalid_token",
            status_code=302,
        )

    # Buscar usuario
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return RedirectResponse(
            f"{settings.frontend_url}/login?verified=0&reason=user_not_found",
            status_code=302,
        )

    # Marcar como verificado (si no lo estaba)
    if not user.is_verified:
        user.is_verified = True
        if hasattr(user, "email_verified_at"):
            user.email_verified_at = datetime.utcnow()
        db.commit()

    # Redirigir al login indicando éxito
    return RedirectResponse(
        f"{settings.frontend_url}/login?verified=1",
        status_code=302,
    )


# ==============================
# Reenviar correo de verificación
# ==============================
@router.post("/verify/send")
def resend_verification(payload: ResendVerificationRequest, db: Session = Depends(get_db)):
    """
    Reenvía el correo de verificación a un usuario no verificado.
    """
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if user.is_verified:
        raise HTTPException(status_code=400, detail="El usuario ya está verificado")

    token_data = {
        "sub": user.email,
        "exp": datetime.utcnow() + timedelta(hours=24),
    }
    token = jwt.encode(token_data, settings.SECRET_KEY, algorithm=settings.algorithm)

    send_verification_email(user.email, token)
    return {"message": "Correo de verificación reenviado exitosamente"}


# ==============================
# Habilitar autenticación 2FA
# ==============================
@router.post("/2fa/enable")
def enable_2fa(user_email: str, db: Session = Depends(get_db)):
    """
    Genera y asocia una clave secreta para activar 2FA.
    """
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    secret = pyotp.random_base32()
    user.twofa_secret = secret
    db.commit()

    otp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=user.email, issuer_name="Sistema de Boletos"
    )
    return {
        "message": "2FA habilitado correctamente",
        "otpauth_url": otp_uri,
    }


# ==============================
# Verificar código 2FA
# ==============================
@router.post("/2fa/verify")
def verify_2fa(user_email: str, code: str, db: Session = Depends(get_db)):
    """
    Verifica el código temporal del 2FA.
    """
    user = db.query(User).filter(User.email == user_email).first()
    if not user or not getattr(user, "twofa_secret", None):
        raise HTTPException(
            status_code=400,
            detail="2FA no configurado para este usuario",
        )

    totp = pyotp.TOTP(user.twofa_secret)
    if not totp.verify(code):
        raise HTTPException(
            status_code=400,
            detail="Código 2FA inválido o expirado",
        )

    user.is_2fa_enabled = True
    db.commit()
    return {"message": "Autenticación de dos factores verificada correctamente"}
