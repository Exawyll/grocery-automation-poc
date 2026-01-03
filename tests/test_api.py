import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.api.main import app
from src.database import Base, get_db

# Base de données de test en mémoire
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_ingredient():
    response = client.post(
        "/api/ingredients/",
        json={
            "name": "Tomate",
            "category": "Légumes",
            "unit": "kg"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Tomate"
    assert data["category"] == "Légumes"
    assert "id" in data


def test_get_ingredients():
    # Créer un ingrédient
    client.post(
        "/api/ingredients/",
        json={"name": "Carotte", "category": "Légumes", "unit": "kg"}
    )

    # Récupérer les ingrédients
    response = client.get("/api/ingredients/")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_create_recipe():
    # Créer un ingrédient d'abord
    ingredient_response = client.post(
        "/api/ingredients/",
        json={"name": "Oignon", "category": "Légumes", "unit": "unité"}
    )
    ingredient_id = ingredient_response.json()["id"]

    # Créer une recette
    response = client.post(
        "/api/recipes/",
        json={
            "name": "Soupe à l'oignon",
            "description": "Une délicieuse soupe",
            "servings": 4,
            "prep_time": 15,
            "cook_time": 45,
            "instructions": "1. Éplucher les oignons\n2. Les faire revenir",
            "ingredients": [
                {
                    "ingredient_id": ingredient_id,
                    "quantity": 6,
                    "unit": "unité"
                }
            ]
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Soupe à l'oignon"
    assert "id" in data


def test_get_recipe_with_ingredients():
    # Créer ingrédient et recette
    ingredient_response = client.post(
        "/api/ingredients/",
        json={"name": "Pomme de terre", "category": "Légumes", "unit": "kg"}
    )
    ingredient_id = ingredient_response.json()["id"]

    recipe_response = client.post(
        "/api/recipes/",
        json={
            "name": "Purée",
            "servings": 4,
            "ingredients": [
                {"ingredient_id": ingredient_id, "quantity": 1, "unit": "kg"}
            ]
        }
    )
    recipe_id = recipe_response.json()["id"]

    # Récupérer la recette avec ingrédients
    response = client.get(f"/api/recipes/{recipe_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["ingredients"]) == 1
    assert data["ingredients"][0]["ingredient_name"] == "Pomme de terre"


def test_create_shopping_list_from_recipes():
    # Créer ingrédients
    ing1 = client.post("/api/ingredients/", json={"name": "Ail", "category": "Épices", "unit": "gousse"})
    ing2 = client.post("/api/ingredients/", json={"name": "Persil", "category": "Herbes", "unit": "botte"})

    ing1_id = ing1.json()["id"]
    ing2_id = ing2.json()["id"]

    # Créer recette
    recipe_response = client.post(
        "/api/recipes/",
        json={
            "name": "Persillade",
            "servings": 2,
            "ingredients": [
                {"ingredient_id": ing1_id, "quantity": 3, "unit": "gousse"},
                {"ingredient_id": ing2_id, "quantity": 1, "unit": "botte"}
            ]
        }
    )
    recipe_id = recipe_response.json()["id"]

    # Générer liste de courses
    response = client.post(
        "/api/shopping/from-recipes",
        json={
            "name": "Courses du weekend",
            "recipe_ids": [recipe_id]
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Courses du weekend"
    assert len(data["items"]) == 2
