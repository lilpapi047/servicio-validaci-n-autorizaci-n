import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine, init_db

# Routers del microservicio
from .routers import (
    login,
    register,
    tokens,
    auth,        # Verificación email + 2FA
    eligibility, # Elegibilidad para la rifa
    raffle,      # Lógica de asignación, reintentos, etc.
    criteria,    # Criterios (edad mínima, reglas, etc.)
    match,       # Información de partidos
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
    "http://localhost:8001",
    "http://localhost:8002",
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
    """
    try:
        Base.metadata.create_all(bind=engine)
        init_db()
        print("Base de datos inicializada correctamente.")
    except Exception as e:
        print("Error inicializando BD:", e)


# ---------------------------------------------------------
# 🔹 Registrar todos los routers
# ---------------------------------------------------------
# IMPORTANTE:
# Cada router ya define su propio `prefix` y `tags`,
# así que aquí NO agregamos prefix extra.

# AUTH (login, register, tokens)
app.include_router(register.router)
app.include_router(login.router)
app.include_router(tokens.router)

# AUTH VALIDATION (email verification + 2FA)
app.include_router(auth.router)

# RAFFLE / ELIGIBILITY
app.include_router(eligibility.router, prefix="/raffle", tags=["raffle"])
app.include_router(raffle.router, prefix="/raffle", tags=["raffle"])

# CRITERIA
app.include_router(criteria.router)

# MATCHES
app.include_router(match.router)

# ---------------------------------------------------------
# 🔹 Endpoint raíz
# ---------------------------------------------------------
@app.get("/")
def health():
    return {
        "status": "ok",
        "service": "Global Cup Ticket API – Unified Microservice",
    }
