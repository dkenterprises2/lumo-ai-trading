from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

@dataclass
class RiskBudget:
    daily_budget_pct: float
    weekly_budget_pct: float
    used_today_pct: float
    used_week_pct: float
    remaining_daily_pct: float
    remaining_weekly_pct: float
    status: str # HEALTHY, WARNING, EXHAUSTED
    action: str  # PERMIT_NEW_TRADES, BLOCK_NEW_TRADES

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class RiskBudgetTracker:
    """Tracks daily and weekly risk budgets against realized and unrealized losses."""

    def __init__(
        self,
        default_daily_budget_pct: float = 5.0,
        default_weekly_budget_pct: float = 12.0
    ):
        self.daily_budget_pct = default_daily_budget_pct
        self.weekly_budget_pct = default_weekly_budget_pct

    def compute_budget(
        self,
        initial_balance: float,
        daily_pnl_usd: float,
        weekly_pnl_usd: float = 0.0,
        open_risk_usd: float = 0.0,
        custom_daily_limit_pct: Optional[float] = None
    ) -> RiskBudget:
        """Compute remaining daily and weekly risk budgets."""
        init_bal = max(1.0, initial_balance)
        d_budget_pct = custom_daily_limit_pct if custom_daily_limit_pct is not None else self.daily_budget_pct
        w_budget_pct = self.weekly_budget_pct

        # Losses convert to positive usage
        daily_loss_usd = abs(min(0.0, daily_pnl_usd)) + open_risk_usd
        weekly_loss_usd = abs(min(0.0, weekly_pnl_usd)) + open_risk_usd

        used_today_pct = (daily_loss_usd / init_bal) * 100.0
        used_week_pct = (weekly_loss_usd / init_bal) * 100.0

        rem_daily_pct = max(0.0, d_budget_pct - used_today_pct)
        rem_weekly_pct = max(0.0, w_budget_pct - used_week_pct)

        action = "PERMIT_NEW_TRADES"
        status = "HEALTHY"

        if rem_daily_pct <= 0.0 or rem_weekly_pct <= 0.0:
            status = "EXHAUSTED"
            action = "BLOCK_NEW_TRADES"
        elif rem_daily_pct <= 1.0 or rem_weekly_pct <= 2.0:
            status = "WARNING"
            action = "PERMIT_NEW_TRADES"

        return RiskBudget(
            daily_budget_pct=round(d_budget_pct, 2),
            weekly_budget_pct=round(w_budget_pct, 2),
            used_today_pct=round(used_today_pct, 2),
            used_week_pct=round(used_week_pct, 2),
            remaining_daily_pct=round(rem_daily_pct, 2),
            remaining_weekly_pct=round(rem_weekly_pct, 2),
            status=status,
            action=action
        )
