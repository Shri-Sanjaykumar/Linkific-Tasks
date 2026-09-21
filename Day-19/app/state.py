"""
Shared State Schema for the LangGraph Workflow.
"""

from typing import TypedDict, List, Dict, Any, Optional

class WorkflowState(TypedDict, total=False):
    """
    Shared workflow state passed through LangGraph nodes.
    
    Fields:
    - question: The active query being processed in the current turn.
    - original_question: The immutable question as initially submitted by the user.
    - retrieval_query: The actual search string used during the current retrieval attempt.
    - retrieved_context: List of retrieved chunk dictionaries containing text, metadata, and score.
    - sources: List of document IDs or filenames cited in the answer.
    - answer: The synthesized final answer or safe fallback text.
    - status: Workflow lifecycle status flag.
    - retrieval_attempts: Total count of retrieval passes executed for this question.
    - max_retries: Maximum allowable retry attempts (default 2 additional after initial).
    - context_sufficient: Boolean flag indicating if retrieved context meets the relevance criteria.
    - error_message: Optional error string if an exception occurred in any node.
    - conversation_history: Cumulative list of prior dialog turns across the session.
    - execution_trace: Ordered audit log of node transitions and routing decisions.
    """
    question: str
    original_question: str
    retrieval_query: str
    retrieved_context: List[Dict[str, Any]]
    sources: List[str]
    answer: str
    status: str
    retrieval_attempts: int
    max_retries: int
    context_sufficient: bool
    error_message: Optional[str]
    conversation_history: List[Dict[str, Any]]
    execution_trace: List[str]
