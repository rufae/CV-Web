"""Outbox SQLite para mensajes de contacto (T4.7).

Persiste los mensajes que no se pudieron enviar y los reintenta con backoff
exponencial. El visitante siempre recibe una confirmación genérica.
"""

import sqlite3
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

_SCHEMA = """
CREATE TABLE IF NOT EXISTS contact_outbox (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at REAL NOT NULL,
    next_attempt_at REAL NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    sender TEXT NOT NULL,
    recipient TEXT NOT NULL,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    message TEXT NOT NULL
);
"""

DEFAULT_MAX_ATTEMPTS = 8
DEFAULT_BASE_BACKOFF_S = 60.0


@dataclass(frozen=True)
class OutboxMessage:
    id: int
    sender: str
    recipient: str
    name: str
    email: str
    message: str
    attempts: int


class ContactOutbox:
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

    def add(
        self,
        *,
        sender: str,
        recipient: str,
        name: str,
        email: str,
        message: str,
        now: float | None = None,
    ) -> int:
        timestamp = time.time() if now is None else now
        with self._connection() as conn:
            cursor = conn.execute(
                "INSERT INTO contact_outbox "
                "(created_at, next_attempt_at, sender, recipient, name, email, message) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (timestamp, timestamp, sender, recipient, name, email, message),
            )
            return int(cursor.lastrowid or 0)

    def due(
        self,
        *,
        now: float | None = None,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    ) -> list[OutboxMessage]:
        timestamp = time.time() if now is None else now
        with self._connection() as conn:
            rows = conn.execute(
                "SELECT id, sender, recipient, name, email, message, attempts "
                "FROM contact_outbox "
                "WHERE next_attempt_at <= ? AND attempts < ? ORDER BY id",
                (timestamp, max_attempts),
            ).fetchall()
        return [OutboxMessage(*row) for row in rows]

    def mark_sent(self, message_id: int) -> None:
        with self._connection() as conn:
            conn.execute("DELETE FROM contact_outbox WHERE id = ?", (message_id,))

    def mark_failed(
        self,
        message_id: int,
        *,
        now: float | None = None,
        base_backoff_s: float = DEFAULT_BASE_BACKOFF_S,
    ) -> None:
        timestamp = time.time() if now is None else now
        with self._connection() as conn:
            row = conn.execute(
                "SELECT attempts FROM contact_outbox WHERE id = ?", (message_id,)
            ).fetchone()
            attempts = int(row[0]) + 1 if row else 1
            backoff = base_backoff_s * (2 ** min(attempts, 6))
            conn.execute(
                "UPDATE contact_outbox SET attempts = ?, next_attempt_at = ? WHERE id = ?",
                (attempts, timestamp + backoff, message_id),
            )

    def count(self) -> int:
        with self._connection() as conn:
            row = conn.execute("SELECT COUNT(*) FROM contact_outbox").fetchone()
        return int(row[0]) if row else 0
