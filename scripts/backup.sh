#!/bin/bash
# Automated Database Backup Script for Lumo AI Quantitative Platform

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="./backups"
mkdir -p $BACKUP_DIR

echo "Starting automated database backup at $TIMESTAMP..."

if [ -f "lumo_trading.db" ]; then
    cp lumo_trading.db "$BACKUP_DIR/lumo_sqlite_backup_$TIMESTAMP.db"
    echo " [SUCCESS] SQLite backup created: $BACKUP_DIR/lumo_sqlite_backup_$TIMESTAMP.db"
fi

if command -v pg_dump &> /dev/null; then
    pg_dump -h localhost -U lumo_admin lumo_trading_prod > "$BACKUP_DIR/lumo_postgres_backup_$TIMESTAMP.sql"
    echo " [SUCCESS] PostgreSQL backup created: $BACKUP_DIR/lumo_postgres_backup_$TIMESTAMP.sql"
fi

find $BACKUP_DIR -type f -mtime +14 -name "*.db" -exec rm {} \;
find $BACKUP_DIR -type f -mtime +14 -name "*.sql" -exec rm {} \;

echo "Database backup completed successfully."
