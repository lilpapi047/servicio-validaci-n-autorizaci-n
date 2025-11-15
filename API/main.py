import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importación del motor y Base de SQLAlchemy
from app.database import Base, engine, init_db

# Routers del microservicio
from app.routers import (
    login,
    register,
    tokens,
    auth,             # Verificación email + 2FA
    eligibility,      # Elegibilidad para la rifa
    raffle,           # Lógica de asignación, reintentos, etc.
    criteria,         # Criterios (edad mínima, reglas, etc.)
    user,             # Perfil del usuario si aplica
    match             # Información de partidos si aplica
)

# ---------------------------------------------------------
# 🔹 Crear la aplicación FastAPI
# ---------------------------------------------------------
app = FastAPI(title="Global Cup Ticket API – Unified Service")

# ---------------------------------------------------------
# 🔹 CORS
# ---------------------------------------------------------
origins = [
    os.getenv("FRONTEND_URL", "http://localhost:5173"),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# 🔹 Inicialización de la base de datos
# ---------------------------------------------------------
@app.on_event("startup")
def startup_event():
    """
    Inicializa la base de datos y crea las tablas si no existen.
    Ideal para el microservicio de integración.
    """
    try:
        Base.metadata.create_all(bind=engine)
        init_db()   # si tu módulo usa algo adicional para inicializar
        print("Base de datos inicializada correctamente.")
    except Exception as e:
        print("Error inicializando BD:", e)


# ---------------------------------------------------------
# 🔹 Registrar todos los routers
# ---------------------------------------------------------
# AUTH (login, register, tokens)
app.include_router(register.router, prefix="/auth", tags=["auth"])
app.include_router(login.router, prefix="/auth", tags=["auth"])
app.include_router(tokens.router, prefix="/auth", tags=["auth"])

# AUTH VALIDATION (email verification + 2FA)
app.include_router(auth.router, prefix="/auth", tags=["auth-verification"])

# RAFFLE / ELEGIBILITY
app.include_router(eligibility.router, prefix="/raffle", tags=["raffle"])
app.include_router(raffle.router, prefix="/raffle", tags=["raffle"])

# CRITERIA
app.include_router(criteria.router, prefix="/criteria", tags=["criteria"])

# USERS (si existe)
if "user" in globals():
    app.include_router(user.router, prefix="/users", tags=["users"])

# ---------------------------------------------------------
# 🔹 Endpoint raíz
# ---------------------------------------------------------
@app.get("/")
def health():
    return {
        "status": "ok",
        "service": "Global Cup Ticket API – Unified Microservice"
    }
