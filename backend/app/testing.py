"""Piezas deterministas para E2E/CI cuando `APP_ENV=test` (T7.3).

Nunca se activan en producción: `main.py` solo las usa con `APP_ENV=test`.
"""

from collections.abc import AsyncGenerator

from app.llm.base import Message, ProviderHealth, Token
from app.rag.retriever import Retrieval, Source
from app.rag.store import QueryHit

FAKE_TOKENS = ("Rafael ", "trabaja ", "en ", "AePTIC ", "y ", "usa ", "FastAPI ", "[1].")
EMPTY_QUERY_MARKERS = ("capital", "tortilla", "chiste", "receta")


class FakeProvider:
    """Proveedor LLM determinista para E2E."""

    name = "fake"
    model = "fake-1"

    async def health(self) -> ProviderHealth:
        return ProviderHealth(ok=True, latency_ms=1.0, model=self.model)

    async def aclose(self) -> None:
        return

    async def stream(
        self,
        messages: list[Message],
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> AsyncGenerator[Token, None]:
        for text in FAKE_TOKENS:
            yield Token(text=text)


class TestRetriever:
    """Retriever fijo: fuera de dominio devuelve vacío; el resto, una fuente."""

    async def retrieve(self, query: str) -> Retrieval:
        lowered = query.lower()
        if any(marker in lowered for marker in EMPTY_QUERY_MARKERS):
            return Retrieval((), ())
        hit = QueryHit(
            id="test-chunk",
            text="Rafael trabaja en AePTIC y usa FastAPI.",
            metadata={
                "source_id": "Public/experiencia/aeptik.md",
                "title": "Experiencia",
                "section": "AePTIC",
            },
            score=0.9,
        )
        return Retrieval(hits=(hit,), sources=(Source(n=1, title="Experiencia", section="AePTIC"),))
