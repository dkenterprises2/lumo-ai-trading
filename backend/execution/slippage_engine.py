from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

@dataclass
class SlippageEstimate:
    estimated_slippage_pct: float
    estimated_slippage_usd: float
    expected_price: float
    estimated_fill_price: float
    action: str  # ALLOW, WARN, REQUIRE_CONFIRMATION, BLOCK
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class SlippageEngine:
    """Institutional Slippage Control and Order-Book Impact Engine."""

    def estimate_slippage(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float = 50000.0,
        available_liquidity_usd: float = 100000.0,
        spread_pct: float = 0.02,
        volatility_atr_pct: float = 2.0
    ) -> SlippageEstimate:
        """Estimate slippage percentage and decision action based on size-to-liquidity ratio."""
        base_p = max(0.00000001, price)
        order_val_usd = quantity * base_p

        # 1. Spread impact
        spread_component = spread_pct / 2.0

        # 2. Size-to-liquidity impact
        liquidity_ratio = (order_val_usd / max(1.0, available_liquidity_usd))
        depth_component = (liquidity_ratio ** 1.5) * 0.50

        # 3. Volatility multiplier
        vol_multiplier = 1.0 + max(0.0, (volatility_atr_pct - 2.0) * 0.1)

        total_slippage_pct = (spread_component + depth_component) * vol_multiplier
        total_slippage_usd = order_val_usd * (total_slippage_pct / 100.0)

        # Expected fill price direction
        if side.upper() in ["BUY", "LONG"]:
            estimated_fill_p = base_p * (1.0 + (total_slippage_pct / 100.0))
        else:
            estimated_fill_p = base_p * (1.0 - (total_slippage_pct / 100.0))

        # Risk Threshold Evaluation
        if total_slippage_pct > 0.50:
            action = "BLOCK"
            reason = f"Estimated slippage ({total_slippage_pct:.3f}%) exceeds maximum safety threshold (0.50%). Order BLOCKED."
        elif total_slippage_pct >= 0.25:
            action = "REQUIRE_CONFIRMATION"
            reason = f"High estimated slippage ({total_slippage_pct:.3f}% >= 0.25%). User confirmation required."
        elif total_slippage_pct >= 0.10:
            action = "WARN"
            reason = f"Moderate slippage warning ({total_slippage_pct:.3f}% >= 0.10%). Execution allowed with warning."
        else:
            action = "ALLOW"
            reason = f"Low estimated slippage ({total_slippage_pct:.3f}% < 0.10%). Execution ALLOWED."

        return SlippageEstimate(
            estimated_slippage_pct=round(total_slippage_pct, 4),
            estimated_slippage_usd=round(total_slippage_usd, 4),
            expected_price=round(base_p, 4),
            estimated_fill_price=round(estimated_fill_p, 4),
            action=action,
            reason=reason
        )
