import numpy as np
import pandas as pd
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional, Tuple

@dataclass
class CorrelationRisk:
    symbol: str
    correlated_symbols: List[str]
    average_correlation: float
    cluster_id: int
    cluster_exposure_pct: float
    risk_score: float  # 0.0 (low) to 1.0 (critical)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class CorrelationEngine:
    """Calculates rolling Pearson/EWMA correlation matrices and cluster exposures."""

    DEFAULT_GROUPS = {
        0: ["BTC/USDT", "ETH/USDT", "SOL/USDT", "AVAX/USDT", "LINK/USDT"], # Major Alts Cluster
        1: ["DOGE/USDT", "SHIB/USDT", "PEPE/USDT", "FLOKI/USDT"],         # Meme Cluster
        2: ["USDT/USD", "USDC/USDT"]                                    # Stable Cluster
    }

    def __init__(self, windows: Optional[List[int]] = None):
        self.windows = windows or [20, 50, 100, 200]

    def compute_correlation_matrix(
        self,
        returns_df: pd.DataFrame,
        window: int = 50,
        ewma: bool = False
    ) -> pd.DataFrame:
        """Compute rolling Pearson or Exponentially Weighted correlation matrix."""
        if returns_df.empty or returns_df.shape[1] < 2:
            cols = returns_df.columns if not returns_df.empty else ["BTC/USDT", "ETH/USDT"]
            return pd.DataFrame(np.eye(len(cols)), index=cols, columns=cols)

        df = returns_df.tail(window)
        if ewma:
            cov = df.ewm(span=window).cov()
            # Extract last slice of covariance
            last_cov = cov.iloc[-len(df.columns):]
            std = np.sqrt(np.diag(last_cov))
            corr = last_cov.values / np.outer(std, std)
            return pd.DataFrame(corr, index=df.columns, columns=df.columns).fillna(0.0)
        else:
            return df.corr().fillna(0.0)

    def analyze_positions_correlation(
        self,
        positions: Dict[str, Dict[str, Any]],
        portfolio_value: float,
        price_history_df: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """Analyze cross-position correlation risk and clustering."""
        if not positions or portfolio_value <= 0:
            return {
                "correlation_matrix": {},
                "average_correlation": 0.0,
                "correlation_risk_score": 0.0,
                "symbol_risks": {},
                "cluster_exposures": {}
            }

        symbols = list(positions.keys())
        if len(symbols) == 1:
            sym = symbols[0]
            pos_val = positions[sym].get("notional_val_usd", positions[sym].get("margin_usd", 0) * positions[sym].get("leverage", 1))
            exp_pct = (pos_val / portfolio_value) * 100.0
            r_item = CorrelationRisk(
                symbol=sym,
                correlated_symbols=[],
                average_correlation=0.0,
                cluster_id=0,
                cluster_exposure_pct=exp_pct,
                risk_score=0.0
            )
            return {
                "correlation_matrix": {sym: {sym: 1.0}},
                "average_correlation": 0.0,
                "correlation_risk_score": 0.0,
                "symbol_risks": {sym: r_item.to_dict()},
                "cluster_exposures": {0: exp_pct}
            }

        # Build empirical correlation matrix or fallback synthetic correlation matrix
        if price_history_df is not None and not price_history_df.empty:
            returns = price_history_df.pct_change().dropna()
            corr_df = self.compute_correlation_matrix(returns, window=50)
        else:
            # Fallback synthetic correlation lookup
            n = len(symbols)
            matrix = np.eye(n)
            for i in range(n):
                for j in range(i + 1, n):
                    s1, s2 = symbols[i], symbols[j]
                    # High correlation for major pairs
                    if ("BTC" in s1 or "ETH" in s1) and ("BTC" in s2 or "ETH" in s2 or "SOL" in s2):
                        val = 0.85
                    elif ("PEPE" in s1 or "SHIB" in s1 or "FLOKI" in s1) and ("PEPE" in s2 or "SHIB" in s2 or "FLOKI" in s2):
                        val = 0.90
                    else:
                        val = 0.45
                    matrix[i, j] = val
                    matrix[j, i] = val
            corr_df = pd.DataFrame(matrix, index=symbols, columns=symbols)

        symbol_risks = {}
        cluster_exposures: Dict[int, float] = {}

        # Calculate cluster exposures
        for idx, sym in enumerate(symbols):
            pos = positions[sym]
            notional = pos.get("notional_val_usd", pos.get("margin_usd", 0) * pos.get("leverage", 1))
            exp_pct = (notional / portfolio_value) * 100.0

            # Assign cluster ID based on symbol pattern
            cid = 0
            if any(m in sym for m in ["PEPE", "SHIB", "FLOKI", "DOGE"]):
                cid = 1
            elif any(s in sym for s in ["USDT", "USDC"]) and "/" not in sym:
                cid = 2

            cluster_exposures[cid] = cluster_exposures.get(cid, 0.0) + exp_pct

            # Correlated symbols (>0.75)
            row = corr_df[sym] if sym in corr_df.columns else pd.Series()
            corr_syms = [s for s in symbols if s != sym and row.get(s, 0) >= 0.75]
            avg_corr = float(row.drop(sym).mean()) if len(symbols) > 1 and sym in row else 0.0
            r_score = min(1.0, max(0.0, avg_corr * (len(corr_syms) / max(1, len(symbols) - 1))))

            symbol_risks[sym] = CorrelationRisk(
                symbol=sym,
                correlated_symbols=corr_syms,
                average_correlation=round(avg_corr, 4),
                cluster_id=cid,
                cluster_exposure_pct=round(exp_pct, 2),
                risk_score=round(r_score, 4)
            ).to_dict()

        # Overall correlation risk score (0.0 to 1.0)
        off_diag = corr_df.values[~np.eye(corr_df.shape[0], dtype=bool)]
        avg_overall_corr = float(np.mean(off_diag)) if len(off_diag) > 0 else 0.0
        portfolio_corr_risk = min(1.0, max(0.0, avg_overall_corr))

        return {
            "correlation_matrix": corr_df.to_dict(),
            "average_correlation": round(avg_overall_corr, 4),
            "correlation_risk_score": round(portfolio_corr_risk, 4),
            "symbol_risks": symbol_risks,
            "cluster_exposures": {k: round(v, 2) for k, v in cluster_exposures.items()}
        }
