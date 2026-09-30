"""Aplicación FastAPI de CV Web (factory + lifespan)."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.features.chat.router import router as chat_router
from app.features.chat.service import ChatService
from app.features.contact.router import router as contact_router
from app.features.contact.service import ContactService
from app.features.health.router import router as health_router
from app.llm.factory import build_providers
from app.llm.health import HealthMonitor, MonitorConfig
from app.llm.router import LLMRouter

logger = logging.getLogger("cvweb")


def create_app() -> FastAPI:
    settings = get_settings()
    setup_logging("INFO")

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        missing = settings.missing_required()
        if missing:
            message = "Faltan variables obligatorias: " + ", ".join(missing)
            if settings.is_production:
                raise RuntimeError(message)
            logger.warning("%s (en desarrollo se deshabilitan los servicios afectados)", message)

        context = (
            settings.context_file.read_text(encoding="utf-8")
            if settings.context_file is not None
            else None
        )
        providers = build_providers(settings)
        monitor = HealthMonitor(
            providers,
            config=MonitorConfig(
                ttl_s=settings.llm_health_ttl_s,
                health_timeout_s=max(settings.llm_connect_timeout_s * 2, 2.0),
            ),
        )
        llm_router = LLMRouter(
            providers,
            monitor,
            first_token_timeout_s=settings.llm_first_token_timeout_s,
            max_concurrency=settings.llm_max_concurrency,
        )
        await monitor.start()

        app.state.chat_service = ChatService(settings, context)
        app.state.contact_service = ContactService(settings)
        app.state.health_monitor = monitor
        app.state.llm_router = llm_router
        try:
            yield
        finally:
            await monitor.stop()
            for provider in providers:
                await provider.aclose()

    app = FastAPI(
        title="CV Web API",
        version="0.1.0",
        lifespan=lifespan,
        docs_url=None if settings.is_production else "/docs",
        redoc_url=None if settings.is_production else "/redoc",
        openapi_url=None if settings.is_production else "/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(chat_router)
    app.include_router(contact_router)

    # Estáticos del frontend (monolito, Opción A). El mount va después de los routers.
    dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
    if dist.is_dir():
        app.mount("/", StaticFiles(directory=dist, html=True), name="static")

    return app


app = create_app()
