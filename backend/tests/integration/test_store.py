"""Tests del almacén Chroma (T3.4, integración local con `tmp_path`)."""

from pathlib import Path

import pytest

from app.rag.chunking import Chunk
from app.rag.store import ChromaStore, StoreConfigMismatch


def _chunk(chunk_id: str, text: str) -> Chunk:
    return Chunk(
        id=chunk_id,
        source_id="Public/nota.md",
        title="Nota",
        section="Sección",
        tags=("test",),
        lang="es",
        updated="2026-09-01",
        context="Nota › Sección",
        text=text,
    )


def _store(path: Path, *, model: str = "bge-m3", read_only: bool = False) -> ChromaStore:
    return ChromaStore(path, embed_model=model, read_only=read_only)


def test_upsert_query_and_metadata(tmp_path: Path) -> None:
    store = _store(tmp_path)
    chunks = [_chunk("a", "texto a"), _chunk("b", "texto b"), _chunk("c", "texto c")]
    store.upsert(chunks, [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.9, 0.1, 0.0]])

    hits = store.query([1.0, 0.0, 0.0], top_k=2)

    assert store.count() == 3
    assert hits[0].id == "a"
    assert hits[0].score >= hits[1].score
    assert hits[0].metadata["title"] == "Nota"
    assert hits[0].metadata["source_id"] == "Public/nota.md"
    assert "Nota › Sección" in hits[0].text


def test_persistence_across_instances(tmp_path: Path) -> None:
    _store(tmp_path).upsert([_chunk("a", "texto")], [[1.0, 0.0]])

    reopened = _store(tmp_path)

    assert reopened.count() == 1
    assert reopened.query([1.0, 0.0], top_k=1)[0].id == "a"


def test_model_mismatch_raises_explicit_error(tmp_path: Path) -> None:
    _store(tmp_path, model="bge-m3").upsert([_chunk("a", "texto")], [[1.0, 0.0]])

    with pytest.raises(StoreConfigMismatch, match="Reindexa"):
        _store(tmp_path, model="otro-modelo")


def test_read_only_store_rejects_writes(tmp_path: Path) -> None:
    _store(tmp_path).upsert([_chunk("a", "texto")], [[1.0, 0.0]])
    read_only = _store(tmp_path, read_only=True)

    with pytest.raises(PermissionError):
        read_only.upsert([_chunk("b", "más")], [[0.0, 1.0]])
    assert read_only.query([1.0, 0.0], top_k=1)[0].id == "a"


def test_delete_source_and_reset(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.upsert([_chunk("a", "texto")], [[1.0, 0.0]])
    store.delete_source("Public/nota.md")
    assert store.count() == 0

    store.upsert([_chunk("a", "texto")], [[1.0, 0.0]])
    store.reset()
    assert store.count() == 0
