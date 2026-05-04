"""Pytest configuration and fixtures."""
import pytest
import sys
from pathlib import Path

# Add the backend directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import get_db
from app.db.base import Base
from app.models.user import UserRole
from app.services.auth_services import AuthService
from app.core.config import settings


SQLALCHEMY_TEST_DATABASE_URL = URL.create(
    "postgresql+psycopg2",
    username=settings.database_username,
    password=settings.database_password,
    host=settings.database_hostname,
    port=settings.database_port,
    database=f"{settings.database_name}_test",
)

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    pool_pre_ping=True,  
    echo=settings.debug_mode,
    future=True,
)

TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def override_get_db():
    """Override database dependency for tests."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db():
    """Create a test database and return a session."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def test_user(db):
    """Create a test user."""
    user = AuthService.register_user(
        db=db,
        email="test@example.com",
        password="testpassword123",
        full_name="Test User",
        role=UserRole.STUDENT
    )
    return user


@pytest.fixture
def test_instructor(db):
    """Create a test instructor user."""
    user = AuthService.register_user(
        db=db,
        email="instructor@example.com",
        password="testpassword123",
        full_name="Test Instructor",
        role=UserRole.INSTRUCTOR
    )
    return user


@pytest.fixture
def test_admin(db):
    """Create a test admin user."""
    user = AuthService.register_user(
        db=db,
        email="admin@example.com",
        password="testpassword123",
        full_name="Test Admin",
        role=UserRole.ADMIN
    )
    return user


@pytest.fixture
def test_token(test_user):
    """Create a test JWT token."""
    from app.core.security import create_access_token
    token = create_access_token(data={"sub": test_user.id})
    return token


@pytest.fixture
def instructor_token(test_instructor):
    """Create an instructor JWT token."""
    from app.core.security import create_access_token
    token = create_access_token(data={"sub": test_instructor.id})
    return token


@pytest.fixture
def admin_token(test_admin):
    """Create an admin JWT token."""
    from app.core.security import create_access_token
    token = create_access_token(data={"sub": test_admin.id})
    return token


@pytest.fixture
def client_with_auth(client, test_token):
    """Test client with authentication headers."""
    client.headers = {"Authorization": f"Bearer {test_token}"}
    return client
