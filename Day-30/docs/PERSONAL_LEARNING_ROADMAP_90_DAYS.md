# 90-Day Personal Learning & Engineering Roadmap (Months 1–3)

| Roadmap Attribute | Specification |
| :--- | :--- |
| **Engineer** | **Shri Sanjaykumar V** (M.Tech Integrated in Software Engineering, VIT Vellore — CGPA: 9.12 / 10.0) |
| **Baseline Project** | **FinDoc-AuditEngine v3.0** (Working FastAPI Prototype — Day 29: `28 passed`, Day 30: `33 passed`) |
| **Primary Objective** | Transition prototype skills into production-grade persistence, calibrated ML evaluation, MLOps, and distributed backend engineering |

## Month 1 (Weeks 1–4 / Days 1–30): Durable Persistence, Security & Optical Document Extraction

*Goal: Address the core prototype limitations of `FinDoc-AuditEngine v3.0` by replacing in-memory state, adding authentication, and integrating true optical OCR.*

| Week | Focus Domain | Concrete Engineering Tasks | Measurable Weekly Deliverable |
| :--- | :--- | :--- | :--- |
| **Week 1 (Days 1–7)** | **Relational Persistence & Async ORM** | Replace the in-memory `AUDIT_LEDGER` Python list with **PostgreSQL** using `SQLAlchemy 2.0` (`asyncpg`) and **Alembic** schema migrations. Design normalized tables for `vendors`, `purchase_orders`, `grn_records`, `invoices`, and `audit_decisions`. | Containerized FastAPI + PostgreSQL service where audit records persist across server restarts. |
| **Week 2 (Days 8–14)** | **Idempotency, Concurrency & Caching** | Integrate **Redis** to enforce idempotency keys (`X-Idempotency-Key` with 24-hour TTL) so duplicate webhook submissions cannot create duplicate ledger entries, plus sliding-window vendor velocity counters. | Automated concurrency test suite verifying zero duplicate ledger writes under parallel requests. |
| **Week 3 (Days 15–21)** | **Authentication, RBAC & Cryptographic Integrity** | Implement **OAuth2 + JWT** role-based access control (`Auditor`, `Manager`, `Director`, `Admin` scopes) and SHA-256 hash-chaining (`prev_hash -> record_hash`) across PostgreSQL audit rows. | Protected API routes with role-based integration tests and tamper-evident ledger verification script. |
| **Week 4 (Days 22–30)** | **Optical OCR & Layout-Aware PDF Parsing** | Upgrade `/api/v1/audit/parse-raw` from regex text parsing to accept real PDF/image invoices using **Tesseract OCR** and layout-aware table extraction (`pdfplumber` / `LayoutLMv3`), plus context-aware NER (`Microsoft Presidio`). | End-to-end PDF upload endpoint extracting multi-line SKU tables with measured field-level F1 accuracy. |

<!-- PAGE_BREAK -->
## Month 2 (Weeks 5–8 / Days 31–60): Applied ML Evaluation, Calibration, MLOps & CI Quality Gates

*Goal: Move beyond synthetic baselines to rigorous model evaluation, probability calibration, drift monitoring, and reproducible container benchmarks.*

| Week | Focus Domain | Concrete Engineering Tasks | Measurable Weekly Deliverable |
| :--- | :--- | :--- | :--- |
| **Week 5 (Days 31–37)** | **Benchmarking on Public Financial Datasets** | Evaluate `IsolationForest`, `LocalOutlierFactor`, and supervised `XGBoost` / `LightGBM` on public tabular anomaly datasets (e.g., IEEE-CIS / Credit Card Fraud) using stratified cross-validation. | Reproducible evaluation notebook & report comparing ROC-AUC, PR-AUC, and Recall@K at fixed false-positive rates. |
| **Week 6 (Days 38–44)** | **Probability Calibration & SHAP Verification** | Apply **Platt Scaling** and **Isotonic Regression** (`CalibratedClassifierCV`) to convert raw anomaly scores into calibrated probabilities (evaluated via Brier score & reliability diagrams), and compare local perturbation against `TreeSHAP`. | Calibration module with reliability plots and quantitative fidelity comparison between Perturbation XAI and SHAP. |
| **Week 7 (Days 45–52)** | **MLflow Registry & Concept Drift Telemetry** | Track model hyperparameters, scaler artifacts, and threshold configs in **MLflow**. Implement weekly **Population Stability Index (PSI)** drift detection across all 7 features using **EvidentlyAI**. | Automated drift-check CLI that flags `PSI > 0.20` and triggers a candidate retraining workflow. |
| **Week 8 (Days 53–60)** | **Code Coverage Gating & Load Benchmarking** | Add `pytest-cov` (`>= 85%` line & branch coverage gate) to GitHub Actions CI, export models to **ONNX Runtime**, and run repeatable **Locust** load benchmarks documenting hardware specs and p50/p95/p99 latency. | Published benchmark report with verified p95 latency and CI badge enforcing test + coverage gates. |

## Month 3 (Weeks 9–12 / Days 61–90): Hybrid RAG, Stateful Agent Workflows & System Design

*Goal: Combine structured financial auditing with grounded document retrieval, stateful human-in-the-loop agents, and interview-ready system design.*

| Week | Focus Domain | Concrete Engineering Tasks | Measurable Weekly Deliverable |
| :--- | :--- | :--- | :--- |
| **Week 9 (Days 61–67)** | **Hybrid BM25 + Dense RAG & Reranking** | Build a procurement contract retrieval engine combining sparse **BM25** and dense vector embeddings (`bge-small-en`) via **Reciprocal Rank Fusion (RRF)** and cross-encoder reranking. | Contract QA API citing exact vendor Master Service Agreement (MSA) clauses alongside 3-way match results. |
| **Week 10 (Days 68–75)** | **Automated RAG Evaluation & Guardrails** | Integrate **RAGAS** / **DeepEval** to measure Context Precision, Faithfulness, and Answer Relevance on a 50-question procurement test set, plus input prompt-injection filters. | Automated evaluation pipeline verifying Faithfulness `>= 0.90` and zero ungrounded numerical claims. |
| **Week 11 (Days 76–82)** | **Stateful LangGraph Dispute Workflows** | Build a cyclic **LangGraph** workflow with persistent Postgres checkpointing (`PostgresSaver`) that drafts vendor discrepancy notices and pauses for human Manager/Director approval before dispatch. | Multi-turn human-in-the-loop agent demo with state resumption and audit logging. |
| **Week 12 (Days 83–90)** | **Async Task Queues & Interview Readiness** | Decouple heavy PDF/ML batch processing using **Celery + Redis / Kafka**, complete 60+ medium/hard DSA problems, and write 4 distributed AI/FinTech system design case studies. | Finalized public GitHub portfolio, system design handbook, and mock technical interview completion. |
