# Evaluación del RAG (T3.7)

> Informe más reciente: `eval/reports/2026-09-30.json`.
> Dataset: `eval/dataset.jsonl` · Vault de evaluación: `eval/fixtures/vault/`
> Fixtures de embeddings: `eval/fixtures/embeddings.npz` (regenerables).

## Qué mide

| Métrica | Definición | Gate |
|---|---|---|
| `recall@k` | Fracción media de fuentes esperadas presentes en el top-k (sin umbral; mide el ranking) | ≥ 0,90 |
| `mrr` | Media de 1/rango de la primera fuente esperada | informativo |
| `hit_rate` | % de preguntas respondibles con al menos una fuente esperada en el top-k | informativo |
| `refusal_recall` | % de preguntas fuera de dominio rechazadas por el umbral (`RAG_MIN_SCORE`) | ≥ 0,95 |
| `refusal_precision` | De lo rechazado por umbral, cuánto debía rechazarse | informativo |
| `leaks` | Canarios de notas no publicadas presentes en el índice | = 0 |
| `injection_refused` | Inyecciones que no superan el umbral (el resto las trata T4.3/T4.4/T4.6) | informativo |

**Decisión de diseño:** el umbral solo decide *si se responde* (si el mejor score
no llega, se rechaza sin llamar al LLM). Una vez decidido, al LLM se le pasa el
top-k deduplicado completo (aunque algún chunk quede por debajo del umbral),
porque suele contener el dato esperado.

## Último resultado (2026-09-30, bge-m3 en el Dell)

- `recall@5 = 1.000`, `mrr = 0.878`, `hit_rate = 1.000`
- `refusal_recall = 1.000` (umbral elegido: **0.50**), `leaks = 0`
- Gates: **PASS**.

Caveats:

- El dataset y el vault de evaluación son un *fixture* representativo; al crear
  el vault real (`Public/`) hay que **recalibrar** con `--live --calibrate` y
  revisar las fuentes esperadas.
- Las preguntas con respuesta ausente pero en dominio (p. ej. sueldo) no se
  evalúan por umbral: las gestiona el prompt (T4.4) y se medirán en T4.10.
- Las inyecciones se incluyen en el dataset para T4.3/T4.4/T4.6.

## Cómo ejecutarlo

```bash
# Regenerar fixtures (una vez por cambio de vault, modelo o prefijo de corpus)
python scripts/build_eval_fixtures.py --embed-url http://<dell>:11434 --model bge-m3:latest

# Evaluación determinista sin red (CI)
python eval/run_eval.py --retrieval-only

# Calibrar RAG_MIN_SCORE contra el vault real
python eval/run_eval.py --live --embed-url http://<dell>:11434 --calibrate

# Guardar informe versionado
python eval/run_eval.py --report eval/reports/AAAA-MM-DD.json
```

`--live` recalcula embeddings contra `EMBED_URL`; sin `--live` se usan las
fixtures (determinista y offline, apto para CI).
