#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONTAINER="${PIVOT_DB_CONTAINER:-pivotseoul-db}"
DB_USER="${POSTGRES_USER:-pivotseoul}"
DB_NAME="${POSTGRES_DB:-pivotseoul}"
DB_HOST="${PIVOT_DB_HOST:-}"

SQL="$SCRIPT_DIR/data/00_reset_demo.sql"

run() {
  if [[ -n "$DB_HOST" ]]; then
    PGPASSWORD="${POSTGRES_PASSWORD:-pivotseoul}" psql \
      -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 -f "$SQL"
  else
    docker exec -i "$CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 < "$SQL"
  fi
}

echo "Resetting demo data (session_uuid LIKE demo-%)..."
run
echo "Done."
