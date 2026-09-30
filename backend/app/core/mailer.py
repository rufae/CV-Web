"""Envío de correo asíncrono (T4.7).

`SmtpMailer` usa `aiosmtplib` con TLS implícito (465) o STARTTLS (587), con
timeout acotado. El contrato `Mailer` permite inyectar fakes en tests.
"""

from email.message import EmailMessage
from typing import Protocol

import aiosmtplib

from app.core.config import Settings


class Mailer(Protocol):
    async def send(self, message: EmailMessage) -> None: ...


class SmtpMailer:
    def __init__(self, settings: Settings) -> None:
        self._host = settings.smtp_host
        self._port = settings.smtp_port
        self._timeout = settings.smtp_timeout_s
        self._username = settings.email
        self._password = settings.password_application

    async def send(self, message: EmailMessage) -> None:
        await aiosmtplib.send(
            message,
            hostname=self._host,
            port=self._port,
            username=self._username,
            password=self._password,
            timeout=self._timeout,
            use_tls=self._port == 465,
            start_tls=self._port != 465,
        )
