#!/usr/bin/env python3
"""Evaluación de recuperación y rechazo del RAG (T3.7).

Por defecto usa `eval/fixtures/embeddings.npz` (determinista, sin red).
`--live` recalcula los embeddings contra `EMBED_URL`; `--calibrate` explora un
rango de umbrales y elige el mejor que cumpla los gates.
"""

import argparse
import asyncio
import json
import sys
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import cast

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

CANARY_PRIVATE = "CANARIO_EVAL_NO_PUBLICADA"
GATES = {"recall_at_k": 0.9, "refusal_recall": 0.95, "leaks": 0}
# Solo el fuera de dominio se rechaza por umbral de recuperación. Las de
# `in_domain_no_data` (p. ej. sueldo) y las inyecciones las gestionan el prompt
# (T4.4), la sanitización de entrada (T4.3) y el output guard (T4.6).
REFUSAL_CATEGORIES = {"out_of_domain"}


@dataclass(frozen=True)
class EvalMetrics:
    recall_at_k: float
    mrr: float
    hit_rate: float
    refusal_recall: float
    refusal_precision: float
    leaks: int
    answerable: int
    refusal_cases: int
    injection_cases: int
    injection_refused: int


def _cosine_scores(query: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    query_norm = query / (float(np.linalg.norm(query)) + 1e-12)
    matrix_norm = matrix / (np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-12)
    return np.asarray(matrix_norm @ query_norm)


def _rank_sources(
    query_vector: np.ndarray,
    chunk_matrix: np.ndarray,
    source_ids: list[str],
    *,
    top_k: int,
) -> list[str]:
    """Top-k fuentes por similitud (sin umbral; mide el ranking del retriever)."""
    scores = _cosine_scores(query_vector, chunk_matrix)
    order = np.argsort(-scores)
    sources: list[str] = []
    seen: set[str] = set()
    for index in order:
        source = source_ids[int(index)]
        if source in seen:
            continue
        seen.add(source)
        sources.append(source)
        if len(sources) >= top_k:
            break
    return sources


def _best_score(query_vector: np.ndarray, chunk_matrix: np.ndarray) -> float:
    scores = np.asarray(_cosine_scores(query_vector, chunk_matrix))
    return float(np.max(scores)) if scores.size else 0.0


def evaluate(
    cases: list[dict[str, object]],
    query_vectors: Mapping[str, np.ndarray],
    chunk_matrix: np.ndarray,
    source_ids: list[str],
    chunk_texts: list[str],
    *,
    top_k: int,
    min_score: float,
) -> EvalMetrics:
    recall_sum = 0.0
    answerable = 0
    hits = 0
    rr_sum = 0.0

    refusal_cases = 0
    refused_correct = 0
    predicted_refusals = 0
    true_refusals = 0
    injection_cases = 0
    injection_refused = 0

    for case in cases:
        case_id = str(case["id"])
        category = str(case["category"])
        query_vector = query_vectors[case_id]
        sources = _rank_sources(
            query_vector,
            chunk_matrix,
            source_ids,
            top_k=top_k,
        )
        refused = _best_score(query_vector, chunk_matrix) < min_score
        if refused:
            predicted_refusals += 1

        if category == "answerable":
            raw_expected = cast(list[object], case.get("expected_sources") or [])
            expected = [str(item) for item in raw_expected]
            answerable += 1
            found = [source for source in expected if source in sources]
            recall_sum += len(found) / len(expected)
            if found:
                hits += 1
                rank = min(sources.index(source) for source in found) + 1
                rr_sum += 1.0 / rank
        elif category in REFUSAL_CATEGORIES:
            refusal_cases += 1
            if refused:
                refused_correct += 1
                true_refusals += 1
        elif category == "injection":
            injection_cases += 1
            if refused:
                injection_refused += 1

    leaks = sum(1 for text in chunk_texts if CANARY_PRIVATE in text)
    return EvalMetrics(
        recall_at_k=recall_sum / answerable if answerable else 0.0,
        mrr=rr_sum / answerable if answerable else 0.0,
        hit_rate=hits / answerable if answerable else 0.0,
        refusal_recall=refused_correct / refusal_cases if refusal_cases else 0.0,
        refusal_precision=(true_refusals / predicted_refusals) if predicted_refusals else 1.0,
        leaks=leaks,
        answerable=answerable,
        refusal_cases=refusal_cases,
        injection_cases=injection_cases,
        injection_refused=injection_refused,
    )


def gates_passed(metrics: EvalMetrics) -> bool:
    return (
        metrics.recall_at_k >= GATES["recall_at_k"]
        and metrics.refusal_recall >= GATES["refusal_recall"]
        and metrics.leaks <= GATES["leaks"]
    )


def _load_cases(path: Path) -> list[dict[str, object]]:
    cases: list[dict[str, object]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            cases.append(json.loads(line))
    return cases


def _load_fixtures(
    path: Path,
) -> tuple[str, str, dict[str, np.ndarray], dict[str, np.ndarray]]:
    data = np.load(path, allow_pickle=False)
    model = str(data["embed_model"].item())
    context_prefix = str(data["context_prefix"].item())
    chunk_vectors = {
        str(chunk_id): vector
        for chunk_id, vector in zip(data["chunk_ids"], data["chunk_vectors"], strict=True)
    }
    query_vectors = {
        str(query_id): vector
        for query_id, vector in zip(data["query_ids"], data["query_vectors"], strict=True)
    }
    return model, context_prefix, chunk_vectors, query_vectors


async def _live_vectors(
    chunk_texts: list[str],
    questions: list[str],
    *,
    embed_url: str,
    model: str,
) -> tuple[list[list[float]], list[list[float]]]:
    from app.rag.embeddings import OllamaEmbedder

    embedder = OllamaEmbedder(embed_url, model)
    try:
        return (
            await embedder.embed(chunk_texts),
            await embedder.embed(questions),
        )
    finally:
        await embedder.aclose()


def _print_metrics(label: str, metrics: EvalMetrics) -> None:
    print(
        f"{label}: recall@k={metrics.recall_at_k:.3f} mrr={metrics.mrr:.3f} "
        f"hit_rate={metrics.hit_rate:.3f} refusal_recall={metrics.refusal_recall:.3f} "
        f"refusal_precision={metrics.refusal_precision:.3f} "
        f"inyecciones_rechazadas={metrics.injection_refused}/{metrics.injection_cases} "
        f"leaks={metrics.leaks}"
    )


def main() -> None:
    from app.core.config import get_settings
    from app.rag.chunking import chunk_note, embedding_text
    from app.rag.ingest import extract_public_notes

    parser = argparse.ArgumentParser(description="Evaluación del RAG (T3.7)")
    parser.add_argument("--dataset", type=Path, default=ROOT / "eval/dataset.jsonl")
    parser.add_argument("--vault", type=Path, default=ROOT / "eval/fixtures/vault")
    parser.add_argument("--fixtures", type=Path, default=ROOT / "eval/fixtures/embeddings.npz")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--min-score", type=float, default=None)
    parser.add_argument("--calibrate", action="store_true")
    parser.add_argument(
        "--retrieval-only",
        action="store_true",
        help="Solo métricas de recuperación y rechazo (comportamiento por defecto)",
    )
    parser.add_argument("--live", action="store_true", help="Calcula embeddings en vivo")
    parser.add_argument("--embed-url", default=None)
    parser.add_argument("--context-prefix", default=None, help="Por defecto RAG_CONTEXT_PREFIX")
    parser.add_argument("--report", type=Path, default=None)
    args = parser.parse_args()

    settings = get_settings()
    cases = _load_cases(args.dataset)
    extraction = extract_public_notes(args.vault)
    chunks = [chunk for note in extraction.notes for chunk in chunk_note(note)]
    source_ids = [chunk.source_id for chunk in chunks]
    questions = [str(case["question"]) for case in cases]
    expected_prefix = (
        args.context_prefix if args.context_prefix is not None else settings.rag_context_prefix
    )

    chunk_vectors: Mapping[str, np.ndarray]
    query_vectors: Mapping[str, np.ndarray]

    if args.live:
        embed_url = args.embed_url or settings.embed_url
        if not embed_url:
            raise SystemExit("ERROR: configura EMBED_URL o pasa --embed-url")
        model = settings.embed_model
        context_prefix = expected_prefix
        live_texts = [embedding_text(chunk, corpus_prefix=context_prefix) for chunk in chunks]
        chunk_vectors_list, query_vectors_list = asyncio.run(
            _live_vectors(live_texts, questions, embed_url=embed_url, model=model)
        )
        chunk_vectors = {
            chunk.id: np.asarray(vector, dtype=np.float64)
            for chunk, vector in zip(chunks, chunk_vectors_list, strict=True)
        }
        query_vectors = {
            str(case["id"]): np.asarray(vector, dtype=np.float64)
            for case, vector in zip(cases, query_vectors_list, strict=True)
        }
    else:
        if not args.fixtures.is_file():
            raise SystemExit(
                f"ERROR: no existe {args.fixtures}; genera fixtures con "
                "scripts/build_eval_fixtures.py o usa --live"
            )
        model, context_prefix, fixture_chunks, query_vectors = _load_fixtures(args.fixtures)
        if context_prefix != expected_prefix:
            raise SystemExit(
                f"ERROR: las fixtures usan prefijo {context_prefix!r} y la configuración "
                f"actual {expected_prefix!r}; regenera scripts/build_eval_fixtures.py"
            )
        expected_ids = {chunk.id for chunk in chunks}
        if set(fixture_chunks) != expected_ids:
            raise SystemExit(
                "ERROR: las fixtures no coinciden con el vault actual "
                "(regenera scripts/build_eval_fixtures.py)"
            )
        chunk_vectors = fixture_chunks

    chunk_texts = [embedding_text(chunk, corpus_prefix=context_prefix) for chunk in chunks]
    chunk_matrix = np.array([chunk_vectors[chunk.id] for chunk in chunks], dtype=np.float64)

    calibration: list[tuple[float, EvalMetrics]] = []
    if args.calibrate:
        for candidate in np.arange(0.30, 0.71, 0.05):
            min_score = round(float(candidate), 2)
            metrics = evaluate(
                cases,
                query_vectors,
                chunk_matrix,
                source_ids,
                chunk_texts,
                top_k=args.top_k,
                min_score=min_score,
            )
            calibration.append((min_score, metrics))
            _print_metrics(f"min_score={min_score:.2f}", metrics)
        passing = [(score, metrics) for score, metrics in calibration if gates_passed(metrics)]
        if not passing:
            print("ERROR: ningún umbral cumple los gates")
            raise SystemExit(1)
        # El umbral más bajo que cumple los gates: maximiza la cobertura.
        chosen, final_metrics = min(passing, key=lambda row: row[0])
    else:
        chosen = args.min_score if args.min_score is not None else settings.rag_min_score
        final_metrics = evaluate(
            cases,
            query_vectors,
            chunk_matrix,
            source_ids,
            chunk_texts,
            top_k=args.top_k,
            min_score=chosen,
        )
        _print_metrics(f"min_score={chosen:.2f}", final_metrics)

    passed = gates_passed(final_metrics)
    print(f"Gates: {GATES} -> {'PASS' if passed else 'FAIL'}")

    if args.report is not None:
        report = {
            "date": date.today().isoformat(),
            "embed_model": model,
            "top_k": args.top_k,
            "min_score": chosen,
            "gates": GATES,
            "passed": passed,
            "cases": len(cases),
            "metrics": asdict(final_metrics),
            "calibration": [
                {"min_score": score, **asdict(metrics)} for score, metrics in calibration
            ],
        }
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Informe escrito en {args.report}")

    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
