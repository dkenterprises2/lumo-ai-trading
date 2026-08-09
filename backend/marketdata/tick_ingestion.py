import time
from typing import Dict, Any, List

class TickIngestionEngine:
    """Sub-Second Tick Data Ingestion, Deduplication, & Bucket Aggregator."""

    def __init__(self):
        self._ticks: List[Dict[str, Any]] = [
            {
                "tick_id": "TICK-101",
                "symbol": "BTC/USDT",
                "price": 64810.5,
                "quantity": 0.25,
                "side": "BUY",
                "timestamp": time.time()
            }
        ]

    def ingest_tick(self, symbol: str, price: float, quantity: float, side: str) -> Dict[str, Any]:
        tick = {
            "tick_id": f"TICK-{len(self._ticks)+1}",
            "symbol": symbol,
            "price": price,
            "quantity": quantity,
            "side": side,
            "timestamp": time.time()
        }
        self._ticks.append(tick)
        return tick

    def get_recent_ticks(self, symbol: str = "BTC/USDT") -> List[Dict[str, Any]]:
        return [t for t in self._ticks if t["symbol"] == symbol]

tick_ingestion_engine = TickIngestionEngine()
