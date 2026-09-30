"""Tests de arranque y salud de la aplicación (T1.3)."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_health_endpoint() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_status_endpoint_without_providers() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/api/status")
    assert response.status_code == 200
    assert response.json() == {"llm": "offline", "tier": "cpu"}
