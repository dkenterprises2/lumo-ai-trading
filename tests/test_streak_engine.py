import pytest
from backend.portfolio_risk.streak_engine import StreakEngine

def test_streak_adaptation():
    engine = StreakEngine()

    # Loss streak of 5
    loss_history = [{"pnl_usd": -10.0} for _ in range(5)]
    res_loss = engine.analyze_streaks(loss_history)
    assert res_loss.consecutive_losses == 5
    assert res_loss.streak_risk_multiplier == 0.50

    # Win streak of 5 -> maintains 1.0x (no emotional escalation)
    win_history = [{"pnl_usd": 20.0} for _ in range(5)]
    res_win = engine.analyze_streaks(win_history)
    assert res_win.consecutive_wins == 5
    assert res_win.streak_risk_multiplier == 1.0
