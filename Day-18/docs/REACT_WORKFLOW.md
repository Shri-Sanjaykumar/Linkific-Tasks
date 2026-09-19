# ReAct-Inspired Architecture & Workflow Specification
**Reasoning and Acting in Synergistic Loops**  
*Linkific AI/ML Internship Day 18*

---

## 1. Theoretical Foundation: The ReAct-Inspired Paradigm
Traditional AI approaches generally bifurcated into two distinct paradigms:
1. **Reasoning-Only (Chain-of-Thought):** The system generates internal thoughts to arrive at conclusions, but lacks access to external tools or real-time data. It suffers from factual drift and hallucinations.
2. **Action-Only:** The system maps inputs directly to tool calls or API requests without deliberate planning or intermediate evaluation, leading to brittle failures when tool outputs deviate from expectations.

The **ReAct (Reason + Act)** paradigm (*Yao et al., 2022*) overcomes these limitations by interleaving reasoning steps with external tool execution. Reasoning guides tool selection and parameterization, while external observations ground subsequent reasoning and decisions.

```
       ┌────────────────────────────────────────────────────────┐
       │                       USER QUERY                       │
       └───────────────────────────┬────────────────────────────┘
                                   │
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │ PLAN: Deconstruct goal, determine intent, build steps  │
       └───────────────────────────┬────────────────────────────┘
                                   │
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │ ACT: Select discrete tool and dispatch with arguments  │
       └───────────────────────────┬────────────────────────────┘
                                   │
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │ OBSERVE: Receive ToolResult, record context in memory  │
       └───────────────────────────┬────────────────────────────┘
                                   │
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │ DECIDE: Evaluate observation against sufficiency rules │
       └───────────┬────────────────────────────────┬───────────┘
                   │                                │
    Borderline (<0.40)                              │ Sufficient (>=0.40)
                   ▼                                ▼
       ┌───────────────────────┐        ┌───────────────────────┐
       │ ACT (Refine Search)   │        │ FINAL_RESPONSE        │
       │ Expand query keywords │        │ Grounded synthesis    │
       └───────────────────────┘        └───────────────────────┘
```

---

## 2. Formal ReAct State Machine Mechanics

### Stage 1: PLAN (Goal Analysis & Hypothesis Formulation)
- **Inputs:** User query string.
- **Process:** Normalizes text, filters stop words, evaluates keyword intersections, and identifies intent.
- **Output:** `ExecutionPlan` containing ordered `PlanStep` sequence.
- **Audit Trace Record:** `state="PLAN"`, logs intent and step count.

### Stage 2: ACT (Discrete Tool Invocation)
- **Inputs:** Selected `PlanStep`, current working memory context.
- **Process:** Maps step target to `ToolRegistry` handler; packages arguments into structured JSON.
- **Output:** Dispatches call to `document_search`, `document_lookup`, or `document_metadata`.
- **Audit Trace Record:** `state="ACT"`, logs tool name and exact parameter payload.

### Stage 3: OBSERVE (Environment Feedback Perception)
- **Inputs:** Raw `ToolResult` returned from tool execution.
- **Process:** Validates return status; extracts matched chunks or document payloads; populates `AgentMemory`.
- **Output:** Concise text observation summary.
- **Audit Trace Record:** `state="OBSERVE"`, logs chunk count and maximum relevance score.

### Stage 4: DECIDE (Sufficiency Evaluation & Branching)
- **Inputs:** Accumulated observations in `AgentMemory`.
- **Process:** Evaluates relevance scores against defined criteria:
  - $	ext{Score} \ge 0.40 \implies$ Context sufficient; advance to `FINAL_RESPONSE`.
  - $0.25 \le 	ext{Score} < 0.40 \implies$ Context borderline; trigger single-pass query refinement (`ACT`).
  - $	ext{Score} < 0.25 \implies$ Context missing; advance to safe refusal in `FINAL_RESPONSE`.
- **Output:** Decision rationale string.
- **Audit Trace Record:** `state="DECIDE"`, logs sufficiency assessment.

### Stage 5: FINAL (Grounded Synthesis & Attribution)
- **Inputs:** Filtered context buffer, user question.
- **Process:** Invokes `final_response` tool; extracts substantive sentences matching substantive query terms; gathers unique document titles.
- **Output:** Structured `AgentResponse` with `answer`, `sources`, and `status`.
- **Audit Trace Record:** `state="FINAL"`, logs completion status and source count.

---

## 3. Real Worked Example Trace
Below is an unedited execution trace captured during automated testing of the query:  
`"What is the leave policy?"`

```
================================================================================
STEP 1: PLAN
State:      PLAN
Timestamp:  2026-09-19T09:46:30.124801
Action:     Analyzed query 'What is the leave policy?' and determined intent 'document_search'. Created 5-step ordered execution plan.
Decision:   Target workflow: document_search

STEP 2: ACT
State:      ACT
Timestamp:  2026-09-19T09:46:30.125120
Tool:       document_search
Action:     Executing tool 'document_search' with arguments: {'query': 'What is the leave policy?', 'top_k': 3}

STEP 3: OBSERVE
State:      OBSERVE
Timestamp:  2026-09-19T09:46:30.126450
Action:     Inspected tool execution result.
Observation: Retrieved 1 chunk(s). Highest relevance score: 0.55.

STEP 4: DECIDE
State:      DECIDE
Timestamp:  2026-09-19T09:46:30.126580
Action:     Evaluated observation against sufficiency criteria.
Decision:   Retrieved context is highly relevant and sufficient. Proceeding to final response synthesis.

STEP 5: FINAL
State:      FINAL
Timestamp:  2026-09-19T09:46:30.127890
Action:     Synthesized grounded final response with source attribution.
Decision:   Status=answered, Source count=1
================================================================================
```

---

## 4. Query Refinement Loop Walkthrough
When a user asks a vague query, such as *"guidelines for interns"*:
1. `document_search` returns chunks with moderate score (e.g., 0.30).
2. `DECIDE` detects score in $[0.25, 0.40)$ range.
3. Secondary `ACT` expands query to top keywords: `"guidelines interns"`.
4. Secondary `OBSERVE` captures supplementary chunks from `DOC-ONBOARD-002` and `DOC-TRAIN-003`.
5. Secondary `DECIDE` aggregates the multi-document context.
6. `FINAL` synthesizes an answer referencing both guides with two cited sources.
