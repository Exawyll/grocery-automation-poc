from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from src.models.enums import IngredientCategory


class IngredientBase(BaseModel):
    """Base schema avec champs communs."""
    name: str = Field(..., min_length=1, max_length=100, description="Nom de l'ingrédient")
    category: IngredientCategory = Field(..., description="Catégorie (SEC, FRAIS_GMS, FRAIS_ARTISAN)")
    carrefour_search_term: Optional[str] = Field(
        None,
        max_length=200,
        description="Terme de recherche Carrefour (nullable pour FRAIS_ARTISAN)"
    )


class IngredientCreate(IngredientBase):
    """Schema pour créer un ingrédient."""
    pass


class IngredientUpdate(BaseModel):
    """Schema pour mise à jour partielle (tous champs optionnels)."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[IngredientCategory] = None
    carrefour_search_term: Optional[str] = Field(None, max_length=200)


class IngredientResponse(IngredientBase):
    """Schema de réponse avec tous les champs."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
