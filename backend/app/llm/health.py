"""Monitor de salud de proveedores LLM con histéresis y circuit breaker (T2.3).

No sondea en la ruta caliente: el router consulta `is_available()` y el monitor
actualiza el estado en segundo plano cada `ttl_s`. Cuando un proveedor cae a
`DOWN` se abre el circuito durante `circuit_open_s` para no pagar timeouts en
cada comprobación; después se vuelve a sondear (semiabierto).
"""

import asyncio
import time
from collections.abc import Callable
from contextlib import suppress
from dataclasses import dataclass
from enum import Enum

from app.llm.base import LLMProvider


class ProviderState(Enum):
    UP = "up"
    DEGRADED = "degraded"
    DOWN = "down"


@dataclass
class ProviderStatus:
    name: str
    state: ProviderState = ProviderState.UP
    latency_ms: float | None = None
    model: str | None = None
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    last_check_s: float | None = None
    opened_at_s: float | None = None


@dataclass(frozen=True)
class MonitorConfig:
    ttl_s: float = 10.0
    health_timeout_s: float = 2.0
    failures_per_step: int = 2
    successes_per_step: int = 3
    circuit_open_s: float = 30.0


class HealthMonitor:
    def __init__(
        self,
        providers: list[LLMProvider],
        *,
        config: MonitorConfig | None = None,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._providers = providers
        self._config = config or MonitorConfig()
        self._clock = clock
        self._statuses: dict[str, ProviderStatus] = {
            provider.name: ProviderStatus(name=provider.name) for provider in providers
        }
        self._task: asyncio.Task[None] | None = None

    @property
    def statuses(self) -> list[ProviderStatus]:
        return list(self._statuses.values())

    def is_available(self, name: str) -> bool:
        status = self._statuses.get(name)
        return status is not None and status.state is not ProviderState.DOWN

    async def check_once(self) -> None:
        for provider in self._providers:
            await self._check_provider(provider)

    async def start(self) -> None:
        if self._task is None:
            self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        if self._task is None:
            return
        self._task.cancel()
        with suppress(asyncio.CancelledError):
            await self._task
        self._task = None

    async def _check_provider(self, provider: LLMProvider) -> None:
        status = self._statuses[provider.name]
        now = self._clock()

        if self._circuit_is_open(status, now):
            return

        ok = False
        latency_ms: float | None = None
        model: str | None = None
        try:
            health = await asyncio.wait_for(
                provider.health(), timeout=self._config.health_timeout_s
            )
            ok = health.ok
            latency_ms = health.latency_ms
            model = health.model
        except TimeoutError:
            ok = False
        except Exception:
            ok = False

        status.last_check_s = now
        if ok:
            status.latency_ms = latency_ms
            status.model = model
            self._register_success(status)
        else:
            self._register_failure(status)

    def _register_success(self, status: ProviderStatus) -> None:
        status.consecutive_failures = 0
        status.consecutive_successes += 1
        if status.consecutive_successes < self._config.successes_per_step:
            return

        status.consecutive_successes = 0
        if status.state is ProviderState.DOWN:
            status.state = ProviderState.DEGRADED
            status.opened_at_s = None
        elif status.state is ProviderState.DEGRADED:
            status.state = ProviderState.UP

    def _register_failure(self, status: ProviderStatus) -> None:
        status.consecutive_successes = 0
        status.consecutive_failures += 1
        if status.consecutive_failures < self._config.failures_per_step:
            return

        status.consecutive_failures = 0
        if status.state is ProviderState.UP:
            status.state = ProviderState.DEGRADED
        elif status.state is ProviderState.DEGRADED:
            status.state = ProviderState.DOWN
            status.opened_at_s = self._clock()
        else:
            status.opened_at_s = self._clock()

    def _circuit_is_open(self, status: ProviderStatus, now: float) -> bool:
        if status.state is not ProviderState.DOWN or status.opened_at_s is None:
            return False
        return (now - status.opened_at_s) < self._config.circuit_open_s

    async def _run(self) -> None:
        while True:
            await self.check_once()
            await asyncio.sleep(self._config.ttl_s)
