# Arquitectura de CV Web

> Documento vivo. Última actualización: 2026-09-30 (T1.4).
> Objetivo final: `plan.md`. Estado del código: fases 1-7 en curso.

## 1. Visión general

```
Visitante ──HTTPS──► FastAPI (uvicorn)          [objetivo: nodo HP]
                      ├─ /            → frontend/dist (estáticos, T1.9)
                      ├─ /api/health
                      ├─ /api/chat    → Gemini hoy; Ollama vía Tailscale en F2 (SSE)
                      └─ /api/contact → SMTP Gmail
```

- **Frontend**: SPA React 19 + TypeScript + Vite 7 + Tailwind. Una sola página con
  navegación por anclas; consume la API con `VITE_API_URL` (`frontend/src/services/api.ts`).
- **Backend**: FastAPI (Python 3.12) en `backend/app/`, estructura feature-first.
- **Sin base de datos** por ahora: el contenido de la web está hardcodeado en el frontend;
  el chat usa `rafa_context.txt` (privado, fuera del repo, ADR-0006) hasta que F3 lo
  sustituya por RAG sobre una colección pública de Chroma.
- **Secretos**: solo en `backend/.env` local y en el `EnvironmentFile` de systemd.
  Plantilla en `backend/.env.example` (sin valores reales).

## 2. Backend

```
backend/
├── app/
│   ├── main.py                  # create_app(), lifespan, CORS, routers, /docs en prod desactivado
│   ├── core/
│   │   └── config.py            # Settings (pydantic-settings), rutas absolutas vía Path(__file__)
│   └── features/
│       ├── chat/                # router.py, schemas.py, service.py  → Gemini
│       ├── contact/             # router.py, schemas.py, service.py  → SMTP Gmail
│       └── health/              # router.py                          → /api/health
├── tests/                       # pytest + httpx (TestClient)
├── scripts/                     # (F3) ingesta del vault público
├── pyproject.toml               # ruff, mypy --strict, pytest
├── requirements.txt / .lock     # runtime (lock con hashes, reproducibilidad)
└── requirements-dev.txt / .lock # ruff, mypy, pytest, pre-commit, httpx
```

### Rutas actuales

| Método | Ruta | Estado |
|---|---|---|
| GET | `/api/health` | liveness |
| POST | `/api/chat` | canónica (F4 la convertirá en SSE) |
| POST | `/api/contact` | canónica |
| POST | `/contact` | alias temporal (se retira en T5.7) |
| GET | `/docs`, `/openapi.json` | solo en `APP_ENV=development` |

### Arranque y validación

- `lifespan` carga el contexto de Rafael una sola vez y construye los servicios.
- `APP_ENV=production`: si falta una variable obligatoria (`GOOGLE_API_KEY`,
  `EMAIL`, `PASSWORD_APPLICATION`) la app **no arranca** con mensaje claro; sin proveedores
  LLM el chat responde 503.
- `development`: avisa por log y deshabilita el servicio afectado (responde 503).

## 3. Frontend

- `src/App.tsx`: layout, tema claro/oscuro, secciones por anclas.
- `src/components/*`: Hero, About, Experience, Projects, Skills, Contact, Footer, ChatBot.
- `src/services/api.ts`: axios con `baseURL: VITE_API_URL` (vacío = same-origin).
- `public/`: CV en PDF, avatar, favicon.

## 4. Configuración

Referencia completa en `backend/.env.example`:

- **Usadas hoy**: `APP_ENV`, `ALLOWED_ORIGINS`, `GEMINI_MODEL`,
  `GOOGLE_API_KEY`, `EMAIL`, `PASSWORD_APPLICATION`.
- **Router LLM y RAG (F2/F3, ya en uso)**: `LLM_*`, `EMBED_*`, `CHROMA_PATH`, `RAG_*`, `VAULT_PATH`, límites y seguridad (`MAX_*`, `RATE_LIMIT_*`, `DAILY_CHAT_BUDGET`,
  `ALLOWED_HOSTS`, `TRUSTED_PROXY_IPS`, `PROMPT_VERSION`, `PUBLIC_CONTACT_ALLOWLIST`,
  `DATA_PATH`), SMTP futuro (`CONTACT_TO`, `SMTP_*`, `TURNSTILE_*`) y `METRICS_TOKEN`.
- `frontend/.env.example`: `VITE_API_URL` (vacío = same-origin).

## 5. Decisiones

- ADR-0006: ubicación del contexto personal fuera del repo.
- ADRs previstos en el plan: 0001 (allow-list del vault), 0002 (estado en un solo worker),
  0003 (prompt hardening), 0004 (fuente única de contenido), 0005 (exposición a Internet).
- Decisiones D1-D9 en `plan.md` §2.
