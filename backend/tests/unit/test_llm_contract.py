"""Tests del contrato de proveedores LLM (T2.1)."""

from collections.abc import AsyncGenerator

import pytest

from app.llm.base import LLMProvider, Message, ProviderHealth, Token
from app.llm.errors import FirstTokenTimeout, ProviderError, ProviderUnavailable


class FakeProvider:
    """Proveedor determinista para tests: emite tokens o falla a demanda."""

    name = "fake"
    model = "fake-1"

    def __init__(
        self,
        tokens: list[str] | None = None,
        fail: type[Exception] | None = None,
    ) -> None:
        self._tokens = tokens if tokens is not None else ["Hola", " mundo"]
        self._fail = fail

    async def health(self) -> ProviderHealth:
        return ProviderHealth(ok=self._fail is None, latency_ms=1.0, model="fake-1")

    async def aclose(self) -> None:
        return

    async def stream(
        self,
        messages: list[Message],
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> AsyncGenerator[Token, None]:
        if self._fail is not None:
            raise self._fail("fallo simulado")
        for text in self._tokens:
            yield Token(text=text)


async def test_protocol_is_satisfied() -> None:
    provider: LLMProvider = FakeProvider()
    assert provider.name == "fake"

    health = await provider.health()

    assert health.ok
    assert health.model == "fake-1"


async def test_stream_emits_tokens_in_order() -> None:
    provider = FakeProvider(tokens=["Rafa", "el"])
    tokens = [token.text async for token in provider.stream([Message(role="user", content="hola")])]

    assert tokens == ["Rafa", "el"]


@pytest.mark.parametrize("error", [ProviderUnavailable, FirstTokenTimeout, ProviderError])
async def test_stream_propagates_errors(error: type[Exception]) -> None:
    provider = FakeProvider(fail=error)

    with pytest.raises(error):
        async for _ in provider.stream([Message(role="user", content="hola")]):
            pass
