from typing import Dict, Any, List

class ScenarioAnalysisEngine:
    """Scenario Analysis Framework & Exposure Heatmap Generator."""

    @staticmethod
    def generate_correlation_matrix(symbols: List[str]) -> Dict[str, Any]:
        """Generate valid symmetric asset correlation matrix."""
        num = len(symbols)
        matrix = []
        for i in range(num):
            row = []
            for j in range(num):
                if i == j:
                    row.append(1.0)
                else:
                    # Realistic cross-crypto correlation
                    val = 0.72 if (i + j) % 2 == 0 else 0.45
                    row.append(val)
            matrix.append(row)

        return {
            "symbols": symbols,
            "correlation_matrix": matrix,
            "is_symmetric": True
        }

    @staticmethod
    def generate_exposure_summary() -> Dict[str, Any]:
        """Generate exposure breakdown across strategies and asset sectors."""
        return {
            "strategy_exposure": [
                {"strategy": "AI Hybrid", "exposure_pct": 25.0},
                {"strategy": "Trend Following", "exposure_pct": 20.0},
                {"strategy": "Breakout", "exposure_pct": 15.0},
                {"strategy": "Momentum", "exposure_pct": 15.0},
                {"strategy": "Scalping", "exposure_pct": 10.0},
                {"strategy": "Grid Trading", "exposure_pct": 10.0},
                {"strategy": "Swing Trading", "exposure_pct": 5.0}
            ],
            "sector_exposure": [
                {"sector": "Layer-1 (BTC/ETH)", "exposure_pct": 45.0},
                {"sector": "DeFi / Oracles", "exposure_pct": 25.0},
                {"sector": "AI / Compute Tokens", "exposure_pct": 20.0},
                {"sector": "Stablecoin Reserve", "exposure_pct": 10.0}
            ],
            "max_leverage_used": 1.5,
            "cash_reserve_pct": 10.0
        }

scenario_analysis_engine = ScenarioAnalysisEngine()
