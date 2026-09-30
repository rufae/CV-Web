"""Tests del estado público del servicio (T2.6)."""

from app.features.health.service import llm_status
from app.llm.health import ProviderState, ProviderStatus


def _status(name: str, state: ProviderState) -> ProviderStatus:
    return ProviderStatus(name=name, state=state)


def test_offline_without_providers() -> None:
    assert llm_status([]) == {"llm": "offline", "tier": "cpu"}


def test_online_when_any_provider_is_up() -> None:
    result = llm_status([_status("tower", ProviderState.DOWN), _status("dell", ProviderState.UP)])

    assert result == {"llm": "online", "tier": "cpu"}


def test_degraded_when_only_degraded_providers() -> None:
    result = llm_status([_status("tower", ProviderState.DEGRADED)])

    assert result == {"llm": "degraded", "tier": "cpu"}


def test_tier_is_gpu_only_when_tower_is_up() -> None:
    result = llm_status(
        [_status("tower", ProviderState.UP), _status("dell", ProviderState.DEGRADED)]
    )

    assert result == {"llm": "online", "tier": "gpu"}
