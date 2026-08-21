"""
Multi-Vector Risk Engine for Lumo Spot Research Subsystem.
Computes 8 separate quantitative risk vectors:
1. Liquidity Risk (Pool depth vs Volume / Market Cap)
2. Volatility Risk (24h Price swing / High-Low Range)
3. Spread Risk (Bid/Ask spread in bps)
4. Volume Anomaly Risk (Abnormal Volume/Liquidity ratios)
5. Listing Age Risk (Age penalties: <24h = High, <7d = Med)
6. FDV Dilution Risk (Market Cap vs FDV)
7. Data Quality & Source Freshness Risk
8. Exchange Availability Risk (DEX unverified vs CEX Tier 1)
"""

import time
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from .coin_discovery_engine import DiscoveredCoin

class RiskVectorDetail(BaseModel):
    name: str
    level: str  # LOW, MEDIUM, HIGH, UNKNOWN
    score: float  # 0.0 (Safe) - 100.0 (Extreme Risk)
    explanation: str

class CoinRiskReport(BaseModel):
    symbol: str
    overall_risk_level: str  # LOW, MEDIUM, HIGH, UNKNOWN
    overall_risk_score: float  # 0 - 100
    risk_vectors: List[RiskVectorDetail] = Field(default_factory=list)
    key_warnings: List[str] = Field(default_factory=list)
    data_completeness_pct: float
    timestamp: float = Field(default_factory=time.time)

class CoinRiskEngine:
    """Evaluates multi-dimensional risk for new and meme coins."""

    def evaluate_risk(self, coin: DiscoveredCoin) -> CoinRiskReport:
        now = time.time()
        vectors: List[RiskVectorDetail] = []
        warnings: List[str] = []
        fields_checked = 8
        fields_present = 0

        # Vector 1: Liquidity Risk
        if coin.liquidity_usd is not None:
            fields_present += 1
            if coin.liquidity_usd < 10000.0:
                vectors.append(RiskVectorDetail(
                    name="Liquidity Depth",
                    level="HIGH",
                    score=95.0,
                    explanation=f"Dangerously low liquidity pool (${coin.liquidity_usd:,.0f} USD). High slippage / rug risk."
                ))
                warnings.append("Ultra-low pool liquidity (< $10k)")
            elif coin.liquidity_usd < 100000.0:
                vectors.append(RiskVectorDetail(
                    name="Liquidity Depth",
                    level="MEDIUM",
                    score=50.0,
                    explanation=f"Moderate pool liquidity (${coin.liquidity_usd:,.0f} USD)."
                ))
            else:
                vectors.append(RiskVectorDetail(
                    name="Liquidity Depth",
                    level="LOW",
                    score=15.0,
                    explanation=f"Healthy liquidity depth (${coin.liquidity_usd:,.0f} USD)."
                ))
        else:
            vectors.append(RiskVectorDetail(
                name="Liquidity Depth",
                level="UNKNOWN",
                score=35.0,
                explanation="Liquidity pool depth data unavailable from source (CEX orderbook format)."
            ))

        # Vector 2: Volatility Risk
        vol = coin.volatility_pct or (abs(coin.price_change_24h_pct) if coin.price_change_24h_pct is not None else None)
        if vol is not None:
            fields_present += 1
            if vol > 40.0:
                vectors.append(RiskVectorDetail(
                    name="24h Volatility",
                    level="HIGH",
                    score=85.0,
                    explanation=f"Extreme price swing ({vol:.1f}% 24h range). High liquidation/drawdown risk."
                ))
                warnings.append(f"Extreme 24h volatility ({vol:.1f}%)")
            elif vol > 15.0:
                vectors.append(RiskVectorDetail(
                    name="24h Volatility",
                    level="MEDIUM",
                    score=50.0,
                    explanation=f"Elevated price volatility ({vol:.1f}% 24h range)."
                ))
            else:
                vectors.append(RiskVectorDetail(
                    name="24h Volatility",
                    level="LOW",
                    score=15.0,
                    explanation=f"Stable price range ({vol:.1f}% 24h range)."
                ))
        else:
            vectors.append(RiskVectorDetail(
                name="24h Volatility",
                level="UNKNOWN",
                score=35.0,
                explanation="Volatility range metrics unavailable."
            ))

        # Vector 3: Spread Risk
        if coin.spread_bps is not None:
            fields_present += 1
            if coin.spread_bps > 100.0:
                vectors.append(RiskVectorDetail(
                    name="Bid/Ask Spread",
                    level="HIGH",
                    score=85.0,
                    explanation=f"Wide execution spread ({coin.spread_bps:.1f} bps). High instant execution friction."
                ))
                warnings.append(f"Wide spread ({coin.spread_bps:.1f} bps)")
            elif coin.spread_bps > 30.0:
                vectors.append(RiskVectorDetail(
                    name="Bid/Ask Spread",
                    level="MEDIUM",
                    score=40.0,
                    explanation=f"Moderate execution spread ({coin.spread_bps:.1f} bps)."
                ))
            else:
                vectors.append(RiskVectorDetail(
                    name="Bid/Ask Spread",
                    level="LOW",
                    score=10.0,
                    explanation=f"Tight institutional spread ({coin.spread_bps:.1f} bps)."
                ))
        else:
            vectors.append(RiskVectorDetail(
                name="Bid/Ask Spread",
                level="UNKNOWN",
                score=30.0,
                explanation="Bid/Ask spread not provided directly by API."
            ))

        # Vector 4: Volume Anomaly Risk
        if coin.volume_24h_usd is not None and coin.liquidity_usd is not None and coin.liquidity_usd > 0:
            fields_present += 1
            vol_to_liq = coin.volume_24h_usd / coin.liquidity_usd
            threshold_high = 40.0 if "BINANCE" in coin.exchange else 15.0
            if vol_to_liq > threshold_high:
                vectors.append(RiskVectorDetail(
                    name="Volume/Liquidity Anomaly",
                    level="HIGH",
                    score=75.0,
                    explanation=f"Volume is {vol_to_liq:.1f}x liquidity. Potential churn or wash trading."
                ))
                warnings.append("Abnormal volume-to-liquidity turnover")
            elif vol_to_liq < 0.01:
                vectors.append(RiskVectorDetail(
                    name="Volume/Liquidity Anomaly",
                    level="HIGH",
                    score=70.0,
                    explanation="Dead pool: Very little trading volume relative to locked capital."
                ))
            else:
                vectors.append(RiskVectorDetail(
                    name="Volume/Liquidity Anomaly",
                    level="LOW",
                    score=15.0,
                    explanation=f"Balanced volume-to-liquidity ratio ({vol_to_liq:.2f}x)."
                ))
        else:
            vectors.append(RiskVectorDetail(
                name="Volume/Liquidity Anomaly",
                level="UNKNOWN",
                score=25.0,
                explanation="Volume-to-liquidity comparison not applicable."
            ))

        # Vector 5: Listing Age Risk
        if coin.listing_ts is not None:
            fields_present += 1
            age_hours = (now - coin.listing_ts) / 3600.0
            if age_hours < 24.0:
                vectors.append(RiskVectorDetail(
                    name="Listing Age",
                    level="HIGH",
                    score=85.0,
                    explanation=f"Brand new token created {age_hours:.1f} hours ago. High initial volatility / rug pull window."
                ))
                warnings.append(f"Newly created token ({age_hours:.1f}h old)")
            elif age_hours < 168.0:  # < 7 days
                vectors.append(RiskVectorDetail(
                    name="Listing Age",
                    level="MEDIUM",
                    score=45.0,
                    explanation=f"Recent token listed {age_hours/24.0:.1f} days ago."
                ))
            else:
                vectors.append(RiskVectorDetail(
                    name="Listing Age",
                    level="LOW",
                    score=10.0,
                    explanation=f"Established listing history ({age_hours/24.0:.0f} days active)."
                ))
        else:
            vectors.append(RiskVectorDetail(
                name="Listing Age",
                level="UNKNOWN",
                score=25.0,
                explanation="Pair creation date not exposed."
            ))

        # Vector 6: FDV Dilution Risk
        if coin.market_cap_usd is not None and coin.fdv_usd is not None and coin.fdv_usd > 0:
            fields_present += 1
            mcap_ratio = coin.market_cap_usd / coin.fdv_usd
            if mcap_ratio < 0.15:
                vectors.append(RiskVectorDetail(
                    name="FDV Dilution",
                    level="HIGH",
                    score=80.0,
                    explanation=f"Severe token overhang: Market Cap is only {mcap_ratio*100:.1f}% of Fully Diluted Valuation."
                ))
                warnings.append("High future token unlock dilution")
            else:
                vectors.append(RiskVectorDetail(
                    name="FDV Dilution",
                    level="LOW",
                    score=15.0,
                    explanation=f"Reasonable circulating supply ratio ({mcap_ratio*100:.1f}% of FDV)."
                ))
        else:
            vectors.append(RiskVectorDetail(
                name="FDV Dilution",
                level="UNKNOWN",
                score=25.0,
                explanation="FDV / Market Cap breakdown unavailable."
            ))

        # Vector 7: Data Quality & Freshness Risk
        fields_present += 1
        if coin.data_freshness_seconds > 120.0:
            vectors.append(RiskVectorDetail(
                name="Data Freshness",
                level="HIGH",
                score=70.0,
                explanation=f"Market data is stale ({coin.data_freshness_seconds:.0f}s old)."
            ))
            warnings.append("Stale market data quote")
        else:
            vectors.append(RiskVectorDetail(
                name="Data Freshness",
                level="LOW",
                score=10.0,
                explanation=f"Fresh live market data ({coin.data_freshness_seconds:.1f}s old)."
            ))

        # Vector 8: Exchange Listing Risk
        fields_present += 1
        if "BINANCE" in coin.exchange:
            vectors.append(RiskVectorDetail(
                name="Exchange Venue",
                level="LOW",
                score=10.0,
                explanation="Listed on Tier-1 Centralized Exchange with institutional compliance."
            ))
        else:
            vectors.append(RiskVectorDetail(
                name="Exchange Venue",
                level="MEDIUM",
                score=40.0,
                explanation=f"Decentralized exchange pool ({coin.exchange}). Subject to smart contract execution risk."
            ))

        # Calculate Overall Risk Score: Weighted combination of average + peak risk vector
        scores = [v.score for v in vectors if v.score is not None]
        avg_score = sum(scores) / len(scores) if scores else 50.0
        max_score = max(scores) if scores else 50.0
        
        # Tail-risk weighting: 50% average + 50% peak vector risk
        composite_score = round((avg_score * 0.5) + (max_score * 0.5), 1)

        high_count = sum(1 for v in vectors if v.level == "HIGH")
        if high_count >= 2 or composite_score >= 60.0:
            overall_level = "HIGH"
        elif high_count == 1 or composite_score >= 35.0:
            overall_level = "MEDIUM"
        else:
            overall_level = "LOW"

        completeness = round((fields_present / fields_checked) * 100.0, 1)

        return CoinRiskReport(
            symbol=coin.symbol,
            overall_risk_level=overall_level,
            overall_risk_score=composite_score,
            risk_vectors=vectors,
            key_warnings=warnings,
            data_completeness_pct=completeness,
            timestamp=now
        )

coin_risk_engine = CoinRiskEngine()
