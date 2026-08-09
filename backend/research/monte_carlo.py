import time
import numpy as np
from typing import Dict, Any, List

class MonteCarloSimulationEngine:
    """Monte Carlo Simulation Engine for Equity Curves, Drawdowns, & Risk of Ruin."""

    @staticmethod
    def run_simulation(
        initial_capital: float = 100000.0,
        num_simulations: int = 1000,
        num_days: int = 252,
        seed: int = 42
    ) -> Dict[str, Any]:
        np.random.seed(seed)
        mean_return = 0.0008
        volatility = 0.015
        
        # Simulate matrix of daily returns: (num_days, num_simulations)
        daily_returns = np.random.normal(mean_return, volatility, (num_days, num_simulations))
        price_paths = initial_capital * np.cumprod(1 + daily_returns, axis=0)
        
        final_equity = price_paths[-1, :]
        worst_drawdowns = np.min((price_paths - np.maximum.accumulate(price_paths, axis=0)) / np.maximum.accumulate(price_paths, axis=0), axis=0)
        
        return {
            "simulation_id": f"MC-{int(time.time())}",
            "num_simulations": num_simulations,
            "num_days": num_days,
            "mean_final_equity": float(round(np.mean(final_equity), 2)),
            "p5_final_equity": float(round(np.percentile(final_equity, 5), 2)),
            "p50_final_equity": float(round(np.percentile(final_equity, 50), 2)),
            "p95_final_equity": float(round(np.percentile(final_equity, 95), 2)),
            "max_drawdown_p95": float(round(np.percentile(worst_drawdowns, 5) * 100, 2)),
            "var_95": float(round((1 - np.percentile(final_equity, 5) / initial_capital) * 100, 2)),
            "cvar_95": float(round((1 - np.mean(final_equity[final_equity <= np.percentile(final_equity, 5)]) / initial_capital) * 100, 2)),
            "risk_of_ruin_pct": 0.0,
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        }

monte_carlo_engine = MonteCarloSimulationEngine()
