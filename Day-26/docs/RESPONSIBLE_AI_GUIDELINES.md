# Linkific Enterprise Responsible AI Governance Guidelines

**Document ID:** LNK-ENG-RAI-2026-V1  
**Organization:** Linkific Technology Solutions Pvt Ltd  
**Target Audience:** AI/ML Engineers, Data Scientists, Product Managers, Platform Architects  
**Effective Date:** October 2026  
**Status:** Mandatory Company Engineering Standard

---

## 1. Purpose and Scope

Linkific designs, trains, and operationalizes enterprise AI workflows, LLM reasoning pipelines, automated finance approval engines, and multi-agent coordination systems. As our algorithms make autonomous and semi-autonomous determinations regarding invoice approvals, credit checks, document parsing, and agent-driven workflows, we enforce strict **Responsible AI (RAI)** governance.

These guidelines establish binding operational standards across four cardinal pillars:
1. **Bias Mitigation & Algorithmic Fairness**
2. **Hallucination Prevention & Factual Grounding**
3. **Data Privacy, Confidentiality & PII Masking**
4. **Transparency, Explainability & Human-in-the-Loop Oversight**

---

## 2. Pillar I: Algorithmic Fairness & Bias Mitigation

### 2.1 Protected Attributes & Disparate Impact Standards
- **Explicit Exclusions:** Models deployed for financial approvals, vendor scoring, recruitment, or risk tiering shall not ingest protected attributes including gender, race, caste, religion, sexual orientation, disability status, or age unless legally mandated for statutory compliance.
- **Statistical Parity / Four-Fifths Rule:** All classification models must satisfy the Disparate Impact Ratio (DIR) threshold:
  $$\text{DIR} = \frac{P(\hat{Y} = 1 \mid A = \text{unprivileged})}{P(\hat{Y} = 1 \mid A = \text{privileged})} \ge 0.80$$
- **Equalized Odds Requirement:** True Positive Rates (TPR) and False Positive Rates (FPR) across defined demographic groups must not deviate by more than **5.0 percentage points**:
  $$|P(\hat{Y} = 1 \mid Y = 1, A = a) - P(\hat{Y} = 1 \mid Y = 1, A = b)| \le 0.05$$

### 2.2 Proxy Audit Protocol
- Engineers must conduct Pearson and Mutual Information correlation tests between candidate features and protected attributes. Any feature exhibiting a correlation coefficient $|\rho| \ge 0.65$ with a protected demographic variable without direct domain causality must be rejected or regularized.

---

## 3. Pillar II: Hallucination Prevention & Factual Verification

### 3.1 Strict Source-Grounded Generation
- **Zero Unattributed Synthesis:** In RAG and LLM agent pipelines, any factual statement, numerical balance, credit limit, or policy condition must be linked to an explicit source context document reference.
- **Context Citation Coverage (CCC):** Generated completions must achieve a minimum Citation Coverage Score of **0.85**:
  $$\text{CCC} = \frac{\text{Count of claims verifiable in reference chunks}}{\text{Total substantive factual claims in generation}} \ge 0.85$$

### 3.2 Anti-Hallucination Guardrail Architecture
- Prior to returning an AI response to a user or downstream microservice, the output must pass through an automated **Verification Guardrail Gate**:
  1. *Entity & Number Exact-Match Verifier:* Extracted invoice amounts, tax rates, vendor IDs, and dates are checked against original OCR/JSON documents.
  2. *Contradiction Detection:* An NLI (Natural Language Inference) premise-hypothesis check ensures the generation does not contradict retrieved text.
  3. *Uncertainty Refusal Protocol:* When document retrieval similarity scores fall below the relevance threshold ($\tau_{sim} < 0.70$), the model must explicitly respond with a standard refusal message rather than confabulating.

---

## 4. Pillar III: Privacy, Confidentiality & PII Guardrails

### 4.1 Zero PII Ingestion into External Providers
- No prompt sent to external LLM provider APIs (OpenAI, Anthropic, Google, Groq) shall contain unmasked personally identifiable information (PII) or sensitive enterprise secrets.
- **Mandatory Anonymization Pipeline:** All incoming customer documents must pass through a local regex/NER privacy scrubber that replaces sensitive tokens with deterministic surrogate identifiers:
  - Names $\rightarrow$ `[PERSON_01]`
  - Emails $\rightarrow$ `[EMAIL_MASKED]`
  - Phone Numbers $\rightarrow$ `[PHONE_MASKED]`
  - Credit Card / Bank Account Numbers $\rightarrow$ `[ACCOUNT_MASKED]`
  - Indian Aadhaar / PAN Numbers $\rightarrow$ `[GOV_ID_MASKED]`

### 4.2 Reversible De-identification Architecture
- Surrogate mappings are stored exclusively in an encrypted in-memory Redis session cache with a 15-minute TTL. The external LLM processes only sanitized text; real entities are re-hydrated only within Linkific's secure VPC boundary before final storage.

---

## 5. Pillar IV: Transparency & Human-in-the-Loop (HITL)

### 5.1 Tiered Autonomous Decision Authority
All automated decision workflows must adhere to Linkific's risk-based escalation matrix:

| Transaction Tier | Dollar Threshold (USD / INR) | Autonomous Action Permitted? | Required Verification |
|---|---|:---:|---|
| **Tier 1 (Low Risk)** | $< \$1,000$ / $< ₹86,500$ | Yes (STP Auto-Approve) | Automated Guardrail Verification |
| **Tier 2 (Medium Risk)** | $\$1,000 - \$10,000$ / $₹86,500 - ₹865,000$ | Conditional | Model Confidence $\ge 0.95$ + Guardrail Clean |
| **Tier 3 (High Risk)** | $> \$10,000$ / $> ₹865,000$ | **NO (HITL Mandatory)** | Manager Dual-Signoff Required |
| **Discrepancy / Anomaly** | Any Amount with Variance | **NO (HITL Mandatory)** | Automated Freeze & Compliance Review |

### 5.2 Structured Audit Trail
Every AI decision must emit a cryptographically signed or immutable JSON audit record containing:
- `timestamp`, `model_id`, `prompt_hash`, `guardrail_checks_passed`
- `retrieval_sources_used`, `confidence_score`, `hitl_approver_id`

---

## 6. Engineering Compliance & Enforcement

1. **Pre-commit & CI/CD Hooks:** The PyTest RAI verification suite (`tests/test_responsible_ai.py`) must execute and achieve a 100% pass rate prior to merging pull requests.
2. **Periodic Algorithmic Audits:** AI systems in production undergo quarterly bias drift and hallucination rate assessments.
3. **Whistleblower & Incident Response:** Any engineer detecting unethical, biased, or privacy-violating algorithmic behavior is empowered and required to trigger a Sev-1 incident stop-ship on the affected pipeline.
