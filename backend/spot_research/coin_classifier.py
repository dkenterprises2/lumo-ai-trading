"""
Coin Classifier for Lumo Spot Research Subsystem.
Categorizes discovered tokens into MEME, NEW, ESTABLISHED, or UNKNOWN
using factual metadata, DexScreener profile descriptions, listing age, and verified token tags.
"""

import time
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from .coin_discovery_engine import DiscoveredCoin

class CoinClassification(BaseModel):
    category: str  # MEME, NEW, ESTABLISHED, UNKNOWN
    confidence: float
    reasons: list[str] = Field(default_factory=list)
    source: str
    timestamp: float = Field(default_factory=time.time)

class CoinClassifier:
    """Transparent rule-based and metadata-driven token classifier."""

    MEME_KEYWORD_PATTERNS = [
        "doge", "shib", "pepe", "floki", "bonk", "wif", "cat", "pup", "inu",
        "meme", "pnut", "goat", "neiro", "brett", "popcat", "mew", "bome",
        "turbo", "toshi", "coq", "silly", "wojak", "ponke", "fart", "santa"
    ]

    ESTABLISHED_ASSETS = {
        "BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "AVAX", "DOT", "LINK",
        "MATIC", "ATOM", "NEAR", "APT", "SUI", "OP", "ARB", "LTC", "ETC",
        "UNI", "AAVE", "MKR", "CRV", "LDO", "GRT", "FTM", "FIL", "ICP"
    }

    def classify(self, coin: DiscoveredCoin) -> CoinClassification:
        reasons = []
        now = time.time()
        base_upper = coin.base_asset.upper()
        base_lower = coin.base_asset.lower()
        desc_lower = (coin.description or "").lower()

        # 1. Check Established Mega/Large-Caps
        if base_upper in self.ESTABLISHED_ASSETS:
            return CoinClassification(
                category="ESTABLISHED",
                confidence=0.98,
                reasons=[f"Top established institutional crypto asset ({base_upper})"],
                source="COIN_MASTER_REGISTRY",
                timestamp=now
            )

        # 2. Check Meme Token Metadata & Keyword Indicators
        meme_score = 0.0
        # A. Symbol / Name Pattern Check
        for kw in self.MEME_KEYWORD_PATTERNS:
            if kw in base_lower:
                meme_score += 0.5
                reasons.append(f"Token symbol contains known meme keyword: '{kw}'")
                break

        # B. Description Metadata Check
        if desc_lower:
            for kw in ["meme", "community token", "parody", "dog", "cat", "mascot", "fun token", "tribute"]:
                if kw in desc_lower:
                    meme_score += 0.4
                    reasons.append(f"Verified profile description references: '{kw}'")
                    break

        # C. DEX Profile / Community Boost Check
        if coin.source == "DEXSCREENER_API" and coin.profile_url:
            meme_score += 0.2
            reasons.append("Token profile listed on DEX community booster stream")

        if meme_score >= 0.5:
            return CoinClassification(
                category="MEME",
                confidence=min(1.0, round(meme_score, 2)),
                reasons=reasons,
                source="METADATA_AND_PROFILE_ANALYSIS",
                timestamp=now
            )

        # 3. Check Newly Listed / Fresh Pair (< 30 days)
        if coin.listing_ts:
            age_days = (now - coin.listing_ts) / 86400.0
            if age_days < 30.0:
                return CoinClassification(
                    category="NEW",
                    confidence=0.90,
                    reasons=[f"Pair created or listed within last {age_days:.1f} days ({coin.exchange})"],
                    source="DEX_LISTING_TIMESTAMP",
                    timestamp=now
                )

        # 4. Fallback: Unknown or General Altcoin
        return CoinClassification(
            category="UNKNOWN" if not reasons else "NEW",
            confidence=0.50,
            reasons=reasons if reasons else ["Insufficient meme or listing metadata to establish classification"],
            source="CLASSIFIER_HEURISTICS",
            timestamp=now
        )

coin_classifier = CoinClassifier()
