"""Tests del proveedor Gemini opcional (T2.5)."""

from types import SimpleNamespace
from typing import Any, cast

import pytest
from google import genai

from app.llm.base import Message
from app.llm.errors import ProviderError
from app.llm.gemini import GeminiProvider


class FakeAioModels:
    def __init__(
        self,
        chunks: list[str | None] | None = None,
        error: Exception | None = None,
    ) -> None:
        self.chunks = chunks or []
        self.error = error

    async def generate_content_stream(self, **kwargs: Any) -> Any:
        if self.error is not None:
            raise self.error
        chunks = self.chunks

        async def generator() -> Any:
            for chunk in chunks:
                yield SimpleNamespace(text=chunk)

        return generator()

    async def get(self, **kwargs: Any) -> Any:
        if self.error is not None:
            raise self.error
        return SimpleNamespace(name="models/gemini-2.5-flash")


class FakeClient:
    def __init__(self, models: FakeAioModels) -> None:
        self.aio = SimpleNamespace(models=models)


def _provider(models: FakeAioModels) -> GeminiProvider:
    return GeminiProvider("dummy-key", client=cast(genai.Client, FakeClient(models)))


def _messages() -> list[Message]:
    return [Message(role="user", content="hola")]


async def test_stream_yields_text_chunks() -> None:
    provider = _provider(FakeAioModels(chunks=["Hola", None, " Rafa"]))

    tokens = [token.text async for token in provider.stream(_messages())]

    assert tokens == ["Hola", " Rafa"]


async def test_stream_maps_errors_to_provider_error() -> None:
    provider = _provider(FakeAioModels(error=RuntimeError("boom")))

    with pytest.raises(ProviderError):
        async for _ in provider.stream(_messages()):
            pass


async def test_health_ok_when_model_is_reachable() -> None:
    provider = _provider(FakeAioModels())

    health = await provider.health()

    assert health.ok
    assert health.model == "models/gemini-2.5-flash"
    assert health.latency_ms is not None


async def test_health_not_ok_on_failure() -> None:
    provider = _provider(FakeAioModels(error=RuntimeError("sin red")))

    health = await provider.health()

    assert not health.ok
