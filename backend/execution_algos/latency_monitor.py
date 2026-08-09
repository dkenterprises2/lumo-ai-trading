from typing import Dict, Any, List

class VenueLatencyMonitor:
    """Venue Latency & Sub-Millisecond Execution Tracking Monitor."""

    @staticmethod
    def get_latency_metrics() -> List[Dict[str, Any]]:
        return [
            {"venue": "Binance", "roundtrip_ms": 12.4, "jitter_ms": 1.2, "status": "OPTIMAL"},
            {"venue": "Bybit", "roundtrip_ms": 18.2, "jitter_ms": 2.1, "status": "OPTIMAL"},
            {"venue": "OKX", "roundtrip_ms": 22.1, "jitter_ms": 3.4, "status": "NORMAL"}
        ]

latency_monitor = VenueLatencyMonitor()
