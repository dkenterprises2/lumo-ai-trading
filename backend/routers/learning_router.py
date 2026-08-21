from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

from backend.models.domain import UserModel
from backend.auth.security import get_optional_current_user
from backend.learning.experience_memory import experience_memory, TradeExperience
from backend.learning.post_mortem_engine import post_mortem_engine, TradePostMortem
from backend.learning.lesson_extractor import lesson_extractor, LearnedLesson
from backend.learning.learning_memories import learning_memories
from backend.learning.human_feedback import human_feedback_manager
from backend.learning.counterfactual_engine import counterfactual_engine
from backend.learning.missed_opportunity_engine import missed_opportunity_engine
from backend.learning.self_diagnostic import self_diagnostic_engine
from backend.learning.learning_ab_validator import learning_ab_validator
from backend.learning.learning_agents import learning_agent_orchestrator

router = APIRouter(prefix="/api/learning", tags=["Phase 44.4 — Continuous Self-Learning Trade Memory Engine"])

class SubmitFeedbackRequest(BaseModel):
    experience_id: str
    rating: str = "CORRECT"  # CORRECT, INCORRECT, PARTIALLY_CORRECT, IRRELEVANT
    user_notes: str
    suggested_action: Optional[str] = None

class LessonStateRequest(BaseModel):
    new_status: str  # APPROVED, HYPOTHESIS, RETIRED, DEACTIVATED

@router.get("/experiences")
async def list_trade_experiences(
    symbol: Optional[str] = None,
    market_regime: Optional[str] = None,
    decision: Optional[str] = None,
    limit: int = 50,
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    """Fetch paginated trade experience records with full pre-trade context."""
    experiences = experience_memory.query_experiences(symbol=symbol, market_regime=market_regime, decision=decision, limit=limit)
    summary = experience_memory.get_summary_stats()
    return {
        "status": "success",
        "summary": summary,
        "count": len(experiences),
        "experiences": [e.to_dict() for e in experiences]
    }

@router.get("/post-mortem/{experience_id}")
async def get_trade_post_mortem(
    experience_id: str,
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    """Fetch 13-point post-mortem RCA diagnostic, counterfactuals, and agent findings."""
    exp = experience_memory.get_experience(experience_id)
    if not exp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Experience {experience_id} not found")

    pm = post_mortem_engine.analyze_trade(exp)
    cf = counterfactual_engine.analyze_counterfactuals(exp)
    agent_audit = learning_agent_orchestrator.run_full_post_trade_audit(exp)
    user_fb = human_feedback_manager.get_feedback_for_experience(experience_id)

    return {
        "status": "success",
        "experience": exp.to_dict(),
        "post_mortem": pm.to_dict(),
        "counterfactuals": cf,
        "agent_audit": agent_audit,
        "user_feedback": user_fb
    }

@router.get("/lessons")
async def list_learned_lessons(
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    """Fetch all active, candidate, and retired learned lessons."""
    all_lessons = list(lesson_extractor.lessons.values())
    active_approved = [l.to_dict() for l in all_lessons if l.status == "APPROVED"]
    hypotheses = [l.to_dict() for l in all_lessons if l.status == "HYPOTHESIS"]
    retired = [l.to_dict() for l in all_lessons if l.status == "RETIRED"]

    return {
        "status": "success",
        "total_lessons_count": len(all_lessons),
        "approved_active_count": len(active_approved),
        "hypotheses_count": len(hypotheses),
        "approved_lessons": active_approved,
        "hypotheses": hypotheses,
        "retired_lessons": retired
    }

@router.post("/lessons/{lesson_id}/state")
async def update_lesson_status(
    lesson_id: str,
    body: LessonStateRequest,
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    """Explicit governance state change: APPROVED, HYPOTHESIS, RETIRED, DEACTIVATED."""
    success = lesson_extractor.set_lesson_status(lesson_id, body.new_status)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Lesson {lesson_id} not found")
    return {
        "status": "success",
        "lesson_id": lesson_id,
        "new_status": body.new_status.upper()
    }

@router.post("/feedback")
async def submit_human_feedback(
    body: SubmitFeedbackRequest,
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    """Record human review annotation on a trade experience."""
    u_id = str(current_user.id) if current_user else "1"
    fb = human_feedback_manager.record_feedback(
        experience_id=body.experience_id,
        user_id=u_id,
        rating=body.rating,
        user_notes=body.user_notes,
        suggested_action=body.suggested_action
    )
    return {"status": "success", "feedback": fb.to_dict()}

@router.get("/memories")
async def get_specialized_memories(
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    """Fetch Pattern Memory, Strategy-Regime Expectancy, and Arbitrage Failure Memories."""
    return {
        "status": "success",
        "pattern_memory": learning_memories.get_pattern_memory(),
        "strategy_regime_matrix": learning_memories.get_strategy_regime_matrix(),
        "arbitrage_failures": learning_memories.get_arbitrage_failures(limit=20)
    }

@router.get("/self-diagnostics")
async def get_self_diagnostics(
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    """Fetch Continuous Performance Decay Diagnosis & Auto-Throttling Status."""
    report = self_diagnostic_engine.run_diagnostics()
    return {"status": "success", "report": report.to_dict()}

@router.get("/ab-benchmark")
async def get_ab_benchmark_results(
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    """Fetch Out-of-Sample A/B performance comparison (Baseline vs Learning Enabled)."""
    res = learning_ab_validator.evaluate_ab_benchmark()
    return {"status": "success", "benchmark": res.to_dict()}

@router.get("/missed-opportunities")
async def get_missed_opportunities_summary(
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    """Fetch forward audit of NO_TRADE decisions to verify rejection filter efficiency."""
    summary = missed_opportunity_engine.get_summary()
    return {"status": "success", "summary": summary}
