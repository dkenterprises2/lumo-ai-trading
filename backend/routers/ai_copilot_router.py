from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from backend.models.domain import UserModel
from backend.auth.security import get_current_user, get_optional_current_user
from backend.ai_copilot.copilot.copilot_service import copilot_service
from backend.ai_copilot.portfolio_assistant.portfolio_assistant_service import portfolio_assistant_service
from backend.ai_copilot.investigation.rca_service import trade_rca_service
from backend.ai_copilot.operations_ai.sre_service import sre_service
from backend.ai_copilot.orchestration.orchestration_service import agent_orchestration_service
from backend.ai_copilot.guardrails.policy_engine import guardrail_policy_engine
from backend.ai_copilot.reports.executive_briefing import executive_briefing_engine

router = APIRouter(tags=["Enterprise AI Copilot, Natural Language Trading & Autonomous Operations"])

@router.post("/api/copilot/chat")
async def chat_with_copilot(
    body: Dict[str, Any],
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    """Conversational quantitative copilot chat endpoint."""
    user_id = current_user.id if current_user else 1
    query = body.get("query", body.get("message", "Explain my portfolio risk"))
    workspace_id = body.get("workspace_id", "default")
    history = body.get("history", [])
    return await copilot_service.process_chat_async(
        query=query,
        user_id=user_id,
        workspace_id=workspace_id,
        history=history
    )

@router.get("/api/portfolio-assistant/summary")
async def get_portfolio_assistant_summary(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    user_id = current_user.id if current_user else 1
    return await portfolio_assistant_service.get_portfolio_explanation(user_id=user_id)

@router.post("/api/portfolio-assistant/explain")
async def explain_portfolio_risk(body: Dict[str, Any], current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    user_id = current_user.id if current_user else 1
    return await portfolio_assistant_service.get_portfolio_explanation(user_id=user_id)

@router.get("/api/investigation/recent-trades")
async def list_recent_trades(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    user_id = current_user.id if current_user else 1
    return await trade_rca_service.list_recent_trades(user_id=user_id)

@router.post("/api/investigation/trades/{order_id}")
async def investigate_trade_rca(order_id: str, current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    user_id = current_user.id if current_user else 1
    return await trade_rca_service.analyze_trade_rca(order_id=order_id, user_id=user_id)

@router.get("/api/operations/incidents")
async def list_incidents(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    return sre_service.get_system_health()

@router.post("/api/operations/incidents/{incident_id}/remediate")
async def remediate_incident(incident_id: str, current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    return sre_service.remediate_component(incident_id)

@router.get("/api/orchestration/workflows")
async def list_agent_workflows(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    return await agent_orchestration_service.list_workflows()

@router.post("/api/governance/ai-actions/{action_id}/approve")
async def approve_ai_action(action_id: str, current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    eval_res = guardrail_policy_engine.evaluate_action("LIVE_DEPLOYMENT", "ADMIN")
    return {"action_id": action_id, "status": "APPROVED", "decision": eval_res["decision"]}

@router.post("/api/governance/ai-actions/{action_id}/reject")
async def reject_ai_action(action_id: str, current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    return {"action_id": action_id, "status": "REJECTED"}
