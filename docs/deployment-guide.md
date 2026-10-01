# Guía de despliegue de Rafita / CV Web

> Arquitectura real: el nodo **HP** (`nodochicohp`, Tailscale `<hp-tailscale>`)
> sirve la web y la API en Docker; la inferencia vive en la **torre GPU**
> (`rafael-server`, `<torre-tailscale>:11435`, RTX 3060) y en el **nodo Dell**
> (`<dell-tailscale>:11434`) como respaldo, siempre por Tailscale.
> Los embeddings (`bge-m3`) siempre se calculan en el Dell.
> El proxy del HP es **nginx-proxy-manager**: `http://cv-web.home/` → `127.0.0.1:8086`.

## 0. Servicios en la tailnet

| Nodo | Tailscale | Servicio | Modelo |
|---|---|---|---|
| Torre GPU (rafael-server) | `<torre-tailscale>:11435` | `rafita-ollama-gpu` (Docker, solo tailnet) | `gemma4:12b` |
| Nodo Dell | `<dell-tailscale>:11434` | Ollama | `gemma4:12b` + `bge-m3:latest` |
| Nodo HP | `<hp-tailscale>` | `cvweb_api` (Docker) + nginx-proxy-manager | — |

El router (`LLM_PROVIDERS_ORDER=tower,dell`) usa la torre mientras está
encendida y sáltala sin coste cuando está apagada (health check + circuit
breaker). Si la torre está apagada o tarda más de
`LLM_FIRST_TOKEN_TIMEOUT_S`, la respuesta la genera el Dell (más lento).

## 1. Despliegue con Docker en el HP (el actual)

```bash
# Repo y datos
cd /home/server/proyectos/CVWEB        # ruta actual en el nodo
git pull

# Secretos (una sola vez; luego solo se editan)
cp backend/.env.example .env
chmod 600 .env
nano .env                              # EMAIL/PASSWORD_APPLICATION y METRICS_TOKEN

# Build de la imagen completa (frontend + backend) y arranque
docker compose up -d --build

# Estado
docker compose ps
curl -s http://127.0.0.1:8086/api/status    # {"llm":"online","tier":"gpu"}
curl -s http://127.0.0.1:8086/api/health    # {"status":"ok"}
```

Valores del `.env` en el HP:

```dotenv
APP_ENV=production
ALLOWED_ORIGINS=
ALLOWED_HOSTS=*
LLM_PROVIDERS_ORDER=tower,dell
LLM_TOWER_URL=http://<torre-tailscale>:11435
LLM_TOWER_MODEL=gemma4:12b
LLM_DELL_URL=http://<dell-tailscale>:11434
LLM_DELL_MODEL=gemma4:12b
LLM_FIRST_TOKEN_TIMEOUT_S=30
EMBED_URL=http://<dell-tailscale>:11434
EMBED_MODEL=bge-m3:latest
VAULT_PATH=/vault
PUBLIC_VAULT_DIR=Public
CHROMA_PATH=/data/chroma
DATA_PATH=/data
RAG_TOP_K=5
RAG_MIN_SCORE=0.60
RAG_CONTEXT_PREFIX=Rafael Castaño
PUBLIC_CONTACT_ALLOWLIST=rafaelcastanoblanca1805@gmail.com
EMAIL=rafaelcastanoblanca1805@gmail.com
PASSWORD_APPLICATION=xxxx xxxx xxxx xxxx
METRICS_TOKEN=<token-largo-aleatorio>
```

## 2. Bóveda pública e ingesta

El contenedor monta `./vault` en `/vault` (solo lectura) y `./data` en `/data`
(Chroma, feedback, outbox). Solo se indexan notas de `Public/` con
`cv_public: true`.

El repo incluye una **bóveda pública versionada** en `deploy/public-vault/Public`
(bio, experiencia, proyectos, stack, formación con el máster y el TFM). Para
sembrarla en el nodo:

```bash
mkdir -p vault/Public
cp -r deploy/public-vault/Public/. vault/Public/     # añade o actualiza notas
# Añade también tus propias notas Public/ con `cv_public: true` si quieres

# Indexación (dentro del contenedor en marcha)
docker compose exec cvweb python scripts/ingest_public_vault.py --vault /vault --rebuild
```

> La bóveda completa de Rafita (`../rafita/mi_boveda_obsidian`) **no** se
> indexa: no tiene `Public/` ni notas `cv_public: true`. El asistente de la web
> solo ve la carpeta pública curada.

Reindexado diario opcional (cron del usuario `server`):

```cron
0 4 * * * cd /home/server/proyectos/CVWEB && docker compose exec -T cvweb python scripts/ingest_public_vault.py --vault /vault >/dev/null 2>&1
```

## 3. Proxy (nginx-proxy-manager)

En NPM, el proxy host `cv-web.home` apunta a `127.0.0.1:8086`. Para que el
streaming SSE no se bufferee, en **Advanced** del proxy host:

```nginx
proxy_buffering off;
proxy_cache off;
proxy_read_timeout 300s;
```

## 4. Verificación

```bash
curl -sI http://cv-web.home/                      # 200
curl -s  http://cv-web.home/api/status            # {"llm":"online","tier":"gpu"}
# Chat en streaming (SSE):
curl -sN -X POST http://cv-web.home/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"¿Qué proyectos de IA ha hecho Rafael?","lang":"es"}'
```

Prueba desde el móvil: web, chat (debe responder Rafita con fuentes),
formulario, descarga del PDF y tema oscuro. Con la torre apagada, el chat debe
seguir respondiendo vía Dell (más lento) sin errores.

## 4-bis. Desplegar cambios sin commit (desde tu estación)

Mientras trabajas en el rediseño sin subir a GitHub, puedes sincronizar el
árbol de trabajo y reconstruir en el nodo con `rsync`:

```bash
rsync -av --delete \
  --exclude .git --exclude .env \
  --exclude frontend/node_modules --exclude frontend/dist --exclude frontend/dist-ssr \
  --exclude backend/.venv --exclude backend/data \
  --exclude data --exclude vault --exclude vault_deploy \
  ./ server@nodochicohp:/home/server/proyectos/CVWEB/

ssh server@nodochicohp 'cd /home/server/proyectos/CVWEB && ./deploy/deploy-docker.sh'
```

`compose.yaml` tiene prioridad sobre el antiguo `docker-compose.yml`, así que
el build pasa a ser multi-stage (ya no hace falta Node en el HP).

## 5. Actualizar y revertir

```bash
cd /home/server/proyectos/CVWEB
git pull
docker compose up -d --build          # reconstruye y recrea

# Volver a la imagen anterior (si se etiquetó) o a un commit concreto
git log --oneline -5
git checkout <commit>
docker compose up -d --build
```

## 6. Backup y restauración

```bash
# Estado + secretos (NUNCA al repositorio)
tar czf cvweb-backup-$(date +%F).tgz .env data/ vault/
# Restaurar: descomprimir, `docker compose up -d --build` y reingestar el vault
```

## 7. Alternativa systemd + Caddy (sin Docker)

Si se prefiere el camino del `docs/runbook.md`: usuario `cvweb`, venv en
`/opt/cvweb/venv`, repo en `/opt/cvweb/repo`, `.env` en `/opt/cvweb/.env`,
`deploy/cvweb.service`, `Caddyfile` en `/etc/caddy/` y
`deploy/deploy.sh origin/main`. En ese caso el proxy es Caddy (el CSP del
`deploy/Caddyfile` ya asume assets autoalojados) y el backend escucha en
`127.0.0.1:8000`.

## 9. Desarrollo local (frontend con `npm run dev`)

El servidor de desarrollo de Vite no sirve el backend: necesita un **proxy**
hacia la API de CVWEB. Se configura con `VITE_DEV_API_TARGET`:

```bash
cd frontend
npm install

# Opción A: backend local (uvicorn en 127.0.0.1:8000)
npm run dev

# Opción B: desarrollar contra el backend desplegado en el nodo
VITE_DEV_API_TARGET=http://<nodo>:8086 npm run dev
# p. ej. VITE_DEV_API_TARGET=http://<hp-tailscale>:8086 npm run dev
```

Abre `http://localhost:5173`. Si el asistente muestra «no está disponible»,
comprueba el proxy:

```bash
curl -s http://localhost:5173/api/status   # debe devolver {"llm":"online",...}
```

> Bug 2026-10-01: el proxy apuntaba a `127.0.0.1:8010` (puerto de Rafita, no
> de CVWEB) y el chat nunca respondía en desarrollo.
