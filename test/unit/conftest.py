import os
import tempfile
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from API.app.main import app
from API.app.database import Base, get_db
from API.app import models


# -----------------------------
# Engine + Session factory
# -----------------------------
@pytest.fixture(scope="session")
def engine_and_sessionmaker():
    """
    Crea una base de datos SQLite temporal para toda la sesión de tests
    y devuelve (engine, SessionLocal).
    """
    # archivo temporal
    db_fd, db_path = tempfile.mkstemp()
    sqlalchemy_url = f"sqlite:///{db_path}"

    engine = create_engine(
        sqlalchemy_url,
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    # crear tablas una sola vez
    Base.metadata.create_all(bind=engine)

    yield engine, TestingSessionLocal

    # limpieza al final de la sesión
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    os.close(db_fd)
    try:
        os.unlink(db_path)
    except PermissionError:
        # por si Windows lo bloquea un momento
        pass


# -----------------------------
# DB fixture por test
# -----------------------------
@pytest.fixture(scope="function")
def db(engine_and_sessionmaker):
    """
    Devuelve una sesión de DB limpia para cada test.
    Limpia todas las tablas antes de cada test.
    """
    engine, TestingSessionLocal = engine_and_sessionmaker
    db = TestingSessionLocal()

    # limpiar todas las tablas antes de cada test (como en tu segundo conftest)
    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())
    db.commit()

    try:
        yield db
        db.rollback()
    finally:
        db.close()


# alias opcional si algunos tests esperan el nombre db_session
@pytest.fixture(scope="function")
def db_session(db):
    """
    Alias para compatibilidad con tests que usaban `db_session`.
    """
    yield db


# -----------------------------
# TestClient fixture
# -----------------------------
@pytest.fixture
def client(db):
    """
    Cliente de test con la DB de prueba inyectada.
    """
    def override_get_db():
        try:
            yield db
        finally:
            # db se cierra en el fixture `db`
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


# -----------------------------
# Helpers de creación de datos
# -----------------------------
def _make_user(db, *, email="test@example.com", verified=False, dob=None):
    """
    Crea un usuario de prueba.
    Ajusta los campos según tu modelo real de User.
    """
    u = models.User(
        email=email,
        hash_pwd="x",  # pon aquí un hash válido si tus tests lo necesitan
        is_verified=verified,
        date_of_birth=dob or datetime(2000, 1, 1),
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def _make_match(db, *, kickoff=None):
    """
    Crea un partido de prueba (Match).
    Ajusta campos/IDs según tu modelo real.
    """
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