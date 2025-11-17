import os
import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.api.database import Base, get_db
from services.api.main import app
from services.api import models

# Usa DATABASE_URL si existe, sino SQLite local
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# Configura SQLAlchemy según tipo de DB
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crea todas las tablas
Base.metadata.create_all(bind=engine)

# Override get_db para FastAPI
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
def db():
    db = TestingSessionLocal()
    # Limpia tablas antes de cada test
    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())
    db.commit()
    yield db
    db.close()

def _make_user(db, *, email="test@example.com", verified=False, dob=None):
    u = models.User(
        email=email,
        hash_pwd="x",
        is_verified=verified,
        date_of_birth=dob or datetime(2000, 1, 1),
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u

def _make_match(db, *, kickoff=None):
    if kickoff is None:
        kickoff = datetime.now(timezone.utc) + timedelta(days=7)
    m = models.Match(
        stadium_id=1,
        home_team_id=1,
        away_team_id=2,
        phase_id=1,
        kickoff_at=kickoff,
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return m
