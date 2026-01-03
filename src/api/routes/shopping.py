from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.database import get_db
from src.models.shopping_list import (
    ShoppingList,
    ShoppingListCreate,
    ShoppingListResponse,
    ShoppingListWithItems,
    ShoppingListFromRecipes
)
from src.services.planning_service import PlanningService
from src.services.carrefour_api import CarrefourAPIService

router = APIRouter(prefix="/shopping", tags=["Listes de courses"])


@router.post("/", response_model=ShoppingListResponse, status_code=status.HTTP_201_CREATED)
def create_shopping_list(shopping_list: ShoppingListCreate, db: Session = Depends(get_db)):
    """Crée une nouvelle liste de courses"""
    db_list = ShoppingList(name=shopping_list.name)
    db.add(db_list)
    db.commit()
    db.refresh(db_list)
    return db_list


@router.get("/", response_model=List[ShoppingListResponse])
def get_shopping_lists(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Récupère toutes les listes de courses avec pagination"""
    lists = db.query(ShoppingList).offset(skip).limit(limit).all()
    return lists


@router.get("/{list_id}", response_model=ShoppingListWithItems)
def get_shopping_list(list_id: int, db: Session = Depends(get_db)):
    """Récupère une liste de courses par son ID avec tous ses articles"""
    shopping_list = db.query(ShoppingList).filter(ShoppingList.id == list_id).first()
    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Liste de courses avec l'ID {list_id} introuvable"
        )

    items = PlanningService.get_shopping_list_items(db, list_id)

    return {
        "id": shopping_list.id,
        "name": shopping_list.name,
        "created_at": shopping_list.created_at,
        "updated_at": shopping_list.updated_at,
        "items": items
    }


@router.delete("/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shopping_list(list_id: int, db: Session = Depends(get_db)):
    """Supprime une liste de courses"""
    shopping_list = db.query(ShoppingList).filter(ShoppingList.id == list_id).first()
    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Liste de courses avec l'ID {list_id} introuvable"
        )
    db.delete(shopping_list)
    db.commit()


@router.post("/from-recipes", response_model=ShoppingListWithItems, status_code=status.HTTP_201_CREATED)
def create_shopping_list_from_recipes(
    request: ShoppingListFromRecipes,
    db: Session = Depends(get_db)
):
    """
    Génère automatiquement une liste de courses à partir de plusieurs recettes
    Les quantités sont agrégées intelligemment
    """
    shopping_list = PlanningService.generate_shopping_list_from_recipes(
        db=db,
        name=request.name,
        recipe_ids=request.recipe_ids,
        servings_multiplier=request.servings_multiplier
    )

    items = PlanningService.get_shopping_list_items(db, shopping_list.id)

    return {
        "id": shopping_list.id,
        "name": shopping_list.name,
        "created_at": shopping_list.created_at,
        "updated_at": shopping_list.updated_at,
        "items": items
    }


@router.patch("/{list_id}/items/{ingredient_id}/check")
def toggle_item_checked(
    list_id: int,
    ingredient_id: int,
    checked: bool,
    db: Session = Depends(get_db)
):
    """Coche ou décoche un article dans la liste de courses"""
    success = PlanningService.update_item_checked_status(db, list_id, ingredient_id, checked)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article introuvable dans cette liste"
        )
    return {"success": True, "checked": checked}


@router.get("/{list_id}/by-category")
def get_shopping_list_by_category(list_id: int, db: Session = Depends(get_db)):
    """Récupère une liste de courses organisée par catégories"""
    shopping_list = db.query(ShoppingList).filter(ShoppingList.id == list_id).first()
    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Liste de courses avec l'ID {list_id} introuvable"
        )

    return PlanningService.organize_shopping_list_by_category(db, list_id)


@router.get("/{list_id}/estimate-cost")
def estimate_shopping_list_cost(list_id: int, db: Session = Depends(get_db)):
    """Estime le coût total d'une liste de courses via l'API Carrefour"""
    shopping_list = db.query(ShoppingList).filter(ShoppingList.id == list_id).first()
    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Liste de courses avec l'ID {list_id} introuvable"
        )

    items = PlanningService.get_shopping_list_items(db, list_id)

    # Préparer les articles pour l'API Carrefour
    carrefour_items = [
        {
            "name": item["ingredient_name"],
            "quantity": item["quantity"]
        }
        for item in items
    ]

    carrefour_service = CarrefourAPIService()
    cost_estimate = carrefour_service.estimate_shopping_list_cost(carrefour_items)

    return cost_estimate


# Endpoints pour la planification
planning_router = APIRouter(prefix="/planning", tags=["Planification"])


@planning_router.get("/weekly-meal-plan")
def get_weekly_meal_plan(
    num_days: int = 7,
    meals_per_day: int = 2,
    db: Session = Depends(get_db)
):
    """Suggère un plan de repas pour la semaine"""
    return PlanningService.suggest_weekly_meal_plan(db, num_days, meals_per_day)
