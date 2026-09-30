"""Aplicación FastAPI de CV Web (factory + lifespan)."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.features.chat.router import router as chat_router
from app.features.chat.service import ChatService
from app.features.contact.router import router as contact_router
from app.features.contact.service import ContactService
from app.features.health.router import router as health_router

logger = logging.getLogger("cvweb")


def create_app() -> FastAPI:
    settings = get_settings()

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
        app.state.chat_service = ChatService(settings, context)
        app.state.contact_service = ContactService(settings)
        yield

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
