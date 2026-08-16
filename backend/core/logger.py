import sys
import os
import time
import logging
from pathlib import Path
from typing import Dict, Any
from loguru import logger
from backend.core.config import settings

# Create logs directory if missing
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Remove default loguru handler
logger.remove()

# 1. Console Handler (Colorized, Human-readable)
CONSOLE_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

logger.add(
    sys.stdout,
    format=CONSOLE_FORMAT,
    level="DEBUG" if settings.DEBUG else "INFO",
    colorize=True,
    backtrace=True,
    diagnose=True
)

# 2. File Handler (JSON Structured, Rotated, Windows Process-Safe)
LOG_FILE_PATH = LOGS_DIR / "lumo_trading_{time:YYYY-MM-DD}.log"
logger.add(
    str(LOG_FILE_PATH),
    rotation="00:00",
    retention="14 days",
    compression="zip",
    serialize=True,  # Outputs structured JSON for log processors
    level="INFO",
    enqueue=True,    # Thread-safe async queueing
    catch=True,      # Suppresses Windows file-sink rotation errors gracefully
    delay=True       # Lazy file handle creation
)


# 3. Intercept Standard Python Logging Handler (for Uvicorn, FastAPI, SQLAlchemy)
class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        # Filter out low-level driver and internal cursor debug spam
        if record.name in ("asyncio", "urllib3", "aiosqlite", "sqlite3") and record.levelno < logging.INFO:
            return

        msg = record.getMessage()
        if "functools.partial" in msg or "PRAGMA main." in msg or "sqlite3.Cursor" in msg or "sqlite3.Connection" in msg:
            return

        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, msg
        )

# Intercept default logging root logger at INFO level
logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO, force=True)
for log_name in ("uvicorn", "uvicorn.access", "fastapi"):
    l = logging.getLogger(log_name)
    l.handlers = [InterceptHandler()]
    l.propagate = False

for noisy_logger in ("sqlalchemy.engine", "aiosqlite", "urllib3", "asyncio"):
    logging.getLogger(noisy_logger).setLevel(logging.WARNING)


# Specialized Quantitative Trading Logger Helpers
def log_trade(action: str, symbol: str, price: float, amount: float, pnl: float = 0.0, reason: str = ""):
    """Log quantitative trade execution events."""
    logger.info(
        f"[TRADE EXECUTION] Action: {action} | Symbol: {symbol} | Price: ${price:,.2f} | "
        f"Amount: {amount:.4f} | PnL: ${pnl:+,.2f} | Reason: {reason}"
    )

def log_signal(symbol: str, action: str, confidence: float, tech_score: float, sentiment_score: float):
    """Log AI strategy decision signal outputs."""
    logger.info(
        f"[AI SIGNAL] Symbol: {symbol} | Action: {action} | Confidence: {confidence:.1f}% | "
        f"TA Score: {tech_score:.1f} | Sentiment Score: {sentiment_score:.1f}"
    )

def log_ai_reasoning(symbol: str, reasoning: str):
    """Log explicit multi-factor AI market reasoning."""
    logger.info(f"[AI REASONING] [{symbol}] {reasoning}")

def log_execution_latency(operation: str, latency_ms: float):
    """Log execution timing latency metrics."""
    logger.debug(f"[PERFORMANCE] {operation} completed in {latency_ms:.2f} ms")

__all__ = [
    "logger",
    "log_trade",
    "log_signal",
    "log_ai_reasoning",
    "log_execution_latency"
]
