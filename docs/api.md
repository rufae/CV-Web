# API de CV Web

> Contrato manual (en producción `/docs` y `/openapi.json` están desactivados).

## `GET /api/health`

Liveness. Respuesta: `{"status": "ok"}`.

## `GET /api/status`

Estado público y saneado: `{"llm": "online" | "degraded" | "offline", "tier": "gpu" | "cpu"}`.
No expone hosts, IPs ni nombres de proveedores.

## `POST /api/chat` (SSE, `text/event-stream`)

Request:

```json
{
  "message": "¿Qué tecnologías usas?",
  "history": [
    {"role": "user", "content": "¿Quién eres?"},
    {"role": "assistant", "content": "Soy el asistente de Rafael..."}
  ],
  "lang": "es"
}
```

Límites: `message` entre 1 y 500 caracteres; `history` máximo 12 turnos;
`extra="forbid"` (campos desconocidos o rol `system` → 422).

Eventos (en orden):

```text
event: meta
data: {"message_id":"a1b2c3","prompt_version":"v1","tier":"gpu"}

event: sources
data: {"sources":[{"n":1,"title":"Experiencia","section":"AePTIC"}]}

event: token
data: {"t":"Rafael "}

event: refusal
data: {"reason":"no_context","message":"No dispongo de esa información…"}

event: done
data: {"first_token_ms":420,"total_ms":3100}

event: error
data: {"code":"provider_unavailable","message":"El asistente no está disponible ahora mismo.","retry_after_s":30}
```

Códigos estables de `error`: `rate_limited`, `daily_budget_exhausted`,
`provider_unavailable`, `first_token_timeout`, `output_blocked`, `internal`.

Errores previos al stream usan HTTP normal: 413 (cuerpo demasiado grande),
422 (validación), 429 (límite, con `Retry-After`), 503 (cola desbordada, con
`Retry-After`). `tier` es `gpu` o `cpu`; nunca se expone host ni IP.

El alias legacy `POST /ask` mantiene el formato JSON `{"response": "..."}` hasta T5.7.

## `POST /api/contact`

Request: `{"name": "...", "email": "....", "message": "..."}` (longitudes y
`extra="forbid"`; sin `\r`/`\n` en nombre/email). Respuesta:
`{"status": "Mensaje enviado correctamente"}`. Errores siempre genéricos.

## `POST /api/feedback`

Request: `{"message_id": "...", "rating": "up" | "down", "comment": "..."}`.
Guarda solo metadatos anónimos (sin pregunta ni IP).
