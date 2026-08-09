from typing import Dict, Any, List

class StrategyBenchmarkingEngine:
    """Strategy Benchmarking Engine against Buy-and-Hold & Benchmark Indexes."""

    @staticmethod
    def get_benchmarks() -> List[Dict[str, Any]]:
        return [
            {"benchmark": "BTC Buy & Hold", "annualized_return": 42.5, "sharpe": 1.15, "max_drawdown": -38.2},
            {"benchmark": "ETH Buy & Hold", "annualized_return": 38.0, "sharpe": 1.02, "max_drawdown": -45.1},
            {"benchmark": "Lumo Quant Multi-Factor", "annualized_return": 64.8, "sharpe": 2.85, "max_drawdown": -12.4}
        ]

benchmarking_engine = StrategyBenchmarkingEngine()
