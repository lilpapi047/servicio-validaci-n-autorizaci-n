import sys
import os
from fastapi import FastAPI

# 👇 Permitir que Python encuentre los módulos dentro de esta carpeta
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ✅ Importación correcta según tu estructura real
from app.routers import auth  # tu archivo se llama app/routers/auth.py
from app.database import init_db  # asegúrate de tener esta función en app/database.py

# Crear la aplicación FastAPI
app = FastAPI(title="Servicio de Validación y Autenticación")

# Inicializar base de datos al iniciar el servidor
@app.on_event("startup")
async def startup_event():
    init_db()

# Incluir tu router principal (autenticación)
app.include_router(auth.router, prefix="/auth", tags=["Autenticación"])

# Endpoint de prueba raíz
@app.get("/")
def root():
    return {"message": "API de Validación funcionando correctamente 🚀"}
