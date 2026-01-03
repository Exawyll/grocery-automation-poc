"""
Tests for Ingredient model.
"""
import pytest
from datetime import datetime, timezone

from src.models import Ingredient, IngredientCategory


class TestIngredient:
    """Test suite for Ingredient model."""

    def test_create_ingredient_with_all_fields(self, session):
        """Test creating an ingredient with all fields populated."""
        ingredient = Ingredient(
            name="Tomate",
            category=IngredientCategory.FRAIS_ARTISAN,
            carrefour_search_term=None
        )
        session.add(ingredient)
        session.commit()

        # Verify the ingredient was created
        assert ingredient.id is not None
        assert len(ingredient.id) == 36  # UUID format
        assert ingredient.name == "Tomate"
        assert ingredient.category == IngredientCategory.FRAIS_ARTISAN
        assert ingredient.carrefour_search_term is None

    def test_create_ingredient_artisan_without_carrefour_term(self, session):
        """Test that FRAIS_ARTISAN ingredients can have NULL carrefour_search_term."""
        ingredient = Ingredient(
            name="Pain de campagne",
            category=IngredientCategory.FRAIS_ARTISAN,
            carrefour_search_term=None
        )
        session.add(ingredient)
        session.commit()

        assert ingredient.carrefour_search_term is None
        assert ingredient.category == IngredientCategory.FRAIS_ARTISAN

    def test_create_ingredient_with_carrefour_term(self, session):
        """Test creating an ingredient with carrefour_search_term."""
        ingredient = Ingredient(
            name="Huile d'olive",
            category=IngredientCategory.SEC,
            carrefour_search_term="huile olive extra vierge"
        )
        session.add(ingredient)
        session.commit()

        assert ingredient.carrefour_search_term == "huile olive extra vierge"
        assert ingredient.category == IngredientCategory.SEC

    def test_ingredient_name_unique_constraint(self, session):
        """Test that ingredient names must be unique."""
        # Create first ingredient
        ingredient1 = Ingredient(
            name="Tomate",
            category=IngredientCategory.FRAIS_ARTISAN
        )
        session.add(ingredient1)
        session.commit()

        # Try to create duplicate
        ingredient2 = Ingredient(
            name="Tomate",
            category=IngredientCategory.FRAIS_GMS
        )
        session.add(ingredient2)

        with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
            session.commit()

    def test_ingredient_timestamps_auto_generated(self, session):
        """Test that created_at and updated_at are automatically generated."""
        ingredient = Ingredient(
            name="Sel",
            category=IngredientCategory.SEC
        )
        session.add(ingredient)
        session.commit()

        # Verify timestamps exist
        assert ingredient.created_at is not None
        assert ingredient.updated_at is not None

    def test_ingredient_repr(self, session):
        """Test that __repr__ returns a readable string."""
        ingredient = Ingredient(
            name="Poivre",
            category=IngredientCategory.SEC
        )
        session.add(ingredient)
        session.commit()

        repr_str = repr(ingredient)
        assert "Ingredient" in repr_str
        assert ingredient.id in repr_str
        assert "Poivre" in repr_str
        assert "SEC" in repr_str
