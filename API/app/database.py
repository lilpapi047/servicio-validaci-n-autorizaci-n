import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ==========================================
# 🔹 Cargar variables del archivo .env
# ==========================================
load_dotenv()

# ==========================================
# 🔹 Obtener URL de base de datos
# Prioridad:
# 1) DATABASE_URL   → desarrollo / CI / Docker
# 2) NEON_DATABASE_URL → prod (opcional)
# ==========================================

DEFAULT_NEON = (
    "postgresql+psycopg2://neondb_owner:npg_1Pit2fkIUyvO@"
    "ep-summer-darkness-ahwe7hy1-pooler.c-3.us-east-1.aws.neon.tech/"
    "neondb?sslmode=require&channel_binding=require"
)

DATABASE_URL = (
    os.getenv("DATABASE_URL") 
    or os.getenv("NEON_DATABASE_URL")
    or DEFAULT_NEON
)

# Normalizar formato postgres:// → postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = "postgresql://" + DATABASE_URL[len("postgres://"):]

# ==========================================
# 🔹 Crear motor de conexión (Engine)
# ==========================================
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True
)

# ==========================================
# 🔹 Crear SessionLocal
# ==========================================
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True
)

# ==========================================
# 🔹 Declarative Base
# ==========================================
Base = declarative_base()

# ==========================================
# 🔹 Inicialización de tablas
# ==========================================
def init_db():
    """
    Inicializa las tablas declaradas en los modelos.
    Llamado desde main.py en el evento startup.
    """
    try:
        Base.metadata.create_all(bind=engine)
        print("Base de datos inicializada correctamente.")
    except Exception as e:
        print("Error inicializando la BD:", e)

# ==========================================
# 🔹 Dependencia para FastAPI
# ==========================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
