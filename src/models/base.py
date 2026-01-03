"""
Base SQLAlchemy pour tous les modèles.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

# Cette config sera remplacée par src/database.py plus tard
# Pour l'instant, on définit juste la Base
