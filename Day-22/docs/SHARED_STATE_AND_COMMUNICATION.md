# Day 22: Shared State & Inter-Agent Communication Specification

This specification provides a deep-dive reference for the **Centralized Shared State Architecture** and the **Typed Message Passing Protocol** powering the Linkific Multi-Agent System.

---

## 1. Centralized Shared State Architecture

### 1.1 Field Ownership & Access Control Matrix

To prevent uncontrolled mutations and distributed state drift, every field in `SharedState` has a single authoritative owner agent. Attempts by unauthorized agents to mutate a field raise `StatePermissionError`.

| Field Name | Type | Authoritative Owner | Read Permissions | Mutation Method |
| :--- | :--- | :--- | :--- | :--- |
| `workflow_id` | `str (UUID)` | System / Engine | All Agents | Initializer only |
| `user_query` | `str` | System / Engine | All Agents | Initializer only |
| `current_status` | `WorkflowStatus` | `CoordinatorAgent` | All Agents | `update_workflow_status()` |
| `execution_plan` | `ExecutionPlan` | `CoordinatorAgent` | All Agents | `set_execution_plan()` |
| `agent_statuses` | `Dict[AgentRole, str]` | `CoordinatorAgent` & Self | All Agents | `update_agent_status()` |
| `revision_count` | `int` | `CoordinatorAgent` | All Agents | `increment_revision_count()` |
| `research_findings` | `ResearchFindings` | `ResearchAgent` | All Agents | `set_research_findings()` |
| `analysis_result` | `AnalysisResult` | `AnalyzerAgent` | All Agents | `set_analysis_result()` |
| `critic_reviews` | `List[CriticReview]` | `CriticAgent` | All Agents | `add_critic_review()` |
| `final_report` | `WriterReport` | `WriterAgent` | All Agents | `set_final_report()` |
| `message_history` | `List[AgentMessage]` | `MessageBus` | All Agents | `record_message()` |
| `transition_history` | `List[StateTransitionRecord]` | `SharedStateManager` | All Agents | `_record_transition()` |

### 1.2 Concurrency & Thread-Safety Guarantees
- Mutations are protected by a re-entrant lock (`threading.RLock`).
- Read operations invoke `state_manager.get_snapshot()`, which produces an isolated deep copy of `SharedState`.
- Agents can read state snapshots without holding locks or blocking concurrent pipeline workers.

### 1.3 State Mutation Audit Trail
Every change to `SharedState` produces an immutable `StateTransitionRecord`:
```json
{
  "transition_id": "a24317f2-085e-49b8-bc71-f9f38f4277b0",
  "timestamp": "2026-09-24T12:00:00.123456+00:00",
  "actor": "critic_agent",
  "field_modified": "critic_reviews",
  "previous_state": null,
  "new_state": "Verdict: approved, Score: 0.95",
  "reason": "Quality verification passed with score 0.95 (100.0% citation coverage)."
}
```

---

## 2. Inter-Agent Communication Protocol

### 2.1 Standard Message Envelope (`AgentMessage`)
All agents communicate via the in-process `MessageBus` using the typed `AgentMessage` envelope:

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message_id` | `str (UUID)` | Yes | Globally unique message identifier |
| `workflow_id` | `str` | Yes | Parent workflow correlation identifier |
| `task_id` | `str` | Yes | Current task milestone e.g. `TASK-RES-002` |
| `sender` | `AgentRole` | Yes | Emitting agent role |
| `receiver` | `AgentRole` | Yes | Target agent role |
| `message_type` | `MessageType` | Yes | Semantic message category |
| `status` | `MessageStatus` | Yes | `sent` -> `delivered` -> `processed` -> `failed` |
| `payload` | `Dict[str, Any]` | Yes | Structured typed payload |
| `evidence_ids` | `List[str]` | Optional | Referent document identifiers |
| `errors` | `List[str]` | Optional | Error strings if processing failed |
| `timestamp` | `str (ISO-8601)` | Yes | Transmission timestamp in UTC |

### 2.2 Semantic Message Types

| Message Type | Sender | Receiver | Purpose |
| :--- | :--- | :--- | :--- |
| `TASK_ASSIGNMENT` | `CoordinatorAgent` | Any Agent | Dispatches a specific milestone for execution |
| `RESEARCH_SUBMISSION` | `ResearchAgent` | `AnalyzerAgent` | Signals completion of evidence gathering |
| `ANALYSIS_SUBMISSION` | `AnalyzerAgent` | `CriticAgent` | Submits structured insights and correlations |
| `CRITIC_REVIEW` | `CriticAgent` | `CoordinatorAgent` | Submits quality score and approval sign-off |
| `REVISION_REQUEST` | `CriticAgent` | `CoordinatorAgent` | Submits defect list requiring remediation |
| `REPORT_DRAFT` | `WriterAgent` | `CoordinatorAgent` | Submits finalized report and traceability matrix |
| `WORKFLOW_COMPLETED` | `CoordinatorAgent` | Client / Bus | Final completion broadcast |
| `ERROR_NOTIFICATION` | Any Agent | `CoordinatorAgent` | Signals unrecoverable agent failure |

### 2.3 Persistent Audit Trail Format (`activity_audit.jsonl`)
Every message transmitted across the `MessageBus` is appended as an atomic JSON line in `Day-22/data/activity_audit.jsonl`:
```json
{"event": "agent_message_transmitted", "timestamp": "2026-09-24T12:00:00Z", "message_id": "...", "workflow_id": "WF-BD1BA0E4", "task_id": "TASK-RES-002", "sender": "research_agent", "receiver": "analyzer_agent", "message_type": "research_submission", "status": "delivered", "evidence_count": 4, "error_count": 0}
```
This ensures 100% auditability for enterprise compliance and post-mortem analysis.
