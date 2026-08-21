import pytest
import time
import queue
from backend.arbitrage.arbitrage_evidence_store import ArbitrageEvidenceStore, ArbitrageForensicEvent

def test_evidence_restart_recovery_drain():
    """
    Test that when stop_worker is invoked on shutdown or reload,
    any in-flight queue items and fallback buffers are completely drained to disk.
    """
    store = ArbitrageEvidenceStore()

    events = [
        ArbitrageForensicEvent(
            event_id=f"RESTART-TEST-{i}-{int(time.time()*1000)}",
            symbol="SOL/USDT",
            buy_exchange="BINANCE",
            sell_exchange="BYBIT",
            decision="REJECTED",
            rejection_reason="NEGATIVE_SPREAD",
            category="NEGATIVE_SPREAD"
        )
        for i in range(25)
    ]

    for ev in events:
        store.record_event(ev)

    # Trigger stop_worker to test graceful drain
    store.stop_worker(timeout=5.0)

    # Re-verify that all 25 events are in DB
    conn = store._get_conn()
    try:
        for ev in events:
            row = conn.execute("SELECT event_id FROM arbitrage_evidence_events WHERE event_id = ?", (ev.event_id,)).fetchone()
            assert row is not None, f"Event {ev.event_id} was lost during stop_worker drain"
    finally:
        conn.close()

    # Restart worker thread for remaining tests
    store._stop_event.clear()
    import threading
    store._worker_thread = threading.Thread(
        target=store._persistence_worker,
        daemon=True,
        name="ArbitrageEvidencePersistenceWorker"
    )
    store._worker_thread.start()
