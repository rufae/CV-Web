"""Latencia del primer token (p50/p95 de las últimas 24 h) para el estado en vivo.

El histograma de Prometheus (`CHAT_FIRST_TOKEN`) ya registra cada muestra, pero
calcular cuantiles exactos desde sus buckets es aproximado. Aquí se guardan las
muestras (una por respuesta) en memoria y se calculan percentiles exactos; el
proceso corre con un único worker, así que el estado es consistente.
"""

import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass

WINDOW_S = 24 * 3600


@dataclass(frozen=True)
class LatencyStats:
    samples: int
    p50_ms: float | None
    p95_ms: float | None


def _percentil(ordenados: list[float], q: float) -> float:
    if not ordenados:
        return 0.0
    indice = min(len(ordenados) - 1, max(0, round(q * (len(ordenados) - 1))))
    return ordenados[indice]


class LatencyTracker:
    """Muestras de primer token de las últimas `window_s` segundos."""

    def __init__(self, window_s: float = WINDOW_S, clock: Callable[[], float] = time.time) -> None:
        self._muestras: deque[tuple[float, float]] = deque()
        self._window_s = window_s
        self._clock = clock

    def record(self, first_token_ms: float) -> None:
        if first_token_ms is None or first_token_ms < 0:
            return
        self._purge()
        self._muestras.append((self._clock(), float(first_token_ms)))

    def stats(self) -> LatencyStats:
        self._purge()
        if not self._muestras:
            return LatencyStats(0, None, None)
        valores = sorted(valor for _, valor in self._muestras)
        return LatencyStats(
            samples=len(valores),
            p50_ms=round(_percentil(valores, 0.50), 1),
            p95_ms=round(_percentil(valores, 0.95), 1),
        )

    def reset(self) -> None:
        self._muestras.clear()

    def _purge(self) -> None:
        limite = self._clock() - self._window_s
        while self._muestras and self._muestras[0][0] < limite:
            self._muestras.popleft()


LATENCY = LatencyTracker()
