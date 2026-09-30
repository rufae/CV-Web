"""Esquemas del endpoint de chat (T4.1).

`ChatRequest` es el contrato nuevo (SSE); `Prompt` se mantiene para el alias
legacy `/ask` hasta T5.7.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

MAX_MESSAGE_CHARS = 500
MAX_HISTORY_TURNS = 6


class Prompt(BaseModel):
    message: str


class Turn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: Literal["user", "assistant"]
    content: str = Field(max_length=MAX_MESSAGE_CHARS)


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str = Field(min_length=1, max_length=MAX_MESSAGE_CHARS)
    history: list[Turn] = Field(default_factory=list, max_length=MAX_HISTORY_TURNS * 2)
    lang: Literal["es", "en"] | None = None
