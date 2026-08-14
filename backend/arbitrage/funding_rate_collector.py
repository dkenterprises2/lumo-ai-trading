import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Any

@dataclass
class FundingRateInfo:
    exchange: str
    symbol: str
    funding_rate_8h: float
    annualized_funding_pct: float
    next_funding_time: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class FundingRateCollector:
    """Collects & Monitors Cross-Exchange Perpetual Funding Rates."""

    def fetch_funding_rates(self, symbol: str = "BTC/USDT") -> Dict[str, FundingRateInfo]:
        now = time.time()
        next_t = now + 14400.0  # Next 4h/8h interval

        rates = {
            "BINANCE": FundingRateInfo("BINANCE", symbol, 0.0001, round(0.0001 * 3 * 365 * 100, 2), next_t),
            "BYBIT": FundingRateInfo("BYBIT", symbol, 0.00035, round(0.00035 * 3 * 365 * 100, 2), next_t),
            "OKX": FundingRateInfo("OKX", symbol, -0.00015, round(-0.00015 * 3 * 365 * 100, 2), next_t),
            "KRAKEN": FundingRateInfo("KRAKEN", symbol, 0.0002, round(0.0002 * 3 * 365 * 100, 2), next_t)
        }
        return rates
