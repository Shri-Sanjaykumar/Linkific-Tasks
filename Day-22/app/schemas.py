"""
Day 22 — Multi-Agent System Schemas & Data Contracts
Provides strongly typed Pydantic v2 schemas for:
- Agent Roles & Message Types
- Evidence Items & Research Findings
- Structured Analysis Insights & Gap Detection
- Adversarial Critic Quality Gates & Defect Classification
- Executive Report Outputs & Traceability Matrices
- Inter-Agent Communication Envelopes & Centralized Shared State
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field, field_validator


# ==============================================================================
# Enumerations for Multi-Agent Topology
# ==============================================================================

class AgentRole(str, Enum):
    """Defined specialized roles participating in the multi-agent system."""
    COORDINATOR = "coordinator_agent"
    RESEARCH = "research_agent"
    ANALYZER = "analyzer_agent"
    CRITIC = "critic_agent"
    WRITER = "writer_agent"


class MessageType(str, Enum):
    """Semantic classifications for inter-agent communication messages."""
    TASK_ASSIGNMENT = "task_assignment"
    RESEARCH_SUBMISSION = "research_submission"
    ANALYSIS_SUBMISSION = "analysis_submission"
    CRITIC_REVIEW = "critic_review"
    REVISION_REQUEST = "revision_request"
    REPORT_DRAFT = "report_draft"
    WORKFLOW_COMPLETED = "workflow_completed"
    ERROR_NOTIFICATION = "error_notification"


class MessageStatus(str, Enum):
    """Lifecycle status of transmitted inter-agent messages."""
    SENT = "sent"
    DELIVERED = "delivered"
    PROCESSED = "processed"
    FAILED = "failed"


class WorkflowStatus(str, Enum):
    """End-to-end lifecycle states of the multi-agent research workflow."""
    INITIALIZED = "initialized"
    PLANNING = "planning"
    RESEARCHING = "researching"
    ANALYZING = "analyzing"
    CRITIQUING = "critiquing"
    REVISING = "revising"
    WRITING = "writing"
    COMPLETED = "completed"
    FAILED = "failed"


class CriticVerdict(str, Enum):
    """Validation outcomes issued by the adversarial Critic Agent."""
    APPROVED = "approved"
    REVISION_REQUIRED = "revision_required"
    REJECTED = "rejected"


class DefectSeverity(str, Enum):
    """Impact severity of defects detected during quality critique."""
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    INFO = "info"


class DefectCategory(str, Enum):
    """Categorical classification of review defects."""
    MISSING_EVIDENCE = "missing_evidence"
    UNSUPPORTED_CLAIM = "unsupported_claim"
    HALLUCINATION = "hallucination"
    CONTRADICTION = "contradiction"
    INCOMPLETE_SCOPE = "incomplete_scope"
    FORMAT_ERROR = "format_error"


# ==============================================================================
# Research & Evidence Schemas
# ==============================================================================

class EvidenceItem(BaseModel):
    """Atomic factual unit retrieved from enterprise document repositories."""
    source_id: str = Field(..., description="Document identifier e.g. DOC-POL-001")
    title: str = Field(..., description="Document title")
    category: str = Field(..., description="Corporate knowledge domain e.g. Human Resources")
    excerpt: str = Field(..., description="Verbatim or highly grounded textual citation")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Semantic or lexical match score")
    version: str = Field(default="1.0", description="Document revision version")
    author: str = Field(default="Enterprise", description="Authoring department or individual")


class ResearchFindings(BaseModel):
    """Consolidated research payload emitted by the Research Agent."""
    query: str = Field(..., description="Query addressed by research")
    evidence: List[EvidenceItem] = Field(default_factory=list, description="Validated evidence items")
    unresolved_queries: List[str] = Field(default_factory=list, description="Sub-questions with missing evidence")
    search_parameters: Dict[str, Any] = Field(default_factory=dict, description="Retrieval parameters used")
    status: str = Field(default="complete", description="Research status: complete, partial, or empty")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ==============================================================================
# Analysis & Insight Schemas
# ==============================================================================

class InsightItem(BaseModel):
    """Structured analytical deduction synthesized by the Analyzer Agent."""
    insight_id: str = Field(default_factory=lambda: f"INS-{uuid.uuid4().hex[:6].upper()}")
    topic: str = Field(..., description="Focus topic or policy dimension")
    statement: str = Field(..., description="Analytical synthesis or factual finding")
    supporting_evidence_ids: List[str] = Field(default_factory=list, description="Referenced source IDs")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in the deduction")
    is_assumption: bool = Field(default=False, description="Flag indicating an inference vs strict fact")


class AnalysisResult(BaseModel):
    """Output contract emitted by the Analyzer Agent."""
    key_insights: List[InsightItem] = Field(default_factory=list)
    thematic_clusters: Dict[str, List[str]] = Field(default_factory=dict, description="Cluster name -> statement list")
    cross_document_correlations: List[str] = Field(default_factory=list, description="Inter-policy relationships")
    identified_gaps: List[str] = Field(default_factory=list, description="Information gaps or policy ambiguities")
    assumptions: List[str] = Field(default_factory=list, description="Unverified working assumptions")
    overall_confidence: float = Field(default=0.85, ge=0.0, le=1.0)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ==============================================================================
# Critic Review & Quality Gate Schemas
# ==============================================================================

class DefectItem(BaseModel):
    """Actionable defect flagged by the Critic Agent."""
    defect_id: str = Field(default_factory=lambda: f"DEF-{uuid.uuid4().hex[:6].upper()}")
    category: DefectCategory
    severity: DefectSeverity
    description: str = Field(..., description="Explanation of the discrepancy or gap")
    target_agent: AgentRole = Field(..., description="Agent assigned to rectify the defect")
    actionable_correction: str = Field(..., description="Specific instructions for remediation")


class CriticReview(BaseModel):
    """Quality evaluation emitted by the Critic Agent."""
    review_id: str = Field(default_factory=lambda: f"REV-{uuid.uuid4().hex[:6].upper()}")
    verdict: CriticVerdict
    quality_score: float = Field(..., ge=0.0, le=1.0, description="Holistic quality score")
    defects: List[DefectItem] = Field(default_factory=list)
    citation_coverage_pct: float = Field(..., ge=0.0, le=100.0, description="Percentage of insights with evidence")
    unsupported_claims_count: int = Field(default=0, ge=0)
    feedback_summary: str = Field(..., description="Executive verdict and direction for revision")
    revision_cycle: int = Field(default=0, ge=0, description="Revision iteration number (0 = initial)")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ==============================================================================
# Writer Report & Presentation Schemas
# ==============================================================================

class ReportSection(BaseModel):
    """Individual section of the final synthesized enterprise report."""
    title: str
    content: str
    cited_sources: List[str] = Field(default_factory=list)


class WriterReport(BaseModel):
    """Final comprehensive deliverable emitted by the Writer Agent."""
    report_id: str = Field(default_factory=lambda: f"REP-{uuid.uuid4().hex[:6].upper()}")
    title: str = Field(..., description="Report title")
    executive_summary: str = Field(..., description="Concise briefing of findings")
    sections: List[ReportSection] = Field(default_factory=list)
    evidence_traceability_matrix: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Maps insight statements or IDs to source documents"
    )
    limitations: List[str] = Field(default_factory=list, description="Explicit boundaries and gaps")
    recommendations: List[str] = Field(default_factory=list, description="Actionable next steps")
    markdown_output: str = Field(default="", description="Rendered publication-ready Markdown text")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ==============================================================================
# Workflow Planning & Inter-Agent Communication Schemas
# ==============================================================================

class ExecutionMilestone(BaseModel):
    """Individual milestone within the Coordinator's execution plan."""
    step_number: int = Field(..., ge=1)
    task_id: str
    assigned_agent: AgentRole
    description: str
    status: str = Field(default="pending", description="pending, running, completed, failed, skipped")
    start_time: Optional[str] = None
    end_time: Optional[str] = None


class ExecutionPlan(BaseModel):
    """Structured plan orchestrating the multi-agent execution order."""
    plan_id: str = Field(default_factory=lambda: f"PLAN-{uuid.uuid4().hex[:6].upper()}")
    goal: str = Field(..., description="Primary objective derived from user request")
    milestones: List[ExecutionMilestone] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AgentMessage(BaseModel):
    """Standardized envelope for structured inter-agent communication."""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str = Field(..., description="Unique ID of the parent workflow")
    task_id: str = Field(..., description="Specific milestone or task ID")
    sender: AgentRole
    receiver: AgentRole
    message_type: MessageType
    status: MessageStatus = Field(default=MessageStatus.SENT)
    payload: Dict[str, Any] = Field(default_factory=dict, description="Typed payload data")
    evidence_ids: List[str] = Field(default_factory=list, description="Referenced evidence keys")
    errors: List[str] = Field(default_factory=list, description="Errors encountered during execution")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ==============================================================================
# Client Request & Response Schemas
# ==============================================================================

class WorkflowRequest(BaseModel):
    """User input initiating the multi-agent research workflow."""
    user_query: str = Field(..., min_length=3, max_length=1000, description="Research question or topic")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional enterprise context")
    max_revisions: Optional[int] = Field(default=2, ge=0, le=5, description="Maximum critic revision cycles")

    @field_validator("user_query")
    @classmethod
    def validate_non_empty(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Query string cannot be empty or whitespace only.")
        return trimmed


class WorkflowResponse(BaseModel):
    """End-to-end response returned to the client upon workflow termination."""
    workflow_id: str
    status: WorkflowStatus
    user_query: str
    final_report: Optional[WriterReport] = None
    execution_plan: ExecutionPlan
    total_revisions: int = 0
    critic_approved: bool = False
    execution_time_seconds: float = 0.0
    audit_events_count: int = 0
    warnings: List[str] = Field(default_factory=list)
