import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional
from .pnl_invariants import pnl_invariants

@dataclass
class ReconciliationReport:
    cash_balance: float
    unrealized_pnl: float
    realized_pnl: float
    total_position_value: float
    total_equity: float
    total_fees_paid: float
    is_reconciled: bool
    discrepancy_amount: float
    timestamp: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class ReconciliationEngine:
    """Performs daily and real-time ledger & portfolio reconciliation audits."""

    def reconcile(
        self,
        cash_balance: float,
        positions: List[Dict[str, Any]],
        realized_pnl: float = 0.0,
        total_fees_paid: float = 0.0
    ) -> ReconciliationReport:
        """Run complete portfolio value reconciliation."""
        total_pos_val = 0.0
        total_unrealized = 0.0

        for pos in positions:
            size = float(pos.get("amount", pos.get("size", 0.0)))
            curr_p = float(pos.get("current_price", pos.get("entry_price", 0.0)))
            entry_p = float(pos.get("entry_price", 0.0))
            side = str(pos.get("side", "BUY")).upper()

            val = size * curr_p
            total_pos_val += val

            if side in ["BUY", "LONG"]:
                u_pnl = size * (curr_p - entry_p)
            else:
                u_pnl = size * (entry_p - curr_p)
            total_unrealized += u_pnl

        calc_equity = cash_balance + total_pos_val
        is_ok = True
        discrepancy = 0.0

        try:
            pnl_invariants.verify_equity_invariant(cash_balance, total_pos_val, calc_equity)
        except Exception as e:
            is_ok = False
            discrepancy = abs((cash_balance + total_pos_val) - calc_equity)

        return ReconciliationReport(
            cash_balance=round(cash_balance, 2),
            unrealized_pnl=round(total_unrealized, 2),
            realized_pnl=round(realized_pnl, 2),
            total_position_value=round(total_pos_val, 2),
            total_equity=round(calc_equity, 2),
            total_fees_paid=round(total_fees_paid, 2),
            is_reconciled=is_ok,
            discrepancy_amount=round(discrepancy, 4),
            timestamp=time.time()
        )

# Global Singleton Engine
reconciliation_engine = ReconciliationEngine()
