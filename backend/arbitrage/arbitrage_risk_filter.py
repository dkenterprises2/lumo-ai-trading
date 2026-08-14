from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

@dataclass
class ArbitrageRiskResult:
    passed: bool
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class ArbitrageRiskFilter:
    """Enforces Strict Risk Rules for Arbitrage Execution."""

    def evaluate_opportunity_risk(
        self,
        net_spread_pct: float,
        slippage_bps: float = 5.0,
        exchange_health: str = "HEALTHY",
        portfolio_heat_utilization_pct: float = 20.0,
        kill_switch_state: str = "NORMAL"
    ) -> ArbitrageRiskResult:
        if kill_switch_state != "NORMAL":
            return ArbitrageRiskResult(False, f"Kill switch is in {kill_switch_state} state (must be NORMAL)")

        if portfolio_heat_utilization_pct >= 70.0:
            return ArbitrageRiskResult(False, f"Portfolio heat ({portfolio_heat_utilization_pct}%) >= 70% threshold")

        if net_spread_pct < 0.15:
            return ArbitrageRiskResult(False, f"Net edge ({net_spread_pct:.4f}%) < 0.15% minimum threshold")

        slippage_pct = slippage_bps / 100.0
        if slippage_pct >= net_spread_pct:
            return ArbitrageRiskResult(False, f"Estimated slippage ({slippage_pct:.4f}%) >= expected net edge ({net_spread_pct:.4f}%)")

        if exchange_health.upper() != "HEALTHY":
            return ArbitrageRiskResult(False, f"Exchange health is {exchange_health}")

        return ArbitrageRiskResult(True, "Arbitrage risk validations passed")
