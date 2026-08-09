from typing import Dict, Any

class MicrosoftEntraOAuthProvider:
    """Microsoft Entra ID OAuth 2.0 Abstraction."""

    @staticmethod
    def get_auth_url(redirect_uri: str = "https://app.lumo.trade/auth/microsoft/callback") -> Dict[str, Any]:
        return {
            "provider": "MICROSOFT_ENTRA",
            "auth_url": f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id=SIMULATED_MS_ID&redirect_uri={redirect_uri}",
            "status": "READY_SIMULATED"
        }

oauth_microsoft = MicrosoftEntraOAuthProvider()
