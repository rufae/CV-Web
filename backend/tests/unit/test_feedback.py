"""Tests del feedback anónimo (T4.9)."""

from pathlib import Path
from typing import cast

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.core.config import get_settings
from app.features.feedback.schemas import FeedbackRequest
from app.features.feedback.service import FeedbackService
from app.features.feedback.store import FeedbackStore
from app.main import create_app


def _payload(**overrides: object) -> FeedbackRequest:
    data: dict[str, object] = {
        "message_id": "m1",
        "rating": "down",
        "comment": "no era exacto",
        "prompt_version": "v1",
        "sources": [1, 2],
        "tier": "gpu",
        "refused": False,
    }
    data.update(overrides)
    return FeedbackRequest.model_validate(data)


def test_schema_rejects_long_comment_and_bad_rating() -> None:
    with pytest.raises(ValidationError):
        _payload(comment="x" * 301)
    with pytest.raises(ValidationError):
        _payload(rating="meh")


def test_store_ignores_duplicate_message_id(tmp_path: Path) -> None:
    store = FeedbackStore(tmp_path / "feedback.db")

    assert store.add(_payload()) is True
    assert store.add(_payload()) is False
    assert store.count() == 1


def test_store_exports_only_down_ratings(tmp_path: Path) -> None:
    store = FeedbackStore(tmp_path / "feedback.db")
    store.add(_payload())
    store.add(
        _payload(
            message_id="m2",
            rating="up",
            comment=None,
            sources=[],
            tier=None,
            refused=True,
        )
    )

    downs = store.downs()

    assert len(downs) == 1
    entry = downs[0]
    assert entry.sources == [1, 2]
    assert entry.tier == "gpu"
    assert entry.prompt_version == "v1"
    assert entry.refused is False


def test_service_records(tmp_path: Path) -> None:
    service = FeedbackService(FeedbackStore(tmp_path / "feedback.db"))

    assert service.record(_payload()) is True
    assert service.store.count() == 1


def test_api_records_and_deduplicates(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATA_PATH", str(tmp_path))
    get_settings.cache_clear()
    try:
        with TestClient(create_app()) as client:
            body = {"message_id": "abc", "rating": "down", "comment": "fallo"}
            first = client.post("/api/feedback", json=body)
            second = client.post("/api/feedback", json=body)
            app = cast(FastAPI, client.app)
            count = app.state.feedback_service.store.count()
    finally:
        get_settings.cache_clear()

    assert first.status_code == 200
    assert second.status_code == 200
    assert count == 1
