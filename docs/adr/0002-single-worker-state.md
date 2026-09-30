# ADR-0002 — Estado en memoria: un solo worker

- **Estado:** aceptada (2026-09-30, T4.2)
- **Contexto:** el rate limiting, el presupuesto diario de chat, la salud de
  proveedores (T2.3) y el semáforo del router (T2.4) viven en memoria del
  proceso. Con varios workers, cada uno tendría su propio estado y los límites
  no serían globales.
- **Decisión:** uvicorn corre con `--workers 1` (ya presente en
  `deploy/cvweb.service`). El nodo HP es pequeño y la carga esperada no
  requiere paralelismo de proceso; la concurrencia se gestiona con `asyncio` y
  el semáforo `LLM_MAX_CONCURRENCY`.
- **Consecuencias:**
  - Un reinicio del servicio resetea contadores y presupuesto (aceptable).
  - Si en el futuro se escala a varios workers, habrá que migrar el estado a
    Redis (rate limits, presupuesto y salud) antes de subir el número de
    workers.
  - El cuerpo máximo (`MAX_BODY_BYTES`) y el rate limit protegen también el
    consumo de la torre/Dell.
