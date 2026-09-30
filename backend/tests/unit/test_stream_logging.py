"""Tests de los logs estructurados del router (T2.6)."""

from collections.abc import AsyncGenerator

import pytest

from app.llm.base import Message, ProviderHealth, Token
from app.llm.errors import ProviderError
from app.llm.health import HealthMonitor, MonitorConfig
from app.llm.router import LLMRouter


class StubLLM:
    def __init__(
        self,
        name: str,
        *,
        tokens: tuple[str, ...] = ("a", "b"),
        fail_after_first: ProviderError | None = None,
    ) -> None:
        self.name = name
        self.model = f"{name}-model"
        self.tokens = tokens
        self.fail_after_first = fail_after_first

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
        for index, text in enumerate(self.tokens):
            if index == 1 and self.fail_after_first is not None:
                raise self.fail_after_first
            yield Token(text=text)


def _messages() -> list[Message]:
    return [Message(role="user", content="hola")]


async def _router(provider: StubLLM) -> LLMRouter:
    monitor = HealthMonitor([provider], config=MonitorConfig())
    await monitor.check_once()
    return LLMRouter([provider], monitor)


async def test_one_log_line_per_completed_stream(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level("INFO", logger="cvweb.llm")
    router = await _router(StubLLM("tower"))

    routed = await router.stream(_messages())
    async for _ in routed:
        pass

    records = [record for record in caplog.records if record.message == "llm_stream"]
    assert len(records) == 1
    extra = records[0].__dict__
    assert extra["provider"] == "tower"
    assert extra["model"] == "tower-model"
    assert extra["outcome"] == "done"
    assert extra["first_token_ms"] is not None
    assert extra["latency_ms"] is not None


async def test_error_outcome_is_logged_once(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level("INFO", logger="cvweb.llm")
    provider = StubLLM("tower", fail_after_first=ProviderError("corte"))
    router = await _router(provider)

    routed = await router.stream(_messages())
    with pytest.raises(ProviderError):
        async for _ in routed:
            pass

    records = [record for record in caplog.records if record.message == "llm_stream"]
    assert len(records) == 1
    assert records[0].__dict__["outcome"] == "error:ProviderError"
