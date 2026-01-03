"""
Pytest configuration and fixtures for testing data models.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models import Base


@pytest.fixture(scope="function")
def engine():
    """
    Create an in-memory SQLite database engine for testing.

    Scope is 'function' to ensure each test gets a fresh database.
    """
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def session(engine):
    """
    Create a SQLAlchemy session with automatic rollback.

    This ensures tests don't interfere with each other.
    """
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    yield session

    session.rollback()
    session.close()
