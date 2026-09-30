"""Proveedor Gemini opcional (T2.5).

Se activa solo con `GEMINI_ENABLED=true`; `app/llm/factory.py` importa este
módulo de forma perezosa, así que con la bandera desactivada `google.genai`
ni siquiera se carga.
"""

import time
from collections.abc import AsyncGenerator
from typing import Any, cast

from google import genai
from google.genai import types

from app.llm.base import Message, ProviderHealth, Token
from app.llm.errors import ProviderError

DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"


class GeminiProvider:
    name = "gemini"

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_GEMINI_MODEL,
        *,
        client: genai.Client | None = None,
    ) -> None:
        self._model = model or DEFAULT_GEMINI_MODEL
        self._client = client or genai.Client(api_key=api_key)

    @property
    def model(self) -> str:
        return self._model

    async def aclose(self) -> None:
        """Los clientes de `google-genai` no exponen cierre asíncrono explícito."""
        return

    async def health(self) -> ProviderHealth:
        start = time.perf_counter()
        try:
            model_info = await self._client.aio.models.get(model=self._model)
        except Exception:
            return ProviderHealth(ok=False, model=self._model)

        latency_ms = (time.perf_counter() - start) * 1000
        return ProviderHealth(ok=True, latency_ms=latency_ms, model=model_info.name or self._model)

    async def stream(
        self,
        messages: list[Message],
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> AsyncGenerator[Token, None]:
        contents = [
            types.Content(role=message.role, parts=[types.Part(text=message.content)])
            for message in messages
        ]
        config = types.GenerateContentConfig(temperature=temperature)
        if max_tokens is not None:
            config.max_output_tokens = max_tokens

        try:
            stream = await self._client.aio.models.generate_content_stream(
                model=self._model,
                contents=cast(Any, contents),
                config=config,
            )
            async for chunk in stream:
                text = chunk.text
                if text:
                    yield Token(text=text)
        except ProviderError:
            raise
        except Exception as exc:
            raise ProviderError(f"gemini: {exc}") from exc
