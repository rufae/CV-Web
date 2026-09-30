#!/usr/bin/env bash
# Despliegue básico en el nodo HP (T1.9).
# T7.4 lo sustituirá por un despliegue por releases con rollback automático.
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/cvweb}"
REPO_DIR="$APP_DIR/repo"
VENV="$APP_DIR/venv"

cd "$REPO_DIR"

echo "==> Actualizando código"
git pull --ff-only

echo "==> Dependencias backend"
"$VENV/bin/pip" install --require-hashes -r backend/requirements.lock

echo "==> Build del frontend"
(cd frontend && npm ci && npm run build)

echo "==> Reiniciando servicio"
sudo systemctl restart cvweb

echo "==> Comprobando salud"
for _ in $(seq 1 10); do
  if curl -fsS http://127.0.0.1:8000/api/health >/dev/null; then
    echo "OK: servicio saludable"
    exit 0
  fi
  sleep 1
done

echo "ERROR: el servicio no responde a /api/health" >&2
exit 1
