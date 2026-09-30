"""Utilidades de seguridad HTTP: IP del cliente y tope de tamaño de cuerpo (T4.2)."""

import json

from fastapi import Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send


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
