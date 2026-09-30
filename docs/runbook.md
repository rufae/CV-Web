# Runbook de CV Web

> Operaciones del nodo HP. Se completa en T7.4 (releases/rollback), T7.6 (monitorización),
> T7.7 (backups) y T7.9 (documentación final).

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
sudo -u cvweb /opt/cvweb/venv/bin/pip install -r /opt/cvweb/repo/backend/requirements.lock
sudo -u cvweb bash -c 'cd /opt/cvweb/repo/frontend && npm ci && npm run build'

# Secretos (nunca en git)
sudo cp /opt/cvweb/repo/backend/.env.example /opt/cvweb/.env
sudo chown cvweb:cvweb /opt/cvweb/.env
sudo chmod 600 /opt/cvweb/.env
sudo -u cvweb nano /opt/cvweb/.env      # rellenar claves y RAFA_CONTEXT_PATH

# Contexto privado (fuera del repo, ver docs/adr/0006)
sudo -u cvweb scp usuario@origen:/ruta/rafa_context.txt /opt/cvweb/data/rafa_context.txt
sudo -u cvweb chmod 600 /opt/cvweb/data/rafa_context.txt
# y en /opt/cvweb/.env: RAFA_CONTEXT_PATH=/opt/cvweb/data/rafa_context.txt

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

# Actualizar (provisional; T7.4 introducirá releases + rollback)
sudo -u cvweb bash -c 'cd /opt/cvweb/repo && git pull --ff-only'
sudo -u cvweb /opt/cvweb/venv/bin/pip install -r /opt/cvweb/repo/backend/requirements.lock
sudo -u cvweb bash -c 'cd /opt/cvweb/repo/frontend && npm ci && npm run build'
sudo systemctl restart cvweb
curl -fsS http://127.0.0.1:8000/api/health

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
- T7.4: despliegue por releases con rollback automático.
- T7.5: exposición definitiva (dominio, CGNAT, Cloudflare Tunnel…) en ADR-0005.
- T7.6: métricas Prometheus, health profundo y alertas.
- T7.7: backups (`.env` cifrado, `feedback.db`, outbox) y simulacro de restauración.
