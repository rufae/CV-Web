# Checklist de puesta en producción (v1.0)

Basada en el Apéndice E de `plan.md`. Estado a 2026-09-30 (F7 completada en
código; despliegue real pendiente en el nodo).

| Punto | Estado | Evidencia / nota |
|---|---|---|
| `gitleaks` limpio en todo el historial; claves antiguas fuera de terceros | ✅ | T1.1; Render/Vercel eliminados |
| `/docs` y `/openapi.json` desactivados en producción; sin trazas en errores | ✅ | `main.py`, `test_headers.py` |
| Ollama accesible **solo** por Tailscale; escaneo externo correcto | ⏳ | Verificar en el nodo (T7.5) |
| Colección `cvweb_public` reconstruida desde el vault; 0 canarios en la suite | ✅ / ⏳ | fixtures ✓; vault real pendiente |
| Evaluación archivada (recall@5 ≥ 0,9; fuga = 0; rechazo ≥ 95 %) | ✅ | `eval/reports/2026-09-30.json` |
| Rate limit, tope de cuerpo y presupuesto verificados con carga | ✅ unit / ⏳ carga real | `test_api_limits.py`; `scripts/load_smoke.py` |
| Failover probado apagando la torre en pleno stream | ✅ simulado / ⏳ real | `test_chaos.py`; game day pendiente |
| Lighthouse móvil ≥ 95 (4 categorías); `axe` sin violaciones graves | ✅ axe / ⏳ Lighthouse | `docs/accessibility.md`; LHCI configurado |
| Alertas activas y probadas; restauración ensayada | ⏳ | T7.6/T7.7 preparados; falta nodo |
| Política de privacidad publicada y coherente con el código | ✅ | `#privacy`, `docs/privacy.md` |
| Web y chat consistentes (`check_consistency.py` en verde) | ✅ | `eval/check_consistency.py` |
| Render/Vercel apagados; CV, LinkedIn y GitHub apuntando al dominio nuevo | ✅ apagados / ⏳ enlaces | T1.1; actualizar enlaces al desplegar |

## Pasos del release

1. Desplegar en el nodo (`deploy/deploy.sh`) y completar las filas ⏳.
2. Ejecutar la checklist del Apéndice E completa con evidencia enlazada.
3. Etiquetar `v1.0.0` y publicar release notes (pendiente de permiso).
4. Actualizar enlaces del CV/LinkedIn/GitHub y archivar los repos antiguos
   (`CVWeb-Back`, `CVWeb-Front`).
