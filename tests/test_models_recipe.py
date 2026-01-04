"""
Tests for Recipe and RecipeIngredient models.
"""
import pytest
from datetime import datetime, timezone
from decimal import Decimal

from src.models import Recipe, RecipeIngredient, Ingredient
from src.models import Season, Difficulty, IngredientCategory, UnitType


class TestRecipe:
    """Test suite for Recipe model."""

    def test_create_recipe_with_all_fields(self, db_session):
        """Test creating a recipe with all fields populated."""
        recipe = Recipe(
            name="Ratatouille",
            description="Légumes du soleil mijotés",
            season=Season.ETE,
            difficulty=Difficulty.MOYEN,
            prep_time_minutes=45,
            portions=4
        )
        db_session.add(recipe)
        db_session.commit()

        # Verify the recipe was created
        assert recipe.id is not None
        assert len(recipe.id) == 36  # UUID format
        assert recipe.name == "Ratatouille"
        assert recipe.description == "Légumes du soleil mijotés"
        assert recipe.season == Season.ETE
        assert recipe.difficulty == Difficulty.MOYEN
        assert recipe.prep_time_minutes == 45
        assert recipe.portions == 4
        assert recipe.created_at is not None
        assert recipe.updated_at is not None

    def test_recipe_without_description(self, db_session):
        """Test that description field is optional."""
        recipe = Recipe(
            name="Salade verte",
            description=None,
            season=Season.ANNEE,
            difficulty=Difficulty.FACILE,
            prep_time_minutes=10,
            portions=2
        )
        db_session.add(recipe)
        db_session.commit()

        assert recipe.description is None
        assert recipe.name == "Salade verte"

    def test_recipe_timestamps_auto_generated(self, db_session):
        """Test that created_at and updated_at are automatically generated."""
        recipe = Recipe(
            name="Soupe",
            season=Season.HIVER,
            difficulty=Difficulty.FACILE,
            prep_time_minutes=30,
            portions=4
        )
        db_session.add(recipe)
        db_session.commit()

        # Verify timestamps exist
        assert recipe.created_at is not None
        assert recipe.updated_at is not None

    def test_recipe_repr(self, db_session):
        """Test that __repr__ returns a readable string."""
        recipe = Recipe(
            name="Tarte aux pommes",
            season=Season.AUTOMNE,
            difficulty=Difficulty.MOYEN,
            prep_time_minutes=60,
            portions=6
        )
        db_session.add(recipe)
        db_session.commit()

        repr_str = repr(recipe)
        assert "Recipe" in repr_str
        assert recipe.id in repr_str
        assert "Tarte aux pommes" in repr_str
        assert "AUTOMNE" in repr_str


class TestRecipeIngredient:
    """Test suite for RecipeIngredient model."""

    def test_create_recipe_ingredient(self, db_session):
        """Test creating a recipe-ingredient association with quantity and unit."""
        # Create ingredient and recipe
        ingredient = Ingredient(
            name="Tomate",
            category=IngredientCategory.FRAIS_ARTISAN
        )
        recipe = Recipe(
            name="Ratatouille",
            season=Season.ETE,
            difficulty=Difficulty.MOYEN,
            prep_time_minutes=45,
            portions=4
        )
        db_session.add(ingredient)
        db_session.add(recipe)
        db_session.commit()

        # Create association
        recipe_ingredient = RecipeIngredient(
            recipe_id=recipe.id,
            ingredient_id=ingredient.id,
            quantity=Decimal("3.00"),
            unit=UnitType.PIECE
        )
        db_session.add(recipe_ingredient)
        db_session.commit()

        # Verify
        assert recipe_ingredient.recipe_id == recipe.id
        assert recipe_ingredient.ingredient_id == ingredient.id
        assert recipe_ingredient.quantity == Decimal("3.00")
        assert recipe_ingredient.unit == UnitType.PIECE
        assert recipe_ingredient.created_at is not None

    def test_recipe_ingredient_composite_primary_key(self, db_session):
        """Test that the same ingredient cannot be added twice to the same recipe."""
        # Create ingredient and recipe
        ingredient = Ingredient(
            name="Courgette",
            category=IngredientCategory.FRAIS_ARTISAN
        )
        recipe = Recipe(
            name="Ratatouille",
            season=Season.ETE,
            difficulty=Difficulty.MOYEN,
            prep_time_minutes=45,
            portions=4
        )
        db_session.add(ingredient)
        db_session.add(recipe)
        db_session.commit()

        # Create first association
        recipe_ingredient1 = RecipeIngredient(
            recipe_id=recipe.id,
            ingredient_id=ingredient.id,
            quantity=Decimal("2.00"),
            unit=UnitType.PIECE
        )
        db_session.add(recipe_ingredient1)
        db_session.commit()

        # Try to create duplicate association
        recipe_ingredient2 = RecipeIngredient(
            recipe_id=recipe.id,
            ingredient_id=ingredient.id,
            quantity=Decimal("5.00"),
            unit=UnitType.PIECE
        )
        db_session.add(recipe_ingredient2)

        with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
            db_session.commit()

    def test_recipe_ingredient_repr(self, db_session):
        """Test that __repr__ returns a readable string."""
        ingredient = Ingredient(
            name="Farine",
            category=IngredientCategory.SEC
        )
        recipe = Recipe(
            name="Pain",
            season=Season.ANNEE,
            difficulty=Difficulty.DIFFICILE,
            prep_time_minutes=120,
            portions=1
        )
        db_session.add(ingredient)
        db_session.add(recipe)
        db_session.commit()

        recipe_ingredient = RecipeIngredient(
            recipe_id=recipe.id,
            ingredient_id=ingredient.id,
            quantity=Decimal("0.50"),
            unit=UnitType.KG
        )
        db_session.add(recipe_ingredient)
        db_session.commit()

        repr_str = repr(recipe_ingredient)
        assert "RecipeIngredient" in repr_str
        assert recipe.id in repr_str
        assert ingredient.id in repr_str
        assert "0.50" in repr_str
        assert "KG" in repr_str
