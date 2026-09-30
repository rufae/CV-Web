#!/usr/bin/env bash
# Despliegue por releases con rollback automático (T7.4).
# Uso: deploy.sh [ref]   (ref por defecto: origin/main)
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/cvweb}"
REPO_DIR="$APP_DIR/repo"
RELEASES_DIR="$APP_DIR/releases"
VENV="$APP_DIR/venv"
KEEP_RELEASES=3
REF="${1:-origin/main}"

cd "$REPO_DIR"
git fetch --all --tags --prune
SHA="$(git rev-parse "$REF")"
RELEASE_DIR="$RELEASES_DIR/$(date -u +%Y%m%d%H%M%S)-${SHA:0:7}"
mkdir -p "$RELEASE_DIR"
git archive "$SHA" | tar -x -C "$RELEASE_DIR"

echo "==> Dependencias backend"
"$VENV/bin/pip" install --require-hashes -r "$RELEASE_DIR/backend/requirements.lock"

echo "==> Build del frontend"
(cd "$RELEASE_DIR/frontend" && npm ci && npm run build)

PREVIOUS="$(readlink -f "$APP_DIR/current" 2>/dev/null || true)"
echo "==> Activando release $RELEASE_DIR"
ln -sfn "$RELEASE_DIR" "$APP_DIR/current"
sudo systemctl restart cvweb

echo "==> Healthcheck"
if ! curl -fsS --retry 5 --retry-delay 1 http://127.0.0.1:8000/api/health >/dev/null; then
  echo "ERROR: healthcheck falló; rollback a ${PREVIOUS:-anterior}" >&2
  if [ -n "$PREVIOUS" ]; then
    ln -sfn "$PREVIOUS" "$APP_DIR/current"
    sudo systemctl restart cvweb
  fi
  exit 1
fi

echo "==> Limpiando releases antiguas (se conservan $KEEP_RELEASES)"
( cd "$RELEASES_DIR" && ls -1dt ./*/ | tail -n +$((KEEP_RELEASES + 1)) | xargs -r rm -rf )

echo "OK: desplegado $SHA en $RELEASE_DIR"
