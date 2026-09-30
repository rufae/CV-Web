"""Generadores SSE del chat (T4.5).

- `refusal_stream`: rechazo sin LLM (`meta` → `refusal` → `done`).
- `routed_stream`: `meta` → `sources` → `token`* → `done`, con latido
  (`: ping`) cada `heartbeat_s` y cancelación aguas arriba al desconectar.
- Cualquier error del proveedor se emite como evento `error` (jamás una traza).
"""

import asyncio
import logging
import time
from collections.abc import AsyncGenerator
from typing import Literal

from app.core.metrics import CHAT_FIRST_TOKEN, CHAT_REFUSALS, CHAT_REQUESTS
from app.features.chat.events import (
    DoneEvent,
    ErrorCode,
    ErrorEvent,
    MetaEvent,
    RefusalEvent,
    RefusalReason,
    SourcesEvent,
    TokenEvent,
    sse,
)
from app.features.chat.output_guard import OutputGuard
from app.llm.errors import FirstTokenTimeout, LLMError, ProviderError, ProviderUnavailable
from app.llm.router import RoutedStream

HEARTBEAT_S = 15.0
PING = ": ping\n\n"
_BLOCKED_MESSAGE = "La respuesta fue bloqueada por seguridad."

logger = logging.getLogger("cvweb.chat")


def _error_code(exc: LLMError) -> ErrorCode:
    if isinstance(exc, FirstTokenTimeout):
        return "first_token_timeout"
    if isinstance(exc, (ProviderUnavailable, ProviderError)):
        return "provider_unavailable"
    return "internal"


async def refusal_stream(
    *,
    message_id: str,
    prompt_version: str,
    tier: Literal["gpu", "cpu"],
    reason: RefusalReason,
    message: str,
) -> AsyncGenerator[str, None]:
    yield sse("meta", MetaEvent(message_id=message_id, prompt_version=prompt_version, tier=tier))
    CHAT_REQUESTS.labels("refused").inc()
    CHAT_REFUSALS.labels(reason).inc()
    yield sse("refusal", RefusalEvent(reason=reason, message=message))
    yield sse("done", DoneEvent(total_ms=0.0))


async def routed_stream(
    *,
    message_id: str,
    prompt_version: str,
    tier: Literal["gpu", "cpu"],
    sources: SourcesEvent,
    routed: RoutedStream,
    heartbeat_s: float = HEARTBEAT_S,
    guard: OutputGuard | None = None,
) -> AsyncGenerator[str, None]:
    started = time.perf_counter()
    yield sse("meta", MetaEvent(message_id=message_id, prompt_version=prompt_version, tier=tier))
    yield sse("sources", sources)

    try:
        while True:
            try:
                token = await asyncio.wait_for(routed.__anext__(), timeout=heartbeat_s)
            except TimeoutError:
                yield PING
                continue
            except StopAsyncIteration:
                break

            if guard is None:
                yield sse("token", TokenEvent(t=token.text))
                continue

            decision = guard.feed(token.text)
            if decision.blocked:
                CHAT_REQUESTS.labels("blocked").inc()
                logger.warning("output_blocked", extra={"outcome": "output_blocked"})
                yield sse("error", ErrorEvent(code="output_blocked", message=_BLOCKED_MESSAGE))
                return
            if decision.text:
                yield sse("token", TokenEvent(t=decision.text))
    except LLMError as exc:
        CHAT_REQUESTS.labels("error").inc()
        yield sse(
            "error",
            ErrorEvent(
                code=_error_code(exc),
                message="El asistente no está disponible ahora mismo.",
            ),
        )
        return
    finally:
        await routed.aclose()

    if guard is not None:
        final = guard.flush()
        if final.blocked:
            CHAT_REQUESTS.labels("blocked").inc()
            logger.warning("output_blocked", extra={"outcome": "output_blocked"})
            yield sse("error", ErrorEvent(code="output_blocked", message=_BLOCKED_MESSAGE))
            return
        if final.text:
            yield sse("token", TokenEvent(t=final.text))

    CHAT_REQUESTS.labels("done").inc()
    if routed.meta.first_token_ms is not None:
        CHAT_FIRST_TOKEN.observe(routed.meta.first_token_ms / 1000)
    yield sse(
        "done",
        DoneEvent(
            first_token_ms=routed.meta.first_token_ms,
            total_ms=(time.perf_counter() - started) * 1000,
        ),
    )
