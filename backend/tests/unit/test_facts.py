"""Tests de la fuente única de contenido (T6.1)."""

from pathlib import Path

import pytest

from app.rag.facts import (
    FactsError,
    compare_facts,
    load_facts,
    missing_terms_in_corpus,
    render_facts_json,
)

VAULT = Path(__file__).resolve().parents[1] / "fixtures" / "facts_vault"


def test_load_facts_from_vault(tmp_path: Path) -> None:
    facts = load_facts(VAULT)

    assert facts["profile"]["name"] == "Rafael Castaño"
    assert facts["experience"][0]["company"] == "AePTIC"


def test_load_facts_requires_public_note(tmp_path: Path) -> None:
    with pytest.raises(FactsError):
        load_facts(tmp_path)


def test_compare_facts_equal_and_stale(tmp_path: Path) -> None:
    facts = load_facts(VAULT)
    facts_json = tmp_path / "facts.json"
    facts_json.write_text(
        render_facts_json(facts, generated_at="2026-09-30T00:00:00Z"), encoding="utf-8"
    )

    assert compare_facts(facts, facts_json) == []

    stale = dict(facts)
    stale["profile"] = {"name": "Otro"}
    problems = compare_facts(stale, facts_json)

    assert any("desactualizado" in problem for problem in problems)


def test_compare_facts_detects_canary_and_sensitive_terms(tmp_path: Path) -> None:
    facts = load_facts(VAULT)
    facts["profile"]["summary"] = "CANARIO_SECRETO y teléfono 600000000"
    facts_json = tmp_path / "facts.json"
    facts_json.write_text(render_facts_json(facts, generated_at="x"), encoding="utf-8")

    problems = compare_facts(facts, facts_json)

    assert any("canario" in problem for problem in problems)
    assert any("sensible" in problem for problem in problems)


def test_missing_terms_in_corpus() -> None:
    facts = load_facts(VAULT)
    assert missing_terms_in_corpus(facts, VAULT) == []

    facts["projects"].append({"name": "Kubernetes Cluster", "technologies": ["Kubernetes"]})
    assert "Kubernetes" in missing_terms_in_corpus(facts, VAULT)
