# System Architecture Description
**Layered Engineering Design and Evolutionary Trajectory**  
*Document Research Assistant Agent — Linkific AI/ML Internship Day 18*

---

## 1. System Overview & Design Philosophy
The Document Research Assistant Agent is engineered to provide modular, explainable, and working and verifiable intelligent search capabilities. It is designed around three architectural pillars:
1. **Separation of Concerns:** Rigid decoupling between planning logic (`planner.py`), short-term working state (`memory.py`), tool execution dispatch (`tools.py`), and orchestration (`agent.py`).
2. **First-Principles Transparency:** Avoids opaque orchestration frameworks (LangChain, CrewAI), ensuring every state change is strictly governed by inspectable Python classes and Pydantic schemas.
3. **Deterministic Safety:** Mitigates hallucinations through strict boundary gating, mathematical relevance scoring, mathematical relevance scoring, and verifiable source attribution.

---

## 2. Detailed Architectural Layer Breakdown

```
┌────────────────────────────────────────────────────────────────────────┐
│                   LAYER 1: PRESENTATION & CLIENT                       │
│ - Antigravity Interactive CLI Runner                                   │
│ - Automated PyTest Verification Harness                                │
│ - Proposed REST API Gateway (FastAPI)                                  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│               LAYER 2: AGENT CORE & STATE ORCHESTRATION                │
│ - DocumentResearchAgent (Controller)                                   │
│ - AgentState Enum (INITIALIZED, PLANNING, ACT, OBSERVE, DECIDE, FINAL) │
│ - AgentMemory (Short-term Trace Buffer, Context Cache, Source Tracker) │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                 LAYER 3: PLANNING & REASONING ENGINE                   │
│ - Planner: Stopword Filtering & Substantive Token Isolation            │
│ - Intent Classifier: Search, Lookup, Metadata, Out-of-Domain           │
│ - ExecutionPlan & PlanStep Generator (Deterministic Ordered Lists)     │
│ - Decision Evaluator: Relevance Score Thresholding & Refinement Gating │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│               LAYER 4: TOOL EXECUTION & DISPATCH ENGINE                │
│ - ToolRegistry: Safe Invocation Wrapper & Exception Isolation          │
│ - document_search: Semantic Chunk Matcher with Heading Weighting       │
│ - document_lookup: Direct Document Fetcher by Primary Key (DOC-*-*)    │
│ - document_metadata: Catalog Inspector (Author, Version, Category)     │
│ - final_response: Grounded Sentence Extractor & Citation Formatter     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│               LAYER 5: SYNTHETIC ENTERPRISE KNOWLEDGE BASE             │
│ - KnowledgeBaseLoader: In-Memory Caching & Document Parsing            │
│ - DOC-LEAVE-001: Leave, Attendance, and Working Schedule Policy        │
│ - DOC-ONBOARD-002: Intern Onboarding & Technical Environment Setup     │
│ - DOC-TRAIN-003: Training Curriculum & Submission Guidelines           │
│ - DOC-WORKFLOW-004: 5-Stage ML Project Lifecycle & QA Guidelines       │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Evolutionary Progression: Day 16 $\rightarrow$ Day 17 $\rightarrow$ Day 18

```
┌─────────────────────────────────────────────────────────────────────────┐
│ DAY 16: Passive Vector Retrieval (ChromaDB + all-MiniLM-L6-v2)         │
│ - Input: Query string                                                   │
│ - Action: Embed query -> cosine similarity search -> return raw chunks  │
│ - Limitation: Cannot evaluate if chunks answer the question             │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ DAY 17: Production REST API (FastAPI + Multipart Document Processing)  │
│ - Input: Multipart PDF/TXT upload + Question endpoint                   │
│ - Action: Parse, chunk, metadata tagging, API validation, 10MB limits   │
│ - Limitation: Static request-response cycle; cannot refine or plan      │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ DAY 18: AI Agent Prototype (ReAct-Inspired) (ReAct + Tool Calling + Planning)     │
│ - Input: Complex or ambiguous natural language goal                     │
│ - Action: Formulates multi-step plan -> Selects specialized tool ->    │
│           Observes outcome -> Evaluates sufficiency -> Refines search   │
│ - Result: Grounded answer with source citations and full audit trace    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Proposed Integration Architecture for Company Project
In the full Linkific production architecture:
1. **Document Ingestion:** The Day 17 FastAPI service receives new company policy documents and technical guides.
2. **Vector Indexing:** The Day 16 indexing pipeline chunks documents, generates dense embeddings, and stores them in ChromaDB.
3. **Agentic Serving:** When a user poses a question in the company portal, the Day 18 `DocumentResearchAgent` coordinates `document_search` (backed by ChromaDB), inspects metadata, checks sufficiency, and returns verified operational answers.
