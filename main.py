from fastapi import FastAPI
from routes.eligibilidad import router as eligibilidad_router
from routes.asignacion import router as asignacion_router
from routes.perfil import router as perfil_router
import uvicorn
from app.config import settings
from services.api.database import Base, engine

# Crear tablas en la BD
Base.metadata.create_all(bind=engine)

# Crear la instancia de FastAPI
app = FastAPI(title=settings.PROJECT_NAME)

# Registrar rutas
app.include_router(eligibilidad_router, prefix="/verificar-eligibilidad", tags=["Elegibilidad"])
app.include_router(asignacion_router, prefix="/asignar-rifa", tags=["Asignación"])
app.include_router(perfil_router, prefix="/api", tags=["Perfil"])

# Ruta de prueba raíz
@app.get("/")
def read_root():
    return {"message": "API funcionando", "version": "1.0"}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": settings.PROJECT_NAME}

# Ejecutar la app con uvicorn si se corre directamente
if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG
    )
