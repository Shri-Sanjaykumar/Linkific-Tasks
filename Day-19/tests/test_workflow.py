"""
Automated PyTest Suite for Day 19 LangGraph Stateful Workflow.
Contains 31 tests across 9 categories:
1. Graph creation and compilation (3 tests)
2. State initialization and schema (3 tests)
3. Retrieval and metadata (4 tests)
4. Conditional routing and loop bounds (4 tests)
5. Answer generation and fallback (3 tests)
6. Input validation (3 tests)
7. Memory persistence and thread isolation (4 tests)
8. Regression and termination (3 tests)
"""

import sys
import os
import pytest

# Ensure Day-19 root is in sys.path
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(TEST_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.config import WorkflowConfig
from app.state import WorkflowState
from app.retriever import LocalDocumentRetriever
from app.nodes import (
    initialize_state,
    retrieve_documents,
    validate_context,
    refine_question_or_retrieve,
    generate_answer,
    handle_failure,
    update_memory,
    finalize,
)
from app.workflow import (
    create_workflow,
    compile_workflow,
    route_after_init,
    route_after_retrieval,
    route_after_validation,
    route_after_generation,
)
from app.memory import get_in_memory_checkpointer, get_thread_config, InMemorySaver

# ==============================================================================
# CATEGORY 1: Graph Creation and Compilation (3 Tests)
# ==============================================================================

def test_01_graph_creation():
    """Verify that create_workflow constructs a valid StateGraph instance."""
    builder = create_workflow()
    assert builder is not None
    # Check that all 8 nodes are registered in the builder
    expected_nodes = {
        "initialize_state",
        "retrieve_documents",
        "validate_context",
        "refine_question_or_retrieve",
        "generate_answer",
        "handle_failure",
        "update_memory",
        "finalize",
    }
    assert expected_nodes.issubset(set(builder.nodes.keys()))

def test_02_graph_compilation_without_checkpointer():
    """Verify that compile_workflow successfully compiles a runnable graph without checkpointer."""
    graph = compile_workflow(checkpointer=None)
    assert graph is not None
    assert hasattr(graph, "invoke")

def test_03_graph_compilation_with_checkpointer():
    """Verify that compile_workflow compiles with an InMemorySaver checkpointer."""
    cp = InMemorySaver()
    graph = compile_workflow(checkpointer=cp)
    assert graph is not None
    assert hasattr(graph, "invoke")

# ==============================================================================
# CATEGORY 2: State Initialization and Schema (3 Tests)
# ==============================================================================

def test_04_state_initialization_valid_input():
    """Verify initialize_state accepts a valid question and initializes state fields."""
    state_in: WorkflowState = {"question": "What is the leave policy?"}
    state_out = initialize_state(state_in)
    assert state_out["status"] == "initialized"
    assert state_out["question"] == "What is the leave policy?"
    assert state_out["retrieval_attempts"] == 0
    assert state_out["context_sufficient"] is False
    assert state_out["error_message"] is None

def test_05_state_schema_keys():
    """Verify initialize_state returns all required schema keys."""
    state_in: WorkflowState = {"question": "How do sprints work?"}
    state_out = initialize_state(state_in)
    required_keys = [
        "question", "original_question", "retrieval_query", "retrieved_context",
        "sources", "answer", "status", "retrieval_attempts", "max_retries",
        "context_sufficient", "error_message", "conversation_history", "execution_trace"
    ]
    for key in required_keys:
        assert key in state_out, f"Missing required state key: {key}"

def test_06_execution_trace_creation():
    """Verify that initialize_state starts the execution trace log."""
    state_in: WorkflowState = {"question": "What are the onboarding steps?"}
    state_out = initialize_state(state_in)
    trace = state_out.get("execution_trace", [])
    assert len(trace) >= 1
    assert "initialize_state: Accepted question" in trace[0]

# ==============================================================================
# CATEGORY 3: Retrieval and Metadata (4 Tests)
# ==============================================================================

def test_07_relevant_document_retrieval():
    """Verify retrieval returns relevant chunks for an in-domain question."""
    retriever = LocalDocumentRetriever.get_instance()
    results = retriever.retrieve("onboarding process steps", top_k=3)
    assert len(results) > 0
    top_chunk = results[0]
    assert top_chunk["document_id"] == "DOC-ONBOARD-001"
    assert top_chunk["score"] >= WorkflowConfig.SIMILARITY_THRESHOLD

def test_08_no_relevant_document_retrieval():
    """Verify out-of-domain queries produce scores below the relevance threshold."""
    retriever = LocalDocumentRetriever.get_instance()
    results = retriever.retrieve("quantum astrophysics warp drive mechanics", top_k=3)
    # The max score for completely alien topics should be below threshold
    if results:
        max_score = max(c["score"] for c in results)
        assert max_score < WorkflowConfig.SIMILARITY_THRESHOLD

def test_09_retrieval_metadata_preservation():
    """Verify every retrieved chunk preserves required metadata attributes."""
    retriever = LocalDocumentRetriever.get_instance()
    results = retriever.retrieve("training attendance quiz passing", top_k=2)
    assert len(results) > 0
    for chunk in results:
        assert "document_id" in chunk
        assert "filename" in chunk
        assert "category" in chunk
        assert "source" in chunk
        assert chunk["source"] == "synthetic"
        assert "chunk_id" in chunk
        assert "score" in chunk
        assert isinstance(chunk["score"], float)

def test_10_retrieval_exception_handling():
    """Verify retrieve_documents catches exceptions and sets status='retrieval_error'."""
    retriever = LocalDocumentRetriever.get_instance()
    retriever.set_simulate_error(True)
    try:
        state_in: WorkflowState = {
            "question": "How to apply for casual leave?",
            "retrieval_query": "How to apply for casual leave?",
            "retrieval_attempts": 0,
            "max_retries": 2,
            "execution_trace": []
        }
        state_out = retrieve_documents(state_in)
        assert state_out["status"] == "retrieval_error"
        assert state_out["error_message"] is not None
        assert "Simulated retriever connection failure" in state_out["error_message"]
        assert state_out["retrieval_attempts"] == 1
    finally:
        retriever.set_simulate_error(False)

# ==============================================================================
# CATEGORY 4: Conditional Routing and Loop Bounds (4 Tests)
# ==============================================================================

def test_11_route_after_init():
    """Verify route_after_init routes to retrieve_documents for valid and handle_failure for error."""
    valid_state: WorkflowState = {"status": "initialized"}
    assert route_after_init(valid_state) == "retrieve_documents"

    invalid_state: WorkflowState = {"status": "validation_error"}
    assert route_after_init(invalid_state) == "handle_failure"

def test_12_route_after_retrieval():
    """Verify route_after_retrieval routes to validate_context or handle_failure on error."""
    success_state: WorkflowState = {"status": "retrieval_complete"}
    assert route_after_retrieval(success_state) == "validate_context"

    error_state: WorkflowState = {"status": "retrieval_error"}
    assert route_after_retrieval(error_state) == "handle_failure"

def test_13_route_after_validation():
    """Verify route_after_validation respects context sufficiency and retry limits."""
    # 1. Sufficient context -> generate_answer
    suff_state: WorkflowState = {"context_sufficient": True}
    assert route_after_validation(suff_state) == "generate_answer"

    # 2. Insufficient + attempts <= max_retries -> refine_question_or_retrieve
    retry_state: WorkflowState = {
        "context_sufficient": False,
        "retrieval_attempts": 1,
        "max_retries": 2
    }
    assert route_after_validation(retry_state) == "refine_question_or_retrieve"

    # 3. Insufficient + attempts > max_retries (exhausted) -> handle_failure
    exhausted_state: WorkflowState = {
        "context_sufficient": False,
        "retrieval_attempts": 3,
        "max_retries": 2
    }
    assert route_after_validation(exhausted_state) == "handle_failure"

def test_14_retry_loop_bounded_execution():
    """Verify an unanswerable query loops up to max_retries and terminates at fallback."""
    graph = compile_workflow()
    result = graph.invoke({"question": "What is the atmospheric pressure on Neptune?"})
    # Must terminate with fallback_completed
    assert result["status"] == "fallback_completed"
    assert result["context_sufficient"] is False
    # Max total attempts is 1 initial + 2 retries = 3
    assert result["retrieval_attempts"] <= 3
    assert result["retrieval_attempts"] >= 2
    assert WorkflowConfig.FALLBACK_NO_CONTEXT in result["answer"]

# ==============================================================================
# CATEGORY 5: Answer Generation and Fallback (3 Tests)
# ==============================================================================

def test_15_answer_generation_with_context():
    """Verify generate_answer synthesizes answer with cited document IDs."""
    retriever = LocalDocumentRetriever.get_instance()
    chunks = retriever.retrieve("annual earned leave accrual rules", top_k=2)
    state_in: WorkflowState = {
        "question": "How does annual leave accrue?",
        "retrieved_context": chunks,
        "sources": ["DOC-LEAVE-002"],
        "execution_trace": []
    }
    state_out = generate_answer(state_in)
    assert state_out["status"] == "generation_complete"
    assert "Based on the sample documentation:" in state_out["answer"]
    assert "DOC-LEAVE-002" in state_out["answer"]

def test_16_no_context_fallback_response():
    """Verify handle_failure returns the user-friendly fallback text."""
    state_in: WorkflowState = {
        "status": "context_insufficient",
        "retrieval_attempts": 3,
        "error_message": "Exhausted retries",
        "execution_trace": []
    }
    state_out = handle_failure(state_in)
    assert state_out["status"] == "fallback_completed"
    assert WorkflowConfig.FALLBACK_NO_CONTEXT in state_out["answer"]

def test_17_generation_exception_handling():
    """Verify route_after_generation routes to handle_failure if generation fails."""
    err_state: WorkflowState = {"status": "generation_error"}
    assert route_after_generation(err_state) == "handle_failure"

# ==============================================================================
# CATEGORY 6: Input Validation (3 Tests)
# ==============================================================================

def test_18_empty_question_rejection():
    """Verify empty string question is rejected during state initialization."""
    state_in: WorkflowState = {"question": ""}
    state_out = initialize_state(state_in)
    assert state_out["status"] == "validation_error"
    assert state_out["error_message"] == WorkflowConfig.FALLBACK_EMPTY_INPUT
    assert state_out["answer"] == WorkflowConfig.FALLBACK_EMPTY_INPUT

def test_19_whitespace_question_rejection():
    """Verify whitespace-only question is rejected during state initialization."""
    state_in: WorkflowState = {"question": "    \t  \n  "}
    state_out = initialize_state(state_in)
    assert state_out["status"] == "validation_error"
    assert state_out["error_message"] == WorkflowConfig.FALLBACK_EMPTY_INPUT

def test_20_short_question_rejection():
    """Verify question below minimum length threshold is rejected."""
    state_in: WorkflowState = {"question": "ab"}
    state_out = initialize_state(state_in)
    assert state_out["status"] == "validation_error"
    assert state_out["error_message"] == WorkflowConfig.FALLBACK_EMPTY_INPUT

# ==============================================================================
# CATEGORY 7: Memory Persistence and Thread Isolation (4 Tests)
# ==============================================================================

def test_21_memory_enabled_with_thread_id():
    """Verify graph executes with a checkpointer and thread_id configuration."""
    cp = InMemorySaver()
    graph = compile_workflow(checkpointer=cp)
    cfg = get_thread_config("test-thread-mem-21")
    result = graph.invoke({"question": "What are the onboarding steps?"}, config=cfg)
    assert result["status"] == "completed"
    assert len(result.get("conversation_history", [])) == 1

def test_22_conversation_history_update():
    """Verify turn record schema inside conversation_history."""
    state_in: WorkflowState = {
        "original_question": "What is the leave policy?",
        "question": "What is the leave policy?",
        "answer": "Here is the policy...",
        "sources": ["DOC-LEAVE-002"],
        "status": "generation_complete",
        "conversation_history": [],
        "execution_trace": []
    }
    state_out = update_memory(state_in)
    history = state_out["conversation_history"]
    assert len(history) == 1
    turn = history[0]
    assert turn["turn_index"] == 1
    assert turn["question"] == "What is the leave policy?"
    assert turn["answer"] == "Here is the policy..."
    assert turn["sources"] == ["DOC-LEAVE-002"]

def test_23_multiple_turns_same_thread():
    """Verify multi-turn history accumulation across two invocations with same thread_id."""
    cp = InMemorySaver()
    graph = compile_workflow(checkpointer=cp)
    cfg = get_thread_config("test-thread-multi-turn-23")

    res1 = graph.invoke({"question": "What are the steps in the onboarding process?"}, config=cfg)
    assert len(res1.get("conversation_history", [])) == 1

    res2 = graph.invoke({"question": "What should I complete first?"}, config=cfg)
    assert len(res2.get("conversation_history", [])) == 2
    assert res2["conversation_history"][0]["turn_index"] == 1
    assert res2["conversation_history"][1]["turn_index"] == 2

def test_24_thread_isolation():
    """Verify two different thread_ids maintain completely isolated conversation histories."""
    cp = InMemorySaver()
    graph = compile_workflow(checkpointer=cp)

    cfg_a = get_thread_config("thread-isolation-alpha")
    cfg_b = get_thread_config("thread-isolation-beta")

    res_a = graph.invoke({"question": "What are the onboarding steps?"}, config=cfg_a)
    assert len(res_a.get("conversation_history", [])) == 1

    # Thread B should start completely clean with 1 entry after its own first turn
    res_b = graph.invoke({"question": "What is the leave policy?"}, config=cfg_b)
    assert len(res_b.get("conversation_history", [])) == 1
    assert res_b["conversation_history"][0]["question"] == "What is the leave policy?"

# ==============================================================================
# CATEGORY 8: Regression and Termination (3 Tests)
# ==============================================================================

def test_25_successful_workflow_terminates():
    """Verify a valid question runs full graph and terminates at completed state."""
    graph = compile_workflow()
    result = graph.invoke({"question": "What are the engineering sprint planning hours?"})
    assert result["status"] == "completed"
    assert result["context_sufficient"] is True
    assert len(result["sources"]) > 0
    assert "DOC-WORKFLOW-004" in result["sources"]

def test_26_retry_loop_terminates_safely():
    """Verify retry loop does not hang and terminates within bounded step limit."""
    graph = compile_workflow()
    result = graph.invoke({"question": "How to bake a chocolate cake at home?"})
    assert result["status"] == "fallback_completed"
    assert result["retrieval_attempts"] <= 3

def test_27_final_response_expected_structure():
    """Verify final workflow return dictionary adheres to complete expected contract."""
    graph = compile_workflow()
    result = graph.invoke({"question": "What is the passing threshold for intern quizzes?"})
    expected_fields = [
        "question", "original_question", "retrieval_query", "retrieved_context",
        "sources", "answer", "status", "retrieval_attempts", "max_retries",
        "context_sufficient", "error_message", "conversation_history", "execution_trace"
    ]
    for field in expected_fields:
        assert field in result, f"Field '{field}' missing from final graph result"
    assert result["status"] == "completed"
    assert "75%" in result["answer"] or "seventy-five percent" in result["answer"].lower()

# ==============================================================================
# CATEGORY 9: Interactive Session Handling & Memory (4 Tests)
# ==============================================================================

from run_workflow import run_interactive_session

def test_28_interactive_exit_commands():
    """Verify that 'exit', 'quit', and 'q' safely stop the interactive loop without errors."""
    for cmd in ["exit", "QUIT", "  q  "]:
        output_buffer = []
        inputs = iter([cmd])
        run_interactive_session(
            thread_id="test-exit-thread",
            input_fn=lambda _: next(inputs),
            output_fn=lambda msg: output_buffer.append(msg)
        )
        combined = "\n".join(output_buffer)
        assert "[Session Ended] Interactive Q&A session closed. Goodbye!" in combined

def test_29_interactive_blank_input_handling():
    """Verify that blank or whitespace input prompts the user without calling the graph."""
    output_buffer = []
    # User types whitespace, then blank, then 'q' to exit
    inputs = iter(["   ", "", "q"])
    run_interactive_session(
        thread_id="test-blank-thread",
        input_fn=lambda _: next(inputs),
        output_fn=lambda msg: output_buffer.append(msg)
    )
    combined = "\n".join(output_buffer)
    assert "[Notice] Question cannot be blank." in combined
    assert "[Session Ended] Interactive Q&A session closed. Goodbye!" in combined

def test_30_interactive_multiple_questions_memory():
    """Verify interactive session accumulates multi-turn conversation memory across queries."""
    output_buffer = []
    cp = InMemorySaver()
    thread_id = "test-interactive-multi-q"

    # User asks question 1, then follow-up question 2, then exits
    inputs = iter([
        "What are the steps in the onboarding process?",
        "What should I complete first?",
        "exit"
    ])

    run_interactive_session(
        thread_id=thread_id,
        checkpointer=cp,
        input_fn=lambda _: next(inputs),
        output_fn=lambda msg: output_buffer.append(msg)
    )

    combined = "\n".join(output_buffer)
    assert "History: 1 turns" in combined
    assert "History: 2 turns" in combined
    assert "[Session Ended] Interactive Q&A session closed. Goodbye!" in combined

def test_31_interactive_safe_termination_on_interrupt():
    """Verify EOFError or KeyboardInterrupt terminates gracefully without crashing."""
    def raise_interrupt(_):
        raise KeyboardInterrupt()

    output_buffer = []
    run_interactive_session(
        thread_id="test-interrupt-thread",
        input_fn=raise_interrupt,
        output_fn=lambda msg: output_buffer.append(msg)
    )
    combined = "\n".join(output_buffer)
    assert "[Session Interrupted] Closing interactive Q&A session. Goodbye!" in combined
