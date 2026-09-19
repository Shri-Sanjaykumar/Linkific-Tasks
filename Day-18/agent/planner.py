"""
Day 18 — Agent Planner
Analyzes user queries, determines task intent, and generates a structured,
ordered execution plan with target tools and expected outputs.
"""

import re
from typing import List
from .schemas import ExecutionPlan, PlanStep


class Planner:
    """Decomposes a user query into a verifiable, step-by-step execution plan."""

    OUT_OF_DOMAIN_KEYWORDS = {
        "stock", "price", "share", "crypto", "bitcoin", "weather",
        "cricket", "football", "movie", "celebrity", "recipe"
    }

    METADATA_KEYWORDS = {"metadata", "author", "version", "who wrote", "when was"}
    LOOKUP_PATTERNS = [r"doc-[a-z]+-\d+", r"doc-\d+"]

    @classmethod
    def identify_intent(cls, question: str) -> str:
        q_lower = question.lower()
        q_tokens = set(re.findall(r"[a-zA-Z0-9]+", q_lower))

        # Check for out-of-domain keywords
        if cls.OUT_OF_DOMAIN_KEYWORDS.intersection(q_tokens):
            return "unsupported_domain"

        # Check for metadata inquiry
        if cls.METADATA_KEYWORDS.intersection(q_tokens):
            return "document_metadata"

        # Check for direct document ID pattern
        for pat in cls.LOOKUP_PATTERNS:
            if re.search(pat, q_lower):
                return "document_lookup"

        # Standard document research query
        return "document_search"

    @classmethod
    def create_plan(cls, question: str) -> ExecutionPlan:
        intent = cls.identify_intent(question)
        steps: List[PlanStep] = []

        if intent == "unsupported_domain":
            steps = [
                PlanStep(
                    step_id=1,
                    description="Analyze query and detect out-of-domain subject matter.",
                    target_tool="domain_analysis",
                    expected_output="Flag topic as unsupported external domain."
                ),
                PlanStep(
                    step_id=2,
                    description="Check synthetic knowledge base operational boundaries.",
                    target_tool="scope_check",
                    expected_output="Confirm topic is outside internal policies, onboarding, training, and workflow documents."
                ),
                PlanStep(
                    step_id=3,
                    description="Evaluate information availability and decide on safe refusal.",
                    target_tool="decision",
                    expected_output="Decision to return controlled refusal to avoid unsupported statements."
                ),
                PlanStep(
                    step_id=4,
                    description="Synthesize safe polite refusal explaining knowledge base scope.",
                    target_tool="final_response",
                    expected_output="Controlled refusal stating available documentation categories."
                )
            ]

        elif intent == "document_lookup":
            match = re.search(r"doc-[a-z0-9-]+", question.lower())
            doc_id = match.group(0).upper() if match else "DOC-UNKNOWN"
            steps = [
                PlanStep(
                    step_id=1,
                    description=f"Identify explicit document identifier: '{doc_id}'.",
                    target_tool="analysis",
                    expected_output="Target document identifier isolated for direct lookup."
                ),
                PlanStep(
                    step_id=2,
                    description=f"Retrieve full structured document text and header metadata for '{doc_id}'.",
                    target_tool="document_lookup",
                    expected_output="Complete structured document text."
                ),
                PlanStep(
                    step_id=3,
                    description="Inspect returned document structure and verify target section content.",
                    target_tool="evaluation",
                    expected_output="Verified document content ready for synthesis."
                ),
                PlanStep(
                    step_id=4,
                    description="Format grounded factual response with source document attribution.",
                    target_tool="final_response",
                    expected_output="Factual response citing specific document ID and title."
                )
            ]

        elif intent == "document_metadata":
            match = re.search(r"doc-[a-z0-9-]+", question.lower())
            doc_id = match.group(0).upper() if match else "DOC-LEAVE-001"
            steps = [
                PlanStep(
                    step_id=1,
                    description=f"Query metadata catalog for document identifier: '{doc_id}'.",
                    target_tool="document_metadata",
                    expected_output="Retrieve author, category, version, and character counts."
                ),
                PlanStep(
                    step_id=2,
                    description="Validate metadata fields against system catalog schema.",
                    target_tool="evaluation",
                    expected_output="Confirmed non-null metadata attributes."
                ),
                PlanStep(
                    step_id=3,
                    description="Present structured metadata summary with source document attribution.",
                    target_tool="final_response",
                    expected_output="Formatted metadata report with version and author attribution."
                )
            ]

        else:
            # intent == "document_search"
            steps = [
                PlanStep(
                    step_id=1,
                    description="Tokenize query, filter stopwords, and extract core keywords.",
                    target_tool="analysis",
                    expected_output="List of substantive search keywords."
                ),
                PlanStep(
                    step_id=2,
                    description="Execute lexical relevance search across synthetic knowledge base chunks.",
                    target_tool="document_search",
                    expected_output="Ranked list of top-3 relevant chunks with term-overlap similarity scores."
                ),
                PlanStep(
                    step_id=3,
                    description="Inspect retrieved chunks and evaluate information sufficiency against threshold.",
                    target_tool="evaluation",
                    expected_output="Determine whether retrieved content sufficiently answers query."
                ),
                PlanStep(
                    step_id=4,
                    description="If sufficient, proceed to answer; if borderline, perform query refinement.",
                    target_tool="decision",
                    expected_output="Decision to synthesize answer or execute refined lexical search."
                ),
                PlanStep(
                    step_id=5,
                    description="Synthesize grounded final response with source document attribution.",
                    target_tool="final_response",
                    expected_output="Factual answer citing source document titles."
                )
            ]

        return ExecutionPlan(
            user_goal=f"Answer user question: '{question}'",
            intent=intent,
            steps=steps
        )
