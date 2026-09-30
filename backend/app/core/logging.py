"""Logging JSON estructurado (T2.6).

Los eventos del subsistema LLM se registran con el logger `cvweb` y campos
extra (`provider`, `model`, `first_token_ms`, `latency_ms`, `outcome`...),
nunca con el contenido de las conversaciones.
"""

import json
import logging
from typing import Any

_EXTRA_FIELDS = (
    "provider",
    "model",
    "first_token_ms",
    "latency_ms",
    "outcome",
    "request_id",
    "tier",
)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for field in _EXTRA_FIELDS:
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def setup_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    logger = logging.getLogger("cvweb")
    logger.handlers = [handler]
    logger.setLevel(level)
    logger.propagate = False
