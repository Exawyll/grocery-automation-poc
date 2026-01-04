from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from typing import Optional
from src.models.ingredient import Ingredient
from src.schemas.ingredient import IngredientCreate, IngredientUpdate


class DuplicateIngredientError(Exception):
    """Raised when trying to create an ingredient with a duplicate name."""
    pass


def create_ingredient(db: Session, data: IngredientCreate) -> Ingredient:
    """Crée un nouvel ingrédient.

    Raises:
        DuplicateIngredientError: Si un ingrédient avec ce nom existe déjà.
    """
    ingredient = Ingredient(**data.model_dump())
    db.add(ingredient)
    try:
        db.commit()
        db.refresh(ingredient)
        return ingredient
    except IntegrityError:
        db.rollback()
        raise DuplicateIngredientError(f"Ingredient '{data.name}' already exists")


def get_ingredient(db: Session, ingredient_id: UUID) -> Optional[Ingredient]:
    """Récupère un ingrédient par son ID."""
    return db.query(Ingredient).filter(Ingredient.id == str(ingredient_id)).first()


def get_ingredient_by_name(db: Session, name: str) -> Optional[Ingredient]:
    """Récupère un ingrédient par son nom."""
    return db.query(Ingredient).filter(Ingredient.name == name).first()


def get_ingredients(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None
) -> list[Ingredient]:
    """Liste les ingrédients avec pagination et filtre optionnel."""
    query = db.query(Ingredient)
    if category:
        query = query.filter(Ingredient.category == category)
    return query.order_by(Ingredient.name).offset(skip).limit(limit).all()


def update_ingredient(
    db: Session,
    ingredient_id: UUID,
    data: IngredientUpdate
) -> Optional[Ingredient]:
    """Met à jour un ingrédient (mise à jour partielle).

    Returns:
        L'ingrédient mis à jour ou None si non trouvé.
    """
    ingredient = get_ingredient(db, ingredient_id)
    if not ingredient:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ingredient, field, value)

    db.commit()
    db.refresh(ingredient)
    return ingredient


def delete_ingredient(db: Session, ingredient_id: UUID) -> bool:
    """Supprime un ingrédient.

    Returns:
        True si supprimé, False si non trouvé.
    """
    ingredient = get_ingredient(db, ingredient_id)
    if not ingredient:
        return False
    db.delete(ingredient)
    db.commit()
    return True
