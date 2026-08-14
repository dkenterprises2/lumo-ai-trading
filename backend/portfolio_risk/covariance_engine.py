import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional

class CovarianceEngine:
    """Computes multi-asset covariance matrices and portfolio volatility attribution."""

    def compute_covariance(self, returns_df: pd.DataFrame, annualize_factor: int = 365) -> pd.DataFrame:
        """Compute annualized covariance matrix from asset returns."""
        if returns_df.empty or returns_df.shape[1] < 1:
            return pd.DataFrame()
        return (returns_df.cov() * annualize_factor).fillna(0.0)

    def calculate_portfolio_variance(
        self,
        cov_matrix: pd.DataFrame,
        weights: Dict[str, float]
    ) -> float:
        """Calculate total portfolio variance given asset weight dict."""
        if cov_matrix.empty or not weights:
            return 0.0

        symbols = [s for s in cov_matrix.columns if s in weights]
        if not symbols:
            return 0.0

        w = np.array([weights[s] for s in symbols])
        cov = cov_matrix.loc[symbols, symbols].values
        var = float(np.dot(w.T, np.dot(cov, w)))
        return max(0.0, var)

    def calculate_marginal_risk_contribution(
        self,
        cov_matrix: pd.DataFrame,
        weights: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate Marginal Risk Contribution (MRC) per asset in portfolio."""
        if cov_matrix.empty or not weights:
            return {}

        symbols = [s for s in cov_matrix.columns if s in weights]
        if not symbols:
            return {}

        w = np.array([weights[s] for s in symbols])
        cov = cov_matrix.loc[symbols, symbols].values
        port_var = float(np.dot(w.T, np.dot(cov, w)))
        port_vol = np.sqrt(port_var) if port_var > 0 else 1e-9

        # Marginal Contribution to Risk (MCR) = (Cov * w) / port_vol
        mcr = np.dot(cov, w) / port_vol
        # Percentage Risk Contribution (PRC) = (w * MCR) / port_vol
        prc = (w * mcr) / port_vol

        return {symbols[i]: float(prc[i]) for i in range(len(symbols))}
