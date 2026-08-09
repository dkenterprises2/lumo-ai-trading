from typing import Dict, Any, List

class SecurityMaster:
    """Canonical Multi-Asset Security Master Registry."""

    def __init__(self):
        self._securities: List[Dict[str, Any]] = [
            {
                "asset_id": "BTCUSDT",
                "asset_class": "CRYPTO",
                "exchange": "BINANCE",
                "base_currency": "BTC",
                "quote_currency": "USDT",
                "tick_size": 0.01,
                "lot_size": 0.0001
            },
            {
                "asset_id": "AAPL",
                "asset_class": "EQUITY",
                "exchange": "NASDAQ",
                "base_currency": "AAPL",
                "quote_currency": "USD",
                "tick_size": 0.01,
                "lot_size": 1.0
            }
        ]

    def list_securities(self) -> List[Dict[str, Any]]:
        return self._securities

    def register_security(self, security_data: Dict[str, Any]) -> Dict[str, Any]:
        self._securities.append(security_data)
        return security_data

security_master = SecurityMaster()
