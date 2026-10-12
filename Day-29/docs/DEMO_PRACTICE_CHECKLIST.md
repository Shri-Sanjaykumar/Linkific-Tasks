# Live Mentor Demo Practice Checklist & Video Walkthrough Guide

**Companion Media & Slide Files in `docs/`:**  
- **Recorded Video Walkthrough (`.mp4`):** [`FinDoc_AuditEngine_Demo_Walkthrough.mp4`](./FinDoc_AuditEngine_Demo_Walkthrough.mp4)  
- **PowerPoint Slide Deck (`.pptx`):** [`FinDoc_AuditEngine_Presentation_Slides.pptx`](./FinDoc_AuditEngine_Presentation_Slides.pptx)  
- **Landscape Slide Deck (`.pdf`):** [`FinDoc_AuditEngine_Slide_Deck.pdf`](./FinDoc_AuditEngine_Slide_Deck.pdf)

---

## 1. Pre-Demo Verification Checklist (5 Minutes Before Presenting)

- [x] **1. Rerun PyTest Suite Locally:**
  ```powershell
  python -m pytest tests -q
  ```
  - Verify output matches **Day 29: `28 passed`** / **Day 30: `33 passed`** (*all collected tests passed*).
- [x] **2. Start the Local FastAPI Server:**
  ```powershell
  python run_server.py
  ```
  - Confirm `http://127.0.0.1:8000` loads the Institutional Editorial Light UI and `http://127.0.0.1:8000/health` returns `"status": "healthy"`.
- [x] **3. Open Presentation & Video Assets:**
  - Open [`FinDoc_AuditEngine_Presentation_Slides.pptx`](./FinDoc_AuditEngine_Presentation_Slides.pptx) (or use Tab 2's built-in Slide Deck & 15:00 Timer in the browser).
  - Have a terminal window visible alongside the browser to show live structured logs during the 3 invoice scenarios.

---

## 2. Step-by-Step 5-Minute Live Demo Script (3 Representative Scenarios)

### Step A: Scenario 1 — Clean Invoice (`INV-1001`) [1.5 Minutes]
1. In the web workbench at `http://127.0.0.1:8000`, click **`Scenario 1: Clean STP ($432)`**.
2. Point out that `SKU-A101` bills `2` units at `$180.00`, matching `PO-9001` (`$180.00`) and the GRN (`2 received, 0 rejected`).
3. Click **`Execute 3-Way Audit & ML Risk Scoring`**.
4. Highlight the result: **`TIER_1_STP_AUTO_APPROVED`**, `$0.00` price variance, engineered risk indicator `25.0 / 100 (LOW)`, and show the matching terminal log line.

### Step B: Scenario 2 — Price Discrepancy (`INV-1004` + Dynamic Table Edit) [2 Minutes]
1. Click **`Scenario 4: Price Discrepancy ($5.4k)`** (`INV-1004` from `Overcharge Technologies`).
2. Point out that `SKU-D404` bills `10` units at **`$450.00`** against a PO contract rate of **`$400.00`**.
3. Click **`Execute 3-Way Audit & ML Risk Scoring`**.
4. Highlight the result: **`REJECTED_DISCREPANCY`** (`Authorized = False`), `+$500.00 USD` (`INR 43,250.00`) price variance, and the Perturbation Attribution bar highlighting `Unit Rate Markup Ratio`.
5. **Live Dynamic Proof:** Change the Invoice Rate or `GRN Rej` cell directly in the table and click **`Execute`** again to show the variance and risk indicator updating dynamically.

### Step C: Scenario 3 — Critical-Risk Anomaly (`INV-1005`) [1.5 Minutes]
1. Click **`Scenario 5: Offshore Fraud ($49.5k)`** (`INV-1005` from `Shadow Island Holding BZ`).
2. Point out that the price (`$49,500`) and quantity (`1`) match `PO-9005` on paper.
3. Click **`Execute 3-Way Audit & ML Risk Scoring`**.
4. Highlight why the hybrid design matters: even though 3-way matching passes, the 7-D Isolation Forest scores the invoice at **`99.0 / 100 (CRITICAL)`** due to offshore jurisdiction (`BZ`), `Net-1` rush payment terms, and `$49,500` scale, routing it to **`FROZEN_FRAUD_RISK`**.

---

## 3. Recorded Video Walkthrough Summary (`FinDoc_AuditEngine_Demo_Walkthrough.mp4`)

The recorded `.mp4` video in `docs/FinDoc_AuditEngine_Demo_Walkthrough.mp4` (`1280x720` H.264) captures:
- **00:00 – 00:06:** Dashboard UI & 4-Stage Prototype Architecture Overview
- **00:06 – 00:12:** Scenario 1 (`INV-1001` Clean Invoice -> `TIER_1_STP_AUTO_APPROVED`) + Terminal Log
- **00:12 – 00:18:** Scenario 2 (`INV-1004` Price Discrepancy `+$500` -> `REJECTED_DISCREPANCY`) + Terminal Log
- **00:18 – 00:24:** Scenario 3 (`INV-1005` Offshore Critical Anomaly `99.0/100` -> `FROZEN_FRAUD_RISK`) + Perturbation Bars
- **00:24 – 00:30:** Terminal PyTest Execution (`Day 29: 28 passed`, `Day 30: 33 passed`) & Prototype Limitations
