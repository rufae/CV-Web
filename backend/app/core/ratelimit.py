"""Rate limiting en memoria y presupuesto diario de chat (T4.2).

El estado vive en el proceso: la app debe correr con `--workers 1` (ADR-0002).
Formato de límite: `10/minute;60/hour` (varios límites separados por `;`).
"""

import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass

from fastapi import Request

from app.core.security import client_ip

_UNITS = {
    "second": 1.0,
    "minute": 60.0,
    "hour": 3600.0,
    "day": 86400.0,
}


class RateLimitExceeded(Exception):
    def __init__(self, retry_after_s: int) -> None:
        super().__init__("rate limit exceeded")
        self.retry_after_s = retry_after_s


class DailyBudgetExceeded(Exception):
    pass


@dataclass(frozen=True)
class RateLimit:
    limit: int
    window_s: float


def parse_limits(spec: str) -> tuple[RateLimit, ...]:
    limits: list[RateLimit] = []
    for part in spec.split(";"):
        part = part.strip()
        if not part:
            continue
        count_text, _, unit_text = part.partition("/")
        unit = _UNITS.get(unit_text.strip().lower())
        if unit is None:
            raise ValueError(f"Unidad de rate limit desconocida: {unit_text!r}")
        limits.append(RateLimit(limit=int(count_text.strip()), window_s=unit))
    return tuple(limits)


class SlidingWindowLimiter:
    def __init__(
        self,
        limits: tuple[RateLimit, ...],
        *,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._limits = limits
        self._clock = clock
        self._events: dict[str, deque[float]] = {}

    def check(self, key: str) -> int | None:
        """Registra la petición y devuelve `retry_after_s` si supera algún límite."""
        now = self._clock()
        events = self._events.setdefault(key, deque())
        max_window = max((limit.window_s for limit in self._limits), default=0.0)
        while events and now - events[0] > max_window:
            events.popleft()

        retry_after = 0.0
        for limit in self._limits:
            in_window = [ts for ts in events if now - ts <= limit.window_s]
            if len(in_window) >= limit.limit:
                retry_after = max(retry_after, limit.window_s - (now - min(in_window)))

        if retry_after > 0:
            return max(1, int(retry_after + 0.999))
        events.append(now)
        return None


class DailyBudget:
    def __init__(self, limit: int, *, clock: Callable[[], float] = time.time) -> None:
        self._limit = limit
        self._clock = clock
        self._day = ""
        self._count = 0

    def allow(self) -> bool:
        """Consume una unidad del presupuesto diario; `limit <= 0` = sin tope."""
        day = time.strftime("%Y-%m-%d", time.gmtime(self._clock()))
        if day != self._day:
            self._day = day
            self._count = 0
        if self._limit <= 0:
            return True
        if self._count >= self._limit:
            return False
        self._count += 1
        return True


def enforce_rate_limit(request: Request, attr: str) -> None:
    limiter: SlidingWindowLimiter = getattr(request.app.state, attr)
    retry_after = limiter.check(client_ip(request))
    if retry_after is not None:
        raise RateLimitExceeded(retry_after)


def enforce_budget(request: Request, attr: str = "chat_budget") -> None:
    budget: DailyBudget = getattr(request.app.state, attr)
    if not budget.allow():
        raise DailyBudgetExceeded()


def enforce_daily_budget(request: Request) -> None:
    enforce_budget(request, "chat_budget")
