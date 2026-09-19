# Limitations & Future Architectural Improvements
**Current Constraints and Production Engineering Roadmap**  
*Document Research Assistant Agent — Linkific AI/ML Internship Day 18*

---

## 1. Objective Assessment of Current Implementation
The Day 18 prototype demonstrates complete agentic control flow, planning, tool dispatch, and ReAct state transitions from first principles. However, as an educational and prototype milestone, it operates under defined technical boundaries. This document transparently articulates those constraints and provides an actionable enterprise roadmap for future iterations.

---

## 2. Current Implementation Limitations

| Subsystem | Current State (Day 18 Prototype) | Operational Limitation |
| :--- | :--- | :--- |
| **Reasoning Engine** | Deterministic heuristic rules and keyword/regex classifiers. | Cannot interpret subtle linguistic nuances, sarcasm, or highly ambiguous queries. |
| **Retrieval Engine** | Tokenized term-frequency overlap with heading bonuses. | Lacks dense semantic vector similarity for synonyms (e.g., matching "vacation" to "leave" without explicit rules). |
| **Memory Architecture** | Single-session, in-memory `AgentMemory`. | Context is lost upon process termination; cannot maintain conversational history across days. |
| **Agent Topology** | Single monolithic agent. | A single agent handles all document categories, rather than specialized domain subagents. |
| **Tool Set** | 4 discrete internal tools. | Cannot query external APIs, send Slack notifications, or trigger email tickets. |
| **Concurrency** | Synchronous execution model. | Multiple sub-queries cannot be dispatched simultaneously. |

---

## 3. Production Engineering Roadmap

### Milestone 1: Dense Vector Hybrid Retrieval
- **Enhancement:** Replace the pure term-frequency matcher in `document_search` with a hybrid BM25 + dense embedding model (e.g., ChromaDB with `all-MiniLM-L6-v2` developed in Day 16).
- **Benefit:** Enables semantic synonym resolution, matching "taking time off" directly to `DOC-LEAVE-001`.

### Milestone 2: Multi-Turn Conversational Memory
- **Enhancement:** Implement persistent session memory using a Redis or PostgreSQL state store.
- **Benefit:** Allows users to ask follow-up questions (e.g., *"How many days are allowed for that?"*) with full antecedent resolution.

### Milestone 3: Multi-Agent Collaboration Swarm
- **Enhancement:** Decompose the single agent into specialized role-based subagents:
  - `PolicyAgent`: Specializes in HR and administrative guidelines.
  - `DevOpsAgent`: Specializes in onboarding, Git, and environment issues.
  - `CurriculumAgent`: Specializes in daily training tasks and milestones.
  - `SupervisorAgent`: Routes user goals to the optimal specialist subagent.

### Milestone 4: Production FastAPI Integration
- **Enhancement:** Mount the agent into Day 17's FastAPI app (`POST /api/v1/agent/query`).
- **Benefit:** Exposes Server-Sent Events (SSE) or WebSockets to stream intermediate ReAct thoughts and tool actions in real time to client frontends.

### Milestone 5: Human-in-the-Loop (HITL) Fallback
- **Enhancement:** When `DECIDE` determines that confidence is below 0.20, automatically generate an escalated support ticket in Jira/Slack for a human mentor.
