"""Cálculo del estado público del servicio (T2.6)."""

from app.llm.health import ProviderState, ProviderStatus


def llm_status(statuses: list[ProviderStatus]) -> dict[str, str]:
    states = {status.state for status in statuses}
    if ProviderState.UP in states:
        llm = "online"
    elif ProviderState.DEGRADED in states:
        llm = "degraded"
    else:
        llm = "offline"

    tower = next((status for status in statuses if status.name == "tower"), None)
    tier = "gpu" if tower is not None and tower.state is ProviderState.UP else "cpu"
    return {"llm": llm, "tier": tier}
