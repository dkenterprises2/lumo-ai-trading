import time
from typing import Dict, Any, Optional
from loguru import logger
from backend.safety.paper_mode_guard import paper_guard, PaperTradingViolation

class CredentialActivationManager:
    """Multi-Stage API Credential & Live Trading Activation Lifecycle Manager.
    
    Hard Invariants:
    1. Merely storing an API key NEVER activates live trading.
    2. Explicit multi-stage verification is required before live execution is enabled.
    3. Paper/Shadow Sandbox mode remains the immutable system default.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CredentialActivationManager, cls).__new__(cls)
            cls._instance._user_states: Dict[str, Dict[str, Any]] = {}
        return cls._instance

    def _get_user_state(self, user_id: str) -> Dict[str, Any]:
        u_id = str(user_id)
        if u_id not in self._user_states:
            self._user_states[u_id] = {
                "credentials_configured": False,
                "exchange_name": "NONE",
                "api_key_masked": "",
                "live_enabled": False,
                "live_permission": False,
                "live_health": True,
                "live_execution_available": False,
                "last_credential_check": 0.0,
                "activation_timestamp": None
            }
        return self._user_states[u_id]

    def register_credentials(
        self,
        user_id: str,
        exchange_name: str,
        api_key: str,
        secret_key: str
    ) -> Dict[str, Any]:
        """Registers and validates API keys, but KEEPS live_enabled = False."""
        state = self._get_user_state(user_id)
        
        # Validate non-empty credentials
        if not api_key or not secret_key or len(api_key) < 8 or len(secret_key) < 8:
            return {
                "status": "error",
                "message": "Invalid API credentials provided. Minimum key length is 8 characters.",
                "credentials_configured": False,
                "live_enabled": False
            }

        state["credentials_configured"] = True
        state["exchange_name"] = exchange_name.upper()
        state["api_key_masked"] = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "****"
        state["last_credential_check"] = time.time()
        state["live_permission"] = True
        
        # CRITICAL: live_enabled remains strictly FALSE upon credential storage
        state["live_enabled"] = False
        state["live_execution_available"] = False

        logger.info(f"[CREDENTIALS_REGISTERED] UserID={user_id} configured API keys for {exchange_name}. LIVE TRADING REMAINS OFF.")
        return {
            "status": "success",
            "message": "API CONNECTED — LIVE TRADING STILL OFF",
            "credentials_configured": True,
            "live_enabled": False,
            "live_execution_available": False,
            "exchange_name": state["exchange_name"],
            "api_key_masked": state["api_key_masked"]
        }

    def activate_live_trading(self, user_id: str, confirmation_token: str) -> Dict[str, Any]:
        """Explicit opt-in activation of Live Trading by user with verification token."""
        state = self._get_user_state(user_id)
        
        if not state["credentials_configured"]:
            return {
                "status": "rejected",
                "message": "Cannot enable live trading: No valid exchange API credentials configured.",
                "live_enabled": False
            }

        if confirmation_token != "CONFIRM_LIVE_TRADING_RISK":
            return {
                "status": "rejected",
                "message": "Invalid confirmation token. User must acknowledge live capital risk.",
                "live_enabled": False
            }

        # Check safety guard (during sandbox dev mode, live execution remains blocked)
        if paper_guard.paper_mode:
            logger.warning(f"[LIVE_ACTIVATION_BLOCKED] Sandbox Paper Guard is active. Live execution blocked.")
            return {
                "status": "blocked",
                "message": "System is running under immutable Paper/Shadow Safety Guard. Live exchange execution is globally disabled.",
                "live_enabled": False,
                "live_execution_available": False
            }

        state["live_enabled"] = True
        state["live_execution_available"] = True
        state["activation_timestamp"] = time.time()
        logger.info(f"[LIVE_ACTIVATED] UserID={user_id} explicitly enabled LIVE trading for {state['exchange_name']}.")
        return {
            "status": "success",
            "message": "LIVE TRADING ACTIVATED",
            "live_enabled": True,
            "live_execution_available": True,
            "exchange_name": state["exchange_name"]
        }

    def deactivate_live_trading(self, user_id: str, reason: str = "User opt-out") -> Dict[str, Any]:
        """Instantly disables live trading and reverts user session to Paper/Shadow mode."""
        state = self._get_user_state(user_id)
        state["live_enabled"] = False
        state["live_execution_available"] = False
        logger.info(f"[LIVE_DEACTIVATED] UserID={user_id} reverted to Paper mode: {reason}")
        return {
            "status": "success",
            "message": "LIVE TRADING DEACTIVATED — REVERTED TO PAPER MODE",
            "live_enabled": False,
            "live_execution_available": False
        }

    def is_live_executable(self, user_id: str) -> bool:
        """Evaluates whether all 5 pre-conditions for live exchange execution are strictly met."""
        state = self._get_user_state(user_id)
        return bool(
            state["credentials_configured"] and
            state["live_enabled"] and
            state["live_permission"] and
            state["live_health"] and
            state["live_execution_available"] and
            not paper_guard.paper_mode
        )

    def get_status(self, user_id: str) -> Dict[str, Any]:
        state = self._get_user_state(user_id)
        return {
            "credentials_configured": state["credentials_configured"],
            "exchange_name": state["exchange_name"],
            "api_key_masked": state["api_key_masked"],
            "live_enabled": state["live_enabled"],
            "live_permission": state["live_permission"],
            "live_health": state["live_health"],
            "live_execution_available": state["live_execution_available"],
            "sandbox_paper_guard_active": paper_guard.paper_mode
        }

# Global Singleton
credential_manager = CredentialActivationManager()
