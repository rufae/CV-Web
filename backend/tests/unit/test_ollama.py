"""Tests del proveedor Ollama (T2.2) con servidor mock (`respx`)."""

import json

import httpx
import pytest
import respx

from app.llm.base import Message
from app.llm.errors import FirstTokenTimeout, ProviderError, ProviderUnavailable
from app.llm.ollama import OllamaProvider

BASE_URL = "http://ollama.test:11434"


def _provider() -> OllamaProvider:
    return OllamaProvider(BASE_URL, "test-model", connect_timeout_s=0.2, read_timeout_s=1.0)


def _ndjson(*chunks: dict[str, object]) -> bytes:
    return ("\n".join(json.dumps(chunk) for chunk in chunks) + "\n").encode()


def _user_message() -> list[Message]:
    return [Message(role="user", content="hola")]


@respx.mock
async def test_stream_yields_tokens_until_done() -> None:
    respx.post(f"{BASE_URL}/api/chat").mock(
        return_value=httpx.Response(
            200,
            content=_ndjson(
                {"message": {"content": "Hola"}, "done": False},
                {"message": {"content": " Rafa"}, "done": False},
                {"message": {"content": ""}, "done": True},
            ),
        )
    )
    provider = _provider()

    tokens = [token.text async for token in provider.stream(_user_message())]
    await provider.aclose()

    assert tokens == ["Hola", " Rafa"]


@respx.mock
async def test_stream_maps_connection_error_to_unavailable() -> None:
    respx.post(f"{BASE_URL}/api/chat").mock(side_effect=httpx.ConnectError("boom"))
    provider = _provider()

    with pytest.raises(ProviderUnavailable):
        async for _ in provider.stream(_user_message()):
            pass

    await provider.aclose()


@respx.mock
async def test_stream_maps_read_timeout_to_first_token_timeout() -> None:
    respx.post(f"{BASE_URL}/api/chat").mock(side_effect=httpx.ReadTimeout("slow"))
    provider = _provider()

    with pytest.raises(FirstTokenTimeout):
        async for _ in provider.stream(_user_message()):
            pass

    await provider.aclose()


@respx.mock
async def test_stream_maps_invalid_ndjson_to_provider_error() -> None:
    respx.post(f"{BASE_URL}/api/chat").mock(
        return_value=httpx.Response(200, content=b"esto no es json\n")
    )
    provider = _provider()

    with pytest.raises(ProviderError):
        async for _ in provider.stream(_user_message()):
            pass

    await provider.aclose()


@respx.mock
async def test_health_ok_when_model_is_available() -> None:
    respx.get(f"{BASE_URL}/api/tags").mock(
        return_value=httpx.Response(200, json={"models": [{"name": "test-model:latest"}]})
    )
    provider = _provider()

    health = await provider.health()
    await provider.aclose()

    assert health.ok
    assert health.model == "test-model"
    assert health.latency_ms is not None


@respx.mock
async def test_health_not_ok_when_model_is_missing() -> None:
    respx.get(f"{BASE_URL}/api/tags").mock(
        return_value=httpx.Response(200, json={"models": [{"name": "otro-modelo:latest"}]})
    )
    provider = _provider()

    health = await provider.health()
    await provider.aclose()

    assert not health.ok


@respx.mock
async def test_cancellation_closes_stream_and_keeps_provider_usable() -> None:
    respx.post(f"{BASE_URL}/api/chat").mock(
        return_value=httpx.Response(
            200,
            content=_ndjson(
                {"message": {"content": "A"}, "done": False},
                {"message": {"content": "B"}, "done": False},
                {"message": {"content": ""}, "done": True},
            ),
        )
    )
    respx.get(f"{BASE_URL}/api/tags").mock(
        return_value=httpx.Response(200, json={"models": [{"name": "test-model:latest"}]})
    )
    provider = _provider()

    stream = provider.stream(_user_message())
    first = await stream.__anext__()
    assert first.text == "A"
    await stream.aclose()

    health = await provider.health()
    await provider.aclose()

    assert health.ok
