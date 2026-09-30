"""Contrato de proveedores LLM y tipos compartidos (T2.1).

Los proveedores se comunican mediante `Message`/`Token` y exponen `health()`
(staff de disponibilidad) y `stream()` (generación por streaming).
"""

from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Literal, Protocol, runtime_checkable

Role = Literal["system", "user", "assistant"]


@dataclass(frozen=True)
class Message:
    role: Role
    content: str


@dataclass(frozen=True)
class Token:
    text: str


@dataclass(frozen=True)
class ProviderHealth:
    ok: bool
    latency_ms: float | None = None
    model: str | None = None


@runtime_checkable
class LLMProvider(Protocol):
    """Protocolo que debe cumplir todo proveedor (Ollama, Gemini, fakes...)."""

    name: str

    async def health(self) -> ProviderHealth:
        """Comprueba disponibilidad y latencia del proveedor."""
        ...

    def stream(
        self,
        messages: list[Message],
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> AsyncGenerator[Token, None]:
        """Genera la respuesta en streaming como secuencia de tokens.

        Devolver un `AsyncGenerator` permite cancelar aguas arriba con `aclose()`.
        """
        ...
