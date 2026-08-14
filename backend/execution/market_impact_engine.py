from typing import Dict, Any, Optional

class MarketImpactEngine:
    """Estimates Market Impact Costs based on order size vs daily volume."""

    def estimate_impact_bps(self, order_val_usd: float, daily_vol_usd: float = 10000000.0) -> float:
        ratio = order_val_usd / max(1.0, daily_vol_usd)
        impact_bps = (ratio ** 0.5) * 50.0
        return round(impact_bps, 2)
