#!/usr/bin/env python3
"""Genera las fixtures de embeddings para la evaluación (T3.7).

Llama al servicio de embeddings (bge-m3 en el Dell) una sola vez y guarda los
vectores de los chunks del vault de evaluación y de las preguntas del dataset
en un `.npz` comprimido. Así `eval/run_eval.py --retrieval-only` es
determinista y ejecutable sin red (CI).
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def _load_cases(path: Path) -> list[dict[str, object]]:
    cases: list[dict[str, object]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            cases.append(json.loads(line))
    return cases


def main() -> None:
    from app.core.config import get_settings
    from app.rag.chunking import chunk_note, embedding_text
    from app.rag.embeddings import OllamaEmbedder
    from app.rag.ingest import extract_public_notes

    parser = argparse.ArgumentParser(description="Genera eval/fixtures/embeddings.npz")
    parser.add_argument("--vault", type=Path, default=ROOT / "eval/fixtures/vault")
    parser.add_argument("--dataset", type=Path, default=ROOT / "eval/dataset.jsonl")
    parser.add_argument("--output", type=Path, default=ROOT / "eval/fixtures/embeddings.npz")
    parser.add_argument("--embed-url", default=None, help="Por defecto EMBED_URL")
    parser.add_argument("--model", default=None, help="Por defecto EMBED_MODEL")
    parser.add_argument("--context-prefix", default=None, help="Por defecto RAG_CONTEXT_PREFIX")
    args = parser.parse_args()

    settings = get_settings()
    embed_url = args.embed_url or settings.embed_url
    model = args.model or settings.embed_model
    context_prefix = (
        args.context_prefix if args.context_prefix is not None else settings.rag_context_prefix
    )
    if not embed_url:
        raise SystemExit("ERROR: configura EMBED_URL o pasa --embed-url")

    extraction = extract_public_notes(args.vault)
    chunks = [chunk for note in extraction.notes for chunk in chunk_note(note)]
    cases = _load_cases(args.dataset)

    async def _embed_all() -> tuple[list[list[float]], list[list[float]]]:
        embedder = OllamaEmbedder(embed_url, model)
        try:
            chunk_vectors = await embedder.embed(
                [embedding_text(chunk, corpus_prefix=context_prefix) for chunk in chunks]
            )
            query_vectors = await embedder.embed([str(case["question"]) for case in cases])
        finally:
            await embedder.aclose()
        return chunk_vectors, query_vectors

    chunk_vectors, query_vectors = asyncio.run(_embed_all())

    args.output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        args.output,
        embed_model=np.array(model),
        context_prefix=np.array(context_prefix),
        chunk_ids=np.array([chunk.id for chunk in chunks]),
        chunk_vectors=np.array(chunk_vectors, dtype=np.float32),
        query_ids=np.array([str(case["id"]) for case in cases]),
        query_vectors=np.array(query_vectors, dtype=np.float32),
    )
    print(
        f"Fixtures escritas en {args.output}: {len(chunks)} chunks, "
        f"{len(cases)} consultas ({model})"
    )


if __name__ == "__main__":
    main()
