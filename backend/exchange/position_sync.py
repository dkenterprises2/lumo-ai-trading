import time
from typing import Dict, Any, List

class PositionSyncEngine:
    """Position Synchronization Engine matching local trader positions with live exchange states."""

    @staticmethod
    def synchronize_positions(local_positions: Dict[str, Any], exchange_positions: Dict[str, Any]) -> Dict[str, Any]:
        """Reconcile local trader position dictionary with live exchange API state."""
        converged = True
        discrepancies = []

        for symbol, loc_pos in local_positions.items():
            if symbol not in exchange_positions:
                discrepancies.append({"symbol": symbol, "issue": "POSITION_MISSING_ON_EXCHANGE"})
                converged = False
            else:
                ex_pos = exchange_positions[symbol]
                if abs(loc_pos.get("amount", 0.0) - ex_pos.get("amount", 0.0)) > 1e-4:
                    discrepancies.append({"symbol": symbol, "issue": "AMOUNT_MISMATCH"})
                    converged = False

        return {
            "converged": converged,
            "discrepancies": discrepancies,
            "synced_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        }

position_sync_engine = PositionSyncEngine()
