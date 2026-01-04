import pytest
from fastapi.testclient import TestClient
from src.models.enums import IngredientCategory


class TestCreateIngredientEndpoint:
    def test_create_ingredient_success(self, client: TestClient):
        """Test POST /api/v1/ingredients - succès."""
        response = client.post("/api/v1/ingredients/", json={
            "name": "Carotte",
            "category": "FRAIS_ARTISAN"
        })

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Carotte"
        assert data["category"] == "FRAIS_ARTISAN"
        assert "id" in data
        assert "created_at" in data

    def test_create_ingredient_with_carrefour_term(self, client: TestClient):
        """Test création avec terme Carrefour."""
        response = client.post("/api/v1/ingredients/", json={
            "name": "Pâtes",
            "category": "SEC",
            "carrefour_search_term": "pates panzani"
        })

        assert response.status_code == 201
        assert response.json()["carrefour_search_term"] == "pates panzani"

    def test_create_ingredient_validation_error(self, client: TestClient):
        """Test validation Pydantic - nom manquant."""
        response = client.post("/api/v1/ingredients/", json={
            "category": "SEC"
        })

        assert response.status_code == 422

    def test_create_ingredient_duplicate(self, client: TestClient):
        """Test erreur sur doublon."""
        payload = {"name": "Duplicate", "category": "SEC"}
        client.post("/api/v1/ingredients/", json=payload)

        response = client.post("/api/v1/ingredients/", json=payload)

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]


class TestListIngredientsEndpoint:
    def test_list_empty(self, client: TestClient):
        """Test GET /api/v1/ingredients - liste vide."""
        response = client.get("/api/v1/ingredients/")

        assert response.status_code == 200
        assert response.json() == []

    def test_list_with_items(self, client: TestClient):
        """Test liste avec éléments."""
        client.post("/api/v1/ingredients/", json={"name": "A", "category": "SEC"})
        client.post("/api/v1/ingredients/", json={"name": "B", "category": "SEC"})

        response = client.get("/api/v1/ingredients/")

        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_filter_by_category(self, client: TestClient):
        """Test filtre par catégorie."""
        client.post("/api/v1/ingredients/", json={"name": "Sec1", "category": "SEC"})
        client.post("/api/v1/ingredients/", json={"name": "Frais1", "category": "FRAIS_GMS"})

        response = client.get("/api/v1/ingredients/?category=SEC")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["category"] == "SEC"


class TestGetIngredientEndpoint:
    def test_get_existing(self, client: TestClient):
        """Test GET /api/v1/ingredients/{id} - existant."""
        create_response = client.post("/api/v1/ingredients/", json={
            "name": "Oignon",
            "category": "FRAIS_ARTISAN"
        })
        ingredient_id = create_response.json()["id"]

        response = client.get(f"/api/v1/ingredients/{ingredient_id}")

        assert response.status_code == 200
        assert response.json()["name"] == "Oignon"

    def test_get_nonexistent(self, client: TestClient):
        """Test GET avec ID inexistant."""
        fake_id = "00000000-0000-0000-0000-000000000000"

        response = client.get(f"/api/v1/ingredients/{fake_id}")

        assert response.status_code == 404


class TestUpdateIngredientEndpoint:
    def test_update_success(self, client: TestClient):
        """Test PATCH /api/v1/ingredients/{id}."""
        create_response = client.post("/api/v1/ingredients/", json={
            "name": "Beurre",
            "category": "FRAIS_GMS"
        })
        ingredient_id = create_response.json()["id"]

        response = client.patch(
            f"/api/v1/ingredients/{ingredient_id}",
            json={"carrefour_search_term": "beurre doux"}
        )

        assert response.status_code == 200
        assert response.json()["carrefour_search_term"] == "beurre doux"
        assert response.json()["name"] == "Beurre"

    def test_update_nonexistent(self, client: TestClient):
        """Test PATCH avec ID inexistant."""
        fake_id = "00000000-0000-0000-0000-000000000000"

        response = client.patch(
            f"/api/v1/ingredients/{fake_id}",
            json={"name": "New"}
        )

        assert response.status_code == 404


class TestDeleteIngredientEndpoint:
    def test_delete_success(self, client: TestClient):
        """Test DELETE /api/v1/ingredients/{id}."""
        create_response = client.post("/api/v1/ingredients/", json={
            "name": "ToDelete",
            "category": "SEC"
        })
        ingredient_id = create_response.json()["id"]

        response = client.delete(f"/api/v1/ingredients/{ingredient_id}")

        assert response.status_code == 204

        # Vérifier suppression
        get_response = client.get(f"/api/v1/ingredients/{ingredient_id}")
        assert get_response.status_code == 404

    def test_delete_nonexistent(self, client: TestClient):
        """Test DELETE avec ID inexistant."""
        fake_id = "00000000-0000-0000-0000-000000000000"

        response = client.delete(f"/api/v1/ingredients/{fake_id}")

        assert response.status_code == 404
