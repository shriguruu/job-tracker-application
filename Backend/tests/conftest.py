import os
import tempfile
import pytest

# Point to isolated temporary SQLite database for tests
temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
temp_db_path = temp_db.name
temp_db.close()

os.environ["DATABASE_URL"] = f"sqlite:///{temp_db_path}"
os.environ["USE_LOCAL_S3_MOCK"] = "true"
os.environ["JWT_SECRET"] = "test_secret_key_for_unit_tests_12345"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app

test_engine = create_engine(
    f"sqlite:///{temp_db_path}",
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(autouse=True)
def setup_test_database():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def user_a_auth(client):
    res = client.post(
        "/api/v1/auth/signup",
        json={
            "user_name": "Alice Developer",
            "email": "alice@example.com",
            "password": "Password123!",
            "phone_number": "+919876543210",
        },
    )
    assert res.status_code == 201
    data = res.json()
    token = data["token"]
    return {
        "user_id": data["user_id"],
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"},
    }


@pytest.fixture
def user_b_auth(client):
    res = client.post(
        "/api/v1/auth/signup",
        json={
            "user_name": "Bob Engineer",
            "email": "bob@example.com",
            "password": "Password456!",
            "phone_number": "+919876543211",
        },
    )
    assert res.status_code == 201
    data = res.json()
    token = data["token"]
    return {
        "user_id": data["user_id"],
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"},
    }
