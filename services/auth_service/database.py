from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from services.auth_service import config

engine = create_engine(config.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# Dependencia
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()