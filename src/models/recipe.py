"""
Modèles Recipe et RecipeIngredient.
"""
import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    Column, String, Text, Integer, DateTime, ForeignKey,
    Enum as SQLEnum, Numeric
)
from sqlalchemy.orm import relationship

from .base import Base
from .enums import Season, Difficulty, UnitType


class Recipe(Base):
    """
    Représente une recette de cuisine.

    Attributes:
        id: UUID unique de la recette
        name: Nom de la recette
        description: Description détaillée (optionnel)
        season: Saison recommandée
        difficulty: Niveau de difficulté
        prep_time_minutes: Temps de préparation en minutes
        portions: Nombre de personnes servies
        created_at: Date de création
        updated_at: Date de dernière modification
    """
    __tablename__ = "recipes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    season = Column(SQLEnum(Season), nullable=False, index=True)
    difficulty = Column(SQLEnum(Difficulty), nullable=False)
    prep_time_minutes = Column(Integer, nullable=False)
    portions = Column(Integer, nullable=False)
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
        back_populates="recipe",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Recipe(id={self.id}, name='{self.name}', season={self.season})>"


class RecipeIngredient(Base):
    """
    Table d'association entre Recipe et Ingredient avec quantité et unité.

    Cette table implémente une relation many-to-many enrichie avec des données
    supplémentaires (quantity, unit).

    Attributes:
        recipe_id: FK vers Recipe
        ingredient_id: FK vers Ingredient
        quantity: Quantité requise (ex: 2.5)
        unit: Unité de mesure (ex: KG, PIECE)
        created_at: Date de création de l'association
    """
    __tablename__ = "recipe_ingredients"

    recipe_id = Column(
        String,
        ForeignKey("recipes.id", ondelete="CASCADE"),
        primary_key=True
    )
    ingredient_id = Column(
        String,
        ForeignKey("ingredients.id", ondelete="CASCADE"),
        primary_key=True
    )
    quantity = Column(Numeric(10, 2), nullable=False)
    unit = Column(SQLEnum(UnitType), nullable=False)
    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    recipe = relationship("Recipe", back_populates="recipe_ingredients")
    ingredient = relationship("Ingredient", back_populates="recipe_ingredients")

    def __repr__(self):
        return (
            f"<RecipeIngredient("
            f"recipe_id={self.recipe_id}, "
            f"ingredient_id={self.ingredient_id}, "
            f"quantity={self.quantity} {self.unit}"
            f")>"
        )
