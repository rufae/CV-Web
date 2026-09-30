# CVWEB — Documentación real del proyecto (handoff técnico)

> **Este documento ES la documentación del proyecto, no un prompt.** Está generado a partir de la revisión directa del código del monorepo, la ejecución de builds instalaciones reales y la inspección del despliegue en producción (30/09/2026).
>
> Repo: `git@github.com:rufae/CV-Web.git` · Rama `main` · Commit documentado: `62ed721`
> Monorepo unificado con `git subtree` (antes: repos separados `CVWeb-Back` y `CVWeb-Front`, con historial preservado).

---

## 0. Ficha rápida (respuestas directas a lo que se pidió)

| Pregunta | Respuesta |
|---|---|
| ¿Qué es? | Web personal tipo *one page* de Rafael Castaño (CV online) con chatbot IA y formulario de contacto real. |
| Frontend | React 19.1.1 + TypeScript 5.8.3 + Vite 7.0.6 + Tailwind CSS 3.4.1 + shadcn/ui (Radix) + framer-motion 12. Componentes propios en `frontend/src/components/`. |
| Backend | Python 3.12 + FastAPI 0.142.x + Uvicorn + Pydantic 2.13. Dos endpoints: `POST /ask` (Google Gemini 2.5 Flash) y `POST /contact` (email SMTP Gmail 465). |
| ¿Router en frontend? | No. SPA de una sola página con navegación por anclas (`#hero`, `#about`…). |
| ¿Base de datos? | No. Los datos de las secciones están hardcodeados en los componentes; el único estado persistente es el tema (localStorage). |
| ¿Dónde está desplegado hoy? | Frontend: Vercel (`https://cv-web-kappa.vercel.app`). Backend: Render (`https://cvweb-e6ey.onrender.com`). |
| **Estado de producción** | **Frontend OK (HTTP 200). Backend caído: Render responde HTTP 503 “Service Suspended” → el chat y el formulario NO funcionan ahora mismo.** |
| Cómo se conecta el front al back | En build: `VITE_API_URL=https://cvweb-e6ey.onrender.com`, embebido en el bundle por Vite. Verificado en el JS desplegado. |
| ¿Hay tests? | No. Ni frontend ni backend. |
| ¿Docker/CI? | No. Despliegue vía plataformas (Vercel y Render) conectadas a GitHub. |
| Objetivo | Unificar despliegue en un servidor doméstico pequeño (“HP node”) sin depender de Vercel/Render. |

### Estado de verificación de esta revisión

| Comprobación | Resultado | Evidencia |
|---|---|---|
| `npm ci && npm run build` (frontend) | ✅ OK, sin errores | `dist/`: JS 465.10 kB (147.42 kB gzip), CSS 63.65 kB (11.26 kB gzip), 2142 módulos |
| `pip install -r requirements.txt` (venv limpio) | ✅ OK | Python 3.12.3, FastAPI 0.142.2, Uvicorn 0.54.0, google-genai 2.25.0, Pydantic 2.13.5 |
| `npm audit --omit=dev` | ⚠️ 3 vulnerabilidades (1 moderada, 2 altas) transitivas de `axios@1.11.0` | Hay fix con `npm audit fix` |
| Frontend en producción | ✅ HTTP 200 | Bundle `assets/index-D8iOPWEv.js` |
| Backend en producción | ❌ HTTP 503, HTML “This service has been suspended by its owner.” | `curl https://cvweb-e6ey.onrender.com/openapi.json` |
| Backend ejecutado en local | ⏸️ No verificado (requiere `.env` con claves reales de Gemini y Gmail) | — |
| UI probada en navegador | ⏸️ No verificado visualmente en esta revisión | Se detectaron bugs de CSS por análisis del CSS compilado |

---

## 1. Resumen funcional

La web tiene una sola página con las secciones (componentes en `frontend/src/components/`):

| Sección (`id`) | Componente | Contenido |
|---|---|---|
| `#hero` | `Hero.tsx` (179 líneas) | Portada con animaciones (partículas, líneas de código), botones: Ver proyectos, Descargar CV, Contacto. |
| `#about` | `About.tsx` (131) | Bio, avatar (`/RAFAEL.png`), “fun facts”, stats (hardcodeados). |
| `#experience` | `Experience.tsx` (179) | Timeline con 2 puestos en AePTIC y tecnologías. |
| `#projects` | `Projects.tsx` (193) | Grid de 3 proyectos **placeholder** (ver §5.6). |
| `#skills` | `Skills.tsx` (240) | Barras de nivel por categoría + descarga de CV. |
| `#contact` | `Contact.tsx` (307) | Formulario real conectado a `POST /contact`, datos de contacto y redes. |
| — | `Footer.tsx` (172) | Enlaces, créditos (“Alojado en Vercel”). |
| — | `ChatBot.tsx` (170) | Widget flotante de chat conectado a `POST /ask`. |
| — | `ImageWithFallback.tsx` (27) | `<img>` con imagen de fallback embebida. |

Extras: tema claro/oscuro (`theme-context.ts` + `localStorage` + `prefers-color-scheme`), toasts con `sonner`.

---

## 2. Estructura completa del monorepo (inventario real)

Ficheros con líneas/tamaño verificados. `ui/` contiene 55 componentes tipo shadcn/ui, de los que solo se usan 9 (ver anexo F).

```
CVWEB/
├── .git/                              # Repo único (historia de ambos proyectos vía git subtree)
├── .gitignore                         # .env, .env.*, .DS_Store, editores
├── CVWEB.md                           # Este documento
│
├── backend/                           # (antiguo CVWeb-Back)
│   ├── .gitignore                     # venv/, .env, __pycache__, *.pyc, logs…
│   ├── main.py                        # 30 líneas — FastAPI + CORS + routers
│   ├── ia.py                          # 45 líneas — /ask (Gemini)
│   ├── form_email.py                  # 99 líneas — /contact (SMTP Gmail)
│   ├── rafa_context.txt               # 113 líneas / 9 KB — contexto del prompt IA
│   └── requirements.txt               # 5 líneas — deps sin fijar
│
└── frontend/                          # (antiguo CVWeb-Front)
    ├── .gitignore                     # node_modules, dist, .env
    ├── index.html                     # 13 líneas — HTML raíz (lang="en", favicon PNG)
    ├── package.json                   # 68 líneas — ver anexo B
    ├── package-lock.json              # 244 KB
    ├── vite.config.ts                 # 7 líneas — solo plugin react, SIN proxy
    ├── tsconfig.json                  # refs a app/node
    ├── tsconfig.app.json              # strict, noUnusedLocals…
    ├── tsconfig.node.json
    ├── tailwind.config.js             # 21 líneas — darkMode class + 6 tokens
    ├── postcss.config.js              # tailwind + autoprefixer
    ├── eslint.config.js               # flat config (js, tseslint, hooks, refresh)
    ├── README.md                      # plantilla por defecto de Vite (desactualizado)
    ├── public/
    │   ├── Curriculum vitae.pdf       # 551 KB — nombre con espacios
    │   ├── curriculum-vitae.png       # 36 KB — favicon
    │   ├── RAFAEL.png                 # 93 KB — avatar
    │   └── vite.svg                   # 1.5 KB — sin usar
    └── src/
        ├── main.tsx                   # 12 líneas — importa index.css, global.css, chatbot.css
        ├── App.tsx                    # 86 líneas — layout, nav, tema, secciones
        ├── theme-context.ts           # 8 líneas — Context light/dark
        ├── index.css                  # 41 líneas — Tailwind + variables hex
        ├── vite-env.d.ts              # 1 línea
        ├── App.css                    # 42 líneas — NO importado (muerto)
        ├── Attributions.md            # 0 bytes (vacío)
        ├── services/
        │   └── api.ts                 # 32 líneas — axios + askRafa + sendContactForm
        └── components/
            ├── Hero.tsx               # 179
            ├── About.tsx              # 131
            ├── Experience.tsx         # 179
            ├── Projects.tsx           # 193
            ├── Skills.tsx             # 240
            ├── Contact.tsx            # 307
            ├── Footer.tsx             # 172
            ├── ChatBot.tsx            # 170
            ├── styles/
            │   ├── global.css         # 194 líneas — variables CSS (duplicadas) + animaciones
            │   └── chatbot.css        # 179 líneas — estilos del chat
            ├── figma/
            │   └── ImageWithFallback.tsx   # 27
            └── ui/                    # 55 ficheros shadcn/ui (solo 9 usados)
```

> `git log -- backend/` y `git log -- frontend/` muestran la historia de cada proyecto por separado, preservada con `git subtree`.

---

## 3. Backend (FastAPI)

### 3.1 Stack y dependencias

`backend/requirements.txt` **completo** (sin versiones fijadas):

```
fastapi
uvicorn
python-dotenv
google-genai
google-generativeai
pydantic[email]
```

- `google-genai` es el SDK **usado** (import `from google import genai`).
- `google-generativeai` es el SDK **legacy y no se usa** en el código; además arrastra `google-api-python-client`, `google-ai-generativelanguage`, `google-auth-httplib2`, etc.
- Instalación verificada en venv limpio (Python 3.12.3): FastAPI 0.142.2, Uvicorn 0.54.0, Pydantic 2.13.5, email-validator 2.3.0, google-genai 2.25.0, google-generativeai 0.8.6, python-dotenv 1.2.3.

### 3.2 API expuesta

| Método | Ruta | Request | Response | Implementación |
|---|---|---|---|---|
| POST | `/ask` | `{"message": "string"}` | `{"response": "string"}` | `ia.py:24-45` |
| POST | `/contact` | `{"name": "string", "email": "email", "message": "string"}` | `{"status": "Mensaje enviado correctamente"}` | `form_email.py:18-99` |
| GET | `/docs` (Swagger) | — | HTML | Automático de FastAPI (expuesto) |
| GET | `/openapi.json` | — | JSON | Automático de FastAPI (expuesto) |

Ejemplo de llamada (en producción hoy daría error 503):

```bash
curl -X POST https://cvweb-e6ey.onrender.com/ask \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Qué tecnologías usas?"}'
```

### 3.3 Código clave (referencias)

- `main.py:14-18` — CORS con allowlist fija: `http://localhost:5173`, `http://127.0.0.1:5173`, `https://cv-web-kappa.vercel.app`; `allow_credentials=True`, `allow_methods=["*"]`, `allow_headers=["*"]`.
- `ia.py:16-17` — `open("rafa_context.txt")` con **ruta relativa al CWD** en tiempo de import.
- `ia.py:10-12` — `GOOGLE_API_KEY` obligatoria en import o la app no arranca.
- `ia.py:37-43` — `client.models.generate_content(model="gemini-2.5-flash", ..., thinking_budget=0)` en cada petición.
- `form_email.py:21-23` — `EMAIL` (emisor y receptor) y `PASSWORD_APPLICATION`.
- `form_email.py:91-93` — `smtplib.SMTP_SSL("smtp.gmail.com", 465)` + `server.login(...)`.
- Código completo de los 3 ficheros en el **anexo A**.

### 3.4 Variables de entorno

| Variable | Uso | Obligatoria |
|---|---|---|
| `GOOGLE_API_KEY` | Gemini (Google AI Studio) | Sí (crash al importar sin ella) |
| `EMAIL` | Cuenta Gmail remitente **y** destinataria | Para `/contact` |
| `PASSWORD_APPLICATION` | Contraseña de aplicación Gmail (16 chars) | Para `/contact` |

No existe `.env.example` (recomendado crearlo, anexo H). El `.env` real está ignorado por git. El CWD esperado al arrancar es `backend/` (por la ruta relativa de `rafa_context.txt`).

### 3.5 Riesgos detectados (backend)

| # | Riesgo | Detalle / referencia | Impacto |
|---|---|---|---|
| B1 | **Ruta relativa frágil** | `ia.py:16` abre `rafa_context.txt` relativo al CWD → `FileNotFoundError` si systemd/uvicorn arranca desde otro directorio | Alto (servicio no arranca) |
| B2 | **Sin rate limit ni límite de tamaño en `/ask`** | Cualquiera puede agotar cuota/coste de Gemini | Alto (coste) |
| B3 | **Sin captcha/honeypot en `/contact`** | Puede usarse como relay de spam | Medio-alto |
| B4 | **HTML del email sin escapar** | `form_email.py:59,63,67` inserta los campos tal cual en el HTML del correo | Medio (phishing/abuso) |
| B5 | **CORS hardcodeado** | `main.py:14-18`; en same-origin sobra; si separado, parametrizar | Medio |
| B6 | **Sin manejo de errores de Gemini** | Excepción → 500 genérico, sin logging estructurado | Medio |
| B7 | **Dependencia legacy y versiones sin fijar** | `google-generativeai` + `requirements.txt` sin pins → builds no reproducibles | Medio |
| B8 | **Sin `/health`, Swagger abierto** | No hay endpoint de salud para systemd/proxy; `/docs` expuesto | Bajo-medio |
| B9 | **Datos personales versionados** | `rafa_context.txt` (fecha de nacimiento) y teléfono/email en repo público | Medio (privacidad) |
| B10 | **Sin tests** | 0 cobertura | Medio |

---

## 4. Frontend (React + Vite)

### 4.1 Stack y versiones instaladas (verificadas)

| Pieza | Versión |
|---|---|
| React / react-dom | 19.1.1 |
| TypeScript | 5.8.3 (`strict`, `noUnusedLocals`, `noUnusedParameters`, `verbatimModuleSyntax`) |
| Vite | 7.0.6 (requiere Node `^20.19` o `>=22.12`) |
| Tailwind / postcss / autoprefixer | 3.4.1 / 8.5.x / 10.4.x |
| framer-motion | 12.23.12 |
| axios | 1.11.0 |
| lucide-react | 0.532.x |
| sonner | 2.0.x |
| shadcn/ui (Radix) | `@radix-ui/*` (mayoría sin usar, ver anexo F) |

`package.json` completo en el **anexo B**.

### 4.2 Scripts npm

| Script | Comando | Verificado |
|---|---|---|
| `dev` | `vite` (puerto 5173) | — |
| `build` | `tsc -b && vite build` → `dist/` | ✅ |
| `lint` | `eslint .` (flat config) | — |
| `preview` | `vite preview` | — |

Métricas del build local: `index.html` 0.48 kB · CSS 63.65 kB (gzip 11.26) · JS 465.10 kB (gzip 147.42) · 2142 módulos · ~1.9 s. El grueso del JS es React + framer-motion.

Avisos del build: (a) PostCSS avisa de **CSS anidado mal configurado** en `global.css:99-149`; (b) `caniuse-lite` desactualizado.

### 4.3 Flujo de datos

```
ChatBot.tsx ──► services/api.ts::askRafa()          ──POST {VITE_API_URL}/ask
Contact.tsx ──► services/api.ts::sendContactForm()  ──POST {VITE_API_URL}/contact

const api = axios.create({ baseURL: import.meta.env.VITE_API_URL, ... })  // api.ts:5-10
```

`api.ts:3` además hace `console.log('API URL:', import.meta.env.VITE_API_URL)` (visible en el bundle de producción: se confirmó que contiene literalmente `console.log("API URL:","https://cvweb-e6ey.onrender.com")`).

**Sin `.envexample` ni `.env` en el repo.** Si `VITE_API_URL` no se define en build, axios usa rutas relativas contra el mismo origen (clave para el despliegue unificado).

### 4.4 Bugs de estilos confirmados en producción

El CSS compilado (tanto local como el desplegado en Vercel) contiene reglas inválidas:

- `tailwind.config.js:10-17` define los colores como `hsl(var(--token))`, pero los tokens de `index.css:6-31` y `global.css:5-94` son hex/rgba (`--accent: #1E90FF`, `--border: rgba(0,0,0,.1)`…). Resultado: `.bg-accent { background-color: hsl(var(--accent)) }` → `hsl(#1E90FF)` es **CSS inválido**, la declaración se ignora. Afecta a `bg-accent`, `text-accent`, `bg-card`, `text-foreground`, `border-border`, etc.
- Tokens usados en el código pero **ausentes** del config → Tailwind no genera esas clases: `text-muted-foreground`, `bg-muted/20`, `bg-secondary`, `text-destructive`, `ring`, `popover`. Verificado con grep sobre el CSS compilado: `text-muted-foreground` no existe.
- Consecuencia práctica: el aspecto final depende de estilos base/defaults; muchos colores semánticos (incluido el botón flotante del chat) no se pintan como se pretende.

Además hay **dos bloques de variables duplicados** (`index.css` y `global.css` con valores distintos en algunos tokens; `global.css` gana por orden de import en `main.tsx:3-5`).

### 4.5 Otros hallazgos frontend

- `Projects.tsx:10-44`: 3 proyectos de ejemplo con URLs placeholder (`github.com/rafael/...`); la tarjeta “CV Web” describe una app del clima. Demos inventadas.
- `Contact.tsx:76` y `Footer.tsx:13`: GitHub apunta a `https://github.com/rafael` (el usuario real parece `rufae`).
- `Hero.tsx:125` y `Skills.tsx:229`: enlace a `/Curriculum vitae.pdf` (espacios en el nombre; funciona URL-encoded pero conviene renombrar).
- `index.html:2`: `lang="en"` con contenido en español.
- `ChatBot.tsx:150`: `onKeyPress` (deprecado en React 19; funciona).
- `ChatBot.tsx:95`: panel de 400×600 px fijos → revisar móvil.
- Código muerto: `App.css`, `Attributions.md` (vacío), `public/vite.svg`, `README.md` de plantilla, ~46 de 55 componentes `ui/`.
- Sin tests, sin PWA, sin SSR (todo cliente).

---

## 5. Despliegue actual (verificado el 30/09/2026)

### 5.1 Diagrama real

```
Usuario
  │
  ▼
https://cv-web-kappa.vercel.app          Frontend estático (Vercel, build de Vite)
  │  bundle index-D8iOPWEv.js  (10.0.4 verificado HTTP 200)
  │  contiene hardcodeado: VITE_API_URL=https://cvweb-e6ey.onrender.com
  ▼
https://cvweb-e6ey.onrender.com          Backend FastAPI (Render)
  ✗ HTTP 503 "Service Suspended" → /ask y /contact NO funcionan
```

### 5.2 Qué se sabe del despliegue

| Elemento | Dato | Fuente |
|---|---|---|
| Frontend host | Vercel | URL pública + `access-control-allow-origin: *` de Vercel |
| Frontend origen del build | Repo `CVWeb-Front` (el bundle desplegado, `index-D8iOPWEv.js`, difiere del build local `index-15m-Nob4.js`, pero mismo contenido funcional) | Hash distinto + console.log visible |
| Backend host | Render (`onrender.com`) | URL en el bundle + HTML de Render |
| Estado backend | **Suspendido por el propietario** (HTTP 503) | `curl /openapi.json` y `/docs` |
| CORS backend | Allowlist con `localhost:5173` y el dominio de Vercel | `main.py:14-18` |
| Secretos de producción | Presumiblemente en paneles de Vercel/Render (no versionados) | `requirements.txt` + código |
| Dominio propio | No consta | — |
| Repos antiguos | `rufae/CVWeb-Back` y `rufae/CVWeb-Front` siguen en GitHub | `git remote -v` de los repos originales |

> **Consecuencia inmediata**: mientras el backend siga suspendido, el chatbot y el formulario de contacto de la web pública están rotos. Migrar al nodo HP resuelve esto además de unificar.

---

## 6. Plan de despliegue propuesto en el nodo HP

### 6.1 Opciones

| Opción | Descripción | Pros | Contras |
|---|---|---|---|
| **A. Todo en FastAPI** (recomendada) | FastAPI sirve `frontend/dist` (`StaticFiles`) + endpoints | 1 proceso, 1 puerto, sin CORS, TLS con 1 proxy; ideal nodo pequeño | Cambio menor en `main.py`; estáticos servidos por Python (suficiente para este tráfico) |
| B. Proxy + Uvicorn separado | nginx/Caddy sirve `dist/` y hace proxy de `/ask` y `/contact` | Mejor rendimiento de estáticos; patrón clásico | 2 configuraciones; CORS innecesario si mismo origen |
| C. Docker Compose | Contenerizar ambos | Portable | Overhead innecesario en nodo modesto; solo si ya se usa Docker |

### 6.2 Fases propuestas

- **Fase 0 — Hecha**: unificación del monorepo (subtree) y subida a `rufae/CV-Web`.
- **Fase 1 — Auditoría/verificación** (este documento): confirmar el estado real (builds, endpoints, deuda) sobre el commit `62ed721`. Decisiones de §8.
- **Fase 2 — Correcciones mínimas**: B1 (ruta absoluta), B2/B3 (rate limit), F1 (Tailwind), F2 (console.log), F4 (audit fix), `.env.example`, `GET /health`.
- **Fase 3 — Preparación del nodo**: instalar Python venv + Node (solo si se compila allí), Caddy/nginx, crear usuario `cvweb`, `/opt/cvweb/`.
- **Fase 4 — Despliegue** (Opción A): copiar código, venv, `.env`, `npm ci && npm run build`, montar estáticos, systemd, TLS.
- **Fase 5 — Validación**: chat, formulario, PDF, tema, móvil, `/health`, logs, reinicio automático, certificado; archivar repos antiguos y actualizar enlaces del CV.

### 6.3 Estructura sugerida en el nodo

```
/opt/cvweb/
├── repo/            # git clone https://github.com/rufae/CV-Web.git
├── venv/            # python3 -m venv venv
├── backend/         # (o usar repo/backend)
├── frontend/dist/   # build estático
└── .env             # secretos, chmod 600, fuera de git
```

### 6.4 systemd (borrador, Opción A)

```ini
[Unit]
Description=CV Web (FastAPI + estáticos)
After=network.target

[Service]
User=cvweb
WorkingDirectory=/opt/cvweb/backend
EnvironmentFile=/opt/cvweb/.env
ExecStart=/opt/cvweb/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### 6.5 TLS con Caddy (borrador)

```
cv.tudominio.com {
    reverse_proxy 127.0.0.1:8000
}
```

Alternativa nginx (Opción B):

```nginx
root /opt/cvweb/frontend/dist;
location / { try_files $uri /index.html; }
location ~ ^/(ask|contact)$ { proxy_pass http://127.0.0.1:8000; }
```

### 6.6 Cambio sugerido en `main.py` (Opción A)

```python
from pathlib import Path
from fastapi.staticfiles import StaticFiles

# ... routers ya registrados ...
dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if dist.is_dir():
    app.mount("/", StaticFiles(directory=dist, html=True), name="static")
```

> El mount va **después** de registrar routers; si no, captura `/ask` y `/contact`.

### 6.7 Script de deploy (borrador)

```bash
#!/usr/bin/env bash
set -euo pipefail
cd /opt/cvweb/repo
git pull --ff-only
cd frontend && npm ci && npm run build
cd ../backend && /opt/cvweb/venv/bin/pip install -r requirements.txt
sudo systemctl restart cvweb
```

---

## 7. Cambios recomendados antes de desplegar

### Backend

| # | Cambio | Referencia |
|---|---|---|
| B1 | Ruta absoluta para `rafa_context.txt` (`Path(__file__).parent / ...`) | `ia.py:16` |
| B2 | Rate limit + longitud máxima en `/ask` y `/contact` (p. ej. `slowapi`, 500–1000 chars) | `ia.py:24`, `form_email.py:18` |
| B3 | Honeypot/captcha o rate limit del proxy en `/contact` | `form_email.py:18` |
| B4 | Escapar HTML del formulario (`html.escape`) | `form_email.py:59-67` |
| B5 | Quitar `google-generativeai` y fijar versiones (`pip freeze` / `uv`) | `requirements.txt` |
| B6 | `GET /health` + deshabilitar `/docs` en prod si se desea | `main.py` |
| B7 | Logging y manejo de errores Gemini/SMTP con mensajes genéricos | `ia.py:37`, `form_email.py:98` |
| B8 | CORS por env o eliminarlo (same-origin) | `main.py:14-18` |
| B9 | `.env.example` | `backend/` |
| B10 | Decidir visibilidad del repo / anonimizar `rafa_context.txt` | `rafa_context.txt` |

### Frontend

| # | Cambio | Referencia |
|---|---|---|
| F1 | Arreglar tokens Tailwind (HSL sin envolver o `var()` directo) y completar `muted`, `secondary`, `destructive`, `input`, `ring`, `popover` | `tailwind.config.js:10-17`, `index.css`, `global.css` |
| F2 | Quitar `console.log` | `services/api.ts:3` |
| F3 | `.env.example` para `VITE_API_URL` (o dejarla vacía en build same-origin) | `frontend/` |
| F4 | `npm audit fix` (3 vulnerabilidades axios) | `package-lock.json` |
| F5 | Podar componentes `ui/` y deps no usadas; borrar `App.css`, `Attributions.md`, `vite.svg`, `README.md` plantilla | `src/components/ui/`, `package.json` |
| F6 | Renombrar PDF a `curriculum-vitae.pdf` y actualizar enlaces | `Hero.tsx:125`, `Skills.tsx:229` |
| F7 | `lang="es"` + metadatos SEO/og | `index.html:2` |
| F8 | `onKeyPress` → `onKeyDown` | `ChatBot.tsx:150` |
| F9 | Chat responsive en móvil | `ChatBot.tsx:95` |
| F10 | Datos reales de proyectos y redes (`rufae`) | `Projects.tsx`, `Contact.tsx:76`, `Footer.tsx:13` |
| F11 | Unificar variables CSS y corregir el aviso de CSS anidado | `index.css`, `global.css:99-149` |

### Monorepo / infra

| # | Cambio |
|---|---|
| M1 | `README.md` raíz con dev + deploy (sustituir el de Vite) |
| M2 | `.env.example` en backend y frontend |
| M3 | Versionar `deploy.sh` y unidad systemd (p. ej. carpeta `deploy/`) |
| M4 | Opcional: Dockerfile/compose |
| M5 | Archivar `CVWeb-Back`/`CVWeb-Front` al validar el despliegue |
| M6 | Actualizar el pie de página (“Alojado en Vercel” ya no aplicará) |

---

## 8. Decisiones abiertas (para el especialista)

1. **Arquitectura**: ¿Opción A (todo FastAPI, recomendada) u Opción B (proxy + Uvicorn)?
2. **Dominio/TLS**: ¿dominio propio? ¿Caddy (auto-HTTPS) o nginx + certbot?
3. **Secretos**: `.env` + `systemd EnvironmentFile`, o gestor de secretos.
4. **Build**: ¿`npm run build` en el nodo (necesita Node LTS ≥20.19) o build en local/CI y subir `dist/`?
5. **Repo**: ¿público (contiene datos personales) o privado?
6. **Alcance**: ¿se aplican las correcciones B1–B10/F1–F11 antes de exponer, o se despliega tal cual y se itera?
7. **Backend actual**: confirmar si el servicio de Render se cancela/elimina y de dónde se recuperan sus variables de entorno.
8. **Contenido**: confirmar datos reales de proyectos/redes (hoy hay placeholders).

---

## 9. Anexos

### A. Código backend completo

#### A.1 `backend/main.py` (30 líneas)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from ia import ask_rafa_endpoint
from form_email import send_email_endpoint

# Cargar variables de entorno
load_dotenv()

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://cv-web-kappa.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir endpoints
app.include_router(ask_rafa_endpoint)
app.include_router(send_email_endpoint)
```

#### A.2 `backend/ia.py` (45 líneas)

```python
from fastapi import APIRouter
from pydantic import BaseModel
from dotenv import load_dotenv
import os

from google import genai
from google.genai import types

load_dotenv()
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("API key de Gemini no encontrada en el archivo .env")

client = genai.Client(api_key=GEMINI_API_KEY)

with open("rafa_context.txt", "r", encoding="utf-8") as f:
    rafa_context = f.read()

ask_rafa_endpoint = APIRouter()

class Prompt(BaseModel):
    message: str

@ask_rafa_endpoint.post("/ask")
async def ask_rafa(prompt: Prompt):
    full_prompt = (
        f"Eres una IA que responde preguntas como si fueses Rafael Castaño, un desarrollador.\n"
        f"Tu misión es contestar siempre de forma clara y concisa, con respuestas breves y directas, "
        f"para que el usuario pueda leerlas fácilmente en pantalla. "
        f"No extiendas demasiado la respuesta salvo que el usuario pida explícitamente una explicación detallada.\n\n"
        f"Aquí tienes toda la información relevante sobre Rafael:\n{rafa_context}\n\n"
        f"Pregunta: {prompt.message}\n\n"
        f"Recuerda ser conciso, excepto si el usuario pide detalle."
        f"Si el usuario te pregunta algo que no esta relacionado con saber algo sobre Rafael Castaño debes decirle que no puede hacer preguntas que no sean para conocer a Rafael pero de una manera profesional y limpia"
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=full_prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0)
        )
    )

    return {"response": response.text}
```

#### A.3 `backend/form_email.py` (99 líneas)

```python
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

load_dotenv()  # carga variables .env automáticamente

send_email_endpoint = APIRouter()

class ContactForm(BaseModel):
    name: str
    email: EmailStr
    message: str

@send_email_endpoint.post("/contact")
async def send_email(form: ContactForm):
    try:
        sender_email = os.getenv("EMAIL")  # tu email emisor real (por ejemplo Gmail)
        receiver_email = os.getenv("EMAIL") # donde quieres recibir los mensajes
        password = os.getenv("PASSWORD_APPLICATION")  # contraseña de aplicación desde .env

        if not password:
            raise HTTPException(status_code=500, detail="No se encontró la contraseña en variables de entorno")

        message = MIMEMultipart("alternative")
        message["Subject"] = f"Nuevo mensaje de {form.name} CV Web"
        message["From"] = sender_email
        message["To"] = receiver_email

        # Texto plano (fallback)
        text = f"Nombre: {form.name}\nEmail: {form.email}\nMensaje:\n{form.message}"

        # HTML con estilo avanzado
        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        <title>Nuevo mensaje de contacto</title>
        </head>
        <body style="margin:0; padding:0; background-color:#f4f6f8; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
        <table align="center" width="600" cellpadding="0" cellspacing="0" style="background:#fff; margin: 40px auto; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
            <tr>
            <td style="background: #0052cc; padding: 20px 30px; border-radius: 10px 10px 0 0; color: #ffffff; text-align: center;">
                <h1 style="margin: 0; font-weight: 700;">Nuevo mensaje desde CV Web</h1>
            </td>
            </tr>
            <tr>
            <td style="padding: 30px;">
                <p style="font-size: 16px; color: #333;">Has recibido un nuevo mensaje con los siguientes detalles:</p>

                <table width="100%" cellpadding="5" cellspacing="0" style="border-collapse: collapse; margin-top: 20px;">
                <tr>
                    <td style="background: #e7f0fd; font-weight: 600; width: 130px; border-radius: 5px 0 0 5px;">Nombre:</td>
                    <td style="background: #f9fbfd; border-radius: 0 5px 5px 0;">{form.name}</td>
                </tr>
                <tr>
                    <td style="background: #e7f0fd; font-weight: 600; border-radius: 5px 0 0 5px;">Email:</td>
                    <td style="background: #f9fbfd; border-radius: 0 5px 5px 0;">{form.email}</td>
                </tr>
                <tr>
                    <td style="background: #e7f0fd; font-weight: 600; vertical-align: top; border-radius: 5px 0 0 5px;">Mensaje:</td>
                    <td style="background: #f9fbfd; border-radius: 0 5px 5px 0; white-space: pre-line;">{form.message}</td>
                </tr>
                </table>

                <p style="font-size: 14px; color: #777; margin-top: 30px;">Este mensaje fue enviado desde tu formulario web.</p>
            </td>
            </tr>
            <tr>
            <td style="background: #f1f3f5; padding: 15px 30px; text-align: center; border-radius: 0 0 10px 10px; font-size: 12px; color: #999;">
                &copy; 2025 Tu Empresa - Todos los derechos reservados
            </td>
            </tr>
        </table>
        </body>
        </html>
        """

        # Adjuntar ambas versiones
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")

        message.attach(part1)
        message.attach(part2)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())

        return {"status": "Mensaje enviado correctamente"}


    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enviando email: {str(e)}")
```

#### A.4 `backend/rafa_context.txt` — estructura (contenido con datos personales, no se reproduce)

113 líneas. Secciones (líneas): Formación académica (7), Experiencia profesional (15), Habilidades técnicas (28), Proyectos relevantes (38), Soft skills (47), Idiomas (57), Intereses (62), Formación continua (71), Objetivos (79), Otros datos (84), Datos de contacto profesional (90), Expresiones frecuentes (98). Se inyecta completo en el prompt de Gemini en cada petición.

#### A.5 `backend/requirements.txt`

```
fastapi
uvicorn
python-dotenv
google-genai
google-generativeai
pydantic[email]
```

### B. `frontend/package.json` completo

```json
{
  "name": "my-cv-web",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "lint": "eslint .",
    "preview": "vite preview"
  },
  "dependencies": {
    "@radix-ui/react-accordion": "^1.2.11",
    "@radix-ui/react-alert-dialog": "^1.1.14",
    "@radix-ui/react-aspect-ratio": "^1.1.7",
    "@radix-ui/react-avatar": "^1.1.10",
    "@radix-ui/react-checkbox": "^1.3.2",
    "@radix-ui/react-context-menu": "^2.2.15",
    "@radix-ui/react-dropdown-menu": "^2.1.15",
    "@radix-ui/react-hover-card": "^1.1.14",
    "@radix-ui/react-label": "^2.1.7",
    "@radix-ui/react-menubar": "^1.1.15",
    "@radix-ui/react-navigation-menu": "^1.2.13",
    "@radix-ui/react-popover": "^1.1.14",
    "@radix-ui/react-progress": "^1.1.7",
    "@radix-ui/react-radio-group": "^1.3.7",
    "@radix-ui/react-scroll-area": "^1.2.9",
    "@radix-ui/react-select": "^2.2.5",
    "@radix-ui/react-separator": "^1.1.7",
    "@radix-ui/react-slider": "^1.3.5",
    "@radix-ui/react-switch": "^1.2.5",
    "@radix-ui/react-tabs": "^1.1.12",
    "@radix-ui/react-toggle-group": "^1.1.10",
    "@radix-ui/react-tooltip": "^1.2.7",
    "axios": "^1.11.0",
    "class-variance-authority": "^0.7.1",
    "cmdk": "^1.1.1",
    "embla-carousel-react": "^8.6.0",
    "framer-motion": "^12.23.12",
    "input-otp": "^1.4.2",
    "lucide-react": "^0.532.0",
    "react": "^19.1.0",
    "react-day-picker": "^9.8.1",
    "react-dom": "^19.1.0",
    "react-hook-form": "^7.61.1",
    "react-resizable-panels": "^3.0.3",
    "recharts": "^3.1.0",
    "sonner": "^2.0.3",
    "tailwind-merge": "^3.3.1",
    "vaul": "^1.1.2"
  },
  "devDependencies": {
    "@eslint/js": "^9.30.1",
    "@types/react": "^19.1.8",
    "@types/react-dom": "^19.1.6",
    "@vitejs/plugin-react": "^4.6.0",
    "autoprefixer": "^10.4.21",
    "eslint": "^9.30.1",
    "eslint-plugin-react-hooks": "^5.2.0",
    "eslint-plugin-react-refresh": "^0.4.20",
    "globals": "^16.3.0",
    "postcss": "^8.5.6",
    "tailwindcss": "^3.4.1",
    "typescript": "~5.8.3",
    "typescript-eslint": "^8.35.1",
    "vite": "^7.0.4"
  }
}
```

### C. Configs frontend clave

`vite.config.ts` (sin proxy, sin alias):

```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})
```

`tailwind.config.js`:

```js
/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        card: 'hsl(var(--card))',
        accent: 'hsl(var(--accent))',
        'accent-foreground': 'hsl(var(--accent-foreground))',
        border: 'hsl(var(--border))',
      },
    },
  },
  plugins: [],
};
```

`index.html`:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/curriculum-vitae.png" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>¡Bienvenid@ a mi CV!</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

`tsconfig.app.json` (resumen): `target ES2022`, `module ESNext`, `moduleResolution bundler`, `jsx react-jsx`, `strict`, `noUnusedLocals`, `noUnusedParameters`, `verbatimModuleSyntax`, `noEmit`.

`README.md` de `frontend/`: plantilla por defecto de Vite (“This template provides a minimal setup to get React working in Vite…”). **No hay README en la raíz del monorepo.**

### D. `frontend/src/services/api.ts` completo

```ts
import axios from 'axios';

console.log('API URL:', import.meta.env.VITE_API_URL);

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const askRafa = async (message: string) => {
  try {
    const response = await api.post('/ask', { message });
    return response.data.response;
  } catch (error) {
    console.error('Error al consultar el backend:', error);
    return 'Ocurrió un error al conectar con Rafael. Intenta de nuevo más tarde.';
  }
};

export const sendContactForm = async (formData: { name: string; email: string; message: string }) => {
  try {
    const response = await api.post('/contact', formData);
    return response.data;
  } catch (error) {
    console.error('Error enviando formulario:', error);
    throw error;
  }
};

export default api;
```

### E. Inventario de componentes `ui/` (55 ficheros)

**Usados (9)**: `avatar`, `badge`, `button`, `card`, `input`, `label`, `progress`, `sonner`, `textarea`.

**Sin usar (46)**: `accordion`, `alert-dialog`, `alert`, `aspect-ratio`, `breadcrumb`, `button-variants`, `buttonVariant`, `badgeVariants`, `calendar`, `carousel`, `chart`, `checkbox`, `collapsible`, `command`, `context-menu`, `dialog`, `drawer`, `dropdown-menu`, `form`, `hover-card`, `input-otp`, `menubar`, `navigation-menu`, `navigation-menu-utils`, `pagination`, `popover`, `radio-group`, `resizable`, `scroll-area`, `select`, `separator`, `sheet`, `SidebarContext`, `sidebar`, `skeleton`, `slider`, `switch`, `table`, `tabs`, `toggle-group`, `toggle`, `toggleVariants`, `tooltip`, `useFormField`, `use-mobile`, `utils`.

> Vite hace tree-shaking, por lo que los no usados no entran al bundle; sí afectan a `tsc`, ESLint y mantenimiento. Las dependencias npm asociadas (recharts, embla, cmdk, vaul, etc.) se pueden eliminar si se podan.

### F. Evidencia de verificación (comandos y salidas)

```text
$ npm ci && npm run build          # frontend, Node 24.14.1
vite v7.0.6 building for production...
✓ 2142 modules transformed.
dist/index.html                   0.48 kB │ gzip:   0.32 kB
dist/assets/index-BpxMQ0Lg.css   63.65 kB │ gzip:  11.26 kB
dist/assets/index-15m-Nob4.js   465.10 kB │ gzip: 147.42 kB
✓ built in 1.93s

$ npm audit --omit=dev
3 vulnerabilities (1 moderate, 2 high)     # transitivas de axios@1.11.0

$ python3 -m venv venv && pip install -r requirements.txt   # Python 3.12.3
Successfully installed fastapi-0.142.2 uvicorn-0.54.0 pydantic-2.13.5 \
  google-genai-2.25.0 google-generativeai-0.8.6 python-dotenv-1.2.3 email-validator-2.3.0 ...

$ curl -sI https://cv-web-kappa.vercel.app/
HTTP/2 200        # frontend vivo

$ curl -s https://cvweb-e6ey.onrender.com/openapi.json
<!DOCTYPE html>...<title>Service Suspended</title>...   # backend caído (503)
```

Evidencia en el bundle de producción (`index-D8iOPWEv.js`):

```js
console.log("API URL:","https://cvweb-e6ey.onrender.com");
const a1 = Wt.create({ baseURL:"https://cvweb-e6ey.onrender.com", headers:{"Content-Type":"application/json"} });
```

### G. Variables de entorno (plantilla propuesta)

```dotenv
# backend/.env
GOOGLE_API_KEY=clave_de_google_ai_studio
EMAIL=rafaelcastanoblanca1805@gmail.com
PASSWORD_APPLICATION=xxxx xxxx xxxx xxxx

# frontend/.env  (solo en tiempo de build; vacío/omitido = same-origin)
VITE_API_URL=http://localhost:8000
```

### H. Comandos útiles

```bash
# Historia por subproyecto
git log --oneline -- backend/
git log --oneline -- frontend/

# Desarrollo local
(cd backend && python3 -m venv venv && source venv/bin/activate && \
   pip install -r requirements.txt && uvicorn main:app --reload --port 8000)
(cd frontend && npm ci && npm run dev)   # necesita frontend/.env con VITE_API_URL

# Build de producción
(cd frontend && npm ci && npm run build)

# Comprobar producción
curl -sI https://cv-web-kappa.vercel.app/
curl -s -o /dev/null -w "%{http_code}\n" https://cvweb-e6ey.onrender.com/docs
```
