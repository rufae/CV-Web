"""Tests del router de proveedores LLM (T2.4)."""

import asyncio
from collections.abc import AsyncGenerator

import pytest

from app.llm.base import Message, ProviderHealth, Token
from app.llm.errors import LLMError, ProviderError, ProviderUnavailable, QueueOverflow
from app.llm.health import HealthMonitor, MonitorConfig
from app.llm.router import LLMRouter


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        self.now += 0.01
        return self.now


class StubLLM:
    def __init__(
        self,
        name: str,
        *,
        model: str | None = None,
        health_ok: bool = True,
        tokens: tuple[str, ...] = ("a", "b"),
        fail_before_first: LLMError | None = None,
        fail_after_first: LLMError | None = None,
        delay_before_first: float = 0.0,
    ) -> None:
        self.name = name
        self.model = model or f"{name}-model"
        self.health_ok = health_ok
        self.tokens = tokens
        self.fail_before_first = fail_before_first
        self.fail_after_first = fail_after_first
        self.delay_before_first = delay_before_first
        self.stream_calls = 0

    async def health(self) -> ProviderHealth:
        return ProviderHealth(ok=self.health_ok, latency_ms=1.0, model=self.model)

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
        if self.fail_before_first is not None:
            raise self.fail_before_first
        if self.delay_before_first:
            await asyncio.sleep(self.delay_before_first)
        for index, text in enumerate(self.tokens):
            if index == 1 and self.fail_after_first is not None:
                raise self.fail_after_first
            yield Token(text=text)


async def _monitor(*providers: StubLLM, down: tuple[str, ...] = ()) -> HealthMonitor:
    for provider in providers:
        provider.health_ok = provider.name not in down
    monitor = HealthMonitor(
        list(providers),
        config=MonitorConfig(ttl_s=1.0, health_timeout_s=1.0, failures_per_step=2),
        clock=FakeClock(),
    )
    for _ in range(4):
        await monitor.check_once()
    return monitor


def _messages() -> list[Message]:
    return [Message(role="user", content="hola")]


async def test_prefers_first_healthy_provider() -> None:
    p1 = StubLLM("p1", tokens=("hola", " mundo"))
    p2 = StubLLM("p2")
    router = LLMRouter([p1, p2], await _monitor(p1, p2))

    routed = await router.stream(_messages())
    tokens = [token.text async for token in routed]

    assert tokens == ["hola", " mundo"]
    assert routed.meta.provider == "p1"
    assert routed.meta.model == "p1-model"
    assert routed.meta.first_token_ms is not None
    assert p2.stream_calls == 0
    assert router.failovers == 0


async def test_skips_down_provider_without_failover_count() -> None:
    p1 = StubLLM("p1")
    p2 = StubLLM("p2", tokens=("b",))
    router = LLMRouter([p1, p2], await _monitor(p1, p2, down=("p1",)))

    routed = await router.stream(_messages())
    tokens = [token.text async for token in routed]

    assert tokens == ["b"]
    assert routed.meta.provider == "p2"
    assert p1.stream_calls == 0
    assert router.failovers == 0


async def test_failover_when_provider_raises_before_first_token() -> None:
    p1 = StubLLM("p1", fail_before_first=ProviderUnavailable("caído"))
    p2 = StubLLM("p2", tokens=("ok",))
    router = LLMRouter([p1, p2], await _monitor(p1, p2))

    routed = await router.stream(_messages())
    tokens = [token.text async for token in routed]

    assert tokens == ["ok"]
    assert routed.meta.provider == "p2"
    assert router.failovers == 1


async def test_failover_when_first_token_is_slow() -> None:
    p1 = StubLLM("p1", delay_before_first=0.2, tokens=("slow",))
    p2 = StubLLM("p2", tokens=("fast",))
    router = LLMRouter([p1, p2], await _monitor(p1, p2), first_token_timeout_s=0.05)

    routed = await router.stream(_messages())
    tokens = [token.text async for token in routed]

    assert tokens == ["fast"]
    assert routed.meta.provider == "p2"
    assert router.failovers == 1


async def test_mid_stream_failure_does_not_switch_provider() -> None:
    p1 = StubLLM("p1", tokens=("a", "b"), fail_after_first=ProviderError("corte"))
    p2 = StubLLM("p2", tokens=("no",))
    router = LLMRouter([p1, p2], await _monitor(p1, p2))

    routed = await router.stream(_messages())
    received: list[str] = []
    with pytest.raises(ProviderError):
        async for token in routed:
            received.append(token.text)

    assert received == ["a"]
    assert p2.stream_calls == 0


async def test_all_providers_down_raises_controlled_error() -> None:
    p1 = StubLLM("p1")
    p2 = StubLLM("p2")
    router = LLMRouter([p1, p2], await _monitor(p1, p2, down=("p1", "p2")))

    with pytest.raises(ProviderUnavailable):
        await router.stream(_messages())


async def test_queue_overflow_raises_with_retry_after() -> None:
    p1 = StubLLM("p1", tokens=("a", "b", "c"))
    router = LLMRouter(
        [p1],
        await _monitor(p1),
        max_concurrency=1,
        queue_limit=0,
        retry_after_s=7,
    )

    first = await router.stream(_messages())
    assert (await first.__anext__()).text == "a"

    with pytest.raises(QueueOverflow) as excinfo:
        await router.stream(_messages())
    assert excinfo.value.retry_after_s == 7

    await first.aclose()
    second = await router.stream(_messages())
    await second.aclose()
