# Seguridad de CV Web

> Cierre de la Fase 4 (T4.10, hito M2). Capas de defensa, pruebas y límites.

## Capas de defensa

| Capa | Medida | Dónde |
|---|---|---|
| Datos | Solo se indexa `Public/` + `cv_public: true`; redacción de PII; canarios de fuga en tests | `app/rag/ingest.py`, ADR-0001 |
| Entrada | NFKC, fuera invisibles/control, delimitadores neutralizados, detector de inyección, bloqueo de extracción de prompt/datos | `app/features/chat/sanitize.py` |
| Prompt | Reglas de máxima prioridad, contexto escapado en `<fuente>`, token canario, recordatorio sándwich | `app/rag/prompts.py`, ADR-0003 |
| Recuperación | Umbral `RAG_MIN_SCORE`; si nada supera, rechazo **sin LLM** | `app/rag/retriever.py` |
| Salida | Búfer de retención: canario, n-gramas del prompt, PII fuera de allowlist, URLs externas, Markdown peligroso y tope de longitud | `app/features/chat/output_guard.py` |
| Infra | Rate limit por IP, presupuesto diario, tope de cuerpo, CORS estricto, TrustedHost, cabeceras CSP/HSTS, sin `/docs` en producción | `app/core/{ratelimit,security}.py`, `app/main.py` |
| Contacto | Honeypot, Turnstile opcional, escape HTML, sin inyección de cabeceras, outbox con reintentos | `app/features/contact/` |
| Privacidad | Feedback anónimo (sin pregunta ni IP); logs sin contenido de usuario | ADR-0002, `docs/privacy.md` |

## Pruebas

- `tests/integration/test_security_suite.py` (T4.10):
  - red-team de `eval/redteam.jsonl` (15 payloads) detectado/bloqueado;
  - un proveedor que **simula fugar el prompt** es cortado por el output guard
    (0 fugas observadas);
  - payloads de extracción no llegan ni al retriever ni al LLM;
  - ráfaga contra el limitador (429) y host no permitido (400);
  - tormenta de 10 cancelaciones SSE seguida de streams nuevos (semáforo sano);
  - el canario de la nota no publicada nunca entra en el índice.
- `tests/unit/test_output_guard.py`, `test_sanitize.py`, `test_ratelimit.py`,
  `test_contact.py`...
- Cobertura (`pytest --cov=app`): **95%** (gate ≥85%).

## Prueba de humo de carga

`scripts/load_smoke.py` lanza N usuarios concurrentes contra `/api/chat`
midiendo el tiempo al primer token. Ejecutar en el nodo con la torre/Dell
encendidos:

```bash
# torre (GPU)
python scripts/load_smoke.py --base-url http://127.0.0.1:8000 --users 50 --duration 60
# con la torre apagada (tier CPU/Dell)
python scripts/load_smoke.py --base-url http://127.0.0.1:8000 --users 20 --duration 60
```

`k6` no está instalado en el nodo; este script es el equivalente mínimo y no
sustituye a una prueba de carga completa. Los p95 por tier se documentarán en
`docs/resilience.md` (T7.8) al ejecutarla.

## Límites conocidos

- El umbral de recuperación solo gestiona fuera de dominio; las preguntas “en
  dominio sin dato” (p. ej. sueldo) las declina el LLM según el prompt.
- La retención de 64 caracteres del output guard agrupa tokens en respuestas
  muy cortas (compromiso por no emitir contenido ya enviado).
- La CSP de la app es de respaldo; la definitiva la aplica Caddy.
