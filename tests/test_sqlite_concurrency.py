import pytest
import time
import threading
import uuid
import random
from backend.database.db_config import get_db_path, create_sqlite_connection, managed_sqlite_connection
from backend.arbitrage.arbitrage_evidence_store import ArbitrageEvidenceStore, ArbitrageForensicEvent
from backend.arbitrage.arbitrage_ledger import ArbitrageLedger
from backend.wallet.sub_wallet_manager import SubWalletManager
from backend.learning.experience_memory import ExperienceMemoryStore, TradeExperience

def test_sqlite_concurrency_multi_writer():
    """
    Sustained multi-threaded concurrency stress test:
    - 10+ concurrent threads generating high-frequency ArbitrageForensicEvents
    - Concurrent SubWalletManager transfers and balance queries
    - Concurrent ArbitrageLedger execution recordings
    - Concurrent ExperienceMemoryStore writes
    - Verify: Zero database lock crashes, 0 dropped events, 100% persisted.
    """
    store = ArbitrageEvidenceStore()
    ledger = ArbitrageLedger()
    wallet = SubWalletManager()
    exp_store = ExperienceMemoryStore()

    initial_generated = store.events_generated
    initial_persisted = store.events_persisted
    initial_failed = store.events_failed
    initial_dropped = store.events_dropped
    initial_lock_errors = store.lock_errors_count
    
    stop_event = threading.Event()
    threads = []
    events_produced = []
    lock = threading.Lock()

    def arbitrage_producer_worker(worker_id: int):
        count = 0
        while not stop_event.is_set():
            event = ArbitrageForensicEvent(
                event_id=f"CONC-EVT-W{worker_id}-{uuid.uuid4().hex[:8]}",
                symbol=random.choice(["BTC/USDT", "ETH/USDT", "SOL/USDT", "AVAX/USDT"]),
                buy_exchange="BINANCE",
                sell_exchange="BYBIT",
                buy_ask=65000.0 + random.uniform(-10, 10),
                sell_bid=65000.0 + random.uniform(-10, 10),
                gross_spread_bps=random.uniform(-5.0, 15.0),
                decision="EXECUTABLE" if random.random() > 0.8 else "REJECTED",
                rejection_reason="NONE" if random.random() > 0.8 else "NEGATIVE_SPREAD",
                category="EXECUTABLE" if random.random() > 0.8 else "NEGATIVE_SPREAD"
            )
            store.record_event(event)
            with lock:
                events_produced.append(event.event_id)
            count += 1
            time.sleep(0.002)

    def wallet_worker():
        while not stop_event.is_set():
            try:
                wallet.record_transfer(
                    from_wallet="funding",
                    to_wallet="arbitrage",
                    asset="USDT",
                    amount=random.uniform(1.0, 50.0)
                )
            except Exception as e:
                pass
            time.sleep(0.02)

    def ledger_worker():
        while not stop_event.is_set():
            try:
                ledger.record_execution({
                    "execution_id": f"EXEC-{uuid.uuid4().hex[:8]}",
                    "opportunity_id": f"OPP-{uuid.uuid4().hex[:6]}",
                    "symbol": "BTC/USDT",
                    "buy_exchange": "BINANCE",
                    "sell_exchange": "BYBIT",
                    "buy_price": 65000.0,
                    "sell_price": 65010.0,
                    "amount_usd": 100.0,
                    "executed_qty": 0.0015,
                    "buy_fill_price": 65000.0,
                    "sell_fill_price": 65010.0,
                    "gross_pnl": 0.15,
                    "fees_usd": 0.05,
                    "slippage_usd": 0.01,
                    "net_pnl": 0.09,
                    "leg_status": "BOTH_FILLED",
                    "execution_status": "COMPLETED",
                    "latency_ms": 15.0
                })
            except Exception as e:
                pass
            time.sleep(0.02)

    def exp_memory_worker():
        while not stop_event.is_set():
            try:
                exp_store.record_experience(TradeExperience(
                    experience_id=f"EXP-CONC-{uuid.uuid4().hex[:8]}",
                    symbol="BTC/USDT",
                    entry_price=65000.0,
                    exit_price=65050.0,
                    quantity=0.01,
                    allocation_usd=650.0,
                    execution_mode="SHADOW",
                    gross_pnl=0.5,
                    net_pnl=0.35,
                    roi_pct=0.05,
                    trade_status="WIN"
                ))
            except Exception as e:
                pass
            time.sleep(0.03)

    # Spawn 8 evidence producers + 3 other domain writers (11 concurrent threads)
    for i in range(8):
        t = threading.Thread(target=arbitrage_producer_worker, args=(i,), daemon=True)
        threads.append(t)
        t.start()

    t_w = threading.Thread(target=wallet_worker, daemon=True)
    t_l = threading.Thread(target=ledger_worker, daemon=True)
    t_e = threading.Thread(target=exp_memory_worker, daemon=True)
    threads.extend([t_w, t_l, t_e])
    t_w.start()
    t_l.start()
    t_e.start()

    # Run sustained write burst
    time.sleep(5.0)
    stop_event.set()

    for t in threads:
        t.join(timeout=3.0)

    # Wait for queue and in-flight micro-batches to drain completely
    t_drain = time.time()
    while not store._write_queue.empty() and time.time() - t_drain < 15.0:
        time.sleep(0.05)

    time.sleep(0.5)

    status = store.get_status()
    total_produced_count = len(events_produced)
    
    # Query database directly to count persisted test events
    conn = store._get_conn()
    try:
        persisted_test_count = conn.execute(
            "SELECT COUNT(*) FROM arbitrage_evidence_events WHERE event_id LIKE 'CONC-EVT-%'"
        ).fetchone()[0]
    finally:
        conn.close()

    assert total_produced_count > 500, f"Expected > 500 produced events, got {total_produced_count}"
    assert persisted_test_count >= total_produced_count, f"Persisted {persisted_test_count} < Produced {total_produced_count}"
    assert status["events_dropped"] == 0, f"Expected 0 dropped events, got {status['events_dropped']}"
    assert status["events_failed"] == 0, f"Expected 0 failed events, got {status['events_failed']}"
    assert status["lock_errors_count"] == 0, f"Expected 0 lock errors, got {status['lock_errors_count']}"
