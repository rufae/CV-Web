"""Esquemas del formulario de contacto."""

from pydantic import BaseModel, EmailStr


class ContactForm(BaseModel):
    name: str
    email: EmailStr
    message: str
