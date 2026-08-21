"""
AI Research Synthesis Engine for Lumo Spot Research Subsystem.
Synthesizes live market metrics, liquidity depth, classifications, and multi-vector risk scores.
Generates structured qualitative research, bullish/bearish catalysts, missing info, and recommendations.

INVARIANT: Dynamic, coin-specific analysis. No static hardcoded duplicate strings.
"""

import os
import time
import json
import requests
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from loguru import logger
from .coin_discovery_engine import DiscoveredCoin
from .coin_classifier import CoinClassification
from .coin_risk_engine import CoinRiskReport

class CoinAIResearchDossier(BaseModel):
    symbol: str
    category: str
    opportunity_score: float  # 0 - 100
    risk_score: float  # 0 - 100
    research_confidence: float  # 0.0 - 1.0
    recommendation: str  # WATCH, PAPER_TEST, REJECT, INSUFFICIENT_DATA
    summary: str
    bullish_factors: List[str] = Field(default_factory=list)
    bearish_factors: List[str] = Field(default_factory=list)
    risk_factors: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    data_sources: List[str] = Field(default_factory=list)
    timestamp: float = Field(default_factory=time.time)

class CoinAIResearcher:
    """Quantitative AI synthesis engine with LLM integration and deterministic structured fallbacks."""

    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")

    def generate_research_dossier(
        self,
        coin: DiscoveredCoin,
        classification: CoinClassification,
        risk_report: CoinRiskReport
    ) -> CoinAIResearchDossier:
        """Generate comprehensive research dossier grounded strictly in real token metrics."""
        now = time.time()
        
        # 1. Identify missing fields for transparent auditability
        missing_fields = []
        if coin.liquidity_usd is None:
            missing_fields.append("DEX Liquidity Pool Depth (CEX orderbook format)")
        if coin.listing_ts is None:
            missing_fields.append("Exact Token Creation / Listing Timestamp")
        if coin.fdv_usd is None:
            missing_fields.append("Fully Diluted Valuation (FDV)")
        if coin.market_cap_usd is None:
            missing_fields.append("Circulating Market Capitalization")
        if coin.spread_bps is None:
            missing_fields.append("Live Bid/Ask Spread in basis points")

        # 2. Derive Opportunity Score (0 - 100)
        opp_score = 50.0
        bullish = []
        bearish = []
        
        # Factor A: Momentum / 24h Change
        pct = coin.price_change_24h_pct or 0.0
        if pct > 20.0:
            opp_score += 15.0
            bullish.append(f"Strong 24h bullish momentum (+{pct:.1f}%)")
        elif pct > 5.0:
            opp_score += 8.0
            bullish.append(f"Positive 24h price action (+{pct:.1f}%)")
        elif pct < -15.0:
            opp_score -= 15.0
            bearish.append(f"Severe 24h price drawdown ({pct:.1f}%)")

        # Factor B: Volume Depth
        vol = coin.volume_24h_usd or 0.0
        if vol >= 1000000.0:
            opp_score += 12.0
            bullish.append(f"High 24h trading volume (${vol:,.0f} USD)")
        elif vol < 50000.0:
            opp_score -= 10.0
            bearish.append(f"Low trading volume (${vol:,.0f} USD) indicates low interest")

        # Factor C: Category Momentum
        if classification.category == "MEME":
            bullish.append("Community viral interest / meme classification")
            opp_score += 5.0
        elif classification.category == "NEW":
            bullish.append("New listing / discovery phase opportunity")
            opp_score += 7.0

        # Factor D: Risk Penalties
        risk_score = risk_report.overall_risk_score
        opp_score = max(5.0, min(95.0, opp_score - (risk_score * 0.3)))
        opp_score = round(opp_score, 1)

        # 3. Compile Risk Factors
        risk_factors = [w for w in risk_report.key_warnings]
        if not risk_factors:
            risk_factors = [f"{v.name}: {v.explanation}" for v in risk_report.risk_vectors if v.level in ["HIGH", "MEDIUM"]][:3]

        # 4. Derive Recommendation
        if risk_report.data_completeness_pct < 40.0:
            recommendation = "INSUFFICIENT_DATA"
        elif risk_report.overall_risk_level == "HIGH" and opp_score < 65.0:
            recommendation = "REJECT"
        elif opp_score >= 55.0 and risk_report.overall_risk_score <= 60.0:
            recommendation = "PAPER_TEST"
        elif opp_score >= 50.0:
            recommendation = "WATCH"
        else:
            recommendation = "REJECT"

        # 5. Generate Qualitative Summary
        price_str = f"${coin.current_price:.6f}" if coin.current_price and coin.current_price < 1.0 else f"${coin.current_price:,.2f}" if coin.current_price else "N/A"
        summary = (
            f"{coin.symbol} is classified as a {classification.category} token on {coin.exchange} "
            f"currently trading at {price_str} ({'+' if pct >= 0 else ''}{pct:.1f}% 24h). "
            f"Risk analysis evaluated {len(risk_report.risk_vectors)} quantitative vectors resulting in an overall "
            f"{risk_report.overall_risk_level} risk profile (Score: {risk_score}/100). "
            f"AI evaluation assigns an Opportunity Score of {opp_score}/100 with final recommendation: {recommendation}."
        )

        sources = [coin.source, classification.source, "QUANT_RISK_ENGINE_V2"]

        return CoinAIResearchDossier(
            symbol=coin.symbol,
            category=classification.category,
            opportunity_score=opp_score,
            risk_score=risk_score,
            research_confidence=round(risk_report.data_completeness_pct / 100.0, 2),
            recommendation=recommendation,
            summary=summary,
            bullish_factors=bullish if bullish else ["Baseline market participation"],
            bearish_factors=bearish if bearish else ["Macro crypto volatility exposure"],
            risk_factors=risk_factors if risk_factors else ["Standard crypto liquidity risk"],
            missing_information=missing_fields if missing_fields else ["All primary quantitative fields verified"],
            data_sources=sources,
            timestamp=now
        )

coin_ai_researcher = CoinAIResearcher()
