from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional

@dataclass
class RiskRecommendation:
    severity: str # LOW, MEDIUM, HIGH, CRITICAL
    recommendation: str
    affected_symbols: List[str]
    evidence: Dict[str, Any]
    confidence: float
    action: str # REDUCE_EXPOSURE, CLOSE_POSITION, LOWER_LEVERAGE, HALT_TRADING, NO_ACTION

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class RiskRecommendationEngine:
    """Generates structured AI Risk Recommendations based on analytical evidence."""

    def generate_recommendations(
        self,
        portfolio_state: Dict[str, Any],
        concentration_analysis: Dict[str, Any],
        correlation_analysis: Dict[str, Any]
    ) -> List[RiskRecommendation]:
        """Generate advisory risk recommendations."""
        recs = []

        # High Concentration Recommendation
        max_sym = concentration_analysis.get("highest_concentrated_symbol", "NONE")
        max_pct = concentration_analysis.get("single_symbol_max_pct", 0.0)

        if max_pct >= 40.0 and max_sym != "NONE":
            recs.append(RiskRecommendation(
                severity="HIGH",
                recommendation=f"Reduce concentration in {max_sym}. Position represents {max_pct:.1f}% of total portfolio.",
                affected_symbols=[max_sym],
                evidence={"concentration_pct": max_pct, "threshold": 40.0},
                confidence=0.92,
                action="REDUCE_EXPOSURE"
            ))

        # High Correlation Cluster Recommendation
        corr_score = correlation_analysis.get("correlation_risk_score", 0.0)
        if corr_score >= 0.70:
            recs.append(RiskRecommendation(
                severity="MEDIUM",
                recommendation="High portfolio correlation detected. Reduce major crypto pair clustering.",
                affected_symbols=list(correlation_analysis.get("symbol_risks", {}).keys()),
                evidence={"correlation_risk_score": corr_score, "threshold": 0.70},
                confidence=0.88,
                action="REDUCE_EXPOSURE"
            ))

        # Portfolio Heat Warning
        heat_status = portfolio_state.get("overall_status", "HEALTHY")
        if heat_status in ["WARNING", "HIGH", "CRITICAL"]:
            recs.append(RiskRecommendation(
                severity="HIGH" if heat_status == "HIGH" else "CRITICAL",
                recommendation=f"Portfolio status is {heat_status}. Limit new trade allocation.",
                affected_symbols=[],
                evidence={"status": heat_status},
                confidence=0.95,
                action="LOWER_LEVERAGE"
            ))

        return recs
