import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from backend.core.config import settings
from backend.core.logger import logger

# Base Declarative Model
Base = declarative_base()

# Explicitly register domain models onto Base metadata
import backend.models.domain  # noqa: F401


raw_db_url = os.getenv("DATABASE_URL", os.getenv("ASYNC_DATABASE_URL", settings.ASYNC_DATABASE_URL))
if raw_db_url.startswith("postgres://"):
    ASYNC_DB_URL = raw_db_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif raw_db_url.startswith("postgresql://") and not raw_db_url.startswith("postgresql+asyncpg://"):
    ASYNC_DB_URL = raw_db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
else:
    ASYNC_DB_URL = raw_db_url

from sqlalchemy import event

is_sqlite = "sqlite" in ASYNC_DB_URL
connect_args = {"check_same_thread": False, "timeout": 30.0} if is_sqlite else {}

engine_kwargs = {
    "echo": False,
    "future": True,
    "connect_args": connect_args
}

if not is_sqlite:
    engine_kwargs.update({
        "pool_size": getattr(settings, "DB_POOL_SIZE", 10),
        "max_overflow": getattr(settings, "DB_MAX_OVERFLOW", 20),
        "pool_recycle": 1800,
        "pool_pre_ping": True
    })

async_engine = create_async_engine(
    ASYNC_DB_URL,
    **engine_kwargs
)


@event.listens_for(async_engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    try:
        conn = getattr(dbapi_connection, "_conn", dbapi_connection)
        if hasattr(conn, "cursor"):
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA busy_timeout=30000")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.close()
    except Exception as e:
        logger.warning(f"Failed to set SQLite PRAGMAs: {e}")



AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency helper to yield async database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


_db_initialized = False

async def init_db():
    """Initialize database tables once without dropping existing data."""
    global _db_initialized
    if _db_initialized:
        return

    try:
        async with async_engine.begin() as conn:
            def create_tables(sync_conn):
                import backend.models.domain  # noqa: F401
                Base.metadata.create_all(sync_conn)

            await conn.run_sync(create_tables)

            # Auto-migrate missing columns across all domain tables
            def auto_migrate_schema(sync_conn):
                from sqlalchemy import inspect, text
                inspector = inspect(sync_conn)
                
                if inspector.has_table("users"):
                    user_cols = [c["name"] for c in inspector.get_columns("users")]
                    user_new_cols = [
                        ("name", "VARCHAR(128) DEFAULT 'Trader User'"),
                        ("avatar", "TEXT DEFAULT 'https://api.dicebear.com/7.x/avataaars/svg?seed=LumoTrader'"),
                        ("currency", "VARCHAR(16) DEFAULT 'USD'"),
                        ("timezone", "VARCHAR(64) DEFAULT 'UTC'"),
                        ("trading_mode", "VARCHAR(32) DEFAULT 'Paper'"),
                        ("failed_login_attempts", "INTEGER DEFAULT 0"),
                        ("locked_until", "DATETIME NULL"),
                        ("updated_at", "DATETIME NULL")
                    ]
                    for col_name, col_type in user_new_cols:
                        if col_name not in user_cols:
                            sync_conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"))

                if inspector.has_table("portfolio"):
                    port_cols = [c["name"] for c in inspector.get_columns("portfolio")]
                    if "default_allocation_usd" not in port_cols:
                        sync_conn.execute(text("ALTER TABLE portfolio ADD COLUMN default_allocation_usd FLOAT DEFAULT 1000.0"))
                    if "default_leverage" not in port_cols:
                        sync_conn.execute(text("ALTER TABLE portfolio ADD COLUMN default_leverage INTEGER DEFAULT 1"))

                user_id_tables = ["portfolio", "positions", "trades", "orders", "equity_history", "wallet_transactions", "performance", "audit_logs", "settings"]
                for tbl in user_id_tables:
                    if inspector.has_table(tbl):
                        cols = [c["name"] for c in inspector.get_columns(tbl)]
                        if "user_id" not in cols:
                            sync_conn.execute(text(f"ALTER TABLE {tbl} ADD COLUMN user_id INTEGER"))

                if inspector.has_table("trades"):
                    columns = [c["name"] for c in inspector.get_columns("trades")]
                    new_cols = [
                        ("strategy", "VARCHAR(64) DEFAULT 'AI Hybrid'"),
                        ("confidence", "FLOAT DEFAULT 75.0"),
                        ("reason", "TEXT DEFAULT ''"),
                        ("exchange", "VARCHAR(64) DEFAULT 'PAPER_EXCHANGE'"),
                        ("order_id", "VARCHAR(128) DEFAULT ''"),
                        ("entry_fee", "FLOAT DEFAULT 0.0"),
                        ("exit_fee", "FLOAT DEFAULT 0.0"),
                        ("funding_fee", "FLOAT DEFAULT 0.0"),
                        ("slippage", "FLOAT DEFAULT 0.0"),
                        ("latency", "FLOAT DEFAULT 0.0")
                    ]
                    for col_name, col_type in new_cols:
                        if col_name not in columns:
                            sync_conn.execute(text(f"ALTER TABLE trades ADD COLUMN {col_name} {col_type}"))

            await conn.run_sync(auto_migrate_schema)

        _db_initialized = True
        logger.info("Database schema initialized/verified successfully.")
    except Exception as e:
        import traceback
        logger.error(f"Error initializing database schema: {e}\n{traceback.format_exc()}")



__all__ = ["Base", "async_engine", "AsyncSessionLocal", "get_db_session", "init_db"]
