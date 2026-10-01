"""Recuperador con umbral y rechazo temprano (T3.6).

- Top-K en Chroma; si **ningún** resultado alcanza `RAG_MIN_SCORE`, el llamante
  debe rechazar **sin llamar al LLM** (ahorra cómputo y evita alucinaciones por
  construcción). Si se decide responder, al LLM se le pasa el top-K completo.
- La consulta se vectoriza con el mismo prefijo de corpus que los chunks
  (codificación simétrica); sin él bge-m3 pierde ~0,1 de similitud y el umbral
  rechazaría preguntas legítimas.
- `hits` conserva **todos** los chunks (una nota larga puede necesitar varios
  para responder); `sources` deduplica por nota y se limita a `max_sources`.
- Las fuentes expuestas son `título + sección`, nunca rutas del vault.
"""

from dataclasses import dataclass
from typing import Protocol

from app.rag.store import QueryHit

DEFAULT_TOP_K = 5
DEFAULT_MIN_SCORE = 0.45
DEFAULT_MAX_SOURCES = 4


class ChatRetriever(Protocol):
    async def retrieve(self, query: str) -> "Retrieval": ...


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
        corpus_prefix: str = "",
    ) -> None:
        self._embedder = embedder
        self._store = store
        self._top_k = top_k
        self._min_score = min_score
        self._max_sources = max_sources
        self._corpus_prefix = corpus_prefix

    async def retrieve(self, query: str) -> Retrieval:
        # Mismo prefijo que en la ingesta: sin esta simetría los scores de
        # bge-m3 caen ~0,1 y el umbral rechaza preguntas legítimas.
        text = f"{self._corpus_prefix} — {query}" if self._corpus_prefix else query
        vectors = await self._embedder.embed([text])
        if not vectors:
            return Retrieval((), ())

        hits = self._store.query(vectors[0], top_k=self._top_k)
        if not hits or max(hit.score for hit in hits) < self._min_score:
            return Retrieval((), ())

        return Retrieval(hits=tuple(hits), sources=_unique_sources(hits, self._max_sources))


def _unique_sources(hits: list[QueryHit], max_sources: int) -> tuple[Source, ...]:
    """Una entrada por nota (el mejor chunk de cada una ya viene primero)."""
    seen: set[str] = set()
    sources: list[Source] = []
    for hit in hits:
        source_id = str(hit.metadata.get("source_id", hit.id))
        if source_id in seen:
            continue
        seen.add(source_id)
        sources.append(
            Source(
                n=len(sources) + 1,
                title=str(hit.metadata.get("title", "")),
                section=str(hit.metadata.get("section", "")),
            )
        )
        if len(sources) >= max_sources:
            break
    return tuple(sources)
