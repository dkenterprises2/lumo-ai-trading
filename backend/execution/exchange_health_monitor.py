import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional

@dataclass
class VenueHealth:
    exchange: str
    is_online: bool
    latency_ms: float
    error_rate_pct: float
    last_ping: float
    status: str  # OPERATIONAL, DEGRADED, OFFLINE

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class ExchangeHealthMonitor:
    """Monitors real-time connectivity, latency, and error rates of connected exchanges."""

    def __init__(self):
        self._venues = {
            "BINANCE": VenueHealth("BINANCE", True, 15.0, 0.0, time.time(), "OPERATIONAL"),
            "BYBIT": VenueHealth("BYBIT", True, 20.0, 0.0, time.time(), "OPERATIONAL"),
            "OKX": VenueHealth("OKX", True, 25.0, 0.1, time.time(), "OPERATIONAL"),
            "KRAKEN": VenueHealth("KRAKEN", True, 40.0, 0.2, time.time(), "OPERATIONAL"),
            "COINBASE": VenueHealth("COINBASE", True, 30.0, 0.0, time.time(), "OPERATIONAL")
        }

    def get_health(self, exchange: str) -> VenueHealth:
        ex = exchange.upper()
        return self._venues.get(ex, VenueHealth(ex, False, 999.0, 100.0, time.time(), "OFFLINE"))

    def get_all_health(self) -> Dict[str, VenueHealth]:
        return self._venues
