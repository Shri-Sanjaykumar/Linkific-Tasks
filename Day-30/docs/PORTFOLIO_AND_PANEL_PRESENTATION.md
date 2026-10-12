# Final Practical — Multi-Stakeholder Presentation & Portfolio Guide

**Presenter:** Shri Sanjaykumar V (`M.Tech Integrated in Software Engineering, VIT Vellore — CGPA: 9.12/10.0`)  
**Audience Tracks:**  
1. **Mentors** (*Focus: Engineering Growth, Code Review Responsiveness, Clean UI/UX & End-to-End Polish*)  
2. **Team Members** (*Focus: Modularity, REST API Contracts, Pydantic Schemas, Testing & Git Workflow*)  
3. **Technical Panel** (*Focus: 7-D Isolation Forest Math, Perturbation XAI, Pre-Inference PII Shield, Complexity & Scalability*)

---

## 1. Tailored Presentation Strategy by Audience (12–15 Minute Structure)

### Track A: Presenting to **Mentors** (3–4 Minutes)
- **Narrative Hook:** Connect my real-world experience as **Purchase Manager for VIT's Riviera & Gravitas festivals** (managing INR 60+ lakhs in purchase orders and vendor settlements) to why I built `FinDoc-AuditEngine v3.0`.
- **Key Evolution to Highlight (Day 26 -> Day 30):**
  1. **Code Review Refactoring (Day 28):** Eliminated hardcoded configs, added custom exception hierarchy (`FinDocAuditError`), and enforced PEP 8 modularity.
  2. **Institutional Editorial UI & 100% Dynamic Execution (Day 29–30):** Replaced generic dark-mode templates with an institutional light accounting grid (`Plus Jakarta Sans` + `IBM Plex Mono` tabular numerals) and re-engineered `collectLineItemsFromDOM()` so every single SKU rate, quantity, and dock rejection is dynamically computed from live user inputs.
- **Live Action:** Click **"Run All 5 Scenarios (Batch)"** or **"Random Invoice"** in the live workbench at `http://127.0.0.1:8000` to demonstrate instant dual-currency (`1 USD = 86.50 INR`) reconciliation.

### Track B: Presenting to **Team Members** (3–4 Minutes)
- **Focus Areas:** Developer ergonomics, clean separation of concerns (`app/core`, `app/services`, `app/routers`), and zero-regression CI/CD.
- **Key Engineering Patterns to Show:**
  1. **Strict API Contracts (`app/models.py`):** Pydantic v2 `@model_validator(mode="after")` rejects mathematically inconsistent invoices (`HTTP 422`) before they ever reach business logic.
  2. **Observability Middleware (`app/main.py`):** Every HTTP response carries `X-Correlation-ID` and `X-Process-Time-Ms`, and every audit response embeds a `StageTimingTelemetry` breakdown (`pii_scrub_ms`, `reconciliation_ms`, `ml_inference_ms`, `governance_routing_ms`).
  3. **30-Test Automated PyTest Suite (`tests/`):** Runs in `< 5 seconds` via `python -m pytest tests/ -v` and GitHub Actions (`.github/workflows/ci.yml`).

### Track C: Presenting to the **Technical Panel** (5–7 Minutes + Q&A)
- **Focus Areas:** Algorithmic depth, mathematical rigor, security/privacy architecture, and production scaling.
- **Deep Technical Talking Points:**
  1. **Why Hybrid Rules + Unsupervised ML?** Rules (`ReconciliationMatcher`) have $100\%$ precision on known contract violations ($\Delta P_i$, $Q_{\text{net}, i}$), while our 7-D `StandardScaler` + 200-tree `IsolationForest` (`AnomalyScorer`) catches zero-day statistical anomalies (such as `$49,500` round-dollar offshore invoices just under the `$50k` CFO limit with `Net-1` rush terms) even when the PO matches.
  2. **How Real-Time Perturbation XAI Works:** Instead of returning an opaque anomaly score, `assess_risk()` computes the marginal risk drop $\Delta R_k(\mathbf{x}) = \max(0, R(\mathbf{x}) - R(\mathbf{x}^{(k \leftarrow \mu_k)}))$ when each feature $k$ is clamped to its historical normal baseline $\mu_k$. Because $D=7$ is compact, all 8 forward passes execute in **`~7.9 ms`** on CPU without external explainer dependencies.
  3. **Pre-Inference Responsible AI Gate:** `FinancialPrivacyScrubber` executes at Stage 1 (`~0.3 ms`), replacing PAN, Aadhaar, Bank Account, Credit Card, Phone, and Email tokens with deterministic surrogates (`[PAN_01]`, `[EMAIL_02]`) so raw PII never enters logs or model vectors.

---

## 2. Live Technical Discussion — Top 5 Panel Rapid-Fire Prompts

| Panel Question | Concise, High-Impact Engineering Answer |
| :--- | :--- |
| **"Show us that your UI and ML model are truly dynamic and not returning fixed preset outputs."** | *"In the live workbench (`http://127.0.0.1:8000`), I can edit any line item's Invoice Rate vs. PO Contract Rate or Dock Rejected quantity, or click **Random Invoice**. As soon as I change SKU #1's Invoice Rate from `$2,100` to `$2,450` and add `1` rejected dock unit, `ReconciliationMatcher` computes the exact dollar variance (`$900.00`), and `AnomalyScorer` dynamically recalculates the 7-D Isolation Forest score (`97.7/100`) and Perturbation XAI bars (`Unit Rate Markup Ratio: +39.3 pts`, `Dock GRN Shortage Ratio: +31.2 pts`)."* |
| **"Why did you apply $\ln(1 + \text{Total}_{\text{USD}})$ and `StandardScaler` before `IsolationForest`?"** | *"While tree splits are invariant to monotonic scaling of a single feature, `IsolationForest` selects features uniformly at random and draws split thresholds uniformly between feature min and max. Compressing heavy-tailed invoice amounts with $\ln(1+x)$ and normalizing all 7 features via `StandardScaler` prevents extreme dollar outliers from masking subtle multi-dimensional interactions."* |
| **"How do you prevent floating-point rounding bugs in dual-currency USD/INR financial math?"** | *"We round line-item products to 2 decimal places (`round(qty * price, 2)`), enforce a `SUBTOTAL_TOLERANCE = 0.05` (`$0.05`) in both Pydantic v2 validation and 3-way reconciliation, and compute INR deterministically at `round(usd * 86.50, 2)`."* |
| **"What happens if a vendor submits an unstructured email memo instead of structured JSON?"** | *"Our `POST /api/v1/audit/parse-raw` endpoint runs `FinancialPrivacyScrubber.scrub_text()` first—redacting PAN, Aadhaar, account, phone, and email tokens—and extracts the Invoice ID, PO Number, Vendor Name, Jurisdiction, and USD Amount directly into the structured workbench."* |
| **"How would you scale this from a single FastAPI node to 10,000 invoices per minute?"** | *"Every service class (`FinancialPrivacyScrubber`, `ReconciliationMatcher`, `AnomalyScorer`, `ApprovalRouter`) is stateless at request time. We scale horizontally behind Gunicorn/Uvicorn workers on Kubernetes, move `AUDIT_LEDGER` to partitioned PostgreSQL (`asyncpg`) + Redis idempotency cache, and vectorize the 8 XAI perturbation vectors into a single `(8, 7)` NumPy batch call to `decision_function()`."* |

---

## 3. Master Portfolio Index (GitHub Repositories)

1. **Primary Internship & Capstone Repository:** [`https://github.com/Shri-Sanjaykumar/Linkific-Tasks`](https://github.com/Shri-Sanjaykumar/Linkific-Tasks)
   - [`Day-28/`](https://github.com/Shri-Sanjaykumar/Linkific-Tasks/tree/main/Day-28) — PR Workflow, Code Review Report & Refactored `FinDoc-AuditEngine`
   - [`Day-29/`](https://github.com/Shri-Sanjaykumar/Linkific-Tasks/tree/main/Day-29) — Institutional Editorial Light UI, 10 Technical Interview Q&As, 12-Slide Deck & Demo Suite
   - [`Day-30/`](https://github.com/Shri-Sanjaykumar/Linkific-Tasks/tree/main/Day-30) — Final Capstone Portfolio Hub, 2–3 Page Reflection Report, Updated Resume (PDF + MD), LinkedIn Guide, 90-Day Roadmap & 30/30 PyTest Suite
2. **Structured Python AI/ML Mirror Repository:** [`https://github.com/Shri-Sanjaykumar/AI-ML-Internship`](https://github.com/Shri-Sanjaykumar/AI-ML-Internship)
