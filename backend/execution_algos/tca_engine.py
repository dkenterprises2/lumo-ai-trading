from typing import Dict, Any

class TransactionCostAnalysisEngine:
    """Transaction Cost Analysis (TCA) Engine (Implementation Shortfall, VWAP/TWAP Slippage)."""

    @staticmethod
    def analyze_execution(
        arrival_price: float,
        executed_vwap: float,
        market_vwap: float,
        total_quantity: float
    ) -> Dict[str, Any]:
        implementation_shortfall_bps = round(((executed_vwap - arrival_price) / arrival_price) * 10000.0, 2)
        vwap_slippage_bps = round(((executed_vwap - market_vwap) / market_vwap) * 10000.0, 2)
        
        return {
            "arrival_price": arrival_price,
            "executed_vwap": executed_vwap,
            "market_vwap": market_vwap,
            "implementation_shortfall_bps": implementation_shortfall_bps,
            "vwap_slippage_bps": vwap_slippage_bps,
            "execution_efficiency_score": max(0.0, min(100.0, 100.0 - abs(implementation_shortfall_bps)))
        }

tca_engine = TransactionCostAnalysisEngine()
