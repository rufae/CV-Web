"""Esquema del feedback de respuestas (T4.9)."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

MAX_COMMENT_CHARS = 300


class FeedbackRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message_id: str = Field(min_length=1, max_length=64)
    rating: Literal["up", "down"]
    comment: str | None = Field(default=None, max_length=MAX_COMMENT_CHARS)
    prompt_version: str | None = Field(default=None, max_length=20)
    sources: list[int] = Field(default_factory=list, max_length=10)
    tier: Literal["gpu", "cpu"] | None = None
    refused: bool = False
