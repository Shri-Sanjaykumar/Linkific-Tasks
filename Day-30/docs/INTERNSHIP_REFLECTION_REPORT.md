# Comprehensive Internship Reflection Report (Days 1–30)

| Metadata Field | Verified Details |
| :--- | :--- |
| **Candidate Name** | **Shri Sanjaykumar V** |
| **Academic Institution** | Vellore Institute of Technology (VIT), Vellore — M.Tech Integrated in Software Engineering (CGPA: 9.12 / 10.0) |
| **Internship Organization** | **Linkific** — AI / Machine Learning Software Engineering Internship |
| **Capstone Prototype** | **FinDoc-AuditEngine v3.0** — Financial Document Reconciliation, Regex PII Masking & Explainable Anomaly Scoring Prototype |
| **Verified Test Results** | **Day 29:** `28 passed` (`python -m pytest tests -q`) • **Day 30:** `33 passed` (`python -m pytest tests -q`) — *all collected tests passed* |

## 1. Executive Summary of the 30-Day Internship Journey

Over the course of this 30-day AI/ML Software Engineering Internship at **Linkific**, my most important professional transition was moving from writing isolated machine-learning scripts to engineering a cohesive, validated, and transparently documented software prototype. Rather than treating data cleaning, anomaly detection, privacy protection, and API design as disconnected exercises, the curriculum guided me through building modular building blocks that culminated in **FinDoc-AuditEngine v3.0**.

Drawing practical inspiration from my role as **Purchase Manager for VIT's Riviera & Gravitas festivals**—where I coordinated procurement and sponsorship deliverables exceeding **INR 60+ Lakhs**—and my prior Generative AI internship at **TForce India Private Limited**, I focused the capstone project on Accounts Payable (AP) invoice auditing. Specifically, the prototype demonstrates how four distinct layers collaborate in a single FastAPI request lifecycle:
- **Stage 1 (Pre-Inference Regex Privacy Masking):** Masks 6 configured financial PII patterns (Indian Tax PAN, 12-digit Aadhaar format, bank account numbers, credit cards, phone numbers, and email addresses) into indexed surrogate tokens prior to downstream processing.
- **Stage 2 (Deterministic 3-Way Line-Item Reconciliation):** Enforces configured SKU-level unit-price ($0.01 tolerance) and Goods Receipt Note (GRN) net accepted quantity rules across Vendor Invoices, Purchase Orders (PO), and warehouse dock logs.
- **Stage 3 (7-Feature Unsupervised Anomaly Scoring & Local Perturbation Attribution):** Evaluates a 7-dimensional feature vector using `StandardScaler` and a 200-tree `IsolationForest` trained on a reproducible seeded synthetic baseline (`N=1,000, random_state=42`), paired with single-feature perturbation explanations.
- **Stage 4 (5-Tier Governance Routing & In-Memory Prototype Ledger):** Assigns each audited transaction to one of five governance queues and records the result in an in-memory Python list (`AUDIT_LEDGER`) with dual-currency USD/INR display (`1 USD = 86.50 INR`) and CSV export.

## 2. Complete 30-Day Technical Progression Matrix

| Training Phase | Days | Core Technical Focus | Key Deliverables & Engineering Outcomes |
| :--- | :--- | :--- | :--- |
| **Phase I: Software & Data Foundations** | Days 1–5 | Python Type Hints, Modular OOP, NumPy Vectorization, Pandas Data Cleaning, EDA | Built structured data preprocessing scripts, statistical outlier handlers, summary dashboards, and reproducible CLI entry points. |
| **Phase II: Classical Machine Learning** | Days 6–12 | Regression, Classification, Model Evaluation (Precision, Recall, F1, ROC-AUC), Unsupervised `IsolationForest` | Practiced strict train/test separation, feature scaling (`StandardScaler`), tree ensembles, and anomaly scoring on tabular datasets. |
| **Phase III: NLP & Document Extraction** | Days 13–15 | Tokenization, TF-IDF, Transformer Embeddings, Hugging Face Pipelines, Regex Entity Parsing | Implemented sentiment analysis pipelines, comparative LLM inference benchmarks, and regex-based structured field extraction. |
| **Phase IV: RAG & Multi-Agent Systems** | Days 16–23 | ChromaDB, FAISS, FastAPI RAG Service, ReAct Agents, Stateful LangGraph Workflows | Built sliding-window document chunkers, grounded QA microservices, multi-tool function calling, and 5-agent LangGraph pipelines. |
| **Phase V: Production & Responsible AI** | Days 24–26 | Rate Limiting, Structured Logging, Docker, Multi-Provider Cost Routing, Privacy Guardrails | Engineered sliding-window rate limiters, correlation-ID telemetry middleware, SLA cost calculators, and regex PII redaction gates. |
| **Phase VI: Capstone & Technical Review** | Days 27–30 | **FinDoc-AuditEngine v3.0**, Code Review Refactoring, Widescreen Slides, Video & Portfolio | Integrated the 4-stage AP audit prototype, refined the institutional light UI, recorded the demo video, and verified all collected PyTests (`28 passed` / `33 passed`). |

<!-- PAGE_BREAK -->
## 3. Deep-Dive into Technical Skills Acquired

1. **Architecting Hybrid Deterministic + Statistical Pipelines:**
   - Learned why financial auditing benefits from separating exact contractual rules from statistical anomaly detection. Deterministic rules (`ReconciliationMatcher`) reliably catch explicit SKU price overcharges and dock shortages, whereas unsupervised anomaly scoring (`AnomalyScorer`) highlights unusual multi-feature combinations (such as an offshore vendor billing $49,500 with Net-1 rush payment terms) even when the invoice matches its PO on paper.
2. **Understanding Synthetic Baselines vs. Calibrated Production Models:**
   - Designed a reproducible seeded synthetic generator (`N=1,000, random_state=42`) to fit the prototype's 7-feature `IsolationForest` (`log_total_usd`, `price_variance_ratio`, `qty_shortage_ratio`, `tax_rate_deviation`, `line_item_concentration`, `jurisdiction_risk_weight`, `payment_urgency_index`).
   - Implemented local single-feature perturbation attribution (`Delta R_k(x) = max(0, R(x) - R(x^(k <- mu_k)))`) to show which features contributed most to an elevated anomaly score.
   - Most importantly, learned to distinguish an **engineered 0–100 anomaly-risk indicator** fit on a synthetic baseline from a **calibrated fraud probability** validated on historical enterprise data.
3. **Defensive API Engineering with FastAPI & Pydantic v2:**
   - Applied Pydantic v2 cross-field validators (`@model_validator(mode='after')`) to verify that line-item subtotals multiplied by `(1 + tax_rate)` match `total_amount_usd` within a `$0.05` floating-point tolerance before business logic executes.
   - Built a structured domain exception hierarchy (`FinDocAuditException`) returning standardized JSON error payloads with `X-Correlation-ID` headers.
4. **Regex-Based Privacy Masking & Scope Awareness:**
   - Implemented `FinancialPrivacyScrubber` in `app/core/privacy.py` using 6 compiled regex patterns (PAN, Aadhaar format, Bank Account, Credit Card, Phone, Email), and documented both what regex masking solves and where context-aware Named Entity Recognition (NER) is needed in production.

## 4. Major Engineering Challenges Overcome

| Challenge Encountered | Root Cause Identified | Implemented Engineering Solution |
| :--- | :--- | :--- |
| **1. Frontend Table Edits Not Affecting Backend Audit** | Early UI iterations submitted the static preset PO line-item array instead of reading edited table cells from the DOM. | Wrote `collectLineItemsFromDOM()` in `dashboard.js` to build separate `InvoicePayload` and `PurchaseOrderRecord` item arrays directly from live HTML `<input>` cells, verified by a multi-line PyTest regression test. |
| **2. Heavy-Tailed Dollar Amounts Skewing Tree Splits** | Raw USD invoice totals ($432 to $49,500) spanned orders of magnitude compared to bounded ratios (`0.0–1.0`). | Applied logarithmic compression `ln(1 + Total_USD)` to feature `F1` and standardized all 7 features with `StandardScaler` prior to fitting `IsolationForest`. |
| **3. Binary Floating-Point Tax Rounding Errors** | IEEE 754 floating-point multiplication (`qty * price * 1.18`) produced sub-cent discrepancies on multi-SKU invoices. | Enforced two-decimal rounding (`round(x, 2)`) at line-item boundaries and configured a `$0.05` `SUBTOTAL_TOLERANCE` across Pydantic validation and 3-way matching. |
| **4. Test-Count & Documentation Drift** | Adding new route verification tests increased collected test counts (`28 passed` in Day 29, `33 passed` in Day 30), outdating earlier screenshots. | Audited every README, slide, PDF report, and terminal screenshot to report exact verified `python -m pytest tests -q` outputs and accurate prototype scope. |

## 5. Honest Assessment of Prototype Scope & Limitations

> **Engineering Transparency Principle:** Credible software engineering requires clearly separating what the current working prototype implements today from what a hardened production deployment would require.

- **In-Memory Prototype Audit Ledger (`AUDIT_LEDGER`):** Audit records are currently stored in an in-memory Python list for fast demonstration and CSV export. Records are non-persistent across server restarts and do not yet enforce database-level immutability or concurrent write locks.
- **Reproducible Synthetic ML Baseline (`N=1,000`):** The `IsolationForest` is trained at startup on a seeded synthetic dataset rather than historical Linkific company invoices. Production deployment would require evaluation, threshold calibration, and drift monitoring on authorized real-world data.
- **Regex Invoice-Text Parser (`/api/v1/audit/parse-raw`):** Parses unstructured plain-text invoice memos using regex patterns rather than an optical PDF/image OCR engine.

<!-- PAGE_BREAK -->
## 6. Core Professional & Technical Lessons Learned

1. **Defensible Technical Communication Matters as Much as Working Code:**
   - During the Day 29 and Day 30 review cycle, I learned that overstating a prototype as a "deployed production platform" or conflating test pass rate (`100% of collected tests passed`) with code coverage undermines technical trust. Presenting exact verified metrics (`28 passed` in Day 29; `33 passed` in Day 30) and stating architectural trade-offs candidly makes technical interviews far more effective.
2. **Code Review Discipline Improves Maintainability:**
   - Refactoring monolithic logic into focused service modules (`app/core/privacy.py`, `app/services/matcher.py`, `app/services/anomaly_detector.py`, `app/services/router.py`) with explicit type annotations and docstrings made debugging and extending the capstone straightforward.
3. **Visual Clarity Accelerates Stakeholder Understanding:**
   - Replacing decorative dark-mode styling with a high-contrast institutional light workbench (`Plus Jakarta Sans` + `IBM Plex Mono` tabular numerals) allowed mentors to inspect SKU price discrepancies, dock rejections, and perturbation risk bars at a glance.

## 7. Summary of the 90-Day Personal Learning Roadmap

To systematically bridge the gap between this internship prototype and production-scale AI/ML engineering over the next 90 days (detailed week-by-week in `PERSONAL_LEARNING_ROADMAP_90_DAYS.pdf`), I have structured a three-month development plan:

| Roadmap Phase | Focus Area | Concrete Engineering Projects & Verification Targets |
| :--- | :--- | :--- |
| **Month 1 (Days 1–30)** | **Durable Storage, Auth & Optical Document Parsing** | • Replace the in-memory `AUDIT_LEDGER` list with async **PostgreSQL (`SQLAlchemy 2.0 + asyncpg`)** and **Alembic** schema migrations.<br/>• Add **Redis** idempotency keys (`24h TTL`) to prevent duplicate invoice submissions.<br/>• Implement **OAuth2 / JWT** role-based access control and integrate optical PDF/image OCR (`Tesseract` / `LayoutLMv3`). |
| **Month 2 (Days 31–60)** | **Applied ML Calibration, MLOps & Coverage Gating** | • Benchmark `IsolationForest` against supervised gradient boosting (`XGBoost` / `LightGBM`) on public anomaly datasets.<br/>• Implement probability calibration (**Platt scaling / Isotonic regression**) and evaluate Precision-Recall AUC and Brier score.<br/>• Add **MLflow** model registry, **EvidentlyAI** Population Stability Index (PSI) drift checks, and `pytest-cov` (`>= 85%` line coverage) in GitHub Actions CI. |
| **Month 3 (Days 61–90)** | **Hybrid RAG, Stateful LangGraph Agents & System Design** | • Build a **Hybrid BM25 + Dense Vector** retrieval pipeline with cross-encoder reranking and automated **RAGAS** evaluation.<br/>• Orchestrate stateful human-in-the-loop dispute resolution workflows using **LangGraph** with persistent Postgres checkpointers.<br/>• Practice asynchronous task queues (**Celery / Kafka**) and complete 6 end-to-end backend/AI system design case studies. |

## 8. Pre-Submission & Public Sharing Checklist

- **Factual Consistency Verified:** Resume, LinkedIn profile guide, and portfolio overview use consistent dates (`Aug 2026 – Oct 2026` at Linkific; `May 2026 – Jul 2026` at TForce India Pvt Ltd) and verified VIT academic records (`CGPA: 9.12 / 10.0`).
- **Confidentiality & Sanitization Verified:** All code, sample invoices (`INV-1001` through `INV-1005`), and synthetic baseline records in `FinDoc-AuditEngine v3.0` use 100% synthetic vendor data with zero proprietary Linkific customer data or internal credentials.
