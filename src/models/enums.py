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
