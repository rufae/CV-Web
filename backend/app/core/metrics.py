"""Métricas Prometheus (T7.6). Se exponen en `/metrics` con token."""

from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Histogram,
    generate_latest,
)

CHAT_REQUESTS = Counter(
    "cvweb_chat_requests_total",
    "Peticiones de chat por resultado",
    ["outcome"],
)
CHAT_REFUSALS = Counter(
    "cvweb_chat_refusals_total",
    "Rechazos del asistente por motivo",
    ["reason"],
)
LLM_FAILOVERS = Counter(
    "cvweb_llm_failovers_total",
    "Failovers del router de proveedores LLM",
)
CHAT_FIRST_TOKEN = Histogram(
    "cvweb_first_token_seconds",
    "Tiempo hasta el primer token",
    buckets=(0.1, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 15.0),
)
CONTACT_MESSAGES = Counter(
    "cvweb_contact_messages_total",
    "Mensajes de contacto por resultado",
    ["outcome"],
)


def render_metrics() -> bytes:
    return generate_latest()


def metrics_content_type() -> str:
    return CONTENT_TYPE_LATEST
