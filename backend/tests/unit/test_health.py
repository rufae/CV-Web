"""Tests del monitor de salud (T2.3): histéresis, circuit breaker y recuperación."""

import asyncio
from collections.abc import AsyncGenerator

from app.llm.base import Message, ProviderHealth, Token
from app.llm.health import HealthMonitor, MonitorConfig, ProviderState


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


class StubProvider:
    name = "stub"
    model = "stub-1"

    def __init__(self, ok: bool = True, latency_ms: float = 5.0) -> None:
        self.ok = ok
        self.latency_ms = latency_ms
        self.health_calls = 0
        self.hang_s: float | None = None

    async def health(self) -> ProviderHealth:
        self.health_calls += 1
        if self.hang_s is not None:
            await asyncio.sleep(self.hang_s)
        return ProviderHealth(ok=self.ok, latency_ms=self.latency_ms, model="stub-1")

    async def aclose(self) -> None:
        return

    async def stream(
        self,
        messages: list[Message],
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> AsyncGenerator[Token, None]:
        yield Token(text="x")


def _config(
    *,
    ttl_s: float = 1.0,
    health_timeout_s: float = 1.0,
    failures_per_step: int = 2,
    successes_per_step: int = 3,
    circuit_open_s: float = 30.0,
) -> MonitorConfig:
    return MonitorConfig(
        ttl_s=ttl_s,
        health_timeout_s=health_timeout_s,
        failures_per_step=failures_per_step,
        successes_per_step=successes_per_step,
        circuit_open_s=circuit_open_s,
    )


def _state(monitor: HealthMonitor) -> ProviderState:
    return monitor.statuses[0].state


async def _force_down(monitor: HealthMonitor, provider: StubProvider) -> None:
    provider.ok = False
    for _ in range(4):  # 2 pasos de 2 fallos: UP -> DEGRADED -> DOWN
        await monitor.check_once()


async def test_two_failures_per_step_until_down() -> None:
    clock = FakeClock()
    provider = StubProvider(ok=True)
    monitor = HealthMonitor([provider], config=_config(), clock=clock)

    await monitor.check_once()
    assert _state(monitor) is ProviderState.UP

    provider.ok = False
    await monitor.check_once()
    assert _state(monitor) is ProviderState.UP  # 1 fallo: sin cambio

    await monitor.check_once()
    assert _state(monitor) is ProviderState.DEGRADED  # 2 fallos

    await monitor.check_once()
    await monitor.check_once()
    assert _state(monitor) is ProviderState.DOWN  # 4 fallos

    assert not monitor.is_available("stub")


async def test_three_successes_per_step_to_recover() -> None:
    clock = FakeClock()
    provider = StubProvider(ok=True)
    monitor = HealthMonitor([provider], config=_config(), clock=clock)
    await _force_down(monitor, provider)

    clock.advance(31.0)  # circuito semiabierto
    provider.ok = True
    for _ in range(3):
        await monitor.check_once()
    assert _state(monitor) is ProviderState.DEGRADED

    for _ in range(3):
        await monitor.check_once()
    assert _state(monitor) is ProviderState.UP
    assert monitor.is_available("stub")


async def test_circuit_breaker_skips_probes_until_timeout() -> None:
    clock = FakeClock()
    provider = StubProvider(ok=True)
    monitor = HealthMonitor([provider], config=_config(), clock=clock)
    await _force_down(monitor, provider)

    calls = provider.health_calls
    await monitor.check_once()
    await monitor.check_once()
    assert provider.health_calls == calls  # circuito abierto: no se sondea

    clock.advance(31.0)
    await monitor.check_once()
    assert provider.health_calls == calls + 1  # semiabierto: se vuelve a sondear


async def test_health_timeout_counts_as_failure() -> None:
    clock = FakeClock()
    provider = StubProvider(ok=True)
    provider.hang_s = 0.2
    monitor = HealthMonitor(
        [provider], config=_config(health_timeout_s=0.01, failures_per_step=1), clock=clock
    )

    await monitor.check_once()

    assert _state(monitor) is ProviderState.DEGRADED


async def test_status_reports_latency_and_model() -> None:
    clock = FakeClock()
    provider = StubProvider(ok=True, latency_ms=12.5)
    monitor = HealthMonitor([provider], config=_config(), clock=clock)

    await monitor.check_once()

    status = monitor.statuses[0]
    assert status.name == "stub"
    assert status.latency_ms == 12.5
    assert status.model == "stub-1"
    assert status.last_check_s == 0.0


async def test_background_loop_polls_and_stops() -> None:
    clock = FakeClock()
    provider = StubProvider(ok=True)
    monitor = HealthMonitor([provider], config=_config(ttl_s=0.01), clock=clock)

    await monitor.start()
    await asyncio.sleep(0.05)
    await monitor.stop()

    assert provider.health_calls >= 1
