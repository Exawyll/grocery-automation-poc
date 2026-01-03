from sqlalchemy import Column, Integer, String
from pydantic import BaseModel
from src.database import Base


class Ingredient(Base):
    """Modèle SQLAlchemy pour les ingrédients"""
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True, index=True)
    category = Column(String(100))  # Ex: légumes, viandes, épices, produits laitiers
    unit = Column(String(50), default="unité")  # Ex: kg, g, L, unité


class IngredientCreate(BaseModel):
    """Schema Pydantic pour créer un ingrédient"""
    name: str
    category: str | None = None
    unit: str = "unité"


class IngredientResponse(BaseModel):
    """Schema Pydantic pour la réponse d'un ingrédient"""
    id: int
    name: str
    category: str | None
    unit: str

    class Config:
        from_attributes = True
