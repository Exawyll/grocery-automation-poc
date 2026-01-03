from sqlalchemy import Column, Integer, String, Text, DateTime, Table, ForeignKey, Float
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from datetime import datetime
from src.database import Base


# Table d'association pour la relation many-to-many entre recettes et ingrédients
recipe_ingredients = Table(
    'recipe_ingredients',
    Base.metadata,
    Column('recipe_id', Integer, ForeignKey('recipes.id', ondelete='CASCADE'), primary_key=True),
    Column('ingredient_id', Integer, ForeignKey('ingredients.id', ondelete='CASCADE'), primary_key=True),
    Column('quantity', Float, nullable=False),
    Column('unit', String(50), nullable=False)
)


class Recipe(Base):
    """Modèle SQLAlchemy pour les recettes"""
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    servings = Column(Integer, default=4)
    prep_time = Column(Integer)  # Temps de préparation en minutes
    cook_time = Column(Integer)  # Temps de cuisson en minutes
    instructions = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    ingredients = relationship(
        "Ingredient",
        secondary=recipe_ingredients,
        backref="recipes"
    )


class RecipeIngredient(BaseModel):
    """Schema Pydantic pour un ingrédient dans une recette"""
    ingredient_id: int
    ingredient_name: str | None = None
    quantity: float
    unit: str


class RecipeCreate(BaseModel):
    """Schema Pydantic pour créer une recette"""
    name: str
    description: str | None = None
    servings: int = 4
    prep_time: int | None = None
    cook_time: int | None = None
    instructions: str | None = None
    ingredients: list[RecipeIngredient] = []


class RecipeResponse(BaseModel):
    """Schema Pydantic pour la réponse d'une recette"""
    id: int
    name: str
    description: str | None
    servings: int
    prep_time: int | None
    cook_time: int | None
    instructions: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RecipeWithIngredients(RecipeResponse):
    """Schema Pydantic pour une recette avec ses ingrédients"""
    ingredients: list[RecipeIngredient] = []
