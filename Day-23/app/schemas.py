"""
Day 23: Schemas and Data Contracts
Linkific Enterprise Multi-Agent System with LangGraph
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field, field_validator


# ==============================================================================
# Enumerations for Multi-Agent Topology & Communication
# ==============================================================================

class AgentRole(str, Enum):
    """Defined specialized agent roles participating in the multi-agent system."""
    USER = "user"
    COORDINATOR = "coordinator_agent"
    RESEARCH = "research_agent"
    RESEARCHER = "research_agent"
    ANALYZER = "analyzer_agent"
    CRITIC = "critic_agent"
    WRITER = "writer_agent"
    ERROR_HANDLER = "error_handler"


class MessageType(str, Enum):
    """Semantic classifications for inter-agent communication messages."""
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
    """Lifecycle status of the multi-agent workflow."""
    INITIALIZED = "initialized"
    PLANNING = "planning"
    RESEARCHING = "researching"
    ANALYZING = "analyzing"
    CRITIQUING = "critiquing"
    REVISING = "revising"
    WRITING = "writing"
    SYNTHESIZING = "synthesizing"
    COMPLETED = "completed"
    COMPLETED_WITH_WARNINGS = "completed_with_warnings"
    FAILED = "failed"


class CriticVerdict(str, Enum):
    """Validation outcomes issued by the adversarial Critic Agent."""
    APPROVED = "approved"
    REVISION_REQUIRED = "revision_required"
    REJECTED = "rejected"


class DefectSeverity(str, Enum):
    """Severity ratings for detected review defects."""
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    INFO = "info"


class DefectCategory(str, Enum):
    """Categories of quality defects audited by the Critic Agent."""
    MISSING_EVIDENCE = "missing_evidence"
    UNSUPPORTED_CLAIM = "unsupported_claim"
    HALLUCINATION = "hallucination"
    NUMERICAL_DISTORTION = "numerical_distortion"
    FORMAT_ERROR = "format_error"
    INCOMPLETE_SCOPE = "incomplete_scope"


# ==============================================================================
# Core Inter-Agent Communication Message Schema
# ==============================================================================

class AgentMessage(BaseModel):
    """
    Standardized typed envelope for all inter-agent communication.
    Documented in the Multi-Agent Communication Log.
    """
    message_id: str = Field(default_factory=lambda: f"MSG-{uuid.uuid4().hex[:8].upper()}")
    correlation_id: str = Field(..., description="Workflow execution correlation identifier")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    sender: AgentRole = Field(..., description="Agent role generating the message")
    recipient: AgentRole = Field(..., description="Intended receiver agent role")
    message_type: MessageType = Field(..., description="Classification of the message")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Domain-specific structured data")
    summary: str = Field(default="", description="Human-readable summary of communication event")

    @field_validator("correlation_id", "summary")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace.")
        return v.strip()


# ==============================================================================
# Domain Entities (Evidence, Analysis, Review, Report)
# ==============================================================================

class EvidenceItem(BaseModel):
    """Atomic factual unit retrieved from enterprise document repositories."""
    source_id: str = Field(..., description="Document identifier e.g. DOC-POL-001")
    title: str = Field(..., description="Document title")
    category: str = Field(..., description="Corporate knowledge domain e.g. Human Resources")
    excerpt: str = Field(..., description="Grounded textual excerpt preserving numerical figures")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")
    version: str = Field(default="1.0", description="Document revision version")
    author: str = Field(default="Enterprise", description="Authoring department or individual")


class ResearchFindings(BaseModel):
    """Consolidated research payload emitted by the Research Agent."""
    query: str = Field(..., description="Query addressed by research")
    evidence: List[EvidenceItem] = Field(default_factory=list, description="Validated evidence items")
    unresolved_queries: List[str] = Field(default_factory=list, description="Sub-questions with missing evidence")
    search_parameters: Dict[str, Any] = Field(default_factory=dict, description="Retrieval parameters used")
    status: str = Field(default="complete", description="complete, partial, or empty")

    @property
    def evidence_items(self) -> List[EvidenceItem]:
        return self.evidence

    @property
    def relevant_documents_count(self) -> int:
        return len(self.evidence)


class InsightItem(BaseModel):
    """Structured analytical deduction synthesized from evidence."""
    insight_id: str = Field(default_factory=lambda: f"INS-{uuid.uuid4().hex[:6].upper()}")
    topic: str = Field(..., description="Substantive theme or category")
    statement: str = Field(..., description="Synthesized insight statement with preserved facts")
    supporting_evidence_ids: List[str] = Field(default_factory=list, description="Referenced source IDs")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    is_assumption: bool = Field(default=False, description="Flag for working inferences vs empirical facts")


class AnalysisResult(BaseModel):
    """Cognitive synthesis product formulated by the Analyzer Agent."""
    key_insights: List[InsightItem] = Field(default_factory=list)
    thematic_clusters: Dict[str, List[str]] = Field(default_factory=dict)
    cross_document_correlations: List[str] = Field(default_factory=list)
    identified_gaps: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    overall_confidence: float = Field(default=1.0, ge=0.0, le=1.0)

    @property
    def insights(self) -> List[InsightItem]:
        return self.key_insights


class DefectItem(BaseModel):
    """Specific critique defect detected during adversarial audit."""
    category: DefectCategory
    severity: DefectSeverity
    description: str
    target_agent: AgentRole
    actionable_correction: str


class CriticReview(BaseModel):
    """Adversarial evaluation report produced by the Critic Agent."""
    review_id: str = Field(default_factory=lambda: f"REV-{uuid.uuid4().hex[:6].upper()}")
    verdict: CriticVerdict
    quality_score: float = Field(..., ge=0.0, le=1.0)
    citation_coverage_pct: float = Field(..., ge=0.0, le=100.0)
    defects: List[DefectItem] = Field(default_factory=list)
    revision_notes: Optional[str] = None
    audited_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def is_approved(self) -> bool:
        return self.verdict == CriticVerdict.APPROVED

    @property
    def score(self) -> float:
        return self.quality_score


class ReportSection(BaseModel):
    """Structured section within an executive intelligence brief."""
    title: str
    content: str
    cited_sources: List[str] = Field(default_factory=list)


class WriterReport(BaseModel):
    """Final executive briefing synthesized by the Writer Agent."""
    report_id: str = Field(default_factory=lambda: f"REP-{uuid.uuid4().hex[:6].upper()}")
    title: str
    executive_summary: str
    sections: List[ReportSection] = Field(default_factory=list)
    evidence_traceability_matrix: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Maps each insight/claim to verified source IDs"
    )
    limitations: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    markdown_output: str = Field(default="", description="Rendered publication-ready markdown")
    compiled_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class Milestone(BaseModel):
    """Execution step tracked by Coordinator Agent."""
    step_number: int
    name: str
    assigned_agent: AgentRole
    status: str = Field(default="pending")  # pending, in_progress, completed, failed
    description: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


# ==============================================================================
# Client Ingress & Egress Contracts
# ==============================================================================

class WorkflowRequest(BaseModel):
    """Inbound client request invoking the multi-agent workflow."""
    query: str = Field(..., min_length=3, description="Research brief or user question")
    mode: str = Field(default="streamlined", description="'streamlined' or 'comprehensive'")
    max_revisions: int = Field(default=2, ge=0, le=5)
    context: Dict[str, Any] = Field(default_factory=dict)


class WorkflowResponse(BaseModel):
    """Consolidated egress payload returned to the user."""
    workflow_id: str
    query: str
    status: WorkflowStatus
    final_answer: str
    executive_report: Optional[WriterReport] = None
    critic_approved: bool = Field(default=True)
    milestones: List[Milestone] = Field(default_factory=list)
    communication_log: List[AgentMessage] = Field(default_factory=list)
    execution_time_seconds: float = 0.0
    errors: List[str] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
