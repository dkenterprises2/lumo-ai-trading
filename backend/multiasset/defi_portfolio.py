from typing import Dict, Any, List

class DeFiPortfolioManager:
    """DeFi Staking, Lending & Liquidity Pool Portfolio Aggregator."""

    @staticmethod
    def get_positions() -> List[Dict[str, Any]]:
        return [
            {"protocol": "Uniswap V3", "chain": "Ethereum", "position_type": "LP", "value_usd": 350000.0},
            {"protocol": "Aave V3", "chain": "Arbitrum", "position_type": "LENDING", "value_usd": 500000.0}
        ]

defi_portfolio = DeFiPortfolioManager()
