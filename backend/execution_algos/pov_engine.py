from typing import Dict, Any

class POVExecutionEngine:
    """Percentage of Volume (POV) Execution Engine."""

    @staticmethod
    def calculate_pov_slice(
        market_volume: float,
        target_participation_pct: float = 10.0,
        max_participation_cap: float = 20.0
    ) -> Dict[str, Any]:
        capped_pct = min(target_participation_pct, max_participation_cap)
        slice_qty = market_volume * (capped_pct / 100.0)
        return {
            "algo": "POV",
            "market_volume": market_volume,
            "target_participation_pct": target_participation_pct,
            "effective_participation_pct": capped_pct,
            "slice_quantity": round(slice_qty, 6)
        }

pov_engine = POVExecutionEngine()
