"""Tests de integración de límites HTTP (T4.2)."""

from typing import cast

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.ratelimit import DailyBudget, SlidingWindowLimiter, parse_limits
from app.main import create_app


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


def test_rate_limit_returns_429_with_retry_after() -> None:
    with TestClient(create_app()) as client:
        app = cast(FastAPI, client.app)
        app.state.chat_limiter = SlidingWindowLimiter(parse_limits("1/minute"), clock=FakeClock())

        first = client.post("/ask", json={"message": "hola"})
        assert first.status_code == 503

        second = client.post("/ask", json={"message": "hola"})
        assert second.status_code == 429
        assert second.headers["Retry-After"] == "60"
        assert second.json() == {"code": "rate_limited", "retry_after_s": 60}


def test_daily_budget_returns_429() -> None:
    with TestClient(create_app()) as client:
        app = cast(FastAPI, client.app)
        app.state.chat_budget = DailyBudget(1, clock=lambda: 0.0)

        first = client.post("/ask", json={"message": "hola"})
        assert first.status_code == 503

        second = client.post("/ask", json={"message": "hola"})
        assert second.status_code == 429
        assert second.json() == {"code": "daily_budget_exhausted"}


def test_body_too_large_is_rejected_with_413() -> None:
    with TestClient(create_app()) as client:
        response = client.post(
            "/api/contact",
            content=b"x" * 20000,
            headers={"content-type": "application/json"},
        )

        assert response.status_code == 413
        assert response.json() == {"code": "payload_too_large"}
