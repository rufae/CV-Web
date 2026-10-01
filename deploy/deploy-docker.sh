#!/usr/bin/env bash
# Despliegue Docker en el nodo HP: build + arranque + verificación.
# Uso: ./deploy/deploy-docker.sh
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ ! -f .env ]]; then
  echo "ERROR: falta .env en la raíz (copia backend/.env.example y rellénalo)." >&2
  exit 1
fi

docker compose up -d --build
docker compose ps

echo "--- Verificación ---"
curl -fsS http://127.0.0.1:8086/api/health
echo
curl -fsS http://127.0.0.1:8086/api/status
echo
