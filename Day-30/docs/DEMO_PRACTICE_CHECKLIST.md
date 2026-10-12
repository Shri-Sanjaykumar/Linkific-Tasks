# Day 29 Deliverable: Mentor Live Demo Practice Checklist & Video Script

**Project:** FinDoc-AuditEngine v3.0  
**Target Demo Duration:** 10–15 Minutes  
**Verification Status:** 25/25 Automated Tests Passing | Localhost Server Active (`http://127.0.0.1:8000`)

---

## 1. Pre-Demo Environment Readiness Checklist (T-Minus 10 Minutes)

- [x] **1. Verify Python & Dependencies:** Python 3.14.3 environment active with `fastapi`, `uvicorn`, `scikit-learn`, `pydantic`, `pytest`.
- [x] **2. Run Pre-Flight PyTest Suite:**
  ```powershell
  cd C:\projects\linkific\internship\Day-29
  python -m pytest tests -v
  ```
  *Confirm output reads `25 passed` in `< 2.0s`.*
- [x] **3. Launch Localhost Server via Application-Control Safe Runner:**
  ```powershell
  python run_server.py
  ```
  *Confirm Uvicorn is listening on `http://127.0.0.1:8000`.*
- [x] **4. Open Browser Tabs in Advance:**
  - Tab 1: **Institutional Audit Workbench** — `http://127.0.0.1:8000/dashboard`
  - Tab 2: **Swagger OpenAPI Specification** — `http://127.0.0.1:8000/docs`
  - Tab 3: **System Health & Model Telemetry** — `http://127.0.0.1:8000/health`
- [x] **5. Terminal Window Arrangement:** Keep PowerShell open alongside the browser so mentors can see live server logs (`Privacy Gate`, `Reconciliation`, `ML Scorer`, `Governance Router`) stream on every click.

---

## 2. Five-Act Live Mentor Demo Script (Step-by-Step)

### Act 1: System Telemetry & Institutional UI Tour (1.5 Minutes)
1. Show `http://127.0.0.1:8000/health` to confirm `IsolationForest_v2.0`, `Perturbation_Marginal_XAI_7D`, and `pegged_usd_to_inr: 86.5`.
2. Switch to `http://127.0.0.1:8000/dashboard`. Point out the clean institutional light grid, `IBM Plex Mono` tabular numerals, and the 5-column KPI strip at the top.

### Act 2: One-Click 5-Scenario Enterprise Batch Execution (2 Minutes)
1. Click **"Run 5-Scenario Batch"** in the top-right command bar.
2. Point out how the KPI strip immediately updates:
   - **Total Invoices Audited:** `5`
   - **Disbursed Capital (USD):** `$32,292.00`
   - **Disbursed Capital (INR):** `INR 2,793,258.00`
   - **Straight-Through Rate (STP):** `20.0%`
   - **Held / Blocked Exceptions:** `2`
3. Use the **Filter Tabs** (`Tier 1 STP`, `Tier 2 Manager`, `Tier 3 Director`, `Rejected`, `Frozen Fraud`) in the bottom ledger and click **"Inspect"** on `INV-1005` to show the slide-over cryptographic JSON Audit Dossier.

### Act 3: Proving 100% Dynamic Execution on Arbitrary Custom Inputs (3 Minutes)
1. Click **"New Blank"** or **"Synthesize Random Invoice"** in Panel 1.
2. Add a second line item using **`+ Add Line Item`**:
   - Row 1: `SKU-SRV`, `Dell PowerEdge Server`, Inv Rate `$4,200`, PO Rate `$4,000` (`+$200` overcharge), Qty `2`, GRN Recv `2`, GRN Rej `0`.
   - Row 2: `SKU-NIC`, `100GbE Fiber Transceiver`, Inv Rate `$300`, PO Rate `$300`, Qty `5`, GRN Recv `5`, GRN Rej `2` (`2 damaged at dock`).
3. Point out the **Live Pre-Audit Calculation Strip** updating as you type:
   - `Projected Rate Variance` and `Projected Dock Shortage` turn crimson before submission.
4. Click **"Execute 3-Way Reconciliation & Isolation Forest Audit"**.
5. In Panel 2, show the **Per-Item Reconciliation Verification Table** (flagging `RATE_VARIANCE` on Row 1 and `QTY_SHORTAGE` on Row 2) and the **Perturbation Feature Attribution Bars** dynamically calculated for your custom input.

### Act 4: Unstructured Free-Text Parsing & PII Redaction (1.5 Minutes)
1. Click **"Paste Raw Text / PII"** in Panel 1.
2. Paste:
   `Invoice INV-7742 from Horizon Cybernetics Pvt Ltd; PO: PO-7742; Total: $890.00; Country: IN; Contact: priya.billing@horizon.in; Tax PAN: ABCDE1234F; Account: 987654321099`
3. Click **"Extract Fields & Scrub PII"**. Show the green confirmation banner proving that 3 PII tokens (`EMAIL`, `PAN`, `ACCOUNT`) were masked and the form fields were populated automatically.
4. Click **"Execute 3-Way Reconciliation & Isolation Forest Audit"** to watch it route to `TIER_1_STP_AUTO_APPROVED`.

### Act 5: Compliance CSV Export & CLI Mentor Demo Runner (2 Minutes)
1. Click **"Export CSV"** in the top command bar to download `FinDoc_Audit_Compliance_Ledger.csv`.
2. Switch to the terminal and run the automated CLI mentor script:
   ```powershell
   python run_mentor_demo.py
   ```
   Show the 5-stage formatted terminal walkthrough and 25/25 test verification.
