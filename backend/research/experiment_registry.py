from typing import Dict, Any, List

class ExperimentRegistryManager:
    """Quantitative Experiment Registry Manager."""

    def list_experiments(self) -> List[Dict[str, Any]]:
        return [
            {"exp_id": "EXP-QUANT-001", "name": "StatArb_BTC_ETH_V1", "status": "COMPLETED"},
            {"exp_id": "EXP-QUANT-002", "name": "Bayesian_EMA_Tuning", "status": "COMPLETED"}
        ]

experiment_registry = ExperimentRegistryManager()
