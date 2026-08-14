from dataclasses import dataclass, asdict
from typing import Dict, Any

class AccountingInvariantViolation(Exception):
    """Raised when cash + position_value != total_equity."""
    pass

class PnLInvariantsManager:
    """Enforces mathematical invariants across cash balance, position values, fees, and total equity."""

    def verify_equity_invariant(
        self,
        cash_balance: float,
        position_value: float,
        total_equity: float,
        tolerance: float = 0.01
    ) -> bool:
        """Verify invariant: cash + position_value == total_equity within tolerance."""
        calculated_equity = cash_balance + position_value
        diff = abs(calculated_equity - total_equity)

        if diff > tolerance:
            raise AccountingInvariantViolation(
                f"ACCOUNTING INVARIANT VIOLATION: cash (${cash_balance:.2f}) + position_val (${position_value:.2f}) = ${calculated_equity:.2f} != total_equity (${total_equity:.2f}) [diff: ${diff:.4f}]"
            )
        return True

    def format_micro_price(self, price: float) -> str:
        """Format sub-cent and micro-penny tokens (PEPE, SHIB, FLOKI) dynamically."""
        if price <= 0:
            return "$0.00"
        if price < 0.0001:
            return f"${price:.8f}"
        elif price < 1.0:
            return f"${price:.4f}"
        else:
            return f"${price:.2f}"

# Global Singleton Manager
pnl_invariants = PnLInvariantsManager()
