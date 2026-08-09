from backend.multiasset.security_master import security_master

class AssetRegistry:
    """Global Asset Classes Catalog."""

    @staticmethod
    def get_supported_classes() -> list:
        return [
            "CRYPTO", "EQUITY", "ETF", "FUTURE", "OPTION",
            "FOREX", "STABLECOIN", "DEFI_POSITION", "TREASURY_INSTRUMENT"
        ]

asset_registry = AssetRegistry()
