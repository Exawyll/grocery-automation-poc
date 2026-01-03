"""
Tests for enum types used in data models.
"""
import pytest

from src.models import Season, Difficulty, IngredientCategory, UnitType


class TestEnums:
    """Test suite for all enum types."""

    def test_season_enum_values(self):
        """Verify Season enum has all expected values."""
        expected_values = {"PRINTEMPS", "ETE", "AUTOMNE", "HIVER", "ANNEE"}
        actual_values = {season.value for season in Season}
        assert actual_values == expected_values, f"Season enum values mismatch: {actual_values}"

    def test_difficulty_enum_values(self):
        """Verify Difficulty enum has all expected values."""
        expected_values = {"FACILE", "MOYEN", "DIFFICILE"}
        actual_values = {difficulty.value for difficulty in Difficulty}
        assert actual_values == expected_values, f"Difficulty enum values mismatch: {actual_values}"

    def test_ingredient_category_enum_values(self):
        """Verify IngredientCategory enum has all expected values."""
        expected_values = {"SEC", "FRAIS_GMS", "FRAIS_ARTISAN"}
        actual_values = {category.value for category in IngredientCategory}
        assert actual_values == expected_values, f"IngredientCategory enum values mismatch: {actual_values}"

    def test_unit_type_enum_values(self):
        """Verify UnitType enum has all expected values."""
        expected_values = {
            "PIECE", "KG", "G", "L", "ML",
            "CUILLERE_SOUPE", "CUILLERE_CAFE", "PINCEE"
        }
        actual_values = {unit.value for unit in UnitType}
        assert actual_values == expected_values, f"UnitType enum values mismatch: {actual_values}"

    def test_enums_are_strings(self):
        """Verify all enums inherit from str."""
        assert isinstance(Season.PRINTEMPS.value, str)
        assert isinstance(Difficulty.FACILE.value, str)
        assert isinstance(IngredientCategory.SEC.value, str)
        assert isinstance(UnitType.PIECE.value, str)

        # Also verify enum members themselves are strings (str, Enum)
        assert isinstance(Season.PRINTEMPS, str)
        assert isinstance(Difficulty.FACILE, str)
        assert isinstance(IngredientCategory.SEC, str)
        assert isinstance(UnitType.PIECE, str)
