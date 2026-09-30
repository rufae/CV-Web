#!/usr/bin/env python3
"""Prueba de humo de carga contra `/api/chat` (T4.10).

Mide el tiempo al primer token de SSE con N usuarios concurrentes durante una
duración dada. Requiere una instancia real con LLM y presupuesto diario
suficiente.

Uso:
    python scripts/load_smoke.py --base-url http://127.0.0.1:8000 --users 50 --duration 60
"""

import argparse
import asyncio
import json
import statistics
import time
from typing import Any

import httpx

QUESTION = "¿Qué experiencia tiene Rafael con Python?"


async def _one_request(client: httpx.AsyncClient) -> float | None:
    started = time.perf_counter()
    async with client.stream("POST", "/api/chat", json={"message": QUESTION}) as response:
        if response.status_code != 200:
            return None
        async for line in response.aiter_lines():
            if line.startswith("data:") and '"t":' in line:
                return (time.perf_counter() - started) * 1000
    return None


async def _worker(
    base_url: str,
    deadline: float,
    results: list[float],
    errors: list[str],
) -> None:
    async with httpx.AsyncClient(base_url=base_url, timeout=60.0) as client:
        while time.monotonic() < deadline:
            value = await _one_request(client)
            if value is None:
                errors.append("sin_token")
            else:
                results.append(value)


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, round(percentile / 100 * (len(ordered) - 1)))
    return ordered[index]


def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke de carga de /api/chat")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--users", type=int, default=50)
    parser.add_argument("--duration", type=float, default=60.0)
    args = parser.parse_args()

    results: list[float] = []
    errors: list[str] = []

    async def _run() -> None:
        deadline = time.monotonic() + args.duration
        await asyncio.gather(
            *(_worker(args.base_url, deadline, results, errors) for _ in range(args.users))
        )

    asyncio.run(_run())

    summary: dict[str, Any] = {
        "base_url": args.base_url,
        "users": args.users,
        "duration_s": args.duration,
        "responses": len(results),
        "errors": len(errors),
        "first_token_ms": {
            "p50": round(statistics.median(results), 1) if results else 0.0,
            "p95": round(_percentile(results, 95), 1),
            "max": round(max(results), 1) if results else 0.0,
        },
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
