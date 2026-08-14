from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional

@dataclass
class StreakAnalysis:
    consecutive_wins: int
    consecutive_losses: int
    rolling_win_rate_pct: float
    rolling_profit_factor: float
    streak_risk_multiplier: float # 1.0, 0.75, 0.50, 0.25
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class StreakEngine:
    """Adapts position sizing based on recent performance streaks without emotional risk escalation."""

    def analyze_streaks(
        self,
        trade_history: List[Dict[str, Any]],
        window: int = 20
    ) -> StreakAnalysis:
        """Analyze consecutive wins/losses and rolling expectancy."""
        if not trade_history:
            return StreakAnalysis(
                consecutive_wins=0,
                consecutive_losses=0,
                rolling_win_rate_pct=50.0,
                rolling_profit_factor=1.0,
                streak_risk_multiplier=1.0,
                reason="No trade history. Normal risk sizing applied."
            )

        recent = trade_history[:window]
        wins = sum(1 for t in recent if t.get("pnl_usd", 0.0) > 0)
        win_rate = (wins / len(recent)) * 100.0 if recent else 50.0

        gross_gains = sum(t.get("pnl_usd", 0.0) for t in recent if t.get("pnl_usd", 0.0) > 0)
        gross_losses = abs(sum(t.get("pnl_usd", 0.0) for t in recent if t.get("pnl_usd", 0.0) < 0))
        pf = (gross_gains / gross_losses) if gross_losses > 0 else (2.0 if gross_gains > 0 else 1.0)

        # Count current consecutive wins or losses
        cons_wins = 0
        cons_losses = 0
        for t in trade_history:
            pnl = t.get("pnl_usd", 0.0)
            if pnl > 0:
                if cons_losses > 0: break
                cons_wins += 1
            elif pnl < 0:
                if cons_wins > 0: break
                cons_losses += 1
            else:
                break

        mult = 1.0
        reason = "Performance streak normal."

        if cons_losses >= 7:
            mult = 0.25
            reason = f"Severe loss streak ({cons_losses} consecutive losses). Risk scaled to 25%."
        elif cons_losses >= 5:
            mult = 0.50
            reason = f"Significant loss streak ({cons_losses} consecutive losses). Risk scaled to 50%."
        elif cons_losses >= 3:
            mult = 0.75
            reason = f"Minor loss streak ({cons_losses} consecutive losses). Risk scaled to 75%."
        elif cons_wins >= 5:
            # Win streak maintains normal risk 1.0x to prevent overconfidence/over-leverage
            mult = 1.0
            reason = f"Win streak detected ({cons_wins} consecutive wins). Maintaining disciplined 1.0x risk sizing."

        return StreakAnalysis(
            consecutive_wins=cons_wins,
            consecutive_losses=cons_losses,
            rolling_win_rate_pct=round(win_rate, 2),
            rolling_profit_factor=round(pf, 2),
            streak_risk_multiplier=round(mult, 2),
            reason=reason
        )
