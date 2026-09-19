# Day 18 — AI Agents: Document Research Assistant Agent
**Proposed AI Agent Architecture for Integration into Company Project**  
*Linkific AI/ML Internship Training — Month 1 Specialization*

---

| Attribute | Specification |
| :--- | :--- |
| **Intern Name** | Shri Sanjaykumar V |
| **Role** | AI/ML Intern, Linkific |
| **Project Module** | Day 18 — AI Agents, Planning, Tool Calling, and ReAct-Inspired Pattern |
| **Implementation Type** | Working AI Agent Prototype (Educational & Verification Implementation) |
| **Tech Stack** | Python 3.13 / 3.14, Pydantic, PyTest, Mermaid.js |
| **Data Scope** | 100% Synthetic Demonstration Knowledge Base (Confidentiality Guaranteed) |
| **Git Status** | Git Commit & Push STRICTLY ON HOLD (Pending User Review) |

---

## 1. Executive Summary
As enterprise documentation expands across human resources, technical onboarding, engineering standards, and project management, static search engines and basic retrieval pipelines fall short. They retrieve fragmented chunks without understanding the overarching task, fail to evaluate whether retrieved text satisfies the user's need, and lack the agency to refine searches or gracefully refuse out-of-domain queries.

This repository implements the **Document Research Assistant Agent**—a working and verifiable AI Agent prototype engineered from first principles in Python. Embodying a structured **ReAct-inspired** architecture, the agent autonomously analyzes natural language inquiries, formulates ordered execution plans, invokes discrete schema-validated tools, perceives external feedback, evaluates information sufficiency against numerical thresholds, and synthesizes factually grounded answers backed by verified source document attribution.

---

## 2. Core Learning Objectives Satisfied

| Objective | Theoretical Concept | Practical Implementation | Verification Evidence |
| :--- | :--- | :--- | :--- |
| **1. AI Agents** | Autonomous, goal-driven software entities interacting with environments. | `DocumentResearchAgent` class managing state, memory, tools, and execution lifecycle. | `Day-18/agent/agent.py` |
| **2. Planning** | Goal deconstruction into discrete, ordered intermediate milestones. | `Planner.create_plan()` generates structured `ExecutionPlan` with target tools and live step statuses (`completed`/`skipped`). | `Day-18/agent/planner.py` |
| **3. Tool Usage** | Discrete, verifiable actions with strongly-typed interfaces. | `ToolRegistry` coordinating `document_search`, `document_lookup`, `document_metadata`, and `final_response`. | `Day-18/agent/tools.py` |
| **4. Agent Workflow** | Deterministic state machine governing lifecycle transitions. | `AgentState` enum tracking 8 distinct lifecycle stages (`INITIALIZED` to `FINAL_RESPONSE`). | `Day-18/agent/schemas.py` |
| **5. ReAct Pattern** | Interleaved reasoning and action loop (`PLAN` -> `ACT` -> `OBSERVE` -> `DECIDE` -> `FINAL`). | Structured ReAct-inspired workflow logging auditable state transitions in `AgentMemory`. | `Day-18/examples/`, `outputs/` |

---

## 3. Proposed AI Agent Architecture for Company Project Integration
The Document Research Assistant Agent is designed as a **proposed architecture for integration** into the company project, conceptually extending document processing and vector retrieval pipelines developed in earlier training stages:
- **Day 16 Foundation:** Explored vector databases, embeddings, and dense retrieval concepts.
- **Day 17 Foundation:** Implemented FastAPI REST endpoints, multipart document uploads, and validation schemas.
- **Day 18 Agentic Innovation:** Introduces dynamic reasoning, multi-step goal planning, autonomous tool selection, iterative query refinement, and anti-hallucination refusal gates.

> **Note on Retrieval Engine:** The current Day 18 prototype employs **lexical relevance search / term-overlap retrieval** with substantive keyword weighting for transparent and explainable tool calling without external dependencies. Dense semantic vector retrieval (using ChromaDB and embeddings from Day 16) is designed as a direct plug-in enhancement for future production deployment.

```
┌─────────────────────────────────────────────────────────────┐
│                 PRESENTATION & CLIENT LAYER                 │
│         Antigravity CLI / REST Clients / Future UI          │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             DOCUMENT RESEARCH ASSISTANT AGENT               │
│ - State Machine: INITIALIZED -> PLANNING -> ACT -> FINAL    │
│ - Short-Term Working Memory (AgentMemory)                   │
│ - Planning & Decision Engine (Planner & Relevance Scoring)  │
└──────┬───────────────────────┬───────────────────────┬──────┘
       │                       │                       │
       ▼                       ▼                       ▼
┌──────────────┐        ┌──────────────┐        ┌──────────────┐
│document_     │        │document_     │        │document_     │
│search        │        │lookup        │        │metadata      │
└──────┬───────┘        └──────┬───────┘        └──────┬───────┘
       │                       │                       │
       └───────────────────────┼───────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             SYNTHETIC ENTERPRISE KNOWLEDGE BASE             │
│ - DOC-LEAVE-001: Attendance, Leave & Working Schedule       │
│ - DOC-ONBOARD-002: Intern Onboarding & Environment Setup    │
│ - DOC-TRAIN-003: Training Curriculum & Submission Rules     │
│ - DOC-WORKFLOW-004: 5-Stage ML Project Lifecycle & QA       │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Complete Directory Structure

```text
Day-18/
├── agent/
│   ├── __init__.py           # Package exports (Agent, Planner, Tools, Schemas)
│   ├── schemas.py            # Pydantic models (AgentState, ExecutionPlan, ToolResult)
│   ├── memory.py             # Short-term working memory & trace manager
│   ├── tools.py              # 4 discrete tools & ToolRegistry dispatcher
│   ├── planner.py            # Goal analysis, intent classification & plan generation
│   └── agent.py              # DocumentResearchAgent core ReAct-inspired loop
├── data/
│   ├── sample_leave_policy.txt       # DOC-LEAVE-001 (Leave & attendance rules)
│   ├── sample_onboarding.txt         # DOC-ONBOARD-002 (Environment setup & Git)
│   ├── sample_training_guidelines.txt# DOC-TRAIN-003 (Curriculum & grading rubric)
│   └── sample_project_workflow.txt   # DOC-WORKFLOW-004 (5-stage ML lifecycle)
├── docs/
│   ├── AI_AGENT_DESIGN_DOCUMENT.md   # 18-section architectural design specification
│   ├── AI_AGENT_PLANNING_DOCUMENT.md # 12-section planning & decision table document
│   ├── USE_CASE_DESCRIPTION.md       # 16-section enterprise use case specification
│   ├── REACT_WORKFLOW.md             # ReAct-inspired workflow & state mechanics
│   ├── ARCHITECTURE_DESCRIPTION.md   # Detailed layer breakdown & Day 16/17 linkages
│   ├── LIMITATIONS_AND_FUTURE_IMPROVEMENTS.md # Prototype constraints & roadmap
│   └── DAY18_REQUIREMENT_MATRIX.md   # Official requirements mapping matrix
├── diagrams/
│   ├── agent_workflow.mmd            # Complete end-to-end flowchart
│   ├── agent_architecture.mmd        # Layered architecture diagram
│   ├── react_loop.mmd                # ReAct-inspired state diagram
│   └── README.md                     # Guide to viewing & rendering diagrams
├── examples/
│   ├── example_01_document_research.json  # Real run: "What is the leave policy?"
│   ├── example_02_training_question.json  # Real run: "What are training requirements?"
│   ├── example_03_no_relevant_context.json# Real run: "What is company stock price?"
│   ├── example_04_document_lookup.json    # Real run: "Look up DOC-WORKFLOW-004 in detail"
│   └── example_05_document_metadata.json  # Real run: "Who is the author of DOC-ONBOARD-002?"
├── outputs/
│   ├── agent_test_results.txt        # Unedited pytest execution log (18/18 passed)
│   └── sample_agent_run.md           # Formatted log of live execution traces (all 5 scenarios)
├── tests/
│   ├── __init__.py
│   └── test_agent.py                 # Automated verification suite: 18 tests, 18/18 passed
├── run_agent.py                      # Interactive CLI runner (--demo, --query, interactive)
├── requirements.txt                  # Minimal dependencies (Pydantic, PyTest)
└── README.md                         # Comprehensive project documentation
```

---

## 5. Synthetic Knowledge Base Inventory

All knowledge documents are 100% synthetic demonstration files:

1. **`DOC-LEAVE-001` (Attendance, Leave, and Working Schedule Policy):**
   - Working hours (9:30 AM – 6:30 PM, Monday–Friday), core collaboration hours (11:00 AM – 4:00 PM).
   - Planned personal leave (24 hours prior email notice to mentor and HR Rebecca Mam).
   - Sick leave (notification by 9:00 AM; medical certificate for > 2 days).
   - Probation attendance requirements (maximum 2 unexcused absences).
2. **`DOC-ONBOARD-002` (Intern Onboarding & Environment Setup Guide):**
   - Technical prerequisites (Python 3.13+, Git, VS Code, virtual environments).
   - Internal credentials, repository access, SSH key configuration.
   - First-week setup checklist and buddy system assignment.
3. **`DOC-TRAIN-003` (Internship Training Curriculum & Submission Guidelines):**
   - 4-week structured curriculum (Week 1 Data, Week 2 Classical ML, Week 3 Deep Learning & RAG, Week 4 Agentic AI).
   - Daily milestone submission protocol (PR by 6:00 PM daily; verified test evidence required).
   - Technical evaluation rubric (Code Quality 30%, Automated Tests 30%, Documentation 40%).
4. **`DOC-WORKFLOW-004` (5-Stage Machine Learning Project Lifecycle):**
   - Stage 1: Problem Definition & Data Hygiene.
   - Stage 2: Feature Engineering & Baseline Modeling.
   - Stage 3: Hyperparameter Tuning & Robust Evaluation.
   - Stage 4: API Serving & Containerization.
   - Stage 5: Production Monitoring & Drift Detection.

---

## 6. The ReAct-Inspired Loop & State Machine

The agent coordinates execution across 5 ReAct-inspired stages:

`User Query` -> `PLAN` -> `ACT` -> `OBSERVE` -> `DECIDE` -> `FINAL`

1. **PLAN:** Tokenizes input, filters stopwords, classifies intent, and builds an ordered execution plan with live status tracking.
2. **ACT:** Selects a discrete tool (`document_search`, `document_lookup`, or `document_metadata`) and executes with structured JSON arguments.
3. **OBSERVE:** Receives `ToolResult`, parses chunks or metadata, and appends context to working memory.
4. **DECIDE:** Evaluates relevance scores against defined criteria:
   - Relevance >= 0.40: Sufficient context; proceed to final response (refinement step marked `skipped`).
   - 0.25 <= Relevance < 0.40: Moderate context; trigger single-pass query refinement (refinement step marked `completed`).
   - Relevance < 0.25: Insufficient context; transition to safe no-information refusal.
5. **FINAL:** Synthesizes grounded answer strictly derived from context lines and formats response citing exact source document titles.

---

## 7. Available Tool Specifications

### `document_search(query: str, top_k: int = 3) -> List[SearchResult]`
- Performs lexical relevance / term-overlap search using substantive keyword frequencies with title boosts.
- Discards chunks scoring below 0.25 threshold.

### `document_lookup(document_id: str) -> Optional[Dict[str, Any]]`
- Retrieves the full text and header attributes for an explicit primary key (e.g., `DOC-LEAVE-001`).

### `document_metadata(document_id: str) -> Optional[Dict[str, Any]]`
- Directly returns catalog metadata (author, version, category, character count, chunk count).

### `final_response(context: str, question: str) -> Dict[str, Any]`
- Synthesizes a grounded factual answer strictly derived from context lines, or returns safe negative notification if context is empty.

---

## 8. Anti-Hallucination & Grounding Guardrails

1. **Out-of-Domain Filtering:** Pre-execution regex and keyword filters capture out-of-scope topics (e.g., stock prices, cryptocurrency, weather, sports) and trigger immediate refusals before retrieval is attempted.
2. **Relevance Thresholding:** Chunks scoring below 0.25 are excluded. If no chunks exceed 0.25, the system flags `no_relevant_information`.
3. **Sentence Extraction Filtering:** Answers are synthesized exclusively from sentences containing intersecting substantive query tokens, guaranteeing zero ungrounded extrapolation.
4. **Citation Discipline:** Status `answered` enforces non-empty source titles; status `no_relevant_information` strictly returns `sources: []`.

---

## 9. How to Run the Project

### Prerequisites
- Python 3.13 or 3.14
- Standard terminal / PowerShell

### 1. Install Dependencies
```bash
cd Day-18
pip install -r requirements.txt
```

### 2. Run Automated Verification Suite
```bash
python -m pytest tests/test_agent.py -v
```

### 3. Run Benchmark Demonstrations
```bash
# Run all 5 benchmark scenarios
python run_agent.py --demo

# Run a single query
python run_agent.py --query "What is the leave policy?"

# Interactive terminal mode
python run_agent.py
```

---

## 10. Benchmark Demonstrations & Verified Output

### Scenario 1: Policy Research (`What is the leave policy?`)
- **Status:** `answered`
- **Tools Used:** `['document_search', 'final_response']`
- **Source Document Attribution:** `['Attendance, Leave, and Working Schedule Policy']`
- **Grounded Answer:** Factually extracts the 24-hour written email notice requirement to mentor and HR coordinator (Rebecca Mam).
- **Execution Plan Status:** Steps 1, 2, 3, 5 `completed`, Step 4 `skipped` (refinement not needed).

### Scenario 2: Training Guidelines (`What are the training requirements?`)
- **Status:** `answered`
- **Tools Used:** `['document_search', 'final_response']`
- **Source Document Attribution:** `['Internship Training Curriculum and Technical Submission Guidelines', 'Attendance, Leave, and Working Schedule Policy']`
- **Grounded Answer:** Factually extracts the 4-week curriculum track and 6:00 PM daily PR submission rule.

### Scenario 3: Out-of-Domain Query (`What is the company's stock price?`)
- **Status:** `no_relevant_information`
- **Tools Used:** `['final_response']`
- **Source Document Attribution:** `[]`
- **Controlled Refusal Answer:** Safely explains that knowledge base covers internal demonstration documents, refusing out-of-domain external topics without hallucination.

### Scenario 4: Direct Document Lookup (`Look up DOC-WORKFLOW-004 in detail`)
- **Status:** `answered`
- **Tools Used:** `['document_lookup', 'final_response']`
- **Source Document Attribution:** `['5-Stage Machine Learning Project Lifecycle and Quality Assurance']`
- **Grounded Answer:** Directly retrieves full structured document and extracts the 5-stage project lifecycle.

### Scenario 5: Metadata Inspection (`Who is the author and version of DOC-ONBOARD-002?`)
- **Status:** `answered`
- **Tools Used:** `['document_metadata', 'final_response']`
- **Source Document Attribution:** `['Intern Onboarding and Technical Environment Setup Guide']`
- **Grounded Answer:** Returns exact schema attributes: Author ('Linkific Developer Experience Team'), Version ('1.8 (September 2026)'), Category ('Engineering Onboarding').

---

## 11. Automated Verification Suite Results

```text
============================= test session starts =============================
platform win32 -- Python 3.14.3 / 3.13 compatible, pytest-9.1.1
collected 18 items

tests/test_agent.py::test_agent_initialization PASSED                    [  5%]
tests/test_agent.py::test_agent_memory_reset PASSED                      [ 11%]
tests/test_agent.py::test_planner_search_intent PASSED                   [ 16%]
tests/test_agent.py::test_planner_lookup_intent PASSED                   [ 22%]
tests/test_agent.py::test_planner_metadata_intent PASSED                 [ 27%]
tests/test_agent.py::test_planner_out_of_domain_intent PASSED            [ 33%]
tests/test_agent.py::test_planner_step_generation PASSED                 [ 38%]
tests/test_agent.py::test_tool_registry_valid_dispatch PASSED            [ 44%]
tests/test_agent.py::test_tool_registry_unknown_tool PASSED              [ 50%]
tests/test_agent.py::test_document_search_execution PASSED               [ 55%]
tests/test_agent.py::test_document_lookup_execution PASSED               [ 61%]
tests/test_agent.py::test_document_lookup_invalid_id PASSED              [ 66%]
tests/test_agent.py::test_document_metadata_execution PASSED             [ 72%]
tests/test_agent.py::test_agent_leave_policy_grounded PASSED             [ 77%]
tests/test_agent.py::test_agent_training_requirements_grounded PASSED    [ 83%]
tests/test_agent.py::test_agent_out_of_domain_refusal PASSED             [ 88%]
tests/test_agent.py::test_agent_empty_query_handling PASSED              [ 94%]
tests/test_agent.py::test_agent_react_trace_completeness PASSED          [100%]

============================= 18 passed in 0.59s ==============================
```

---

## 12. Prototype Limitations & Proposed Roadmap

### Current Implementation Constraints
1. **Rule-Guided Heuristics:** Intent classification uses substantive keyword and regex patterns rather than generative probabilistic models.
2. **Lexical Matching:** Chunk scoring is token-frequency based rather than dense vector embeddings.
3. **Volatile Memory:** `AgentMemory` is single-session in-memory and resets per conversation turn.

### Enterprise Integration Roadmap
- **Roadmap 1:** Connect Day 16 ChromaDB vector engine as hybrid retrieval backend for `document_search`.
- **Roadmap 2:** Mount agent inside Day 17 FastAPI framework (`POST /api/v1/agent/query`) with WebSocket streaming.
- **Roadmap 3:** Implement multi-agent specialization (Policy Agent, DevOps Agent, Curriculum Agent, QA Supervisor).
- **Roadmap 4:** Add Redis-backed persistent conversational history for multi-turn dialogue.

---

## 13. Security, Confidentiality & Compliance

- **Confidentiality:** 100% synthetic demonstration data; no proprietary Linkific intellectual property, customer data, or internal source code is included.
- **Secrets Scan:** Zero API keys, passwords, or authentication tokens exist in the codebase.
- **Offline Self-Contained:** Runs completely locally without external cloud API dependencies.
- **Strict Git Boundary:** Git commit and push operations remain **strictly on hold** pending formal user review.
