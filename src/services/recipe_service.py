from sqlalchemy.orm import Session
from src.models.recipe import Recipe, RecipeCreate, recipe_ingredients
from src.models.ingredient import Ingredient
from typing import List


class RecipeService:
    """Service pour la gestion des recettes"""

    @staticmethod
    def create_recipe(db: Session, recipe_data: RecipeCreate) -> Recipe:
        """Crée une nouvelle recette avec ses ingrédients"""
        # Créer la recette sans les ingrédients
        recipe = Recipe(
            name=recipe_data.name,
            description=recipe_data.description,
            servings=recipe_data.servings,
            prep_time=recipe_data.prep_time,
            cook_time=recipe_data.cook_time,
            instructions=recipe_data.instructions
        )
        db.add(recipe)
        db.flush()  # Pour obtenir l'ID de la recette

        # Ajouter les ingrédients
        for ingredient_data in recipe_data.ingredients:
            # Vérifier que l'ingrédient existe
            ingredient = db.query(Ingredient).filter(
                Ingredient.id == ingredient_data.ingredient_id
            ).first()

            if ingredient:
                # Insérer dans la table d'association
                stmt = recipe_ingredients.insert().values(
                    recipe_id=recipe.id,
                    ingredient_id=ingredient_data.ingredient_id,
                    quantity=ingredient_data.quantity,
                    unit=ingredient_data.unit
                )
                db.execute(stmt)

        db.commit()
        db.refresh(recipe)
        return recipe

    @staticmethod
    def get_recipe(db: Session, recipe_id: int) -> Recipe | None:
        """Récupère une recette par son ID"""
        return db.query(Recipe).filter(Recipe.id == recipe_id).first()

    @staticmethod
    def get_recipes(db: Session, skip: int = 0, limit: int = 100) -> List[Recipe]:
        """Récupère toutes les recettes avec pagination"""
        return db.query(Recipe).offset(skip).limit(limit).all()

    @staticmethod
    def update_recipe(db: Session, recipe_id: int, recipe_data: RecipeCreate) -> Recipe | None:
        """Met à jour une recette"""
        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if not recipe:
            return None

        # Mettre à jour les champs de base
        recipe.name = recipe_data.name
        recipe.description = recipe_data.description
        recipe.servings = recipe_data.servings
        recipe.prep_time = recipe_data.prep_time
        recipe.cook_time = recipe_data.cook_time
        recipe.instructions = recipe_data.instructions

        # Supprimer les anciens ingrédients
        db.execute(
            recipe_ingredients.delete().where(recipe_ingredients.c.recipe_id == recipe_id)
        )

        # Ajouter les nouveaux ingrédients
        for ingredient_data in recipe_data.ingredients:
            ingredient = db.query(Ingredient).filter(
                Ingredient.id == ingredient_data.ingredient_id
            ).first()

            if ingredient:
                stmt = recipe_ingredients.insert().values(
                    recipe_id=recipe.id,
                    ingredient_id=ingredient_data.ingredient_id,
                    quantity=ingredient_data.quantity,
                    unit=ingredient_data.unit
                )
                db.execute(stmt)

        db.commit()
        db.refresh(recipe)
        return recipe

    @staticmethod
    def delete_recipe(db: Session, recipe_id: int) -> bool:
        """Supprime une recette"""
        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if not recipe:
            return False

        db.delete(recipe)
        db.commit()
        return True

    @staticmethod
    def get_recipe_ingredients(db: Session, recipe_id: int):
        """Récupère les ingrédients d'une recette avec leurs quantités"""
        result = db.execute(
            recipe_ingredients.select().where(recipe_ingredients.c.recipe_id == recipe_id)
        ).fetchall()

        ingredients_list = []
        for row in result:
            ingredient = db.query(Ingredient).filter(Ingredient.id == row.ingredient_id).first()
            if ingredient:
                ingredients_list.append({
                    "ingredient_id": ingredient.id,
                    "ingredient_name": ingredient.name,
                    "quantity": row.quantity,
                    "unit": row.unit
                })

        return ingredients_list

    @staticmethod
    def search_recipes(db: Session, query: str) -> List[Recipe]:
        """Recherche des recettes par nom ou description"""
        return db.query(Recipe).filter(
            (Recipe.name.ilike(f"%{query}%")) |
            (Recipe.description.ilike(f"%{query}%"))
        ).all()
