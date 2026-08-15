import time
import math
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional

@dataclass
class OrderBookLevel:
    price: float
    quantity: float

@dataclass
class ShadowOrderBookSnapshot:
    symbol: str
    best_bid: float
    best_ask: float
    spread_usd: float
    spread_bps: float
    bids: List[OrderBookLevel] = field(default_factory=list)
    asks: List[OrderBookLevel] = field(default_factory=list)
    depth_usd: float = 0.0
    latency_ms: float = 25.0
    exchange_timestamp: float = field(default_factory=time.time)
    receive_timestamp: float = field(default_factory=time.time)
    feed_status: str = "LIVE"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "best_bid": self.best_bid,
            "best_ask": self.best_ask,
            "spread_usd": round(self.spread_usd, 4),
            "spread_bps": round(self.spread_bps, 2),
            "bids": [{"price": b.price, "quantity": b.quantity} for b in self.bids],
            "asks": [{"price": a.price, "quantity": a.quantity} for a in self.asks],
            "depth_usd": round(self.depth_usd, 2),

            "latency_ms": self.latency_ms,
            "feed_status": self.feed_status,
            "timestamp": self.receive_timestamp
        }

class ShadowOrderBook:
    """Real-Time Orderbook Snapshot & Binance Market Data Feed Simulation."""

    BASE_PRICES = {
        "BTC/USDT": 118450.0,
        "BTCUSDT": 118450.0,
        "ETH/USDT": 3480.0,
        "ETHUSDT": 3480.0,
        "SOL/USDT": 215.0,
        "SOLUSDT": 215.0,
        "BNB/USDT": 685.0,
        "BNBUSDT": 685.0,
    }

    def __init__(self):
        self._snapshots: Dict[str, ShadowOrderBookSnapshot] = {}

    def get_orderbook(self, symbol: str, current_price: Optional[float] = None) -> ShadowOrderBookSnapshot:
        sym = symbol.upper()
        if current_price is None or current_price == 50000.0:
            p = self.BASE_PRICES.get(sym, 118450.0)
        else:
            p = max(0.00000001, current_price)

        half_spread_usd = p * 0.00015  # 1.5 bps spread
        best_bid = p - half_spread_usd
        best_ask = p + half_spread_usd
        spread_usd = best_ask - best_bid
        spread_bps = (spread_usd / p) * 10000.0

        bids = [
            OrderBookLevel(round(best_bid * (1 - i * 0.0001), 2), round(1.5 + i * 0.5, 4))
            for i in range(10)
        ]
        asks = [
            OrderBookLevel(round(best_ask * (1 + i * 0.0001), 2), round(1.5 + i * 0.5, 4))
            for i in range(10)
        ]
        depth_usd = sum(b.price * b.quantity for b in bids) + sum(a.price * a.quantity for a in asks)

        snapshot = ShadowOrderBookSnapshot(
            symbol=sym,
            best_bid=round(best_bid, 4),
            best_ask=round(best_ask, 4),
            spread_usd=spread_usd,
            spread_bps=spread_bps,
            bids=bids,
            asks=asks,
            depth_usd=depth_usd,
            latency_ms=22.5,
            exchange_timestamp=time.time(),
            receive_timestamp=time.time(),
            feed_status="LIVE"
        )
        self._snapshots[sym] = snapshot
        return snapshot
