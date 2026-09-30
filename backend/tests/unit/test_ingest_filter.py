"""Tests de extracción/filtrado del vault público (T3.2)."""

import hashlib
from pathlib import Path

from app.rag.ingest import IngestResult, extract_public_notes

VAULT = Path(__file__).resolve().parents[1] / "fixtures" / "vault"

CANARIOS_PRIVADOS = (
    "CANARIO_SIN_CV_PUBLIC",
    "CANARIO_PRIVADO_EN_DENYLIST",
    "CANARIO_DIARIO",
    "CANARIO_NO_MD",
    "CANARIO_COMENTARIO",
)

EXPECTED_PATHS = {
    "Public/experiencia/aeptik.md",
    "Public/proyectos/cvweb.md",
    "Public/sobre-mi/bio.md",
}


def _extract() -> IngestResult:
    return extract_public_notes(VAULT)


def _all_text(result: IngestResult) -> str:
    return "\n".join(note.content for note in result.notes)


def _note(result: IngestResult, suffix: str) -> str:
    return next(note.content for note in result.notes if note.relative_path.endswith(suffix))


def test_only_notes_inside_public_with_flag_are_extracted() -> None:
    result = _extract()
    assert {note.relative_path for note in result.notes} == EXPECTED_PATHS


def test_private_canaries_never_leak() -> None:
    text = _all_text(_extract())
    for canary in CANARIOS_PRIVADOS:
        assert canary not in text


def test_public_contents_are_present() -> None:
    text = _all_text(_extract())
    assert "CANARIO_PUBLICO_BIO" in text
    assert "CANARIO_PUBLICO_EXPERIENCIA" in text
    assert "CANARIO_PUBLICO_PROYECTO" in text


def test_sensitive_patterns_are_redacted() -> None:
    bio = _note(_extract(), "bio.md")

    assert "rafael@example.com" not in bio
    assert "[email redactado]" in bio
    assert "+34 600 11 22 33" not in bio
    assert "[teléfono redactado]" in bio
    assert "12345678Z" not in bio
    assert "[DNI/NIE redactado]" in bio
    assert "ES12 3456 7890 1234 5678 9012" not in bio
    assert "[IBAN redactado]" in bio
    assert "01/01/1990" not in bio
    assert "[fecha de nacimiento redactada]" in bio


def test_obsidian_syntax_is_cleaned() -> None:
    text = _all_text(_extract())

    assert "[[" not in text
    assert "![[" not in text
    assert "%%" not in text
    assert "[!note]" not in text
    assert "mi portfolio" in text
    assert "Diario/2026-01-01" not in text
    assert "privado.png" not in text


def test_manifest_is_deterministic_and_matches_notes() -> None:
    first = _extract()
    second = _extract()

    assert first.manifest == second.manifest
    assert set(first.manifest) == EXPECTED_PATHS
    for note in first.notes:
        assert first.manifest[note.relative_path] == note.content_hash


def test_vault_is_read_only() -> None:
    before = _hash_tree(VAULT)
    _extract()
    after = _hash_tree(VAULT)

    assert before == after


def _hash_tree(root: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            hashes[path.relative_to(root).as_posix()] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
    return hashes
