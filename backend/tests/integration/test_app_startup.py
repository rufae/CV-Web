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
    body = response.json()
    assert body["llm"] == "offline"
    assert body["tier"] == "cpu"
    # Estado en vivo (2026-10-01): sin peticiones aun no hay percentiles.
    assert body["p50_ms"] is None
    assert body["p95_ms"] is None
    assert body["samples"] == 0
