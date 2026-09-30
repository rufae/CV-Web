"""Router del chat.

- `POST /api/chat`: streaming SSE (T4.5).
- `POST /ask`: alias legacy JSON (se retira en T5.7).
"""

import secrets
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, StreamingResponse

from app.core.config import get_settings
from app.core.ratelimit import enforce_daily_budget, enforce_rate_limit
from app.features.chat.events import SourceItem, SourcesEvent
from app.features.chat.output_guard import OutputGuard
from app.features.chat.sanitize import sanitize_input
from app.features.chat.schemas import ChatRequest, Prompt
from app.features.chat.service import ChatService
from app.features.chat.sse import refusal_stream, routed_stream
from app.features.health.service import llm_status
from app.llm.errors import LLMError, QueueOverflow
from app.llm.health import HealthMonitor
from app.llm.router import LLMRouter
from app.rag.prompts import REFUSAL_MESSAGE, PromptBuilder
from app.rag.retriever import Retriever

router = APIRouter(tags=["chat"])

SSE_HEADERS = {
    "Cache-Control": "no-cache, no-transform",
    "X-Accel-Buffering": "no",
}


async def _chat_limits(request: Request) -> None:
    enforce_rate_limit(request, "chat_limiter")
    enforce_daily_budget(request)


def _sse_response(stream: AsyncIterator[str]) -> StreamingResponse:
    return StreamingResponse(stream, media_type="text/event-stream", headers=SSE_HEADERS)


@router.post("/api/chat", dependencies=[Depends(_chat_limits)], response_model=None)
async def chat_sse(payload: ChatRequest, request: Request) -> StreamingResponse | JSONResponse:
    settings = get_settings()
    monitor: HealthMonitor = request.app.state.health_monitor
    builder: PromptBuilder = request.app.state.prompt_builder
    message_id = secrets.token_hex(6)
    tier = llm_status(monitor.statuses)["tier"]

    sanitized = sanitize_input(payload.message, payload.history)
    if sanitized.blocked:
        return _sse_response(
            refusal_stream(
                message_id=message_id,
                prompt_version=builder.version,
                tier=tier,
                reason="injection",
                message=REFUSAL_MESSAGE,
            )
        )

    retriever: Retriever | None = request.app.state.retriever
    if retriever is None:
        return JSONResponse(
            status_code=503,
            content={
                "code": "provider_unavailable",
                "message": "El asistente no está configurado.",
            },
        )

    try:
        retrieval = await retriever.retrieve(sanitized.message)
    except LLMError:
        return JSONResponse(
            status_code=503,
            content={
                "code": "provider_unavailable",
                "message": "El asistente no está disponible ahora mismo.",
                "retry_after_s": 30,
            },
            headers={"Retry-After": "30"},
        )

    if retrieval.is_empty:
        return _sse_response(
            refusal_stream(
                message_id=message_id,
                prompt_version=builder.version,
                tier=tier,
                reason="no_context",
                message=REFUSAL_MESSAGE,
            )
        )

    prompt = builder.build(
        question=sanitized.message,
        history=list(sanitized.history),
        retrieval=retrieval,
        injection_suspected=sanitized.injection_suspected,
        corpus_prefix=settings.rag_context_prefix,
    )

    llm_router: LLMRouter = request.app.state.llm_router
    try:
        routed = await llm_router.stream(
            prompt.messages,
            temperature=prompt.temperature,
            max_tokens=prompt.max_tokens,
        )
    except QueueOverflow as exc:
        return JSONResponse(
            status_code=503,
            content={
                "code": "provider_unavailable",
                "message": "El asistente está ocupado; inténtalo en unos segundos.",
                "retry_after_s": exc.retry_after_s,
            },
            headers={"Retry-After": str(exc.retry_after_s)},
        )
    except LLMError:
        return JSONResponse(
            status_code=503,
            content={
                "code": "provider_unavailable",
                "message": "El asistente no está disponible ahora mismo.",
            },
        )

    sources_event = SourcesEvent(
        sources=[
            SourceItem(n=source.n, title=source.title, section=source.section)
            for source in prompt.sources
        ]
    )
    guard = OutputGuard(
        canary=prompt.canary,
        system_prompt=prompt.messages[0].content,
        allowlist=tuple(
            item.strip() for item in settings.public_contact_allowlist.split(",") if item.strip()
        ),
        allowed_domains=tuple(
            item.strip() for item in settings.allowed_output_domains.split(",") if item.strip()
        ),
    )
    return _sse_response(
        routed_stream(
            message_id=message_id,
            prompt_version=prompt.prompt_version,
            tier=tier,
            sources=sources_event,
            routed=routed,
            guard=guard,
        )
    )


@router.post("/ask", include_in_schema=False, dependencies=[Depends(_chat_limits)])
async def ask_rafa(prompt: Prompt, request: Request) -> dict[str, str]:
    service: ChatService = request.app.state.chat_service
    return {"response": await service.ask(prompt.message)}
