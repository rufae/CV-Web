"""Tests del recuperador con umbral (T3.6)."""

from app.rag.prompts import REFUSAL_MESSAGE
from app.rag.retriever import Retriever
from app.rag.store import QueryHit


class FakeEmbedder:
    def __init__(self, vector: list[float] | None = None) -> None:
        self.vector = vector or [1.0, 0.0]
        self.queries: list[list[str]] = []

    async def embed(self, texts: list[str]) -> list[list[float]]:
        self.queries.append(list(texts))
        return [self.vector for _ in texts]


class FakeStore:
    def __init__(self, hits: list[QueryHit]) -> None:
        self.hits = hits
        self.calls: list[tuple[list[float], int]] = []

    def query(self, embedding: list[float], *, top_k: int = 5) -> list[QueryHit]:
        self.calls.append((embedding, top_k))
        return self.hits[:top_k]


def _hit(
    hit_id: str,
    score: float,
    *,
    source_id: str = "Public/nota.md",
    title: str = "Experiencia",
    section: str = "AePTIC",
) -> QueryHit:
    return QueryHit(
        id=hit_id,
        text=f"texto de {hit_id}",
        metadata={"source_id": source_id, "title": title, "section": section},
        score=score,
    )


async def test_relevant_hits_are_returned_with_sources() -> None:
    store = FakeStore([_hit("a", 0.9), _hit("b", 0.6, source_id="Public/otra.md")])
    retriever = Retriever(FakeEmbedder(), store, min_score=0.5)

    result = await retriever.retrieve("¿qué experiencia tiene?")

    assert not result.is_empty
    assert len(result.hits) == 2
    assert result.sources[0].n == 1
    assert result.sources[0].title == "Experiencia"
    assert result.sources[0].section == "AePTIC"
    assert store.calls[0][1] == 5


async def test_below_threshold_refuses_without_sources() -> None:
    store = FakeStore([_hit("a", 0.2), _hit("b", 0.1)])
    retriever = Retriever(FakeEmbedder(), store, min_score=0.45)

    result = await retriever.retrieve("¿capital de Francia?")

    assert result.is_empty
    assert result.sources == ()
    assert REFUSAL_MESSAGE


async def test_context_includes_chunks_below_threshold_when_best_passes() -> None:
    store = FakeStore(
        [
            _hit("a", 0.9, source_id="Public/nota.md"),
            _hit("b", 0.4, source_id="Public/otra.md"),
        ]
    )
    retriever = Retriever(FakeEmbedder(), store, min_score=0.5)

    result = await retriever.retrieve("pregunta")

    assert not result.is_empty
    assert [hit.id for hit in result.hits] == ["a", "b"]
    assert len(result.sources) == 2


async def test_hits_are_deduped_by_note_keeping_best() -> None:
    store = FakeStore(
        [
            _hit("a", 0.9, source_id="Public/nota.md"),
            _hit("b", 0.8, source_id="Public/nota.md"),
            _hit("c", 0.7, source_id="Public/otra.md"),
        ]
    )
    retriever = Retriever(FakeEmbedder(), store, min_score=0.5)

    result = await retriever.retrieve("pregunta")

    assert [hit.id for hit in result.hits] == ["a", "c"]
    assert len(result.sources) == 2


async def test_sources_are_limited_and_numbered() -> None:
    store = FakeStore([_hit(f"c{i}", 0.9, source_id=f"Public/nota{i}.md") for i in range(6)])
    retriever = Retriever(FakeEmbedder(), store, min_score=0.5, max_sources=3)

    result = await retriever.retrieve("pregunta")

    assert [source.n for source in result.sources] == [1, 2, 3]
    assert all(not hasattr(source, "source_id") for source in result.sources)


async def test_top_k_is_configurable() -> None:
    store = FakeStore([_hit(f"c{i}", 0.9, source_id=f"Public/n{i}.md") for i in range(10)])
    retriever = Retriever(FakeEmbedder(), store, top_k=2, min_score=0.5, max_sources=10)

    result = await retriever.retrieve("pregunta")

    assert len(result.hits) == 2
    assert store.calls[0][1] == 2
