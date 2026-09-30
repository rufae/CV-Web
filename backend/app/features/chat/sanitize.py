"""Sanitización de entrada y detección heurística de inyección (T4.3).

- Normaliza (NFKC), elimina caracteres invisibles/de control y colapsa espacios.
- Neutraliza los delimitadores del prompt (`<fuente>`, `</fuentes>`…).
- El historial del cliente es **no confiable** (se sanea igual).
- El detector heurístico ES/EN marca `injection_suspected` (no bloquea por sí
  solo); solo se bloquea ante extracción explícita de prompt o datos personales.
"""

import re
import unicodedata
from dataclasses import dataclass

from app.features.chat.schemas import Turn

_ZERO_WIDTH = re.compile(r"[\u200b-\u200f\u202a-\u202e\u2060-\u2064\ufeff]")
_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_WHITESPACE = re.compile(r"\s+")
_DELIMITERS = re.compile(r"<\s*/?\s*fuentes?\b[^>]*>?", re.IGNORECASE)

_INJECTION_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"ignora (todas )?(las|tus) (instrucciones|reglas)", re.IGNORECASE),
    re.compile(r"</?\s*fuentes?\b", re.IGNORECASE),
    re.compile(r"ignore (all )?(previous|prior|above) instructions", re.IGNORECASE),
    re.compile(r"(system|sistema) prompt", re.IGNORECASE),
    re.compile(
        r"(revela\w*|mu[eé]stra\w*|repite\w*|dime|print|reveal\w*|repeat|show).{0,40}"
        r"\b(prompt|instrucciones|instructions|system)",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"(act[úu]a|act)\s+como\s+(un\s+)?(asistente\s+)?(sin restricciones|jailbreak|dan\b)",
        re.IGNORECASE,
    ),
    re.compile(r"modo (desarrollador|desarrollo|developer mode)", re.IGNORECASE),
    re.compile(r"\bjailbreak\w*\b", re.IGNORECASE),
    re.compile(
        r"\byou are now\b.{0,40}\b(dan|jailbroken|unrestricted|developer mode)",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(r"<\|[^|]*\|>"),
    re.compile(r"###\s*(system|instruction)", re.IGNORECASE),
)

_BLOCK_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(
        r"(mu[eé]stra\w*|revela\w*|repite\w*|dime|print|reveal\w*|repeat|show).{0,60}"
        r"\b(prompt|instrucciones|instructions|system)",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"\b(el|su|tu)?\s*(tel[ée]fono|phone|direcci[óo]n|address|dni|nie|iban|pasaporte)\b",
        re.IGNORECASE,
    ),
)


@dataclass(frozen=True)
class SanitizedInput:
    message: str
    history: tuple[Turn, ...]
    injection_suspected: bool
    blocked: bool


def sanitize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    cleaned = _ZERO_WIDTH.sub("", normalized)
    cleaned = _CONTROL.sub("", cleaned)
    cleaned = _DELIMITERS.sub("[texto]", cleaned)
    return _WHITESPACE.sub(" ", cleaned).strip()


def detect_injection(text: str) -> bool:
    return any(pattern.search(text) for pattern in _INJECTION_PATTERNS)


def is_explicit_extraction(text: str) -> bool:
    return any(pattern.search(text) for pattern in _BLOCK_PATTERNS)


def sanitize_input(message: str, history: list[Turn]) -> SanitizedInput:
    clean_message = sanitize_text(message)
    clean_history = tuple(
        Turn(role=turn.role, content=sanitize_text(turn.content)) for turn in history
    )

    suspected = detect_injection(clean_message) or any(
        detect_injection(turn.content) for turn in clean_history
    )
    blocked = is_explicit_extraction(clean_message)
    return SanitizedInput(
        message=clean_message,
        history=clean_history,
        injection_suspected=suspected,
        blocked=blocked,
    )
