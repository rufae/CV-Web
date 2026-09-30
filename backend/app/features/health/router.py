"""Endpoints de salud, estado público y métricas (T2.6/T7.6)."""

import time
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, Response

from app.core.config import get_settings
from app.core.metrics import metrics_content_type, render_metrics
from app.features.health.service import LlmStatus, llm_status
from app.llm.health import HealthMonitor

router = APIRouter(tags=["health"])


def _require_metrics_token(request: Request) -> None:
    token = get_settings().metrics_token
    if token == "":
        raise HTTPException(status_code=404, detail="Not found")
    if request.headers.get("x-metrics-token") != token:
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.get("/metrics")
async def metrics(request: Request) -> Response:
    _require_metrics_token(request)
    return Response(content=render_metrics(), media_type=metrics_content_type())


@router.get("/api/health/deep")
async def deep_health(request: Request) -> dict[str, object]:
    _require_metrics_token(request)
    settings = get_settings()
    monitor: HealthMonitor = request.app.state.health_monitor
    embedder = getattr(request.app.state, "embedder", None)
    embed_ok = bool(await embedder.health()) if embedder is not None else False

    manifest = Path(settings.data_path) / "ingest_manifest.json"
    index_age_hours: float | None = None
    if manifest.is_file():
        index_age_hours = round((time.time() - manifest.stat().st_mtime) / 3600, 1)

    return {
        "status": "ok",
        "llm": llm_status(monitor.statuses),
        "providers": [
            {"name": status.name, "state": status.state.value} for status in monitor.statuses
        ],
        "embed_ok": embed_ok,
        "index_age_hours": index_age_hours,
    }


@router.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/api/status")
async def status(request: Request) -> LlmStatus:
    monitor: HealthMonitor = request.app.state.health_monitor
    return llm_status(monitor.statuses)
