#!/usr/bin/env python3
"""Genera `frontend/src/content/facts.json` desde el vault público (T6.1)."""

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

ROOT = BACKEND_DIR.parent


def main() -> None:
    from app.core.config import get_settings
    from app.rag.facts import FACTS_NOTE, load_facts, render_facts_json

    parser = argparse.ArgumentParser(description="Exporta facts.json desde el vault público")
    parser.add_argument("--vault", type=Path, default=None, help="Ruta del vault (o VAULT_PATH)")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "frontend/src/content/facts.json",
        help="Ruta de salida del JSON",
    )
    parser.add_argument("--facts-note", default=FACTS_NOTE)
    args = parser.parse_args()

    settings = get_settings()
    vault = args.vault or (Path(settings.vault_path) if settings.vault_path else None)
    if vault is None:
        raise SystemExit("ERROR: configura VAULT_PATH o pasa --vault")

    facts = load_facts(vault, facts_note=args.facts_note)
    generated_at = datetime.now(UTC).isoformat(timespec="seconds")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_facts_json(facts, generated_at=generated_at), encoding="utf-8")
    print(f"facts.json escrito en {args.output} ({generated_at})")


if __name__ == "__main__":
    main()
