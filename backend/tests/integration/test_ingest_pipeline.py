"""Tests de la ingesta incremental e idempotente (T3.5)."""

import shutil
from pathlib import Path

from app.rag.pipeline import plan_ingest, run_ingest
from app.rag.store import ChromaStore

FIXTURE_VAULT = Path(__file__).resolve().parents[1] / "fixtures" / "vault"


class FakeEmbedder:
    def __init__(self) -> None:
        self.calls: list[list[str]] = []

    async def embed(self, texts: list[str]) -> list[list[float]]:
        self.calls.append(list(texts))
        return [
            [float(len(text) % 7), float(sum(ord(char) for char in text) % 13), 1.0]
            for text in texts
        ]

    async def aclose(self) -> None:
        return


def _setup(tmp_path: Path) -> tuple[Path, ChromaStore, FakeEmbedder, Path]:
    vault = tmp_path / "vault"
    shutil.copytree(FIXTURE_VAULT, vault)
    store = ChromaStore(tmp_path / "chroma", embed_model="fake-model", collection_name="cvweb_test")
    manifest = tmp_path / "ingest_manifest.json"
    return vault, store, FakeEmbedder(), manifest


async def test_initial_ingest_then_idempotent_rerun(tmp_path: Path) -> None:
    vault, store, embedder, manifest = _setup(tmp_path)

    first = await run_ingest(vault, embedder=embedder, store=store, manifest_path=manifest)

    assert first.added == 3
    assert first.chunks > 0
    assert store.count() == first.chunks
    saved = manifest.read_text(encoding="utf-8")

    second = await run_ingest(vault, embedder=embedder, store=store, manifest_path=manifest)

    assert (second.added, second.updated, second.removed, second.chunks) == (0, 0, 0, 0)
    assert store.count() == first.chunks
    assert manifest.read_text(encoding="utf-8") == saved


async def test_unpublishing_a_note_removes_its_chunks(tmp_path: Path) -> None:
    vault, store, embedder, manifest = _setup(tmp_path)
    await run_ingest(vault, embedder=embedder, store=store, manifest_path=manifest)
    before = store.count()

    note = vault / "Public/experiencia/aeptik.md"
    note.write_text(
        note.read_text(encoding="utf-8").replace("cv_public: true", "cv_public: false"),
        encoding="utf-8",
    )

    summary = await run_ingest(vault, embedder=embedder, store=store, manifest_path=manifest)

    assert summary.removed == 1
    assert store.count() < before
    hits = store.query([1.0, 1.0, 1.0], top_k=10)
    assert all(hit.metadata["source_id"] != "Public/experiencia/aeptik.md" for hit in hits)


async def test_modified_note_is_reindexed(tmp_path: Path) -> None:
    vault, store, embedder, manifest = _setup(tmp_path)
    await run_ingest(vault, embedder=embedder, store=store, manifest_path=manifest)

    note = vault / "Public/proyectos/cvweb.md"
    note.write_text(
        note.read_text(encoding="utf-8") + "\n\n## Nueva sección\n\nContenido nuevo.\n",
        encoding="utf-8",
    )

    summary = await run_ingest(vault, embedder=embedder, store=store, manifest_path=manifest)

    assert summary.updated == 1
    assert summary.chunks > 0
    assert plan_ingest(vault, manifest_path=manifest).unchanged == 3


async def test_dry_run_makes_no_changes(tmp_path: Path) -> None:
    vault, store, embedder, manifest = _setup(tmp_path)
    manifest_existed = manifest.exists()

    summary = await run_ingest(
        vault, embedder=embedder, store=store, manifest_path=manifest, dry_run=True
    )

    assert summary.dry_run
    assert summary.added == 3
    assert store.count() == 0
    assert manifest.exists() == manifest_existed


async def test_rebuild_swaps_atomically(tmp_path: Path) -> None:
    vault, store, embedder, manifest = _setup(tmp_path)
    first = await run_ingest(vault, embedder=embedder, store=store, manifest_path=manifest)

    summary = await run_ingest(
        vault, embedder=embedder, store=store, manifest_path=manifest, rebuild=True
    )

    assert summary.rebuild
    assert summary.chunks == first.chunks
    assert store.count() == first.chunks
    assert plan_ingest(vault, manifest_path=manifest).unchanged == 3
