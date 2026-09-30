"""Suite de seguridad e integración (T4.10) — cubre R1-R10 de extremo a extremo."""

import asyncio
import json
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any, cast

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.ratelimit import SlidingWindowLimiter, parse_limits
from app.features.chat.sanitize import detect_injection, is_explicit_extraction
from app.llm.base import LLMProvider, Message, ProviderHealth, Token
from app.llm.health import HealthMonitor, MonitorConfig
from app.llm.router import LLMRouter
from app.main import create_app
from app.rag.chunking import chunk_note
from app.rag.ingest import extract_public_notes
from tests.integration.test_chat_sse import (
    FakeRetriever,
    StubProvider,
    _events,
    _retrieval,
    _router,
)

ROOT = Path(__file__).resolve().parents[3]


class EchoPromptProvider:
    """Simula un modelo que filtra el prompt de sistema (peor caso)."""

    name = "tower"
    model = "tower-model"

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
        yield Token(text=messages[0].content[:200])


class StormProvider:
    name = "tower"
    model = "tower-model"

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
        for index in range(200):
            await asyncio.sleep(0.001)
            yield Token(text=f"t{index}")


def _redteam() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for line in (ROOT / "eval/redteam.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            cases.append(json.loads(line))
    return cases


def test_redteam_payloads_are_detected() -> None:
    for case in _redteam():
        payload = str(case["payload"])
        if case["expect"] in {"injection", "blocked"}:
            assert detect_injection(payload) or is_explicit_extraction(payload), case["id"]
        if case["expect"] == "blocked":
            assert is_explicit_extraction(payload), case["id"]


def test_redteam_never_leaks_prompt_text() -> None:
    leak_marker = "REGLAS (máxima prioridad"
    provider = EchoPromptProvider()
    monitor = HealthMonitor([cast(LLMProvider, provider)], config=MonitorConfig())
    with TestClient(create_app()) as client:
        app = cast(FastAPI, client.app)
        app.state.retriever = FakeRetriever(_retrieval())
        app.state.llm_router = LLMRouter([cast(LLMProvider, provider)], monitor)
        app.state.chat_limiter = SlidingWindowLimiter(parse_limits("1000/minute"))

        for case in _redteam():
            response = client.post("/api/chat", json={"message": case["payload"]})

            assert response.status_code == 200, case["id"]
            assert leak_marker not in response.text, case["id"]
            assert "token interno" not in response.text, case["id"]
            events = _events(response.text)
            error_codes = {data["code"] for name, data in events if name == "error"}
            assert error_codes <= {"output_blocked"}, case["id"]


def test_blocked_payloads_never_reach_retrieval_nor_llm() -> None:
    provider = StubProvider()
    retriever = FakeRetriever(_retrieval())
    with TestClient(create_app()) as client:
        app = cast(FastAPI, client.app)
        app.state.retriever = retriever
        app.state.llm_router = _router(provider)

        for case in _redteam():
            if case["expect"] != "blocked":
                continue
            response = client.post("/api/chat", json={"message": case["payload"]})
            events = _events(response.text)
            assert [name for name, _ in events] == ["meta", "refusal", "done"], case["id"]
            assert events[1][1]["reason"] == "injection"

    assert retriever.calls == 0
    assert provider.stream_calls == 0


def test_burst_is_rate_limited() -> None:
    with TestClient(create_app()) as client:
        app = cast(FastAPI, client.app)
        app.state.chat_limiter = SlidingWindowLimiter(parse_limits("3/minute"))

        statuses = [
            client.post("/api/chat", json={"message": "hola"}).status_code for _ in range(4)
        ]

    assert statuses[-1] == 429
    assert statuses[0] == 503  # servicio sin claves en test, pero el limitador cuenta


def test_private_canary_never_reaches_the_index() -> None:
    extraction = extract_public_notes(ROOT / "eval/fixtures/vault")
    chunks = [chunk for note in extraction.notes for chunk in chunk_note(note)]

    assert chunks
    assert all("CANARIO_EVAL_NO_PUBLICADA" not in chunk.embedded_text for chunk in chunks)
    assert all("borrador.md" not in chunk.source_id for chunk in chunks)


def test_disallowed_host_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALLOWED_HOSTS", "midominio.test")
    get_settings.cache_clear()
    try:
        with TestClient(create_app(), base_url="http://midominio.test") as client:
            allowed = client.get("/api/health")
        with TestClient(create_app(), base_url="http://otro.test") as client:
            denied = client.get("/api/health")
    finally:
        get_settings.cache_clear()

    assert allowed.status_code == 200
    assert denied.status_code == 400


async def test_cancellation_storm_releases_slots() -> None:
    provider = StormProvider()
    monitor = HealthMonitor([provider], config=MonitorConfig())
    router = LLMRouter([provider], monitor, max_concurrency=2, queue_limit=100)

    async def consume_and_cancel() -> None:
        routed = await router.stream([Message(role="user", content="hola")])
        await routed.__anext__()
        await routed.aclose()

    await asyncio.gather(*(consume_and_cancel() for _ in range(10)))

    first = await router.stream([Message(role="user", content="hola")])
    second = await router.stream([Message(role="user", content="hola")])
    await first.aclose()
    await second.aclose()
