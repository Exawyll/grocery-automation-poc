from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.database import get_db
from src.models.recipe import RecipeCreate, RecipeResponse, RecipeWithIngredients
from src.models.ingredient import IngredientCreate, IngredientResponse
from src.services.recipe_service import RecipeService
from src.models.ingredient import Ingredient

router = APIRouter(prefix="/recipes", tags=["Recettes"])


@router.post("/", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
def create_recipe(recipe: RecipeCreate, db: Session = Depends(get_db)):
    """Crée une nouvelle recette"""
    return RecipeService.create_recipe(db, recipe)


@router.get("/", response_model=List[RecipeResponse])
def get_recipes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Récupère toutes les recettes avec pagination"""
    return RecipeService.get_recipes(db, skip, limit)


@router.get("/{recipe_id}", response_model=RecipeWithIngredients)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """Récupère une recette par son ID avec ses ingrédients"""
    recipe = RecipeService.get_recipe(db, recipe_id)
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recette avec l'ID {recipe_id} introuvable"
        )

    # Récupérer les ingrédients
    ingredients = RecipeService.get_recipe_ingredients(db, recipe_id)

    return {
        "id": recipe.id,
        "name": recipe.name,
        "description": recipe.description,
        "servings": recipe.servings,
        "prep_time": recipe.prep_time,
        "cook_time": recipe.cook_time,
        "instructions": recipe.instructions,
        "created_at": recipe.created_at,
        "updated_at": recipe.updated_at,
        "ingredients": ingredients
    }


@router.put("/{recipe_id}", response_model=RecipeResponse)
def update_recipe(recipe_id: int, recipe: RecipeCreate, db: Session = Depends(get_db)):
    """Met à jour une recette"""
    updated_recipe = RecipeService.update_recipe(db, recipe_id, recipe)
    if not updated_recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recette avec l'ID {recipe_id} introuvable"
        )
    return updated_recipe


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """Supprime une recette"""
    success = RecipeService.delete_recipe(db, recipe_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recette avec l'ID {recipe_id} introuvable"
        )


@router.get("/search/", response_model=List[RecipeResponse])
def search_recipes(q: str, db: Session = Depends(get_db)):
    """Recherche des recettes par nom ou description"""
    return RecipeService.search_recipes(db, q)


# Endpoints pour les ingrédients
ingredient_router = APIRouter(prefix="/ingredients", tags=["Ingrédients"])


@ingredient_router.post("/", response_model=IngredientResponse, status_code=status.HTTP_201_CREATED)
def create_ingredient(ingredient: IngredientCreate, db: Session = Depends(get_db)):
    """Crée un nouvel ingrédient"""
    db_ingredient = Ingredient(
        name=ingredient.name,
        category=ingredient.category,
        unit=ingredient.unit
    )
    db.add(db_ingredient)
    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient


@ingredient_router.get("/", response_model=List[IngredientResponse])
def get_ingredients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Récupère tous les ingrédients avec pagination"""
    ingredients = db.query(Ingredient).offset(skip).limit(limit).all()
    return ingredients


@ingredient_router.get("/{ingredient_id}", response_model=IngredientResponse)
def get_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    """Récupère un ingrédient par son ID"""
    ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    if not ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ingrédient avec l'ID {ingredient_id} introuvable"
        )
    return ingredient


@ingredient_router.delete("/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    """Supprime un ingrédient"""
    ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    if not ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ingrédient avec l'ID {ingredient_id} introuvable"
        )
    db.delete(ingredient)
    db.commit()
