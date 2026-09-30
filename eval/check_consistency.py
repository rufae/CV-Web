#!/usr/bin/env python3
"""Verifica que web (`facts.json`) y vault público cuentan lo mismo (T6.1)."""

import argparse
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

ROOT = BACKEND_DIR.parent


def main() -> None:
    from app.rag.facts import compare_facts, load_facts, missing_terms_in_corpus

    parser = argparse.ArgumentParser(description="Consistencia web ↔ vault (ADR-0004)")
    parser.add_argument("--vault", type=Path, default=ROOT / "eval/fixtures/vault")
    parser.add_argument(
        "--facts-json",
        type=Path,
        default=ROOT / "frontend/src/content/facts.json",
    )
    args = parser.parse_args()

    facts = load_facts(args.vault)
    problems = compare_facts(facts, args.facts_json)
    problems.extend(
        f"'{term}' no aparece en las notas públicas"
        for term in missing_terms_in_corpus(facts, args.vault)
    )

    if problems:
        for problem in problems:
            print(f"✗ {problem}")
        raise SystemExit(1)
    print("✓ Web y vault consistentes")


if __name__ == "__main__":
    main()
