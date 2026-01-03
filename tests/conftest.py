"""Configuration globale pytest et fixtures réutilisables."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.api.main import app
from src.database import get_db
from src.models.base import Base

# Database de test en mémoire (isolée des données réelles)
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session() -> Session:
    """Fixture pour obtenir une session DB de test.

    Crée une nouvelle base en mémoire pour chaque test,
    puis la détruit après le test pour isolation complète.

    Yields:
        Session: Session SQLAlchemy connectée à la DB de test
    """
    # Import des models pour créer les tables
    from src.models import Ingredient, Recipe, RecipeIngredient  # noqa: F401

    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session: Session):
    """Fixture pour obtenir un TestClient FastAPI.

    Override la dépendance get_db pour utiliser la DB de test
    au lieu de la DB réelle.

    Args:
        db_session: Session de test (fixture)

    Yields:
        TestClient: Client de test FastAPI
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Cleanup : retirer l'override après le test
    app.dependency_overrides.clear()
