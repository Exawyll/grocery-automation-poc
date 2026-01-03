# TASK-002 : Setup FastAPI & Database

## 🎯 Objectif

Mettre en place l'infrastructure backend complète avec FastAPI, SQLAlchemy, et SQLite. Cette tâche pose les fondations pour toutes les futures features du POC.

**Branch Git** : `task/002-setup-fastapi`
**Parent Task** : TASK-001 (Modèle de données - DONE)
**Estimation** : 3h

---

## 📦 Stack Technique

- **FastAPI** 0.109+ : Framework web async
- **SQLAlchemy** 2.0+ : ORM avec support async
- **Pydantic** 2.5+ : Validation et sérialisation
- **SQLite** : Base de données (POC)
- **Uvicorn** : Serveur ASGI
- **Pytest** : Framework de tests

---

## 📁 Structure du Projet Complète

```
grocery-automation-poc/
├── .claude/
│   └── tasks/
│       ├── TASK-001-conception-modele-donnees.md
│       └── TASK-002-setup-fastapi-database.md  ← Ce fichier
├── src/
│   ├── __init__.py                 ← NOUVEAU
│   ├── config.py                   ← NOUVEAU - Configuration centralisée
│   ├── database.py                 ← NOUVEAU - SQLAlchemy engine & session
│   ├── models/                     ← Existant (TASK-001)
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── ingredient.py
│   │   ├── recipe.py
│   │   └── recipe_ingredient.py
│   └── api/
│       ├── __init__.py             ← NOUVEAU
│       └── main.py                 ← NOUVEAU - Point d'entrée FastAPI
├── tests/
│   ├── __init__.py                 ← NOUVEAU
│   ├── conftest.py                 ← NOUVEAU - Fixtures pytest
│   └── test_api/
│       ├── __init__.py             ← NOUVEAU
│       └── test_main.py            ← NOUVEAU - Tests endpoint /health
├── scripts/
│   └── init_db.py                  ← NOUVEAU - Script initialisation DB
├── .env.example                    ← NOUVEAU - Template variables env
├── .gitignore                      ← NOUVEAU
├── requirements.txt                ← NOUVEAU
├── pytest.ini                      ← NOUVEAU
└── README.md                       ← À METTRE À JOUR
```

---

## 💻 Code Détaillé

### 1. Configuration & Dependencies

#### `requirements.txt`

```txt
# Web Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.25
alembic==1.13.1

# Validation & Serialization
pydantic==2.5.3
pydantic-settings==2.1.0

# Utils
python-dotenv==1.0.0

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
httpx==0.26.0  # Pour tester FastAPI
```

#### `.env.example`

```bash
# Application
APP_NAME="Grocery Automation API"
APP_VERSION="0.1.0"
ENVIRONMENT="development"  # development, staging, production
DEBUG=True

# Database
DATABASE_URL="sqlite:///./grocery_automation.db"

# API
API_V1_PREFIX="/api/v1"
ALLOWED_ORIGINS="http://localhost:3000,http://localhost:5173"  # Pour CORS
```

#### `.gitignore`

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
ENV/

# Database
*.db
*.db-journal

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# Testing
.pytest_cache/
.coverage
htmlcov/

# OS
.DS_Store
Thumbbs.db
```

---

### 2. Configuration Centralisée

#### `src/config.py`

```python
"""Configuration centralisée de l'application avec Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Configuration centralisée de l'application.
    
    Les valeurs sont chargées depuis les variables d'environnement
    ou le fichier .env à la racine du projet.
    """
    
    # Application
    app_name: str = "Grocery Automation API"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True
    
    # Database
    database_url: str = "sqlite:///./grocery_automation.db"
    
    # API
    api_v1_prefix: str = "/api/v1"
    allowed_origins: str = "http://localhost:3000"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )
    
    @property
    def origins_list(self) -> list[str]:
        """Parse CORS origins string to list.
        
        Returns:
            list[str]: Liste des origins autorisées pour CORS
        """
        return [origin.strip() for origin in self.allowed_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    """Factory pour obtenir les settings (avec cache).
    
    Utilisé comme dependency injection dans FastAPI.
    Le cache évite de recharger les settings à chaque requête.
    
    Returns:
        Settings: Instance unique des settings
    """
    return Settings()
```

---

### 3. Database Layer

#### `src/database.py`

```python
"""Configuration de la base de données avec SQLAlchemy."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from src.config import get_settings

settings = get_settings()

# SQLAlchemy Engine
# Pour SQLite, on doit désactiver le check_same_thread
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},  # Nécessaire pour SQLite
    echo=settings.debug  # Log des requêtes SQL en mode debug
)

# Session Factory
# autocommit=False : Les transactions doivent être commitées explicitement
# autoflush=False : Pas de flush automatique avant les queries
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """Dependency injection pour obtenir une session DB dans FastAPI.
    
    Crée une nouvelle session pour chaque requête, puis la ferme
    automatiquement à la fin de la requête.
    
    Yields:
        Session: Session SQLAlchemy pour interagir avec la DB
    
    Example:
        ```python
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
        ```
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Crée toutes les tables dans la base de données.
    
    Importe tous les models pour que SQLAlchemy les connaisse,
    puis crée les tables si elles n'existent pas déjà.
    
    Cette fonction est idempotente : elle peut être appelée plusieurs fois
    sans effet de bord.
    """
    from src.models.base import Base
    # Import explicite de tous les models pour les enregistrer dans Base.metadata
    from src.models import ingredient, recipe, recipe_ingredient  # noqa: F401
    
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully")
```

---

### 4. FastAPI Application

#### `src/api/__init__.py`

```python
"""API module for FastAPI application."""
```

#### `src/api/main.py`

```python
"""Point d'entrée de l'application FastAPI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import get_settings

settings = get_settings()

# Initialisation de l'application FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API pour automatiser la planification des repas et listes de courses",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc alternative
)

# Configuration CORS Middleware
# Permet les appels depuis des frontends locaux (React, Vue, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["System"])
def health_check():
    """Endpoint de health check pour monitoring.
    
    Utilisé par les systèmes de monitoring (Docker, Kubernetes, etc.)
    pour vérifier que l'application est en vie.
    
    Returns:
        dict: Status de l'application, version et environnement
    """
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment
    }


@app.get("/", tags=["System"])
def root():
    """Page d'accueil de l'API.
    
    Renvoie les informations de base et les liens vers la documentation.
    
    Returns:
        dict: Message de bienvenue et liens utiles
    """
    return {
        "message": "Grocery Automation API",
        "docs": "/docs",
        "health": "/health"
    }
```

---

### 5. Script d'Initialisation

#### `scripts/init_db.py`

```python
#!/usr/bin/env python3
"""Script pour initialiser la base de données.

Ce script crée toutes les tables définies dans les models SQLAlchemy.
Il est idempotent : peut être exécuté plusieurs fois sans problème.

Usage:
    python scripts/init_db.py
"""

from src.database import init_db

if __name__ == "__main__":
    print("🚀 Initializing database...")
    init_db()
    print("✅ Done!")
```

---

### 6. Configuration Tests

#### `pytest.ini`

```ini
[pytest]
pythonpath = .
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --tb=short
    --disable-warnings
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
```

#### `tests/__init__.py`

```python
"""Tests module for Grocery Automation API."""
```

#### `tests/conftest.py`

```python
"""Configuration globale pytest et fixtures réutilisables."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.api.main import app
from src.database import get_db
from src.models.base import Base

# Database de test en mémoire (isolée des données réelles)
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session() -> Session:
    """Fixture pour obtenir une session DB de test.
    
    Crée une nouvelle base en mémoire pour chaque test,
    puis la détruit après le test pour isolation complète.
    
    Yields:
        Session: Session SQLAlchemy connectée à la DB de test
    """
    # Import des models pour créer les tables
    from src.models import ingredient, recipe, recipe_ingredient  # noqa: F401
    
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session: Session):
    """Fixture pour obtenir un TestClient FastAPI.
    
    Override la dépendance get_db pour utiliser la DB de test
    au lieu de la DB réelle.
    
    Args:
        db_session: Session de test (fixture)
    
    Yields:
        TestClient: Client de test FastAPI
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Cleanup : retirer l'override après le test
    app.dependency_overrides.clear()
```

#### `tests/test_api/__init__.py`

```python
"""API tests module."""
```

#### `tests/test_api/test_main.py`

```python
"""Tests pour les endpoints système de l'API."""

import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Test de l'endpoint racine /.
    
    Vérifie que la page d'accueil renvoie les bonnes informations.
    """
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Grocery Automation API"
    assert "docs" in data
    assert "health" in data


def test_health_check(client: TestClient):
    """Test du health check.
    
    Vérifie que l'endpoint /health renvoie le bon statut
    et les informations de l'application.
    """
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "app" in data
    assert "version" in data
    assert "environment" in data


def test_docs_accessible(client: TestClient):
    """Test que Swagger UI est accessible.
    
    Vérifie que la documentation interactive est disponible.
    """
    response = client.get("/docs")
    assert response.status_code == 200


def test_redoc_accessible(client: TestClient):
    """Test que ReDoc est accessible.
    
    Vérifie que la documentation alternative est disponible.
    """
    response = client.get("/redoc")
    assert response.status_code == 200
```

---

## 🔄 Workflow Git Détaillé

### Étape 1 : Créer la branche de feature

```bash
# S'assurer d'être sur main et à jour
git checkout main
git pull origin main

# Créer la branche de feature
git checkout -b task/002-setup-fastapi
```

### Étape 2 : Développement avec commits atomiques

**Commit 1 : Structure projet + dependencies**
```bash
git add requirements.txt .env.example .gitignore pytest.ini
git commit -m "chore: setup project structure and dependencies (task #2)

- Add requirements.txt with FastAPI, SQLAlchemy, Pydantic
- Add .env.example template
- Add .gitignore for Python project
- Add pytest.ini configuration"
```

**Commit 2 : Configuration**
```bash
git add src/config.py src/__init__.py
git commit -m "feat: add centralized configuration with pydantic-settings (task #2)

- Create Settings class with app, database, and API config
- Add get_settings() factory with LRU cache
- Support for .env file loading
- Parse CORS origins to list"
```

**Commit 3 : Database layer**
```bash
git add src/database.py scripts/init_db.py
git commit -m "feat: setup SQLAlchemy database layer and init script (task #2)

- Create SQLAlchemy engine with SQLite
- Add SessionLocal factory for dependency injection
- Add get_db() generator for FastAPI
- Add init_db() function to create tables
- Add init_db.py script for manual DB initialization"
```

**Commit 4 : FastAPI app**
```bash
git add src/api/__init__.py src/api/main.py
git commit -m "feat: create FastAPI app with health check endpoint (task #2)

- Initialize FastAPI app with metadata
- Add CORS middleware configuration
- Add /health endpoint for monitoring
- Add / root endpoint with API info
- Auto-generate Swagger docs at /docs"
```

**Commit 5 : Tests**
```bash
git add tests/conftest.py tests/test_api/test_main.py tests/__init__.py tests/test_api/__init__.py
git commit -m "test: add tests for health check and root endpoints (task #2)

- Add pytest fixtures in conftest.py
- Create in-memory test database
- Override get_db dependency for testing
- Add 4 tests for system endpoints
- All tests passing ✅"
```

### Étape 3 : Push et Pull Request

```bash
# Push de la branche
git push origin task/002-setup-fastapi

# Créer PR sur GitHub avec :
# Titre : "feat: Setup FastAPI & Database (TASK-002)"
# Description : (voir template ci-dessous)
# Labels : backend, setup, P0
# Reviewers : (si applicable)
```

**Template Description PR** :
```markdown
## 🎯 Objectif

Setup de l'infrastructure backend de base pour le POC Grocery Automation.

## ✅ Checklist

- [x] Structure projet créée
- [x] Dependencies installées (requirements.txt)
- [x] Configuration centralisée (Pydantic Settings)
- [x] Database layer (SQLAlchemy + SQLite)
- [x] FastAPI app avec CORS
- [x] Endpoint /health et / (root)
- [x] Tests pytest (4/4 passent)
- [x] .env.example documenté
- [x] .gitignore configuré

## 🧪 Tests

```bash
pytest tests/test_api/test_main.py -v

# Résultat :
# tests/test_api/test_main.py::test_root_endpoint PASSED
# tests/test_api/test_main.py::test_health_check PASSED
# tests/test_api/test_main.py::test_docs_accessible PASSED
# tests/test_api/test_main.py::test_redoc_accessible PASSED
# ======================== 4 passed in 0.5s ========================
```

## 🚀 Déploiement Local

```bash
# Installation
pip install -r requirements.txt

# Init DB
python scripts/init_db.py

# Lancer serveur
uvicorn src.api.main:app --reload

# Tester
curl http://localhost:8000/health
# Swagger : http://localhost:8000/docs
```

## 🔗 Liens

- TASK-002 dans Notion : [lien]
- Specs détaillées : `.claude/tasks/TASK-002-setup-fastapi-database.md`
- Task précédente : TASK-001 (Modèle de données) - DONE

## 📝 Notes Techniques

- SQLite utilisé pour POC (migration PostgreSQL prévue)
- Pydantic Settings pour type-safe config
- Tests en mémoire pour isolation
- CORS configuré pour dev local frontend
```

### Étape 4 : Après merge

```bash
# Retourner sur main
git checkout main

# Pull les changements
git pull origin main

# Supprimer la branche locale
git branch -d task/002-setup-fastapi
```

---

## ✅ Critères de Validation

### Tests Automatisés (OBLIGATOIRE)

```bash
# Lancer les tests
pytest tests/test_api/test_main.py -v

# Résultat attendu :
# tests/test_api/test_main.py::test_root_endpoint PASSED        [ 25%]
# tests/test_api/test_main.py::test_health_check PASSED         [ 50%]
# tests/test_api/test_main.py::test_docs_accessible PASSED      [ 75%]
# tests/test_api/test_main.py::test_redoc_accessible PASSED     [100%]
# ======================== 4 passed in 0.5s ========================
```

**Tous les tests doivent passer avant de créer la PR !**

### Validation Manuelle

**1. Installation**
```bash
pip install -r requirements.txt
# Attendu : Installation sans erreur
```

**2. Initialisation DB**
```bash
python scripts/init_db.py
# Attendu : 
# 🚀 Initializing database...
# ✅ Database initialized successfully
# ✅ Done!

# Vérifier que grocery_automation.db existe à la racine
ls -lh grocery_automation.db
```

**3. Lancement serveur**
```bash
uvicorn src.api.main:app --reload

# Attendu :
# INFO:     Will watch for changes in these directories: [...]
# INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
# INFO:     Started reloader process [...]
# INFO:     Started server process [...]
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
```

**4. Test endpoint /health**
```bash
curl http://localhost:8000/health

# Attendu :
# {
#   "status": "healthy",
#   "app": "Grocery Automation API",
#   "version": "0.1.0",
#   "environment": "development"
# }
```

**5. Test endpoint / (root)**
```bash
curl http://localhost:8000/

# Attendu :
# {
#   "message": "Grocery Automation API",
#   "docs": "/docs",
#   "health": "/health"
# }
```

**6. Swagger UI**
- Ouvrir http://localhost:8000/docs dans un navigateur
- ✅ Interface Swagger visible
- ✅ Endpoint `GET /health` présent dans la liste
- ✅ Endpoint `GET /` présent dans la liste
- ✅ Possibilité de tester les endpoints depuis l'interface

### Checklist PR (avant merge)

- [ ] Tous les fichiers créés selon structure définie
- [ ] Tests pytest passent à 100% (4/4)
- [ ] `uvicorn` démarre sans erreur
- [ ] Swagger accessible sur `/docs`
- [ ] ReDoc accessible sur `/redoc`
- [ ] Database SQLite créée par `init_db.py`
- [ ] `.env.example` documenté avec tous les paramètres
- [ ] `.gitignore` configuré (pas de `.db` ou `.env` commités)
- [ ] Code formatté (ruff/black si configuré)
- [ ] Commits suivent convention (feat/chore/test)
- [ ] README.md mis à jour avec instructions de setup

---

## 🎓 Notes Techniques

### Pourquoi Pydantic Settings ?

- ✅ Validation automatique des variables d'environnement
- ✅ Type safety (pas de `os.getenv("PORT", "8000")`)
- ✅ Support `.env` natif
- ✅ Cache avec `@lru_cache` pour performance
- ✅ Autocomplete dans l'IDE

### Pourquoi SQLite pour POC ?

- ✅ Zero-config (pas de serveur DB à installer)
- ✅ File-based (facile à reset pour tests)
- ✅ Compatible SQLAlchemy (migration PostgreSQL facile)
- ✅ Suffisant pour <100k rows
- ⚠️ **Limitation** : Pas de concurrent writes (OK pour POC)

### Pourquoi CORS middleware ?

- ✅ Permet appels API depuis frontend local (React/Vue sur port 3000)
- ✅ Configuration via `.env` (différente par environnement)
- ✅ Sécurisé en production (origins spécifiques seulement)
- ⚠️ **Attention** : Ne jamais mettre `allow_origins=["*"]` en prod !

### Session DB vs Connection Pool

- `sessionmaker` crée une factory de sessions
- `get_db()` utilisé comme dependency FastAPI
- Auto-cleanup avec `try/finally`
- Pas de connection leak
- Une nouvelle session par requête HTTP

### Tests en Mémoire

- ✅ Isolation totale entre tests
- ✅ Rapide (pas d'I/O disque)
- ✅ Pas besoin de cleanup manuel
- ✅ Pas de pollution de la DB réelle

---

## 📝 Pour Claude Code

**Prompt complet à utiliser** :

```
Lis le fichier .claude/tasks/TASK-002-setup-fastapi-database.md et implémente-le complètement.

Workflow Git à suivre strictement :
1. Crée la branche task/002-setup-fastapi depuis main
2. Implémente tous les fichiers décrits dans les specs
3. Fais des commits atomiques comme indiqué dans la section "Workflow Git Détaillé"
4. Lance les tests avec pytest et assure-toi qu'ils passent tous (4/4)
5. Fais la validation manuelle (uvicorn, curl /health, /docs)
6. Push la branche et affiche-moi le résumé pour créer la PR

Critères de succès OBLIGATOIRES :
- ✅ 4/4 tests passent
- ✅ uvicorn démarre sans erreur
- ✅ /docs accessible dans navigateur
- ✅ Database créée par init_db.py
- ✅ Tous les commits suivent la convention
- ✅ Pas de fichier .db ou .env commité

Si un test échoue ou si uvicorn ne démarre pas, DEBUG avant de continuer.
```

---

## 🔗 Liens Utiles

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

## 📊 Métriques de Succès

- **Code Coverage** : 100% sur src/api/main.py
- **Tests** : 4/4 passent
- **Build Time** : <10s
- **Startup Time** : <2s
- **Lines of Code** : ~250 (sans commentaires)
- **Files Created** : 14

---

**Date de création** : 2026-01-03
**Auteur** : Claude Desktop (Notion workflow)
**Status** : READY TO IMPLEMENT
