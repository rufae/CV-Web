"""Exportación y verificación de `facts.json` desde el vault (T6.1, ADR-0004).

La nota canónica (`Public/portfolio/facts.md`) contiene en su frontmatter el
bloque `facts` que alimenta la web; su cuerpo alimenta al asistente (RAG). Así
web y chat comparten una única fuente de verdad.
"""

import json
from pathlib import Path
from typing import Any

import frontmatter

from app.rag.ingest import extract_public_notes

FACTS_NOTE = "Public/portfolio/facts.md"
CANARY_PREFIX = "CANARIO"
FORBIDDEN_TERMS = ("teléfono", "phone", "dni", "iban")


class FactsError(RuntimeError):
    pass


def load_facts(vault_path: Path, *, facts_note: str = FACTS_NOTE) -> dict[str, Any]:
    path = vault_path / facts_note
    if not path.is_file():
        raise FactsError(f"No existe la nota canónica de facts: {facts_note}")
    post = frontmatter.loads(path.read_text(encoding="utf-8"))
    if post.metadata.get("cv_public") is not True:
        raise FactsError("La nota de facts debe tener cv_public: true")
    facts = post.metadata.get("facts")
    if not isinstance(facts, dict):
        raise FactsError("La nota de facts no tiene el bloque `facts` en el frontmatter")
    return dict(facts)


def render_facts_json(facts: dict[str, Any], *, generated_at: str) -> str:
    payload: dict[str, Any] = {"generated_at": generated_at, **facts}
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def compare_facts(expected: dict[str, Any], facts_json_path: Path) -> list[str]:
    """Problemas de consistencia entre el vault y el `facts.json` de la web."""
    problems: list[str] = []
    if not facts_json_path.is_file():
        return [f"No existe {facts_json_path}; ejecuta scripts/build_facts.py"]

    actual = json.loads(facts_json_path.read_text(encoding="utf-8"))
    actual.pop("generated_at", None)
    if actual != expected:
        problems.append(
            "facts.json está desactualizado respecto al vault (regenera con build_facts.py)"
        )

    serialized = json.dumps(expected, ensure_ascii=False).lower()
    if CANARY_PREFIX.lower() in serialized:
        problems.append("facts contiene un canario de fuga")
    for term in FORBIDDEN_TERMS:
        if term in serialized:
            problems.append(f"facts contiene el término sensible '{term}'")
    return problems


def facts_terms(facts: dict[str, Any]) -> set[str]:
    terms: set[str] = set()
    for experience in facts.get("experience", []):
        if isinstance(experience, dict):
            if "company" in experience:
                terms.add(str(experience["company"]))
            for technology in experience.get("technologies", []):
                terms.add(str(technology))
    for project in facts.get("projects", []):
        if isinstance(project, dict):
            if "name" in project:
                terms.add(str(project["name"]))
            for technology in project.get("technologies", []):
                terms.add(str(technology))
    return terms


def missing_terms_in_corpus(facts: dict[str, Any], vault_path: Path) -> list[str]:
    """Términos de facts que no aparecen en el corpus público indexable."""
    extraction = extract_public_notes(vault_path)
    corpus = "\n".join(note.content for note in extraction.notes).lower()
    return sorted(term for term in facts_terms(facts) if term.lower() not in corpus)
