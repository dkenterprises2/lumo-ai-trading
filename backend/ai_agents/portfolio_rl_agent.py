from typing import Dict, Any

class PortfolioAllocationRLAgent:
    """Continuous Portfolio Weight Allocation RL Agent."""

    @staticmethod
    def allocate_weights() -> Dict[str, float]:
        return {
            "BTC": 0.50,
            "ETH": 0.30,
            "USDT_CASH": 0.20
        }

portfolio_rl_agent = PortfolioAllocationRLAgent()
