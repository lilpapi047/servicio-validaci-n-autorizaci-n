from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# Cargar variables del archivo .env
load_dotenv()

# Obtener la URL de conexión desde el .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Crear el motor de conexión
engine = create_engine(DATABASE_URL)

# Crear sesión local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarativa (para tus modelos)
Base = declarative_base()

# Inicializar base (opcional, por si querés crear tablas al iniciar)
def init_db():
    Base.metadata.create_all(bind=engine)

# Dependencia para usar en tus endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
