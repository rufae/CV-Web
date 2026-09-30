"""Esquemas del endpoint de chat."""

from pydantic import BaseModel


class Prompt(BaseModel):
    message: str
