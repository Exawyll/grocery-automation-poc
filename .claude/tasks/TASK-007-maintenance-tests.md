# TASK-007 : Maintenance - Réparer tests préexistants (session fixture)

## 🎯 Objectif

Réparer les **17 tests préexistants** qui échouent suite au refactoring du fixture `session` → `db_session` réalisé lors de TASK-003.

**Contexte :** Le commit `8a7e977` a modifié `tests/conftest.py` pour résoudre des problèmes de partage de session. Les anciens tests utilisent encore l'ancien nom de fixture.

## 🐛 Problème Identifié

```bash
# Erreur typique
fixture 'session' not found
available fixtures: db_session, test_client, ...
```

Les tests de TASK-001 et TASK-002 référencent un fixture `session` qui a été renommé en `db_session`.

## 📁 Fichiers à Analyser/Modifier

### Fichiers de tests à corriger (probablement) :
```
tests/
├── test_models/
│   ├── test_ingredient.py      # Tests modèle Ingredient
│   ├── test_recipe.py          # Tests modèle Recipe  
│   └── test_recipe_ingredient.py  # Tests relation
├── test_database/
│   └── test_config.py          # Tests configuration DB
└── conftest.py                 # Fixture principal (déjà modifié)
```

## 💻 Procédure de Correction

### Étape 1 : Diagnostic complet
```bash
# Lancer tous les tests pour identifier les échecs
pytest -v --tb=short 2>&1 | grep -E "(FAILED|ERROR|fixture)"
```

### Étape 2 : Correction des fixtures

**Option A - Renommer les usages** (recommandé si `db_session` est le nouveau standard) :
```python
# Avant
def test_create_ingredient(session):
    ingredient = Ingredient(name="Test", ...)
    session.add(ingredient)

# Après  
def test_create_ingredient(db_session):
    ingredient = Ingredient(name="Test", ...)
    db_session.add(ingredient)
```

**Option B - Ajouter un alias** (si compatibilité arrière nécessaire) :
```python
# Dans conftest.py
@pytest.fixture
def session(db_session):
    """Alias pour compatibilité avec anciens tests"""
    return db_session
```

### Étape 3 : Vérifier le fixture db_session actuel
```python
# Vérifier dans conftest.py que db_session :
# - Crée une session de test isolée
# - Fait le rollback après chaque test
# - Ne partage pas l'état entre tests
```

## ✅ Critères de Validation

- [ ] `pytest -v tests/test_models/` → 100% pass
- [ ] `pytest -v tests/test_database/` → 100% pass
- [ ] `pytest -v tests/test_services/` → 100% pass (TASK-003)
- [ ] `pytest -v tests/test_api/` → 100% pass (TASK-003)
- [ ] `pytest -v` → **Tous les tests passent** (aucun skip, aucun fail)
- [ ] Les tests restent isolés (pas de pollution entre tests)

## 📝 Commit

```bash
git add tests/
git commit -m "fix: repair legacy tests after session fixture refactor (task #7)

- Rename session → db_session in test_models/
- Rename session → db_session in test_database/
- Ensure all 40+ tests pass
- No regressions in TASK-003 tests"
```

## 🔍 Points d'Attention

1. **Ne pas modifier la logique des tests** - juste les noms de fixtures
2. **Vérifier l'isolation** - chaque test doit être indépendant
3. **Garder db_session comme standard** - c'est plus explicite que `session`
4. **Documenter si nécessaire** - ajouter un commentaire dans conftest.py

## 📊 Résultat Attendu

```bash
$ pytest -v
========================= test session starts ==========================
...
tests/test_api/test_health.py::test_health_check PASSED
tests/test_api/test_ingredients.py::test_create_ingredient PASSED
... (tous les tests)
========================= XX passed in X.XXs ===========================
```

## 🔗 Liens

- **Causé par :** Commit 8a7e977 (TASK-003)
- **Bloque :** Merge de `task/003-crud-ingredients` → `main`
- **Notion :** https://www.notion.so/2de15cc889a081e884daea19df05f5a7
