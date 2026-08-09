from typing import Dict, Any, List

class LiquidityHeatmapGenerator:
    """Historical Order Book Resting Liquidity Density Heatmap Generator."""

    @staticmethod
    def get_heatmap(symbol: str = "BTC/USDT") -> Dict[str, Any]:
        return {
            "symbol": symbol,
            "heatmap_matrix": [
                {"price_level": 64800.0, "density": 0.95, "cluster_type": "SUPPORT"},
                {"price_level": 64900.0, "density": 0.88, "cluster_type": "RESISTANCE"}
            ]
        }

liquidity_heatmap = LiquidityHeatmapGenerator()
