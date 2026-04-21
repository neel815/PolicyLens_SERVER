"""
Test utilities and helpers for PolicyLens test suite.
Provides common fixtures and helper functions for testing.
"""

import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.db.database import Base
from app.models.base import Base as AppBase


# Test database configuration
TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture(scope="function")
def test_db_engine():
    """Create a test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_db_session(test_db_engine) -> Generator[Session, None, None]:
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_db_engine
    )
    session = TestingSessionLocal()
    yield session
    session.close()


def create_test_user_data(
    email: str = "test@example.com",
    password: str = "testpass123"
) -> dict:
    """Create test user data."""
    return {
        "email": email,
        "password": password,
        "full_name": "Test User"
    }


def create_test_file_data(
    filename: str = "test_policy.pdf",
    content: bytes = b"fake pdf content"
) -> dict:
    """Create test file upload data."""
    return {
        "filename": filename,
        "content": content
    }
