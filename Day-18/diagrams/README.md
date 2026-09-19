# Day 18 — Architecture & Workflow Diagrams

This directory contains formal **Mermaid.js** diagram specifications illustrating the architecture, decision-making workflow, and ReAct-inspired loop of the **Document Research Assistant Agent**.

---

## Diagram Index

| File | Type | Description |
| :--- | :--- | :--- |
| [`agent_workflow.mmd`](agent_workflow.mmd) | Flowchart (`flowchart TD`) | Complete end-to-end execution workflow from user question to grounded answer, including fast-path rejection and query refinement. |
| [`agent_architecture.mmd`](agent_architecture.mmd) | Layered Architecture (`flowchart TB`) | 5-layer system architecture detailing presentation, agent core, planning, tool dispatch, and synthetic knowledge storage. |
| [`react_loop.mmd`](react_loop.mmd) | State Diagram (`stateDiagram-v2`) | Detailed ReAct-inspired state machine lifecycle: `PLAN` -> `ACT` -> `OBSERVE` -> `DECIDE` -> [Refine] -> `FINAL_RESPONSE`. |

---

## 1. End-to-End Workflow (`agent_workflow.mmd`)
Illustrates how user queries transition across distinct agent states:
1. **INITIALIZED:** Memory and traces are cleared.
2. **PLANNING:** Query intent is classified into `document_search`, `document_lookup`, `document_metadata`, or `unsupported_domain`.
3. **TOOL SELECTION & EXECUTION (ACT):** Target tool invoked with strongly-typed arguments.
4. **OBSERVING (OBSERVE):** Tool outputs recorded into short-term working memory (`AgentMemory`).
5. **DECIDING (DECIDE):** Evaluates context sufficiency using relevance score thresholds.
6. **FINAL RESPONSE (FINAL):** Grounded synthesis tool formats factual response with source document attribution.

---

## 2. Layered Architecture (`agent_architecture.mmd`)
Details the 5 functional layers:
- **Layer 1: Presentation & Interface Layer:** CLI runner and proposed FastAPI service extension.
- **Layer 2: Agent Core & Orchestration Layer:** State machine, agent memory, and conversation lifecycle.
- **Layer 3: Planning & Reasoning Layer:** Deterministic intent classifier, step decomposer, and sufficiency evaluator.
- **Layer 4: Tool Execution & Dispatch Layer:** `ToolRegistry` managing `document_search`, `document_lookup`, `document_metadata`, and `final_response`.
- **Layer 5: Synthetic Knowledge Base Layer:** Four clean, synthetic policy and operational documents (`DOC-LEAVE-001` through `DOC-WORKFLOW-004`).

---

## 3. ReAct-Inspired State Machine Loop (`react_loop.mmd`)
Formal state transition graph showing:
- Explicit separation between internal reasoning (`PLAN`, `DECIDE`) and environment interaction (`ACT`, `OBSERVE`).
- Single-pass refinement loop for borderline relevance scores ($0.25 \le \text{score} < 0.40$).
- Strict non-hallucinatory refusal path for out-of-domain topics.

---

## Rendering Diagrams Locally
These diagrams use standard GitHub-compatible Mermaid syntax. You can view them directly in VS Code / GitHub markdown previews, or render them using the Mermaid CLI:
```bash
# Install Mermaid CLI (optional)
npm install -g @mermaid-js/mermaid-cli

# Render to PNG/SVG
mmdc -i diagrams/agent_workflow.mmd -o diagrams/agent_workflow.png
mmdc -i diagrams/agent_architecture.mmd -o diagrams/agent_architecture.png
mmdc -i diagrams/react_loop.mmd -o diagrams/react_loop.png
```
