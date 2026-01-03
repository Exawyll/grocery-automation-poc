"""Tests pour les endpoints système de l'API."""

import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Test de l'endpoint racine /.

    Vérifie que la page d'accueil renvoie les bonnes informations.
    """
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Grocery Automation API"
    assert "docs" in data
    assert "health" in data


def test_health_check(client: TestClient):
    """Test du health check.

    Vérifie que l'endpoint /health renvoie le bon statut
    et les informations de l'application.
    """
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "app" in data
    assert "version" in data
    assert "environment" in data


def test_docs_accessible(client: TestClient):
    """Test que Swagger UI est accessible.

    Vérifie que la documentation interactive est disponible.
    """
    response = client.get("/docs")
    assert response.status_code == 200


def test_redoc_accessible(client: TestClient):
    """Test que ReDoc est accessible.

    Vérifie que la documentation alternative est disponible.
    """
    response = client.get("/redoc")
    assert response.status_code == 200
