"""Router de proveedores LLM con failover antes del primer token (T2.4).

Reglas:
- Orden de prioridad el de la lista recibida (vendrá de `LLM_PROVIDERS_ORDER`).
- Se saltan proveedores en estado `DOWN` (circuit breaker de `HealthMonitor`).
- El failover solo ocurre **antes del primer token**. Si el stream se corta a
  mitad, el error se propaga (no se mezclan respuestas de dos modelos).
- Semáforo global para acotar la concurrencia; cola con límite que devuelve
  `QueueOverflow` (se traducirá a HTTP 503 con `Retry-After`).
"""

import asyncio
import logging
import time
from collections.abc import AsyncGenerator, Callable
from contextlib import suppress
from dataclasses import dataclass

from app.llm.base import LLMProvider, Message, Token
from app.llm.errors import (
    FirstTokenTimeout,
    LLMError,
    ProviderError,
    ProviderUnavailable,
    QueueOverflow,
)
from app.llm.health import HealthMonitor

DEFAULT_FIRST_TOKEN_TIMEOUT_S = 15.0
DEFAULT_MAX_CONCURRENCY = 2
DEFAULT_QUEUE_LIMIT = 10
DEFAULT_RETRY_AFTER_S = 5


@dataclass
class StreamMeta:
    provider: str
    model: str | None = None
    first_token_ms: float | None = None


class RoutedStream:
    """Stream enrutado: itera tokens y expone metadatos de la ruta elegida."""

    def __init__(
        self,
        meta: StreamMeta,
        tokens: AsyncGenerator[Token, None],
        *,
        clock: Callable[[], float],
        on_close: Callable[[], None],
        logger: logging.Logger,
    ) -> None:
        self.meta = meta
        self._tokens = tokens
        self._clock = clock
        self._on_close = on_close
        self._logger = logger
        self._started_s = clock()
        self._first_token = True
        self._closed = False
        self._outcome = "cancelled"

    def __aiter__(self) -> "RoutedStream":
        return self

    async def __anext__(self) -> Token:
        try:
            token = await self._tokens.__anext__()
        except StopAsyncIteration:
            self._outcome = "done"
            await self.aclose()
            raise
        except BaseException as exc:
            self._outcome = (
                "cancelled"
                if isinstance(exc, asyncio.CancelledError)
                else f"error:{type(exc).__name__}"
            )
            await self.aclose()
            raise

        if self._first_token:
            self.meta.first_token_ms = (self._clock() - self._started_s) * 1000
            self._first_token = False
        return token

    async def aclose(self) -> None:
        if self._closed:
            return
        self._closed = True
        with suppress(Exception):
            await self._tokens.aclose()
        self._on_close()
        self._logger.info(
            "llm_stream",
            extra={
                "provider": self.meta.provider,
                "model": self.meta.model,
                "first_token_ms": self.meta.first_token_ms,
                "latency_ms": round((self._clock() - self._started_s) * 1000, 1),
                "outcome": self._outcome,
            },
        )


class LLMRouter:
    def __init__(
        self,
        providers: list[LLMProvider],
        monitor: HealthMonitor,
        *,
        first_token_timeout_s: float = DEFAULT_FIRST_TOKEN_TIMEOUT_S,
        max_concurrency: int = DEFAULT_MAX_CONCURRENCY,
        queue_limit: int = DEFAULT_QUEUE_LIMIT,
        retry_after_s: int = DEFAULT_RETRY_AFTER_S,
        clock: Callable[[], float] = time.perf_counter,
        logger: logging.Logger | None = None,
    ) -> None:
        self._providers = providers
        self._monitor = monitor
        self._first_token_timeout_s = first_token_timeout_s
        self._queue_limit = queue_limit
        self._retry_after_s = retry_after_s
        self._clock = clock
        self._logger = logger or logging.getLogger("cvweb.llm")
        self._semaphore = asyncio.Semaphore(max_concurrency)
        self._waiters = 0
        self._failovers = 0

    @property
    def failovers(self) -> int:
        return self._failovers

    async def stream(
        self,
        messages: list[Message],
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> RoutedStream:
        await self._acquire_slot()
        try:
            provider, tokens = await self._start_stream(
                messages, temperature=temperature, max_tokens=max_tokens
            )
        except BaseException:
            self._release_slot()
            raise

        return RoutedStream(
            StreamMeta(provider=provider.name, model=provider.model),
            tokens,
            clock=self._clock,
            on_close=self._release_slot,
            logger=self._logger,
        )

    async def _start_stream(
        self,
        messages: list[Message],
        *,
        temperature: float,
        max_tokens: int | None,
    ) -> tuple[LLMProvider, AsyncGenerator[Token, None]]:
        candidates = self._available_providers()
        if not candidates:
            raise ProviderUnavailable("No hay proveedores de IA disponibles")

        last_error: LLMError = ProviderUnavailable("No hay proveedores de IA disponibles")
        for provider in candidates:
            outcome = await self._try_start(
                provider, messages, temperature=temperature, max_tokens=max_tokens
            )
            if isinstance(outcome, LLMError):
                last_error = outcome
                self._failovers += 1
                continue
            first_token, stream = outcome
            return provider, self._chain_first(first_token, stream)

        raise last_error

    async def _try_start(
        self,
        provider: LLMProvider,
        messages: list[Message],
        *,
        temperature: float,
        max_tokens: int | None,
    ) -> tuple[Token, AsyncGenerator[Token, None]] | LLMError:
        stream = provider.stream(messages, temperature=temperature, max_tokens=max_tokens)
        try:
            first = await asyncio.wait_for(stream.__anext__(), timeout=self._first_token_timeout_s)
        except TimeoutError:
            with suppress(Exception):
                await stream.aclose()
            return FirstTokenTimeout(f"{provider.name} no respondió a tiempo")
        except StopAsyncIteration:
            with suppress(Exception):
                await stream.aclose()
            return ProviderError(f"{provider.name} devolvió un stream vacío")
        except LLMError as exc:
            with suppress(Exception):
                await stream.aclose()
            return exc
        return first, stream

    async def _chain_first(
        self, first: Token, stream: AsyncGenerator[Token, None]
    ) -> AsyncGenerator[Token, None]:
        try:
            yield first
            async for token in stream:
                yield token
        finally:
            with suppress(Exception):
                await stream.aclose()

    def _available_providers(self) -> list[LLMProvider]:
        return [
            provider for provider in self._providers if self._monitor.is_available(provider.name)
        ]

    async def _acquire_slot(self) -> None:
        if self._semaphore.locked():
            if self._waiters >= self._queue_limit:
                raise QueueOverflow(self._retry_after_s)
            self._waiters += 1
            try:
                await self._semaphore.acquire()
            finally:
                self._waiters -= 1
        else:
            await self._semaphore.acquire()

    def _release_slot(self) -> None:
        self._semaphore.release()
