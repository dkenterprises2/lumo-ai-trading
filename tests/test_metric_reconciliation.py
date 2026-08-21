import pytest
import time
from backend.arbitrage.arbitrage_evidence_store import ArbitrageEvidenceStore
from backend.arbitrage.arbitrage_metrics import ArbitrageMetricsTracker

def test_metric_reconciliation_zero_drift():
    """
    Test that displayed metric counts match underlying persistent database records
    with zero unverified discrepancy.
    """
    store = ArbitrageEvidenceStore()

    # Ensure in-flight queue is drained
    t0 = time.time()
    while not store._write_queue.empty() and time.time() - t0 < 5.0:
        time.sleep(0.05)
    time.sleep(0.1)

    db_counts = store.get_category_counts()
    metrics = ArbitrageMetricsTracker.get_summary(db_counts=db_counts).to_dict()
    report = store.reconcile_metrics(metrics, db_counts=db_counts)
    
    assert report["status"] in ["INTEGRITY_VERIFIED", "PASS"]
    assert report["is_consistent"] is True
    
    for row in report["reconciliation"]:
        assert row["difference"] == 0, f"Discrepancy detected in {row['card_metric']}: displayed={row['displayed_count']}, evidence={row['evidence_count']}"
