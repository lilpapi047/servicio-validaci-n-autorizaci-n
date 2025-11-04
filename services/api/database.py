from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Neon connection string
DATABASE_URL = "postgresql://neondb_owner:npg_1Pit2fkIUyvO@ep-summer-darkness-ahwe7hy1-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency (you’ll use this in your routers)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()