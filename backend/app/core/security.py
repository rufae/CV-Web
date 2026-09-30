"""Utilidades de seguridad HTTP (T4.2/T4.8): IP, tope de cuerpo, cabeceras y request-id."""

import json
import uuid

from fastapi import Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.logging import request_id_var

SECURITY_HEADERS: dict[str, str] = {
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=()",
    "X-Frame-Options": "DENY",
    "Content-Security-Policy": (
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; font-src 'self'; connect-src 'self'; object-src 'none'; "
        "base-uri 'self'; form-action 'self'; frame-ancestors 'none'"
    ),
}
_NO_STORE_PATHS = {"/api/chat", "/api/contact"}


def client_ip(request: Request) -> str:
    """IP real del cliente (uvicorn la resuelve con `--proxy-headers`)."""
    if request.client is not None:
        return request.client.host
    return "unknown"


class _BodyTooLarge(Exception):
    pass


async def _json_response(send: Send, status: int, content: dict[str, object]) -> None:
    body = json.dumps(content).encode()
    await send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(body)).encode()),
            ],
        }
    )
    await send({"type": "http.response.body", "body": body})


class BodySizeLimitMiddleware:
    """Rechaza cuerpos mayores que `max_bytes` con 413.

    Comprueba `Content-Length` y, si no está, corta la lectura del stream.
    """

    def __init__(self, app: ASGIApp, *, max_bytes: int) -> None:
        self._app = app
        self._max_bytes = max_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return

        headers = {
            key.decode("latin-1").lower(): value.decode("latin-1")
            for key, value in scope.get("headers", [])
        }
        content_length = headers.get("content-length")
        if (
            content_length is not None
            and content_length.isdigit()
            and int(content_length) > self._max_bytes
        ):
            await _json_response(send, 413, {"code": "payload_too_large"})
            return

        received = 0
        started = False

        async def limited_receive() -> Message:
            nonlocal received
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > self._max_bytes:
                    raise _BodyTooLarge
            return message

        async def tracking_send(message: Message) -> None:
            nonlocal started
            if message["type"] == "http.response.start":
                started = True
            await send(message)

        try:
            await self._app(scope, limited_receive, tracking_send)
        except _BodyTooLarge:
            if not started:
                await _json_response(send, 413, {"code": "payload_too_large"})


class SecurityHeadersMiddleware:
    """Añade cabeceras de seguridad y `Cache-Control: no-store` a la API."""

    def __init__(self, app: ASGIApp) -> None:
        self._app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return

        path = str(scope.get("path", ""))
        no_store = path.startswith("/api/") or path in _NO_STORE_PATHS

        async def send_with_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                present = {key.lower() for key, _ in headers}
                extra = dict(SECURITY_HEADERS)
                if no_store:
                    extra["Cache-Control"] = "no-store"
                for key, value in extra.items():
                    encoded = key.lower().encode()
                    if encoded not in present:
                        headers.append((encoded, value.encode()))
                message["headers"] = headers
            await send(message)

        await self._app(scope, receive, send_with_headers)


class RequestIdMiddleware:
    """Genera un `X-Request-ID` por petición y lo propaga a los logs."""

    def __init__(self, app: ASGIApp) -> None:
        self._app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return

        request_id = uuid.uuid4().hex[:16]
        token = request_id_var.set(request_id)

        async def send_with_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((b"x-request-id", request_id.encode()))
                message["headers"] = headers
            await send(message)

        try:
            await self._app(scope, receive, send_with_id)
        finally:
            request_id_var.reset(token)
