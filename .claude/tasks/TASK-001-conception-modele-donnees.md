# TASK-001 : Conception - Modèle de Données

**Statut** : Not started  
**Priorité** : P0 - Urgent  
**Assignation** : Claude Code  
**Estimation** : 4h  
**Date début** : 2026-01-02  

---

## 🎯 Objectif

Définir et documenter le modèle de données complet pour l'application Grocery Automation POC. Ce modèle servira de fondation pour toutes les fonctionnalités backend (CRUD Ingredients, CRUD Recipes, génération de listes de courses).

---

## 📁 Fichiers à Créer

```
grocery-automation-poc/
├── src/
│   └── models/
│       ├── __init__.py
│       ├── base.py              # Base SQLAlchemy
│       ├── enums.py             # Tous les Enums
│       ├── ingredient.py        # Modèle Ingredient + ORM
│       └── recipe.py            # Modèles Recipe + RecipeIngredient + ORM
├── docs/
│   └── database_schema.md       # Documentation du schéma
└── alembic/                     # (Optionnel pour POC)
    └── versions/
        └── 001_initial_schema.py
```

---

## 💻 Code Détaillé

### 1. `src/models/enums.py`

```python
"""
Enums pour le modèle de données Grocery Automation.
"""
from enum import Enum


class Season(str, Enum):
    """Saisons pour catégoriser les recettes."""
    PRINTEMPS = "PRINTEMPS"
    ETE = "ETE"
    AUTOMNE = "AUTOMNE"
    HIVER = "HIVER"
    ANNEE = "ANNEE"  # Pour recettes disponibles toute l'année


class Difficulty(str, Enum):
    """Niveaux de difficulté pour les recettes."""
    FACILE = "FACILE"
    MOYEN = "MOYEN"
    DIFFICILE = "DIFFICILE"


class IngredientCategory(str, Enum):
    """Catégories d'ingrédients pour la stratégie d'achat."""
    SEC = "SEC"                    # Produits secs (huile, riz, pâtes...)
    FRAIS_GMS = "FRAIS_GMS"        # Frais grande surface (crème, beurre...)
    FRAIS_ARTISAN = "FRAIS_ARTISAN"  # Artisans (tomates, viande, pain...)


class UnitType(str, Enum):
    """Unités de mesure pour les quantités d'ingrédients."""
    PIECE = "PIECE"                # Unité (1 oignon, 2 tomates)
    KG = "KG"
    G = "G"
    L = "L"
    ML = "ML"
    CUILLERE_SOUPE = "CUILLERE_SOUPE"
    CUILLERE_CAFE = "CUILLERE_CAFE"
    PINCEE = "PINCEE"
```

### 2. `src/models/base.py`

```python
"""
Base SQLAlchemy pour tous les modèles.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

# Cette config sera remplacée par src/database.py plus tard
# Pour l'instant, on définit juste la Base
```

### 3. `src/models/ingredient.py`

```python
"""
Modèle Ingredient - Représente un ingrédient utilisable dans les recettes.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Column, String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship

from .base import Base
from .enums import IngredientCategory


class Ingredient(Base):
    """
    Représente un ingrédient (ex: Tomate, Huile d'olive, Farine).
    
    Attributes:
        id: UUID unique de l'ingrédient
        name: Nom de l'ingrédient (unique)
        category: Catégorie (SEC, FRAIS_GMS, FRAIS_ARTISAN)
        carrefour_search_term: Terme de recherche pour l'API Carrefour (nullable)
        created_at: Date de création
        updated_at: Date de dernière modification
    """
    __tablename__ = "ingredients"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, unique=True, index=True)
    category = Column(
        SQLEnum(IngredientCategory),
        nullable=False,
        index=True
    )
    carrefour_search_term = Column(String(200), nullable=True)
    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    recipe_ingredients = relationship(
        "RecipeIngredient",
        back_populates="ingredient",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Ingredient(id={self.id}, name='{self.name}', category={self.category})>"
```

### 4. `src/models/recipe.py`

```python
"""
Modèles Recipe et RecipeIngredient.
"""
import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    Column, String, Text, Integer, DateTime, ForeignKey,
    Enum as SQLEnum, Numeric
)
from sqlalchemy.orm import relationship

from .base import Base
from .enums import Season, Difficulty, UnitType


class Recipe(Base):
    """
    Représente une recette de cuisine.
    
    Attributes:
        id: UUID unique de la recette
        name: Nom de la recette
        description: Description détaillée (optionnel)
        season: Saison recommandée
        difficulty: Niveau de difficulté
        prep_time_minutes: Temps de préparation en minutes
        portions: Nombre de personnes servies
        created_at: Date de création
        updated_at: Date de dernière modification
    """
    __tablename__ = "recipes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    season = Column(SQLEnum(Season), nullable=False, index=True)
    difficulty = Column(SQLEnum(Difficulty), nullable=False)
    prep_time_minutes = Column(Integer, nullable=False)
    portions = Column(Integer, nullable=False)
    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    recipe_ingredients = relationship(
        "RecipeIngredient",
        back_populates="recipe",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Recipe(id={self.id}, name='{self.name}', season={self.season})>"


class RecipeIngredient(Base):
    """
    Table d'association entre Recipe et Ingredient avec quantité et unité.
    
    Cette table implémente une relation many-to-many enrichie avec des données
    supplémentaires (quantity, unit).
    
    Attributes:
        recipe_id: FK vers Recipe
        ingredient_id: FK vers Ingredient
        quantity: Quantité requise (ex: 2.5)
        unit: Unité de mesure (ex: KG, PIECE)
        created_at: Date de création de l'association
    """
    __tablename__ = "recipe_ingredients"

    recipe_id = Column(
        String,
        ForeignKey("recipes.id", ondelete="CASCADE"),
        primary_key=True
    )
    ingredient_id = Column(
        String,
        ForeignKey("ingredients.id", ondelete="CASCADE"),
        primary_key=True
    )
    quantity = Column(Numeric(10, 2), nullable=False)
    unit = Column(SQLEnum(UnitType), nullable=False)
    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    recipe = relationship("Recipe", back_populates="recipe_ingredients")
    ingredient = relationship("Ingredient", back_populates="recipe_ingredients")

    def __repr__(self):
        return (
            f"<RecipeIngredient("
            f"recipe_id={self.recipe_id}, "
            f"ingredient_id={self.ingredient_id}, "
            f"quantity={self.quantity} {self.unit}"
            f")>"
        )
```

### 5. `src/models/__init__.py`

```python
"""
Models package - Expose tous les modèles ORM.
"""
from .base import Base
from .enums import Season, Difficulty, IngredientCategory, UnitType
from .ingredient import Ingredient
from .recipe import Recipe, RecipeIngredient

__all__ = [
    "Base",
    "Season",
    "Difficulty",
    "IngredientCategory",
    "UnitType",
    "Ingredient",
    "Recipe",
    "RecipeIngredient",
]
```

### 6. `docs/database_schema.md`

```markdown
# Schéma de Base de Données - Grocery Automation

## Vue d'Ensemble

Ce document décrit le schéma de base de données pour le POC Grocery Automation.

**Base de données** : SQLite (POC) → PostgreSQL (Production)  
**ORM** : SQLAlchemy 2.0+  
**Date de création** : 2026-01-02

---

## Diagramme ERD

```
┌─────────────────┐         ┌──────────────────────┐         ┌─────────────────┐
│     Recipe      │         │  RecipeIngredient    │         │   Ingredient    │
├─────────────────┤         ├──────────────────────┤         ├─────────────────┤
│ id (PK)         │◄────────│ recipe_id (FK)       │────────►│ id (PK)         │
│ name            │         │ ingredient_id (FK)   │         │ name (unique)   │
│ description     │         │ quantity             │         │ category        │
│ season          │         │ unit                 │         │ carrefour_...   │
│ difficulty      │         │ created_at           │         │ created_at      │
│ prep_time_min   │         └──────────────────────┘         │ updated_at      │
│ portions        │                                           └─────────────────┘
│ created_at      │
│ updated_at      │
└─────────────────┘
```

---

## Tables

### `ingredients`

Stocke tous les ingrédients utilisables dans les recettes.

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| id | VARCHAR(36) | PK | UUID de l'ingrédient |
| name | VARCHAR(100) | NOT NULL, UNIQUE, INDEX | Nom de l'ingrédient |
| category | ENUM | NOT NULL, INDEX | SEC, FRAIS_GMS, FRAIS_ARTISAN |
| carrefour_search_term | VARCHAR(200) | NULLABLE | Terme de recherche API Carrefour |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Date de création |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Date de modification |

**Indexes** :
- `idx_ingredient_name` sur `name`
- `idx_ingredient_category` sur `category`

**Contraintes métier** :
- `carrefour_search_term` doit être NULL si `category = FRAIS_ARTISAN`
- `name` est case-insensitive unique

---

### `recipes`

Stocke les recettes de cuisine.

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| id | VARCHAR(36) | PK | UUID de la recette |
| name | VARCHAR(200) | NOT NULL | Nom de la recette |
| description | TEXT | NULLABLE | Description détaillée |
| season | ENUM | NOT NULL, INDEX | PRINTEMPS, ETE, AUTOMNE, HIVER, ANNEE |
| difficulty | ENUM | NOT NULL | FACILE, MOYEN, DIFFICILE |
| prep_time_minutes | INTEGER | NOT NULL | Temps de préparation |
| portions | INTEGER | NOT NULL | Nombre de personnes |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Date de création |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Date de modification |

**Indexes** :
- `idx_recipe_season` sur `season`

---

### `recipe_ingredients`

Table d'association many-to-many entre recettes et ingrédients.

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| recipe_id | VARCHAR(36) | PK, FK → recipes(id) | ID de la recette |
| ingredient_id | VARCHAR(36) | PK, FK → ingredients(id) | ID de l'ingrédient |
| quantity | DECIMAL(10,2) | NOT NULL | Quantité requise |
| unit | ENUM | NOT NULL | PIECE, KG, G, L, ML, CUILLERE_SOUPE, CUILLERE_CAFE, PINCEE |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Date de création |

**Primary Key** : Composite `(recipe_id, ingredient_id)`

**Foreign Keys** :
- `recipe_id` → `recipes.id` ON DELETE CASCADE
- `ingredient_id` → `ingredients.id` ON DELETE CASCADE

---

## Enums

### `Season`
- PRINTEMPS
- ETE
- AUTOMNE
- HIVER
- ANNEE

### `Difficulty`
- FACILE
- MOYEN
- DIFFICILE

### `IngredientCategory`
- SEC
- FRAIS_GMS
- FRAIS_ARTISAN

### `UnitType`
- PIECE
- KG
- G
- L
- ML
- CUILLERE_SOUPE
- CUILLERE_CAFE
- PINCEE

---

## Décisions de Conception

### Pourquoi `unit` dans RecipeIngredient et pas dans Ingredient ?

Un même ingrédient peut avoir des unités différentes selon les recettes :
- "Farine" peut être en KG (pain) ou G (gâteau)
- "Tomate" peut être en PIECE (salade) ou KG (sauce)

Cette approche est plus flexible et évite la duplication d'ingrédients.

### Pourquoi `carrefour_search_term` nullable ?

Les ingrédients FRAIS_ARTISAN ne sont pas commandables via API Carrefour (pain artisan, viande du boucher...). Ce champ est donc inutile pour cette catégorie.

### Pourquoi composite primary key pour RecipeIngredient ?

Empêche les doublons (même ingrédient 2x dans une recette) et optimise les JOINs.

---

## Migrations (Phase 2)

Pour POC : Utiliser `Base.metadata.create_all(engine)`  
Pour Production : Utiliser Alembic pour versionner les changements

---

## Exemples de Données

**Ingredient**
```python
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Tomate",
  "category": "FRAIS_ARTISAN",
  "carrefour_search_term": null,
  "created_at": "2026-01-02T10:00:00Z",
  "updated_at": "2026-01-02T10:00:00Z"
}
```

**Recipe**
```python
{
  "id": "650e8400-e29b-41d4-a716-446655440001",
  "name": "Ratatouille",
  "description": "Légumes du soleil mijotés",
  "season": "ETE",
  "difficulty": "MOYEN",
  "prep_time_minutes": 45,
  "portions": 4,
  "created_at": "2026-01-02T10:00:00Z",
  "updated_at": "2026-01-02T10:00:00Z"
}
```

**RecipeIngredient**
```python
{
  "recipe_id": "650e8400-e29b-41d4-a716-446655440001",
  "ingredient_id": "550e8400-e29b-41d4-a716-446655440000",
  "quantity": 3.0,
  "unit": "PIECE",
  "created_at": "2026-01-02T10:00:00Z"
}
```
```

---

## ✅ Critères de Validation

**Fichiers créés** :
- [ ] `src/models/enums.py` avec tous les Enums
- [ ] `src/models/base.py` avec Base SQLAlchemy
- [ ] `src/models/ingredient.py` avec modèle Ingredient
- [ ] `src/models/recipe.py` avec modèles Recipe et RecipeIngredient
- [ ] `src/models/__init__.py` qui expose tous les modèles
- [ ] `docs/database_schema.md` avec documentation complète

**Qualité du code** :
- [ ] Type hints sur tous les modèles
- [ ] Docstrings sur classes et méthodes
- [ ] Relations bidirectionnelles (`back_populates`)
- [ ] Cascade DELETE configuré correctement
- [ ] Timestamps automatiques (created_at, updated_at)

**Contraintes métier** :
- [ ] UUIDs générés automatiquement
- [ ] `carrefour_search_term` nullable
- [ ] Composite PK sur RecipeIngredient
- [ ] Indexes sur champs fréquemment filtrés
- [ ] Enums en français (PRINTEMPS, ETE, etc.)

**Tests manuels** :
- [ ] Import de tous les modèles sans erreur
- [ ] Création d'instances de test sans erreur
- [ ] Vérification des types Enum

---

## 📝 Notes d'Implémentation

### Pour SQLAlchemy

1. **Timestamps** : Utiliser `datetime.now(timezone.utc)` pour éviter problèmes de timezone
2. **UUID** : Générer côté Python avec `uuid.uuid4()` (pas AUTO_INCREMENT)
3. **Enums** : Utiliser `sqlalchemy.Enum` avec `values_callable` pour intégrer les Enums Python
4. **Relations** : Toujours utiliser `back_populates` pour navigation bidirectionnelle
5. **Cascade** : `cascade="all, delete-orphan"` sur les relations one-to-many

### Pour Pydantic (Phase suivante)

Créer des schémas séparés pour :
- `IngredientCreate`, `IngredientUpdate`, `IngredientResponse`
- `RecipeCreate`, `RecipeUpdate`, `RecipeResponse`

### Ordre d'Implémentation

1. `enums.py` (pas de dépendances)
2. `base.py` (pas de dépendances)
3. `ingredient.py` (dépend de base + enums)
4. `recipe.py` (dépend de base + enums + ingredient)
5. `__init__.py` (expose tout)
6. `database_schema.md` (documentation)

---

## 🔗 Liens

- **Notion - TASK-001** : https://www.notion.so/2dc15cc889a081aa8c6ac1c671799023
- **Notion - Architecture Backend** : https://www.notion.so/2dc15cc889a08144a0cac67ae09d9c01
- **Notion - Modèle de Données** : https://www.notion.so/2dc15cc889a081f796d0cf78582adc87

---

## 🚀 Commandes pour Claude Code

```bash
# Dans le terminal, après avoir pull les specs
cd grocery-automation-poc

# Lancer Claude Code
claude-code

# Dans Claude Code, dire :
"Lis le fichier .claude/tasks/TASK-001-conception-modele-donnees.md et implémente-le complètement :
- Crée tous les fichiers models
- Vérifie que les imports fonctionnent
- Commit avec message : feat: implement data models with SQLAlchemy (task #1)"
```

---

**Fin de TASK-001**
