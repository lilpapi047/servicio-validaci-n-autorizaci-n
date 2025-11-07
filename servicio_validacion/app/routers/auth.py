from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timedelta
from app.database import get_db
from app.models.user import User
from app.services.email_service import send_verification_email
from app.schemas.user import UserRegister
from shared.config import settings
import pyotp
import requests
import os

router = APIRouter(prefix="/auth", tags=["Autenticación"])

# URL base del microservicio de registro (la definís en .env)
REGISTER_SERVICE_URL = os.getenv("REGISTER_SERVICE_URL", "http://servicio-registro:8001")

# ==============================
# 🔹 Registro de usuario (vía API REST)
# ==============================
@router.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):
    """
    Envía la solicitud de registro al microservicio de registro (auth-service),
    luego devuelve la respuesta al cliente.
    """
    try:
        # Construir la URL completa del endpoint remoto
        endpoint = f"{REGISTER_SERVICE_URL}/register"

        # Enviar el payload al servicio remoto
        response = requests.post(endpoint, json=user.dict())

        # Si falla la comunicación o devuelve error HTTP
        if response.status_code != 200 and response.status_code != 201:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        # Retornar la respuesta JSON del servicio remoto
        return response.json()

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error al comunicar con el servicio de registro: {str(e)}")
