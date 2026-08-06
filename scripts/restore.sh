#!/bin/bash
# Disaster Recovery Database Restore Script for Lumo AI Quantitative Platform

if [ -z "$1" ]; then
    echo "Usage: ./scripts/restore.sh <backup_file_path>"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file $BACKUP_FILE does not exist."
    exit 1
fi

echo "Restoring database from $BACKUP_FILE..."

if [[ "$BACKUP_FILE" == *.db ]]; then
    cp "$BACKUP_FILE" lumo_trading.db
    echo " [SUCCESS] Restored SQLite database from $BACKUP_FILE."
elif [[ "$BACKUP_FILE" == *.sql ]]; then
    psql -h localhost -U lumo_admin lumo_trading_prod < "$BACKUP_FILE"
    echo " [SUCCESS] Restored PostgreSQL database from $BACKUP_FILE."
else
    echo "Error: Unsupported backup file extension."
    exit 1
fi

echo "Database restoration completed successfully."
