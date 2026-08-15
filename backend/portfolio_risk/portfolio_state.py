import time
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional

@dataclass
class PortfolioRiskState:
    """Institutional Portfolio Risk State snapshot."""
    user_id: str
    equity: float = 10000.0
    available_balance: float = 10000.0
    unrealized_pnl: float = 0.0
    realized_pnl_today: float = 0.0
    drawdown_pct: float = 0.0
    volatility_regime: str = "NORMAL"
    market_regime: str = "BULL"
    open_positions: int = 0
    configured_max_positions: int = 10
    dynamic_max_positions: int = 10
    effective_max_positions: int = 10
    portfolio_heat_pct: float = 0.0
    correlation_risk_score: float = 0.0
    concentration_risk_score: float = 0.0
    leverage_used: float = 1.0
    recommended_max_leverage: float = 2.0
    risk_budget_remaining_pct: float = 5.0
    risk_score: Optional[float] = None
    overall_status: str = "HEALTHY"
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
