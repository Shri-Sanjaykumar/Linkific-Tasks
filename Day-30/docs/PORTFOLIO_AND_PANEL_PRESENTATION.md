# Final Practical — Multi-Stakeholder Presentation & Portfolio Guide

**Presenter:** Shri Sanjaykumar V (`M.Tech Integrated in Software Engineering, VIT Vellore — CGPA: 9.12/10.0`)  
**Companion Presentation & Video Files in `docs/`:**  
- **PowerPoint Presentation (`.pptx`):** [`FinDoc_AuditEngine_Presentation_Slides.pptx`](./FinDoc_AuditEngine_Presentation_Slides.pptx) (12 Widescreen 16:9 Slides)  
- **Landscape Slide Deck (`.pdf`):** [`FinDoc_AuditEngine_Slide_Deck.pdf`](./FinDoc_AuditEngine_Slide_Deck.pdf) (12 Designed 16:9 Slides)  
- **Recorded Demo Video (`.mp4`):** [`FinDoc_AuditEngine_Demo_Walkthrough.mp4`](./FinDoc_AuditEngine_Demo_Walkthrough.mp4) (HD 720p Walkthrough)  
**Verified Automated Tests:** Day 29: `28 passed` (`python -m pytest tests -q`) | Day 30: `33 passed` (`python -m pytest tests -q`) — *all collected tests passed*

---

## 1. Tailored Presentation Strategy by Audience (10–12 Minute Structure)

### Track A: Presenting to **Mentors**
- **Focus:** Practical domain motivation, iterative improvements from code review through final polish, and honest engineering reflection.
- **Key Points:**
  1. Inspired by real procurement workflows (managing purchase orders and vendor sponsorships for VIT's Riviera & Gravitas festivals).
  2. Evolved into a clean, self-contained FastAPI working prototype with an institutional light-theme workbench (`1 USD = 86.50 INR`).
  3. Demonstrates three representative scenarios clearly: a clean auto-approved invoice (`INV-1001`), a contract price discrepancy (`INV-1004`), and a high-risk anomaly (`INV-1005`).

### Track B: Presenting to **Team Members**
- **Focus:** Code organization, API contracts, testing workflow, and reproducibility.
- **Key Points:**
  1. Modular directory structure separating `app/core` (config, logging, regex privacy scrubber), `app/services` (3-way matcher, anomaly scorer, router), and `app/routers` (`audit`, `mentor_prep`, `portfolio`).
  2. Fail-fast `Pydantic v2` schema validators (`@model_validator`) enforcing `$0.05` subtotal tolerances and valid GRN quantities.
  3. Reproducible automated test suite (`python -m pytest tests -q` -> `28 passed` in Day 29; `33 passed` in Day 30 — all collected tests passed).

### Track C: Presenting to the **Technical Panel**
- **Focus:** Mathematical logic, synthetic baseline scope, perturbation attribution, and transparent discussion of prototype limitations.
- **Key Points:**
  1. **Hybrid Design:** Deterministic 3-way matching enforces configured SKU price/quantity rules, while the 7-feature `IsolationForest` surfaces unusual multi-feature patterns.
  2. **Accurate Model Scope:** The `IsolationForest` is trained on a seeded synthetic baseline of 1,000 records (`random_state=42`), and its `0–100` output is an engineered anomaly-risk indicator rather than a calibrated probability of fraud.
  3. **Prototype Limitations & Future Work:** Clearly explain that `AUDIT_LEDGER` is an in-memory Python list (requiring PostgreSQL for persistence), `FinancialPrivacyScrubber` and `/parse-raw` use regex rules (requiring NER and optical OCR for production), and model thresholds require real-world calibration.
