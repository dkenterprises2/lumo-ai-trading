from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional

@dataclass
class VenueScore:
    exchange: str
    score: float
    liquidity_score: float
    spread_score: float
    latency_score: float
    fee_score: float
    health_score: float
    bid: float
    ask: float
    spread_pct: float
    is_available: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class SmartOrderRouter:
    """Institutional Smart Order Router (SOR) for Best-Execution Venue Selection."""

    SUPPORTED_EXCHANGES = ["BINANCE", "BYBIT", "OKX", "KRAKEN", "COINBASE"]

    def __init__(self):
        # Default mock metrics per venue
        self.venue_metrics = {
            "BINANCE": {"liquidity": 0.95, "spread_pct": 0.01, "latency_ms": 15, "fee_bps": 7.5, "health": 1.0},
            "BYBIT": {"liquidity": 0.90, "spread_pct": 0.012, "latency_ms": 20, "fee_bps": 8.0, "health": 1.0},
            "OKX": {"liquidity": 0.85, "spread_pct": 0.015, "latency_ms": 25, "fee_bps": 8.5, "health": 1.0},
            "KRAKEN": {"liquidity": 0.75, "spread_pct": 0.02, "latency_ms": 40, "fee_bps": 12.0, "health": 1.0},
            "COINBASE": {"liquidity": 0.80, "spread_pct": 0.018, "latency_ms": 30, "fee_bps": 15.0, "health": 1.0}
        }

    def score_venue(self, exchange: str, symbol: str, quantity: float, current_price: float = 50000.0) -> VenueScore:
        metrics = self.venue_metrics.get(exchange.upper(), {"liquidity": 0.5, "spread_pct": 0.05, "latency_ms": 100, "fee_bps": 20.0, "health": 0.5})

        liq_s = metrics["liquidity"]
        spread_s = max(0.0, 1.0 - (metrics["spread_pct"] / 0.10))
        lat_s = max(0.0, 1.0 - (metrics["latency_ms"] / 200.0))
        fee_s = max(0.0, 1.0 - (metrics["fee_bps"] / 50.0))
        health_s = metrics["health"]

        # Institutional Weighted Venue Scoring Formula
        total_score = (liq_s * 0.35) + (spread_s * 0.25) + (lat_s * 0.15) + (fee_s * 0.15) + (health_s * 0.10)

        half_spread = current_price * (metrics["spread_pct"] / 100.0) / 2.0
        bid = current_price - half_spread
        ask = current_price + half_spread

        return VenueScore(
            exchange=exchange.upper(),
            score=round(total_score, 4),
            liquidity_score=round(liq_s, 4),
            spread_score=round(spread_s, 4),
            latency_score=round(lat_s, 4),
            fee_score=round(fee_s, 4),
            health_score=round(health_s, 4),
            bid=round(bid, 4),
            ask=round(ask, 4),
            spread_pct=round(metrics["spread_pct"], 4),
            is_available=health_s > 0.0
        )

    def route_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str = "MARKET",
        requested_exchange: Optional[str] = None,
        price: Optional[float] = None
    ) -> VenueScore:
        """Select best execution venue based on smart routing score."""
        current_p = price if (price and price > 0) else 50000.0

        if requested_exchange and requested_exchange.upper() in self.SUPPORTED_EXCHANGES:
            return self.score_venue(requested_exchange.upper(), symbol, quantity, current_p)

        scores = [self.score_venue(ex, symbol, quantity, current_p) for ex in self.SUPPORTED_EXCHANGES]
        available_scores = [s for s in scores if s.is_available]

        if not available_scores:
            # Fallback to Binance
            return self.score_venue("BINANCE", symbol, quantity, current_p)

        best_venue = max(available_scores, key=lambda s: s.score)
        return best_venue
