from typing import Dict, Any

class WhiteLabelBrandingService:
    """White-Label Theme, Logo, Color Palette & Favicon Customizer."""

    def __init__(self):
        self._branding = {
            "app_name": "Lumo Pro",
            "logo_url": "https://app.lumo.trade/assets/logo.png",
            "primary_color": "#6366F1",
            "secondary_color": "#10B981",
            "custom_css": "",
            "support_email": "support@lumo.trade"
        }

    def get_branding(self) -> Dict[str, Any]:

        return self._branding

    def update_branding(self, data: Dict[str, Any]) -> Dict[str, Any]:
        self._branding.update(data)
        return self._branding

branding_service = WhiteLabelBrandingService()
