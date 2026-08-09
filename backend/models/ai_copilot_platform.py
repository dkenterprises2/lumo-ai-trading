from typing import Optional
from sqlalchemy import String, Float, Integer, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.session import Base

class CopilotWorkspaceModel(Base):
    """Copilot Workspaces Table."""
    __tablename__ = "p24_copilot_workspaces"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    workspace_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)

class CopilotConversationModel(Base):
    """Copilot Conversations Table."""
    __tablename__ = "copilot_conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    conversation_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class CopilotMessageModel(Base):
    """Copilot Messages Table."""
    __tablename__ = "copilot_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    msg_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class ConversationContextSnapshotModel(Base):
    """Conversation Context Snapshots Table."""
    __tablename__ = "conversation_context_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    snap_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class NLStrategyRequestModel(Base):
    """NL Strategy Requests Table."""
    __tablename__ = "nl_strategy_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    req_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class GeneratedStrategySpecModel(Base):
    """Generated Strategy Specs Table."""
    __tablename__ = "generated_strategy_specs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    spec_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class AIRecommendationModel(Base):
    """AI Recommendations Table."""
    __tablename__ = "ai_recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    rec_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class AIActionRequestModel(Base):
    """AI Action Requests Table."""
    __tablename__ = "ai_action_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    action_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class AIActionApprovalModel(Base):
    """AI Action Approvals Table."""
    __tablename__ = "ai_action_approvals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    approval_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class InvestigationReportModel(Base):
    """Investigation Reports Table."""
    __tablename__ = "investigation_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    report_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class InvestigationEvidenceItemModel(Base):
    """Investigation Evidence Items Table."""
    __tablename__ = "investigation_evidence_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    item_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class IncidentEventModel(Base):
    """Incident Events Table."""
    __tablename__ = "incident_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class AutonomousRemediationActionModel(Base):
    """Autonomous Remediation Actions Table."""
    __tablename__ = "autonomous_remediation_actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    action_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class RAGDocumentModel(Base):
    """RAG Documents Table."""
    __tablename__ = "rag_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    document_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class RAGDocumentVersionModel(Base):
    """RAG Document Versions Table."""
    __tablename__ = "rag_document_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ver_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class RAGChunkModel(Base):
    """RAG Chunks Table."""
    __tablename__ = "rag_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    chunk_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class RAGRetrievalLogModel(Base):
    """RAG Retrieval Logs Table."""
    __tablename__ = "rag_retrieval_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    log_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class AgentWorkflowModel(Base):
    """Agent Workflows Table."""
    __tablename__ = "agent_workflows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    workflow_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class AgentTaskModel(Base):
    """Agent Tasks Table."""
    __tablename__ = "agent_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    task_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class AgentMessageModel(Base):
    """Agent Messages Table."""
    __tablename__ = "p24_agent_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    msg_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class MemoryEntryModel(Base):
    """Memory Entries Table."""
    __tablename__ = "memory_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    entry_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class DecisionProvenanceNodeModel(Base):
    """Decision Provenance Nodes Table."""
    __tablename__ = "decision_provenance_nodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    node_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class DecisionProvenanceEdgeModel(Base):
    """Decision Provenance Edges Table."""
    __tablename__ = "decision_provenance_edges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    edge_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class GuardrailEventModel(Base):
    """Guardrail Events Table."""
    __tablename__ = "guardrail_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class ExecutiveBriefingModel(Base):
    """Executive Briefings Table."""
    __tablename__ = "executive_briefings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    briefing_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
