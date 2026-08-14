from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional

@dataclass
class PortfolioHeat:
    gross_heat_pct: float
    net_heat_pct: float
    risk_budget_pct: float
    utilization_pct: float
    status: str  # NORMAL, WARNING, HIGH, CRITICAL

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class PortfolioHeatEngine:
    """Calculates gross and net portfolio heat based on capital at risk, stop distance, leverage, and correlation multipliers."""

    def __init__(self, default_risk_budget_pct: float = 5.0):
        self.default_risk_budget_pct = default_risk_budget_pct

    def compute_heat(
        self,
        positions: Dict[str, Dict[str, Any]],
        portfolio_value: float,
        correlation_risk_score: float = 0.0,
        risk_budget_pct: Optional[float] = None
    ) -> PortfolioHeat:
        """Compute gross and net portfolio heat percentages."""
        budget_pct = risk_budget_pct or self.default_risk_budget_pct
        if not positions or portfolio_value <= 0:
            return PortfolioHeat(
                gross_heat_pct=0.0,
                net_heat_pct=0.0,
                risk_budget_pct=budget_pct,
                utilization_pct=0.0,
                status="NORMAL"
            )

        gross_risk_usd = 0.0
        for sym, pos in positions.items():
            entry_p = pos.get("entry_price", 1.0)
            sl_p = pos.get("stop_loss_price", 0.0)
            amount = pos.get("amount", 0.0)
            margin = pos.get("margin_usd", 0.0)

            if sl_p > 0 and entry_p > 0:
                sl_distance_pct = abs(entry_p - sl_p) / entry_p
                trade_risk_usd = amount * abs(entry_p - sl_p)
            else:
                # Default 5% risk estimate if stop loss missing
                trade_risk_usd = margin * 0.50

            gross_risk_usd += trade_risk_usd

        gross_heat_pct = (gross_risk_usd / portfolio_value) * 100.0
        # Correlation multiplier (1.0 to 1.5x)
        corr_mult = 1.0 + (max(0.0, correlation_risk_score) * 0.5)
        net_heat_pct = gross_heat_pct * corr_mult

        utilization_pct = (net_heat_pct / budget_pct) * 100.0 if budget_pct > 0 else 100.0

        status = "NORMAL"
        if utilization_pct >= 100.0:
            status = "CRITICAL"
        elif utilization_pct >= 80.0:
            status = "HIGH"
        elif utilization_pct >= 60.0:
            status = "WARNING"

        return PortfolioHeat(
            gross_heat_pct=round(gross_heat_pct, 2),
            net_heat_pct=round(net_heat_pct, 2),
            risk_budget_pct=round(budget_pct, 2),
            utilization_pct=round(utilization_pct, 2),
            status=status
        )
