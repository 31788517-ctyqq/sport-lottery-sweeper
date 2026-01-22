"""
pytest configuration and fixtures.

This file is automatically discovered by pytest and is used to define
fixtures, hooks, and general configuration for the entire test suite.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ..main import app  # Import your main FastAPI app instance
from ..database import get_db_session  # Import the dependency to override
from ..models import Base  # Import your declarative base

# Use an in-memory SQLite database for testing, which is fast and isolated.
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """
    Creates an instance of the default event loop for each test session.
    This is often required for async tests.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def db_engine():
    """
    Creates a test database engine.
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        # connect_args={"check_same_thread": False}, # For SQLite
        poolclass=StaticPool, # Use StaticPool for in-memory DB
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(db_engine):
    """
    Creates a new database session for a test, ensuring isolation.
    """
    async_session = sessionmaker(
        bind=db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        # Begin a transaction
        await session.begin()
        try:
            yield session
        finally:
            # Rollback the transaction after the test finishes
            await session.rollback()


@pytest.fixture(scope="function")
def override_get_db_session(db_session):
    """
    Overrides the get_db_session dependency with the test session.
    """
    async def _get_db_session_override():
        yield db_session

    app.dependency_overrides[get_db_session] = _get_db_session_override
    yield
    # Clean up the override after the test
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(override_get_db_session):
    """
    Provides a FastAPI TestClient instance with overridden dependencies.
    """
    with TestClient(app) as c:
        yield c


# Example of mocking an async external call (e.g., in a processor or scraper)
@pytest.fixture
def mock_aiohttp_get():
    """
    Fixture to mock aiohttp.ClientSession.get
    """
    with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
        yield mock_get

# Example of a fixture for sample data
@pytest.fixture
def sample_user_data():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "strongpassword123"
    }

@pytest.fixture
def sample_match_data():
    return {
        "home_team": "Team A",
        "away_team": "Team B",
        "match_time": "2023-10-27T15:00:00Z",
        "league": "Test League",
        "venue": "Test Stadium"
    }