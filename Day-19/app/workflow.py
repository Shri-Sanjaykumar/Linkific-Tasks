"""
LangGraph StateGraph Definition and Compilation for Day 19.
"""

from typing import Optional
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

from .config import WorkflowConfig
from .state import WorkflowState
from .nodes import (
    initialize_state,
    retrieve_documents,
    validate_context,
    refine_question_or_retrieve,
    generate_answer,
    handle_failure,
    update_memory,
    finalize,
)

def route_after_init(state: WorkflowState) -> str:
    """
    Route after input validation:
    - If validation failed (empty/too short): route to handle_failure
    - If valid: route to retrieve_documents
    """
    if state.get("status") == "validation_error":
        return "handle_failure"
    return "retrieve_documents"

def route_after_retrieval(state: WorkflowState) -> str:
    """
    Route after retrieval execution:
    - If retriever raised an exception: route to handle_failure
    - If retrieval completed normally: route to validate_context
    """
    if state.get("status") == "retrieval_error":
        return "handle_failure"
    return "validate_context"

def route_after_validation(state: WorkflowState) -> str:
    """
    Route after context validation:
    - If context is sufficient: route to generate_answer
    - If context is insufficient and retries remaining: route to refine_question_or_retrieve
    - If context is insufficient and retry limit reached: route to handle_failure
    """
    if state.get("context_sufficient", False) is True:
        return "generate_answer"

    attempts = state.get("retrieval_attempts", 0)
    max_retries = state.get("max_retries", WorkflowConfig.MAX_RETRIES)
    # max_retries is additional retries after initial retrieval.
    # Initial attempt = 1, Retry 1 = 2, Retry 2 = 3.
    # If attempts <= max_retries, further retries are permitted.
    if attempts <= max_retries:
        return "refine_question_or_retrieve"
    return "handle_failure"

def route_after_generation(state: WorkflowState) -> str:
    """
    Route after answer synthesis:
    - If generator raised an exception: route to handle_failure
    - If generation completed: route to update_memory
    """
    if state.get("status") == "generation_error":
        return "handle_failure"
    return "update_memory"

def create_workflow() -> StateGraph:
    """
    Construct the full LangGraph StateGraph with nodes, edges, and conditional routing.
    """
    builder = StateGraph(WorkflowState)

    # Register all 8 workflow nodes
    builder.add_node("initialize_state", initialize_state)
    builder.add_node("retrieve_documents", retrieve_documents)
    builder.add_node("validate_context", validate_context)
    builder.add_node("refine_question_or_retrieve", refine_question_or_retrieve)
    builder.add_node("generate_answer", generate_answer)
    builder.add_node("handle_failure", handle_failure)
    builder.add_node("update_memory", update_memory)
    builder.add_node("finalize", finalize)

    # 1. Start transition
    builder.add_edge(START, "initialize_state")

    # 2. Decision after initialize_state (Valid Input?)
    builder.add_conditional_edges(
        "initialize_state",
        route_after_init,
        {
            "retrieve_documents": "retrieve_documents",
            "handle_failure": "handle_failure",
        }
    )

    # 3. Decision after retrieve_documents (Retrieval Error?)
    builder.add_conditional_edges(
        "retrieve_documents",
        route_after_retrieval,
        {
            "validate_context": "validate_context",
            "handle_failure": "handle_failure",
        }
    )

    # 4. Decision after validate_context (Context Sufficient?)
    builder.add_conditional_edges(
        "validate_context",
        route_after_validation,
        {
            "generate_answer": "generate_answer",
            "refine_question_or_retrieve": "refine_question_or_retrieve",
            "handle_failure": "handle_failure",
        }
    )

    # 5. Retry loop: refine_question_or_retrieve cycles back to retrieve_documents
    builder.add_edge("refine_question_or_retrieve", "retrieve_documents")

    # 6. Decision after generate_answer (Generation Error?)
    builder.add_conditional_edges(
        "generate_answer",
        route_after_generation,
        {
            "update_memory": "update_memory",
            "handle_failure": "handle_failure",
        }
    )

    # 7. Failure convergence
    builder.add_edge("handle_failure", "update_memory")

    # 8. Memory update to finalize
    builder.add_edge("update_memory", "finalize")

    # 9. Finalize to END
    builder.add_edge("finalize", END)

    return builder

def compile_workflow(checkpointer: Optional[InMemorySaver] = None):
    """
    Compile the StateGraph into a runnable graph, optionally binding an InMemorySaver checkpointer.
    """
    builder = create_workflow()
    if checkpointer is not None:
        return builder.compile(checkpointer=checkpointer)
    return builder.compile()
