import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine, init_db

# Routers del microservicio
from .routers import (
    login,
    tokens,
    auth,        # Verificación email + 2FA + Registro
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todos los orígenes (solo para desarrollo)
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

# AUTH (login, tokens, register, verification, 2FA)
app.include_router(login.router)
app.include_router(tokens.router)
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
