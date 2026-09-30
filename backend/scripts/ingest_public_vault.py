#!/usr/bin/env python3
"""CLI de extracción del vault público (T3.2). Solo lectura sobre el vault."""

import argparse
import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def main() -> None:
    from app.core.config import get_settings
    from app.rag.ingest import extract_public_notes

    parser = argparse.ArgumentParser(
        description="Extrae las notas públicas del vault (aplica ADR-0001; solo lectura)"
    )
    parser.add_argument("--vault", type=Path, default=None, help="Ruta del vault (o VAULT_PATH)")
    parser.add_argument(
        "--public-dir", default=None, help="Carpeta publicable (o PUBLIC_VAULT_DIR)"
    )
    parser.add_argument("--manifest", type=Path, default=None, help="Ruta del manifiesto JSON")
    parser.add_argument("--dry-run", action="store_true", help="No escribe el manifiesto")
    args = parser.parse_args()

    settings = get_settings()
    vault = args.vault or (Path(settings.vault_path) if settings.vault_path else None)
    if vault is None:
        raise SystemExit("ERROR: indica --vault o configura VAULT_PATH")
    public_dir = args.public_dir or settings.public_vault_dir

    result = extract_public_notes(vault, public_dir=public_dir)
    for note in result.notes:
        print(f"  - {note.relative_path} ({note.redactions} redacciones)")
    print(f"Notas públicas: {len(result.notes)} · redacciones: {result.redactions}")

    if args.manifest is not None and not args.dry_run:
        args.manifest.write_text(
            json.dumps(result.manifest, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"Manifiesto escrito en {args.manifest}")


if __name__ == "__main__":
    main()
