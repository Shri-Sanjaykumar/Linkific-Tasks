# Day 29 — Project Polish, Documentation, Presentation, Video & Testing (`FinDoc-AuditEngine v3.0`)

**Project Classification:** Internship Capstone Working Prototype / Production-Oriented Reference Implementation  
**Candidate:** Shri Sanjaykumar V (`M.Tech Integrated in Software Engineering @ VIT Vellore`)  
**Verified Automated Test Result:** **`28 passed`** (`python -m pytest tests -q` — *all 28 collected tests passed*)  
**Currency Display:** Dual-Currency USD (`$`) and INR (`1 USD = 86.50 INR` configured rate)

---

## 1. Business Problem & Prototype Solution

Enterprise Accounts Payable (AP) teams must reconcile vendor invoices against contractual Purchase Orders (POs) and physical warehouse Goods Receipt Notes (GRNs) while protecting sensitive tax/banking identifiers and flagging unusual payment requests.
- **Deterministic 3-Way Matching (`ReconciliationMatcher`):** Enforces configured SKU unit-price, net accepted dock quantity (`received - rejected`), and `$0.05` subtotal tolerance rules.
- **Pre-Inference Regex Privacy Masking (`FinancialPrivacyScrubber`):** Masks 6 configured identifier patterns (Indian PAN, 12-digit Aadhaar format, Bank Account keywords, Credit Card digits, Indian phone numbers, and Email addresses) prior to logging or scoring.
- **Unsupervised Anomaly Scoring (`AnomalyScorer`):** Uses a `StandardScaler` + 200-tree `IsolationForest` trained on a **reproducible seeded synthetic baseline of 1,000 transaction-like records** across 7 features, paired with single-feature perturbation attribution. *Note: The displayed `0–100` score is an engineered anomaly-risk indicator, not a calibrated probability of fraud; production use would require evaluation and calibration on authorized real-world data.*
- **Governance Router & In-Memory Prototype Ledger (`ApprovalRouter`):** Routes invoices into 5 approval queues and stores records in an **in-memory Python list (`AUDIT_LEDGER`)** for interactive demonstration and CSV export.

---

## 2. Day 29 Deliverables (All Included in `docs/`)

| Deliverable | File Path(s) | Description |
| :--- | :--- | :--- |
| **1. PowerPoint Slide Deck (`.pptx`)** | [`docs/FinDoc_AuditEngine_Presentation_Slides.pptx`](./docs/FinDoc_AuditEngine_Presentation_Slides.pptx) | Native 12-slide 16:9 PowerPoint presentation with visual cards and embedded speaker notes following the 10–12 minute structure. |
| **2. Landscape Slide Deck (`.pdf`) & Notes** | [`docs/FinDoc_AuditEngine_Slide_Deck.pdf`](./docs/FinDoc_AuditEngine_Slide_Deck.pdf)<br/>[`docs/PRESENTATION_NOTES_AND_SLIDES.md`](./docs/PRESENTATION_NOTES_AND_SLIDES.md)<br/>[`docs/PRESENTATION_NOTES_AND_SLIDES.pdf`](./docs/PRESENTATION_NOTES_AND_SLIDES.pdf) | Designed 16:9 widescreen PDF slide deck plus the 10–12 minute speaker script (`1m Problem -> 2m Architecture -> 5m 3-Scenario Demo -> 2m Testing -> 2m Limitations`). |
| **3. Recorded Demo Walkthrough Video (`.mp4`)** | [`docs/FinDoc_AuditEngine_Demo_Walkthrough.mp4`](./docs/FinDoc_AuditEngine_Demo_Walkthrough.mp4) | HD `1280x720` H.264 video walkthrough showing the web dashboard, 3 representative invoice scenarios (`INV-1001`, `INV-1004`, `INV-1005`), terminal logs, and `28 passed` test results. |
| **4. 10 Technical Interview Q&As** | [`docs/INTERVIEW_QA.md`](./docs/INTERVIEW_QA.md)<br/>[`docs/INTERVIEW_QA.pdf`](./docs/INTERVIEW_QA.pdf) | Covers architecture, why Isolation Forest was chosen, 7-D feature engineering, risk-score interpretation, 3-way matching, regex PII scope, error handling, testing, limitations, and scalability. |
| **5. Demo Practice Checklist** | [`docs/DEMO_PRACTICE_CHECKLIST.md`](./docs/DEMO_PRACTICE_CHECKLIST.md)<br/>[`docs/DEMO_PRACTICE_CHECKLIST.pdf`](./docs/DEMO_PRACTICE_CHECKLIST.pdf) | Pre-flight verification, 5-minute 3-scenario live demo script, and video walkthrough breakdown. |
| **6. Architecture & Limitations Document** | [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md)<br/>[`docs/ARCHITECTURE.pdf`](./docs/ARCHITECTURE.pdf) | 4-stage pipeline diagram, 7-feature math, and explicit table of current prototype limitations vs. planned production work. |

---

## 3. Setup, Demo & Testing Commands

```powershell
# 1. Navigate to Day-29
cd C:\projects\linkific\internship\Day-29

# 2. Run the Complete Automated Test Suite (Verified: 28 passed)
python -m pytest tests -q

# 3. Run the CLI Mentor Demo (3 Representative Scenarios + Batch + CSV Export)
python run_mentor_demo.py

# 4. Start the Web Workbench & Interactive Presentation Portal on http://127.0.0.1:8000
python run_server.py
```

---

## 4. REST API Endpoints Overview

| Method & Path | Description |
| :--- | :--- |
| `GET /` or `GET /dashboard` | Serves the Institutional Editorial Light Web Workbench & 4-Tab Mentor Demo Portal. |
| `GET /health` | Returns service health, configured FX rate (`86.50`), and active prototype component labels. |
| `POST /api/v1/audit/process` | Executes 4-stage audit (Regex PII Mask -> 3-Way Match -> 7-D Synthetic Baseline IF -> Governance Router). |
| `POST /api/v1/audit/parse-raw` | Regex-based invoice-text parser & PII scrubber for unstructured text memos. |
| `POST /api/v1/audit/demo-batch` | Runs the 5 benchmark scenarios (`INV-1001` to `INV-1005`) into the in-memory ledger. |
| `GET /api/v1/audit/export/csv` | Exports the current in-memory audit ledger as a downloadable CSV file. |
| `GET /api/v1/prep/slides` | Returns the 12 presentation slides and speaker notes for the interactive slide viewer. |
| `GET /api/v1/prep/interview-qa` | Returns the 10 technical interview Q&As. |
| `GET /api/v1/prep/download/{filename}` | Downloads `.pptx`, `.mp4`, `.pdf`, or `.md` deliverables from `docs/`. |

---

## 5. Current Prototype Limitations

1. **In-Memory Audit Ledger:** `AUDIT_LEDGER` is stored in a Python list in RAM and resets when the server restarts.
2. **Synthetic ML Baseline:** The `IsolationForest` is trained on 1,000 seeded synthetic records; real-world deployment requires retraining and threshold calibration on authorized historical invoices.
3. **Regex Parsing & Masking Scope:** `FinancialPrivacyScrubber` and `/api/v1/audit/parse-raw` rely on deterministic regular expressions rather than optical OCR or transformer NER.
