from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from src.database import get_db
from src.schemas.ingredient import (
    IngredientCreate,
    IngredientUpdate,
    IngredientResponse
)
from src.services import ingredient_service
from src.services.ingredient_service import DuplicateIngredientError

router = APIRouter(prefix="/api/v1/ingredients", tags=["ingredients"])


@router.post("/", response_model=IngredientResponse, status_code=201)
def create_ingredient(
    data: IngredientCreate,
    db: Session = Depends(get_db)
):
    """Crée un nouvel ingrédient."""
    try:
        return ingredient_service.create_ingredient(db, data)
    except DuplicateIngredientError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[IngredientResponse])
def list_ingredients(
    skip: int = Query(0, ge=0, description="Nombre d'éléments à sauter"),
    limit: int = Query(100, ge=1, le=100, description="Nombre max d'éléments"),
    category: Optional[str] = Query(None, description="Filtrer par catégorie"),
    db: Session = Depends(get_db)
):
    """Liste tous les ingrédients avec pagination et filtre optionnel."""
    return ingredient_service.get_ingredients(db, skip, limit, category)


@router.get("/{ingredient_id}", response_model=IngredientResponse)
def get_ingredient(
    ingredient_id: UUID,
    db: Session = Depends(get_db)
):
    """Récupère un ingrédient par son ID."""
    ingredient = ingredient_service.get_ingredient(db, ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient


@router.patch("/{ingredient_id}", response_model=IngredientResponse)
def update_ingredient(
    ingredient_id: UUID,
    data: IngredientUpdate,
    db: Session = Depends(get_db)
):
    """Met à jour un ingrédient (mise à jour partielle)."""
    ingredient = ingredient_service.update_ingredient(db, ingredient_id, data)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient


@router.delete("/{ingredient_id}", status_code=204)
def delete_ingredient(
    ingredient_id: UUID,
    db: Session = Depends(get_db)
):
    """Supprime un ingrédient."""
    if not ingredient_service.delete_ingredient(db, ingredient_id):
        raise HTTPException(status_code=404, detail="Ingredient not found")
