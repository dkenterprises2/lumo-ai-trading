import pytest
from backend.accounting.pnl_invariants import PnLInvariantsManager, AccountingInvariantViolation
from backend.accounting.reconciliation_engine import ReconciliationEngine

def test_pnl_invariant_passes():
    mgr = PnLInvariantsManager()
    res = mgr.verify_equity_invariant(cash_balance=1000.0, position_value=500.0, total_equity=1500.0)
    assert res is True

def test_pnl_invariant_raises_on_discrepancy():
    mgr = PnLInvariantsManager()
    with pytest.raises(AccountingInvariantViolation):
        mgr.verify_equity_invariant(cash_balance=1000.0, position_value=500.0, total_equity=1800.0)

def test_micro_price_formatting():
    mgr = PnLInvariantsManager()
    assert mgr.format_micro_price(0.00001234) == "$0.00001234"
    assert mgr.format_micro_price(0.0543) == "$0.0543"
    assert mgr.format_micro_price(65230.50) == "$65230.50"

def test_reconciliation_report():
    engine = ReconciliationEngine()
    positions = [
        {"amount": 1.0, "entry_price": 50000.0, "current_price": 51000.0, "side": "BUY"}
    ]
    report = engine.reconcile(cash_balance=5000.0, positions=positions, realized_pnl=200.0)
    assert report.is_reconciled is True
    assert report.total_position_value == 51000.0
    assert report.unrealized_pnl == 1000.0
    assert report.total_equity == 56000.0
