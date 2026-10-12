"""Day 29 & 30 Technical Presentation, 12-Slide Deck, 10 Interview Q&As, Demo Checklist & Video Script API."""

import os
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()
DOCS_DIR = Path(__file__).resolve().parent.parent.parent / "docs"

SLIDES_DECK = [
    {
        "slide": 1,
        "title": "FinDoc-AuditEngine v3.0 — Enterprise AP Reconciliation & Explainable ML Risk Gateway",
        "time_mark": "00:00 – 01:00",
        "section": "Title & Executive Overview",
        "bullets": [
            "Presenter: Shri Sanjaykumar V (M.Tech Integrated SWE @ VIT Vellore, CGPA: 9.12/10.0)",
            "Domain Inspiration: Managing INR 60+ Lakhs in procurement & sponsor purchase orders for VIT Riviera & Gravitas",
            "Core Mission: Eliminate manual Accounts Payable bottlenecks, vendor overbilling, and opaque black-box AI risk scoring",
            "Dual-Currency Institutional Standard: Real-time USD ($) and INR (pegged at 1 USD = 86.50 INR) ledger auditing",
        ],
        "speaker_notes": "Welcome mentors and panel members. Today I am presenting FinDoc-AuditEngine v3.0, an institutional Accounts Payable reconciliation and explainable ML risk gateway inspired by real procurement challenges.",
    },
    {
        "slide": 2,
        "title": "The Enterprise Accounts Payable Problem & Why Pure Rules or Pure LLMs Fail",
        "time_mark": "01:00 – 02:15",
        "section": "Problem Statement",
        "bullets": [
            "Pure Deterministic Rules Miss Statistical Fraud: An invoice can match a PO 100% yet come from an offshore tax haven demanding a 1-day wire just below the $50,000 CFO threshold.",
            "Pure LLMs / Black-Box ML Fail Financial Audits: Hallucinated arithmetic on floating-point tax rates and unexplainable risk scores violate SOX and internal audit standards.",
            "PII Exposure Risk: Raw vendor invoices contain Indian Tax PANs, Aadhaar numbers, IBANs, and emails that must never leak into logs or model weights.",
        ],
        "speaker_notes": "Enterprise finance teams face a dual challenge: static ERP rules miss statistical anomalies when a rogue PO matches an invoice, while pure LLMs struggle with exact floating-point arithmetic and regulatory explainability.",
    },
    {
        "slide": 3,
        "title": "4-Stage Hybrid Neuro-Symbolic Pipeline Architecture (< 15ms End-to-End)",
        "time_mark": "02:15 – 03:30",
        "section": "System Architecture",
        "bullets": [
            "Stage 1 — Pre-Inference PII Privacy Shield (~0.3 ms): Regex redaction of PAN, Aadhaar, Bank Account, Credit Card, Phone & Email into indexed surrogates ([PAN_01]).",
            "Stage 2 — Deterministic 3-Way Line-Item Matcher (~0.4 ms): SKU-by-SKU verification of Invoice vs. Purchase Order vs. Goods Receipt Note (GRN) with $0.05 tolerance.",
            "Stage 3 — 7-D Isolation Forest + Perturbation XAI (~7.9 ms): 200 isolation trees + StandardScaler + Single-Feature Perturbation Attribution.",
            "Stage 4 — 5-Tier Corporate Governance Router (~0.2 ms): Routes to Tier 1 STP, Tier 2 Manager, Tier 3 Director, Rejected Discrepancy, or Frozen Fraud Risk.",
        ],
        "speaker_notes": "Our architecture decouples deterministic arithmetic from statistical anomaly detection across four sequential, stateless stages instrumented with microsecond telemetry.",
    },
    {
        "slide": 4,
        "title": "Stage 1: Pre-Inference Responsible AI & Unstructured OCR Document Parser",
        "time_mark": "03:30 – 04:45",
        "section": "Privacy & Ingestion",
        "bullets": [
            "DPDP Act 2023 & GDPR Compliance: FinancialPrivacyScrubber executes BEFORE logging, ledger storage, or ML vectorization.",
            "6 High-Precision Compiled Regex Patterns: Masks PAN ([A-Z]{5}[0-9]{4}[A-Z]{1}), Aadhaar (12-digit), Bank Accounts, Credit Cards, Phones, and Emails.",
            "Dynamic Free-Text Parser (POST /api/v1/audit/parse-raw): Extracts Invoice ID, PO Number, Vendor, Country, and USD total from raw email/OCR memos while scrubbing PII.",
        ],
        "speaker_notes": "Before any invoice touches our matcher or ML model, Stage 1 strips six categories of financial PII and maps them to deterministic surrogates.",
    },
    {
        "slide": 5,
        "title": "Stage 2: Deterministic 3-Way Reconciliation Engine (Invoice vs. PO vs. GRN)",
        "time_mark": "04:45 – 06:00",
        "section": "3-Way Matching Math",
        "bullets": [
            "Contractual Unit Rate Check: Flags RATE_VARIANCE whenever P_inv,i - P_po,i > $0.01 per SKU.",
            "Dock GRN Net Quantity Check: Computes net accepted units Q_net,i = Q_received,i - Q_rejected,i and flags QTY_SHORTAGE if billed quantity exceeds Q_net,i.",
            "Pydantic v2 Fail-Fast Invariant: Cross-field @model_validator rejects invoices whose line-item sum * (1 + tax_rate) diverges from total_amount_usd by > $0.05.",
        ],
        "speaker_notes": "Stage 2 enforces zero-compromise accounting math. Every SKU is matched against its PO contract rate and physical warehouse Goods Receipt Note.",
    },
    {
        "slide": 6,
        "title": "Stage 3A: 7-Dimensional Feature Engineering & 200-Tree Isolation Forest",
        "time_mark": "06:00 – 07:30",
        "section": "Machine Learning Core",
        "bullets": [
            "7 Continuous Financial Features: (1) ln(1 + Total_USD), (2) Unit Rate Markup Ratio, (3) Dock GRN Shortage Ratio, (4) Tax Deviation from 18% GST, (5) Line Concentration, (6) Jurisdiction Risk Weight, (7) Payment Urgency Index.",
            "Why Log-Compression + StandardScaler: Prevents raw dollar totals ($50,000) from dominating bounded ratios (0.0–1.0) during random split threshold selection.",
            "Trained on 1,000 Realistic Historical Procurement Records (92% normal multi-tier AP traffic, 8% injected multi-vector anomalies).",
        ],
        "speaker_notes": "Even if an invoice matches its PO, our 7-dimensional Isolation Forest evaluates whether the transaction is statistically isolated in joint feature space.",
    },
    {
        "slide": 7,
        "title": "Stage 3B: Real-Time Explainable AI via Single-Feature Perturbation Attribution",
        "time_mark": "07:30 – 08:45",
        "section": "Explainable AI (XAI)",
        "bullets": [
            "Mathematical Formulation: Delta R_k(x) = max(0, R(x) - R(x^(k <- mu_k))) where mu_k is the historical normal baseline median for feature k.",
            "Human-Auditable Attribution Bars: Outputs exact point contributions (e.g., Unit Rate Markup Ratio: +39.3 pts, Dock GRN Shortage Ratio: +31.2 pts).",
            "Sub-8ms CPU Execution: Evaluates all 7 feature perturbations without heavy external SHAP C++ compilation bottlenecks.",
        ],
        "speaker_notes": "Auditors cannot block a vendor payment based on an unexplained number. Our perturbation XAI engine clamps each feature to its normal baseline to measure its exact marginal point contribution.",
    },
    {
        "slide": 8,
        "title": "Stage 4: 5-Tier Corporate Governance Routing & Dual-Currency Ledger",
        "time_mark": "08:45 – 09:45",
        "section": "Governance & Compliance",
        "bullets": [
            "Tier 1 STP Auto-Approved (<= $1,000, Matched, Risk < 38): Zero-touch straight-through disbursement.",
            "Tier 2 Manager Review ($1,000 – $10,000) & Tier 3 Director Sign-Off (> $10,000): Escalated human-in-the-loop (HITL) queues.",
            "Rejected Discrepancy & Frozen Fraud Risk (Risk >= 68 or Tax-Haven Anomaly): Automatic payment freeze + downloadable CSV compliance ledger.",
        ],
        "speaker_notes": "Stage 4 combines deterministic match flags with the calibrated ML risk score to route every invoice into one of five corporate governance queues.",
    },
    {
        "slide": 9,
        "title": "Institutional Editorial Light UI & 100% Dynamic DOM Execution",
        "time_mark": "09:45 – 11:00",
        "section": "UI/UX & Dynamic Frontend",
        "bullets": [
            "Swiss Accounting Grid Aesthetic: #F8FAFC stone canvas, #FFFFFF crisp panels, 1px solid #E2E8F0 hairline borders, Plus Jakarta Sans + IBM Plex Mono tabular-nums.",
            "Zero Static Scenario Coupling: collectLineItemsFromDOM() reads every SKU's Invoice Rate, PO Contract Rate, Billed Qty, GRN Received, and GRN Rejected live from DOM inputs.",
            "Interactive Capabilities: + Add Line Item, Random Realistic Invoice Synthesizer, Unstructured OCR Text Parser, and 1-Click 5-Scenario Batch Execution.",
        ],
        "speaker_notes": "Let's transition to the live workbench at localhost:8000. Notice the clean institutional light typography and how editing any cell dynamically recalculates 3-way variances and XAI bars.",
    },
    {
        "slide": 10,
        "title": "Testing, Reliability, Observability & CI/CD Verification (30/30 PyTests)",
        "time_mark": "11:00 – 12:00",
        "section": "Quality Assurance",
        "bullets": [
            "100% Automated PyTest Pass Rate: Unit tests for 3-way math, ML anomaly monotonicity, perturbation XAI, PII regexes, custom exceptions, and dynamic REST routes.",
            "Custom Exception Hierarchy (FinDocAuditError): Structured JSON error responses with HTTP status codes, correlation IDs, and RFC-3339 UTC timestamps.",
            "GitHub Actions CI/CD (.github/workflows/ci.yml): Automated lint and regression verification on every push.",
        ],
        "speaker_notes": "Every component is backed by our automated PyTest suite running in under 5 seconds, verifying both deterministic edge cases and ML risk monotonicity.",
    },
    {
        "slide": 11,
        "title": "Key Engineering Challenges Overcome During Days 1–30",
        "time_mark": "12:00 – 13:00",
        "section": "Challenges & Solutions",
        "bullets": [
            "1. Eliminating Frontend Scenario Coupling: Decoupled Invoice vs. PO line-item arrays in collectLineItemsFromDOM() for arbitrary real-world user inputs.",
            "2. Preventing Dollar Magnitude Dominance in Isolation Trees: Combined ln(1+x) compression with z-score StandardScaler.",
            "3. IEEE 754 Floating-Point Tax Precision: Applied two-decimal boundary rounding and a $0.05 subtotal tolerance invariant.",
        ],
        "speaker_notes": "Here are the three most critical engineering challenges we solved during development, from frontend DOM decoupling to multivariate tree scaling.",
    },
    {
        "slide": 12,
        "title": "90-Day Post-Internship Roadmap & Production Scaling Blueprint",
        "time_mark": "13:00 – 15:00 (Q&A)",
        "section": "Future Roadmap & Q&A",
        "bullets": [
            "Month 1 (Days 1–30): Hybrid BM25 + Dense RAG (Reciprocal Rank Fusion), LangGraph Dispute Agents & LayoutLMv3 PDF table extraction.",
            "Month 2 (Days 31–60): Async PostgreSQL (asyncpg) + Redis idempotency, MLflow + EvidentlyAI PSI drift monitoring & vectorized ONNX Runtime (<1.8ms).",
            "Month 3 (Days 61–90): Apache Kafka event-driven ingestion (10k invoices/min), OWASP LLM Top 10 AppSec hardening & Kubernetes HPA deployment.",
        ],
        "speaker_notes": "Looking ahead to the next 90 days, our roadmap scales FinDoc-AuditEngine to 10,000 invoices per minute using Kafka, async PostgreSQL, ONNX Runtime, and EvidentlyAI drift monitoring. Thank you—I now welcome questions from the panel.",
    },
]

INTERVIEW_QA_ITEMS = [
    {
        "id": "Q1",
        "category": "Architecture",
        "question": "Why did you design a hybrid architecture combining deterministic 3-Way Matching with an unsupervised Isolation Forest instead of using a single ML model or LLM?",
        "answer": "In regulated enterprise finance, known contractual violations (unit price overcharges or dock quantity shortages) require 100% deterministic mathematical precision down to $0.01—which probabilistic models cannot guarantee. Conversely, deterministic rules fail when a fraudulent or collusive invoice matches its PO on paper (e.g., an offshore shell vendor billing $49,500 just under the $50k CFO approval cap with Net-1 rush terms). Combining Stage 2 deterministic reconciliation with Stage 3 7-D Isolation Forest gives us 100% precision on contract breaches AND statistical zero-day anomaly detection.",
        "code_ref": "app/services/matcher.py & app/services/anomaly_detector.py",
    },
    {
        "id": "Q2",
        "category": "Machine Learning & Math",
        "question": "Why did you apply ln(1 + Total_USD) and StandardScaler before training the 200-tree IsolationForest?",
        "answer": "Although a single decision tree split is invariant to monotonic feature scaling, IsolationForest selects features uniformly at random and draws split thresholds uniformly between [min(X_j), max(X_j)]. Without log-compression on heavy-tailed dollar amounts ($100 to $100,000+) and z-score standardization (mu=0, sigma=1), extreme capital outliers skew path depths and mask subtle multi-feature anomalies across bounded ratios like price_variance_ratio and qty_shortage_ratio.",
        "code_ref": "app/services/anomaly_detector.py (lines 110–155)",
    },
    {
        "id": "Q3",
        "category": "Explainable AI (XAI)",
        "question": "How does your Single-Feature Perturbation Attribution (XAI) algorithm work, and why did you choose it over KernelSHAP?",
        "answer": "For any invoice vector x in R^7 with calibrated risk R(x), we iteratively construct 7 counterfactual vectors x^(k <- mu_k) where feature k is replaced by its historical normal baseline median mu_k. The marginal risk contribution is Delta R_k = max(0, R(x) - R(x^(k <- mu_k))). Because D=7 is compact, evaluating 8 forward passes takes ~7.9ms in pure NumPy/scikit-learn with zero C++ compilation issues on Windows/Linux containers, whereas KernelSHAP requires 2^7 = 128 coalitions.",
        "code_ref": "app/services/anomaly_detector.py (assess_risk)",
    },
    {
        "id": "Q4",
        "category": "Data Validation & Edge Cases",
        "question": "How do you prevent IEEE 754 floating-point rounding discrepancies from falsely rejecting valid multi-line tax invoices?",
        "answer": "In binary floating-point arithmetic, expressions like 3 * 19.99 * 1.18 produce 70.76460000000001. We enforce two-decimal rounding at line-item boundaries (round(qty * unit_price, 2)) and apply a deterministic SUBTOTAL_TOLERANCE = 0.05 ($0.05) in both our Pydantic v2 @model_validator(mode='after') and our 3-Way Matcher, preventing false-positive penny rejections while catching real tampering.",
        "code_ref": "app/models.py & app/core/config.py",
    },
    {
        "id": "Q5",
        "category": "Responsible AI & Security",
        "question": "Why is PII scrubbing executed at Stage 1 before ML inference, and how do you preserve auditability?",
        "answer": "To comply with India's DPDP Act 2023 and GDPR data-minimization mandates, raw PII (PAN, Aadhaar, Bank Account, Credit Card, Phone, Email) must never be written to application logs or passed into model pipelines. FinancialPrivacyScrubber replaces each match with an indexed surrogate token ([PAN_01], [EMAIL_02]) in ~0.3ms and returns the redaction count for governance telemetry.",
        "code_ref": "app/core/privacy.py (FinancialPrivacyScrubber)",
    },
    {
        "id": "Q6",
        "category": "Frontend-Backend Integration",
        "question": "How did you ensure the web workbench handles arbitrary real-world user inputs dynamically rather than relying on preset scenarios?",
        "answer": "We architected collectLineItemsFromDOM() in dashboard.js so every table row renders independent editable HTML inputs for SKU Code, Description, Invoice Rate ($), PO Contract Rate ($), Billed Qty, GRN Received, and GRN Rejected. On submission, the frontend constructs distinct InvoicePayload and PurchaseOrderRecord line-item arrays directly from the DOM, allowing any custom combination of price markup and dock damage to be audited live.",
        "code_ref": "app/static/js/dashboard.js (collectLineItemsFromDOM)",
    },
    {
        "id": "Q7",
        "category": "Error Handling & Observability",
        "question": "How does your FastAPI microservice handle domain exceptions and request tracing in production?",
        "answer": "We implemented a custom exception hierarchy rooted at FinDocAuditException and registered a global FastAPI exception handler that returns structured JSON error payloads (error_code, message, details, UTC timestamp, request path). Every HTTP request also passes through our telemetry middleware, which injects X-Correlation-ID and X-Process-Time-Ms headers.",
        "code_ref": "app/exceptions.py & app/main.py",
    },
    {
        "id": "Q8",
        "category": "System Design & Scaling",
        "question": "What are the bottlenecks if transaction volume grows from 50 invoices/min to 10,000 invoices/min, and how would you re-architect?",
        "answer": "First, we replace the in-memory AUDIT_LEDGER list with partitioned PostgreSQL tables via SQLAlchemy 2.0 (asyncpg) and add Redis idempotency keys (24h TTL) to prevent duplicate ERP webhook submissions. Second, we vectorize the 8 XAI perturbation vectors into a single (8, 7) NumPy matrix call to decision_function(), cutting ML latency from 7.9ms to <1.8ms. Third, we place Apache Kafka in front of worker pods for burst buffering.",
        "code_ref": "docs/ARCHITECTURE.md & docs/PERSONAL_LEARNING_ROADMAP_90_DAYS.md",
    },
    {
        "id": "Q9",
        "category": "MLOps & Concept Drift",
        "question": "How do you detect and mitigate concept drift as vendor pricing and inflation shift over time?",
        "answer": "Because IsolationForest is calibrated on historical baseline distributions, macroeconomic inflation can gradually shift Total_USD upward. In production, we compute weekly Population Stability Index (PSI) across all 7 features using EvidentlyAI. Whenever PSI > 0.20 on any feature, an automated retraining pipeline fits a new candidate StandardScaler + IsolationForest on the trailing 90 days of auditor-verified invoices in MLflow.",
        "code_ref": "docs/INTERVIEW_QA.md (Question 9)",
    },
    {
        "id": "Q10",
        "category": "Adversarial Defense",
        "question": "How does the system defend against split-invoicing (structuring) where a vendor splits a $60,000 invoice into sixty $999 invoices to trigger Tier 1 Auto-Approval?",
        "answer": "Single-invoice stateless checks can be bypassed by structuring (smurfing). Our governance roadmap adds a Redis 24-hour sliding-window velocity counter keyed by (vendor_name, po_number). If cumulative 24h vendor billing exceeds $5,000 or invoice frequency exceeds 3/day, Tier 1 STP is automatically overridden and escalated to Tier 3 Director Sign-Off.",
        "code_ref": "docs/INTERVIEW_QA.md (Question 10)",
    },
]

DEMO_CHECKLIST_AND_VIDEO = {
    "checklist": [
        {"id": "chk1", "phase": "Pre-Demo Setup (T-5 Min)", "task": "Verify FastAPI server is running on http://127.0.0.1:8000 and /health returns HTTP 200 HEALTHY."},
        {"id": "chk2", "phase": "Pre-Demo Setup (T-5 Min)", "task": "Run 'python -m pytest tests/ -v' in terminal to show 100% automated test pass rate."},
        {"id": "chk3", "phase": "Live Demo Step 1 (Min 0–3)", "task": "Present architectural overview & click 'Run All 5 Scenarios (Batch)' to populate all 5 governance tiers in USD & INR."},
        {"id": "chk4", "phase": "Live Demo Step 2 (Min 3–6)", "task": "Click 'Scenario 4 (Rate + Dock Variance)' or edit a live row's Invoice Rate vs. PO Rate and GRN Rejected units to prove 100% dynamic execution."},
        {"id": "chk5", "phase": "Live Demo Step 3 (Min 6–9)", "task": "Walk through the Perturbation XAI Attribution bars (+pts per feature) and Stage Timing Telemetry (<15ms total)."},
        {"id": "chk6", "phase": "Live Demo Step 4 (Min 9–11)", "task": "Paste a raw invoice memo with PAN, Aadhaar & Email into the Unstructured OCR Parser and click 'Parse & Scrub PII'."},
        {"id": "chk7", "phase": "Live Demo Step 5 (Min 11–15)", "task": "Click 'Export CSV' to download the compliance ledger and transition to the 10 Technical Interview Q&As."},
    ],
    "video_storyboard": [
        {"scene": "Scene 1 (0:00 – 0:35)", "title": "Executive Hook & Architecture", "visual": "Show Institutional Editorial Light UI header, KPI ribbon (1 USD = 86.50 INR), and 4-stage pipeline diagram.", "narration": "Introduce FinDoc-AuditEngine v3.0 and why hybrid deterministic 3-Way Matching + 7-D Explainable Isolation Forest outperforms black-box AI."},
        {"scene": "Scene 2 (0:35 – 1:20)", "title": "1-Click 5-Scenario Enterprise Batch", "visual": "Click 'Run All 5 Scenarios (Batch)' and highlight Tier 1 STP ($432), Tier 3 Director ($27,000), and Frozen Fraud Risk ($49,500 Offshore).", "narration": "Explain how INV-1005 matches its PO mathematically but is frozen at 99.0/100 CRITICAL risk due to offshore jurisdiction and Net-1 rush payment."},
        {"scene": "Scene 3 (1:20 – 2:10)", "title": "Live Dynamic Line-Item Editing & Perturbation XAI", "visual": "Modify SKU unit rate and dock rejected units in the table, click 'Execute 3-Way Audit & ML Risk Scoring', and zoom into the XAI attribution bars.", "narration": "Show real-time Single-Feature Perturbation XAI attributing exact risk points to Unit Rate Markup and Dock GRN Shortage."},
        {"scene": "Scene 4 (2:10 – 2:40)", "title": "Unstructured OCR Memo Parsing & Pre-Inference PII Shield", "visual": "Open Raw OCR Parser, click 'Parse & Scrub PII', and show masked [EMAIL_01], [PAN_02], [AADHAAR_05] tokens.", "narration": "Demonstrate DPDP Act / GDPR compliance via Stage 1 pre-inference PII redaction."},
        {"scene": "Scene 5 (2:40 – 3:00)", "title": "PyTest Suite (100% Pass) & CSV Compliance Export", "visual": "Download CSV compliance ledger and show terminal running PyTest suite.", "narration": "Conclude with sub-15ms pipeline telemetry, 100% test coverage, and 90-day production MLOps roadmap."},
    ],
}


@router.get("/slides")
def get_presentation_slides():
    """Return all 12 presentation slides with speaker notes and timing."""
    return {"total_slides": len(SLIDES_DECK), "duration_minutes": 15, "slides": SLIDES_DECK}


@router.get("/interview-qa")
def get_interview_questions():
    """Return all 10 technical interview questions and deep architectural answers."""
    return {"total_questions": len(INTERVIEW_QA_ITEMS), "items": INTERVIEW_QA_ITEMS}


@router.get("/checklist-and-video")
def get_checklist_and_video():
    """Return the interactive demo practice checklist and 5-scene video storyboard."""
    return DEMO_CHECKLIST_AND_VIDEO


@router.get("/deliverables")
def get_day29_deliverables():
    """List all Day 29 deliverables (PDF and Markdown) for direct download."""
    catalog = [
        ("INTERVIEW_QA.pdf", "10 Technical Interview Questions & Answers (True Vector PDF)", "PDF"),
        ("PRESENTATION_NOTES_AND_SLIDES.pdf", "12-Slide Presentation Deck & 15-Min Speaker Notes (Vector PDF)", "PDF"),
        ("DEMO_PRACTICE_CHECKLIST.pdf", "Live Mentor Demo Practice Checklist & Video Script (Vector PDF)", "PDF"),
        ("ARCHITECTURE.pdf", "System & 7-D Explainable ML Architecture Guide (Vector PDF)", "PDF"),
        ("INTERVIEW_QA.md", "10 Technical Interview Questions & Answers (Markdown)", "Markdown"),
        ("PRESENTATION_NOTES_AND_SLIDES.md", "12-Slide Presentation Deck & Speaker Notes (Markdown)", "Markdown"),
        ("DEMO_PRACTICE_CHECKLIST.md", "Live Mentor Demo Practice Checklist & Video Script (Markdown)", "Markdown"),
        ("ARCHITECTURE.md", "System & 7-D Explainable ML Architecture Guide (Markdown)", "Markdown"),
    ]
    out = []
    for fname, title, fmt in catalog:
        fpath = DOCS_DIR / fname
        size_kb = round(fpath.stat().st_size / 1024.0, 1) if fpath.exists() else 0.0
        out.append({
            "filename": fname,
            "title": title,
            "format": fmt,
            "size_kb": size_kb,
            "download_url": f"/api/v1/prep/download/{fname}",
        })
    return {"count": len(out), "deliverables": out}


@router.get("/download/{filename}")
def download_day29_deliverable(filename: str):
    """Download a Day 29 PDF or Markdown deliverable."""
    safe = os.path.basename(filename)
    target = DOCS_DIR / safe
    if not target.exists():
        raise HTTPException(status_code=404, detail=f"File '{safe}' not found.")
    media = "application/pdf" if safe.endswith(".pdf") else "text/markdown; charset=utf-8"
    return FileResponse(path=str(target), media_type=media, filename=safe)
