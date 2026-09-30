"""Pipeline de ingesta incremental e idempotente (T3.5).

Planifica los cambios comparando el manifiesto (hash por nota), aplica solo
altas/cambios/bajas y guarda el nuevo manifiesto. Con `--rebuild` reconstruye
todo en una colección temporal y hace *swap* atómico (sin ventana con índice
vacío). La ingesta incremental nunca vacía la colección activa.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from app.rag.chunking import Chunk, chunk_note
from app.rag.ingest import extract_public_notes
from app.rag.store import ChromaStore


class Embedder(Protocol):
    async def embed(self, texts: list[str]) -> list[list[float]]: ...

    async def aclose(self) -> None: ...


@dataclass(frozen=True)
class IngestPlan:
    current: dict[str, str]
    added: tuple[str, ...]
    updated: tuple[str, ...]
    removed: tuple[str, ...]
    unchanged: int


@dataclass(frozen=True)
class IngestSummary:
    added: int
    updated: int
    removed: int
    unchanged: int
    chunks: int
    rebuild: bool
    dry_run: bool


def load_manifest(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {str(key): str(value) for key, value in data.items()}


def save_manifest(path: Path, manifest: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )


def plan_ingest(
    vault: Path,
    *,
    manifest_path: Path,
    public_dir: str = "Public",
) -> IngestPlan:
    extraction = extract_public_notes(vault, public_dir=public_dir)
    current = extraction.manifest
    previous = load_manifest(manifest_path)

    added = tuple(sorted(set(current) - set(previous)))
    removed = tuple(sorted(set(previous) - set(current)))
    updated = tuple(
        sorted(path for path in current if path in previous and current[path] != previous[path])
    )
    unchanged = len(current) - len(added) - len(updated)
    return IngestPlan(
        current=current,
        added=added,
        updated=updated,
        removed=removed,
        unchanged=unchanged,
    )


async def run_ingest(
    vault: Path,
    *,
    embedder: Embedder,
    store: ChromaStore,
    manifest_path: Path,
    public_dir: str = "Public",
    dry_run: bool = False,
    rebuild: bool = False,
) -> IngestSummary:
    plan = plan_ingest(vault, manifest_path=manifest_path, public_dir=public_dir)

    if dry_run:
        return IngestSummary(
            added=len(plan.added),
            updated=len(plan.updated),
            removed=len(plan.removed),
            unchanged=plan.unchanged,
            chunks=0,
            rebuild=rebuild,
            dry_run=True,
        )

    if rebuild:
        extraction = extract_public_notes(vault, public_dir=public_dir)
        chunks = [chunk for note in extraction.notes for chunk in chunk_note(note)]
        replacement = store.start_replacement()
        await _embed_and_upsert(replacement, embedder, chunks)
        store.commit_replacement(replacement)
        save_manifest(manifest_path, plan.current)
        return IngestSummary(
            added=len(plan.added),
            updated=len(plan.updated),
            removed=len(plan.removed),
            unchanged=plan.unchanged,
            chunks=len(chunks),
            rebuild=True,
            dry_run=False,
        )

    extraction = extract_public_notes(vault, public_dir=public_dir)
    by_path = {note.relative_path: note for note in extraction.notes}

    total_chunks = 0
    for path in (*plan.added, *plan.updated):
        store.delete_source(path)
        chunks = chunk_note(by_path[path])
        await _embed_and_upsert(store, embedder, chunks)
        total_chunks += len(chunks)

    for path in plan.removed:
        store.delete_source(path)

    save_manifest(manifest_path, plan.current)
    return IngestSummary(
        added=len(plan.added),
        updated=len(plan.updated),
        removed=len(plan.removed),
        unchanged=plan.unchanged,
        chunks=total_chunks,
        rebuild=False,
        dry_run=False,
    )


async def _embed_and_upsert(store: ChromaStore, embedder: Embedder, chunks: list[Chunk]) -> None:
    if not chunks:
        return
    vectors = await embedder.embed([chunk.embedded_text for chunk in chunks])
    store.upsert(chunks, vectors)
