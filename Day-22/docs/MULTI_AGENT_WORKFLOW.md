# Day 22: Multi-Agent Workflow Design & Execution Lifecycle

This document describes the orchestration architecture, workflow planning, execution phases, and revision loop mechanics of the **Linkific Multi-Agent Research Assistant** system.

---

## 1. System Architecture & Workflow Diagram

The system employs a collaborative hub-and-spoke multi-agent topology governed by a central **Coordinator Agent**, an audited **MessageBus**, and a centralized **SharedState** single-source-of-truth.

```mermaid
flowchart TD
    User(["Client / Enterprise User"]) -->|Submit Research Brief| CoordInit["Coordinator Agent<br/>(1. Decompose Query & Create Execution Plan)"]

    subgraph Orchestration["Centralized Orchestration & Shared State"]
        CoordInit --> StateManager[("Centralized Shared State<br/>• Single Source of Truth<br/>• Role-Governed Access<br/>• Transition Audit Log")]
        MessageBus["In-Process Message Bus<br/>• Typed Message Contracts<br/>• Persistent JSONL Audit Trail"]
    end

    CoordInit -->|TASK-RES-002| ResAgent["Research Agent<br/>(2. Evidence Gathering)"]
    ResAgent -.->|Query Corpus| Corpus[("Enterprise Document Corpus<br/>sample_docs.json")]
    Corpus -.->|Grounded Chunks| ResAgent
    ResAgent -->|RESEARCH_SUBMISSION| MessageBus
    MessageBus --> StateManager

    StateManager -->|Read Findings| AnaAgent["Analyzer Agent<br/>(3. Cognitive Insight Synthesis)"]
    AnaAgent -->|Thematic Clusters & Correlations| AnaAgent
    AnaAgent -->|ANALYSIS_SUBMISSION| MessageBus
    MessageBus --> StateManager

    StateManager -->|Read Evidence & Analysis| CriticAgent["Critic Agent<br/>(4. Adversarial Quality Gate)"]
    CriticAgent -->|Audit Factual Groundedness| CriticAgent
    
    CriticAgent -->|Verdict & Defect List| MessageBus
    MessageBus --> CoordEval{"Coordinator Agent<br/>Evaluates Verdict"}

    CoordEval -->|Verdict = REVISION_REQUIRED<br/>& Revision Count < Max Limit| ReviseRouter{"Revision Router"}
    ReviseRouter -->|Target: Missing Sources| ResAgent
    ReviseRouter -->|Target: Reasoning Defect| AnaAgent

    CoordEval -->|Verdict = APPROVED<br/>OR Max Revisions Reached| WriterAgent["Writer Agent<br/>(5. Executive Report Synthesis)"]
    
    WriterAgent -->|Embed Provenance Citations| WriterAgent
    WriterAgent -->|Construct Traceability Matrix| WriterAgent
    WriterAgent -->|REPORT_DRAFT| MessageBus
    MessageBus --> StateManager

    StateManager --> Finalize["Coordinator Agent<br/>(6. Final Validation & Telemetry)"]
    Finalize --> Response(["Verified Enterprise Brief<br/>• Executive Summary<br/>• Evidence Citations<br/>• Audit Telemetry"])
```

---

## 2. Step-by-Step Execution Phases

### Phase 1: Planning & Topology Construction (`CoordinatorAgent`)
1. Ingests user research brief via `WorkflowRequest`.
2. Validates query constraints (`min_length=3`, `max_length=1000`).
3. Instantiates `SharedStateManager` and `MessageBus` with a unique `workflow_id`.
4. Decomposes the research objective into a deterministic 6-milestone `ExecutionPlan`:
   - `TASK-PLAN-001`: Request analysis and topology definition.
   - `TASK-RES-002`: Evidence retrieval and provenance indexing.
   - `TASK-ANA-003`: Cognitive insight synthesis and correlation mapping.
   - `TASK-CRI-004`: Adversarial verification and quality audit.
   - `TASK-WRI-005`: Executive briefing synthesis and citation embedding.
   - `TASK-FIN-006`: Final validation sign-off and audit compilation.
5. Transitions workflow state to `WorkflowStatus.PLANNING` -> `WorkflowStatus.RESEARCHING`.

### Phase 2: Evidence Gathering & Provenance (`ResearchAgent`)
1. Receives `TASK_ASSIGNMENT` from the MessageBus.
2. Tokenizes query, filters stop words, and scans the vetted enterprise document corpus (`sample_docs.json`).
3. Computes lexical overlap and category affinity scores.
4. Filters documents exceeding relevance threshold (`SIMILARITY_THRESHOLD = 0.10`).
5. Extracts exact verbatim excerpts, doc IDs, author metadata, and version numbers.
6. Emits structured `ResearchFindings` into `SharedState`.
7. Dispatches `RESEARCH_SUBMISSION` message notifying the `AnalyzerAgent`.

### Phase 3: Cognitive Synthesis & Correlation Analysis (`AnalyzerAgent`)
1. Reads `ResearchFindings` from `SharedState`.
2. Groups evidence into thematic clusters (e.g., Human Resources, InfoSec, Engineering).
3. Synthesizes individual `InsightItem` objects, binding each insight to supporting evidence IDs.
4. Identifies cross-domain policy intersections (e.g., remote work attendance vs. VPN/MFA compliance).
5. Segregates empirical facts from working assumptions if evidence is limited.
6. Populates `AnalysisResult` in `SharedState` and emits `ANALYSIS_SUBMISSION` to the Critic.

### Phase 4: Adversarial Quality Gate (`CriticAgent`)
1. Ingests both `ResearchFindings` and `AnalysisResult`.
2. Executes four deterministic quality checks:
   - **Check 1: Evidence Availability**: Confirms evidence items exist and meet minimum threshold.
   - **Check 2: Citation Validity**: Confirms all cited doc IDs actually exist in the retrieved corpus. Flags phantom citations as `HALLUCINATION` (CRITICAL severity).
   - **Check 3: Unsupported Claims**: Flags any statement without supporting source IDs as `UNSUPPORTED_CLAIM` (MAJOR severity).
   - **Check 4: Scope Coverage**: Verifies that primary user concepts appear in evidence.
3. Computes holistic `quality_score` (0.0 to 1.0) with penalties for defects.
4. Issues verdict:
   - `CriticVerdict.APPROVED`: If `quality_score >= 0.80` and zero CRITICAL defects.
   - `CriticVerdict.REVISION_REQUIRED`: If score < 0.80 or CRITICAL defects are detected.
5. Appends `CriticReview` to SharedState and notifies Coordinator.

### Phase 5: Dynamic Revision Loop & Circuit Breaker
1. `CoordinatorAgent` evaluates the Critic's verdict:
   - **Path A (Approved)**: Advances workflow to `WorkflowStatus.WRITING`.
   - **Path B (Revision Required & Under Limit)**:
     - Increments `revision_count` in `SharedState`.
     - Sets state to `WorkflowStatus.REVISING`.
     - Analyzes defect list to identify target agent (`RESEARCH` or `ANALYZER`).
     - Re-invokes target agent with specific correction instructions (e.g. broader search keywords).
     - Loops back through Analyzer and Critic until approved.
   - **Path C (Revision Required & Max Limit Exceeded)**:
     - **Circuit Breaker Triggered**: Coordinator logs a formal warning, flags the report as qualified/partial, and advances to Writer to prevent an infinite loop.

### Phase 6: Executive Synthesis & Delivery (`WriterAgent` & `CoordinatorAgent`)
1. `WriterAgent` structures findings into publication-ready Markdown:
   - Executive Summary
   - Thematic Sections with inline `[DOC-XXX]` citation badges
   - Cross-Policy Intersections
   - Explicit Operational Boundaries & Limitations
   - Evidence Traceability Matrix (mapping statement IDs to source documents)
   - Strategic Recommendations
2. `CoordinatorAgent` finalizes state to `WorkflowStatus.COMPLETED`, compiles execution timing, and returns a verified `WorkflowResponse`.
