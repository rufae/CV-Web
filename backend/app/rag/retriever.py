"""Recuperador con umbral y rechazo temprano (T3.6).

- Top-K en Chroma; si **ningún** resultado alcanza `RAG_MIN_SCORE`, el llamante
  debe rechazar **sin llamar al LLM** (ahorra cómputo y evita alucinaciones por
  construcción). Si se decide responder, al LLM se le pasa el top-K completo
  deduplicado (los chunks por debajo del umbral pueden ser el contexto útil).
- Deduplicación por nota (se conserva el mejor chunk de cada fuente).
- Las fuentes expuestas son `título + sección`, nunca rutas del vault.
"""

from dataclasses import dataclass
from typing import Protocol

from app.rag.store import QueryHit

DEFAULT_TOP_K = 5
DEFAULT_MIN_SCORE = 0.45
DEFAULT_MAX_SOURCES = 4


class EmbedderLike(Protocol):
    async def embed(self, texts: list[str]) -> list[list[float]]: ...


class VectorQuery(Protocol):
    def query(self, embedding: list[float], *, top_k: int = 5) -> list[QueryHit]: ...


@dataclass(frozen=True)
class Source:
    n: int
    title: str
    section: str


@dataclass(frozen=True)
class Retrieval:
    hits: tuple[QueryHit, ...]
    sources: tuple[Source, ...]

    @property
    def is_empty(self) -> bool:
        return not self.hits


class Retriever:
    def __init__(
        self,
        embedder: EmbedderLike,
        store: VectorQuery,
        *,
        top_k: int = DEFAULT_TOP_K,
        min_score: float = DEFAULT_MIN_SCORE,
        max_sources: int = DEFAULT_MAX_SOURCES,
    ) -> None:
        self._embedder = embedder
        self._store = store
        self._top_k = top_k
        self._min_score = min_score
        self._max_sources = max_sources

    async def retrieve(self, query: str) -> Retrieval:
        vectors = await self._embedder.embed([query])
        if not vectors:
            return Retrieval((), ())

        hits = self._store.query(vectors[0], top_k=self._top_k)
        deduped = _dedupe_by_source(hits)
        if not deduped or max(hit.score for hit in deduped) < self._min_score:
            return Retrieval((), ())

        sources = tuple(
            Source(
                n=index + 1,
                title=str(hit.metadata.get("title", "")),
                section=str(hit.metadata.get("section", "")),
            )
            for index, hit in enumerate(deduped[: self._max_sources])
        )
        return Retrieval(hits=tuple(deduped), sources=sources)


def _dedupe_by_source(hits: list[QueryHit]) -> list[QueryHit]:
    seen: set[str] = set()
    deduped: list[QueryHit] = []
    for hit in hits:
        source_id = str(hit.metadata.get("source_id", hit.id))
        if source_id in seen:
            continue
        seen.add(source_id)
        deduped.append(hit)
    return deduped
