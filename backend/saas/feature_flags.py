from typing import Dict, Any, List

class FeatureFlagsManager:
    """Dynamic Feature Flags & Licensing Entitlement Service."""

    def __init__(self):
        self._flags = {
            "ai_trading": True,
            "multiasset": True,
            "white_label": True,
            "saml_sso": True,
            "custom_domains": True
        }

    def is_enabled(self, flag: str) -> bool:
        return self._flags.get(flag, False)

    def set_flag(self, flag: str, enabled: bool) -> Dict[str, Any]:
        self._flags[flag] = enabled
        return {"flag": flag, "enabled": enabled}

feature_flags = FeatureFlagsManager()
