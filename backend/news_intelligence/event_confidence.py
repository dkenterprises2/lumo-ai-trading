from typing import List

class EventConfidenceScorer:
    """Computes Event Confidence Score (0.00 to 1.00)."""

    SOURCE_REPUTATION = {
        "SEC.gov": 0.99,
        "Binance Announcements": 0.98,
        "OKX Announcements": 0.97,
        "Bybit Announcements": 0.97,
        "Reuters Crypto": 0.92,
        "CoinDesk": 0.90,
        "The Block": 0.88,
        "CoinTelegraph": 0.85,
        "Decrypt": 0.82,
        "Twitter/X": 0.65
    }

    def compute_confidence(self, source: str, corroborating_sources: List[str] = None) -> float:
        base = self.SOURCE_REPUTATION.get(source, 0.70)
        corr_count = len(corroborating_sources) if corroborating_sources else 0
        bonus = min(0.15, corr_count * 0.05)
        
        final_conf = min(0.99, base + bonus)
        return round(final_conf, 2)
