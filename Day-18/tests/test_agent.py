"""
Day 18 — Automated Test Suite
Verifies DocumentResearchAgent, Planner, ToolRegistry, Memory, and ReAct loop.
Covers 17 comprehensive test cases to ensure complete functionality and grounding.
"""

import pytest
from agent.schemas import AgentState, AgentResponse, ExecutionPlan, ToolResult
from agent.memory import AgentMemory
from agent.planner import Planner
from agent.tools import (
    KnowledgeBaseLoader,
    ToolRegistry,
    document_search,
    document_lookup,
    document_metadata,
    final_response
)
from agent.agent import DocumentResearchAgent


# ------------------------------------------------------------------------------
# 1. INITIALIZATION TESTS
# ------------------------------------------------------------------------------
def test_agent_initialization():
    """Verify agent starts in INITIALIZED state with fresh memory and no tools."""
    agent = DocumentResearchAgent()
    assert agent.state == AgentState.INITIALIZED
    assert len(agent.memory.trace) == 0
    assert len(agent.memory.retrieved_contexts) == 0
    assert len(agent.tools_used) == 0


def test_agent_memory_reset():
    """Verify memory reset wipes all traces, contexts, and sources cleanly."""
    memory = AgentMemory()
    memory.add_trace("PLAN", "Initial planning")
    memory.add_context("Sample context paragraph", "Sample Document")
    assert len(memory.trace) == 1
    assert len(memory.retrieved_contexts) == 1
    assert len(memory.get_source_titles()) == 1

    memory.reset()
    assert len(memory.trace) == 0
    assert len(memory.retrieved_contexts) == 0
    assert len(memory.get_source_titles()) == 0


# ------------------------------------------------------------------------------
# 2. PLANNER & INTENT CLASSIFICATION TESTS
# ------------------------------------------------------------------------------
def test_planner_search_intent():
    """Verify standard operational query classifies as document_search."""
    intent = Planner.identify_intent("What is the leave policy for interns?")
    assert intent == "document_search"


def test_planner_lookup_intent():
    """Verify query with explicit document ID classifies as document_lookup."""
    intent = Planner.identify_intent("Look up DOC-WORKFLOW-004 in detail")
    assert intent == "document_lookup"


def test_planner_metadata_intent():
    """Verify query asking for author or version classifies as document_metadata."""
    intent = Planner.identify_intent("Who is the author and version of DOC-ONBOARD-002?")
    assert intent == "document_metadata"


def test_planner_out_of_domain_intent():
    """Verify out-of-scope query classifies as unsupported_domain."""
    intent1 = Planner.identify_intent("What is the company stock price?")
    assert intent1 == "unsupported_domain"

    intent2 = Planner.identify_intent("What is the current bitcoin price?")
    assert intent2 == "unsupported_domain"


def test_planner_step_generation():
    """Verify Planner constructs ordered, non-empty plan steps."""
    plan = Planner.create_plan("What is the probation period?")
    assert isinstance(plan, ExecutionPlan)
    assert plan.intent == "document_search"
    assert len(plan.steps) == 5
    assert plan.steps[0].target_tool == "analysis"
    assert plan.steps[1].target_tool == "document_search"
    assert plan.steps[-1].target_tool == "final_response"


# ------------------------------------------------------------------------------
# 3. TOOL EXECUTION & DISPATCH TESTS
# ------------------------------------------------------------------------------
def test_tool_registry_valid_dispatch():
    """Verify ToolRegistry dispatches valid tools successfully."""
    result = ToolRegistry.execute("document_lookup", {"document_id": "DOC-LEAVE-001"})
    assert isinstance(result, ToolResult)
    assert result.success is True
    assert result.tool_name == "document_lookup"
    assert "Attendance, Leave" in result.data["title"]


def test_tool_registry_unknown_tool():
    """Verify ToolRegistry isolates unknown tool invocations safely."""
    result = ToolRegistry.execute("non_existent_tool", {})
    assert isinstance(result, ToolResult)
    assert result.success is False
    assert "Unknown tool" in result.error_message


def test_document_search_execution():
    """Verify document_search returns ranked search results with positive score."""
    results = document_search("leave policy", top_k=3)
    assert len(results) > 0
    assert results[0].relevance_score >= 0.25
    assert results[0].document_id == "DOC-LEAVE-001"


def test_document_lookup_execution():
    """Verify document_lookup retrieves full document structure by ID."""
    doc = document_lookup("DOC-WORKFLOW-004")
    assert doc is not None
    assert doc["document_id"] == "DOC-WORKFLOW-004"
    assert "5-Stage Machine Learning Project Lifecycle" in doc["content"]


def test_document_lookup_invalid_id():
    """Verify document_lookup returns None for non-existent document ID."""
    doc = document_lookup("DOC-NONEXISTENT-999")
    assert doc is None


def test_document_metadata_execution():
    """Verify document_metadata returns catalog metadata attributes."""
    meta = document_metadata("DOC-ONBOARD-002")
    assert meta is not None
    assert meta["document_id"] == "DOC-ONBOARD-002"
    assert "Developer Experience" in meta["author"] or "Linkific" in meta["author"]
    assert meta["char_count"] > 100
    assert meta["chunk_count"] > 0


# ------------------------------------------------------------------------------
# 4. FULL AGENT REAC WORKFLOW TESTS (END-TO-END)
# ------------------------------------------------------------------------------
def test_agent_leave_policy_grounded():
    """Verify full agent execution for Leave Policy query (UC-1)."""
    agent = DocumentResearchAgent()
    response = agent.run("What is the leave policy?")

    assert response.status == "answered"
    assert len(response.sources) > 0
    assert "Attendance, Leave, and Working Schedule Policy" in response.sources
    assert "Planned Leave Request Procedure" in response.answer or "leave" in response.answer.lower()
    assert "document_search" in response.tools_used
    assert "final_response" in response.tools_used


def test_agent_training_requirements_grounded():
    """Verify full agent execution for Training Requirements query (UC-2)."""
    agent = DocumentResearchAgent()
    response = agent.run("What are the training requirements?")

    assert response.status == "answered"
    assert len(response.sources) > 0
    assert any("Training Curriculum" in s for s in response.sources)
    assert "Curriculum Track Structure" in response.answer or "training" in response.answer.lower()


def test_agent_out_of_domain_refusal():
    """Verify safe controlled refusal for out-of-domain query (UC-5)."""
    agent = DocumentResearchAgent()
    response = agent.run("What is the company's stock price?")

    assert response.status == "no_relevant_information"
    assert len(response.sources) == 0
    assert "financial, stock market" in response.answer
    assert "final_response" in response.tools_used


def test_agent_empty_query_handling():
    """Verify agent gracefully handles empty or whitespace string."""
    agent = DocumentResearchAgent()
    response = agent.run("   ")

    assert response.status == "no_relevant_information"
    assert len(response.sources) == 0
    assert "valid question" in response.answer.lower()


def test_agent_react_trace_completeness():
    """Verify execution trace captures all ReAct states: PLAN, ACT, OBSERVE, DECIDE, FINAL."""
    agent = DocumentResearchAgent()
    response = agent.run("What is the leave policy?")

    trace_states = [s["state"] for s in response.execution_trace]
    assert "PLAN" in trace_states
    assert "ACT" in trace_states
    assert "OBSERVE" in trace_states
    assert "DECIDE" in trace_states
    assert "FINAL" in trace_states
