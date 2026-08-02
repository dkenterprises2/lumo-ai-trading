import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from backend.core.config import settings
from backend.core.logger import logger

# Base Declarative Model
Base = declarative_base()

# Configure Async Database Engine
ASYNC_DB_URL = settings.ASYNC_DATABASE_URL

# SQLite vs PostgreSQL async pool handling
connect_args = {"check_same_thread": False} if "sqlite" in ASYNC_DB_URL else {}

async_engine = create_async_engine(
    ASYNC_DB_URL,
    echo=False,
    connect_args=connect_args,
    future=True
)

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
            await session.commit()
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
            # Import models inside function to register metadata
            import backend.models.domain  # noqa: F401
            await conn.run_sync(Base.metadata.create_all)

            # Auto-migrate missing columns for Trades table
            def migrate_trades(sync_conn):
                from sqlalchemy import inspect, text
                inspector = inspect(sync_conn)
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

            await conn.run_sync(migrate_trades)

        logger.info("Database schema initialized/verified successfully.")
    except Exception as e:
        logger.error(f"Error initializing database schema: {e}")


__all__ = ["Base", "async_engine", "AsyncSessionLocal", "get_db_session", "init_db"]
