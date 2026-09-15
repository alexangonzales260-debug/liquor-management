import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.api.routes.products import get_db
from app.main import app

_test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@pytest.fixture
def client():
    SQLModel.metadata.create_all(_test_engine)
    with Session(_test_engine) as session:

        def override_get_db():
            yield session

        app.dependency_overrides[get_db] = override_get_db
        try:
            yield TestClient(app)
        finally:
            app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(_test_engine)