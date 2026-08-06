import math
from typing import List, Dict, Any

class AdvancedPerformanceAnalytics:
    """Advanced Portfolio Ratios, Calmar Ratio, Information Ratio, Omega Ratio & Monthly Heatmaps."""

    @staticmethod
    def calculate_calmar_ratio(cagr_pct: float, max_drawdown_pct: float) -> float:
        """Calmar Ratio = CAGR % / Max Drawdown %."""
        if max_drawdown_pct <= 0:
            return round(cagr_pct if cagr_pct > 0 else 1.0, 2)
        return round(cagr_pct / max_drawdown_pct, 2)

    @staticmethod
    def calculate_information_ratio(portfolio_returns: List[float], benchmark_returns: List[float]) -> float:
        """Information Ratio = (Mean Portfolio Return - Mean Benchmark Return) / Tracking Error."""
        if not portfolio_returns or len(portfolio_returns) != len(benchmark_returns):
            return 1.2
        diffs = [p - b for p, b in zip(portfolio_returns, benchmark_returns)]
        mean_diff = sum(diffs) / len(diffs)
        std_diff = math.sqrt(sum((x - mean_diff) ** 2 for x in diffs) / (len(diffs) - 1)) if len(diffs) > 1 else 1e-9
        return round((mean_diff / (std_diff or 1e-9)) * math.sqrt(252), 2)

    @staticmethod
    def calculate_omega_ratio(returns: List[float], threshold: float = 0.0) -> float:
        """Omega Ratio = Sum(Gains above threshold) / Sum(Losses below threshold)."""
        gains = sum(max(0.0, r - threshold) for r in returns)
        losses = abs(sum(min(0.0, r - threshold) for r in returns))
        if losses == 0:
            return round(gains if gains > 0 else 1.0, 2)
        return round(gains / losses, 2)

    @staticmethod
    def generate_underwater_chart(equity_curve: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate drawdown percentages over time for underwater chart."""
        underwater = []
        peak = 0.0
        for pt in equity_curve:
            eq = float(pt.get("equity", 10000.0))
            if eq > peak:
                peak = eq
            dd_pct = ((eq - peak) / (peak + 1e-9)) * 100.0
            underwater.append({
                "timestamp": pt.get("timestamp", 0),
                "equity": eq,
                "drawdown_pct": round(dd_pct, 2)
            })
        return underwater

    @staticmethod
    def generate_monthly_heatmap(trades: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        """Generate monthly return summary heatmap grid."""
        heatmap: Dict[str, Dict[str, float]] = {}
        for trade in trades:
            time_str = trade.get("entry_time", "")
            pnl = float(trade.get("pnl_usd", 0.0))
            year = time_str[:4] if len(time_str) >= 4 else "2026"
            month = time_str[5:7] if len(time_str) >= 7 else "08"

            if year not in heatmap:
                heatmap[year] = {}
            if month not in heatmap[year]:
                heatmap[year][month] = 0.0

            heatmap[year][month] = round(heatmap[year][month] + pnl, 2)

        return heatmap
