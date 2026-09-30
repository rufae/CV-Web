"""Contrato de eventos SSE de `POST /api/chat` (Apéndice B de `plan.md`).

Orden normal: `meta` → `sources` → `token`* → `done`.
Rechazo sin LLM: `meta` → `refusal` → `done`.
Un fallo en curso emite `error` y cierra.
"""

from typing import Literal

from pydantic import BaseModel

ErrorCode = Literal[
    "rate_limited",
    "daily_budget_exhausted",
    "provider_unavailable",
    "first_token_timeout",
    "output_blocked",
    "internal",
]
RefusalReason = Literal["no_context", "off_topic", "injection"]


class MetaEvent(BaseModel):
    message_id: str
    prompt_version: str
    tier: Literal["gpu", "cpu"]


class SourceItem(BaseModel):
    n: int
    title: str
    section: str


class SourcesEvent(BaseModel):
    sources: list[SourceItem]


class TokenEvent(BaseModel):
    t: str


class RefusalEvent(BaseModel):
    reason: RefusalReason
    message: str


class DoneEvent(BaseModel):
    first_token_ms: float | None = None
    total_ms: float


class ErrorEvent(BaseModel):
    code: ErrorCode
    message: str
    retry_after_s: int | None = None


def sse(event: str, data: BaseModel) -> str:
    """Formatea un evento SSE (`event:` + `data:` con JSON compacto)."""
    return f"event: {event}\ndata: {data.model_dump_json()}\n\n"
