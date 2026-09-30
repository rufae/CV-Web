"""Endpoints de salud y estado público."""

from fastapi import APIRouter, Request

from app.features.health.service import llm_status
from app.llm.health import HealthMonitor

router = APIRouter(tags=["health"])


@router.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/api/status")
async def status(request: Request) -> dict[str, str]:
    monitor: HealthMonitor = request.app.state.health_monitor
    return llm_status(monitor.statuses)
