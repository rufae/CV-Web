"""Cliente de embeddings asíncrono contra Ollama (T3.4).

Vectoriza siempre en el nodo Dell con `bge-m3` (D4): el mismo modelo y espacio
vectorial se usan en indexado y en consulta. Soporta batching.
"""

import httpx

from app.llm.errors import ProviderError, ProviderUnavailable

DEFAULT_BATCH_SIZE = 16
DEFAULT_TIMEOUT_S = 60.0


class OllamaEmbedder:
    def __init__(
        self,
        base_url: str,
        model: str = "bge-m3",
        *,
        batch_size: int = DEFAULT_BATCH_SIZE,
        timeout_s: float = DEFAULT_TIMEOUT_S,
        connect_timeout_s: float = 5.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._model = model
        self._batch_size = max(1, batch_size)
        self._client = client or httpx.AsyncClient(
            base_url=base_url,
            timeout=httpx.Timeout(timeout_s, connect=connect_timeout_s),
        )
        self._owns_client = client is None

    @property
    def model(self) -> str:
        return self._model

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def embed(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for start in range(0, len(texts), self._batch_size):
            batch = texts[start : start + self._batch_size]
            vectors.extend(await self._embed_batch(batch))
        return vectors

    async def _embed_batch(self, batch: list[str]) -> list[list[float]]:
        try:
            response = await self._client.post(
                "/api/embed",
                json={"model": self._model, "input": batch},
            )
            response.raise_for_status()
            payload = response.json()
        except httpx.ConnectError as exc:
            raise ProviderUnavailable("No se pudo conectar con el servicio de embeddings") from exc
        except httpx.TimeoutException as exc:
            raise ProviderError("Timeout del servicio de embeddings") from exc
        except httpx.HTTPStatusError as exc:
            raise ProviderError(f"Embeddings devolvió HTTP {exc.response.status_code}") from exc
        except ValueError as exc:
            raise ProviderError("Respuesta de embeddings inválida") from exc

        embeddings = payload.get("embeddings")
        if not isinstance(embeddings, list) or len(embeddings) != len(batch):
            raise ProviderError("Número de embeddings inesperado")
        return [[float(value) for value in vector] for vector in embeddings]
