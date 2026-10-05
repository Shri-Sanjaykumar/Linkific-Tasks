"""
Linkific Enterprise AI Service - Data Schemas & Contracts
Pydantic v2 validation models for Multi-Agent Workflows, Finance Automation, and System Telemetry.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field, field_validator


# ==============================================================================
# Enumerations
# ==============================================================================
class AgentRole(str, Enum):
    COORDINATOR = "coordinator_agent"
    RESEARCHER = "research_agent"
    ANALYZER = "analyzer_agent"
    CRITIC = "critic_agent"
    WRITER = "writer_agent"
    ERROR_HANDLER = "error_handler"


class MessageType(str, Enum):
    USER_REQUEST = "user_request"
    TASK_ASSIGNMENT = "task_assignment"
    RESEARCH_SUBMISSION = "research_submission"
    ANALYSIS_SUBMISSION = "analysis_submission"
    CRITIC_REVIEW = "critic_review"
    REVISION_REQUEST = "revision_request"
    REPORT_DRAFT = "report_draft"
    FINAL_ANSWER = "final_answer"
    ERROR_NOTIFICATION = "error_notification"


class WorkflowStatus(str, Enum):
    INITIALIZED = "initialized"
    PLANNING = "planning"
    RESEARCHING = "researching"
    ANALYZING = "analyzing"
    REVIEWING = "reviewing"
    REVISING = "revising"
    WRITING = "writing"
    COMPLETED = "completed"
    FAILED = "failed"


class ApprovalTier(str, Enum):
    STRAIGHT_THROUGH = "straight_through_processing"
    MANAGER_APPROVAL = "manager_approval"
    DIRECTOR_APPROVAL = "director_approval"
    REJECTED = "rejected"


# ==============================================================================
# Multi-Agent State & Communication Models
# ==============================================================================
class EvidenceItem(BaseModel):
    claim_id: str
    doc_id: str
    excerpt: str
    category: str
    relevance_score: float = Field(ge=0.0, le=1.0)


class ResearchFindings(BaseModel):
    query: str
    items: List[EvidenceItem] = Field(default_factory=list)
    total_retrieved: int = 0
    sources_used: List[str] = Field(default_factory=list)


class InsightItem(BaseModel):
    insight_id: str
    category: str
    summary: str
    grounding_claims: List[str]
    confidence: float = Field(ge=0.0, le=1.0)


class AnalysisResult(BaseModel):
    insights: List[InsightItem] = Field(default_factory=list)
    thematic_clusters: List[str] = Field(default_factory=list)
    overall_confidence: float = Field(default=0.85, ge=0.0, le=1.0)


class CriticReview(BaseModel):
    verdict: str  # "approved" or "rejected"
    quality_score: float = Field(ge=0.0, le=1.0)
    defect_count: int = 0
    critique_notes: List[str] = Field(default_factory=list)
    factual_accuracy_checks: Dict[str, bool] = Field(default_factory=dict)
    citation_coverage: float = Field(default=100.0, ge=0.0, le=100.0)


class WriterReport(BaseModel):
    report_id: str
    title: str
    executive_summary: str
    sections: Dict[str, str] = Field(default_factory=dict)
    evidence_matrix: Dict[str, List[str]] = Field(default_factory=dict)
    strategic_recommendations: List[str] = Field(default_factory=list)
    citations: List[str] = Field(default_factory=list)


class Milestone(BaseModel):
    step: int = 1
    step_number: Optional[int] = None
    agent: str = "coordinator_agent"
    assigned_agent: Optional[str] = None
    task: str = "Execution"
    name: Optional[str] = None
    status: str = "pending"
    details: str = ""
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None

    def model_post_init(self, __context: Any) -> None:
        if self.step_number is None:
            self.step_number = self.step
        else:
            self.step = self.step_number
        if self.name is None:
            self.name = self.task
        else:
            self.task = self.name
        if self.assigned_agent is None:
            self.assigned_agent = self.agent
        else:
            self.agent = self.assigned_agent



class AgentMessage(BaseModel):
    message_id: str = Field(default_factory=lambda: f"MSG-{uuid.uuid4().hex[:8].upper()}")
    correlation_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    sender: str
    recipient: str
    message_type: MessageType
    payload: Dict[str, Any] = Field(default_factory=dict)
    summary: str


# ==============================================================================
# API Request & Response Contracts
# ==============================================================================
class WorkflowRequest(BaseModel):
    query: str = Field(..., min_length=3, description="Inquiry to process through the Linkific Multi-Agent System")
    mode: str = Field(default="streamlined", description="Execution topology: 'streamlined' or 'comprehensive'")
    correlation_id: Optional[str] = Field(default=None, description="Optional distributed tracing correlation ID")

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v: str) -> str:
        val = v.lower().strip()
        if val not in {"streamlined", "comprehensive"}:
            raise ValueError("mode must be either 'streamlined' or 'comprehensive'")
        return val


class WorkflowResponse(BaseModel):
    workflow_id: str
    correlation_id: str
    status: str
    execution_time_seconds: float
    final_answer: str
    critic_approved: bool
    milestones_completed: int
    report: Optional[WriterReport] = None
    communication_hops: int = 0
    errors: List[str] = Field(default_factory=list)


# ==============================================================================
# Finance Automation Models (Linkific Practical)
# ==============================================================================
class InvoiceLineItem(BaseModel):
    item_name: str
    quantity: int = Field(gt=0)
    unit_price: float = Field(ge=0.0)
    total_price: float = Field(ge=0.0)


class FinanceApprovalRequest(BaseModel):
    invoice_id: str = Field(..., min_length=3)
    po_number: str = Field(..., min_length=3)
    vendor_name: str = Field(..., min_length=2)
    amount: float = Field(..., ge=0.0)
    currency: str = Field(default="USD")
    line_items: List[InvoiceLineItem] = Field(default_factory=list)
    submitted_by: str = Field(default="system_ingest")


class FinanceApprovalResponse(BaseModel):
    invoice_id: str
    po_number: str
    vendor_name: str
    amount: float
    currency: str
    status: str  # "approved", "pending_approval", "flagged"
    approval_tier: ApprovalTier
    required_signers: List[str]
    matched_po: bool
    auto_approved: bool
    audit_id: str
    timestamp: str
    routing_reason: str


# ==============================================================================
# System Health & Info Models
# ==============================================================================
class ComponentStatus(BaseModel):
    name: str
    status: str  # "healthy", "degraded", "unhealthy"
    details: str


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    environment: str
    uptime_seconds: float
    components: Dict[str, ComponentStatus]
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class SystemInfoResponse(BaseModel):
    app_name: str
    version: str
    environment: str
    debug: bool
    logging_level: str
    metrics_enabled: bool
    corpus_document_count: int
