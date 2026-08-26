#!/usr/bin/env bash
# Pivot Seoul — DB genie loader (Flyway 이후 마스터·데모·마트·품질)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="$SCRIPT_DIR/data"
QUALITY_DIR="$SCRIPT_DIR/quality"
SCRIPTS_DIR="$SCRIPT_DIR/scripts"
DA_SQL_DIR="$SCRIPT_DIR/../../da/sql"

CONTAINER="${PIVOT_DB_CONTAINER:-pivotseoul-db}"
DB_USER="${POSTGRES_USER:-pivotseoul}"
DB_NAME="${POSTGRES_DB:-pivotseoul}"
DB_HOST="${PIVOT_DB_HOST:-}"

MODE="all"
for arg in "$@"; do
  case "$arg" in
    --demo-only) MODE="demo" ;;
    --reference-only) MODE="reference" ;;
    --incremental) MODE="incremental" ;;
    --mart-only) MODE="mart" ;;
    --quality) MODE="quality" ;;
    --explain) MODE="explain" ;;
    --help|-h)
      cat <<'EOF'
Usage: ./back/db/load.sh [options]

  (default)         reference + districts + demo + mart refresh + quality
  --reference-only  01_reference + 02_districts
  --demo-only       03_demo_mvp
  --incremental     reference + districts + demo + mart (skip full quality)
  --mart-only       da/sql/06_refresh_analytics_mart
  --quality         quality/run_checks.sql
  --explain         scripts/explain_analyze.sql
EOF
      exit 0
      ;;
  esac
done

run_sql() {
  local file="$1"
  echo ">> $(basename "$file")"
  if [[ -n "$DB_HOST" ]]; then
    PGPASSWORD="${POSTGRES_PASSWORD:-pivotseoul}" psql \
      -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" \
      -v ON_ERROR_STOP=1 -f "$file"
  else
    if ! docker ps --format '{{.Names}}' | grep -qx "$CONTAINER"; then
      echo "Error: container '$CONTAINER' not running. Start with: docker compose up -d db"
      echo "Or set PIVOT_DB_HOST=localhost for direct psql."
      exit 1
    fi
    docker exec -i "$CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 < "$file"
  fi
}

files=()
case "$MODE" in
  all)
    files=(
      "$DATA_DIR/01_reference.sql"
      "$DATA_DIR/02_districts.sql"
      "$DATA_DIR/03_demo_mvp.sql"
      "$DA_SQL_DIR/06_refresh_analytics_mart.sql"
      "$QUALITY_DIR/run_checks.sql"
    )
    ;;
  reference)
    files=("$DATA_DIR/01_reference.sql" "$DATA_DIR/02_districts.sql")
    ;;
  demo)
    files=("$DATA_DIR/03_demo_mvp.sql")
    ;;
  incremental)
    files=(
      "$DATA_DIR/01_reference.sql"
      "$DATA_DIR/02_districts.sql"
      "$DATA_DIR/03_demo_mvp.sql"
      "$DA_SQL_DIR/06_refresh_analytics_mart.sql"
    )
    ;;
  mart)
    files=("$DA_SQL_DIR/06_refresh_analytics_mart.sql")
    ;;
  quality)
    files=("$QUALITY_DIR/run_checks.sql")
    ;;
  explain)
    files=("$SCRIPTS_DIR/explain_analyze.sql")
    ;;
esac

echo "Pivot Seoul DB load (mode=$MODE)"
for f in "${files[@]}"; do
  [[ -f "$f" ]] || { echo "Missing: $f"; exit 1; }
  run_sql "$f"
done
echo "Done."
