from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional

@dataclass
class ExecutionCostAnalysis:
    order_id: str
    expected_price: float
    actual_average_fill: float
    quantity: float
    slippage_cost_usd: float
    spread_cost_usd: float
    fee_cost_usd: float
    market_impact_cost_usd: float
    total_execution_cost_usd: float
    implementation_shortfall_bps: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class ExecutionCostEngine:
    """Institutional Execution Cost Analytics & Implementation Shortfall Calculator."""

    def compute_cost_analysis(
        self,
        order_id: str,
        expected_price: float,
        actual_average_fill: float,
        quantity: float,
        side: str = "BUY",
        fee_usd: float = 0.0,
        spread_pct: float = 0.02
    ) -> ExecutionCostAnalysis:
        """Compute complete cost decomposition for executed order."""
        p_exp = max(0.00000001, expected_price)
        p_act = max(0.00000001, actual_average_fill)
        qty = max(0.0, quantity)
        notional = qty * p_exp

        # Slippage Cost
        if side.upper() in ["BUY", "LONG"]:
            slip_diff = max(0.0, p_act - p_exp)
        else:
            slip_diff = max(0.0, p_exp - p_act)

        slippage_cost = qty * slip_diff

        # Spread Cost
        spread_cost = notional * (spread_pct / 200.0)

        # Market Impact Cost (estimated 20% of slippage)
        impact_cost = slippage_cost * 0.20

        # Total Execution Cost
        total_cost = slippage_cost + spread_cost + fee_usd + impact_cost

        # Implementation Shortfall in basis points (bps)
        shortfall_bps = (abs(p_act - p_exp) / p_exp) * 10000.0

        return ExecutionCostAnalysis(
            order_id=order_id,
            expected_price=round(p_exp, 4),
            actual_average_fill=round(p_act, 4),
            quantity=round(qty, 6),
            slippage_cost_usd=round(slippage_cost, 4),
            spread_cost_usd=round(spread_cost, 4),
            fee_cost_usd=round(fee_usd, 4),
            market_impact_cost_usd=round(impact_cost, 4),
            total_execution_cost_usd=round(total_cost, 4),
            implementation_shortfall_bps=round(shortfall_bps, 2)
        )
