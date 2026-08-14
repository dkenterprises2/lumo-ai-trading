from typing import List, Any

class ArbitrageOpportunityRanker:
    """Ranks Arbitrage Opportunities by Net Executable Edge and Risk-Adjusted Score."""

    def rank_opportunities(self, opportunities: List[Any]) -> List[Any]:
        return sorted(opportunities, key=lambda x: getattr(x, 'net_spread_pct', 0.0), reverse=True)
