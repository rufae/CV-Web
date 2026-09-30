#!/usr/bin/env python3
"""CLI de ingesta del vault público (T3.2/T3.5). Solo lectura sobre el vault."""

import argparse
import asyncio
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Ingesta incremental del vault público en Chroma (ADR-0001; solo lectura)"
    )
    parser.add_argument("--vault", type=Path, default=None, help="Ruta del vault (o VAULT_PATH)")
    parser.add_argument(
        "--public-dir", default=None, help="Carpeta publicable (o PUBLIC_VAULT_DIR)"
    )
    parser.add_argument("--manifest", type=Path, default=None, help="Ruta del manifiesto JSON")
    parser.add_argument("--dry-run", action="store_true", help="Solo muestra qué cambiaría")
    parser.add_argument("--rebuild", action="store_true", help="Reconstruye todo con swap atómico")
    return parser


def main() -> None:
    from app.core.config import get_settings
    from app.rag.embeddings import OllamaEmbedder
    from app.rag.pipeline import plan_ingest, run_ingest
    from app.rag.store import ChromaStore, StoreConfigMismatch

    args = _build_parser().parse_args()
    settings = get_settings()
    vault = args.vault or (Path(settings.vault_path) if settings.vault_path else None)
    if vault is None:
        raise SystemExit("ERROR: indica --vault o configura VAULT_PATH")
    public_dir = args.public_dir or settings.public_vault_dir
    manifest = args.manifest or Path(settings.data_path) / "ingest_manifest.json"

    if args.dry_run:
        plan = plan_ingest(vault, manifest_path=manifest, public_dir=public_dir)
        for path in plan.added:
            print(f"  + {path}")
        for path in plan.updated:
            print(f"  ~ {path}")
        for path in plan.removed:
            print(f"  - {path}")
        print(
            f"Añadidas: {len(plan.added)} · actualizadas: {len(plan.updated)} · "
            f"borradas: {len(plan.removed)} · sin cambios: {plan.unchanged}"
        )
        return

    if not settings.embed_url:
        raise SystemExit("ERROR: configura EMBED_URL (servicio de embeddings en el Dell)")

    embedder = OllamaEmbedder(settings.embed_url, settings.embed_model)

    async def _run() -> int:
        try:
            store = ChromaStore(settings.chroma_path, embed_model=settings.embed_model)
        except StoreConfigMismatch as exc:
            print(f"ERROR: {exc}")
            return 2

        try:
            summary = await run_ingest(
                vault,
                embedder=embedder,
                store=store,
                manifest_path=manifest,
                public_dir=public_dir,
                rebuild=args.rebuild,
            )
        finally:
            await embedder.aclose()

        print(
            f"Añadidas: {summary.added} · actualizadas: {summary.updated} · "
            f"borradas: {summary.removed} · sin cambios: {summary.unchanged} · "
            f"chunks escritos: {summary.chunks}" + (" (rebuild)" if summary.rebuild else "")
        )
        return 0

    raise SystemExit(asyncio.run(_run()))


if __name__ == "__main__":
    main()
