"""Almacén SQLite del feedback (T4.9).

No guarda la pregunta ni la IP; solo metadatos anónimos: timestamp, rating,
versión del prompt, ids de fuentes (números), tier y si fue rechazo. El
comentario es opcional y voluntario.
"""

import json
import sqlite3
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from app.features.feedback.schemas import FeedbackRequest

_SCHEMA = """
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at REAL NOT NULL,
    message_id TEXT NOT NULL UNIQUE,
    rating TEXT NOT NULL,
    comment TEXT,
    prompt_version TEXT,
    sources TEXT NOT NULL DEFAULT '[]',
    tier TEXT,
    refused INTEGER NOT NULL DEFAULT 0
);
"""


@dataclass(frozen=True)
class FeedbackEntry:
    id: int
    created_at: float
    message_id: str
    rating: str
    comment: str | None
    prompt_version: str | None
    sources: list[int]
    tier: str | None
    refused: bool


class FeedbackStore:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._connection() as conn:
            conn.execute(_SCHEMA)

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self._path)
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def add(self, payload: FeedbackRequest, *, now: float | None = None) -> bool:
        """Registra el feedback; devuelve `False` si `message_id` ya existía."""
        timestamp = time.time() if now is None else now
        try:
            with self._connection() as conn:
                conn.execute(
                    "INSERT INTO feedback (created_at, message_id, rating, comment, "
                    "prompt_version, sources, tier, refused) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        timestamp,
                        payload.message_id,
                        payload.rating,
                        payload.comment,
                        payload.prompt_version,
                        json.dumps(payload.sources),
                        payload.tier,
                        1 if payload.refused else 0,
                    ),
                )
        except sqlite3.IntegrityError:
            return False
        return True

    def count(self) -> int:
        with self._connection() as conn:
            row = conn.execute("SELECT COUNT(*) FROM feedback").fetchone()
        return int(row[0]) if row else 0

    def downs(self) -> list[FeedbackEntry]:
        with self._connection() as conn:
            rows = conn.execute(
                "SELECT id, created_at, message_id, rating, comment, prompt_version, "
                "sources, tier, refused FROM feedback WHERE rating = 'down' ORDER BY id"
            ).fetchall()
        return [
            FeedbackEntry(
                id=int(row[0]),
                created_at=float(row[1]),
                message_id=str(row[2]),
                rating=str(row[3]),
                comment=row[4],
                prompt_version=row[5],
                sources=json.loads(row[6] or "[]"),
                tier=row[7],
                refused=bool(row[8]),
            )
            for row in rows
        ]
