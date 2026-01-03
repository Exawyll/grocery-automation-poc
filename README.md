# Grocery Automation POC

API backend Python avec FastAPI pour gérer des recettes et générer automatiquement des listes de courses.

## Fonctionnalités

- **Gestion des recettes** : Créer, lire, modifier et supprimer des recettes
- **Gestion des ingrédients** : Base de données d'ingrédients avec catégories
- **Listes de courses automatisées** : Générer automatiquement des listes de courses à partir de recettes
- **Planification hebdomadaire** : Suggérer des plans de repas pour la semaine
- **Intégration Carrefour API** : Estimation des coûts et recherche de produits (en simulation)
- **Organisation par catégories** : Trier les listes de courses par catégories

## Structure du projet

```
grocery-automation-poc/
├── src/
│   ├── models/
│   │   ├── recipe.py          # Modèle Recette
│   │   ├── ingredient.py      # Modèle Ingrédient
│   │   └── shopping_list.py   # Modèle Liste de courses
│   ├── services/
│   │   ├── recipe_service.py  # Logique métier recettes
│   │   ├── carrefour_api.py   # Intégration API Carrefour
│   │   └── planning_service.py # Planification hebdomadaire
│   ├── api/
│   │   ├── routes/
│   │   │   ├── recipes.py     # Endpoints recettes
│   │   │   └── shopping.py    # Endpoints courses
│   │   └── main.py            # Point d'entrée FastAPI
│   └── database.py            # Configuration BDD
├── tests/
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

## Installation

1. Cloner le repository :
```bash
git clone <repository-url>
cd grocery-automation-poc
```

2. Créer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Configurer les variables d'environnement :
```bash
cp .env.example .env
# Éditer .env avec vos configurations
```

## Démarrage

Lancer le serveur en mode développement :
```bash
python -m src.api.main
```

Ou avec uvicorn directement :
```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

L'API sera accessible à : `http://localhost:8000`

Documentation interactive : `http://localhost:8000/docs`

## Endpoints principaux

### Recettes

- `POST /api/recipes/` - Créer une recette
- `GET /api/recipes/` - Lister toutes les recettes
- `GET /api/recipes/{id}` - Récupérer une recette avec ses ingrédients
- `PUT /api/recipes/{id}` - Mettre à jour une recette
- `DELETE /api/recipes/{id}` - Supprimer une recette
- `GET /api/recipes/search/?q=query` - Rechercher des recettes

### Ingrédients

- `POST /api/ingredients/` - Créer un ingrédient
- `GET /api/ingredients/` - Lister tous les ingrédients
- `GET /api/ingredients/{id}` - Récupérer un ingrédient
- `DELETE /api/ingredients/{id}` - Supprimer un ingrédient

### Listes de courses

- `POST /api/shopping/` - Créer une liste de courses
- `GET /api/shopping/` - Lister toutes les listes
- `GET /api/shopping/{id}` - Récupérer une liste avec ses articles
- `DELETE /api/shopping/{id}` - Supprimer une liste
- `POST /api/shopping/from-recipes` - Générer une liste depuis des recettes
- `PATCH /api/shopping/{id}/items/{ingredient_id}/check` - Cocher/décocher un article
- `GET /api/shopping/{id}/by-category` - Liste organisée par catégories
- `GET /api/shopping/{id}/estimate-cost` - Estimer le coût total

### Planification

- `GET /api/planning/weekly-meal-plan` - Suggérer un plan de repas hebdomadaire

## Exemples d'utilisation

### Créer un ingrédient

```bash
curl -X POST "http://localhost:8000/api/ingredients/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Tomates",
    "category": "Légumes",
    "unit": "kg"
  }'
```

### Créer une recette

```bash
curl -X POST "http://localhost:8000/api/recipes/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sauce tomate maison",
    "description": "Une délicieuse sauce tomate",
    "servings": 4,
    "prep_time": 10,
    "cook_time": 30,
    "instructions": "1. Couper les tomates\n2. Faire revenir...",
    "ingredients": [
      {
        "ingredient_id": 1,
        "quantity": 1.5,
        "unit": "kg"
      }
    ]
  }'
```

### Générer une liste de courses depuis des recettes

```bash
curl -X POST "http://localhost:8000/api/shopping/from-recipes" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Courses de la semaine",
    "recipe_ids": [1, 2, 3],
    "servings_multiplier": {
      "1": 2.0,
      "2": 1.5
    }
  }'
```

## Technologies utilisées

- **FastAPI** : Framework web moderne et rapide
- **SQLAlchemy** : ORM pour la gestion de base de données
- **Pydantic** : Validation de données et sérialisation
- **SQLite** : Base de données (peut être remplacée par PostgreSQL)
- **Uvicorn** : Serveur ASGI
- **Python 3.10+**

## Développement futur

- [ ] Authentification utilisateur
- [ ] Export des listes de courses (PDF, Email)
- [ ] Intégration réelle avec l'API Carrefour
- [ ] Suggestions de recettes basées sur les ingrédients disponibles
- [ ] Gestion des allergies et préférences alimentaires
- [ ] Application mobile ou interface web

## Licence

MIT
