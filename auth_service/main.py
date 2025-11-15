from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth_service.app.routers import login, register, tokens


app = FastAPI(title="Auth Service")

# Configuración de CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos HTTP (GET, POST, PUT, DELETE, OPTIONS)
    allow_headers=["*"],  # Permite todos los headers
)

# Rutas
app.include_router(register.router)
app.include_router(login.router)
app.include_router(tokens.router)

@app.get("/")
def health_check():
    return {"status": "ok", "service": "auth-service"}