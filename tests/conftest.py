import pytest
from collections.abc import Callable, Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.infrastructure.database.base import Base
from app.infrastructure.database.session import get_db
from app.infrastructure.orm import models as _orm_models  # noqa: F401
from app.main import app

PROPERTY_PAYLOAD = {
    "title": "2-room apartment",
    "description": "Near metro",
    "city": "Moscow",
    "address": "Tverskaya 1",
    "property_type": "apartment",
    "deal_type": "sale",
    "price": 12_000_000,
    "area": 65,
    "rooms": 2,
    "floor": 5,
    "total_floors": 12,
}


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def register_user(client: TestClient) -> Callable[..., TestClient]:
    def _register(
        email: str = "owner@example.com",
        password: str = "secret123",
        full_name: str = "Owner",
    ) -> TestClient:
        # Fresh client so cookies are isolated per user; DB override stays on app.
        user_client = TestClient(app)
        response = user_client.post(
            "/api/auth/register",
            json={"email": email, "password": password, "full_name": full_name},
        )
        assert response.status_code == 201, response.text
        return user_client

    return _register


@pytest.fixture()
def auth_client(register_user: Callable[..., TestClient]) -> TestClient:
    return register_user()
