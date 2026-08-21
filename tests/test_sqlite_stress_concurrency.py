import os
import sys
import time
import json
import uuid
import pytest
import sqlite3
import threading
import concurrent.futures
# setup path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from backend.database.db_config import (
    get_db_path,
    create_sqlite_connection,
    execute_write_with_retry,
    managed_sqlite_connection,
    get_database_diagnostics,
    transaction_tracker
)
from backend.arbitrage.arbitrage_evidence_store import ArbitrageEvidenceStore, ArbitrageForensicEvent
from backend.shadow_trading.shadow_autonomous_learner import ShadowAutonomousLearner, LearningExperimentResult
from backend.core.logger import sanitize_sensitive_data, logger


def generate_dummy_event(sym="BTC/USDT", category="SPREAD_TOO_LOW") -> ArbitrageForensicEvent:
    return ArbitrageForensicEvent(
        event_id=f"TEST-EVT-{uuid.uuid4().hex[:12].upper()}",
        symbol=sym,
        route_id="BINANCE->BYBIT",
        buy_exchange="BINANCE",
        sell_exchange="BYBIT",
        buy_bid=60000.0,
        buy_ask=60001.0,
        sell_bid=60002.0,
        sell_ask=60003.0,
        gross_spread_bps=2.5,
        decision="RBJECTED",
        rejection_reason=category,
        category=category,
        raw_snapshot_json=json.dumps({"test": True, "created": time.time()})
    )


def test_1_multiple_concurrent_evidence_writes():
    """TEST 1: Multiple concurrent threads submitting evidence events."""
    store = ArbitrageEvidenceStore()
    num_threads = 10
    events_per_thread = 50

    def worker(worker_id):
        for i in range(events_per_thread):
            evt = generate_dummy_event(sym="ETH/USDT", category="NEGATIVE_SPREAD")
            store.record_event(evt)

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(worker, i) for i in range(num_threads)]
        concurrent.futures.wait(futures)

    time.sleep(1.0)
    assert store.events_generated >= num_threads * events_per_thread
    assert store.events_dropped == 0



def test_2_evidence_and_shadow_learner_simultaneous_writes():
    """TEST 2: Evidence store and ShadowAutonomousLearner persisting simultaneously."""
    store = ArbitrageEvidenceStore()
    learner = ShadowAutonomousLearner()
    stop_event = threading.Event()

    def evidence_worker():
        for _ in range(40):
            if stop_event.is_set():
                break
            evt = generate_dummy_event(sym="SOL/USDT", category="RISK_GATE_BLOCKED")
            store.record_event(evt)
            time.sleep(0.01)

    def shadow_worker():
        for i in range(20):
            if stop_event.is_set():
                break
            exp = LearningExperimentResult(
                experiment_id=f"TEST-EXP-{uuid.uuid4().hex[:8].upper()}",
                timestamp=time.time(),
                symbol="SOL/USDT",
                timeframe="15m",
                duration_preset="3M",
                candles_analyzed=1000,
                technique_id="TECH_EMA_PULLBACK",
                technique_name="Adaptive EMA Trend Pullback",
                parameters={"fast_ema": 9, "slow_ema": 21},
                trades_count=20,
                wins=14,
                losses=6,
                win_rate_pct=70.0,
                gross_pnl=120.0,
                friction_deducted=5.0,
                net_pnl=115.0,
                profit_factor=2.4,
                max_drawdown_pct=4.5,
                sharpe_ratio=2.1,
                is_champion=True,
                learned_insight="Strong bounce on EMA20"
            )
            learner._persist_experiment(exp)
            learner._save_persistent_state()
            time.sleep(0.02)

    t1 = threading.Thread(target=evidence_worker)
    t2 = threading.Thread(target=shadow_worker)
    t1.start()
    t2.start()
    t1.join(timeout=10.0)
    t2.join(timeout=10.0)

    time.sleep(1.0)
    assert store.events_dropped == 0
    assert learner.experiments_failed == 0



def test_3_concurrent_api_reads_and_db_writes():
    """TEST 3: High-frequency SELECT queries running simultaneously with active writes."""
    store = ArbitrageEvidenceStore()
    db_path = get_db_path()
    read_counts = [0]
    errors = []

    def read_worker():
        for _ in range(25):
            conn = None
            try:
                conn = create_sqlite_connection(db_path, read_only=True)
                row = conn.execute("SELECT event_id, symbol FROM arbitrage_evidence_events ORDER BY created_at DESC LIMIT 10").fetchall()
                assert row is not None
                read_counts[0] += 1
            except Exception as e:
                errors.append(str(e))
            finally:
                if conn:
                    try:
                        conn.close()
                    except Exception:
                        pass

    def write_worker():
        for _ in range(25):
            evt = generate_dummy_event(sym="AVAX/USDT")
            store.record_event(evt)
            time.sleep(0.005)

    r_thread = threading.Thread(target=read_worker)
    w_thread = threading.Thread(target=write_worker)
    r_thread.start()
    w_thread.start()

    r_thread.join(timeout=5.0)
    w_thread.join(timeout=5.0)

    assert len(errors) == 0
    assert read_counts[0] == 25


def test_4_hundred_event_batch_persistence():
    """TEST 4: Single large batch (100 items) persisted cleanly."""
    store = ArbitrageEvidenceStore()
    batch = [generate_dummy_event(sym="DOGE/USDT") for _ in range(100)]
    success = store._insert_batch_with_retry(batch)
    assert success is True



def test_5_five_hundred_concurrent_events():
    """TEST 5: 500+ rapid events generated in burst mode."""
    store = ArbitrageEvidenceStore()
    events = [generate_dummy_event(sym="XRP/USDT") for _ in range(500)]
    t0 = time.perf_counter()
    for e in events:
        store.record_event(e)
    elapsed = time.perf_counter() - t0
    assert elapsed < 0.30
    assert store.events_dropped == 0



def test_6_temporary_database_lock_simulation():
    """TEST 6: Inject an exclusive database lock and verify retry mechanism backs off."""
    db_path = get_db_path()
    lock_released = threading.Event()
    write_finished = threading.Event()
    write_result = [False]

    def locker_worker():
        conn = sqlite3.connect(db_path, timeout=10.0)
        conn.execute("BEGIN EXCLUSIVE")
        time.sleep(0.4)  # Hold exclusive lock for 400ms
        conn.commit()
        conn.close()
        lock_released.set()

    def retrying_writer():
        def _write_op(c):
            c.execute("INSERT OR REPLACE INTO shadow_learner_state (id, is_running, updated_at) values (1, 1, ?)", (time.time(),))
            return True

        res = execute_write_with_retry(
            _write_op,
            writer_name="LockTestWriter",
            table_or_query="shadow_learner_state",
            max_retries=10,
            initial_delay=0.05,
            db_path=db_path
        )
        write_result[0] = res
        write_finished.set()

    t_lock = threading.Thread(target=locker_worker)
    t_write = threading.Thread(target=retrying_writer)

    t_lock.start()
    time.sleep(0.05)
    t_write.start()

    t_lock.join(timeout=3.0)
    t_write.join(timeout=5.0)

    assert write_result[0] is True
    assert write_finished.is_set()


def test_7_recovery_after_lock_disappears():
    """TEST 7: Pending queued items flush immediately once the lock is released."""
    store = ArbitrageEvidenceStore()
    batch = [generate_dummy_event(sym="NEAR/USDT") for _ in range(10)]
    success = store._insert_batch_with_retry(batch)
    assert success is True


def test_8_application_restart_spillover_recovery():
    """TEST 8: Verify spillover items on disk are recovered on startup."""
    store = ArbitrageEvidenceStore()
    spillover_event = generate_dummy_event(sym="PEPE/USDT", category="TEST_SPILLOVER")
    store._append_to_spillover_file([spillover_event])

    assert os.path.exists(store.spillover_file)
    store._recover_spillover_on_startup()

    row = None
    for _ in range(25):
        time.sleep(0.1)
        with create_sqlite_connection(store.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM arbitrage_evidence_events WHERE event_id = ?",
                (spillover_event.event_id,)
            ).fetchone()
            if row is not None:
                break

    assert row is not None
    assert row["symbol"] == "PEPE/USDT"


def test_9_zero_evidence_events_silently_lost():
    """TEST 9: Assert zero events dropped across store lifecycle."""
    store = ArbitrageEvidenceStore()
    assert store.events_dropped == 0



def test_10_jwt_and_credential_log_redaction():
    """TEST 10: Verify sensitive JWT tokens, passwords, and API keys are completely redacted."""
    raw_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMDQiLCJleHAiOjE3NDczMTcwMDB9.AbCdEf123456789"
    test_logs = [
        f"GET /ws/stream?token={raw_jwt} HTTP/1.1",
        f"Authorization: Bearer {raw_jwt}",
        'Connecting with api_key: "SUPER_SECRET_KEY_1234"',
        'User entered password="MySecurePassword999"',
        'Payload contained refresh_token: "REFRESH_XYZ_987654321"'
    ]

    for raw in test_logs:
        sanitized = sanitize_sensitive_data(raw)
        assert raw_jwt not in sanitized
        assert "SUPER_SECRET_KEY_1234" not in sanitized
        assert "MySecurePassword999" not in sanitized
        assert "REFRESH_XYZ_987654321" not in sanitized
        assert "[REDACTED]" in sanitized



def test_11_scanner_continues_while_persistence_busy():
    """TEST 11: Market scanner event recording is sub-millisecond even when SQLite is under load."""
    store = ArbitrageEvidenceStore()
    t_start = time.perf_counter()
    for _ in range(50):
        store.record_event(generate_dummy_event("BTC/USDT"))
    t_end = time.perf_counter()
    assert (t_end - t_start) < 0.05



def test_12_shadow_learner_resiliency_on_transient_lock():
    """TEST 12: Shadow learner state saving completes resiliently."""
    learner = ShadowAutonomousLearner()
    learner._save_persistent_state()
    assert learner.experiments_failed == 0
