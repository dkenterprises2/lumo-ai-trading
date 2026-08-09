from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from backend.models.domain import UserModel
from backend.routers.auth_router import get_current_user
from backend.ai_copilot.copilot.copilot_service import copilot_service
from backend.ai_copilot.nlp_trading.intent_parser import strategy_translator
from backend.ai_copilot.portfolio_assistant.portfolio_explainer import portfolio_explainer
from backend.ai_copilot.investigation.trade_investigator import trade_investigator
from backend.ai_copilot.operations_ai.incident_detector import operations_ai
from backend.ai_copilot.rag.document_ingestion import rag_engine
from backend.ai_copilot.orchestration.agent_registry import agentic_orchestrator
from backend.ai_copilot.memory.session_memory import memory_provenance
from backend.ai_copilot.guardrails.policy_engine import guardrail_policy_engine
from backend.ai_copilot.reports.executive_briefing import executive_briefing_engine

router = APIRouter(tags=["Enterprise AI Copilot, Natural Language Trading & Autonomous Operations"])

@router.post("/api/copilot/chat")
async def chat_copilot(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    ws_id = body.get("workspace_id", "ws_quant_team")
    query = body.get("query", "Explain current risk exposure")
    return copilot_service.process_chat(ws_id, current_user.email, query)

@router.get("/api/copilot/conversations")
async def list_conversations(current_user: UserModel = Depends(get_current_user)):
    return {"conversations": [{"conversation_id": "conv_copilot_101", "title": "Portfolio Risk & Execution Chat"}]}

@router.get("/api/copilot/conversations/{conversation_id}")
async def get_conversation(conversation_id: str, current_user: UserModel = Depends(get_current_user)):
    return {"conversation_id": conversation_id, "messages": 6, "status": "ACTIVE"}

@router.post("/api/nlp/strategy/build")
async def nlp_build_strategy(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    prompt = body.get("prompt", "Create BTC momentum strategy")
    return strategy_translator.parse_intent(prompt)

@router.post("/api/nlp/execution/validate")
async def nlp_validate_execution(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    return {"valid": True, "command": "BUY 1 BTCUSDT", "risk_approved": True}

@router.get("/api/portfolio-assistant/summary")
async def get_portfolio_assistant_summary(current_user: UserModel = Depends(get_current_user)):
    return portfolio_explainer.explain_portfolio()

@router.post("/api/portfolio-assistant/explain")
async def explain_portfolio_risk(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    return portfolio_explainer.explain_portfolio()

@router.post("/api/investigation/trades/{order_id}")
async def investigate_trade_rca(order_id: str, current_user: UserModel = Depends(get_current_user)):
    return trade_investigator.investigate_order(order_id)

@router.get("/api/investigation/reports/{report_id}")
async def get_investigation_report(report_id: str, current_user: UserModel = Depends(get_current_user)):
    return {"report_id": report_id, "confidence": 0.94, "status": "COMPLETED"}

@router.get("/api/operations/incidents")
async def list_incidents(current_user: UserModel = Depends(get_current_user)):
    return {"incidents": operations_ai.get_incidents()}

@router.post("/api/operations/incidents/{incident_id}/remediate")
async def remediate_incident(incident_id: str, current_user: UserModel = Depends(get_current_user)):
    return operations_ai.remediate_incident(incident_id)

@router.post("/api/rag/documents")
async def ingest_rag_document(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    title = body.get("title", "Risk Management Policy")
    content = body.get("content", "Policy text")
    return rag_engine.ingest_document(title, content)

@router.get("/api/rag/search")
async def search_rag(q: str = Query(..., alias="q"), current_user: UserModel = Depends(get_current_user)):
    return {"results": rag_engine.search_knowledge(q)}

@router.get("/api/rag/documents/{document_id}")
async def get_rag_document(document_id: str, current_user: UserModel = Depends(get_current_user)):
    return {"document_id": document_id, "title": "Institutional Risk Management Policy v4.0", "status": "INDEXED"}

@router.post("/api/orchestration/workflows")
async def create_agent_workflow(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    task_name = body.get("task_name", "AutoML to Shadow Deployment Workflow")
    return agentic_orchestrator.create_workflow(task_name)

@router.get("/api/orchestration/workflows/{workflow_id}")
async def get_agent_workflow(workflow_id: str, current_user: UserModel = Depends(get_current_user)):
    return {"workflow_id": workflow_id, "status": "RUNNING", "current_stage": "AlphaFactoryAgent"}

@router.post("/api/governance/ai-actions/{action_id}/approve")
async def approve_ai_action(action_id: str, current_user: UserModel = Depends(get_current_user)):
    eval_res = guardrail_policy_engine.evaluate_action("LIVE_DEPLOYMENT", "ADMIN")
    return {"action_id": action_id, "status": "APPROVED", "decision": eval_res["decision"]}

@router.post("/api/governance/ai-actions/{action_id}/reject")
async def reject_ai_action(action_id: str, current_user: UserModel = Depends(get_current_user)):
    return {"action_id": action_id, "status": "REJECTED"}

@router.get("/api/memory/workspaces/{workspace_id}")
async def get_workspace_memory(workspace_id: str, current_user: UserModel = Depends(get_current_user)):
    return memory_provenance.get_workspace_memory(workspace_id)

@router.delete("/api/memory/workspaces/{workspace_id}/purge")
async def purge_workspace_memory(workspace_id: str, current_user: UserModel = Depends(get_current_user)):
    return memory_provenance.purge_memory(workspace_id)

@router.get("/api/reports/executive/daily")
async def get_daily_executive_report(current_user: UserModel = Depends(get_current_user)):
    return executive_briefing_engine.generate_daily_briefing()

@router.post("/api/reports/executive/generate")
async def generate_executive_report(current_user: UserModel = Depends(get_current_user)):
    return executive_briefing_engine.generate_daily_briefing()
