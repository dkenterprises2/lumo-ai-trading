import time
from typing import Dict, Any, List

class WhaleMonitorEngine:
    """Whale Wallet Large Transfer Monitoring & Alerting Abstraction."""

    def __init__(self):
        self._alerts: List[Dict[str, Any]] = [
            {
                "alert_id": "WHALE-101",
                "symbol": "BTC",
                "amount": 2500.0,
                "value_usd": 162000000.0,
                "from_address": "0x111...aaa",
                "to_address": "Binance Hot Wallet",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
            }
        ]

    def list_alerts(self) -> List[Dict[str, Any]]:
        return self._alerts

whale_monitor = WhaleMonitorEngine()
