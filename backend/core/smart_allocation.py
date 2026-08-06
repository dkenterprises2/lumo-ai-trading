from typing import Dict, Any, List

class SmartCapitalAllocator:
    """Smart Capital Allocator optimizing portfolio exposure, sector caps, and strategy weights."""

    def __init__(self, max_single_strategy_pct: float = 30.0, max_sector_exposure_pct: float = 50.0):
        self.max_single_strategy_pct = max_single_strategy_pct
        self.max_sector_exposure_pct = max_sector_exposure_pct

    def calculate_allocations(
        self,
        total_equity: float,
        strategy_performances: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Calculate dynamic capital weights based on Sharpe ratio & Win Rate."""
        if not strategy_performances or total_equity <= 0:
            return []

        total_weight = 0.0
        weighted_strats = []
        for s in strategy_performances:
            sharpe = max(0.1, float(s.get("sharpe_ratio", 1.0)))
            win_rate = max(0.1, float(s.get("win_rate", 50.0)) / 100.0)
            raw_weight = sharpe * win_rate
            total_weight += raw_weight
            weighted_strats.append({
                "strategy_id": s["strategy_id"],
                "raw_weight": raw_weight
            })

        allocations = []
        for s in weighted_strats:
            norm_pct = (s["raw_weight"] / total_weight) * 100.0 if total_weight > 0 else 12.5
            capped_pct = min(self.max_single_strategy_pct, norm_pct)
            allocated_usd = (capped_pct / 100.0) * total_equity

            allocations.append({
                "strategy_id": s["strategy_id"],
                "allocation_pct": round(capped_pct, 2),
                "allocated_usd": round(allocated_usd, 2)
            })

        return allocations

smart_allocator = SmartCapitalAllocator()
