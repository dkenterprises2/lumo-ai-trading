from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional

@dataclass
class ExposureAllocation:
    strategy_name: str
    target_weight_pct: float
    allocated_usd: float
    max_exposure_usd: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class ExposureAllocator:
    """Allocates portfolio capital across strategies based on risk-budget and Sharpe ratios."""

    def allocate_exposure(
        self,
        portfolio_equity: float,
        strategies: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, ExposureAllocation]:
        """Allocate risk-weighted capital across strategies."""
        if not strategies:
            strategies = [
                {"name": "AI Hybrid", "sharpe": 2.1, "base_weight": 0.50},
                {"name": "Scalping", "sharpe": 1.7, "base_weight": 0.30},
                {"name": "Stat Arb", "sharpe": 1.5, "base_weight": 0.20}
            ]

        eq = max(1.0, portfolio_equity)
        total_sharpe = sum(s.get("sharpe", 1.0) for s in strategies)
        result = {}

        for s in strategies:
            s_name = s["name"]
            weight = (s.get("sharpe", 1.0) / total_sharpe) if total_sharpe > 0 else (1.0 / len(strategies))
            alloc_usd = eq * weight
            result[s_name] = ExposureAllocation(
                strategy_name=s_name,
                target_weight_pct=round(weight * 100.0, 2),
                allocated_usd=round(alloc_usd, 2),
                max_exposure_usd=round(alloc_usd * 1.5, 2)
            )

        return result
