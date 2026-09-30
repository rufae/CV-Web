"""Servicio de contacto endurecido (T4.7).

- Valida y escapa; el nombre del visitante nunca va en cabeceras.
- `Reply-To` apunta al visitante; `From` es la cuenta propia.
- Honeypot silencioso y Turnstile opcional.
- Si el SMTP falla, el mensaje queda en el outbox y se reintenta con backoff;
  el error real solo va a los logs.
"""

import html
import logging
from email.message import EmailMessage
from pathlib import Path

import httpx
from fastapi import HTTPException

from app.core.config import Settings
from app.core.mailer import Mailer, SmtpMailer
from app.features.contact.outbox import ContactOutbox
from app.features.contact.schemas import ContactForm

logger = logging.getLogger("cvweb.contact")

SUBJECT = "Nuevo mensaje desde CV Web"
TURNSTILE_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


class ContactService:
    def __init__(
        self,
        settings: Settings,
        *,
        mailer: Mailer | None = None,
        outbox: ContactOutbox | None = None,
    ) -> None:
        self._settings = settings
        self._mailer = mailer or SmtpMailer(settings)
        self._outbox = outbox or ContactOutbox(Path(settings.data_path) / "contact_outbox.db")

    @property
    def outbox(self) -> ContactOutbox:
        return self._outbox

    async def send(self, form: ContactForm) -> None:
        if not self._settings.contact_enabled:
            raise HTTPException(
                status_code=503,
                detail="El formulario de contacto no está disponible ahora mismo.",
            )
        if form.honeypot.strip():
            logger.info("contact_honeypot_dropped")
            return
        if self._settings.turnstile_enabled and not await self._verify_turnstile(
            form.turnstile_token
        ):
            raise HTTPException(
                status_code=400,
                detail="No se pudo verificar que seas humano.",
            )

        await self.flush_outbox()
        await self._deliver(name=form.name, email=form.email, message=form.message)

    async def flush_outbox(self) -> None:
        for pending in self._outbox.due():
            await self._deliver(
                name=pending.name,
                email=pending.email,
                message=pending.message,
                outbox_id=pending.id,
            )

    async def _deliver(
        self,
        *,
        name: str,
        email: str,
        message: str,
        outbox_id: int | None = None,
    ) -> bool:
        sender = self._settings.email
        recipient = self._settings.contact_to or sender
        try:
            await self._mailer.send(self._build_message(name=name, email=email, message=message))
        except Exception:
            logger.error("contact_delivery_failed", extra={"outbox_id": outbox_id})
            if outbox_id is None:
                self._outbox.add(
                    sender=sender,
                    recipient=recipient,
                    name=name,
                    email=email,
                    message=message,
                )
            else:
                self._outbox.mark_failed(outbox_id)
            return False

        if outbox_id is not None:
            self._outbox.mark_sent(outbox_id)
        return True

    def _build_message(self, *, name: str, email: str, message: str) -> EmailMessage:
        sender = self._settings.email
        recipient = self._settings.contact_to or sender

        email_message = EmailMessage()
        email_message["Subject"] = SUBJECT
        email_message["From"] = sender
        email_message["To"] = recipient
        email_message["Reply-To"] = email
        email_message.set_content(f"Nombre: {name}\nEmail: {email}\nMensaje:\n{message}")
        email_message.add_alternative(
            _html_body(name=name, email=email, message=message),
            subtype="html",
        )
        return email_message

    async def _verify_turnstile(self, token: str | None) -> bool:
        if not token:
            return False
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    TURNSTILE_URL,
                    data={"secret": self._settings.turnstile_secret, "response": token},
                )
            return bool(response.json().get("success"))
        except httpx.HTTPError:
            return False


def _html_body(*, name: str, email: str, message: str) -> str:
    safe_name = html.escape(name)
    safe_email = html.escape(email)
    safe_message = html.escape(message)
    return f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8" /></head>
<body style="margin:0; padding:0; background-color:#f4f6f8; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
<table align="center" width="600" cellpadding="0" cellspacing="0" style="background:#fff; margin: 40px auto; border-radius: 10px;">
<tr><td style="background: #0052cc; padding: 20px 30px; color: #ffffff; text-align: center;">
<h1 style="margin: 0;">Nuevo mensaje desde CV Web</h1></td></tr>
<tr><td style="padding: 30px;">
<p><strong>Nombre:</strong> {safe_name}</p>
<p><strong>Email:</strong> {safe_email}</p>
<p><strong>Mensaje:</strong></p>
<p style="white-space: pre-line;">{safe_message}</p>
</td></tr>
</table>
</body>
</html>
"""
