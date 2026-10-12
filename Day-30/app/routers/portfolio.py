"""Day 30 Executive Portfolio, Multi-Stakeholder Panel Briefing & Deliverable Download API."""

import os
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()
DOCS_DIR = Path(__file__).resolve().parent.parent.parent / "docs"


@router.get("/overview")
def get_portfolio_overview():
    """Return candidate profile, 30-day progression matrix, and flagship engineering projects."""
    return {
        "candidate": {
            "name": "Shri Sanjaykumar V",
            "location": "Vellore, India",
            "phone": "+91 6369945011",
            "email": "v.shrisanjaykumar@gmail.com",
            "linkedin": "https://www.linkedin.com/in/shri-sanjaykumar-v-588bab28a/",
            "github_primary": "https://github.com/Shri-Sanjaykumar/Linkific-Tasks",
            "github_mirror": "https://github.com/Shri-Sanjaykumar/AI-ML-Internship",
            "education": "M.Tech Integrated in Software Engineering — Vellore Institute of Technology (VIT), Vellore",
            "cgpa": "9.12 / 10.0",
            "internships": [
                {
                    "company": "Linkific",
                    "role": "AI/ML Software Engineering Intern",
                    "period": "Aug 2026 – Oct 2026",
                    "highlight": "Architected FinDoc-AuditEngine v3.0 (3-Way AP Matcher, Pre-Inference PII Shield, 7-D Isolation Forest + Perturbation XAI, 33 passed in Day 30 / 28 passed in Day 29)",
                },
                {
                    "company": "TForce India Private Limited",
                    "role": "Software Engineering Intern – Generative AI",
                    "period": "May 2026 – Jul 2026",
                    "highlight": "Engineered enterprise Generative AI workflows and RAG pipelines using Python, SAP BTP, and SAP Generative AI Hub SDK",
                },
            ],
        },
        "progression_matrix": [
            {
                "phase": "Phase I (Days 1–5)",
                "title": "Software Engineering & Data Foundations",
                "skills": ["Python Type Safety", "Modular OOP", "NumPy/Pandas Vectorization", "EDA"],
                "outcome": "PEP 8 data processing pipelines, outlier filtering, and reproducible CLI architecture.",
            },
            {
                "phase": "Phase II (Days 6–10)",
                "title": "Classical Machine Learning & Anomaly Detection",
                "skills": ["scikit-learn", "IsolationForest", "RandomForest", "Cross-Validation"],
                "outcome": "Calibrated supervised & unsupervised pipelines with strict train/validation separation.",
            },
            {
                "phase": "Phase III (Days 11–15)",
                "title": "Deep Learning, NLP & Sequence Modeling",
                "skills": ["Tokenization", "Transformer Embeddings", "Regex + Semantic Entity Extraction"],
                "outcome": "Unstructured financial text parsing and confidence-scored sequence classification.",
            },
            {
                "phase": "Phase IV (Days 16–20)",
                "title": "RAG, Vector Search & Factual Preservation",
                "skills": ["Dense Embeddings", "Vector Indexing", "Context Grounding", "Anti-Hallucination"],
                "outcome": "Source-cited retrieval pipelines with deterministic factual-preservation guardrails.",
            },
            {
                "phase": "Phase V (Days 21–25)",
                "title": "Responsible AI, FastAPI Microservices & CI/CD",
                "skills": ["Pre-Inference PII Redaction", "FastAPI", "Pydantic v2", "Docker & GitHub Actions"],
                "outcome": "PAN/Aadhaar/Account privacy gates, OpenAPI microservices, and automated CI test runners.",
            },
            {
                "phase": "Phase VI (Days 26–30)",
                "title": "Capstone FinDoc-AuditEngine v3.0 & Panel Defense",
                "skills": ["3-Way Reconciliation", "7-D Isolation Forest + Perturbation XAI", "Institutional UI"],
                "outcome": "Production AP audit workbench (USD/INR @ 86.50, 33 passed in Day 30 / 28 passed in Day 29).",
            },
        ],
        "projects": [
            {
                "name": "FinDoc-AuditEngine v3.0",
                "stack": "Python, FastAPI, scikit-learn, 7-D Isolation Forest, Perturbation XAI, Pydantic v2, PyTest",
                "impact": "SKU-level 3-Way Matching + Pre-Inference PII Scrubbing + 7-D Explainable Anomaly Scoring (working prototype / reference implementation).",
            },
            {
                "name": "LEGITIFY – Security & Compliance Platform",
                "stack": "Python, DevSecOps, AppSec, GitHub API",
                "impact": "Automated source-code vulnerability detection and policy-driven repository compliance auditing.",
            },
            {
                "name": "CampusLLM – Personalized University Assistant",
                "stack": "Python, Next.js, React, RAG, Vector Search, OpenAI API",
                "impact": "Context-grounded university RAG assistant with intelligent query routing (~3s average latency).",
            },
            {
                "name": "FinTrack – Group Settlement Platform",
                "stack": "Python, React, Node.js, Firebase, REST APIs",
                "impact": "Modular 5+ service personal finance platform with graph-based multi-party debt settlement.",
            },
            {
                "name": "Solar Energy Forecasting",
                "stack": "Python, scikit-learn, XGBoost, LSTM, NASA POWER API",
                "impact": "Benchmarked 5 ML/DL models on multivariate NASA weather features for automated 7-day forecasting.",
            },
        ],
    }


@router.get("/panel-briefing")
def get_panel_briefing():
    """Return structured Final Practical presentation tracks for Mentors, Team Members, and Technical Panel."""
    return {
        "tracks": {
            "mentors": {
                "audience": "Mentors & Program Leadership",
                "focus": "Engineering Maturity, Domain Context, Code Review Responsiveness & UI/UX Polish",
                "duration": "3–4 Minutes",
                "key_points": [
                    "Real-World Procurement Motivation: Inspired by managing INR 60+ Lakhs in sponsorships and purchase orders as Purchase Manager for VIT's Riviera & Gravitas festivals.",
                    "Iterative Engineering Growth: Evolved from Day 26 prototype to Day 28 PR code review refactoring, Day 29 Institutional Editorial Light UI, and Day 30 Executive Capstone.",
                    "100% Dynamic Execution: Eliminated static scenario coupling via collectLineItemsFromDOM(), supporting live SKU rate edits, GRN dock rejections, and raw OCR memo parsing.",
                    "Dual-Currency Institutional Ledger: Real-time accounting in USD ($) and INR (pegged at 1 USD = 86.50 INR) with downloadable CSV compliance reports.",
                ],
            },
            "team_members": {
                "audience": "Engineering Team Members & Peers",
                "focus": "Modular Service Architecture, Pydantic v2 Contracts, Observability & Zero-Regression CI/CD",
                "duration": "3–4 Minutes",
                "key_points": [
                    "Clean Layered Architecture: Strict separation between app/core (config, logging, privacy), app/services (matcher, anomaly_detector, router), and app/routers (audit, portfolio).",
                    "Fail-Fast Schema Invariants: Pydantic v2 @model_validator(mode='after') enforces subtotal arithmetic (within $0.05 tolerance) and GRN bounds before business logic runs.",
                    "Microsecond Request Telemetry: Every response carries X-Correlation-ID and X-Process-Time-Ms headers plus a 5-stage StageTimingTelemetry breakdown.",
                    "Automated PyTest Suite (All Collected Tests Passed: 28 in Day 29, 33 in Day 30): Runs in <5s covering unit math, 7-D ML monotonicity, PII redaction, custom domain exceptions, and dynamic REST routes.",
                ],
            },
            "technical_panel": {
                "audience": "Technical Panel & Senior Architects",
                "focus": "7-D Isolation Forest Math, Single-Feature Perturbation XAI, Pre-Inference PII Shield & Scale",
                "duration": "5–7 Minutes + Technical Q&A",
                "key_points": [
                    "Hybrid Neuro-Symbolic Design: Deterministic 3-Way Matching catches exact contract breaches (100% precision), while 200-tree IsolationForest catches zero-day statistical anomalies.",
                    "Log-Compression & StandardScaler: Applies ln(1 + Total_USD) and z-score scaling across all 7 features so dollar magnitude never dominates bounded variance ratios in random tree splits.",
                    "Real-Time Perturbation XAI: Computes marginal risk drop delta_R_k = max(0, R(x) - R(x^(k <- mu_k))) across all 7 features in ~7.9ms on CPU without heavy SHAP overhead.",
                    "Pre-Inference Responsible AI Gate: Stage 1 regex shield masks PAN, Aadhaar, Bank Account, Credit Card, Phone, and Email into deterministic surrogates ([PAN_01]) prior to inference.",
                ],
            },
        }
    }


@router.get("/roadmap")
def get_learning_roadmap():
    """Return the structured 90-Day Personal Learning Roadmap (Months 1-3)."""
    return {
        "duration_days": 90,
        "phases": [
            {
                "month": "Month 1 (Days 1–30)",
                "theme": "Stateful Multi-Agent Systems, Hybrid RAG & Automated AI Evaluation",
                "milestones": [
                    "Weeks 1–2: Reciprocal Rank Fusion (BM25 + Dense Vector + Cross-Encoder Reranking) & LangGraph cyclic procurement dispute agents.",
                    "Weeks 3–4: CI-integrated RAGAS / DeepEval quality gates (Faithfulness >= 0.92) & LayoutLMv3 multimodal PDF invoice table extraction.",
                ],
                "kpi": "Recall@5 improvement >= +18% and automated multi-page PDF invoice table extraction.",
            },
            {
                "month": "Month 2 (Days 31–60)",
                "theme": "Cloud-Native MLOps, Kubernetes, ONNX/vLLM Serving & Drift Telemetry",
                "milestones": [
                    "Weeks 5–6: Async PostgreSQL (SQLAlchemy 2.0 + asyncpg) + Redis idempotency cache; MLflow Registry + EvidentlyAI PSI drift alerts (PSI > 0.20).",
                    "Weeks 7–8: Vectorized ONNX Runtime export (<1.8ms XAI inference) & Kubernetes (EKS/AKS) Helm deployment with Prometheus/Grafana histograms.",
                ],
                "kpi": "1,000+ concurrent RPS under Locust load testing and sub-2ms vectorized ONNX anomaly scoring.",
            },
            {
                "month": "Month 3 (Days 61–90)",
                "theme": "Distributed Event-Driven FinTech, AppSec AI Hardening & System Design Mastery",
                "milestones": [
                    "Weeks 9–10: Apache Kafka event-driven ingestion (10,000 invoices/min) & OWASP LLM Top 10 adversarial prompt-injection defense with LEGITIFY.",
                    "Weeks 11–12: 60+ advanced DSA problems, 6 distributed FinTech system design blueprints, 2 published engineering blog posts & OSS PR.",
                ],
                "kpi": "Zero message loss at 10k invoices/min burst load and 100% interview readiness for Tier-1 SDE/AI roles.",
            },
        ],
    }


@router.get("/deliverables")
def list_day30_deliverables():
    """List all Day 30 career, reflection, presentation, and architecture deliverables available for download."""
    catalog = [
        ("FinDoc_AuditEngine_Presentation_Slides.pptx", "12-Slide Widescreen PowerPoint Presentation (.pptx)", "PPTX"),
        ("FinDoc_AuditEngine_Slide_Deck.pdf", "12-Slide Widescreen Presentation Deck (16:9 Vector PDF)", "PDF"),
        ("FinDoc_AuditEngine_Demo_Walkthrough.mp4", "Recorded Demo Walkthrough Video (HD 720p H.264 .mp4)", "MP4"),
        ("SHRI_SANJAYKUMAR_V_UPDATED_RESUME_LINKIFIC.pdf", "Updated ATS Resume (True Vector PDF with Clickable Links)", "PDF"),
        ("SHRI_SANJAYKUMAR_V_UPDATED_RESUME_LINKIFIC.tex", "Updated ATS Resume (LaTeX Overleaf Source Code)", "LaTeX"),
        ("INTERNSHIP_REFLECTION_REPORT.pdf", "Internship Reflection Report (2-3 Page True Vector PDF)", "PDF"),
        ("PERSONAL_LEARNING_ROADMAP_90_DAYS.pdf", "Personal Learning Roadmap — 90 Days (True Vector PDF)", "PDF"),
        ("UPDATED_LINKEDIN_PROFILE.pdf", "Updated LinkedIn Profile Blueprint (True Vector PDF)", "PDF"),
        ("PORTFOLIO_AND_PANEL_PRESENTATION.pdf", "Final Panel Presentation Playbook (True Vector PDF)", "PDF"),
        ("INTERNSHIP_REFLECTION_REPORT.md", "Internship Reflection Report (2–3 Pages Full Markdown)", "Markdown"),
        ("UPDATED_RESUME_SHRI_SANJAYKUMAR_V.md", "Updated Resume (ATS Markdown & Structured Sections)", "Markdown"),
        ("UPDATED_LINKEDIN_PROFILE.md", "Updated LinkedIn Profile Guide (shri-sanjaykumar-v-588bab28a)", "Markdown"),
        ("PERSONAL_LEARNING_ROADMAP_90_DAYS.md", "Personal Learning Roadmap (90-Day / 12-Week Plan)", "Markdown"),
        ("PORTFOLIO_AND_PANEL_PRESENTATION.md", "Final Panel Presentation Guide (Mentors, Team, Tech Panel)", "Markdown"),
        ("INTERVIEW_QA.md", "10 Technical Interview Questions & Architectural Answers", "Markdown"),
        ("PRESENTATION_NOTES_AND_SLIDES.md", "12-Slide Presentation Deck & 15-Minute Speaker Script", "Markdown"),
        ("DEMO_PRACTICE_CHECKLIST.md", "Live Demo Practice Checklist & Video Storyboard", "Markdown"),
        ("ARCHITECTURE.md", "System & 7-D Explainable ML Architecture Guide", "Markdown"),
    ]
    items = []
    for fname, title, fmt in catalog:
        fpath = DOCS_DIR / fname
        size_kb = round(fpath.stat().st_size / 1024.0, 1) if fpath.exists() else 0.0
        items.append({
            "filename": fname,
            "title": title,
            "format": fmt,
            "size_kb": size_kb,
            "download_url": f"/api/v1/portfolio/download/{fname}",
        })
    return {"count": len(items), "deliverables": items}


@router.get("/download/{filename}")
def download_deliverable(filename: str):
    """Serve a Day 30 deliverable file (PDF or Markdown) for direct download."""
    safe_name = os.path.basename(filename)
    target = DOCS_DIR / safe_name
    if not target.exists():
        raise HTTPException(status_code=404, detail=f"Deliverable '{safe_name}' not found.")
    if safe_name.endswith(".pdf"):
        media_type = "application/pdf"
    elif safe_name.endswith(".pptx"):
        media_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    elif safe_name.endswith(".mp4"):
        media_type = "video/mp4"
    else:
        media_type = "text/markdown; charset=utf-8"
    return FileResponse(path=str(target), media_type=media_type, filename=safe_name)
