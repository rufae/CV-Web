"""Aplicación FastAPI de CV Web (factory + lifespan)."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.core.ratelimit import (
    DailyBudget,
    DailyBudgetExceeded,
    RateLimitExceeded,
    SlidingWindowLimiter,
    parse_limits,
)
from app.core.security import (
    BodySizeLimitMiddleware,
    RequestIdMiddleware,
    SecurityHeadersMiddleware,
)
from app.features.chat.router import router as chat_router
from app.features.chat.service import ChatService
from app.features.contact.router import router as contact_router
from app.features.contact.service import ContactService
from app.features.health.router import router as health_router
from app.llm.factory import build_providers
from app.llm.health import HealthMonitor, MonitorConfig
from app.llm.router import LLMRouter
from app.rag.embeddings import OllamaEmbedder
from app.rag.prompts import PromptBuilder
from app.rag.retriever import Retriever
from app.rag.store import ChromaStore, StoreConfigMismatch

logger = logging.getLogger("cvweb")


async def _rate_limit_handler(_: Request, exc: Exception) -> JSONResponse:
    retry_after = exc.retry_after_s if isinstance(exc, RateLimitExceeded) else 60
    return JSONResponse(
        status_code=429,
        content={"code": "rate_limited", "retry_after_s": retry_after},
        headers={"Retry-After": str(retry_after)},
    )


async def _daily_budget_handler(_: Request, __: Exception) -> JSONResponse:
    return JSONResponse(status_code=429, content={"code": "daily_budget_exhausted"})


async def _http_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, StarletteHTTPException):
        if exc.status_code == 404:
            return JSONResponse(status_code=404, content={"code": "not_found"})
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=exc.headers,
        )
    return JSONResponse(status_code=500, content={"code": "internal"})


async def _unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.error("unhandled_error: %s", type(exc).__name__)
    return JSONResponse(status_code=500, content={"code": "internal"})


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

        prompt_builder = PromptBuilder()
        embedder: OllamaEmbedder | None = None
        retriever: Retriever | None = None
        if settings.embed_url:
            try:
                store = ChromaStore(
                    settings.chroma_path,
                    embed_model=settings.embed_model,
                    read_only=True,
                )
                embedder = OllamaEmbedder(settings.embed_url, settings.embed_model)
                retriever = Retriever(
                    embedder,
                    store,
                    top_k=settings.rag_top_k,
                    min_score=settings.rag_min_score,
                )
            except StoreConfigMismatch as exc:
                logger.error("Índice incompatible; asistente deshabilitado: %s", exc)

        app.state.prompt_builder = prompt_builder
        app.state.retriever = retriever

        app.state.chat_limiter = SlidingWindowLimiter(parse_limits(settings.rate_limit_chat))
        app.state.contact_limiter = SlidingWindowLimiter(parse_limits(settings.rate_limit_contact))
        app.state.feedback_limiter = SlidingWindowLimiter(
            parse_limits(settings.rate_limit_feedback)
        )
        app.state.chat_budget = DailyBudget(settings.daily_chat_budget)
        app.state.contact_budget = DailyBudget(settings.daily_contact_budget)

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
            if embedder is not None:
                await embedder.aclose()

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
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )
    hosts = [host.strip() for host in settings.allowed_hosts.split(",") if host.strip()]
    if hosts:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=hosts)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(BodySizeLimitMiddleware, max_bytes=settings.max_body_bytes)
    app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)
    app.add_exception_handler(DailyBudgetExceeded, _daily_budget_handler)
    app.add_exception_handler(StarletteHTTPException, _http_exception_handler)
    app.add_exception_handler(Exception, _unhandled_exception_handler)

    app.include_router(health_router)
    app.include_router(chat_router)
    app.include_router(contact_router)

    # Estáticos del frontend (monolito, Opción A). El mount va después de los routers.
    dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
    if dist.is_dir():
        app.mount("/", StaticFiles(directory=dist, html=True), name="static")

    return app


app = create_app()
