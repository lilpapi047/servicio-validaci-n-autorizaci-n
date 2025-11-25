import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Configuración centralizada de la aplicación"""
    
    # Base de datos
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://testuser:testpass@localhost:5432/testdb"
    )
    
    # Aplicación
    PROJECT_NAME = os.getenv("PROJECT_NAME", "Mi API")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    PORT = int(os.getenv("PORT", "8000"))
    
    # Validaciones
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL no está configurada en .env")

settings = Settings()
