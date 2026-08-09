import time
from typing import Dict, Any, List

class FeatureStoreVersionManager:
    """Feature Store with Immutable Versioning & Statistics."""

    def __init__(self):
        self._versions: List[Dict[str, Any]] = [
            {
                "feature_set_id": "FS-V1.0",
                "name": "Institutional Crypto Features V1",
                "features": ["rsi_14", "macd_diff", "volatility_regime", "orderbook_imbalance"],
                "version": "1.0.0",
                "is_immutable": True,
                "registered_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
            }
        ]

    def register_feature_version(self, name: str, features: List[str], version: str) -> Dict[str, Any]:
        """Register a new immutable feature store version."""
        feat_set = {
            "feature_set_id": f"FS-V{version}",
            "name": name,
            "features": features,
            "version": version,
            "is_immutable": True,
            "registered_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        }
        self._versions.insert(0, feat_set)
        return feat_set

    def list_feature_versions(self) -> List[Dict[str, Any]]:
        return self._versions

feature_store_manager = FeatureStoreVersionManager()
