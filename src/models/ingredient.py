"""
Modèle Ingredient - Représente un ingrédient utilisable dans les recettes.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Column, String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship

from .base import Base
from .enums import IngredientCategory


class Ingredient(Base):
    """
    Représente un ingrédient (ex: Tomate, Huile d'olive, Farine).

    Attributes:
        id: UUID unique de l'ingrédient
        name: Nom de l'ingrédient (unique)
        category: Catégorie (SEC, FRAIS_GMS, FRAIS_ARTISAN)
        carrefour_search_term: Terme de recherche pour l'API Carrefour (nullable)
        created_at: Date de création
        updated_at: Date de dernière modification
    """
    __tablename__ = "ingredients"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, unique=True, index=True)
    category = Column(
        SQLEnum(IngredientCategory),
        nullable=False,
        index=True
    )
    carrefour_search_term = Column(String(200), nullable=True)
    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    recipe_ingredients = relationship(
        "RecipeIngredient",
        back_populates="ingredient",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Ingredient(id={self.id}, name='{self.name}', category={self.category})>"
