from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

@dataclass
class DynamicTradeLimitResult:
    configured_max_positions: int
    dynamic_risk_limit: int
    effective_max_positions: int
    currently_open_positions: int
    available_trade_slots: int
    can_open_new_trade: bool
    constraining_factor: str
    reasons: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class DynamicTradeLimitEngine:
    """Calculates dynamic effective trade limit as min(user_configured_max, dynamic_risk_limit)."""

    def compute_effective_limit(
        self,
        user_configured_max_positions: int = 10,
        currently_open_positions: int = 0,
        portfolio_heat_status: str = "NORMAL",
        drawdown_pct: float = 0.0,
        correlation_risk_score: float = 0.0,
        volatility_regime: str = "NORMAL",
        daily_loss_used_pct: float = 0.0,
        max_daily_loss_pct: float = 5.0
    ) -> DynamicTradeLimitResult:
        """Compute dynamic safe maximum open positions."""
        u_max = max(1, user_configured_max_positions)
        d_limit = u_max

        factors = []
        constraining_factor = "USER_HARD_CEILING"

        # 1. Portfolio Heat constraint
        if portfolio_heat_status == "CRITICAL":
            d_limit = 0
            constraining_factor = "PORTFOLIO_HEAT_CRITICAL"
            factors.append("Portfolio heat critical (0 slots)")
        elif portfolio_heat_status == "HIGH":
            d_limit = min(d_limit, max(1, int(u_max * 0.4)))
            constraining_factor = "PORTFOLIO_HEAT_HIGH"
            factors.append("Portfolio heat high (40% capacity)")
        elif portfolio_heat_status == "WARNING":
            d_limit = min(d_limit, max(2, int(u_max * 0.7)))
            if constraining_factor == "USER_HARD_CEILING": constraining_factor = "PORTFOLIO_HEAT_WARNING"

        # 2. Drawdown constraint
        if drawdown_pct >= 10.0:
            d_limit = 0
            constraining_factor = "MAX_DRAWDOWN_BREACH"
            factors.append("Drawdown >= 10% (Trading Halted)")
        elif drawdown_pct >= 5.0:
            d_limit = min(d_limit, max(1, int(u_max * 0.5)))
            if constraining_factor == "USER_HARD_CEILING": constraining_factor = "DRAWDOWN_ELEVATED"
            factors.append("Drawdown >= 5% (50% capacity)")

        # 3. High Correlation constraint
        if correlation_risk_score > 0.70:
            d_limit = min(d_limit, max(2, int(u_max * 0.6)))
            if constraining_factor == "USER_HARD_CEILING": constraining_factor = "CORRELATION_HIGH"
            factors.append("Correlation risk high (>0.70)")

        # 4. Volatility Regime constraint
        if volatility_regime == "EXTREME":
            d_limit = min(d_limit, max(1, int(u_max * 0.3)))
            if constraining_factor == "USER_HARD_CEILING": constraining_factor = "VOLATILITY_EXTREME"
            factors.append("Volatility extreme")

        # 5. Daily Loss Budget constraint
        if daily_loss_used_pct >= max_daily_loss_pct:
            d_limit = 0
            constraining_factor = "DAILY_LOSS_EXHAUSTED"
            factors.append("Daily loss budget exhausted")

        # CRITICAL SAFETY RULE: Never exceed user hard ceiling!
        effective_limit = min(u_max, d_limit)
        available_slots = max(0, effective_limit - currently_open_positions)
        can_open = available_slots > 0 and effective_limit > 0

        return DynamicTradeLimitResult(
            configured_max_positions=u_max,
            dynamic_risk_limit=d_limit,
            effective_max_positions=effective_limit,
            currently_open_positions=currently_open_positions,
            available_trade_slots=available_slots,
            can_open_new_trade=can_open,
            constraining_factor=constraining_factor,
            reasons={"factors": factors, "summary": f"User max: {u_max}, Dynamic limit: {d_limit}, Effective: {effective_limit}"}
        )
