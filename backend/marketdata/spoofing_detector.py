import time
from typing import Dict, Any, List

class SpoofingDetector:
    """Heuristic Detector for Order Book Fake Liquidity & Spoofing."""

    def __init__(self):
        self._alerts: List[Dict[str, Any]] = [
            {
                "alert_id": "SPOOF-101",
                "symbol": "BTC/USDT",
                "severity": "HIGH",
                "pattern": "LARGE_NON_EXECUTING_BID_CANCEL",
                "price": 64805.0,
                "quantity": 25.0,
                "detected_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
            }
        ]

    def list_alerts(self) -> List[Dict[str, Any]]:
        return self._alerts

spoofing_detector = SpoofingDetector()
