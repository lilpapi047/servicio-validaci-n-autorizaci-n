import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app
import tempfile
import os


@pytest.fixture(scope="session")
def test_db():
    # Crear archivo temporal de base de datos
    db_fd, db_path = tempfile.mkstemp()
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Crear tablas
    Base.metadata.create_all(bind=engine)

    # Entregamos la sesión a los tests
    yield TestingSessionLocal

    # 🔹 LIMPIEZA CORRECTA
    Base.metadata.drop_all(bind=engine)
    engine.dispose()  # 🔸 Cierra todas las conexiones y libera el archivo
    os.close(db_fd)
    try:
        os.unlink(db_path)  # 🔸 Ahora sí podemos borrarlo sin error
    except PermissionError:
        # En caso de que Windows aún lo mantenga bloqueado, lo ignoramos
        pass


@pytest.fixture(scope="function")
def db_session(test_db):
    """Crea una sesión nueva para cada test"""
    session = test_db()
    try:
        yield session
        session.rollback()  # rollback tras cada test
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    """Cliente de test con la DB de prueba inyectada"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # No cerramos aquí, lo hace db_session

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()