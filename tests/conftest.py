import os
import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.api.database import Base, get_db
from services.api import models

# Configurar BD de prueba
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test_db.db")

if "sqlite" in DATABASE_URL:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Create tables (ensure models exist)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Transactional DB fixture: start a connection + transaction and provide a
# session bound to that connection. Rollback after the test so the real DB
# state is preserved and tests are isolated.
@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

# Funciones de ayuda para tests
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
