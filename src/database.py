"""Configuration de la base de données avec SQLAlchemy."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from src.config import get_settings

settings = get_settings()

# SQLAlchemy Engine
# Pour SQLite, on doit désactiver le check_same_thread
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},  # Nécessaire pour SQLite
    echo=settings.debug  # Log des requêtes SQL en mode debug
)

# Session Factory
# autocommit=False : Les transactions doivent être commitées explicitement
# autoflush=False : Pas de flush automatique avant les queries
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """Dependency injection pour obtenir une session DB dans FastAPI.

    Crée une nouvelle session pour chaque requête, puis la ferme
    automatiquement à la fin de la requête.

    Yields:
        Session: Session SQLAlchemy pour interagir avec la DB

    Example:
        ```python
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
        ```
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Crée toutes les tables dans la base de données.

    Importe tous les models pour que SQLAlchemy les connaisse,
    puis crée les tables si elles n'existent pas déjà.

    Cette fonction est idempotente : elle peut être appelée plusieurs fois
    sans effet de bord.
    """
    from src.models.base import Base
    # Import explicite de tous les models pour les enregistrer dans Base.metadata
    from src.models import Ingredient, Recipe, RecipeIngredient  # noqa: F401

    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully")
