from typing import Dict, Any
from .arbitrage_execution_simulator import ArbitrageExecutionSimulator, ArbitrageExecutionResult
from .arbitrage_risk_filter import ArbitrageRiskFilter

class ArbitrageShadowRouter:
    """Shadow Execution Router for Cross-Exchange Arbitrage Opportunities."""

    def __init__(self):
        self.simulator = ArbitrageExecutionSimulator()
        self.risk_filter = ArbitrageRiskFilter()
        self.history = []

    def route_arbitrage_opportunity(
        self,
        symbol: str,
        buy_exchange: str,
        sell_exchange: str,
        buy_price: float,
        sell_price: float,
        net_spread_pct: float,
        amount_usd: float = 10000.0,
        quote_status: str = "FRESH",
        data_age_ms: float = 0.0
    ) -> Dict[str, Any]:
        risk_res = self.risk_filter.evaluate_opportunity_risk(net_spread_pct=net_spread_pct)
        if not risk_res.passed:
            return {"status": "rejected", "reason": risk_res.reason}

        exec_res = self.simulator.simulate_arbitrage_execution(
            symbol=symbol,
            buy_exchange=buy_exchange,
            sell_exchange=sell_exchange,
            buy_price=buy_price,
            sell_price=sell_price,
            amount_usd=amount_usd,
            quote_status=quote_status,
            data_age_ms=data_age_ms
        )
        self.history.append(exec_res)

        if exec_res.status == "REJECTED":
            return {
                "status": "rejected",
                "reason": exec_res.rejection_reason or "Simulation rejected",
                "execution": exec_res.to_dict()
            }

        return {
            "status": "success",
            "mode": "SHADOW",
            "execution": exec_res.to_dict()
        }
