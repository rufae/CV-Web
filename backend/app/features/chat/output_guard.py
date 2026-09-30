"""Filtro de salida en streaming (T4.6).

Última barrera si el modelo desobedece o el contexto contiene algo que no
debía. Inspecciona el stream con un búfer de retención (~64 caracteres) antes
de emitir y bloquea:

- el token canario o n-gramas del prompt de sistema (fuga de instrucciones),
- patrones sensibles (email, teléfono, DNI/NIE, IBAN) fuera de la allowlist,
- URLs fuera de los dominios permitidos y Markdown peligroso,
- respuestas que superan el tope duro de longitud.

Compromiso documentado: se añade una latencia mínima (retención) a cambio de no
emitir contenido ya enviado.
"""

import re
from dataclasses import dataclass

DEFAULT_RETENTION = 64
DEFAULT_MAX_LENGTH = 4000
DEFAULT_NGRAM_SIZE = 8

_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE = re.compile(
    r"\b(?:\+34[\s.-]?)?(?:6\d{2}|7\d{2}|9\d{2})[\s.-]?\d{2}[\s.-]?\d{2}[\s.-]?\d{2}\b"
)
_DNI = re.compile(r"\b[XYZ]?\d{7,8}[A-Z]\b")
_IBAN = re.compile(r"\bES\d{2}[ ]?(?:\d{4}[ ]?){5}\b")
_URL = re.compile(r"https?://([^\s/)\]]+)", re.IGNORECASE)
_REMOTE_IMAGE = re.compile(r"!\[[^\]]*\]\(\s*(?:https?:)?//", re.IGNORECASE)
_JS_SCHEME = re.compile(r"javascript:\s*", re.IGNORECASE)
_NORMALIZE = re.compile(r"[^\wáéíóúüñ]+", re.IGNORECASE)


@dataclass(frozen=True)
class GuardDecision:
    text: str
    reason: str | None = None

    @property
    def blocked(self) -> bool:
        return self.reason is not None


class OutputGuard:
    def __init__(
        self,
        *,
        canary: str,
        system_prompt: str,
        allowlist: tuple[str, ...] = (),
        allowed_domains: tuple[str, ...] = (),
        retention: int = DEFAULT_RETENTION,
        max_length: int = DEFAULT_MAX_LENGTH,
        ngram_size: int = DEFAULT_NGRAM_SIZE,
    ) -> None:
        self._canary = canary
        self._retention = max(0, retention)
        self._max_length = max_length
        self._allowlist = tuple(item.strip().lower() for item in allowlist if item.strip())
        self._allowed_domains = tuple(
            domain.strip().lower() for domain in allowed_domains if domain.strip()
        )
        self._prompt_ngrams = _ngrams(system_prompt, ngram_size)
        self._buffer = ""
        self._emitted = 0

    def feed(self, token: str) -> GuardDecision:
        if not token:
            return GuardDecision("")

        self._buffer += token
        if len(self._buffer) <= self._retention:
            return GuardDecision("")

        emit = self._buffer[: len(self._buffer) - self._retention]
        self._buffer = self._buffer[len(emit) :]
        return self._check_and_emit(emit)

    def flush(self) -> GuardDecision:
        emit = self._buffer
        self._buffer = ""
        return self._check_and_emit(emit)

    def _check_and_emit(self, emit: str) -> GuardDecision:
        window = self._buffer + emit if self._buffer else emit
        reason = self._violation(window)
        if reason is not None:
            return GuardDecision("", reason)
        if self._emitted + len(emit) > self._max_length:
            return GuardDecision("", "too_long")
        self._emitted += len(emit)
        return GuardDecision(emit)

    def _violation(self, window: str) -> str | None:
        if not window:
            return None
        if self._canary and self._canary in window:
            return "canary"
        if _prompt_leak(window, self._prompt_ngrams):
            return "prompt_leak"
        if _JS_SCHEME.search(window) or _REMOTE_IMAGE.search(window):
            return "dangerous_markdown"
        if _has_disallowed(_EMAIL, window, self._allowlist):
            return "email"
        if _has_disallowed(_PHONE, window, self._allowlist):
            return "phone"
        if _has_disallowed(_DNI, window, self._allowlist):
            return "dni"
        if _has_disallowed(_IBAN, window, self._allowlist):
            return "iban"
        for match in _URL.finditer(window):
            domain = match.group(1).lower().split(":", 1)[0]
            if not any(
                domain == allowed or domain.endswith(f".{allowed}")
                for allowed in self._allowed_domains
            ):
                return "external_url"
        return None


def _has_disallowed(pattern: re.Pattern[str], text: str, allowlist: tuple[str, ...]) -> bool:
    for match in pattern.finditer(text):
        value = match.group(0).strip().lower()
        if any(allowed in value or value in allowed for allowed in allowlist):
            continue
        return True
    return False


def _ngrams(text: str, size: int) -> set[tuple[str, ...]]:
    words = tuple(word for word in _NORMALIZE.split(text.lower()) if word)
    if len(words) < size:
        return set()
    return {words[index : index + size] for index in range(len(words) - size + 1)}


def _prompt_leak(window: str, prompt_ngrams: set[tuple[str, ...]]) -> bool:
    if not prompt_ngrams:
        return False
    words = tuple(word for word in _NORMALIZE.split(window.lower()) if word)
    size = len(next(iter(prompt_ngrams)))
    if len(words) < size:
        return False
    window_ngrams = (words[index : index + size] for index in range(len(words) - size + 1))
    return any(ngram in prompt_ngrams for ngram in window_ngrams)
