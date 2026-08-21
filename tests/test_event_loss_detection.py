import pytest
import time
import random
from backend.arbitrage.arbitrage_evidence_store import ArbitrageEvidenceStore, ArbitrageForensicEvent

def test_event_loss_detection_zero_loss_invariant():
    """
    Test zero event loss invariant:
    events_generated == events_persisted + events_failed + events_dropped
    with events_dropped == 0.
    """
    store = ArbitrageEvidenceStore()

    initial_generated = store.events_generated
    initial_persisted = store.events_persisted
    initial_failed = store.events_failed
    initial_dropped = store.events_dropped

    count_to_send = 100
    for i in range(count_to_send):
        ev = ArbitrageForensicEvent(
            event_id=f"LOSS-CHK-{i}-{int(time.time()*1000)}",
            symbol="AVAX/USDT",
            buy_exchange="BINANCE",
            sell_exchange="BYBIT",
            decision="REJECTED",
            rejection_reason="NEGATIVE_SPREAD",
            category="NEGATIVE_SPREAD"
        )
        store.record_event(ev)

    # Wait for queue to flush
    t0 = time.time()
    while not store._write_queue.empty() and time.time() - t0 < 5.0:
        time.sleep(0.05)

    time.sleep(0.2)

    status = store.get_status()
    delta_generated = status["events_generated"] - initial_generated
    delta_persisted = status["events_persisted"] - initial_persisted
    delta_failed = status["events_failed"] - initial_failed
    delta_dropped = status["events_dropped"] - initial_dropped

    assert delta_dropped == 0, f"delta_dropped is {delta_dropped}, expected 0"
    assert delta_failed == 0, f"delta_failed is {delta_failed}, expected 0"
    assert delta_generated == count_to_send, f"delta_generated is {delta_generated}, expected {count_to_send}"
    assert delta_generated == delta_persisted + delta_failed + delta_dropped
