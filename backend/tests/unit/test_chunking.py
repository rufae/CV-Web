"""Tests del chunking Markdown (T3.3)."""

from app.rag.chunking import MAX_TOKENS, chunk_note, estimate_tokens
from app.rag.ingest import PublicNote

LONG_PARAGRAPH = "palabra " * 400


def _note(content: str) -> PublicNote:
    return PublicNote(
        relative_path="Public/test/nota.md",
        title="Nota de prueba",
        tags=("test", "rag"),
        lang="es",
        updated="2026-09-01",
        content=content,
        redactions=0,
    )


def _sample_note() -> PublicNote:
    return _note(
        "# Nota de prueba\n\n"
        "## Experiencia\n\n"
        f"{LONG_PARAGRAPH}\n\n"
        "### Backend\n\n"
        "Párrafo de backend.\n\n"
        "- item 1\n- item 2\n- item 3\n\n"
        "```python\n"
        "def hola():\n"
        "    print('mundo')\n\n"
        "    print('sigue')\n"
        "```\n\n"
        "## Otra sección\n\n"
        "Texto final.\n"
    )


def test_context_and_section_are_annotated() -> None:
    chunks = chunk_note(_sample_note())
    contexts = {chunk.context for chunk in chunks}

    assert "Nota de prueba › Experiencia" in contexts
    assert "Nota de prueba › Experiencia › Backend" in contexts
    assert any(chunk.section == "Experiencia › Backend" for chunk in chunks)


def test_no_chunk_exceeds_token_limit() -> None:
    chunks = chunk_note(_sample_note())

    assert chunks
    for chunk in chunks:
        assert estimate_tokens(chunk.text) <= MAX_TOKENS


def test_code_fence_is_never_cut() -> None:
    chunks = chunk_note(_sample_note())
    fence_chunks = [chunk for chunk in chunks if "```python" in chunk.text]

    assert len(fence_chunks) == 1
    fence = fence_chunks[0].text
    assert fence.count("```") == 2
    assert "print('sigue')" in fence


def test_list_is_not_split() -> None:
    chunks = chunk_note(_sample_note())
    list_chunks = [chunk for chunk in chunks if "item 1" in chunk.text]

    assert len(list_chunks) == 1
    assert "item 3" in list_chunks[0].text


def test_ids_are_deterministic_and_unique() -> None:
    first = chunk_note(_sample_note())
    second = chunk_note(_sample_note())

    assert [chunk.id for chunk in first] == [chunk.id for chunk in second]
    assert len({chunk.id for chunk in first}) == len(first)


def test_metadata_is_propagated() -> None:
    chunks = chunk_note(_sample_note())
    chunk = chunks[0]

    assert chunk.source_id == "Public/test/nota.md"
    assert chunk.tags == ("test", "rag")
    assert chunk.lang == "es"
    assert chunk.updated == "2026-09-01"
    assert chunk.embedded_text.startswith(chunk.context)


def test_consecutive_chunks_overlap() -> None:
    paragraphs = [f"bloque{index} " * 40 for index in range(1, 7)]
    note = _note("# N\n\n## S\n\n" + "\n\n".join(paragraphs) + "\n")

    chunks = chunk_note(note, max_tokens=200, overlap_tokens=80)

    assert len(chunks) >= 2
    first_units = chunks[0].text.split("\n\n")
    second_units = chunks[1].text.split("\n\n")
    assert first_units[-1] == second_units[0]


def test_empty_content_produces_no_chunks() -> None:
    assert chunk_note(_note("# Solo título\n\n## Sección vacía\n")) == []
