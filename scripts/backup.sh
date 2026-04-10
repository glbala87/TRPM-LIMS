#!/usr/bin/env bash
# TRPM-LIMS PostgreSQL backup script.
# Designed to be run daily by cron or the backup Docker service.
#
# Usage: ./scripts/backup.sh
# Env vars: POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, PGPASSWORD
# Outputs gzipped dump to $BACKUP_DIR (default /backups).

set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/backups}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_HOST="${POSTGRES_HOST:-db}"
DB_PORT="${POSTGRES_PORT:-5432}"
DB_NAME="${POSTGRES_DB:-trpm_lims}"
DB_USER="${POSTGRES_USER:-lims}"
FILENAME="${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.sql.gz"

mkdir -p "$BACKUP_DIR"

echo "[$(date)] Starting backup of ${DB_NAME} to ${FILENAME}..."
pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
    --format=custom --compress=9 \
    -f "${FILENAME%.gz}"

gzip -f "${FILENAME%.gz}"

echo "[$(date)] Backup completed: $(du -sh "$FILENAME" | cut -f1)"

# Prune old backups
find "$BACKUP_DIR" -name "${DB_NAME}_*.sql.gz" -mtime +"$RETENTION_DAYS" -delete
REMAINING=$(find "$BACKUP_DIR" -name "${DB_NAME}_*.sql.gz" | wc -l)
echo "[$(date)] Retention: kept ${REMAINING} backups (${RETENTION_DAYS}-day policy)."
