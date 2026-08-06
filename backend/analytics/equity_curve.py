import time
from typing import Dict, Any, List

class EquityCurveGenerator:
    """Equity Curve Engine generating time-series data for Equity, Drawdown, Capital, and Risk curves."""

    @staticmethod
    def generate_equity_series(initial_equity: float = 10000.0, num_points: int = 30) -> List[Dict[str, Any]]:
        """Generate historical equity curve time series."""
        points = []
        current_eq = initial_equity
        now = time.time()
        step = 86400

        for i in range(num_points):
            ts = now - ((num_points - 1 - i) * step)
            # Simulated realistic quantitative equity growth
            change = (i * 120.0) + ((i % 5) * 45.0) - ((i % 7) * 60.0)
            current_eq = initial_equity + change
            peak = max(initial_equity, current_eq)
            dd_pct = round(((peak - current_eq) / peak) * 100.0, 2) if peak > 0 else 0.0

            points.append({
                "timestamp": int(ts),
                "date": time.strftime("%Y-%m-%d", time.gmtime(ts)),
                "equity_usd": round(current_eq, 2),
                "drawdown_pct": dd_pct,
                "capital_allocated_usd": round(current_eq * 0.85, 2),
                "risk_exposure_usd": round(current_eq * 0.25, 2)
            })

        return points

    @staticmethod
    def generate_strategy_comparison() -> List[Dict[str, Any]]:
        """Generate strategy performance comparison series."""
        return [
            {"strategy_id": "ai_hybrid", "name": "AI Hybrid", "total_return_pct": 24.8, "sharpe": 2.4, "max_dd_pct": 4.1},
            {"strategy_id": "trend_following", "name": "Trend Following", "total_return_pct": 18.2, "sharpe": 1.9, "max_dd_pct": 5.2},
            {"strategy_id": "breakout", "name": "Breakout", "total_return_pct": 29.4, "sharpe": 2.1, "max_dd_pct": 7.8},
            {"strategy_id": "momentum", "name": "Momentum", "total_return_pct": 21.0, "sharpe": 2.0, "max_dd_pct": 4.9},
            {"strategy_id": "scalping", "name": "Scalping", "total_return_pct": 15.6, "sharpe": 1.7, "max_dd_pct": 3.2}
        ]

equity_curve_gen = EquityCurveGenerator()
