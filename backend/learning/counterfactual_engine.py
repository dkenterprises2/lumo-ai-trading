import time
from dataclasses import dataclass, asdict
from typing import Dict, Any, List
from .experience_memory import TradeExperience

@dataclass
class CounterfactualOutcome:
    scenario_name: str
    simulated_pnl: float
    pnl_difference: float
    conclusion: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class CounterfactualEngine:
    """Post-Trade Counterfactual Simulation Engine.
    
    Evaluates 'What If' scenarios strictly post-trade without look-ahead bias at decision time.
    """

    def analyze_counterfactuals(self, exp: TradeExperience, future_candles: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        outcomes = []
        actual_pnl = exp.realized_pnl

        # Scenario 1: What if we did NOT trade?
        no_trade_pnl = 0.0
        outcomes.append(CounterfactualOutcome(
            scenario_name="NO_TRADE",
            simulated_pnl=no_trade_pnl,
            pnl_difference=round(no_trade_pnl - actual_pnl, 2),
            conclusion="Avoided loss" if actual_pnl < 0 else "Forewent profit"
        ).to_dict())

        # Scenario 2: What if we had used 50% position sizing?
        half_size_pnl = round(actual_pnl * 0.5, 2)
        outcomes.append(CounterfactualOutcome(
            scenario_name="HALF_SIZING_50PCT",
            simulated_pnl=half_size_pnl,
            pnl_difference=round(half_size_pnl - actual_pnl, 2),
            conclusion="Reduced drawdown" if actual_pnl < 0 else "Reduced upside capture"
        ).to_dict())

        # Scenario 3: What if we traded OPPOSITE direction?
        # Invert price change minus double friction
        inverted_pnl = round(-actual_pnl - (exp.fees_usd * 2.0), 2)
        outcomes.append(CounterfactualOutcome(
            scenario_name="OPPOSITE_DIRECTION",
            simulated_pnl=inverted_pnl,
            pnl_difference=round(inverted_pnl - actual_pnl, 2),
            conclusion="Opposite thesis was profitable" if inverted_pnl > 0 else "Both directions unprofitable due to chop/friction"
        ).to_dict())

        # Scenario 4: What if tight 1.5R Exit was applied?
        target_1_5r_pnl = round(exp.allocation_usd * (exp.expected_edge_bps / 10000.0) * 1.5, 2)
        outcomes.append(CounterfactualOutcome(
            scenario_name="TIGHT_1_5R_EXIT",
            simulated_pnl=target_1_5r_pnl,
            pnl_difference=round(target_1_5r_pnl - actual_pnl, 2),
            conclusion="Fixed RR exit captured theoretical target"
        ).to_dict())

        return {
            "experience_id": exp.experience_id,
            "actual_pnl": actual_pnl,
            "scenarios": outcomes,
            "optimal_scenario": max(outcomes, key=lambda x: x["simulated_pnl"])["scenario_name"]
        }

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

# Global Singleton
counterfactual_engine = CounterfactualEngine()
