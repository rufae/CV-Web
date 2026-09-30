"""Escenarios de caos del router y la monitorización (T7.8).

Complementan a los tests unitarios: verifican el comportamiento controlado ante
fallos combinados (sin trazas para el usuario).
"""

from collections.abc import AsyncGenerator

import pytest

from app.llm.base import Message, Token
from app.llm.errors import FirstTokenTimeout, ProviderError, ProviderUnavailable
from app.llm.health import HealthMonitor, MonitorConfig
from app.llm.router import LLMRouter
from tests.integration.test_chat_sse import StubProvider


def _messages() -> list[Message]:
    return [Message(role="user", content="hola")]


async def test_both_providers_down_is_controlled_error() -> None:
    first = StubProvider()
    first.name = "tower"
    second = StubProvider()
    second.name = "dell"
    monitor = HealthMonitor([first, second], config=MonitorConfig())
    router = LLMRouter([first, second], monitor)

    async def unavailable(
        self: StubProvider, messages: list[Message], **_: object
    ) -> AsyncGenerator[Token, None]:
        raise ProviderUnavailable("torre apagada")
        yield Token(text="nunca")

    first.stream = unavailable.__get__(first)  # type: ignore[method-assign]
    second.stream = unavailable.__get__(second)  # type: ignore[method-assign]

    with pytest.raises(ProviderUnavailable) as excinfo:
        await router.stream(_messages())

    assert isinstance(excinfo.value, ProviderUnavailable)
    assert router.failovers == 2


async def test_slow_tower_fails_over_and_dell_recovers_later() -> None:
    tower = StubProvider(tokens=("lenta",))
    tower.name = "tower"
    tower.delay_between = 0.2
    dell = StubProvider(tokens=("ok",))
    dell.name = "dell"
    monitor = HealthMonitor([tower, dell], config=MonitorConfig())
    router = LLMRouter([tower, dell], monitor, first_token_timeout_s=0.05)

    routed = await router.stream(_messages())
    tokens = [token.text async for token in routed]

    assert tokens == ["ok"]
    assert routed.meta.provider == "dell"
    assert router.failovers == 1


async def test_mid_stream_crash_never_switches_provider() -> None:
    tower = StubProvider(tokens=("a", "b"), fail_after_first=ProviderError("corte"))
    tower.name = "tower"
    dell = StubProvider(tokens=("no-debe-usarse",))
    dell.name = "dell"
    monitor = HealthMonitor([tower, dell], config=MonitorConfig())
    router = LLMRouter([tower, dell], monitor)

    routed = await router.stream(_messages())
    received: list[str] = []
    with pytest.raises(ProviderError):
        async for token in routed:
            received.append(token.text)

    assert received == ["a"]
    assert dell.stream_calls == 0


async def test_timeout_before_first_token_is_controlled() -> None:
    tower = StubProvider(tokens=("x",))
    tower.name = "tower"
    tower.delay_between = 0.2
    monitor = HealthMonitor([tower], config=MonitorConfig())
    router = LLMRouter([tower], monitor, first_token_timeout_s=0.01)

    with pytest.raises(FirstTokenTimeout):
        await router.stream(_messages())
