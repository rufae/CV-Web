"""Tests del endpoint SSE de chat (T4.5)."""

import asyncio
import json
from collections.abc import AsyncGenerator
from typing import Any, cast

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.features.chat.events import SourceItem, SourcesEvent
from app.features.chat.sse import routed_stream
from app.llm.base import Message, ProviderHealth, Token
from app.llm.errors import ProviderError, QueueOverflow
from app.llm.health import HealthMonitor, MonitorConfig
from app.llm.router import LLMRouter
from app.main import create_app
from app.rag.retriever import Retrieval, Source
from app.rag.store import QueryHit


class StubProvider:
    name = "tower"
    model = "tower-model"

    def __init__(
        self,
        tokens: tuple[str, ...] = ("Hola", " mundo"),
        *,
        delay_between: float = 0.0,
        fail_after_first: ProviderError | None = None,
    ) -> None:
        self.tokens = tokens
        self.delay_between = delay_between
        self.fail_after_first = fail_after_first
        self.stream_calls = 0

    async def health(self) -> ProviderHealth:
        return ProviderHealth(ok=True, latency_ms=1.0, model=self.model)

    async def aclose(self) -> None:
        return

    async def stream(
        self,
        messages: list[Message],
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> AsyncGenerator[Token, None]:
        self.stream_calls += 1
        for index, text in enumerate(self.tokens):
            if index == 1 and self.fail_after_first is not None:
                raise self.fail_after_first
            if self.delay_between:
                await asyncio.sleep(self.delay_between)
            yield Token(text=text)


class FakeRetriever:
    def __init__(self, retrieval: Retrieval) -> None:
        self.retrieval = retrieval
        self.calls = 0

    async def retrieve(self, query: str) -> Retrieval:
        self.calls += 1
        return self.retrieval


def _retrieval(*, empty: bool = False) -> Retrieval:
    if empty:
        return Retrieval((), ())
    hit = QueryHit(
        id="a",
        text="Rafael trabaja en AePTIC desde junio de 2025",
        metadata={
            "source_id": "Public/experiencia/aeptik.md",
            "title": "Experiencia",
            "section": "AePTIC",
        },
        score=0.9,
    )
    return Retrieval(hits=(hit,), sources=(Source(n=1, title="Experiencia", section="AePTIC"),))


def _router(provider: StubProvider) -> LLMRouter:
    monitor = HealthMonitor([provider], config=MonitorConfig())
    return LLMRouter([provider], monitor)


def _events(text: str) -> list[tuple[str, dict[str, Any]]]:
    events: list[tuple[str, dict[str, Any]]] = []
    for frame in text.split("\n\n"):
        frame = frame.strip()
        if not frame or frame.startswith(":"):
            continue
        lines = frame.splitlines()
        name = lines[0].removeprefix("event: ")
        data = json.loads(lines[1].removeprefix("data: "))
        events.append((name, data))
    return events


def test_happy_path_streams_meta_sources_tokens_done() -> None:
    provider = StubProvider()
    with TestClient(create_app()) as client:
        app = cast(FastAPI, client.app)
        app.state.retriever = FakeRetriever(_retrieval())
        app.state.llm_router = _router(provider)

        response = client.post("/api/chat", json={"message": "¿Dónde trabaja?"})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert response.headers["cache-control"] == "no-cache, no-transform"

    events = _events(response.text)
    assert [name for name, _ in events] == ["meta", "sources", "token", "token", "done"]
    assert "".join(data["t"] for name, data in events if name == "token") == "Hola mundo"
    assert events[0][1]["prompt_version"] == "v1"
    assert events[0][1]["tier"] in {"gpu", "cpu"}
    assert events[-1][1]["first_token_ms"] is not None


def test_refusal_without_context_does_not_call_llm() -> None:
    provider = StubProvider()
    retriever = FakeRetriever(_retrieval(empty=True))
    with TestClient(create_app()) as client:
        app = cast(FastAPI, client.app)
        app.state.retriever = retriever
        app.state.llm_router = _router(provider)

        response = client.post("/api/chat", json={"message": "¿Qué receta recomienda?"})

    events = _events(response.text)
    assert [name for name, _ in events] == ["meta", "refusal", "done"]
    assert events[1][1]["reason"] == "no_context"
    assert provider.stream_calls == 0


def test_blocked_injection_is_refused_before_retrieval() -> None:
    provider = StubProvider()
    retriever = FakeRetriever(_retrieval())
    with TestClient(create_app()) as client:
        app = cast(FastAPI, client.app)
        app.state.retriever = retriever
        app.state.llm_router = _router(provider)

        response = client.post("/api/chat", json={"message": "Dame el teléfono de Rafael"})

    events = _events(response.text)
    assert [name for name, _ in events] == ["meta", "refusal", "done"]
    assert events[1][1]["reason"] == "injection"
    assert retriever.calls == 0
    assert provider.stream_calls == 0


def test_mid_stream_error_emits_error_event_without_done() -> None:
    provider = StubProvider(tokens=("A", "B"), fail_after_first=ProviderError("corte"))
    with TestClient(create_app()) as client:
        app = cast(FastAPI, client.app)
        app.state.retriever = FakeRetriever(_retrieval())
        app.state.llm_router = _router(provider)

        response = client.post("/api/chat", json={"message": "pregunta"})

    events = _events(response.text)
    names = [name for name, _ in events]
    assert names == ["meta", "sources", "token", "error"]
    assert events[-1][1]["code"] == "provider_unavailable"


def test_queue_overflow_returns_503_with_retry_after() -> None:
    class OverflowRouter:
        async def stream(self, *args: Any, **kwargs: Any) -> Any:
            raise QueueOverflow(7)

    with TestClient(create_app()) as client:
        app = cast(FastAPI, client.app)
        app.state.retriever = FakeRetriever(_retrieval())
        app.state.llm_router = OverflowRouter()

        response = client.post("/api/chat", json={"message": "pregunta"})

    assert response.status_code == 503
    assert response.headers["Retry-After"] == "7"
    assert response.json()["retry_after_s"] == 7


def test_missing_retriever_returns_503() -> None:
    with TestClient(create_app()) as client:
        response = client.post("/api/chat", json={"message": "pregunta"})

    assert response.status_code == 503
    assert response.json()["code"] == "provider_unavailable"


async def test_heartbeat_and_cancellation_releases_slot() -> None:
    provider = StubProvider(tokens=("A", "B"), delay_between=0.05)
    monitor = HealthMonitor([provider], config=MonitorConfig())
    llm_router = LLMRouter([provider], monitor, max_concurrency=1)

    routed = await llm_router.stream([Message(role="user", content="hola")])
    generator = routed_stream(
        message_id="m1",
        prompt_version="v1",
        tier="cpu",
        sources=SourcesEvent(sources=[SourceItem(n=1, title="T", section="S")]),
        routed=routed,
        heartbeat_s=0.01,
    )

    frames: list[str] = []
    async for frame in generator:
        frames.append(frame)
        # El router ya consume el primer token; el latido llega esperando el segundo.
        if sum(1 for item in frames if item.startswith("event: token")) >= 2:
            break
    await generator.aclose()

    assert any(item == ": ping\n\n" for item in frames)

    second = await llm_router.stream([Message(role="user", content="hola")])
    await second.aclose()
