from typing import Dict, Any

class GoogleOAuthProvider:
    """Google OAuth 2.0 Identity Provider Abstraction."""

    @staticmethod
    def get_auth_url(redirect_uri: str = "https://app.lumo.trade/auth/google/callback") -> Dict[str, Any]:
        return {
            "provider": "GOOGLE",
            "auth_url": f"https://accounts.google.com/o/oauth2/v2/auth?client_id=SIMULATED_GOOGLE_ID&redirect_uri={redirect_uri}",
            "status": "READY_SIMULATED"
        }

oauth_google = GoogleOAuthProvider()
