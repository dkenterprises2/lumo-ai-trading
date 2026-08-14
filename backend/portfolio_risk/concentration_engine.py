from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional

@dataclass
class ConcentrationAnalysis:
    single_symbol_max_pct: float
    top_2_exposure_pct: float
    top_5_exposure_pct: float
    cluster_max_pct: float
    highest_concentrated_symbol: str
    concentration_risk_score: float # 0.0 to 1.0
    status: str # NORMAL, WARNING (>25%), HIGH (>40%), CRITICAL (>60%)
    warning_messages: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class ConcentrationEngine:
    """Evaluates portfolio concentration across single symbols, top-N assets, and asset clusters."""

    def __init__(
        self,
        warning_threshold_pct: float = 25.0,
        high_threshold_pct: float = 40.0,
        critical_threshold_pct: float = 60.0
    ):
        self.warning_threshold = warning_threshold_pct
        self.high_threshold = high_threshold_pct
        self.critical_threshold = critical_threshold_pct

    def evaluate_concentration(
        self,
        positions: Dict[str, Dict[str, Any]],
        portfolio_value: float
    ) -> ConcentrationAnalysis:
        """Evaluate portfolio concentration risk."""
        if not positions or portfolio_value <= 0:
            return ConcentrationAnalysis(
                single_symbol_max_pct=0.0,
                top_2_exposure_pct=0.0,
                top_5_exposure_pct=0.0,
                cluster_max_pct=0.0,
                highest_concentrated_symbol="NONE",
                concentration_risk_score=0.0,
                status="NORMAL",
                warning_messages=[]
            )

        symbol_exposures: Dict[str, float] = {}
        cluster_exposures: Dict[str, float] = {}

        for sym, pos in positions.items():
            notional = pos.get("notional_val_usd", pos.get("margin_usd", 0) * pos.get("leverage", 1))
            exp_pct = (notional / portfolio_value) * 100.0
            symbol_exposures[sym] = exp_pct

            # Grouping
            group = "MEME" if any(m in sym for m in ["PEPE", "SHIB", "FLOKI", "DOGE"]) else "MAJOR"
            cluster_exposures[group] = cluster_exposures.get(group, 0.0) + exp_pct

        sorted_symbols = sorted(symbol_exposures.items(), key=lambda x: x[1], reverse=True)
        max_sym, max_pct = sorted_symbols[0] if sorted_symbols else ("NONE", 0.0)

        top_2_pct = sum(pct for _, pct in sorted_symbols[:2])
        top_5_pct = sum(pct for _, pct in sorted_symbols[:5])
        max_cluster_pct = max(cluster_exposures.values()) if cluster_exposures else 0.0

        warnings = []
        status = "NORMAL"
        score = min(1.0, max_pct / 100.0)

        if max_pct >= self.critical_threshold:
            status = "CRITICAL"
            warnings.append(f"Critical single-symbol concentration: {max_sym} accounts for {max_pct:.1f}% of capital (Limit: {self.critical_threshold}%).")
        elif max_pct >= self.high_threshold:
            status = "HIGH"
            warnings.append(f"High single-symbol concentration: {max_sym} accounts for {max_pct:.1f}% of capital (Limit: {self.high_threshold}%).")
        elif max_pct >= self.warning_threshold:
            status = "WARNING"
            warnings.append(f"Concentration warning: {max_sym} accounts for {max_pct:.1f}% of capital (Threshold: {self.warning_threshold}%).")

        if top_2_pct > 70.0:
            warnings.append(f"Top 2 positions account for {top_2_pct:.1f}% of total portfolio capital.")

        return ConcentrationAnalysis(
            single_symbol_max_pct=round(max_pct, 2),
            top_2_exposure_pct=round(top_2_pct, 2),
            top_5_exposure_pct=round(top_5_pct, 2),
            cluster_max_pct=round(max_cluster_pct, 2),
            highest_concentrated_symbol=max_sym,
            concentration_risk_score=round(score, 4),
            status=status,
            warning_messages=warnings
        )
