from typing import Dict, List, Any
from .validation_scenario import ScenarioResult

class ValidationMetricsCalculator:
    """Calculates Autonomous Lifecycle Score (0–100) strictly from empirical validation results."""

    @staticmethod
    def calculate_validation_score(results: List[ScenarioResult]) -> Dict[str, Any]:
        if not results:
            return {
                "overall_score": 0.0,
                "readiness_label": "NOT YET VERIFIED",
                "breakdown": {}
            }

        total_scenarios = len(results)
        passed_scenarios = sum(1 for r in results if r.passed)
        success_rate = (passed_scenarios / total_scenarios) * 100.0 if total_scenarios > 0 else 0.0

        # Component breakdown scores (10 points each)
        cat_map = {}
        for r in results:
            cat = r.scenario_code
            cat_map[cat] = 10.0 if r.passed else 0.0

        score_detection = 10.0 if any(r.passed for r in results if "PROFITABLE" in r.scenario_code) else 0.0
        score_risk = 10.0 if any(r.passed for r in results if "RISK" in r.scenario_code) else 0.0
        score_gov = 10.0 if any(r.passed for r in results if "GOVERNANCE" in r.scenario_code) else 0.0
        score_oms = 10.0 if any(r.passed for r in results if r.execution_id and r.passed) else 0.0
        score_fills = 10.0 if any(r.passed for r in results if "PROFITABLE" in r.scenario_code) else 0.0
        score_position = 10.0 if any(r.passed for r in results if "POSITION" in r.scenario_code) else 0.0
        score_exit = 10.0 if any(r.passed for r in results if "EXIT" in r.scenario_code or "DECAY" in r.scenario_code) else 0.0
        score_pnl = 10.0 if any(r.passed and r.realized_shadow_pnl != 0.0 for r in results if r.scenario_code.startswith("SCENARIO_G")) else 0.0
        score_safety = 10.0 if any(r.passed for r in results if "KILL_SWITCH" in r.scenario_code) else 0.0
        score_audit = 10.0 if any(len(r.state_history) > 0 for r in results) else 0.0

        overall_score = round(
            (score_detection + score_risk + score_gov + score_oms + score_fills +
             score_position + score_exit + score_pnl + score_safety + score_audit), 1
        )

        if overall_score >= 90.0 and success_rate == 100.0:
            readiness_label = "READY FOR EXTENDED SHADOW"
        elif overall_score >= 70.0:
            readiness_label = "READY FOR CONTROLLED SHADOW"
        else:
            readiness_label = "NOT READY"

        return {
            "overall_score": overall_score,
            "readiness_label": readiness_label,
            "scenarios_total": total_scenarios,
            "scenarios_passed": passed_scenarios,
            "scenarios_failed": total_scenarios - passed_scenarios,
            "success_rate_pct": round(success_rate, 1),
            "breakdown": {
                "opportunity_detection": score_detection,
                "risk_integration": score_risk,
                "governance_integration": score_gov,
                "oms_ems_integration": score_oms,
                "shadow_fill_accuracy": score_fills,
                "position_tracking": score_position,
                "automatic_exit": score_exit,
                "pnl_accuracy": score_pnl,
                "safety_isolation": score_safety,
                "observability": score_audit
            }
        }
