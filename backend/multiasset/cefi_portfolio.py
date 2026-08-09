from typing import Dict, Any, List

class CeFiPortfolioManager:
    """Centralized Exchange Multi-Account Portfolio Aggregator."""

    @staticmethod
    def get_positions() -> List[Dict[str, Any]]:
        return [
            {"exchange": "Binance", "account_type": "SPOT", "value_usd": 1250000.0},
            {"exchange": "Bybit", "account_type": "PERPETUAL", "value_usd": 850000.0}
        ]

cefi_portfolio = CeFiPortfolioManager()
