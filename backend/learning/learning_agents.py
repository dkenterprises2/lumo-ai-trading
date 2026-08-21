import time
from typing import Dict, List, Any
from .experience_memory import TradeExperience
from .post_mortem_engine import post_mortem_engine, TradePostMortem
from .lesson_extractor import lesson_extractor, LearnedLesson

class TradeAnalystAgent:
    """Evaluates granular execution metrics, holding periods, and MFE/MAE."""
    def analyze(self, exp: TradeExperience) -> Dict[str, Any]:
        pnl = exp.realized_pnl
        hold_time = exp.holding_time_seconds
        efficiency = (exp.realized_pnl_pct / max(0.01, exp.max_favorable_excursion_pct)) if exp.max_favorable_excursion_pct > 0 else 0.0
        return {
            "agent": "TradeAnalystAgent",
            "experience_id": exp.experience_id,
            "profitability": "PROFITABLE" if pnl > 0 else "LOSS",
            "capture_efficiency_pct": round(efficiency * 100.0, 2),
            "holding_duration_seconds": hold_time,
            "latency_rating": "OPTIMAL" if exp.execution_latency_ms < 25.0 else "ELEVATED"
        }

class RCAAgent:
    """Diagnoses root cause, contributing factors, and error taxonomy."""
    def analyze(self, exp: TradeExperience) -> Dict[str, Any]:
        pm: TradePostMortem = post_mortem_engine.analyze_trade(exp)
        return {
            "agent": "RCAAgent",
            "root_cause": pm.root_cause,
            "contributing_factors": pm.contributing_factors,
            "lesson_hypothesis": pm.lesson_hypothesis,
            "attribution": pm.attribution_type
        }

class PatternDiscoveryAgent:
    """Identifies recurring clusters of losing setups to generate candidate lessons."""
    def cluster_patterns(self, experiences: List[TradeExperience]) -> List[Dict[str, Any]]:
        patterns = []
        losing_trades = [e for e in experiences if e.realized_pnl < 0]
        regime_counts = {}
        for lt in losing_trades:
            regime_counts[lt.market_regime] = regime_counts.get(lt.market_regime, 0) + 1
        
        for reg, count in regime_counts.items():
            if count >= 3:
                patterns.append({
                    "cluster": f"Elevated loss frequency in [{reg}]",
                    "occurrences": count,
                    "recommended_action": "Tighten entry confirmation requirements in this regime."
                })
        return patterns

class RiskAnalystAgent:
    """Evaluates portfolio drawdown, leverage concentration, and correlation risk."""
    def analyze(self, exp: TradeExperience) -> Dict[str, Any]:
        return {
            "agent": "RiskAnalystAgent",
            "portfolio_exposure_pct": round(exp.portfolio_exposure * 100.0, 1),
            "correlation_risk": "HIGH" if exp.correlation_exposure > 0.40 else "MODERATE",
            "drawdown_impact_usd": exp.drawdown_usd
        }

class ExecutionAnalystAgent:
    """Analyzes slippage, venue rejection rates, and taker fees."""
    def analyze(self, exp: TradeExperience) -> Dict[str, Any]:
        friction_pct = ((exp.fees_usd + exp.slippage_usd) / max(1.0, exp.allocation_usd)) * 100.0
        return {
            "agent": "ExecutionAnalystAgent",
            "fees_usd": exp.fees_usd,
            "slippage_usd": exp.slippage_usd,
            "friction_drag_pct": round(friction_pct, 4),
            "execution_quality": "EXCELLENT" if friction_pct < 0.10 else "DEGRADED"
        }

class ArbitrageAnalystAgent:
    """Evaluates dual-leg executability, freshness decay, and legging risk."""
    def analyze_spread(self, gross_spread: float, fees_bps: float, slippage_bps: float, latency_ms: float) -> Dict[str, Any]:
        friction_bps = fees_bps + slippage_bps + (latency_ms * 0.05)
        net_edge_bps = (gross_spread * 10000.0) - friction_bps
        is_viable = net_edge_bps >= 15.0
        return {
            "agent": "ArbitrageAnalystAgent",
            "gross_spread_bps": round(gross_spread * 10000.0, 1),
            "total_friction_bps": round(friction_bps, 1),
            "net_executable_edge_bps": round(net_edge_bps, 1),
            "executable_verdict": "VIABLE" if is_viable else "FRICTION_TRAP"
        }

class LearningValidationAgent:
    """Validates candidate hypotheses on walk-forward datasets before promotion."""
    def validate_lesson(self, lesson: LearnedLesson) -> Dict[str, Any]:
        score = lesson_extractor.calculate_quality_score(lesson)
        is_approved = score >= 70.0 and lesson.evidence_count >= 5 and lesson.confidence_score >= 0.75
        return {
            "agent": "LearningValidationAgent",
            "lesson_id": lesson.lesson_id,
            "quality_score": score,
            "evidence_count": lesson.evidence_count,
            "recommendation": "APPROVE" if is_approved else "KEEP_IN_OBSERVATION"
        }

class LearningAgentOrchestrator:
    """Master Coordinator of all 7 Diagnostic Learning Agents."""
    def __init__(self):
        self.trade_analyst = TradeAnalystAgent()
        self.rca_agent = RCAAgent()
        self.pattern_agent = PatternDiscoveryAgent()
        self.risk_analyst = RiskAnalystAgent()
        self.execution_analyst = ExecutionAnalystAgent()
        self.arbitrage_analyst = ArbitrageAnalystAgent()
        self.validation_agent = LearningValidationAgent()

    def run_full_post_trade_audit(self, exp: TradeExperience) -> Dict[str, Any]:
        return {
            "experience_id": exp.experience_id,
            "trade_analysis": self.trade_analyst.analyze(exp),
            "rca": self.rca_agent.analyze(exp),
            "risk_analysis": self.risk_analyst.analyze(exp),
            "execution_analysis": self.execution_analyst.analyze(exp)
        }

# Global Singleton
learning_agent_orchestrator = LearningAgentOrchestrator()
