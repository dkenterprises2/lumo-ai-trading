import uuid
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional

from .exchange_price_collector import ExchangePriceCollector, ExchangeQuote
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
    executable_quantity: float = 0.0
    executable_capacity_usd: float = 0.0
    estimated_profit_usd: float = 0.0
    quote_age_ms: float = 0.0
    is_live_quote: bool = True
    score: float = 0.0
    status: str = "EXECUTABLE"  # EXECUTABLE, THEORETICAL, STALE_CACHED, INSUFFICIENT_LIQUIDITY
    rejection_reason: str = "NONE"
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class CrossExchangeArbitrageEngine:
    """Master Depth-Aware & Freshness-Gated Cross-Exchange Arbitrage Engine."""

    def __init__(self):
        self.collector = ExchangePriceCollector()
        self.detector = SpreadDetector()
        self.funding_collector = FundingRateCollector()

    def scan_opportunities(self, symbol: str = "BTC/USDT") -> List[CrossExchangeOpportunity]:
        quotes = self.collector.fetch_all_quotes(symbol)
        opps: List[CrossExchangeOpportunity] = []
        tracker = ArbitrageMetricsTracker()
        from .arbitrage_evidence_store import ArbitrageForensicEvent, arbitrage_evidence_store
        import json
        import datetime

        scan_cycle_id = f"CYCLE-{int(time.time() * 1000)}"
        exchanges = list(quotes.keys())

        for i in range(len(exchanges)):
            for j in range(len(exchanges)):
                if i != j:
                    buy_ex = exchanges[i]
                    sell_ex = exchanges[j]
                    q_buy: Optional[ExchangeQuote] = quotes.get(buy_ex)
                    q_sell: Optional[ExchangeQuote] = quotes.get(sell_ex)

                    # Determine gross profitability
                    is_gross_profitable = False
                    buy_ask = q_buy.ask_price if q_buy else 0.0
                    buy_bid = q_buy.bid_price if q_buy else 0.0
                    sell_bid = q_sell.bid_price if q_sell else 0.0
                    sell_ask = q_sell.ask_price if q_sell else 0.0
                    
                    if q_buy and q_sell and buy_ask > 0.0 and sell_bid > buy_ask:
                        is_gross_profitable = True

                    gross_diff = sell_bid - buy_ask
                    gross_pct = (gross_diff / buy_ask) * 100.0 if buy_ask > 0 else 0.0
                    gross_bps = gross_pct * 100.0

                    buy_fee_bps = self.collector.EXCHANGE_FEES_BPS.get(buy_ex, 7.5)
                    sell_fee_bps = self.collector.EXCHANGE_FEES_BPS.get(sell_ex, 7.5)
                    buy_depth = q_buy.ask_size if q_buy else 0.0
                    sell_depth = q_sell.bid_size if q_sell else 0.0
                    exec_qty = round(min(max(0.0, buy_depth), max(0.0, sell_depth)), 4)
                    exec_cap = round(exec_qty * buy_ask, 2)

                    max_age = max(q_buy.data_age_ms if q_buy else 9999.0, q_sell.data_age_ms if q_sell else 9999.0)
                    avg_latency = ((q_buy.latency_ms if q_buy else 50.0) + (q_sell.latency_ms if q_sell else 50.0)) / 2.0

                    # 1. ALWAYS increment scanned route counter BEFORE any filtering
                    tracker.record_scanned_route(is_gross_profitable=is_gross_profitable)

                    # Default forensic event skeleton
                    event = ArbitrageForensicEvent(
                        symbol=symbol,
                        route_id=f"{buy_ex}->{sell_ex}",
                        buy_exchange=buy_ex,
                        sell_exchange=sell_ex,
                        buy_quote_timestamp=q_buy.source_timestamp if q_buy else time.time(),
                        sell_quote_timestamp=q_sell.source_timestamp if q_sell else time.time(),
                        buy_bid=buy_bid,
                        buy_ask=buy_ask,
                        sell_bid=sell_bid,
                        sell_ask=sell_ask,
                        buy_price_used=buy_ask,
                        sell_price_used=sell_bid,
                        gross_spread_bps=round(gross_bps, 2),
                        gross_spread_pct=round(gross_pct, 4),
                        estimated_quantity=exec_qty,
                        orderbook_depth_buy=buy_depth,
                        orderbook_depth_sell=sell_depth,
                        estimated_fee_buy=buy_fee_bps,
                        estimated_fee_sell=sell_fee_bps,
                        estimated_slippage_buy=2.0,
                        estimated_slippage_sell=2.0,
                        latency_ms=round(avg_latency, 1),
                        quote_age_ms=round(max_age, 1),
                        scan_cycle_id=scan_cycle_id,
                        market_data_source=f"{buy_ex} & {sell_ex} Public REST / WebSocket Feeds",
                        market_data_provider=buy_ex,
                        source_timestamp=min(q_buy.source_timestamp if q_buy else time.time(), q_sell.source_timestamp if q_sell else time.time()),
                        received_timestamp=time.time(),
                        data_age_ms=round(max_age, 1)
                    )

                    # Snapshot dictionary for 100% deterministic replay
                    snapshot_dict = {
                        "symbol": symbol,
                        "buy_exchange": buy_ex,
                        "sell_exchange": sell_ex,
                        "buy_ask": buy_ask,
                        "sell_bid": sell_bid,
                        "buy_fee_bps": buy_fee_bps,
                        "sell_fee_bps": sell_fee_bps,
                        "latency_ms": avg_latency,
                        "quote_age_ms": max_age,
                        "quote_status": q_buy.status if (q_buy and q_sell and q_buy.status == q_sell.status) else "FRESH",
                        "is_live_buy": q_buy.is_live_quote if q_buy else False,
                        "is_live_sell": q_sell.is_live_quote if q_sell else False,
                        "buy_depth": buy_depth,
                        "sell_depth": sell_depth
                    }
                    event.raw_snapshot_json = json.dumps(snapshot_dict)

                    # 2. Check for missing or offline quotes
                    if not q_buy or not q_sell or q_buy.status == "DATA_UNAVAILABLE" or q_sell.status == "DATA_UNAVAILABLE":
                        tracker.record_rejection("DATA_UNAVAILABLE_REJECT")
                        event.decision = "REJECTED"
                        event.rejection_reason = "DATA_UNAVAILABLE"
                        event.category = "NEGATIVE_SPREAD"
                        event.freshness_result = "OFFLINE"
                        arbitrage_evidence_store.record_event(event)
                        continue

                    # 3. Check for Fallback or Cached quotes
                    if q_buy.is_fallback or q_sell.is_fallback or q_buy.status == "FALLBACK" or q_sell.status == "FALLBACK":
                        tracker.record_rejection("FALLBACK_QUOTE_REJECT")
                        event.decision = "REJECTED"
                        event.rejection_reason = "FALLBACK_QUOTE"
                        event.category = "CACHED_FALLBACK"
                        event.freshness_result = "FALLBACK"
                        arbitrage_evidence_store.record_event(event)
                        continue

                    if max_age > self.collector.MAX_QUOTE_AGE_MS or q_buy.status == "STALE" or q_sell.status == "STALE":
                        tracker.record_rejection("STALE_QUOTE_REJECT")
                        event.decision = "REJECTED"
                        event.rejection_reason = "STALE_QUOTE"
                        event.category = "STALE_QUOTES"
                        event.freshness_result = "STALE"
                        arbitrage_evidence_store.record_event(event)
                        continue

                    # 4. Check for Negative Gross Spread
                    if not is_gross_profitable:
                        tracker.record_rejection("NEGATIVE_SPREAD_REJECT")
                        event.decision = "REJECTED"
                        event.rejection_reason = "NEGATIVE_SPREAD"
                        event.category = "NEGATIVE_SPREAD"
                        arbitrage_evidence_store.record_event(event)
                        continue

                    # 5. Evaluate Complete Spread, Fees, Slippage & Latency
                    spread: ArbitrageSpread = self.detector.compute_spread(
                        symbol=symbol,
                        buy_exchange=buy_ex,
                        sell_exchange=sell_ex,
                        buy_ask_price=q_buy.ask_price,
                        sell_bid_price=q_sell.bid_price,
                        buy_ask_size=q_buy.ask_size,
                        sell_bid_size=q_sell.bid_size,
                        is_live_buy=q_buy.is_live_quote,
                        is_live_sell=q_sell.is_live_quote,
                        buy_fee_bps=buy_fee_bps,
                        sell_fee_bps=sell_fee_bps,
                        latency_ms=avg_latency,
                        data_age_ms=max_age,
                        quote_status=q_buy.status if q_buy.status == q_sell.status else "FRESH"
                    )

                    event.net_edge_pct = spread.net_spread_pct
                    event.net_edge_bps = round(spread.net_spread_pct * 100.0, 2)
                    event.gross_spread_pct = spread.gross_spread_pct
                    event.gross_spread_bps = round(spread.gross_spread_pct * 100.0, 2)

                    if spread.is_executable:
                        tracker.record_executable_opportunity(spread.net_spread_pct)
                        prof_usd = spread.executable_capacity_usd * (spread.net_spread_pct / 100.0)
                        
                        event.decision = "EXECUTABLE"
                        event.rejection_reason = "NONE"
                        event.category = "EXECUTABLE"
                        event.execution_status = "EXECUTABLE"
                        arbitrage_evidence_store.record_event(event)

                        opp = CrossExchangeOpportunity(
                            symbol=symbol,
                            opp_type="SPOT_SPOT",
                            buy_exchange=buy_ex,
                            sell_exchange=sell_ex,
                            buy_price=spread.buy_price,
                            sell_price=spread.sell_price,
                            gross_spread_pct=spread.gross_spread_pct,
                            net_spread_pct=spread.net_spread_pct,
                            executable_quantity=spread.executable_quantity,
                            executable_capacity_usd=spread.executable_capacity_usd,
                            estimated_profit_usd=round(prof_usd, 2),
                            quote_age_ms=round(max_age, 1),
                            is_live_quote=True,
                            score=round(spread.net_spread_pct * 100.0, 1),
                            status="EXECUTABLE",
                            rejection_reason="NONE"
                        )
                        opps.append(opp)
                    else:
                        tracker.record_rejection(spread.rejection_reason)
                        event.decision = "REJECTED"
                        event.rejection_reason = spread.rejection_reason
                        r_lower = spread.rejection_reason.lower()
                        if "fee" in r_lower:
                            event.category = "FEE_REJECTIONS"
                        elif "slippage" in r_lower:
                            event.category = "SLIPPAGE_REJECTIONS"
                        elif "liquidity" in r_lower or "depth" in r_lower:
                            event.category = "LIQUIDITY_REJECTIONS"
                        elif "risk" in r_lower:
                            event.category = "RISK_REJECTIONS"
                        elif "gov" in r_lower or "kill" in r_lower:
                            event.category = "GOVERNANCE_REJECTIONS"
                        elif spread.net_spread_pct > 0:
                            event.category = "NET_PROFITABLE"
                        else:
                            event.category = "NEGATIVE_SPREAD"
                        arbitrage_evidence_store.record_event(event)

        return opps

# Global Singleton
cross_exchange_engine = CrossExchangeArbitrageEngine()
