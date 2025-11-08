from fastapi import FastAPI
from services.auth_service.api.routers import login, register, tokens


app = FastAPI(title="Auth Service")

# Rutas
app.include_router(register.router)
app.include_router(login.router)
app.include_router(tokens.router)

@app.get("/")
def health_check():
    return {"status": "ok", "service": "auth-service"}