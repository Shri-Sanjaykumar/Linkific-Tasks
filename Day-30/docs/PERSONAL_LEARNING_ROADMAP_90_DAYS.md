# Personal Learning Roadmap — Next 90 Days (Post-Internship Development Plan)

**Candidate:** Shri Sanjaykumar V (`M.Tech Integrated in Software Engineering, VIT Vellore`)  
**Current Baseline (End of Day 30):** Completed the `FinDoc-AuditEngine v3.0` working prototype (FastAPI, Pydantic v2, deterministic 3-way reconciliation, regex PII masking, 7-feature synthetic-baseline `IsolationForest` with perturbation attribution, and PyTest suite).  
**90-Day Goal:** Systematically address the current prototype's limitations (persistence, authentication, real-world ML evaluation/calibration, optical OCR, and asynchronous scaling) while strengthening core Software & AI Engineering fundamentals.

---

## Month 1 (Days 1–30): Durable Persistence, API Security & Document OCR

| Week | Days | Focus Area | Concrete Learning & Implementation Tasks | Measurable Weekly Target |
| :--- | :--- | :--- | :--- | :--- |
| **Week 1** | Days 1–7 | **Relational Persistence (`PostgreSQL` + `SQLAlchemy 2.0` + `Alembic`)** | Replace the prototype's in-memory `AUDIT_LEDGER` Python list with persistent PostgreSQL tables (`invoices`, `purchase_orders`, `audit_decisions`) and schema migrations. | Working async CRUD layer where audit history survives server restarts; verified by integration tests. |
| **Week 2** | Days 8–14 | **Idempotency, Caching & Concurrency (`Redis`)** | Add Redis-backed idempotency keys (`X-Idempotency-Key`) and sliding-window velocity counters to detect duplicate or split-invoice submissions. | Benchmark concurrent requests using `locust` or `httpx.AsyncClient` with zero duplicate ledger writes. |
| **Week 3** | Days 15–21 | **API Security (`OAuth2 / JWT`, RBAC & Rate Limiting)** | Implement user authentication and role-based access control (`Auditor`, `Finance_Manager`, `Director`) to secure approval endpoints and ledger exports. | Protected API routes with unit tests verifying `401 Unauthorized` and `403 Forbidden` role boundaries. |
| **Week 4** | Days 22–30 | **Optical OCR & Context-Aware PII Redaction (`Tesseract / LayoutLM` & `Presidio`)** | Upgrade `/api/v1/audit/parse-raw` from regex-only text parsing to actual PDF/image OCR table extraction, and pair regex PII rules with Named Entity Recognition (NER). | End-to-end sample PDF invoice ingestion test extracting line items and masking names/addresses. |

---

## Month 2 (Days 31–60): Rigorous ML Evaluation, Calibration, MLOps & Containerization

| Week | Days | Focus Area | Concrete Learning & Implementation Tasks | Measurable Weekly Target |
| :--- | :--- | :--- | :--- | :--- |
| **Week 5** | Days 31–37 | **Benchmarking on Public Financial Anomaly Datasets & Score Calibration** | Evaluate `IsolationForest`, `LocalOutlierFactor`, and `XGBoost` on public labeled fraud/anomaly datasets; study Platt scaling and isotonic regression for probability calibration. | Reproducible evaluation notebook reporting ROC-AUC, PR-AUC, and Brier score calibration curves. |
| **Week 6** | Days 38–44 | **Experiment Tracking & Model Registry (`MLflow`)** | Log model hyperparameters, `StandardScaler` artifacts, feature medians, and evaluation metrics in `MLflow` instead of fitting on synthetic data at app startup. | Versioned model artifact loaded deterministically from an `MLflow` registry path at startup. |
| **Week 7** | Days 45–52 | **Data Drift Monitoring (`EvidentlyAI` & Population Stability Index)** | Build a scheduled drift evaluation script that computes PSI and Kolmogorov-Smirnov statistics across the 7 input features over time. | Automated HTML/JSON drift report flagging simulated distribution shifts ($\text{PSI} > 0.20$). |
| **Week 8** | Days 53–60 | **Code Coverage (`pytest-cov`), Docker Multi-Stage Builds & CI Gates** | Measure actual line and branch coverage using `pytest-cov`, containerize the FastAPI + PostgreSQL stack with `docker-compose`, and enforce coverage checks in GitHub Actions. | Verified `pytest --cov=app` report (`>= 85%` measured line coverage) running automatically on every PR. |

---

## Month 3 (Days 61–90): Hybrid RAG, Asynchronous Workflows & Interview Readiness

| Week | Days | Focus Area | Concrete Learning & Implementation Tasks | Measurable Weekly Target |
| :--- | :--- | :--- | :--- | :--- |
| **Week 9** | Days 61–67 | **Hybrid Retrieval (`BM25 + Dense Vector Search`) & Evaluation (`RAGAS`)** | Combine keyword search (`BM25`) with vector embeddings (`Qdrant` / `pgvector`) to retrieve procurement policy clauses for flagged invoices; measure faithfulness. | Policy-grounded explanation module evaluated on a 30-question test set. |
| **Week 10** | Days 68–75 | **Asynchronous Task Queues (`Celery` / `RabbitMQ`)** | Offload batch invoice processing and report generation to background worker queues with retry and dead-letter handling. | Async batch audit endpoint with job-status polling (`PENDING -> COMPLETED`). |
| **Week 11** | Days 76–82 | **Data Structures, Algorithms & Backend System Design** | Practice 45+ medium/hard DSA problems (graphs, heaps, dynamic programming) and review 4 core system design architectures. | Documented system design notes and timed coding problem solutions. |
| **Week 12** | Days 83–90 | **Portfolio Consolidation & Mock Technical Interviews** | Conduct full mock technical interviews covering all projects (`FinDoc-AuditEngine`, `LEGITIFY`, `CampusLLM`, `FinTrack`, `Solar Forecasting`), refine documentation, and finalize applications. | Clean, reproducible GitHub portfolio with verified READMEs and architecture guides. |
