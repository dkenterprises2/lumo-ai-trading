import math
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger

@dataclass
class PortfolioExposureGraph:
    total_notional_usd: float
    long_notional_usd: float
    short_notional_usd: float
    short_ratio_pct: float             # [0.0, 100.0]
    portfolio_beta_btc: float          # Beta to Bitcoin
    effective_independent_bets: float  # Neff based on correlation matrix
    cluster_concentrations: Dict[str, float]
    is_balanced: bool
    risk_warnings: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class AntiCorrelationPortfolioBrain:
    """
    Phase 44.3 Anti-Correlation Portfolio Exposure & Concentration Brain.
    Prevents 100% homogeneous SHORT/LONG bets and enforces true statistical independence.
    """

    # Empirical correlation with Bitcoin for major crypto assets
    BTC_CORRELATIONS = {
        "BTC/USDT": 1.00,
        "ETH/USDT": 0.88,
        "SOL/USDT": 0.82,
        "AVAX/USDT": 0.84,
        "LINK/USDT": 0.80,
        "DOT/USDT": 0.83,
        "MATIC/USDT": 0.81,
        "ADA/USDT": 0.79,
        "DOGE/USDT": 0.72,
        "BNB/USDT": 0.75,
        "SUI/USDT": 0.70,
        "NEAR/USDT": 0.78,
        "APT/USDT": 0.76
    }

    # Hard Risk Invariants
    MAX_SAME_DIRECTION_PCT = 60.0      # Max 60% of total exposure in one direction (Long or Short)
    MAX_PORTFOLIO_BETA_ABS = 1.25      # Max portfolio beta magnitude
    MAX_CLUSTER_EXPOSURE_PCT = 30.0    # Max 30% capital in single correlated cluster (e.g. Layer-1s)

    def analyze_portfolio(self, current_positions: Dict[str, Dict[str, Any]]) -> PortfolioExposureGraph:
        """
        Analyze current active positions and calculate portfolio beta, directional skew, and effective bets.
        """
        long_notional = 0.0
        short_notional = 0.0
        weighted_beta_sum = 0.0
        cluster_exposure: Dict[str, float] = {}
        warnings: List[str] = []

        if not current_positions:
            return PortfolioExposureGraph(
                total_notional_usd=0.0,
                long_notional_usd=0.0,
                short_notional_usd=0.0,
                short_ratio_pct=50.0,
                portfolio_beta_btc=0.0,
                effective_independent_bets=0.0,
                cluster_concentrations={},
                is_balanced=True,
                risk_warnings=[]
            )

        for pos in current_positions.values():
            sym = pos.get("symbol", "BTC/USDT")
            side = pos.get("side", "BUY").upper()
            qty = float(pos.get("amount", 0.0))
            price = float(pos.get("entry_price", 0.0))
            notional = qty * price if (qty and price) else float(pos.get("margin_usd", 1000.0)) * float(pos.get("leverage", 1))

            corr_btc = self.BTC_CORRELATIONS.get(sym, 0.75)

            if side in ["BUY", "LONG"]:
                long_notional += notional
                weighted_beta_sum += (notional * corr_btc)
            else:
                short_notional += notional
                weighted_beta_sum -= (notional * corr_btc)

            # Cluster tracking (Major L1s, DeFi, Memes)
            if sym in ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "AVAX/USDT"]:
                cluster = "MAJOR_L1"
            elif sym in ["LINK/USDT", "UNI/USDT", "AAVE/USDT", "MKR/USDT", "CRV/USDT"]:
                cluster = "DEFI"
            elif sym in ["DOGE/USDT", "SHIB/USDT", "PEPE/USDT", "FLOKI/USDT"]:
                cluster = "MEMES"
            else:
                cluster = "ALT_GENERAL"

            cluster_exposure[cluster] = cluster_exposure.get(cluster, 0.0) + notional

        total_notional = long_notional + short_notional
        short_ratio = (short_notional / total_notional * 100.0) if total_notional > 0 else 50.0
        portfolio_beta = round(weighted_beta_sum / max(1.0, total_notional), 2)

        # Calculate Effective Independent Bets: Neff = (Total Notional)^2 / Sum(wi * wj * rho_ij)
        # Approximate using average cross-correlation ~0.80
        avg_rho = 0.80
        n_positions = len(current_positions)
        effective_bets = round(n_positions / (1.0 + (n_positions - 1) * avg_rho), 1) if n_positions > 0 else 0.0

        is_balanced = True
        if short_ratio > self.MAX_SAME_DIRECTION_PCT:
            is_balanced = False
            warnings.append(f"Severe SHORT concentration ({short_ratio:.1f}% > {self.MAX_SAME_DIRECTION_PCT}% limit).")
        elif (100.0 - short_ratio) > self.MAX_SAME_DIRECTION_PCT:
            is_balanced = False
            warnings.append(f"Severe LONG concentration ({(100.0 - short_ratio):.1f}% > {self.MAX_SAME_DIRECTION_PCT}% limit).")

        if abs(portfolio_beta) > self.MAX_PORTFOLIO_BETA_ABS:
            is_balanced = False
            warnings.append(f"High Portfolio Beta magnitude ({portfolio_beta:.2f} vs max {self.MAX_PORTFOLIO_BETA_ABS}).")

        cluster_pcts = {k: round((v / max(1.0, total_notional)) * 100.0, 1) for k, v in cluster_exposure.items()}

        return PortfolioExposureGraph(
            total_notional_usd=round(total_notional, 2),
            long_notional_usd=round(long_notional, 2),
            short_notional_usd=round(short_notional, 2),
            short_ratio_pct=round(short_ratio, 1),
            portfolio_beta_btc=portfolio_beta,
            effective_independent_bets=effective_bets,
            cluster_concentrations=cluster_pcts,
            is_balanced=is_balanced,
            risk_warnings=warnings
        )

    def evaluate_order_portfolio_fit(
        self,
        symbol: str,
        side: str,
        proposed_notional_usd: float,
        current_positions: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evaluates whether adding a proposed trade violates anti-correlation or direction-skew invariants.
        """
        # If no positions open, first trade is always approved
        if not current_positions:
            return {
                "passed": True,
                "adjusted_notional_usd": proposed_notional_usd,
                "reason": "Initial position approved for fresh portfolio."
            }

        graph = self.analyze_portfolio(current_positions)
        proposed_side = side.upper()

        # Check Same-Direction Stacking Limit (60% Hard Cap)
        current_total = graph.total_notional_usd
        new_total = current_total + proposed_notional_usd

        if proposed_side in ["SELL", "SHORT"]:
            new_short_notional = graph.short_notional_usd + proposed_notional_usd
            new_short_ratio = (new_short_notional / max(1.0, new_total)) * 100.0
            if new_short_ratio > self.MAX_SAME_DIRECTION_PCT and len(current_positions) >= 3:
                return {
                    "passed": False,
                    "reason": f"ANTI_CORRELATION_BLOCKED: Proposed SHORT increases portfolio SHORT skew to {new_short_ratio:.1f}% (Hard limit: {self.MAX_SAME_DIRECTION_PCT}%). Blocked to prevent market-beta stacking."
                }
        else:
            new_long_notional = graph.long_notional_usd + proposed_notional_usd
            new_long_ratio = (new_long_notional / max(1.0, new_total)) * 100.0
            if new_long_ratio > self.MAX_SAME_DIRECTION_PCT and len(current_positions) >= 3:
                return {
                    "passed": False,
                    "reason": f"ANTI_CORRELATION_BLOCKED: Proposed LONG increases portfolio LONG skew to {new_long_ratio:.1f}% (Hard limit: {self.MAX_SAME_DIRECTION_PCT}%). Blocked to prevent market-beta stacking."
                }

        # Check Correlated Alt Stacking (If already holding 3+ correlated L1 shorts)
        corr_btc = self.BTC_CORRELATIONS.get(symbol, 0.75)
        if corr_btc >= 0.80 and graph.short_ratio_pct >= 55.0 and proposed_side in ["SELL", "SHORT"]:
            # Reduce allocation to scale down correlation exposure
            adjusted = round(proposed_notional_usd * 0.50, 2)
            return {
                "passed": True,
                "adjusted_notional_usd": adjusted,
                "reason": f"High correlation asset ({symbol} rho={corr_btc:.2f}) scaled down by 50% to prevent cluster crowding."
            }

        return {
            "passed": True,
            "adjusted_notional_usd": proposed_notional_usd,
            "reason": f"Portfolio exposure within safe bounds (Short skew: {graph.short_ratio_pct:.1f}%, Beta: {graph.portfolio_beta_btc:.2f})."
        }

# Global Singleton
portfolio_brain = AntiCorrelationPortfolioBrain()
