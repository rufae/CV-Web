"""Generadores SSE del chat (T4.5).

- `refusal_stream`: rechazo sin LLM (`meta` → `refusal` → `done`).
- `routed_stream`: `meta` → `sources` → `token`* → `done`, con latido
  (`: ping`) cada `heartbeat_s` y cancelación aguas arriba al desconectar.
- Cualquier error del proveedor se emite como evento `error` (jamás una traza).
"""

import asyncio
import time
from collections.abc import AsyncGenerator
from typing import Literal

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
from app.llm.errors import FirstTokenTimeout, LLMError, ProviderError, ProviderUnavailable
from app.llm.router import RoutedStream

HEARTBEAT_S = 15.0
PING = ": ping\n\n"


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
            yield sse("token", TokenEvent(t=token.text))
    except LLMError as exc:
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

    yield sse(
        "done",
        DoneEvent(
            first_token_ms=routed.meta.first_token_ms,
            total_ms=(time.perf_counter() - started) * 1000,
        ),
    )
