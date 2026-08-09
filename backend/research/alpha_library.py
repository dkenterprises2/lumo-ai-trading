from typing import Dict, Any, List

class AlphaFactorLibrary:
    """Library of Quantitative Alpha Factors (WorldQuant / Formulaic Alphas)."""

    @staticmethod
    def get_alpha_factors() -> List[Dict[str, Any]]:
        return [
            {"id": "ALPHA-001", "name": "CrossSectionalMomentum", "category": "MOMENTUM", "ic": 0.084},
            {"id": "ALPHA-002", "name": "MeanReversionZScore", "category": "VALUE", "ic": 0.062},
            {"id": "ALPHA-003", "name": "VolatilityClusteringRatio", "category": "VOLATILITY", "ic": 0.051},
            {"id": "ALPHA-004", "name": "VolumeImbalanceSpread", "category": "LIQUIDITY", "ic": 0.076}
        ]

alpha_library = AlphaFactorLibrary()
