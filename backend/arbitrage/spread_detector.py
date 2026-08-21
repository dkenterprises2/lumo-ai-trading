from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class ArbitrageSpread:
    symbol: str
    buy_exchange: str
    sell_exchange: str
    buy_price: float
    sell_price: float
    gross_spread_usd: float
    gross_spread_pct: float
    total_fees_bps: float
    transfer_cost_usd: float
    latency_penalty_bps: float
    slippage_bps: float
    market_impact_bps: float
    funding_cost_bps: float
    net_spread_pct: float
    executable_quantity: float
    executable_capacity_usd: float
    is_executable: bool
    rejection_reason: str = "NONE"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class SpreadDetector:
    """Calculates Net Executable Arbitrage Spread with Full Depth & Friction Deductions.
    
    Formula:
    net_edge = gross_spread - buy_fee - sell_fee - slippage - market_impact - latency_cost - funding_cost - transfer_cost
    """

    MAX_QUOTE_AGE_MS = 1500.0
    MINIMUM_NET_EDGE_PCT = 0.02  # 2.0 bps net edge hurdle after fees & slippage
    MINIMUM_CAPACITY_USD = 100.0

    def compute_spread(
        self,
        symbol: str,
        buy_exchange: str,
        sell_exchange: str,
        buy_ask_price: float,
        sell_bid_price: float,
        buy_ask_size: float = 1.0,
        sell_bid_size: float = 1.0,
        is_live_buy: bool = True,
        is_live_sell: bool = True,
        buy_fee_bps: float = 7.5,
        sell_fee_bps: float = 7.5,
        latency_ms: float = 25.0,
        slippage_bps: float = 2.0,
        market_impact_bps: float = 1.0,
        funding_cost_bps: float = 0.5,
        data_age_ms: float = 0.0,
        quote_status: str = "FRESH"
    ) -> ArbitrageSpread:
        exec_qty = round(min(max(0.0, buy_ask_size), max(0.0, sell_bid_size)), 4)
        exec_cap_usd = round(exec_qty * buy_ask_price, 2)

        if buy_ask_price <= 0.0 or sell_bid_price <= 0.0:
            return ArbitrageSpread(
                symbol=symbol,
                buy_exchange=buy_exchange,
                sell_exchange=sell_exchange,
                buy_price=round(buy_ask_price, 2),
                sell_price=round(sell_bid_price, 2),
                gross_spread_usd=0.0,
                gross_spread_pct=0.0,
                total_fees_bps=buy_fee_bps + sell_fee_bps,
                transfer_cost_usd=1.0,
                latency_penalty_bps=0.0,
                slippage_bps=slippage_bps,
                market_impact_bps=market_impact_bps,
                funding_cost_bps=funding_cost_bps,
                net_spread_pct=0.0,
                executable_quantity=0.0,
                executable_capacity_usd=0.0,
                is_executable=False,
                rejection_reason="DATA_UNAVAILABLE"
            )

        # 1. Strict Freshness & Provenance Gate: Reject if cached, fallback, or stale
        if not is_live_buy or not is_live_sell or quote_status in ["DATA_STALE", "STALE", "CACHED", "FALLBACK"] or data_age_ms > self.MAX_QUOTE_AGE_MS:
            gross_usd = sell_bid_price - buy_ask_price
            gross_pct = ((sell_bid_price - buy_ask_price) / buy_ask_price) * 100.0 if buy_ask_price > 0 else 0.0
            
            reason = "FALLBACK_QUOTE" if (quote_status == "FALLBACK" or not is_live_buy or not is_live_sell) else ("STALE_QUOTE" if data_age_ms > self.MAX_QUOTE_AGE_MS else "CACHED_QUOTE")
            return ArbitrageSpread(
                symbol=symbol,
                buy_exchange=buy_exchange,
                sell_exchange=sell_exchange,
                buy_price=round(buy_ask_price, 2),
                sell_price=round(sell_bid_price, 2),
                gross_spread_usd=round(gross_usd, 2),
                gross_spread_pct=round(gross_pct, 4),
                total_fees_bps=buy_fee_bps + sell_fee_bps,
                transfer_cost_usd=1.0,
                latency_penalty_bps=0.0,
                slippage_bps=slippage_bps,
                market_impact_bps=market_impact_bps,
                funding_cost_bps=funding_cost_bps,
                net_spread_pct=0.0,
                executable_quantity=exec_qty,
                executable_capacity_usd=exec_cap_usd,
                is_executable=False,
                rejection_reason=reason
            )

        gross_usd = sell_bid_price - buy_ask_price
        gross_pct = (gross_usd / buy_ask_price) * 100.0 if buy_ask_price > 0 else 0.0

        total_fees_bps = buy_fee_bps + sell_fee_bps
        latency_penalty_bps = (latency_ms / 100.0) * 1.5  # 1.5 bps per 100ms
        transfer_cost_usd = 1.0
        transfer_cost_bps = (transfer_cost_usd / max(100.0, exec_cap_usd)) * 10000.0

        total_friction_bps = total_fees_bps + latency_penalty_bps + slippage_bps + market_impact_bps + funding_cost_bps + transfer_cost_bps
        net_pct = gross_pct - (total_friction_bps / 100.0)

        # 2. Depth & Liquidity Gate
        if exec_cap_usd < self.MINIMUM_CAPACITY_USD:
            return ArbitrageSpread(
                symbol=symbol,
                buy_exchange=buy_exchange,
                sell_exchange=sell_exchange,
                buy_price=round(buy_ask_price, 2),
                sell_price=round(sell_bid_price, 2),
                gross_spread_usd=round(gross_usd, 2),
                gross_spread_pct=round(gross_pct, 4),
                total_fees_bps=round(total_fees_bps, 2),
                transfer_cost_usd=transfer_cost_usd,
                latency_penalty_bps=round(latency_penalty_bps, 2),
                slippage_bps=round(slippage_bps, 2),
                market_impact_bps=round(market_impact_bps, 2),
                funding_cost_bps=round(funding_cost_bps, 2),
                net_spread_pct=round(net_pct, 4),
                executable_quantity=exec_qty,
                executable_capacity_usd=exec_cap_usd,
                is_executable=False,
                rejection_reason="INSUFFICIENT_LIQUIDITY"
            )

        is_exec = net_pct >= self.MINIMUM_NET_EDGE_PCT
        reason = "NONE" if is_exec else ("FEE_FRICTION_REJECT" if gross_pct > 0 else "NEGATIVE_SPREAD")

        return ArbitrageSpread(
            symbol=symbol,
            buy_exchange=buy_exchange,
            sell_exchange=sell_exchange,
            buy_price=round(buy_ask_price, 2),
            sell_price=round(sell_bid_price, 2),
            gross_spread_usd=round(gross_usd, 2),
            gross_spread_pct=round(gross_pct, 4),
            total_fees_bps=round(total_fees_bps, 2),
            transfer_cost_usd=transfer_cost_usd,
            latency_penalty_bps=round(latency_penalty_bps, 2),
            slippage_bps=round(slippage_bps, 2),
            market_impact_bps=round(market_impact_bps, 2),
            funding_cost_bps=round(funding_cost_bps, 2),
            net_spread_pct=round(net_pct, 4),
            executable_quantity=exec_qty,
            executable_capacity_usd=exec_cap_usd,
            is_executable=is_exec,
            rejection_reason=reason
        )
