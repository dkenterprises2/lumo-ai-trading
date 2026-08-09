import time
import uuid
from typing import Dict, Any, List, Optional

class ExperimentTracker:
    """MLFlow-style Experiment & Run Tracking Engine."""

    def __init__(self):
        self._experiments: List[Dict[str, Any]] = [
            {
                "experiment_id": "EXP-101",
                "name": "BTC-USDT Momentum & Volatility Model",
                "description": "AutoML training with XGBoost and LSTM ensemble",
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                "runs_count": 3
            }
        ]
        self._runs: List[Dict[str, Any]] = []

    def start_experiment(self, name: str, description: str = "") -> Dict[str, Any]:
        """Start a new MLOps experiment."""
        exp_id = f"EXP-{int(time.time())}"
        experiment = {
            "experiment_id": exp_id,
            "name": name,
            "description": description,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "runs_count": 0
        }
        self._experiments.insert(0, experiment)
        return experiment

    def log_run(self, experiment_id: str, metrics: Dict[str, float], params: Dict[str, Any]) -> Dict[str, Any]:
        """Log a training run with metrics and parameters."""
        run_id = f"RUN-{str(uuid.uuid4())[:8]}"
        run = {
            "run_id": run_id,
            "experiment_id": experiment_id,
            "metrics": metrics,
            "params": params,
            "logged_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        }
        self._runs.insert(0, run)
        return run

    def list_experiments(self) -> List[Dict[str, Any]]:
        return self._experiments

experiment_tracker = ExperimentTracker()
