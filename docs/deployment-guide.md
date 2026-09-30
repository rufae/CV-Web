# Guía de despliegue en `nodochicohp` (lista para copiar)

> Preparada para el nodo HP en Tailscale (`100.121.77.29`). Sustituye
> `cv.tudominio.example` por tu dominio real y rellena los valores de tus nodos.
> Referencias: `docs/runbook.md`, `docs/adr/0005-public-exposure.md`.

## 0. Prerrequisitos en el HP

```bash
sudo apt update && sudo apt install -y git python3-venv python3-pip curl

# Node LTS (solo para el build; se usa una vez por despliegue)
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs
node --version   # >= 20.19

# Caddy (TLS automático)
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update && sudo apt install -y caddy
```

## 1. Usuario y estructura

```bash
sudo adduser --system --group --home /opt/cvweb --shell /usr/sbin/nologin cvweb
sudo mkdir -p /opt/cvweb/{repo,releases,data}
sudo chown -R cvweb:cvweb /opt/cvweb

sudo -u cvweb git clone https://github.com/rufae/CV-Web.git /opt/cvweb/repo
sudo -u cvweb python3 -m venv /opt/cvweb/venv
sudo -u cvweb /opt/cvweb/venv/bin/pip install --require-hashes -r /opt/cvweb/repo/backend/requirements.lock
```

## 2. Secretos (`/opt/cvweb/.env`)

```bash
sudo cp /opt/cvweb/repo/backend/.env.example /opt/cvweb/.env
sudo chown cvweb:cvweb /opt/cvweb/.env && sudo chmod 600 /opt/cvweb/.env
sudo -u cvweb nano /opt/cvweb/.env
```

Valores mínimos (los LLM van por Tailscale; nunca a Internet):

```dotenv
APP_ENV=production
ALLOWED_ORIGINS=
ALLOWED_HOSTS=cv.tudominio.example,localhost

# Proveedores (IPs Tailscale conocidas)
LLM_PROVIDERS_ORDER=tower,dell
LLM_TOWER_URL=http://100.83.40.103:11434     # nodo con bge-m3/LLMs (Dell)
LLM_TOWER_MODEL=bge-m3:latest                # ajusta al modelo de generación
LLM_DELL_URL=http://100.83.40.103:11434
LLM_DELL_MODEL=qwen2.5:7b
EMBED_URL=http://100.83.40.103:11434
EMBED_MODEL=bge-m3:latest
# Si tu torre GPU tiene otro modelo, ponla primero en el orden y su URL.

VAULT_PATH=/opt/cvweb/vault                  # copia aquí tu carpeta Public/
CHROMA_PATH=/opt/cvweb/data/chroma
DATA_PATH=/opt/cvweb/data
PUBLIC_CONTACT_ALLOWLIST=rafaelcastanoblanca1805@gmail.com

EMAIL=rafaelcastanoblanca1805@gmail.com
PASSWORD_APPLICATION=xxxx xxxx xxxx xxxx    # nueva contraseña de aplicación
METRICS_TOKEN=<token-largo-aleatorio>
```

## 3. Vault público e ingesta

```bash
# Copia tu vault (o solo la carpeta Public/) al nodo
sudo mkdir -p /opt/cvweb/vault && sudo chown -R cvweb:cvweb /opt/cvweb/vault
# scp -r ./MiVault/Public cvweb@<hp>:/opt/cvweb/vault/

# Indexación inicial (usa el repo, antes del primer deploy)
sudo -u cvweb bash -c 'cd /opt/cvweb/repo/backend && \
  /opt/cvweb/venv/bin/python scripts/ingest_public_vault.py \
  --manifest /opt/cvweb/data/ingest_manifest.json'
```

## 4. Servicios (systemd) y Caddy

```bash
sudo cp /opt/cvweb/repo/deploy/cvweb.service /etc/systemd/system/cvweb.service
sudo cp /opt/cvweb/repo/deploy/ingest.service /etc/systemd/system/ingest.service
sudo cp /opt/cvweb/repo/deploy/ingest.timer /etc/systemd/system/ingest.timer
sudo systemctl daemon-reload

# Caddy: ajusta el dominio y copia el bloque
sudo cp /opt/cvweb/repo/deploy/Caddyfile /etc/caddy/Caddyfile.d-cvweb
# edítalo (dominio real) e inclúyelo desde /etc/caddy/Caddyfile: `import Caddyfile.d-cvweb`
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl reload caddy
```

## 5. Primer despliegue (releases + rollback)

```bash
sudo -u cvweb bash /opt/cvweb/repo/deploy/deploy.sh origin/main
sudo systemctl enable --now cvweb ingest.timer
curl -fsS http://127.0.0.1:8000/api/health
```

## 6. Firewall y verificación externa

```bash
sudo ufw default deny incoming && sudo ufw default allow outgoing
sudo ufw allow OpenSSH && sudo ufw allow 80/tcp && sudo ufw allow 443/tcp
sudo ufw enable && sudo ufw status verbose

# Desde fuera de tu red:
curl -sI https://cv.tudominio.example/            # 200 + HSTS/CSP
curl -s  https://cv.tudominio.example/api/status  # {"llm":"online","tier":"gpu"}
```

Comprueba desde el móvil (fuera de casa): web, chat en streaming, formulario,
descarga del PDF y tema oscuro. Prueba también `systemctl kill cvweb` (se
recupera) y un reinicio del nodo.

## 7. Operación

```bash
# Actualizar / rollback
sudo -u cvweb bash /opt/cvweb/repo/deploy/deploy.sh origin/main
ls -1dt /opt/cvweb/releases/*/ | head -5
sudo ln -sfn /opt/cvweb/releases/<anterior> /opt/cvweb/current && sudo systemctl restart cvweb

# Backups + restauración (T7.7)
sudo -u cvweb bash /opt/cvweb/repo/deploy/backup.sh
# restaurar: copia .env y data/*.db de vuelta y reingesta el vault

# Métricas y health profundo
curl -s -H "X-Metrics-Token: $TOKEN" http://127.0.0.1:8000/metrics | head
curl -s -H "X-Metrics-Token: $TOKEN" http://127.0.0.1:8000/api/health/deep

# Carga (game day)
/opt/cvweb/venv/bin/python /opt/cvweb/repo/scripts/load_smoke.py \
  --base-url http://127.0.0.1:8000 --users 20 --duration 60
```

## 8. Cierre v1.0

1. Completar `docs/release-v1.0-checklist.md` con los ⏳.
2. Uptime Kuma (o equivalente) contra `/` y `/api/health/deep` con alertas
   (caída >5 min, ambos proveedores, índice >8 días, cert <14 días, disco >85 %).
3. Actualizar enlaces del CV, LinkedIn y GitHub; archivar `CVWeb-Back`/`CVWeb-Front`.
