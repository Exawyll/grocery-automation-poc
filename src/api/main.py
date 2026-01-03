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
