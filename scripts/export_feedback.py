#!/usr/bin/env python3
"""Exporta los 👎 del feedback a JSONL para revisión manual (T4.9)."""

import argparse
import dataclasses
import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def main() -> None:
    from app.core.config import get_settings
    from app.features.feedback.store import FeedbackStore

    parser = argparse.ArgumentParser(description="Exporta feedback negativo (JSONL)")
    parser.add_argument("--db", type=Path, default=None, help="Ruta de feedback.db")
    parser.add_argument("--output", type=Path, default=None, help="Fichero de salida")
    args = parser.parse_args()

    settings = get_settings()
    db_path = args.db or Path(settings.data_path) / "feedback.db"
    if not db_path.is_file():
        raise SystemExit(f"ERROR: no existe {db_path}")

    entries = FeedbackStore(db_path).downs()
    lines = [
        json.dumps(dataclasses.asdict(entry), ensure_ascii=False) for entry in entries
    ]
    text = "\n".join(lines)

    if args.output is not None:
        args.output.write_text(text, encoding="utf-8")
        print(f"{len(entries)} valoraciones negativas escritas en {args.output}")
    else:
        print(text)


if __name__ == "__main__":
    main()
