#!/usr/bin/env bash
# TRPM-LIMS backup restore drill.
# Restores the latest backup into a throwaway database, verifies, then drops it.
# Exit code 0 = drill passed; 1 = failure.
#
# Usage: ./scripts/restore_drill.sh

set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/backups}"
DB_HOST="${POSTGRES_HOST:-db}"
DB_PORT="${POSTGRES_PORT:-5432}"
DB_USER="${POSTGRES_USER:-lims}"
DB_NAME="${POSTGRES_DB:-trpm_lims}"
DRILL_DB="${DB_NAME}_restore_drill"

LATEST=$(ls -t "${BACKUP_DIR}/${DB_NAME}_"*.sql.gz 2>/dev/null | head -1)
if [ -z "$LATEST" ]; then
    echo "ERROR: No backup files found in $BACKUP_DIR"
    exit 1
fi

echo "[$(date)] Restore drill using: $LATEST"

# Create throwaway database
echo "[$(date)] Creating temporary database: $DRILL_DB"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres \
    -c "DROP DATABASE IF EXISTS \"$DRILL_DB\";" \
    -c "CREATE DATABASE \"$DRILL_DB\";"

# Restore
echo "[$(date)] Restoring..."
gunzip -c "$LATEST" | pg_restore -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" \
    -d "$DRILL_DB" --no-owner --no-privileges || true

# Verify — run a basic query
echo "[$(date)] Verifying restore..."
TABLE_COUNT=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DRILL_DB" \
    -t -A -c "SELECT count(*) FROM information_schema.tables WHERE table_schema='public';")

if [ "$TABLE_COUNT" -lt 10 ]; then
    echo "ERROR: Only ${TABLE_COUNT} tables found — restore may be incomplete."
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres \
        -c "DROP DATABASE IF EXISTS \"$DRILL_DB\";"
    exit 1
fi

echo "[$(date)] Restore verified: ${TABLE_COUNT} tables in restored database."

# Cleanup
echo "[$(date)] Dropping temporary database..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres \
    -c "DROP DATABASE IF EXISTS \"$DRILL_DB\";"

echo "[$(date)] Restore drill PASSED."
