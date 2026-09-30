"""Tests del formulario de contacto endurecido (T4.7)."""

from email.message import EmailMessage
from pathlib import Path

import httpx
import pytest
import respx
from fastapi import HTTPException
from pydantic import ValidationError

from app.core.config import Settings
from app.features.contact.outbox import ContactOutbox
from app.features.contact.schemas import ContactForm
from app.features.contact.service import TURNSTILE_URL, ContactService


class FakeMailer:
    def __init__(self) -> None:
        self.sent: list[EmailMessage] = []
        self.fail = False

    async def send(self, message: EmailMessage) -> None:
        if self.fail:
            raise RuntimeError("SMTP caído")
        self.sent.append(message)


def _settings(tmp_path: Path, *, turnstile: bool = False, configured: bool = True) -> Settings:
    return Settings(
        _env_file=None,  # type: ignore[call-arg]
        email="sender@example.com" if configured else "",
        password_application="secret" if configured else "",
        contact_to="receiver@example.com",
        data_path=str(tmp_path),
        turnstile_enabled=turnstile,
        turnstile_secret="turnstile-secret",
    )


def _service(
    tmp_path: Path, *, turnstile: bool = False, configured: bool = True
) -> tuple[ContactService, FakeMailer, ContactOutbox]:
    mailer = FakeMailer()
    outbox = ContactOutbox(tmp_path / "outbox.db")
    service = ContactService(
        _settings(tmp_path, turnstile=turnstile, configured=configured),
        mailer=mailer,
        outbox=outbox,
    )
    return service, mailer, outbox


def _form(message: str = "Hola", **overrides: object) -> ContactForm:
    data: dict[str, object] = {
        "name": "Visitante",
        "email": "visitante@example.com",
        "message": message,
    }
    data.update(overrides)
    return ContactForm.model_validate(data)


def test_schema_rejects_header_injection() -> None:
    with pytest.raises(ValidationError):
        _form(name="Rafael\r\nBcc: evil@example.com")


def test_schema_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        ContactForm.model_validate(
            {"name": "a", "email": "a@b.c", "message": "hola", "subject": "inyectado"}
        )


def test_schema_rejects_overlong_message() -> None:
    with pytest.raises(ValidationError):
        _form(message="x" * 2001)


async def test_delivery_escapes_html_and_sets_headers(tmp_path: Path) -> None:
    service, mailer, _ = _service(tmp_path)

    await service.send(_form(message="<script>alert(1)</script>"))

    assert len(mailer.sent) == 1
    message = mailer.sent[0]
    assert message["From"] == "sender@example.com"
    assert message["To"] == "receiver@example.com"
    assert message["Reply-To"] == "visitante@example.com"
    html_part = message.get_body(preferencelist=("html",))
    text_part = message.get_body(preferencelist=("plain",))
    assert html_part is not None and text_part is not None
    assert "&lt;script&gt;" in str(html_part.get_content())
    assert "<script>" not in str(html_part.get_content())
    assert "<script>" in str(text_part.get_content())


async def test_honeypot_drops_message_silently(tmp_path: Path) -> None:
    service, mailer, outbox = _service(tmp_path)

    await service.send(_form(honeypot="bot"))

    assert mailer.sent == []
    assert outbox.count() == 0


async def test_smtp_failure_is_queued_and_retried(tmp_path: Path) -> None:
    service, mailer, outbox = _service(tmp_path)
    mailer.fail = True

    await service.send(_form("primer mensaje"))

    assert outbox.count() == 1
    assert mailer.sent == []

    mailer.fail = False
    await service.send(_form("segundo mensaje"))

    assert outbox.count() == 0
    assert len(mailer.sent) == 2


async def test_unconfigured_service_returns_503(tmp_path: Path) -> None:
    service, _, _ = _service(tmp_path, configured=False)

    with pytest.raises(HTTPException) as excinfo:
        await service.send(_form())

    assert excinfo.value.status_code == 503


async def test_turnstile_without_token_is_rejected(tmp_path: Path) -> None:
    service, mailer, _ = _service(tmp_path, turnstile=True)

    with pytest.raises(HTTPException) as excinfo:
        await service.send(_form())

    assert excinfo.value.status_code == 400
    assert mailer.sent == []


@respx.mock
async def test_turnstile_success_allows_delivery(tmp_path: Path) -> None:
    respx.post(TURNSTILE_URL).mock(return_value=httpx.Response(200, json={"success": True}))
    service, mailer, _ = _service(tmp_path, turnstile=True)

    await service.send(_form(turnstile_token="token-valido"))

    assert len(mailer.sent) == 1


@respx.mock
async def test_turnstile_failure_blocks_delivery(tmp_path: Path) -> None:
    respx.post(TURNSTILE_URL).mock(return_value=httpx.Response(200, json={"success": False}))
    service, mailer, _ = _service(tmp_path, turnstile=True)

    with pytest.raises(HTTPException):
        await service.send(_form(turnstile_token="token-invalido"))

    assert mailer.sent == []


def test_outbox_backoff_and_due(tmp_path: Path) -> None:
    outbox = ContactOutbox(tmp_path / "outbox.db")
    message_id = outbox.add(
        sender="a@b.c",
        recipient="d@e.f",
        name="n",
        email="x@y.z",
        message="m",
        now=1000.0,
    )

    outbox.mark_failed(message_id, now=1000.0, base_backoff_s=60.0)

    assert outbox.due(now=1000.0) == []
    due = outbox.due(now=1000.0 + 121.0)
    assert len(due) == 1
    assert due[0].attempts == 1

    outbox.mark_sent(message_id)
    assert outbox.count() == 0
