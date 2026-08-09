import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.infrastructure.postgres_migration import postgres_migration_layer

def test_postgres_migration_layer():
    sqlite_status = postgres_migration_layer.get_database_status("sqlite+aiosqlite:///lumo_trading.db")
    assert sqlite_status["engine"] == "SQLite"
    assert sqlite_status["driver"] == "aiosqlite"

    pg_status = postgres_migration_layer.get_database_status("postgresql+asyncpg://user:pass@host/db")
    assert pg_status["engine"] == "PostgreSQL"
    assert pg_status["driver"] == "asyncpg"
