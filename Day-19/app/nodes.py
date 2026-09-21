"""
Workflow Node Functions for the Day 19 LangGraph Architecture.
"""

from typing import Dict, Any, List
from .config import WorkflowConfig
from .state import WorkflowState
from .retriever import LocalDocumentRetriever
from .utils import clean_text, extract_keywords

def initialize_state(state: WorkflowState) -> Dict[str, Any]:
    """
    Node 1: Validate input, preserve conversation history across turns, and initialize turn state.
    """
    raw_question = state.get("question", "")
    question = clean_text(raw_question)
    existing_history = list(state.get("conversation_history") or [])
    existing_trace = list(state.get("execution_trace") or [])

    # Validate input: reject empty, whitespace-only, or under minimum length
    if len(question) < WorkflowConfig.MIN_QUESTION_LENGTH:
        err_msg = WorkflowConfig.FALLBACK_EMPTY_INPUT
        trace_entry = f"initialize_state: REJECTED empty or too short input '{raw_question}'"
        return {
            "question": question,
            "original_question": raw_question,
            "retrieval_query": "",
            "retrieved_context": [],
            "sources": [],
            "answer": err_msg,
            "status": "validation_error",
            "retrieval_attempts": 0,
            "max_retries": state.get("max_retries", WorkflowConfig.MAX_RETRIES),
            "context_sufficient": False,
            "error_message": err_msg,
            "conversation_history": existing_history,
            "execution_trace": existing_trace + [trace_entry]
        }

    trace_entry = f"initialize_state: Accepted question='{question}' (existing_history_turns={len(existing_history)})"
    return {
        "question": question,
        "original_question": question,
        "retrieval_query": question,
        "retrieved_context": [],
        "sources": [],
        "answer": "",
        "status": "initialized",
        "retrieval_attempts": 0,
        "max_retries": state.get("max_retries", WorkflowConfig.MAX_RETRIES),
        "context_sufficient": False,
        "error_message": None,
        "conversation_history": existing_history,
        "execution_trace": existing_trace + [trace_entry]
    }

def retrieve_documents(state: WorkflowState) -> Dict[str, Any]:
    """
    Node 2: Retrieve relevant chunks using current retrieval_query and increment attempt counter.
    """
    query = state.get("retrieval_query") or state.get("question", "")
    attempts = state.get("retrieval_attempts", 0) + 1
    trace = list(state.get("execution_trace") or [])

    retriever = LocalDocumentRetriever.get_instance()

    try:
        results = retriever.retrieve(query=query, top_k=WorkflowConfig.DEFAULT_TOP_K)
        sources = list(dict.fromkeys([c["document_id"] for c in results]))
        trace.append(
            f"retrieve_documents: attempt={attempts}/{state.get('max_retries', 2) + 1}, "
            f"query='{query}', chunks_retrieved={len(results)}"
        )
        return {
            "retrieved_context": results,
            "sources": sources,
            "retrieval_attempts": attempts,
            "status": "retrieval_complete",
            "execution_trace": trace
        }
    except Exception as exc:
        trace.append(f"retrieve_documents: EXCEPTION caught during retrieval: {exc}")
        return {
            "retrieved_context": [],
            "sources": [],
            "retrieval_attempts": attempts,
            "status": "retrieval_error",
            "error_message": str(exc),
            "execution_trace": trace
        }

def validate_context(state: WorkflowState) -> Dict[str, Any]:
    """
    Node 3: Validate retrieved chunks using score threshold, chunk count, and substantive content.
    """
    retrieved = state.get("retrieved_context", [])
    threshold = WorkflowConfig.SIMILARITY_THRESHOLD
    trace = list(state.get("execution_trace") or [])

    has_chunks = len(retrieved) > 0
    scores = [c.get("score", 0.0) for c in retrieved]
    max_score = max(scores, default=0.0)
    has_sufficient_score = max_score >= threshold
    has_content = any(len(c.get("text", "").strip()) > 30 for c in retrieved)

    context_sufficient = has_chunks and has_sufficient_score and has_content

    if context_sufficient:
        status = "context_sufficient"
        trace.append(
            f"validate_context: SUFFICIENT (max_score={max_score:.4f} >= {threshold}, chunks={len(retrieved)})"
        )
    else:
        status = "context_insufficient"
        trace.append(
            f"validate_context: INSUFFICIENT (max_score={max_score:.4f} < {threshold}, chunks={len(retrieved)})"
        )

    return {
        "context_sufficient": context_sufficient,
        "status": status,
        "execution_trace": trace
    }

def refine_question_or_retrieve(state: WorkflowState) -> Dict[str, Any]:
    """
    Node 4: Refine query when context is insufficient and retries remain.
    Applies transparent stopword stripping and contextual topic expansion.
    """
    original = state.get("original_question") or state.get("question", "")
    current_query = state.get("retrieval_query", "")
    attempts = state.get("retrieval_attempts", 0)
    history = state.get("conversation_history", [])
    trace = list(state.get("execution_trace") or [])

    # Extract keywords from current and original query
    keywords = extract_keywords(current_query)
    if not keywords:
        keywords = extract_keywords(original)

    # Contextual expansion: if prior turn discussed onboarding, leave, training, or workflow
    context_prefix = []
    if history:
        last_turn = history[-1]
        last_q = last_turn.get("question", "").lower()
        if "onboard" in last_q and "onboard" not in keywords:
            context_prefix.append("onboarding")
        elif "leave" in last_q and "leave" not in keywords:
            context_prefix.append("leave policy")
        elif ("train" in last_q or "guideline" in last_q) and "training" not in keywords:
            context_prefix.append("training guidelines")
        elif ("workflow" in last_q or "sprint" in last_q) and "workflow" not in keywords:
            context_prefix.append("project workflow")

    refined_parts = context_prefix + keywords
    if refined_parts:
        refined_query = " ".join(refined_parts)
    else:
        refined_query = original.strip()

    # Avoid exact identical string loop if unchanged
    if refined_query == current_query and not context_prefix:
        refined_query = f"{refined_query} policy guidelines"

    trace.append(
        f"refine_question_or_retrieve: attempt={attempts}, previous='{current_query}', "
        f"refined='{refined_query}'"
    )

    return {
        "retrieval_query": refined_query,
        "status": "refining_query",
        "execution_trace": trace
    }

def generate_answer(state: WorkflowState) -> Dict[str, Any]:
    """
    Node 5: Deterministic grounded answer generation strictly using retrieved context.
    """
    query = state.get("question", "")
    retrieved = state.get("retrieved_context", [])
    sources = state.get("sources", [])
    trace = list(state.get("execution_trace") or [])

    try:
        # Synthesize answer from top chunks
        top_chunks = retrieved[:2]
        extracted_sections = []
        for c in top_chunks:
            extracted_sections.append(
                f"[{c.get('document_id', 'DOC')} | {c.get('filename', '')}]:\n{c.get('text', '').strip()}"
            )

        context_block = "\n\n".join(extracted_sections)
        
        answer_text = (
            f"Based on the sample documentation:\n\n"
            f"{context_block}\n\n"
            f"Sources Cited: {', '.join(sources)}"
        )

        trace.append(f"generate_answer: synthesized grounded answer from {len(top_chunks)} chunks ({len(sources)} sources)")
        return {
            "answer": answer_text,
            "status": "generation_complete",
            "execution_trace": trace
        }
    except Exception as exc:
        trace.append(f"generate_answer: EXCEPTION caught during answer generation: {exc}")
        return {
            "answer": WorkflowConfig.FALLBACK_GENERATION_ERROR,
            "status": "generation_error",
            "error_message": str(exc),
            "execution_trace": trace
        }

def handle_failure(state: WorkflowState) -> Dict[str, Any]:
    """
    Node 6: Handle validation, retrieval, generation, or out-of-domain failures safely.
    """
    status = state.get("status", "")
    trace = list(state.get("execution_trace") or [])
    err_msg = state.get("error_message")

    if status == "validation_error":
        answer = WorkflowConfig.FALLBACK_EMPTY_INPUT
        reason = "Invalid or empty question input"
    elif status == "retrieval_error":
        answer = WorkflowConfig.FALLBACK_RETRIEVAL_ERROR
        reason = f"Retriever exception ({err_msg})"
    elif status == "generation_error":
        answer = WorkflowConfig.FALLBACK_GENERATION_ERROR
        reason = f"Answer generator exception ({err_msg})"
    else:
        # Insufficient context after all retries exhausted
        answer = WorkflowConfig.FALLBACK_NO_CONTEXT
        reason = f"No relevant documentation found after {state.get('retrieval_attempts', 0)} retrieval attempts"

    trace.append(f"handle_failure: resolved with fallback answer (reason='{reason}')")
    return {
        "answer": answer,
        "status": "fallback_completed",
        "error_message": reason,
        "execution_trace": trace
    }

def update_memory(state: WorkflowState) -> Dict[str, Any]:
    """
    Node 7: Store current turn into conversation_history.
    """
    history = list(state.get("conversation_history") or [])
    trace = list(state.get("execution_trace") or [])
    
    question = state.get("original_question") or state.get("question", "")
    answer = state.get("answer", "")
    sources = state.get("sources", [])
    status = state.get("status", "")

    history.append({
        "turn_index": len(history) + 1,
        "question": question,
        "answer": answer,
        "sources": sources,
        "status": status
    })
    trace.append(f"update_memory: recorded turn {len(history)} into conversation_history")

    return {
        "conversation_history": history,
        "execution_trace": trace
    }

def finalize(state: WorkflowState) -> Dict[str, Any]:
    """
    Node 8: Finalize state, ensure clean output structure, and close execution trace.
    """
    trace = list(state.get("execution_trace") or [])
    status = state.get("status", "completed")
    
    final_status = "completed" if status in ("generation_complete", "completed") else "fallback_completed"
    trace.append(f"finalize: workflow completed with final_status='{final_status}'")

    return {
        "status": final_status,
        "execution_trace": trace
    }
