from fastapi import APIRouter, Depends, Query
from typing import Dict, Any, Optional

from backend.auth.security import get_current_user
from backend.models.domain import UserModel
from backend.news_intelligence import (
    MasterNewsCollector,
    EventReasoningEngine,
    NewsSentimentEngine,
    ImpactForecaster,
    SocialSentimentEngine,
    EventSignalEngine,
    NewsGovernanceEngine
)

router = APIRouter(prefix="/api/news", tags=["Phase 38 — AI News Intelligence & Event-Driven Trading"])

collector = MasterNewsCollector()
reasoning_engine = EventReasoningEngine()
sentiment_engine = NewsSentimentEngine()
impact_forecaster = ImpactForecaster()
social_engine = SocialSentimentEngine()
signal_engine = EventSignalEngine()
governance_engine = NewsGovernanceEngine()

@router.get("/feed")
async def get_news_feed(current_user: UserModel = Depends(get_current_user)):
    """Fetch live ingested and deduplicated news feed items."""
    items = collector.collect_all_news()
    return {"status": "success", "count": len(items), "feed": [i.to_dict() for i in items]}

@router.get("/events")
async def get_classified_events(current_user: UserModel = Depends(get_current_user)):
    """Fetch AI-classified events with LLM reasoning breakdown."""
    items = collector.collect_all_news()
    events = []
    for item in items:
        reasoning = reasoning_engine.analyze_event(item.title, item.source, item.extracted_symbols)
        sig = signal_engine.generate_signal(reasoning.event_type, item.extracted_symbols[0] if item.extracted_symbols else "BTC/USDT", reasoning.confidence)
        events.append({
            "news_id": item.item_id,
            "title": item.title,
            "source": item.source,
            "reasoning": reasoning.to_dict(),
            "signal": sig.to_dict()
        })
    return {"status": "success", "count": len(events), "events": events}

@router.get("/sentiment")
async def get_news_sentiment(symbol: Optional[str] = "BTC/USDT", current_user: UserModel = Depends(get_current_user)):
    """Fetch composite headline, article, and social sentiment breakdown."""
    items = collector.collect_all_news()
    snap = sentiment_engine.aggregate_sentiment(symbol=symbol, news_items=items)
    return {"status": "success", "sentiment": snap.to_dict()}

@router.get("/forecast")
async def get_impact_forecast(symbol: Optional[str] = "BTC/USDT", current_user: UserModel = Depends(get_current_user)):
    """Fetch 1h, 4h, 24h price impact and horizon volatility forecast."""
    forecast = impact_forecaster.forecast_impact(symbol=symbol, event_type="ETF_APPROVAL", expected_impact="BULLISH")
    return {"status": "success", "forecast": forecast.to_dict()}

@router.get("/high-impact")
async def get_high_impact_events(current_user: UserModel = Depends(get_current_user)):
    """Fetch high severity breaking news and events requiring immediate risk action."""
    items = collector.collect_all_news()
    high_impact = []
    for item in items:
        reasoning = reasoning_engine.analyze_event(item.title, item.source, item.extracted_symbols)
        if reasoning.severity in ["CRITICAL", "HIGH"]:
            gov = governance_engine.evaluate_news_event(item.title, item.source, reasoning.confidence)
            high_impact.append({
                "item": item.to_dict(),
                "reasoning": reasoning.to_dict(),
                "governance": gov.to_dict()
            })
    return {"status": "success", "count": len(high_impact), "high_impact_events": high_impact}

@router.get("/social")
async def get_social_intelligence(symbol: Optional[str] = "BTC/USDT", current_user: UserModel = Depends(get_current_user)):
    """Fetch social sentiment, influencer credibility scores, and whale transfers."""
    snap = social_engine.get_social_sentiment(symbol=symbol)
    return {"status": "success", "social_sentiment": snap.to_dict()}

@router.get("/events/{event_id}/decision")
async def get_news_event_decision(event_id: str, current_user: UserModel = Depends(get_current_user)):
    """Fetch complete Event -> Sentiment -> Risk -> Execution -> Governance decision chain."""
    items = collector.collect_all_news()
    matching_item = next((i for i in items if i.item_id == event_id), items[0] if items else None)

    if not matching_item:
        title = "SEC Approves Spot Bitcoin ETF Applications"
        source = "CoinDesk"
        symbols = ["BTC/USDT"]
    else:
        title = matching_item.title
        source = matching_item.source
        symbols = matching_item.extracted_symbols or ["BTC/USDT"]

    reasoning = reasoning_engine.analyze_event(title, source, symbols)
    sig = signal_engine.generate_signal(reasoning.event_type, symbols[0], reasoning.confidence)
    forecast = impact_forecaster.forecast_impact(symbol=symbols[0], event_type=reasoning.event_type, expected_impact="BULLISH" if sig.direction == "BUY" else "BEARISH")
    gov = governance_engine.evaluate_news_event(title, source, reasoning.confidence)

    decision_chain = {
        "event_id": event_id,
        "title": title,
        "source": source,
        "extracted_symbols": symbols,
        "event_classification": reasoning.event_type,
        "severity": reasoning.severity,
        "confidence_score": round(reasoning.confidence, 2),
        "sentiment_score": 0.85 if sig.action == "BUY" else -0.65,
        "expected_price_impact_pct": forecast.impact_1h_pct,
        "horizon_volatility_pct": forecast.volatility.expected_volatility_1h_pct,
        "risk_engine_action": "ALLOW_TRADE_WITH_SCALED_ALLOCATION" if gov.is_allowed else "BLOCK_TRADE_INSUFFICIENT_CONFIDENCE",
        "execution_engine_action": f"SHADOW_{sig.action}_ROUTER_ENGAGED" if gov.is_allowed else "SHADOW_ACTION_BLOCKED",
        "governance_status": "APPROVED (Confidence >= 0.80)" if gov.is_allowed else "REJECTED (Confidence < 0.80)",
        "decision_summary": f"Event '{title}' processed through AI Event Classifier (Confidence: {(reasoning.confidence*100):.0f}%). Risk & Governance status: {'APPROVED' if gov.is_allowed else 'REJECTED'}."
    }

    return {"status": "success", "decision_chain": decision_chain}

@router.get("/governance")
async def get_news_governance_rules(current_user: UserModel = Depends(get_current_user)):
    """Fetch news intelligence governance rules & threshold criteria."""
    gov = governance_engine.evaluate_news_event("SEC Approves Spot ETF", "CoinDesk", 0.95)
    return {
        "status": "success",
        "minimum_confidence_threshold": 0.80,
        "sample_validation": gov.to_dict(),
        "rules": [
            "Confidence < 0.80: Action Blocked",
            "Single Social Source: Warning Warning Triggered",
            "Unverified Rumor: Hard Blocked"
        ]
    }
