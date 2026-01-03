from sqlalchemy.orm import Session
from src.models.recipe import Recipe
from src.models.shopping_list import ShoppingList, shopping_list_items
from src.models.ingredient import Ingredient
from src.models.recipe import recipe_ingredients
from typing import List, Dict
from datetime import datetime, timedelta


class PlanningService:
    """Service pour la planification des repas et génération de listes de courses"""

    @staticmethod
    def generate_shopping_list_from_recipes(
        db: Session,
        name: str,
        recipe_ids: List[int],
        servings_multiplier: Dict[int, float] | None = None
    ) -> ShoppingList:
        """
        Génère une liste de courses automatique à partir de plusieurs recettes

        Args:
            db: Session de base de données
            name: Nom de la liste de courses
            recipe_ids: Liste des IDs de recettes
            servings_multiplier: Multiplicateur de portions par recette

        Returns:
            La liste de courses créée
        """
        # Créer la liste de courses
        shopping_list = ShoppingList(name=name)
        db.add(shopping_list)
        db.flush()

        # Dictionnaire pour agréger les ingrédients
        aggregated_ingredients = {}

        # Multiplier par défaut à 1
        if servings_multiplier is None:
            servings_multiplier = {}

        # Parcourir toutes les recettes
        for recipe_id in recipe_ids:
            recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
            if not recipe:
                continue

            multiplier = servings_multiplier.get(recipe_id, 1.0)

            # Récupérer les ingrédients de la recette
            recipe_ingr = db.execute(
                recipe_ingredients.select().where(recipe_ingredients.c.recipe_id == recipe_id)
            ).fetchall()

            for row in recipe_ingr:
                ingredient_id = row.ingredient_id
                quantity = row.quantity * multiplier
                unit = row.unit

                # Agréger les quantités si l'ingrédient existe déjà
                key = f"{ingredient_id}_{unit}"
                if key in aggregated_ingredients:
                    aggregated_ingredients[key]["quantity"] += quantity
                else:
                    aggregated_ingredients[key] = {
                        "ingredient_id": ingredient_id,
                        "quantity": quantity,
                        "unit": unit
                    }

        # Ajouter les ingrédients agrégés à la liste de courses
        for item in aggregated_ingredients.values():
            stmt = shopping_list_items.insert().values(
                shopping_list_id=shopping_list.id,
                ingredient_id=item["ingredient_id"],
                quantity=item["quantity"],
                unit=item["unit"],
                checked=False
            )
            db.execute(stmt)

        db.commit()
        db.refresh(shopping_list)
        return shopping_list

    @staticmethod
    def get_shopping_list_items(db: Session, shopping_list_id: int) -> List[Dict]:
        """Récupère les articles d'une liste de courses avec leurs détails"""
        result = db.execute(
            shopping_list_items.select().where(
                shopping_list_items.c.shopping_list_id == shopping_list_id
            )
        ).fetchall()

        items = []
        for row in result:
            ingredient = db.query(Ingredient).filter(
                Ingredient.id == row.ingredient_id
            ).first()

            if ingredient:
                items.append({
                    "ingredient_id": ingredient.id,
                    "ingredient_name": ingredient.name,
                    "category": ingredient.category,
                    "quantity": row.quantity,
                    "unit": row.unit,
                    "checked": row.checked
                })

        return items

    @staticmethod
    def update_item_checked_status(
        db: Session,
        shopping_list_id: int,
        ingredient_id: int,
        checked: bool
    ) -> bool:
        """Met à jour le statut coché d'un article"""
        stmt = (
            shopping_list_items.update()
            .where(shopping_list_items.c.shopping_list_id == shopping_list_id)
            .where(shopping_list_items.c.ingredient_id == ingredient_id)
            .values(checked=checked)
        )
        result = db.execute(stmt)
        db.commit()
        return result.rowcount > 0

    @staticmethod
    def suggest_weekly_meal_plan(
        db: Session,
        num_days: int = 7,
        meals_per_day: int = 2
    ) -> Dict:
        """
        Suggère un plan de repas pour la semaine

        Args:
            db: Session de base de données
            num_days: Nombre de jours à planifier
            meals_per_day: Nombre de repas par jour

        Returns:
            Plan de repas avec les recettes suggérées
        """
        recipes = db.query(Recipe).limit(num_days * meals_per_day).all()

        meal_plan = {}
        recipe_index = 0

        for day in range(num_days):
            day_name = (datetime.now() + timedelta(days=day)).strftime("%A %d/%m")
            daily_meals = []

            for meal in range(meals_per_day):
                if recipe_index < len(recipes):
                    recipe = recipes[recipe_index]
                    daily_meals.append({
                        "recipe_id": recipe.id,
                        "recipe_name": recipe.name,
                        "meal_type": "Déjeuner" if meal == 0 else "Dîner"
                    })
                    recipe_index += 1

            meal_plan[day_name] = daily_meals

        return {
            "start_date": datetime.now().strftime("%Y-%m-%d"),
            "num_days": num_days,
            "meal_plan": meal_plan,
            "total_recipes": recipe_index
        }

    @staticmethod
    def organize_shopping_list_by_category(db: Session, shopping_list_id: int) -> Dict:
        """Organise une liste de courses par catégories"""
        items = PlanningService.get_shopping_list_items(db, shopping_list_id)

        categorized = {}
        for item in items:
            category = item.get("category", "Autres")
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(item)

        return {
            "shopping_list_id": shopping_list_id,
            "categories": categorized,
            "total_items": len(items)
        }
