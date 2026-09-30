#!/usr/bin/env bash
# Copia de seguridad de CV Web (T7.7). NO incluye Chroma (se reconstruye con la ingesta).
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/cvweb}"
DEST_DIR="${DEST_DIR:-$APP_DIR/backups}"
STAMP="$(date -u +%Y%m%d)"
ARCHIVE="$DEST_DIR/cvweb-$STAMP.tar.gz"

mkdir -p "$DEST_DIR"
cd "$APP_DIR"

tar czf "$ARCHIVE" \
  --warning=no-file-changed \
  .env \
  data/contact_outbox.db \
  data/feedback.db \
  data/ingest_manifest.json \
  repo/deploy 2>/dev/null || true

chmod 600 "$ARCHIVE"
echo "Backup en $ARCHIVE"
echo "Recuerda: el .env contiene secretos; guárdalo cifrado fuera del nodo."
