from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

@dataclass
class UserRiskProfile:
    name: str  # CONSERVATIVE, BALANCED, AGGRESSIVE, CUSTOM
    risk_multiplier: float
    max_portfolio_heat_pct: float
    max_leverage: int
    volatility_tolerance: str
    drawdown_tolerance_pct: float
    minimum_confidence_pct: float
    dynamic_trade_limit_multiplier: float
    max_concurrent_trades: int = 10
    max_capital_per_trade_pct: float = 10.0
    daily_loss_limit_pct: float = 5.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class UserRiskProfileManager:
    """Manages user risk profile presets and Phase 26 preferences."""

    PROFILES = {
        "CONSERVATIVE": UserRiskProfile(
            name="CONSERVATIVE",
            risk_multiplier=0.60,
            max_portfolio_heat_pct=3.0,
            max_leverage=2,
            volatility_tolerance="LOW",
            drawdown_tolerance_pct=5.0,
            minimum_confidence_pct=80.0,
            dynamic_trade_limit_multiplier=0.60,
            max_concurrent_trades=5,
            max_capital_per_trade_pct=5.0,
            daily_loss_limit_pct=3.0
        ),
        "BALANCED": UserRiskProfile(
            name="BALANCED",
            risk_multiplier=1.0,
            max_portfolio_heat_pct=5.0,
            max_leverage=5,
            volatility_tolerance="MEDIUM",
            drawdown_tolerance_pct=10.0,
            minimum_confidence_pct=70.0,
            dynamic_trade_limit_multiplier=1.0,
            max_concurrent_trades=10,
            max_capital_per_trade_pct=10.0,
            daily_loss_limit_pct=5.0
        ),
        "AGGRESSIVE": UserRiskProfile(
            name="AGGRESSIVE",
            risk_multiplier=1.40,
            max_portfolio_heat_pct=8.0,
            max_leverage=10,
            volatility_tolerance="HIGH",
            drawdown_tolerance_pct=15.0,
            minimum_confidence_pct=60.0,
            dynamic_trade_limit_multiplier=1.0,
            max_concurrent_trades=20,
            max_capital_per_trade_pct=15.0,
            daily_loss_limit_pct=10.0
        )
    }

    def get_profile(self, profile_name: str = "BALANCED") -> UserRiskProfile:
        """Get profile preset or default to BALANCED with safe defaults."""
        name = profile_name.upper() if profile_name else "BALANCED"
        prof = self.PROFILES.get(name, self.PROFILES["BALANCED"])

        # Fallback safe defaults if missing or invalid
        if not getattr(prof, "max_concurrent_trades", None) or prof.max_concurrent_trades <= 0:
            prof.max_concurrent_trades = 10
        if not getattr(prof, "max_capital_per_trade_pct", None) or prof.max_capital_per_trade_pct <= 0:
            prof.max_capital_per_trade_pct = 10.0
        if not getattr(prof, "daily_loss_limit_pct", None) or prof.daily_loss_limit_pct <= 0:
            prof.daily_loss_limit_pct = 5.0

        return prof
