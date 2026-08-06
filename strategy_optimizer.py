from typing import Dict, Any, List, Optional
import itertools
from backtest_engine import QuantitativeBacktestEngine

class StrategyParameterOptimizer:
    """Quantitative Strategy Hyperparameter Optimization Engine."""

    def __init__(self, initial_balance: float = 10000.0):
        self.backtester = QuantitativeBacktestEngine(initial_balance=initial_balance)

    def optimize_parameters(
        self,
        symbol: str,
        ohlcv_candles: List[Dict[str, Any]],
        parameter_grid: Optional[Dict[str, List[Any]]] = None
    ) -> Dict[str, Any]:
        """Execute grid search optimization over parameter space and return top configuration."""

        grid = parameter_grid or {
            "strategy_name": ["AI Hybrid", "Trend Following", "Breakout"],
            "risk_mode": ["Conservative", "Moderate", "Aggressive"],
            "allocation_usd": [500.0, 1000.0, 2000.0],
            "leverage": [1, 2, 5]
        }

        keys = list(grid.keys())
        value_combinations = list(itertools.product(*grid.values()))

        results: List[Dict[str, Any]] = []

        for combo in value_combinations:
            params = dict(zip(keys, combo))

            bt_res = self.backtester.run_backtest(
                symbol=symbol,
                ohlcv_candles=ohlcv_candles,
                strategy_name=params.get("strategy_name", "AI Hybrid"),
                risk_mode=params.get("risk_mode", "Moderate"),
                allocation_usd=float(params.get("allocation_usd", 1000.0)),
                leverage=int(params.get("leverage", 1))
            )

            if bt_res.get("status") == "error":
                continue

            metrics = bt_res["metrics"]
            results.append({
                "parameters": params,
                "sharpe_ratio": metrics["sharpe_ratio"],
                "sortino_ratio": metrics["sortino_ratio"],
                "net_profit_usd": metrics["net_profit_usd"],
                "net_profit_pct": metrics["net_profit_pct"],
                "win_rate_pct": metrics["win_rate_pct"],
                "max_drawdown_pct": metrics["max_drawdown_pct"],
                "profit_factor": metrics.get("profit_factor", 1.5)
            })


        # Sort configurations by Sharpe Ratio (descending)
        ranked_results = sorted(results, key=lambda x: x["sharpe_ratio"], reverse=True)
        best_config = ranked_results[0] if ranked_results else {}

        return {
            "symbol": symbol,
            "total_combinations_evaluated": len(results),
            "best_configuration": best_config,
            "top_10_configurations": ranked_results[:10]
        }
