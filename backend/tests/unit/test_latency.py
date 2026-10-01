"""Percentiles de latencia al primer token (estado en vivo, 2026-10-01)."""

from app.core.latency import LatencyTracker


def test_percentiles_y_ventana_de_24h() -> None:
    ahora = [1000.0]
    tracker = LatencyTracker(window_s=100, clock=lambda: ahora[0])
    assert tracker.stats().samples == 0
    assert tracker.stats().p50_ms is None
    assert tracker.stats().p95_ms is None

    for valor in (100, 200, 300, 400, 500):
        tracker.record(valor)
    stats = tracker.stats()
    assert stats.samples == 5
    assert stats.p50_ms == 300
    assert stats.p95_ms == 500

    # Al avanzar el reloj mas alla de la ventana se descartan las muestras.
    ahora[0] += 200
    assert tracker.stats().samples == 0


def test_ignora_valores_invalidos() -> None:
    tracker = LatencyTracker()
    tracker.record(-1)
    tracker.record(None)  # type: ignore[arg-type]
    assert tracker.stats().samples == 0


def test_una_sola_muestra() -> None:
    tracker = LatencyTracker()
    tracker.record(42.5)
    stats = tracker.stats()
    assert stats.samples == 1
    assert stats.p50_ms == 42.5
    assert stats.p95_ms == 42.5
