# Runbook de CV Web

> Operaciones del nodo HP. Releases/rollback y backups ya descritos; monitorización en T7.6.

## 1. Preparación del nodo (una vez)

```bash
# Usuario de sistema sin login
sudo adduser --system --group --home /opt/cvweb --shell /usr/sbin/nologin cvweb

# Estructura
sudo mkdir -p /opt/cvweb/repo /opt/cvweb/data
sudo chown -R cvweb:cvweb /opt/cvweb

# Código y dependencias
sudo -u cvweb git clone https://github.com/rufae/CV-Web.git /opt/cvweb/repo
sudo -u cvweb python3 -m venv /opt/cvweb/venv
sudo mkdir -p /opt/cvweb/releases
sudo -u cvweb bash -c 'cd /opt/cvweb/repo && git fetch --all'

# Secretos (nunca en git)
sudo cp /opt/cvweb/repo/backend/.env.example /opt/cvweb/.env
sudo chown cvweb:cvweb /opt/cvweb/.env
sudo chmod 600 /opt/cvweb/.env
sudo -u cvweb nano /opt/cvweb/.env      # EMAIL, PASSWORD_APPLICATION, LLM_*, EMBED_*, VAULT_PATH

# Ingesta del vault público (RAG): indexa solo Public/ + cv_public:true
sudo -u cvweb bash -c 'cd /opt/cvweb/repo/backend && \
  /opt/cvweb/venv/bin/python scripts/ingest_public_vault.py \
  --manifest /opt/cvweb/data/ingest_manifest.json'

# Servicio
sudo cp /opt/cvweb/repo/deploy/cvweb.service /etc/systemd/system/cvweb.service
sudo systemctl daemon-reload
sudo systemctl enable --now cvweb
```

## 2. Firewall

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status verbose
```

- Ollama y otros servicios de IA escuchan **solo** en localhost/Tailscale (nunca en la
  interfaz pública). Verificable con `ss -tlnp`.
- Escaneo externo (desde otra red): solo 80/443 visibles.
- `fail2ban` para SSH y, si se añade, el proxy.

## 3. Operaciones habituales

```bash
# Estado y logs
systemctl status cvweb
journalctl -u cvweb -f

# Recargar Caddy tras editar su config
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl reload caddy

# Actualizar (releases + rollback automático, T7.4)
sudo -u cvweb bash /opt/cvweb/repo/deploy/deploy.sh origin/main

# Rollback manual: apuntar al release anterior y reiniciar
ls -1dt /opt/cvweb/releases/*/ | head -5
sudo ln -sfn /opt/cvweb/releases/<release-anterior> /opt/cvweb/current
sudo systemctl restart cvweb

# Reinicio del nodo
sudo systemctl restart cvweb    # debe arrancar solo tras reboot (enable)
```

## 4. Verificación de hardening

```bash
systemd-analyze security cvweb                 # objetivo: < 5
sudo ss -tlnp | grep -E ':80|:443|:8000'       # 8000 solo en 127.0.0.1
sudo -u cvweb test -r /opt/cvweb/.env && echo "permisos .env OK"
```

## 5. Pendiente de fases posteriores

- T4.2/T4.7: rate limiting, tope de cuerpo y presupuesto diario.
- T7.5: exposición definitiva (dominio, CGNAT, Cloudflare Tunnel…) — decisión pendiente, ADR-0005.
- T7.6: monitorización lista. `GET /metrics` (Prometheus) y `GET /api/health/deep`
  requieren cabecera `X-Metrics-Token: $METRICS_TOKEN` (404 si no está
  configurado). Métricas: peticiones de chat por resultado, rechazos, failovers,
  histograma de primer token y mensajes de contacto. Alertas recomendadas con
  Uptime Kuma: caída >5 min, **ambos proveedores caídos**, índice sin actualizar
  >8 días, certificado a <14 días y disco >85 %.
- T7.7: `deploy/backup.sh` + restauración: copia `.env`, `feedback.db`, outbox y
  manifiesto; el índice Chroma NO se copia (se reconstruye con la ingesta).
  Simulacro de restauración pendiente en el nodo.
