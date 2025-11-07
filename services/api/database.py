from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# Cargar el .env
load_dotenv()

# Prioridades
# 1) DATABASE_URL (CI /Local)
# 2) NEON_DATABASE_URL (Produccion)
# 3) Hardcoded Neon URL (Fallback; Temporal con env)
DEFAULT_NEON = (
    "postgresql://neondb_owner:npg_1Pit2fkIUyvO@"
    "ep-summer-darkness-ahwe7hy1-pooler.c-3.us-east-1.aws.neon.tech/"
    "neondb?sslmode=require&channel_binding=require"
)

db_url = (
    os.getenv("DATABASE_URL")
    or os.getenv("NEON_DATABASE_URL")
    or DEFAULT_NEON
)

if db_url.startswith("postgresql://"):
    pass
elif db_url.startswith("postgres://"):
    db_url = "postgresql://" + db_url[len("postgres://"):]

engine = create_engine(
    db_url,
    pool_pre_ping=True,      
    future=True
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
