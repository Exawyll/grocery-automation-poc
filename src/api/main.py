from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.database import init_db
from src.api.routes import recipes, shopping

app = FastAPI(
    title="Grocery Automation API",
    description="API pour gérer des recettes et générer automatiquement des listes de courses",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les origines autorisées
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialiser la base de données au démarrage
@app.on_event("startup")
def on_startup():
    init_db()


# Routes principales
@app.get("/", tags=["Root"])
def read_root():
    return {
        "message": "Bienvenue sur l'API Grocery Automation",
        "version": "1.0.0",
        "documentation": "/docs"
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}


# Enregistrer les routers
app.include_router(recipes.router, prefix="/api")
app.include_router(recipes.ingredient_router, prefix="/api")
app.include_router(shopping.router, prefix="/api")
app.include_router(shopping.planning_router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
