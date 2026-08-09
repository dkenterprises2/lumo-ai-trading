from typing import Dict, Any

class SlippageTracker:
    """Slippage Tracker measuring expected vs actual fill execution prices."""

    @staticmethod
    def calculate_slippage(expected_price: float, filled_price: float, side: str = "BUY") -> Dict[str, Any]:
        """Compute execution price slippage in basis points (bps)."""
        if expected_price <= 0:
            return {"slippage_bps": 0.0, "status": "INVALID_PRICE"}

        diff = (filled_price - expected_price) if side.upper() == "BUY" else (expected_price - filled_price)
        slippage_pct = (diff / expected_price) * 100.0
        slippage_bps = round(slippage_pct * 100.0, 2)

        return {
            "expected_price": expected_price,
            "filled_price": filled_price,
            "side": side.upper(),
            "slippage_bps": slippage_bps,
            "is_adverse": slippage_bps > 0
        }

slippage_tracker = SlippageTracker()
