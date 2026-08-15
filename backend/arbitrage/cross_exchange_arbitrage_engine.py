import uuid
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional

from .exchange_price_collector import ExchangePriceCollector
from .spread_detector import SpreadDetector, ArbitrageSpread
from .funding_rate_collector import FundingRateCollector
from .arbitrage_metrics import ArbitrageMetricsTracker

@dataclass
class CrossExchangeOpportunity:
    opp_id: str = field(default_factory=lambda: f"ARB-{uuid.uuid4().hex[:8].upper()}")
    symbol: str = "BTC/USDT"
    opp_type: str = "SPOT_SPOT"  # SPOT_SPOT, BASIS, FUNDING_RATE, TRIANGULAR
    buy_exchange: str = "BINANCE"
    sell_exchange: str = "BYBIT"
    buy_price: float = 0.0
    sell_price: float = 0.0
    gross_spread_pct: float = 0.0
    net_spread_pct: float = 0.0
    estimated_profit_usd: float = 0.0
    score: float = 0.0
    status: str = "EXECUTABLE"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class CrossExchangeArbitrageEngine:
    """Master Cross-Exchange Arbitrage Detector."""

    def __init__(self):
        self.collector = ExchangePriceCollector()
        self.detector = SpreadDetector()
        self.funding_collector = FundingRateCollector()

    def scan_opportunities(self, symbol: str = "BTC/USDT") -> List[CrossExchangeOpportunity]:
        quotes = self.collector.fetch_all_quotes(symbol)
        opps = []
        tracker = ArbitrageMetricsTracker()

        exchanges = list(quotes.keys())
        for i in range(len(exchanges)):
            for j in range(len(exchanges)):
                if i != j:
                    buy_ex = exchanges[i]
                    sell_ex = exchanges[j]
                    q_buy = quotes[buy_ex]
                    q_sell = quotes[sell_ex]

                    # Staleness / availability check
                    if q_buy.status == "DATA_UNAVAILABLE" or q_sell.status == "DATA_UNAVAILABLE":
                        continue

                    if q_buy.status == "DATA_STALE" or q_sell.status == "DATA_STALE":
                        tracker.record_opportunity(
                            is_executable=False,
                            net_spread=0.0,
                            rejected_reason="Quote data stale"
                        )
                        continue

                    if q_buy.ask_price > 0.0 and q_sell.bid_price > q_buy.ask_price:
                        max_age = max(q_buy.data_age_ms, q_sell.data_age_ms)
                        spread = self.detector.compute_spread(
                            symbol=symbol,
                            buy_exchange=buy_ex,
                            sell_exchange=sell_ex,
                            buy_ask_price=q_buy.ask_price,
                            sell_bid_price=q_sell.bid_price,
                            buy_fee_bps=self.collector.EXCHANGE_FEES_BPS.get(buy_ex, 7.5),
                            sell_fee_bps=self.collector.EXCHANGE_FEES_BPS.get(sell_ex, 7.5),
                            latency_ms=(q_buy.latency_ms + q_sell.latency_ms) / 2.0,
                            data_age_ms=max_age,
                            quote_status=q_buy.status if q_buy.status == q_sell.status else "FRESH"
                        )

                        tracker.record_opportunity(
                            is_executable=spread.is_executable,
                            net_spread=spread.net_spread_pct,
                            rejected_reason=None if spread.is_executable else spread.rejection_reason
                        )

                        if spread.is_executable:
                            prof_usd = 10000.0 * (spread.net_spread_pct / 100.0)
                            opps.append(CrossExchangeOpportunity(
                                symbol=symbol,
                                opp_type="SPOT_SPOT",
                                buy_exchange=buy_ex,
                                sell_exchange=sell_ex,
                                buy_price=spread.buy_price,
                                sell_price=spread.sell_price,
                                gross_spread_pct=spread.gross_spread_pct,
                                net_spread_pct=spread.net_spread_pct,
                                estimated_profit_usd=round(prof_usd, 2),
                                score=round(spread.net_spread_pct * 100.0, 1),
                                status="EXECUTABLE"
                            ))
        return opps
