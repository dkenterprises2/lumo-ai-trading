import pytest
import time
import sqlite3
import threading
from backend.arbitrage.arbitrage_evidence_store import ArbitrageEvidenceStore, ArbitrageForensicEvent
from backend.database.db_config import create_sqlite_connection

def test_evidence_retry_under_artificial_lock():
    """
    Test that ArbitrageEvidenceStore retries with backoff and persists successfully
    even when another process/thread temporarily holds an EXCLUSIVE lock on SQLite.
    """
    store = ArbitrageEvidenceStore()
    
    # Create an artificial external lock for 1.5 seconds
    lock_active = threading.Event()
    lock_released = threading.Event()

    def lock_holder():
        conn = create_sqlite_connection(store.db_path, timeout=5.0, isolation_level=None)
        try:
            conn.execute("BEGIN EXCLUSIVE;")
            lock_active.set()
            time.sleep(1.0)
            conn.execute("COMMIT;")
        finally:
            conn.close()
            lock_released.set()

    t_lock = threading.Thread(target=lock_holder, daemon=True)
    t_lock.start()
    
    lock_active.wait(timeout=5.0)

    # Now attempt to insert a batch while the database is locked
    test_event = ArbitrageForensicEvent(
        event_id=f"RETRY-TEST-{int(time.time()*1000)}",
        symbol="BTC/USDT",
        buy_exchange="BINANCE",
        sell_exchange="BYBIT",
        decision="REJECTED",
        rejection_reason="NEGATIVE_SPREAD",
        category="NEGATIVE_SPREAD"
    )

    batch = [test_event]
    success = store._insert_batch_with_retry(batch)
    
    assert success is True, "Expected _insert_batch_with_retry to succeed after lock release"
    
    # Query database to confirm row exists
    persisted_event = store.get_event_by_id(test_event.event_id)
    assert persisted_event is not None
    assert persisted_event["event_id"] == test_event.event_id
