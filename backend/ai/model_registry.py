import time
from typing import Dict, Any, List, Optional

class MLModelMetadata:
    """Metadata container for registered ML models."""
    def __init__(
        self,
        model_id: str,
        name: str,
        algorithm: str,  # XGBOOST, LIGHTGBM, CATBOOST, RANDOM_FOREST, GRADIENT_BOOSTING, LOGISTIC_REGRESSION, LSTM, TRANSFORMER
        version: str,
        is_champion: bool = False,
        accuracy: float = 0.78,
        f1_score: float = 0.76,
        sharpe_improvement: float = 0.45,
        parameters: Optional[Dict[str, Any]] = None
    ):
        self.model_id = model_id
        self.name = name
        self.algorithm = algorithm
        self.version = version
        self.is_champion = is_champion
        self.accuracy = accuracy
        self.f1_score = f1_score
        self.sharpe_improvement = sharpe_improvement
        self.parameters = parameters or {}
        self.created_at = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())

class MLModelRegistry:
    """Central AI Model Registry managing pluggable ML models & Champion/Challenger promotions."""

    def __init__(self):
        self._models: Dict[str, MLModelMetadata] = {}
        self._champion_id: Optional[str] = None
        self._register_default_models()

    def _register_default_models(self):
        defaults = [
            MLModelMetadata("xgb_prod_v2", "XGBoost Production Signal Classifier", "XGBOOST", "v2.1.0", is_champion=True, accuracy=0.82, f1_score=0.80, sharpe_improvement=0.65),
            MLModelMetadata("lgb_challenger_v1", "LightGBM High-Speed Classifier", "LIGHTGBM", "v2.1.0", is_champion=False, accuracy=0.79, f1_score=0.77, sharpe_improvement=0.52),
            MLModelMetadata("cat_challenger_v1", "CatBoost Categorical Regime Classifier", "CATBOOST", "v2.1.0", is_champion=False, accuracy=0.81, f1_score=0.79, sharpe_improvement=0.60),
            MLModelMetadata("rf_baseline_v1", "Random Forest Ensemble Baseline", "RANDOM_FOREST", "v2.0.0", is_champion=False, accuracy=0.75, f1_score=0.73, sharpe_improvement=0.35),
            MLModelMetadata("lstm_seq_v1", "LSTM Sequential Price Movement Predictor", "LSTM", "v2.1.0", is_champion=False, accuracy=0.77, f1_score=0.75, sharpe_improvement=0.48),
            MLModelMetadata("transformer_v1", "Transformer Multi-Head Attention Predictor", "TRANSFORMER", "v2.1.0", is_champion=False, accuracy=0.84, f1_score=0.82, sharpe_improvement=0.72)
        ]
        for m in defaults:
            self._models[m.model_id] = m
            if m.is_champion:
                self._champion_id = m.model_id

    def list_models(self) -> List[Dict[str, Any]]:
        return [
            {
                "model_id": m.model_id,
                "name": m.name,
                "algorithm": m.algorithm,
                "version": m.version,
                "is_champion": m.is_champion,
                "accuracy": m.accuracy,
                "f1_score": m.f1_score,
                "sharpe_improvement": m.sharpe_improvement,
                "parameters": m.parameters,
                "created_at": m.created_at
            }
            for m in self._models.values()
        ]

    def get_champion_model(self) -> Optional[MLModelMetadata]:
        return self._models.get(self._champion_id) if self._champion_id else None

    def promote_champion(self, model_id: str) -> Dict[str, Any]:
        if model_id not in self._models:
            return {"status": "error", "message": f"Model {model_id} not found."}

        for m in self._models.values():
            m.is_champion = False

        self._models[model_id].is_champion = True
        self._champion_id = model_id
        return {"status": "success", "message": f"Model {model_id} promoted to CHAMPION.", "champion_id": model_id}

    def rollback_champion(self, previous_model_id: str = "xgb_prod_v2") -> Dict[str, Any]:
        return self.promote_champion(previous_model_id)

ml_model_registry = MLModelRegistry()
