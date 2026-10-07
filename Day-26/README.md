# Day 26: Responsible AI Engineering & Ethical Governance POC

**Company:** Linkific Technology Solutions Pvt Ltd  
**Track:** AI/ML Internship  
**Topic:** Responsible AI, Bias Mitigation, Hallucination Prevention, Privacy Guardrails & Governance Guidelines  
**Execution Status:** Verified & 100% Passed (24/24 Tests)

---

## 1. Executive Overview

Day 26 establishes a production-grade **Responsible AI (RAI) Proof of Concept (POC)** and corporate ethical governance architecture for Linkific Technology Solutions.

This implementation addresses four critical failure modes of enterprise AI systems:
1. **Algorithmic Bias & Proxy Variables:** Mathematical prevention of disparate demographic impact adhering to the EEOC 4/5ths Rule (80% rule).
2. **Factual & Numerical Hallucinations:** Source-grounded verification gates blocking altered amounts, false discounts, and ungrounded statements.
3. **Data Privacy & PII Leakage:** Pre-inference regex and token scrubbers masking emails, phones, credit cards, SSNs, Aadhaar, PAN cards, and bank account numbers before third-party LLM transmission.
4. **Human-in-the-Loop (HITL) Governance:** Risk-tiered transaction approval rules safeguarding high-value enterprise decisions.

---

## 2. Deliverables Summary

1. **Responsible AI Case Study Report ([`docs/CASE_STUDY_REPORT.md`](file:///C:/projects/linkific/internship/Day-26/docs/CASE_STUDY_REPORT.md)):**
   - Deep-dive into the Optum / Obermeyer et al. (2019) healthcare racial bias incident published in *Science*.
   - Technical analysis of proxy variable substitution ($Y_{cost} \to Y_{health}$) and its socio-economic harm.
   - 5-Whys root cause analysis and software prevention engineering controls.

2. **Company Responsible AI Guidelines ([`docs/RESPONSIBLE_AI_GUIDELINES.md`](file:///C:/projects/linkific/internship/Day-26/docs/RESPONSIBLE_AI_GUIDELINES.md)):**
   - Formal 4-pillar binding company engineering policy covering fairness thresholds, hallucination refusal protocols, PII masking standards, and HITL escalation tiers.

3. **Executive Summary ([`docs/RESPONSIBLE_AI_SUMMARY.md`](file:///C:/projects/linkific/internship/Day-26/docs/RESPONSIBLE_AI_SUMMARY.md)):**
   - Executive takeaway summarizing the prevention framework and business value for Linkific.

4. **Modular Guardrail Proof of Concept (`app/guardrails/`):**
   - [`privacy_masker.py`](file:///C:/projects/linkific/internship/Day-26/app/guardrails/privacy_masker.py): PII scrubber with reversible surrogate rehydration within trusted VPC boundaries.
   - [`fairness_auditor.py`](file:///C:/projects/linkific/internship/Day-26/app/guardrails/fairness_auditor.py): Statistical engine computing Disparate Impact Ratio (DIR) and Demographic Parity Difference.
   - [`grounding_verifier.py`](file:///C:/projects/linkific/internship/Day-26/app/guardrails/grounding_verifier.py): Anti-hallucination guardrail validating numerical exact-match fidelity and citation coverage.
   - [`pipeline.py`](file:///C:/projects/linkific/internship/Day-26/app/guardrails/pipeline.py): End-to-end unified gateway managing pre-inference masking and post-inference audit records.

5. **CLI Demonstration Runner (`run_responsible_ai.py`):**
   - Interactive command-line tool (`--mode all`, `--mode privacy`, `--mode grounding`, `--mode fairness`, `--mode pipeline`).

6. **PyTest Automated Test Suite (`tests/`):**
   - 18 RAI unit/integration tests + 6 cross-day regression tests (Days 20 to 25) = **24/24 tests passed** in under 0.8 seconds.

---

## 3. How to Run

### Run CLI Demonstration
```powershell
python run_responsible_ai.py --mode all
```

Options:
- `--mode privacy`: Demonstrate PII redaction and secure rehydration.
- `--mode grounding`: Demonstrate hallucination detection and number verification.
- `--mode fairness`: Demonstrate demographic bias auditing on biased vs fair datasets.
- `--mode pipeline`: Run complete unified guardrail audit cycle.

### Run Test Suite
```powershell
python -m pytest tests -v
```
All 24 tests will execute and pass cleanly.
