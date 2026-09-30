"""Esquema endurecido del formulario de contacto (T4.7)."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

MAX_NAME = 100
MAX_MESSAGE = 2000


class ContactForm(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=MAX_NAME)
    email: EmailStr
    message: str = Field(min_length=1, max_length=MAX_MESSAGE)
    honeypot: str = Field(default="", max_length=200)
    turnstile_token: str | None = Field(default=None, max_length=2048)

    @field_validator("name", "email")
    @classmethod
    def _reject_header_injection(cls, value: str) -> str:
        if "\r" in value or "\n" in value:
            raise ValueError("El campo contiene caracteres no permitidos")
        return value
