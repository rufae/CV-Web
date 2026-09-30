"""Proveedor Ollama asíncrono con streaming NDJSON (T2.2).

Implementa el contrato `LLMProvider` contra la API HTTP de Ollama:

- `POST /api/chat` con `stream: true` (un objeto JSON por línea, NDJSON).
- `GET /api/tags` para comprobar disponibilidad del modelo configurado.
- Timeouts diferenciados: conexión corta, lectura larga.
- Errores mapeados a la taxonomía de `app.llm.errors`.
"""

import json
import time
from collections.abc import AsyncGenerator

import httpx

from app.llm.base import Message, ProviderHealth, Token
from app.llm.errors import FirstTokenTimeout, ProviderError, ProviderUnavailable

DEFAULT_CONNECT_TIMEOUT_S = 1.5
DEFAULT_READ_TIMEOUT_S = 60.0


class OllamaProvider:
    name = "ollama"

    def __init__(
        self,
        base_url: str,
        model: str,
        *,
        connect_timeout_s: float = DEFAULT_CONNECT_TIMEOUT_S,
        read_timeout_s: float = DEFAULT_READ_TIMEOUT_S,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._model = model
        self._client = client or httpx.AsyncClient(
            base_url=base_url,
            timeout=httpx.Timeout(read_timeout_s, connect=connect_timeout_s),
        )
        self._owns_client = client is None

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def health(self) -> ProviderHealth:
        start = time.perf_counter()
        try:
            response = await self._client.get("/api/tags")
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError):
            return ProviderHealth(ok=False, model=self._model)

        latency_ms = (time.perf_counter() - start) * 1000
        names = [str(item.get("name", "")) for item in payload.get("models", [])]
        available = any(name == self._model or name.startswith(f"{self._model}:") for name in names)
        return ProviderHealth(ok=available, latency_ms=latency_ms, model=self._model)

    async def stream(
        self,
        messages: list[Message],
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> AsyncGenerator[Token, None]:
        options: dict[str, object] = {"temperature": temperature}
        if max_tokens is not None:
            options["num_predict"] = max_tokens

        payload: dict[str, object] = {
            "model": self._model,
            "messages": [
                {"role": message.role, "content": message.content} for message in messages
            ],
            "stream": True,
            "options": options,
        }

        first_token_received = False
        try:
            async with self._client.stream("POST", "/api/chat", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError as exc:
                        raise ProviderError("NDJSON inválido del proveedor Ollama") from exc
                    if not isinstance(data, dict):
                        raise ProviderError("Evento NDJSON inesperado del proveedor Ollama")
                    if data.get("error"):
                        raise ProviderError(str(data["error"]))
                    message = data.get("message")
                    text = message.get("content", "") if isinstance(message, dict) else ""
                    if text:
                        first_token_received = True
                        yield Token(text=str(text))
                    if data.get("done"):
                        break
        except httpx.ConnectError as exc:
            raise ProviderUnavailable(f"No se pudo conectar con {self.name}") from exc
        except httpx.TimeoutException as exc:
            if not first_token_received:
                raise FirstTokenTimeout(f"{self.name} no respondió a tiempo") from exc
            raise ProviderError(f"{self.name} interrumpió el stream") from exc
        except httpx.HTTPStatusError as exc:
            raise ProviderError(f"{self.name} devolvió HTTP {exc.response.status_code}") from exc
