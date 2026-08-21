import pytest
import time
from backend.arbitrage.arbitrage_evidence_store import ArbitrageEvidenceStore, ArbitrageForensicEvent

def test_evidence_idempotent_duplicate_insert():
    """
    Test that re-inserting the exact same event_id does not throw Primary Key violation
    and maintains database integrity without duplicates.
    """
    store = ArbitrageEvidenceStore()
    
    unique_id = f"IDEM-EVT-{int(time.time()*1000)}"
    event = ArbitrageForensicEvent(
        event_id=unique_id,
        symbol="ETH/USDT",
        buy_exchange="BINANCE",
        sell_exchange="BYBIT",
        buy_ask=3500.0,
        sell_bid=3505.0,
        gross_spread_bps=14.28,
        decision="EXECUTABLE",
        rejection_reason="NONE",
        category="EXECUTABLE"
    )

    # 1. Insert once
    batch_1 = [event]
    success_1 = store._insert_batch_with_retry(batch_1)
    assert success_1 is True

    # 2. Re-insert identical batch
    batch_2 = [event]
    success_2 = store._insert_batch_with_retry(batch_2)
    assert success_2 is True

    # 3. Check that exactly 1 row exists
    conn = store._get_conn()
    try:
        count = conn.execute("SELECT COUNT(*) FROM arbitrage_evidence_events WHERE event_id = ?", (unique_id,)).fetchone()[0]
        assert count == 1, f"Expected exactly 1 record for event_id, got {count}"
    finally:
        conn.close()
