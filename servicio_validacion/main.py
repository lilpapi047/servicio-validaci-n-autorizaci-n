import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Asegurar que las rutas relativas funcionen correctamente
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importaciones locales
from app.routers import auth  
from app.database import init_db  

# Crear la aplicación FastAPI
app = FastAPI(title="Servicio de Validación y Autenticación")

# ====================================================
# 🔹 Middleware CORS (permite comunicación con frontend)
# ====================================================
origins = [
    os.getenv("FRONTEND_URL", "http://localhost:5173"),   # Vue o React local
    "http://localhost:8001",                              # Microservicio de registro
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====================================================
# 🔹 Inicialización de base de datos
# ====================================================
@app.on_event("startup")
async def startup_event():
    init_db()
    print("Base de datos inicializada correctamente")

# ====================================================
# 🔹 Routers principales
# ====================================================
app.include_router(auth.router, prefix="/auth", tags=["Autenticación"])

# ====================================================
# 🔹 Endpoint raíz (health check)
# ====================================================
@app.get("/")
def root():
    return {"message": "API de Validación funcionando correctamente "}
