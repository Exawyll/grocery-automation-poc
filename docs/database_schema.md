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
