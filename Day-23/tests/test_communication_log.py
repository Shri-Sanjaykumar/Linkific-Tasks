"""Tests specifically verifying the Multi-Agent Communication Log and information flow."""

import json
from pathlib import Path
from app.graph import build_multi_agent_graph
from app.state import create_initial_state
from app.schemas import MessageType, AgentRole


def test_communication_log_completeness_and_order(sample_query):
    graph = build_multi_agent_graph()
    workflow_id = "WF-COMM-001"
    initial_state = create_initial_state(
        query=sample_query,
        workflow_id=workflow_id,
        mode="streamlined",
    )
    final_state = graph.invoke(initial_state)

    log = final_state["communication_log"]
    assert len(log) == 5

    # 1. User -> Coordinator (User Request)
    assert log[0].sender == AgentRole.USER
    assert log[0].recipient == AgentRole.COORDINATOR
    assert log[0].message_type == MessageType.USER_REQUEST
    assert log[0].correlation_id == workflow_id
    assert "query" in log[0].payload

    # 2. Coordinator -> Researcher (Task Assignment)
    assert log[1].sender == AgentRole.COORDINATOR
    assert log[1].recipient == AgentRole.RESEARCHER
    assert log[1].message_type == MessageType.TASK_ASSIGNMENT
    assert log[1].correlation_id == workflow_id

    # 3. Researcher -> Writer (Research Submission)
    assert log[2].sender == AgentRole.RESEARCHER
    assert log[2].recipient == AgentRole.WRITER
    assert log[2].message_type == MessageType.RESEARCH_SUBMISSION
    assert log[2].correlation_id == workflow_id
    assert "evidence_count" in log[2].payload

    # 4. Writer -> Coordinator (Report Draft)
    assert log[3].sender == AgentRole.WRITER
    assert log[3].recipient == AgentRole.COORDINATOR
    assert log[3].message_type == MessageType.REPORT_DRAFT
    assert log[3].correlation_id == workflow_id
    assert "report_id" in log[3].payload

    # 5. Coordinator -> User (Final Answer)
    assert log[4].sender == AgentRole.COORDINATOR
    assert log[4].recipient == AgentRole.USER
    assert log[4].message_type == MessageType.FINAL_ANSWER
    assert log[4].correlation_id == workflow_id
    assert "final_answer" in log[4].payload


def test_communication_log_correlation_id_continuity(sample_query):
    graph = build_multi_agent_graph()
    workflow_id = "WF-CORR-CHECK-999"
    initial_state = create_initial_state(
        query=sample_query,
        workflow_id=workflow_id,
        mode="comprehensive",
    )
    final_state = graph.invoke(initial_state)

    log = final_state["communication_log"]
    for msg in log:
        assert msg.correlation_id == workflow_id
        assert msg.timestamp is not None
        assert msg.message_id.startswith("MSG-")
        assert len(msg.summary) > 0


def test_communication_log_json_serialization(sample_query, tmp_path):
    graph = build_multi_agent_graph()
    initial_state = create_initial_state(
        query=sample_query,
        workflow_id="WF-JSON-TEST",
        mode="streamlined",
    )
    final_state = graph.invoke(initial_state)

    log = final_state["communication_log"]
    serialized = [msg.model_dump(mode="json") for msg in log]

    out_file = tmp_path / "comm_log_test.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(serialized, f, indent=2)

    assert out_file.exists()
    assert out_file.stat().st_size > 0

    with open(out_file, "r", encoding="utf-8") as f:
        reloaded = json.load(f)

    assert len(reloaded) == 5
    assert reloaded[0]["sender"] == "user"
    assert reloaded[-1]["recipient"] == "user"
