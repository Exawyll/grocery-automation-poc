import pytest
from uuid import uuid4
from src.services import ingredient_service
from src.services.ingredient_service import DuplicateIngredientError
from src.schemas.ingredient import IngredientCreate, IngredientUpdate
from src.models.enums import IngredientCategory


class TestCreateIngredient:
    def test_create_ingredient_success(self, db_session):
        """Test création d'un ingrédient."""
        data = IngredientCreate(
            name="Tomate",
            category=IngredientCategory.FRAIS_ARTISAN,
            carrefour_search_term=None
        )
        ingredient = ingredient_service.create_ingredient(db_session, data)

        assert ingredient.id is not None
        assert ingredient.name == "Tomate"
        assert ingredient.category == IngredientCategory.FRAIS_ARTISAN
        assert ingredient.carrefour_search_term is None

    def test_create_ingredient_with_carrefour_term(self, db_session):
        """Test création avec terme Carrefour."""
        data = IngredientCreate(
            name="Huile d'olive",
            category=IngredientCategory.SEC,
            carrefour_search_term="huile olive vierge"
        )
        ingredient = ingredient_service.create_ingredient(db_session, data)

        assert ingredient.carrefour_search_term == "huile olive vierge"

    def test_create_ingredient_duplicate_name(self, db_session):
        """Test erreur sur nom dupliqué."""
        data = IngredientCreate(
            name="Sel",
            category=IngredientCategory.SEC
        )
        ingredient_service.create_ingredient(db_session, data)

        with pytest.raises(DuplicateIngredientError):
            ingredient_service.create_ingredient(db_session, data)


class TestGetIngredient:
    def test_get_existing_ingredient(self, db_session):
        """Test récupération d'un ingrédient existant."""
        data = IngredientCreate(name="Poivre", category=IngredientCategory.SEC)
        created = ingredient_service.create_ingredient(db_session, data)

        found = ingredient_service.get_ingredient(db_session, created.id)

        assert found is not None
        assert found.id == created.id
        assert found.name == "Poivre"

    def test_get_nonexistent_ingredient(self, db_session):
        """Test récupération d'un ingrédient inexistant."""
        fake_id = uuid4()
        found = ingredient_service.get_ingredient(db_session, fake_id)

        assert found is None


class TestGetIngredients:
    def test_list_all_ingredients(self, db_session):
        """Test liste de tous les ingrédients."""
        ingredient_service.create_ingredient(
            db_session,
            IngredientCreate(name="A", category=IngredientCategory.SEC)
        )
        ingredient_service.create_ingredient(
            db_session,
            IngredientCreate(name="B", category=IngredientCategory.FRAIS_GMS)
        )

        ingredients = ingredient_service.get_ingredients(db_session)

        assert len(ingredients) == 2

    def test_filter_by_category(self, db_session):
        """Test filtre par catégorie."""
        ingredient_service.create_ingredient(
            db_session,
            IngredientCreate(name="Riz", category=IngredientCategory.SEC)
        )
        ingredient_service.create_ingredient(
            db_session,
            IngredientCreate(name="Lait", category=IngredientCategory.FRAIS_GMS)
        )

        sec_only = ingredient_service.get_ingredients(
            db_session,
            category=IngredientCategory.SEC
        )

        assert len(sec_only) == 1
        assert sec_only[0].name == "Riz"

    def test_pagination(self, db_session):
        """Test pagination."""
        for i in range(5):
            ingredient_service.create_ingredient(
                db_session,
                IngredientCreate(name=f"Ing{i}", category=IngredientCategory.SEC)
            )

        page1 = ingredient_service.get_ingredients(db_session, skip=0, limit=2)
        page2 = ingredient_service.get_ingredients(db_session, skip=2, limit=2)

        assert len(page1) == 2
        assert len(page2) == 2


class TestUpdateIngredient:
    def test_update_ingredient(self, db_session):
        """Test mise à jour partielle."""
        data = IngredientCreate(name="Farine", category=IngredientCategory.SEC)
        created = ingredient_service.create_ingredient(db_session, data)

        update = IngredientUpdate(carrefour_search_term="farine T55")
        updated = ingredient_service.update_ingredient(db_session, created.id, update)

        assert updated.carrefour_search_term == "farine T55"
        assert updated.name == "Farine"  # Non modifié

    def test_update_nonexistent(self, db_session):
        """Test mise à jour d'un ingrédient inexistant."""
        fake_id = uuid4()
        update = IngredientUpdate(name="New Name")

        result = ingredient_service.update_ingredient(db_session, fake_id, update)

        assert result is None


class TestDeleteIngredient:
    def test_delete_ingredient(self, db_session):
        """Test suppression."""
        data = IngredientCreate(name="ToDelete", category=IngredientCategory.SEC)
        created = ingredient_service.create_ingredient(db_session, data)

        result = ingredient_service.delete_ingredient(db_session, created.id)

        assert result is True
        assert ingredient_service.get_ingredient(db_session, created.id) is None

    def test_delete_nonexistent(self, db_session):
        """Test suppression d'un ingrédient inexistant."""
        fake_id = uuid4()

        result = ingredient_service.delete_ingredient(db_session, fake_id)

        assert result is False
