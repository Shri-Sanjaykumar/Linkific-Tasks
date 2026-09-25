# Day 23: Multi-Agent Sequence Diagram

**Project:** Linkific Enterprise AI Service — Multi-Agent Research Assistant  
**Milestone:** Day 23 — LangGraph Multi-Agent Implementation  
**Status:** **VERIFIED & PRODUCTION READY**  

---

## 1. Visual Sequence Diagram

The following Mermaid sequence diagram models the exact communication protocol and data flow for the Linkific Multi-Agent System across both the **Streamlined Company Practical Mode** (`User -> Coordinator -> Research -> Writer -> Answer`) and the **Comprehensive Mode** (`Coordinator -> Research -> Analyzer -> Critic -> Writer -> Answer`).

```mermaid
sequenceDiagram
    autonumber
    actor User as User / Client Application
    participant Coord as Coordinator Agent<br/>(LangGraph Node)
    participant State as MultiAgentState<br/>(StateGraph Channel)
    participant Res as Research Agent<br/>(LangGraph Node)
    participant Analyzer as Analyzer Agent<br/>(LangGraph Node)
    participant Critic as Critic Agent<br/>(LangGraph Node)
    participant Writer as Writer Agent<br/>(LangGraph Node)
    participant Log as Communication Log<br/>(Append-Only Reducer)

    %% Step 1: User Request Ingress
    User->>Coord: 1. Submit Research Query (query, mode="streamlined")
    activate Coord
    Coord->>Log: Append MSG-001 (USER_REQUEST: User -> Coordinator)
    Coord->>State: Initialize State (status: PLANNING, milestones)
    
    %% Step 2: Task Assignment
    Coord->>Res: 2. Dispatch Task (TASK_ASSIGNMENT)
    Coord->>Log: Append MSG-002 (TASK_ASSIGNMENT: Coordinator -> Research)
    deactivate Coord

    %% Step 3: Research Execution
    activate Res
    Res->>Res: Search company_docs.json & Score Candidates
    Res->>State: Store ResearchFindings (Evidence Items, Scores, Source IDs)
    
    alt Streamlined Mode (Company Practical)
        Res->>Writer: 3a. Deliver Findings (RESEARCH_SUBMISSION)
        Res->>Log: Append MSG-003 (RESEARCH_SUBMISSION: Research -> Writer)
        deactivate Res
        
        %% Step 4: Writer Synthesis
        activate Writer
        Writer->>Writer: Extract Grounded Clauses (Preserve 1.5 Days)
        Writer->>Writer: Build Sections & Traceability Matrix
        Writer->>State: Store WriterReport
        Writer->>Coord: 4a. Submit Report Draft (REPORT_DRAFT)
        Writer->>Log: Append MSG-004 (REPORT_DRAFT: Writer -> Coordinator)
        deactivate Writer

    else Comprehensive Mode
        Res->>Analyzer: 3b. Forward Findings (RESEARCH_SUBMISSION)
        deactivate Res
        activate Analyzer
        Analyzer->>Analyzer: Thematic Clustering & Correlations
        Analyzer->>Critic: Submit Insights (ANALYSIS_SUBMISSION)
        deactivate Analyzer
        activate Critic
        Critic->>Critic: Check Grounding, Citations & Factual Decimals
        alt Quality Score >= 0.80 & No Critical Defects
            Critic->>Coord: Submit Approval (CRITIC_REVIEW: APPROVED)
            Critic->>Writer: Authorize Drafting
            Writer->>Coord: Submit Report (REPORT_DRAFT)
        else Defects Found & Revisions < Max
            Critic-->>Analyzer: Cycle Revision (REVISION_REQUEST)
        end
        deactivate Critic
    end

    %% Step 5: Final Synthesis & Egress
    activate Coord
    Coord->>Coord: Evaluate Report Deliverables & Compile Final Answer
    Coord->>State: Update status: COMPLETED
    Coord->>Log: Append MSG-005 (FINAL_ANSWER: Coordinator -> User)
    Coord->>User: 5. Return Consolidated WorkflowResponse (Answer + Report)
    deactivate Coord
```

---

## 2. Protocol Handoff Analysis

### Handoff 1: Client Ingress to Coordinator
- **Contract:** `WorkflowRequest` $\rightarrow$ `MultiAgentState` initialization.
- **Verification:** Query length validated ($\ge 3$ characters). Rejects empty or whitespace inputs, routing directly to `error_handler`.

### Handoff 2: Coordinator to Research Agent
- **Contract:** `AgentMessage` of type `TASK_ASSIGNMENT`.
- **Payload:** Research parameters, top-k bounds, category filters, and target search query.

### Handoff 3: Research Agent to Downstream Consumers
- **Contract:** `ResearchFindings` containing validated `EvidenceItem` records.
- **Routing:** In Streamlined mode, directly feeds `WriterAgent`; in Comprehensive mode, routes to `AnalyzerAgent`.
- **Factual Integrity:** Excerpts are captured verbatim from `company_docs.json` preserving numerical constants (`1.5 paid leave days`, `$500 hardware allowance`, `10:00 AM-5:00 PM IST`).

### Handoff 4: Writer Agent to Coordinator
- **Contract:** `WriterReport` containing executive summary, thematic sections with inline citation tags `[DOC-POL-XXX]`, and a complete `Evidence Traceability Matrix`.

### Handoff 5: Coordinator to User Egress
- **Contract:** `WorkflowResponse` containing final consolidated answer, report markdown, milestones completion audit, execution timing, and complete `communication_log`.
