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
