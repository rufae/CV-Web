"""Tests de métricas y health profundo (T7.6)."""

from collections.abc import Iterator
from typing import cast

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import create_app


@pytest.fixture(autouse=True)
def _clear_settings() -> Iterator[None]:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_metrics_disabled_without_token() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/metrics")

    assert response.status_code == 404


def test_metrics_requires_valid_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("METRICS_TOKEN", "secreto")
    get_settings.cache_clear()

    with TestClient(create_app()) as client:
        unauthorized = client.get("/metrics")
        authorized = client.get("/metrics", headers={"x-metrics-token": "secreto"})

    assert unauthorized.status_code == 401
    assert authorized.status_code == 200
    assert "cvweb_chat_requests_total" in authorized.text


def test_deep_health_requires_token_and_reports_state(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("METRICS_TOKEN", "secreto")
    get_settings.cache_clear()

    with TestClient(create_app()) as client:
        response = client.get("/api/health/deep", headers={"x-metrics-token": "secreto"})
        app = cast(FastAPI, client.app)
        app.state.embedder = None

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["llm"]["llm"] == "offline"
    assert body["embed_ok"] is False
    assert "index_age_hours" in body
