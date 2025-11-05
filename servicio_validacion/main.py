import sys
import os
from fastapi import FastAPI


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.routers import auth  
from app.database import init_db  

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
