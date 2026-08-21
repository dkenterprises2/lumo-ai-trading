import os
import time
import random
import sqlite3
import threading
from contextlib import contextmanager
from typing import Dict, Any, Optional, List, Callable, TypeVar
from loguru import logger

T = TypeVar("T")

# Absolute canonical database path
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "lumo_trading.db"))

class SQLiteTransactionTracker:
    """Diagnostic registry tracking active SQLite transactions and concurrency metrics across threads/tasks."""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SQLiteTransactionTracker, cls).__new__(cls)
                cls._instance._active_writers: Dict[int, Dict[str, Any]] = {}
                cls._instance._write_latencies: List[float] = []
                cls._instance.db_write_success = 0
                cls._instance.db_write_retry = 0
                cls._instance.db_write_failure = 0
                cls._instance.db_lock_events = 0
                cls._instance.last_successful_write_utc = "None"
                cls._instance.last_lock_event_utc = "None"
                cls._instance.last_lock_writer = "None"
            return cls._instance

    def register_start(self, conn_id: int, writer_name: str, table_or_query: str):
        with self._lock:
            now = time.time()
            self._active_writers[conn_id] = {
                "writer_name": writer_name,
                "table_or_query": table_or_query[:60],
                "thread_name": threading.current_thread().name,
                "thread_id": threading.get_ident(),
                "timestamp_start": now,
                "db_path": DB_PATH
            }

    def register_end(self, conn_id: int, success: bool = True):
        with self._lock:
            dur_ms = 0.0
            if conn_id in self._active_writers:
                rec = self._active_writers.pop(conn_id)
                dur_ms = (time.time() - rec["timestamp_start"]) * 1000.0
                self._write_latencies.append(dur_ms)
                if len(self._write_latencies) > 2000:
                    self._write_latencies.pop(0)
            if success:
                self.db_write_success += 1
                self.last_successful_write_utc = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
            return dur_ms

    def get_latency_percentiles(self) -> Dict[str, float]:
        with self._lock:
            if not self._write_latencies:
                return {"p50_ms": 0.0, "p95_ms": 0.0, "p99_ms": 0.0, "count": 0}
            s = sorted(self._write_latencies)
            n = len(s)
            p50 = s[int(n * 0.50)]
            p95 = s[min(n - 1, int(n * 0.95))]
            p99 = s[min(n - 1, int(n * 0.99))]
            return {
                "p50_ms": round(p50, 2),
                "p95_ms": round(p95, 2),
                "p99_ms": round(p99, 2),
                "count": n
            }

    def get_active_writers(self) -> List[Dict[str, Any]]:
        with self._lock:
            now = time.time()
            res = []
            for cid, info in self._active_writers.items():
                item = dict(info)
                item["conn_id"] = cid
                item["elapsed_ms"] = round((now - info["timestamp_start"]) * 1000.0, 2)
                res.append(item)
            return res

    def record_conflict(self, requesting_writer: str) -> List[Dict[str, Any]]:
        with self._lock:
            self.db_lock_events += 1
            self.db_write_retry += 1
            self.last_lock_event_utc = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
            self.last_lock_writer = requesting_writer
            other_writers = [dict(w) for w in self._active_writers.values()]
        return other_writers

    def record_failure(self):
        with self._lock:
            self.db_write_failure += 1

transaction_tracker = SQLiteTransactionTracker()

def get_db_path() -> str:
    """Returns the single authoritative absolute SQLite database path."""
    return DB_PATH

def create_sqlite_connection(
    db_path: Optional[str] = None,
    timeout: float = 60.0,
    read_only: bool = False,
    isolation_level: Optional[str] = None
) -> sqlite3.Connection:
    """
    Creates a high-performance SQLite connection enforcing WAL mode, 60s busy timeout,
    and institutional concurrency pragmas.
    """
    target_path = db_path or DB_PATH
    if read_only:
        norm_path = target_path.replace("\\", "/")
        uri_path = f"file:{norm_path}?mode=ro"
        conn = sqlite3.connect(uri_path, uri=True, timeout=timeout, check_same_thread=False)
    else:
        conn = sqlite3.connect(
            target_path,
            timeout=timeout,
            check_same_thread=False,
            isolation_level=isolation_level
        )

    conn.row_factory = sqlite3.Row
    try:
        if not read_only:
            conn.execute("PRAGMA journal_mode = WAL;")
            conn.execute("PRAGMA synchronous = NORMAL;")
        conn.execute("PRAGMA mmap_size = 268435456;")  # 256MB memory map
        conn.execute("PRAGMA cache_size = -64000;")  # 64MB RAM page cache
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA busy_timeout = 60000;")
        conn.execute("PRAGMA temp_store = MEMORY;")
        conn.execute("PRAGMA cache_size = -64000;")
    except Exception as e:
        logger.debug(f"[SQLitePragmaInit] Non-critical pragma notice: {e}")

    return conn

@contextmanager
def managed_sqlite_connection(
    writer_name: str = "AnonymousWriter",
    table_or_query: str = "General",
    timeout: float = 60.0,
    db_path: Optional[str] = None,
    isolation_level: Optional[str] = None
):
    """
    Context manager yielding a tracked, auto-closing SQLite connection with micro-transaction timing.
    """
    conn = create_sqlite_connection(
        db_path=db_path,
        timeout=timeout,
        isolation_level=isolation_level
    )
    conn_id = id(conn)
    transaction_tracker.register_start(conn_id, writer_name, table_or_query)
    is_success = False
    try:
        yield conn
        is_success = True
    except sqlite3.OperationalError as op_err:
        err_str = str(op_err).lower()
        if "locked" in err_str or "busy" in err_str:
            active = transaction_tracker.record_conflict(writer_name)
            logger.warning(
                f"[SQLiteLockContention] Writer '{writer_name}' encountered lock on '{table_or_query}'. "
                f"Active conflicting writers: {active}"
            )
        raise
    finally:
        transaction_tracker.register_end(conn_id, success=is_success)
        try:
            conn.close()
        except Exception:
            pass

def execute_write_with_retry(
    operation: Callable[[sqlite3.Connection], T],
    writer_name: str = "AnonymousWriter",
    table_or_query: str = "GeneralWrite",
    max_retries: int = 10,
    initial_delay: float = 0.05,
    max_delay: float = 2.0,
    db_path: Optional[str] = None
) -> T:
    """
    Executes a database write transaction with bounded exponential backoff + jitter retries.
    Guarantees no infinite loops, explicit error logging, and telemetry counter tracking.
    """
    target_path = db_path or DB_PATH
    last_err = None

    for attempt in range(1, max_retries + 1):
        conn = None
        conn_id = None
        try:
            conn = create_sqlite_connection(target_path, timeout=60.0)
            conn_id = id(conn)
            transaction_tracker.register_start(conn_id, writer_name, table_or_query)
            
            result = operation(conn)
            conn.commit()
            transaction_tracker.register_end(conn_id, success=True)
            return result
        except sqlite3.OperationalError as op_err:
            last_err = op_err
            err_msg = str(op_err).lower()
            if conn_id is not None:
                transaction_tracker.register_end(conn_id, success=False)
            if "locked" in err_msg or "busy" in err_msg:
                transaction_tracker.record_conflict(writer_name)
                delay = min(max_delay, initial_delay * (1.6 ** attempt)) + random.uniform(0.01, 0.05)
                logger.debug(
                    f"[SQLiteRetry] Writer '{writer_name}' lock on '{table_or_query}'. "
                    f"Attempt {attempt}/{max_retries}. Backoff {delay:.3f}s..."
                )
                time.sleep(delay)
            else:
                logger.error(f"[SQLiteWriteError] Operational error in '{writer_name}' on '{table_or_query}': {op_err}")
                raise
        except Exception as ex:
            last_err = ex
            if conn_id is not None:
                transaction_tracker.register_end(conn_id, success=False)
            logger.error(f"[SQLiteWriteError] Unexpected error in '{writer_name}' on '{table_or_query}': {ex}")
            raise
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

    transaction_tracker.record_failure()
    logger.error(
        f"[SQLiteWriteExhausted] Writer '{writer_name}' failed to execute on '{table_or_query}' "
        f"after {max_retries} attempts. Last error: {last_err}"
    )
    raise last_err

def get_database_diagnostics() -> Dict[str, Any]:
    """
    Returns non-sensitive real-time database concurrency, health, and lock metrics.
    """
    tracker = transaction_tracker
    active = tracker.get_active_writers()
    journal_mode = "unknown"
    busy_timeout_ms = 0
    try:
        with managed_sqlite_connection("DiagnosticsReader", "PRAGMA", timeout=5.0) as c:
            j_row = c.execute("PRAGMA journal_mode;").fetchone()
            if j_row:
                journal_mode = str(j_row[0])
            b_row = c.execute("PRAGMA busy_timeout;").fetchone()
            if b_row:
                busy_timeout_ms = int(b_row[0])
    except Exception as ex:
        logger.debug(f"[DiagnosticsReader] Notice reading pragmas: {ex}")

    file_size_bytes = 0
    try:
        if os.path.exists(DB_PATH):
            file_size_bytes = os.path.getsize(DB_PATH)
    except Exception:
        pass

    return {
        "status": "healthy" if tracker.db_write_failure == 0 else "degraded",
        "database_file": os.path.basename(DB_PATH),
        "file_size_kb": round(file_size_bytes / 1024.0, 2),
        "journal_mode": journal_mode.upper(),
        "is_wal_enabled": journal_mode.upper() == "WAL",
        "busy_timeout_ms": busy_timeout_ms,
        "concurrency": {
            "active_writers_count": len(active),
            "active_writers": active,
            "write_latency_percentiles": tracker.get_latency_percentiles(),
            "db_write_success": tracker.db_write_success,
            "db_write_retry": tracker.db_write_retry,
            "db_write_failure": tracker.db_write_failure,
            "db_lock_events": tracker.db_lock_events,
            "last_successful_write_utc": tracker.last_successful_write_utc,
            "last_lock_event_utc": tracker.last_lock_event_utc,
            "last_lock_writer": tracker.last_lock_writer
        }
    }
