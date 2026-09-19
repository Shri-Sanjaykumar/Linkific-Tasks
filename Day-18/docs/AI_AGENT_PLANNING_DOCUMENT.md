# AI Agent Planning Document
**Goal Decomposition, Tool Selection, and Decision-Making Architecture**  
*Document Research Assistant Agent — Linkific AI/ML Internship Day 18*

---

| Attribute | Specification |
| :--- | :--- |
| **Author** | Shri Sanjaykumar V (AI/ML Intern) |
| **Organization** | Linkific |
| **Document Purpose** | Comprehensive Planning & Decision Specification |
| **Date** | September 2026 |
| **Confidentiality** | 100% Synthetic Enterprise Policies |

---

## 1. Executive Overview
AI agent architectures differ fundamentally from passive retrieval scripts in their capacity to deliberate before acting. The planning subsystem is the intellectual control unit of the **Document Research Assistant Agent**. It is responsible for analyzing unstructured natural language inputs, determining task viability, decomposing goals into ordered intermediate milestones, selecting optimal tool actions, and evaluating incoming observations to make justified control flow transitions.

This document details the planning principles, intent taxonomy, decision criteria, heuristic rules, and grounding thresholds governing the agent's behavior.

---

## 2. Agent Objective & Mission
### Core Mission Statement
> *"To autonomously, accurately, and verifiably resolve user inquiries regarding internal organizational policies, technical onboarding guides, training curriculum, and project engineering lifecycles by coordinating specialized tools through a structured ReAct loop, mitigating unsupported statements through grounded documentation and source document attribution."*

### Key Functional Objectives
1. **Intent Resolution:** Accurately classify user goals into operational categories.
2. **Deterministic Plan Construction:** Generate step-by-step plan structures detailing target tools and expected deliverables.
3. **Adaptive Tool Execution:** Dynamically invoke tools with minimal necessary arguments.
4. **Iterative Verification:** Evaluate retrieved observations against strict sufficiency criteria.
5. **Safe Failure Termination:** Gracefully refuse out-of-domain or ungrounded queries without fabrications.

---

## 3. Goal Decomposition & Analysis
When a user submits a query, the agent does not immediately invoke retrieval. It executes goal analysis to establish:
- **Core Entity Target:** What document, process, or rule is being investigated?
- **Task Scope:** Is this a targeted lookup, a general policy research task, a catalog metadata inquiry, or an unsupported subject?
- **Information Dependency:** Can the goal be satisfied in a single retrieval step, or does it require multi-pass refinement?

```
User Query
    │
    ▼
[Stopword & Noise Filtering]
    │
    ▼
[Substantive Keyword & Regex Extraction]
    │
    ▼
┌───────────────────────────────────────────────────────┐
│ Intent Classification:                                │
│ 1. unsupported_domain (stock, crypto, weather, etc.)   │
│ 2. document_metadata  (author, version, who wrote)    │
│ 3. document_lookup    (DOC-*-* explicit ID pattern)   │
│ 4. document_search    (general semantic research)     │
└───────────────────────────────────────────────────────┘
```

---

## 4. Deterministic Intent Classification
Intent classification operates via rule-guided heuristic analysis:

| Intent Category | Identification Triggers | Target Strategy |
| :--- | :--- | :--- |
| `unsupported_domain` | Intersecting keywords: `stock`, `price`, `share`, `crypto`, `weather`, `cricket`, `recipe`. | Bypass retrieval; execute fast-path safe refusal. |
| `document_metadata` | Intersecting keywords: `metadata`, `author`, `version`, `who wrote`, `when was`. | Invoke `document_metadata` tool for explicit document ID. |
| `document_lookup` | Regex match: `DOC-[A-Z]+-[0-9]+` or `DOC-[0-9]+`. | Invoke `document_lookup` tool for targeted full document retrieval. |
| `document_search` | Default operational path for descriptive natural language questions. | Invoke `document_search` with tokenized keywords across knowledge chunks. |

---

## 5. Step-by-Step Execution Plan Generation
For each classified intent, the `Planner` generates an immutable `ExecutionPlan` containing an ordered list of `PlanStep` objects.

### Plan Structure for `document_search` (General Research)
1. **Step 1 (Analysis):** Tokenize query, filter stopwords, and extract core information targets.
2. **Step 2 (Execution):** Execute lexical relevance search across synthetic knowledge base chunks (`document_search`).
3. **Step 3 (Observation):** Inspect retrieved chunks and evaluate information sufficiency.
4. **Step 4 (Decision):** If sufficient ($\ge 0.40$), synthesize grounded answer; if weak ($0.25 - 0.39$), refine query once; if below $0.25$, refuse safely.
5. **Step 5 (Final Response):** Return grounded final response with source document attribution (`final_response`).

### Plan Structure for `document_lookup` (Direct ID)
1. **Step 1 (Targeting):** Identify explicit document identifier from query.
2. **Step 2 (Execution):** Retrieve full structured document text and header metadata (`document_lookup`).
3. **Step 3 (Inspection):** Inspect returned document structure and verify target section content.
4. **Step 4 (Final Response):** Format grounded factual response citing specific document ID and title.

### Plan Structure for `unsupported_domain` (Boundary Enforcement)
1. **Step 1 (Analysis):** Analyze query and detect out-of-domain subject matter (`domain_analysis`).
2. **Step 2 (Scope Check):** Check synthetic knowledge base operational boundaries (`scope_check`).
3. **Step 3 (Decision):** Evaluate information availability and decide on safe refusal (`decision`).
4. **Step 4 (Final Refusal):** Synthesize safe polite refusal explaining knowledge base scope (`final_response`).

---

## 6. Available Tool Inventory

```
┌──────────────────────────────────────────────────────────────────┐
│                    AGENT TOOL REGISTRY                           │
├──────────────────────┬─────────────────────┬─────────────────────┤
│ Tool Name            │ Primary Purpose     │ Arguments           │
├──────────────────────┼─────────────────────┼─────────────────────┤
│ document_search      │ Semantic chunk      │ query (str),        │
│                      │ retrieval           │ top_k (int)         │
├──────────────────────┼─────────────────────┼─────────────────────┤
│ document_lookup      │ Full document       │ document_id (str)   │
│                      │ retrieval by ID     │                     │
├──────────────────────┼─────────────────────┼─────────────────────┤
│ document_metadata    │ Inspect catalog     │ document_id (str)   │
│                      │ metadata fields     │                     │
├──────────────────────┼─────────────────────┼─────────────────────┤
│ final_response       │ Grounded synthesis  │ context (str),      │
│                      │ with source citation│ question (str)      │
└──────────────────────┴─────────────────────┴─────────────────────┘
```

---

## 7. Tool Selection Heuristics
1. **Heuristic 1 (Precision First):** If the user explicitly mentions a Document ID (e.g., `DOC-LEAVE-001`), prioritize `document_lookup` or `document_metadata` over general search.
2. **Heuristic 2 (Minimal Necessary Scope):** For descriptive inquiries (e.g., "What is the probation period?"), use `document_search` with $k=3$ to minimize noise.
3. **Heuristic 3 (Zero-Retrieval Refusal):** Never invoke retrieval tools for queries definitively recognized as out-of-domain.

---

## 8. Decision-Making Process & Sufficiency Evaluation
The agent evaluates observations using explicit mathematical and heuristic thresholds:

$$	ext{Relevance Score} = \min\left(1.0, rac{|	ext{QueryTokens} \cap 	ext{ChunkTokens}|}{|	ext{QueryTokens}|} + 	ext{PhraseBonus} + 	ext{TitleBonus}
ight)$$

### Decision Tree
```
Is Intent == 'unsupported_domain'?
 ├── YES ──> Emit Safe Refusal (Status: no_relevant_information, Sources: [])
 └── NO  ──> Execute Target Tool
               │
               ▼
       Evaluate Top Relevance Score:
         ├── Score >= 0.40 ──────> Context Sufficient -> Proceed to final_response
         ├── 0.25 <= Score < 0.40 -> Context Borderline -> Execute Single-Pass Refinement
         └── Score < 0.25  ──────> Context Missing    -> Safe No-Information Refusal
```

---

## 9. Comprehensive Decision-Making Table

| Scenario / Query | Detected Intent | Selected Tool | Tool Arguments | Expected Observation | Sufficiency Condition | Next Action | Final Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| *"What is the leave policy?"* | `document_search` | `document_search` | `{"query": "...", "top_k": 3}` | Top chunk score $\ge 0.50$ from `DOC-LEAVE-001`. | Score $\ge 0.40$ (High). | Invoke `final_response` with leave context. | `answered` |
| *"What are the training requirements?"* | `document_search` | `document_search` | `{"query": "...", "top_k": 3}` | Matched chunks from `DOC-TRAIN-003` and `DOC-LEAVE-001`. | Score $\ge 0.40$ (High). | Invoke `final_response` with curriculum context. | `answered` |
| *"Look up DOC-WORKFLOW-004"* | `document_lookup` | `document_lookup` | `{"document_id": "DOC-WORKFLOW-004"}` | Full document text containing 5-stage lifecycle. | Content is not null. | Synthesize answer citing lifecycle stages. | `answered` |
| *"Who wrote DOC-ONBOARD-002?"* | `document_metadata` | `document_metadata` | `{"document_id": "DOC-ONBOARD-002"}` | Metadata record: Author = "Linkific DevOps & Engineering". | Metadata record exists. | Format author and version summary. | `answered` |
| *"What is the company stock price?"* | `unsupported_domain` | Fast Path (None) | None | N/A (Detected out-of-scope financial topic). | Immediate out-of-scope flag. | Refuse safely; state operational scope. | `no_relevant_information` |
| *"Who won the cricket match?"* | `unsupported_domain` | Fast Path (None) | None | N/A (Sports trivia). | Immediate out-of-scope flag. | Refuse safely; state operational scope. | `no_relevant_information` |
| *"" (Empty query)* | `empty_query` | None | None | N/A | Immediate empty input flag. | Prompt user for valid operational query. | `no_relevant_information` |

---

## 10. Query Refinement Strategy
When initial retrieval yields borderline relevance ($0.25 \le 	ext{Score} < 0.40$), the agent does not immediately fail. It performs a **single-pass query expansion**:
1. Strips conversational filler words and short tokens ($\le 3$ characters).
2. Isolates top substantive nouns and domain verbs.
3. Dispatches a secondary search with broadened terms ($k=2$).
4. Merges unique newly retrieved chunks into `AgentMemory`.
5. Logs both refinement actions and updated observations in the ReAct trace.

---

## 11. Hallucination Mitigation & Grounding Guardrails
To prevent generative fabrications:
- **Strict Context Dependency:** The answer generator is only permitted to construct statements derived from retrieved text blocks.
- **Citation Enforcement:** If status is `answered`, the response MUST return non-empty `sources` matching the title of the context document.
- **Controlled Refusal Standard:** If status is `no_relevant_information`, the response MUST return `sources: []`.

---

## 12. Expected Outputs & Verification Criteria
Every execution yields a strict Pydantic `AgentResponse`:
```json
{
  "question": "What is the leave policy?",
  "answer": "Based on the demonstration documentation: ...",
  "sources": ["Attendance, Leave, and Working Schedule Policy"],
  "status": "answered",
  "plan": [...],
  "tools_used": ["document_search", "final_response"],
  "execution_trace": [
    {"state": "PLAN", "action_or_plan": "..."},
    {"state": "ACT", "tool": "document_search"},
    {"state": "OBSERVE", "observation": "..."},
    {"state": "DECIDE", "decision": "..."},
    {"state": "FINAL", "decision": "..."}
  ]
}
```
All fields are verified via automated unit testing.
