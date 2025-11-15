from fastapi import FastAPI
from routes.eligibilidad import router as eligibilidad_router
from routes.asignacion import router as asignacion_router
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()  # Carga variables de entorno del .env

app = FastAPI()

# Rutas
app.include_router(eligibilidad_router, prefix="/verificar-eligibilidad")
app.include_router(asignacion_router, prefix="/asignar-rifa")

if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=PORT)
