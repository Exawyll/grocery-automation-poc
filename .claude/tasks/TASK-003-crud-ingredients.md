# TASK-003 : CRUD Ingredients

## 🎯 Objectif

Créer les endpoints CRUD complets pour gérer les ingrédients via l'API REST.

**Dépendances** : TASK-001 ✅ (modèles) + TASK-002 ✅ (FastAPI setup)

## 📁 Fichiers à Créer

```
src/
├── schemas/
│   ├── __init__.py
│   └── ingredient.py          # Pydantic schemas
├── services/
│   ├── __init__.py
│   └── ingredient_service.py  # Business logic
└── api/
    └── routes/
        ├── __init__.py
        └── ingredients.py     # API endpoints

tests/
├── test_services/
│   ├── __init__.py
│   └── test_ingredient_service.py
└── test_api/
    └── test_ingredients.py
```

## 💻 Code Détaillé

### 1. Schemas Pydantic

**src/schemas/__init__.py**
```python
from .ingredient import IngredientCreate, IngredientUpdate, IngredientResponse

__all__ = ["IngredientCreate", "IngredientUpdate", "IngredientResponse"]
```

**src/schemas/ingredient.py**
```python
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from src.models.enums import IngredientCategory


class IngredientBase(BaseModel):
    """Base schema avec champs communs."""
    name: str = Field(..., min_length=1, max_length=100, description="Nom de l'ingrédient")
    category: IngredientCategory = Field(..., description="Catégorie (SEC, FRAIS_GMS, FRAIS_ARTISAN)")
    carrefour_search_term: Optional[str] = Field(
        None, 
        max_length=200,
        description="Terme de recherche Carrefour (nullable pour FRAIS_ARTISAN)"
    )


class IngredientCreate(IngredientBase):
    """Schema pour créer un ingrédient."""
    pass


class IngredientUpdate(BaseModel):
    """Schema pour mise à jour partielle (tous champs optionnels)."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[IngredientCategory] = None
    carrefour_search_term: Optional[str] = Field(None, max_length=200)


class IngredientResponse(IngredientBase):
    """Schema de réponse avec tous les champs."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

### 2. Service Layer

**src/services/__init__.py**
```python
from . import ingredient_service

__all__ = ["ingredient_service"]
```

**src/services/ingredient_service.py**
```python
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
    return db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()


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
```

### 3. Routes API

**src/api/routes/__init__.py**
```python
from .ingredients import router as ingredients_router

__all__ = ["ingredients_router"]
```

**src/api/routes/ingredients.py**
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from src.database import get_db
from src.schemas.ingredient import (
    IngredientCreate,
    IngredientUpdate,
    IngredientResponse
)
from src.services import ingredient_service
from src.services.ingredient_service import DuplicateIngredientError

router = APIRouter(prefix="/api/v1/ingredients", tags=["ingredients"])


@router.post("/", response_model=IngredientResponse, status_code=201)
def create_ingredient(
    data: IngredientCreate,
    db: Session = Depends(get_db)
):
    """Crée un nouvel ingrédient."""
    try:
        return ingredient_service.create_ingredient(db, data)
    except DuplicateIngredientError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[IngredientResponse])
def list_ingredients(
    skip: int = Query(0, ge=0, description="Nombre d'éléments à sauter"),
    limit: int = Query(100, ge=1, le=100, description="Nombre max d'éléments"),
    category: Optional[str] = Query(None, description="Filtrer par catégorie"),
    db: Session = Depends(get_db)
):
    """Liste tous les ingrédients avec pagination et filtre optionnel."""
    return ingredient_service.get_ingredients(db, skip, limit, category)


@router.get("/{ingredient_id}", response_model=IngredientResponse)
def get_ingredient(
    ingredient_id: UUID,
    db: Session = Depends(get_db)
):
    """Récupère un ingrédient par son ID."""
    ingredient = ingredient_service.get_ingredient(db, ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient


@router.patch("/{ingredient_id}", response_model=IngredientResponse)
def update_ingredient(
    ingredient_id: UUID,
    data: IngredientUpdate,
    db: Session = Depends(get_db)
):
    """Met à jour un ingrédient (mise à jour partielle)."""
    ingredient = ingredient_service.update_ingredient(db, ingredient_id, data)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient


@router.delete("/{ingredient_id}", status_code=204)
def delete_ingredient(
    ingredient_id: UUID,
    db: Session = Depends(get_db)
):
    """Supprime un ingrédient."""
    if not ingredient_service.delete_ingredient(db, ingredient_id):
        raise HTTPException(status_code=404, detail="Ingredient not found")
```

### 4. Modifier main.py pour inclure les routes

**Modifier src/api/main.py** - Ajouter après les imports existants :
```python
from src.api.routes import ingredients_router

# Après la création de l'app, ajouter :
app.include_router(ingredients_router)
```

## ✅ Tests Unitaires

### tests/test_services/__init__.py
```python
# empty file
```

### tests/test_services/test_ingredient_service.py
```python
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
```

### tests/test_api/test_ingredients.py
```python
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
```

## 🔍 Critères de Validation

- [ ] `pytest -v` : 16+ tests passent
- [ ] Swagger `/docs` : 5 endpoints visibles
- [ ] POST /ingredients : 201 + validation
- [ ] GET /ingredients : liste + filtre category
- [ ] GET /ingredients/{id} : 200 ou 404
- [ ] PATCH /ingredients/{id} : update partiel
- [ ] DELETE /ingredients/{id} : 204 ou 404
- [ ] Commits conventionnels (feat/test)

## 📝 Commits Suggérés

```bash
# Commit 1 : Schemas
git add src/schemas/
git commit -m "feat: add Pydantic schemas for ingredients (task #3)"

# Commit 2 : Service
git add src/services/
git commit -m "feat: add ingredient service layer (task #3)"

# Commit 3 : Routes
git add src/api/routes/ src/api/main.py
git commit -m "feat: add CRUD endpoints for ingredients (task #3)"

# Commit 4 : Tests
git add tests/
git commit -m "test: add comprehensive tests for ingredient CRUD (task #3)"
```

## 🚀 Workflow Git

```bash
# 1. Créer branche
git checkout main
git pull origin main
git checkout -b task/003-crud-ingredients

# 2. Développer + commiter

# 3. Push + PR
git push origin task/003-crud-ingredients
# Créer PR sur GitHub
```
