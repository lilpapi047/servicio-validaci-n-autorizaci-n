import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from servicio_validacion.main import app
from servicio_validacion.app.database import Base, get_db
from servicio_validacion.app.models.user import User