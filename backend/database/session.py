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


# Configure Async Database Engine
ASYNC_DB_URL = settings.ASYNC_DATABASE_URL

from sqlalchemy import event

connect_args = {"check_same_thread": False, "timeout": 30.0} if "sqlite" in ASYNC_DB_URL else {}

async_engine = create_async_engine(
    ASYNC_DB_URL,
    echo=False,
    connect_args=connect_args,
    future=True
)

@event.listens_for(async_engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    try:
        cursor = dbapi_connection.cursor()
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


async def init_db():
    """Initialize database tables without dropping existing data."""
    try:
        async with async_engine.begin() as conn:
            def create_tables(sync_conn):
                import backend.models.domain  # noqa: F401
                for mod_name in [
                    "backend.models.journal", "backend.models.exchange", "backend.models.strategy",
                    "backend.models.analytics", "backend.models.ml", "backend.models.research",
                    "backend.models.live_execution", "backend.models.observability", "backend.models.mlops",
                    "backend.models.saas", "backend.models.compliance", "backend.models.execution_algos",
                    "backend.models.marketdata", "backend.models.ai_agents", "backend.models.multiasset",
                    "backend.models.saas_enterprise", "backend.models.platform_infra",
                    "backend.models.quant_research_platform", "backend.models.alpha_factory_platform",
                    "backend.models.execution_network_platform", "backend.models.ai_copilot_platform"
                ]:
                    try:
                        __import__(mod_name)
                    except Exception:
                        pass

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
                        ("avatar", "VARCHAR(256) DEFAULT 'https://api.dicebear.com/7.x/avataaars/svg?seed=LumoTrader'"),
                        ("timezone", "VARCHAR(64) DEFAULT 'UTC'"),
                        ("trading_mode", "VARCHAR(32) DEFAULT 'Paper'"),
                        ("failed_login_attempts", "INTEGER DEFAULT 0"),
                        ("locked_until", "DATETIME NULL"),
                        ("updated_at", "DATETIME NULL")
                    ]
                    for col_name, col_type in user_new_cols:
                        if col_name not in user_cols:
                            sync_conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"))

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


        logger.info("Database schema initialized/verified successfully.")
    except Exception as e:
        import traceback
        logger.error(f"Error initializing database schema: {e}\n{traceback.format_exc()}")



__all__ = ["Base", "async_engine", "AsyncSessionLocal", "get_db_session", "init_db"]
