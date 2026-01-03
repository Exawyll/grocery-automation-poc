#!/usr/bin/env python3
"""Script pour initialiser la base de données.

Ce script crée toutes les tables définies dans les models SQLAlchemy.
Il est idempotent : peut être exécuté plusieurs fois sans problème.

Usage:
    python scripts/init_db.py
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database import init_db

if __name__ == "__main__":
    print("🚀 Initializing database...")
    init_db()
    print("✅ Done!")
