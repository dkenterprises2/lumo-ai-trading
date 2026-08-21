import sys
import os
import time

sys.path.insert(0, os.path.abspath("."))

def run_tests():
    print("================================================================")
    print("RUNNING SQLITE CONCURRENCY & EVIDENCE RESILIENCE TEST SUITE")
    print("================================================================")

    import tests.test_evidence_idempotency as t_idem
    print("\n[1/6] Running test_evidence_idempotency...")
    t0 = time.time()
    t_idem.test_evidence_idempotent_duplicate_insert()
    print(f"--> PASS ({time.time() - t0:.3f}s)")

    import tests.test_evidence_retry as t_retry
    print("\n[2/6] Running test_evidence_retry...")
    t0 = time.time()
    t_retry.test_evidence_retry_under_artificial_lock()
    print(f"--> PASS ({time.time() - t0:.3f}s)")

    import tests.test_event_loss_detection as t_loss
    print("\n[3/6] Running test_event_loss_detection...")
    t0 = time.time()
    t_loss.test_event_loss_detection_zero_loss_invariant()
    print(f"--> PASS ({time.time() - t0:.3f}s)")

    import tests.test_evidence_restart_recovery as t_rec
    print("\n[4/6] Running test_evidence_restart_recovery...")
    t0 = time.time()
    t_rec.test_evidence_restart_recovery_drain()
    print(f"--> PASS ({time.time() - t0:.3f}s)")

    import tests.test_metric_reconciliation as t_recon
    print("\n[5/6] Running test_metric_reconciliation...")
    t0 = time.time()
    t_recon.test_metric_reconciliation_zero_drift()
    print(f"--> PASS ({time.time() - t0:.3f}s)")

    import tests.test_sqlite_concurrency as t_conc
    print("\n[6/6] Running test_sqlite_concurrency (Multi-Threaded Burst)...")
    t0 = time.time()
    t_conc.test_sqlite_concurrency_multi_writer()
    print(f"--> PASS ({time.time() - t0:.3f}s)")

    print("\n================================================================")
    print("ALL 6 CONCURRENCY & EVIDENCE STORE TESTS PASSED SUCCESSFULLY!")
    print("================================================================")

if __name__ == "__main__":
    run_tests()
