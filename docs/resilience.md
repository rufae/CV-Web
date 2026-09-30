# Resiliencia — escenarios de caos (T7.8)

> La ejecución en el nodo real (apagar la torre en pleno stream, cortar
> Tailscale, reiniciar el HP…) queda pendiente del despliegue; aquí se
> documentan los comportamientos esperados y la evidencia automatizada.

| Escenario | Comportamiento esperado | Evidencia |
|---|---|---|
| Torre apagada antes de la petición | El monitor la marca DOWN y el router usa el Dell sin pagar timeouts (circuit breaker) | `test_health.py`, `test_router.py` |
| Torre lenta (sin primer token en 15 s) | Failover al Dell **antes** del primer token | `test_chaos.py::test_slow_tower_fails_over…`, `test_router.py` |
| Ambas caídas | Error controlado 503/evento SSE, nunca una traza | `test_chaos.py::test_both_providers_down…` |
| Corte a mitad de stream | El error se propaga como evento `error`; **no** se mezclan respuestas de dos modelos | `test_chaos.py::test_mid_stream_crash…` |
| Timeout de primer token con un solo proveedor | `FirstTokenTimeout` controlado | `test_chaos.py::test_timeout_before_first_token…` |
| Torre se enciende de nuevo | Recuperación UP→DEGRADED→UP sin reiniciar (histéresis) | `test_health.py` |
| SMTP caído | Mensaje a outbox con backoff; visitante recibe confirmación genérica | `test_contact.py` |
| Chroma con otro `EMBED_MODEL` | Error explícito (reindexar), nunca resultados basura | `test_store.py` |
| Ollama/embeddings caídos en la consulta | 503 controlado antes del stream | `test_chat_sse.py` (sin retriever) |
| Disco lleno / reinicio del HP | Pendiente de medir en el nodo | — |
| Corte de Tailscale | Equivalente a “proveedor caído”: failover/errores controlados | pendiente de medir |

Tiempos de detección y recuperación medidos: pendientes (game day en el nodo).
