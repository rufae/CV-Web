"""Tests del cliente de embeddings (T3.4)."""

import httpx
import pytest
import respx

from app.llm.errors import ProviderError, ProviderUnavailable
from app.rag.embeddings import OllamaEmbedder

BASE_URL = "http://dell.test:11434"


def _embedder(batch_size: int = 16) -> OllamaEmbedder:
    return OllamaEmbedder(BASE_URL, "bge-m3", batch_size=batch_size, timeout_s=1.0)


@respx.mock
async def test_embed_returns_vectors_in_order() -> None:
    respx.post(f"{BASE_URL}/api/embed").mock(
        return_value=httpx.Response(200, json={"embeddings": [[1.0, 0.0], [0.0, 1.0]]})
    )
    embedder = _embedder()

    vectors = await embedder.embed(["a", "b"])
    await embedder.aclose()

    assert vectors == [[1.0, 0.0], [0.0, 1.0]]


@respx.mock
async def test_embed_batches_requests() -> None:
    route = respx.post(f"{BASE_URL}/api/embed").mock(
        side_effect=[
            httpx.Response(200, json={"embeddings": [[1.0]]}),
            httpx.Response(200, json={"embeddings": [[2.0]]}),
        ]
    )
    embedder = _embedder(batch_size=1)

    vectors = await embedder.embed(["a", "b"])
    await embedder.aclose()

    assert route.call_count == 2
    assert vectors == [[1.0], [2.0]]


@respx.mock
async def test_embed_maps_connection_error() -> None:
    respx.post(f"{BASE_URL}/api/embed").mock(side_effect=httpx.ConnectError("boom"))
    embedder = _embedder()

    with pytest.raises(ProviderUnavailable):
        await embedder.embed(["a"])

    await embedder.aclose()


@respx.mock
async def test_embed_maps_http_error() -> None:
    respx.post(f"{BASE_URL}/api/embed").mock(return_value=httpx.Response(500))
    embedder = _embedder()

    with pytest.raises(ProviderError):
        await embedder.embed(["a"])

    await embedder.aclose()


@respx.mock
async def test_embed_rejects_mismatched_payload() -> None:
    respx.post(f"{BASE_URL}/api/embed").mock(
        return_value=httpx.Response(200, json={"embeddings": []})
    )
    embedder = _embedder()

    with pytest.raises(ProviderError):
        await embedder.embed(["a"])

    await embedder.aclose()


@respx.mock
async def test_embed_empty_list_makes_no_calls() -> None:
    route = respx.post(f"{BASE_URL}/api/embed").mock(return_value=httpx.Response(200, json={}))
    embedder = _embedder()

    assert await embedder.embed([]) == []
    assert route.call_count == 0

    await embedder.aclose()
