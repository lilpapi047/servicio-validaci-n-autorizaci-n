import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from services.api.main import app
from services.api.database import Base, get_db  # <-- FIXED

TEST_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:753951@localhost:5432/app_test",
)

engine = create_engine(TEST_DATABASE_URL, future=True)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)

@pytest.fixture(scope="session", autouse=True)
def _create_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(autouse=True)
def _clean_tables():
    with engine.begin() as conn:
        conn.exec_driver_sql("""
            TRUNCATE TABLE
              raffle_assignment,
              attendance_ban,
              email_verification,
              match,
              "user"
            RESTART IDENTITY CASCADE;
        """)
    yield

@pytest.fixture
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def client(db):
    def _override_get_db():
        try:
            yield db
        finally:
            pass
    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
