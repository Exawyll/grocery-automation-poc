from sqlalchemy import Column, Integer, String, DateTime, Table, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from datetime import datetime
from src.database import Base


# Table d'association pour la relation many-to-many entre listes de courses et ingrédients
shopping_list_items = Table(
    'shopping_list_items',
    Base.metadata,
    Column('shopping_list_id', Integer, ForeignKey('shopping_lists.id', ondelete='CASCADE'), primary_key=True),
    Column('ingredient_id', Integer, ForeignKey('ingredients.id', ondelete='CASCADE'), primary_key=True),
    Column('quantity', Float, nullable=False),
    Column('unit', String(50), nullable=False),
    Column('checked', Boolean, default=False)
)


class ShoppingList(Base):
    """Modèle SQLAlchemy pour les listes de courses"""
    __tablename__ = "shopping_lists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    items = relationship(
        "Ingredient",
        secondary=shopping_list_items,
        backref="shopping_lists"
    )


class ShoppingListItem(BaseModel):
    """Schema Pydantic pour un article de liste de courses"""
    ingredient_id: int
    ingredient_name: str | None = None
    category: str | None = None
    quantity: float
    unit: str
    checked: bool = False


class ShoppingListCreate(BaseModel):
    """Schema Pydantic pour créer une liste de courses"""
    name: str
    items: list[ShoppingListItem] = []


class ShoppingListResponse(BaseModel):
    """Schema Pydantic pour la réponse d'une liste de courses"""
    id: int
    name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ShoppingListWithItems(ShoppingListResponse):
    """Schema Pydantic pour une liste de courses avec ses articles"""
    items: list[ShoppingListItem] = []


class ShoppingListFromRecipes(BaseModel):
    """Schema Pydantic pour générer une liste de courses depuis des recettes"""
    name: str
    recipe_ids: list[int]
    servings_multiplier: dict[int, float] | None = None  # {recipe_id: multiplier}
