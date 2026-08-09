from typing import Dict, Any

class RewardEngine:
    """Configurable Multi-Component RL Reward Shaping Framework."""

    @staticmethod
    def calculate_reward(
        pnl: float,
        sharpe: float,
        drawdown: float,
        turnover: float,
        slippage: float
    ) -> float:
        reward = (
            (pnl * 1.0)
            + (sharpe * 0.5)
            - (drawdown * 0.8)
            - (turnover * 0.2)
            - (slippage * 0.3)
        )
        return round(reward, 4)

reward_engine = RewardEngine()
