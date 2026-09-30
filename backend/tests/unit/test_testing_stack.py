"""Tests del stack determinista de test (T7.3)."""

from app.llm.base import LLMProvider, Message
from app.testing import FAKE_TOKENS, FakeProvider, TestRetriever


async def test_fake_provider_streams_deterministic_tokens() -> None:
    provider: LLMProvider = FakeProvider()

    tokens = [token.text async for token in provider.stream([Message(role="user", content="hola")])]

    assert "".join(tokens) == "".join(FAKE_TOKENS)
    assert (await provider.health()).ok


async def test_test_retriever_refuses_off_domain() -> None:
    retriever = TestRetriever()

    assert (await retriever.retrieve("¿Cuál es la capital de Francia?")).is_empty
    assert (await retriever.retrieve("¿Dónde trabaja?")).is_empty is False
