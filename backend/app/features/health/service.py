"""Cálculo del estado público del servicio (T2.6)."""

from typing import Literal, TypedDict

from app.llm.health import ProviderState, ProviderStatus


class LlmStatus(TypedDict):
    llm: Literal["online", "degraded", "offline"]
    tier: Literal["gpu", "cpu"]


def llm_status(statuses: list[ProviderStatus]) -> LlmStatus:
    states = {status.state for status in statuses}
    llm: Literal["online", "degraded", "offline"]
    if ProviderState.UP in states:
        llm = "online"
    elif ProviderState.DEGRADED in states:
        llm = "degraded"
    else:
        llm = "offline"

    tower = next((status for status in statuses if status.name == "tower"), None)
    tier: Literal["gpu", "cpu"] = (
        "gpu" if tower is not None and tower.state is ProviderState.UP else "cpu"
    )
    return {"llm": llm, "tier": tier}
