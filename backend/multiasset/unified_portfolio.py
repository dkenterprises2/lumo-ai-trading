from typing import Dict, Any
from backend.multiasset.defi_portfolio import defi_portfolio
from backend.multiasset.cefi_portfolio import cefi_portfolio

class UnifiedPortfolioAggregator:
    """Unified CeFi + DeFi Global NAV Aggregator."""

    @staticmethod
    def calculate_global_nav(base_currency: str = "USD") -> Dict[str, Any]:
        cefi_total = sum(p["value_usd"] for p in cefi_portfolio.get_positions())
        defi_total = sum(p["value_usd"] for p in defi_portfolio.get_positions())
        global_nav = cefi_total + defi_total

        return {
            "base_currency": base_currency,
            "cefi_total_usd": cefi_total,
            "defi_total_usd": defi_total,
            "global_nav_usd": global_nav
        }

unified_portfolio = UnifiedPortfolioAggregator()
