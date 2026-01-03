"""
Integration tests for model relationships and cascade deletes.
"""
import pytest
from decimal import Decimal

from src.models import Recipe, RecipeIngredient, Ingredient
from src.models import Season, Difficulty, IngredientCategory, UnitType


class TestRelations:
    """Test suite for bidirectional relationships."""

    def test_recipe_to_ingredients_relation(self, session):
        """Test that recipe.recipe_ingredients works correctly."""
        # Create recipe
        recipe = Recipe(
            name="Salade niçoise",
            season=Season.ETE,
            difficulty=Difficulty.FACILE,
            prep_time_minutes=20,
            portions=4
        )
        session.add(recipe)
        session.commit()

        # Create ingredients
        tomate = Ingredient(name="Tomate", category=IngredientCategory.FRAIS_ARTISAN)
        olive = Ingredient(name="Olives", category=IngredientCategory.FRAIS_GMS)
        session.add_all([tomate, olive])
        session.commit()

        # Create associations
        ri1 = RecipeIngredient(
            recipe_id=recipe.id,
            ingredient_id=tomate.id,
            quantity=Decimal("4.00"),
            unit=UnitType.PIECE
        )
        ri2 = RecipeIngredient(
            recipe_id=recipe.id,
            ingredient_id=olive.id,
            quantity=Decimal("100.00"),
            unit=UnitType.G
        )
        session.add_all([ri1, ri2])
        session.commit()

        # Test relationship navigation
        assert len(recipe.recipe_ingredients) == 2
        ingredient_names = {ri.ingredient.name for ri in recipe.recipe_ingredients}
        assert ingredient_names == {"Tomate", "Olives"}

    def test_ingredient_to_recipes_relation(self, session):
        """Test that ingredient.recipe_ingredients works correctly."""
        # Create ingredient
        ingredient = Ingredient(
            name="Poulet",
            category=IngredientCategory.FRAIS_ARTISAN
        )
        session.add(ingredient)
        session.commit()

        # Create multiple recipes
        recipe1 = Recipe(
            name="Poulet rôti",
            season=Season.ANNEE,
            difficulty=Difficulty.MOYEN,
            prep_time_minutes=90,
            portions=4
        )
        recipe2 = Recipe(
            name="Curry de poulet",
            season=Season.HIVER,
            difficulty=Difficulty.MOYEN,
            prep_time_minutes=60,
            portions=4
        )
        session.add_all([recipe1, recipe2])
        session.commit()

        # Create associations
        ri1 = RecipeIngredient(
            recipe_id=recipe1.id,
            ingredient_id=ingredient.id,
            quantity=Decimal("1.50"),
            unit=UnitType.KG
        )
        ri2 = RecipeIngredient(
            recipe_id=recipe2.id,
            ingredient_id=ingredient.id,
            quantity=Decimal("0.80"),
            unit=UnitType.KG
        )
        session.add_all([ri1, ri2])
        session.commit()

        # Test relationship navigation
        assert len(ingredient.recipe_ingredients) == 2
        recipe_names = {ri.recipe.name for ri in ingredient.recipe_ingredients}
        assert recipe_names == {"Poulet rôti", "Curry de poulet"}


class TestCascadeDelete:
    """Test suite for cascade delete behavior."""

    def test_delete_recipe_cascades_to_recipe_ingredients(self, session):
        """Test that deleting a recipe also deletes its recipe_ingredients."""
        # Create recipe and ingredient
        recipe = Recipe(
            name="Quiche lorraine",
            season=Season.ANNEE,
            difficulty=Difficulty.MOYEN,
            prep_time_minutes=50,
            portions=6
        )
        ingredient = Ingredient(
            name="Lardons",
            category=IngredientCategory.FRAIS_GMS
        )
        session.add_all([recipe, ingredient])
        session.commit()

        # Create association
        recipe_ingredient = RecipeIngredient(
            recipe_id=recipe.id,
            ingredient_id=ingredient.id,
            quantity=Decimal("200.00"),
            unit=UnitType.G
        )
        session.add(recipe_ingredient)
        session.commit()

        recipe_id = recipe.id
        ingredient_id = ingredient.id

        # Verify association exists
        ri_count = session.query(RecipeIngredient).filter_by(recipe_id=recipe_id).count()
        assert ri_count == 1

        # Delete recipe
        session.delete(recipe)
        session.commit()

        # Verify recipe_ingredient was cascade deleted
        ri_count_after = session.query(RecipeIngredient).filter_by(recipe_id=recipe_id).count()
        assert ri_count_after == 0

        # Verify ingredient still exists
        ingredient_still_exists = session.query(Ingredient).filter_by(id=ingredient_id).first()
        assert ingredient_still_exists is not None

    def test_delete_ingredient_cascades_to_recipe_ingredients(self, session):
        """Test that deleting an ingredient also deletes its recipe_ingredients."""
        # Create recipe and ingredient
        recipe = Recipe(
            name="Gratin dauphinois",
            season=Season.HIVER,
            difficulty=Difficulty.MOYEN,
            prep_time_minutes=75,
            portions=6
        )
        ingredient = Ingredient(
            name="Pomme de terre",
            category=IngredientCategory.FRAIS_ARTISAN
        )
        session.add_all([recipe, ingredient])
        session.commit()

        # Create association
        recipe_ingredient = RecipeIngredient(
            recipe_id=recipe.id,
            ingredient_id=ingredient.id,
            quantity=Decimal("1.50"),
            unit=UnitType.KG
        )
        session.add(recipe_ingredient)
        session.commit()

        recipe_id = recipe.id
        ingredient_id = ingredient.id

        # Verify association exists
        ri_count = session.query(RecipeIngredient).filter_by(ingredient_id=ingredient_id).count()
        assert ri_count == 1

        # Delete ingredient
        session.delete(ingredient)
        session.commit()

        # Verify recipe_ingredient was cascade deleted
        ri_count_after = session.query(RecipeIngredient).filter_by(ingredient_id=ingredient_id).count()
        assert ri_count_after == 0

        # Verify recipe still exists
        recipe_still_exists = session.query(Recipe).filter_by(id=recipe_id).first()
        assert recipe_still_exists is not None
