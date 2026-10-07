"""Day 26 CLI Demonstration: Responsible AI Guardrail Gateway.

Demonstrates:
1. PII Redaction & Reversible Masking (Emails, Phone, PAN, Aadhaar, Credit Cards)
2. Hallucination Detection & Numerical Exact-Match Verification
3. Algorithmic Fairness & EEOC 4/5ths Rule Disparate Impact Auditing
4. Dual USD and INR Financial Thresholds (1 USD = 86.50 INR)
"""

import os
import sys
import json
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.guardrails.privacy_masker import PrivacyMasker
from app.guardrails.fairness_auditor import FairnessAuditor
from app.guardrails.grounding_verifier import GroundingVerifier
from app.guardrails.pipeline import ResponsibleAIPipeline


def print_banner():
    banner = """
====================================================================================================
     LINKIFIC AI/ML INTERNSHIP - DAY 26: RESPONSIBLE AI & ETHICAL GOVERNANCE POC
     Pillars: Privacy (PII Masking) | Factual Grounding (Hallucination Gate) | Fairness (DIR Audit)
     Regulatory Grounding: EEOC 4/5ths Rule | GDPR / DPDPA PII Standards | Dual USD/INR Support
====================================================================================================
"""
    print(banner)


def demo_privacy_masking():
    """Demonstrate pre-inference PII scrubbing and secure post-inference rehydration."""
    print("\n[1] PILLAR I: PII REDACTION & PRIVACY PRESERVATION GATE:")
    print("-" * 115)

    sample_prompt = (
        "Vendor contact Rahul Sharma submitted invoice #INV-2026-881 for Linkific billing.\n"
        "Customer email: rahul.sharma@enterprise-solutions.com, Mobile: +91 98765 43210.\n"
        "Tax registration PAN: ABCDE1234F, Aadhaar ID: 4123 8812 9904.\n"
        "Disbursement bank account: 91823746192837, corporate credit card: 4111-2222-3333-4444.\n"
        "Please confirm payment authorization for USD $8,500.00 (INR 735,250.00)."
    )

    print("--- RAW USER PROMPT (CONTAINS SENSITIVE PII) ---")
    print(sample_prompt)
    print("\n>>> EXECUTING PRIVACY SCRUBBER (LOCAL PRE-INFERENCE GATE)...")

    scrub_result = PrivacyMasker.scrub_text(sample_prompt)

    print(f"\n[OK] Detected & Redacted Tokens Count: {scrub_result.redacted_count}")
    for t in scrub_result.masked_tokens:
        print(f"  - [{t.token_type.value:<14}] Original: '{t.original_text}' --> Surrogate: '{t.surrogate}'")

    print("\n--- SANITIZED PROMPT SAFE FOR THIRD-PARTY LLM DISPATCH (OPENAI / CLAUDE / GEMINI / GROQ) ---")
    print(scrub_result.sanitized_text)

    # Rehydration test
    rehydrated = PrivacyMasker.rehydrate_text(scrub_result.sanitized_text, scrub_result.surrogate_map)
    assert rehydrated == sample_prompt
    print("\n[OK] Secure In-VPC Rehydration Test: Passed (100% reversible within trusted boundary).")
    print("-" * 115)


def demo_hallucination_verification():
    """Demonstrate post-inference grounding check catching numerical discrepancies & fabrications."""
    print("\n[2] PILLAR II: FACTUAL GROUNDING & HALLUCINATION PREVENTION GATE:")
    print("-" * 115)

    source_erp_ledger = (
        "PURCHASE ORDER PO-8840 SPECIFICATIONS:\n"
        "Vendor: Apex Microelectronics Pvt Ltd. Contract Date: 2026-09-15.\n"
        "Authorized items: 50 units High-Performance Edge TPU accelerators @ $400.00 each = $20,000.00 USD (INR 1,730,000.00).\n"
        "Shipping & handling fee: $350.00 USD (INR 30,275.00). Statutory GST (18%): $3,663.00 USD (INR 316,849.50).\n"
        "Total Authorized Net Payable: $24,013.00 USD (INR 2,077,124.50)."
    )

    # Clean Grounded Generation
    grounded_llm_response = (
        "Reconciliation Summary: Apex Microelectronics delivered 50 units of Edge TPU accelerators at $400.00 each, "
        "amounting to $20,000.00 USD. Including shipping fee of $350.00 and GST of $3,663.00, the total payable is $24,013.00 USD."
    )

    # Hallucinated Generation (Altered tax rate, inflated amount, invented discount)
    hallucinated_llm_response = (
        "Reconciliation Summary: Apex Microelectronics delivered 50 units of Edge TPU accelerators at $450.00 each, "
        "amounting to $22,500.00 USD. A special holiday discount of $1,200.00 was applied, resulting in net payable $21,300.00 USD."
    )

    print(">>> TEST CASE A: VERIFYING GROUNDED COMPLETION...")
    res_a = GroundingVerifier.verify_grounding(grounded_llm_response, source_erp_ledger)
    print(f"  - Status: {res_a.status} | Citation Score: {res_a.citation_coverage_score:.2f} | Action: {res_a.action}")
    print(f"  - Grounded: {res_a.is_grounded}")

    print("\n>>> TEST CASE B: VERIFYING HALLUCINATED COMPLETION (CONTAINS FABRICATED NUMBERS)...")
    res_b = GroundingVerifier.verify_grounding(hallucinated_llm_response, source_erp_ledger)
    print(f"  - Status: {res_b.status} | Citation Score: {res_b.citation_coverage_score:.2f} | Action: {res_b.action}")
    print(f"  - Grounded: {res_b.is_grounded}")
    print("  - Detected Violations:")
    for v in res_b.unsupported_claims:
        print(f"    * {v}")
    print("-" * 115)


def demo_fairness_audit():
    """Demonstrate statistical fairness auditing and Disparate Impact Ratio testing."""
    print("\n[3] PILLAR III: ALGORITHMIC FAIRNESS & DISPARATE IMPACT AUDIT (EEOC 4/5ths RULE):")
    print("-" * 115)

    data_dir = os.path.join(BASE_DIR, "data")
    biased_file = os.path.join(data_dir, "biased_decision_log.json")
    fair_file = os.path.join(data_dir, "fair_decision_log.json")

    with open(biased_file, "r") as f:
        biased_data = json.load(f)
    with open(fair_file, "r") as f:
        fair_data = json.load(f)

    print(">>> AUDITING HISTORICAL MODEL A (SUSPECTED PROXY BIAS - METRO VS RURAL):")
    m_biased = FairnessAuditor.audit_decisions(
        records=biased_data,
        protected_attribute="region",
        privileged_group_value="Metro",
        unprivileged_group_value="Rural",
    )
    print(f"  - Privileged (Metro) Approval Rate    : {m_biased.group_a_approval_rate * 100:.1f}%")
    print(f"  - Unprivileged (Rural) Approval Rate  : {m_biased.group_b_approval_rate * 100:.1f}%")
    print(f"  - Disparate Impact Ratio (DIR)        : {m_biased.disparate_impact_ratio:.3f} (Legal Threshold: >= 0.800)")
    print(f"  - Demographic Parity Difference (DPD) : {m_biased.demographic_parity_difference * 100:.1f}%")
    print(f"  - Passes EEOC 4/5ths Parity Rule      : {m_biased.passes_four_fifths_rule}")
    print(f"  - Model Compliance Status             : {m_biased.status}")
    for viol in m_biased.violations:
        print(f"    * {viol}")

    print("\n>>> AUDITING DE-BIASED PRODUCTION MODEL B (REGULARIZED CAUSAL WEIGHTS):")
    m_fair = FairnessAuditor.audit_decisions(
        records=fair_data,
        protected_attribute="region",
        privileged_group_value="Metro",
        unprivileged_group_value="Rural",
    )
    print(f"  - Privileged (Metro) Approval Rate    : {m_fair.group_a_approval_rate * 100:.1f}%")
    print(f"  - Unprivileged (Rural) Approval Rate  : {m_fair.group_b_approval_rate * 100:.1f}%")
    print(f"  - Disparate Impact Ratio (DIR)        : {m_fair.disparate_impact_ratio:.3f} (Legal Threshold: >= 0.800)")
    print(f"  - Passes EEOC 4/5ths Parity Rule      : {m_fair.passes_four_fifths_rule}")
    print(f"  - Model Compliance Status             : {m_fair.status}")
    print("-" * 115)


def demo_full_pipeline():
    """Run unified end-to-end Responsible AI evaluation cycle."""
    print("\n[4] PILLAR IV: END-TO-END RESPONSIBLE AI GATEWAY AUDIT CYCLE:")
    print("-" * 115)
    pipeline = ResponsibleAIPipeline()

    user_input = "Finance manager Priya Nair (priya.nair@linkific.in, Ph: +91 99887 76655) requests approval for INV-4491."
    source_doc = "INVOICE #INV-4491: Amount due USD $3,450.00 (INR 298,425.00) payable to CloudTech Systems for Cloud Hosting."
    llm_output = "Invoice #INV-4491 amount due USD $3,450.00 (INR 298,425.00) payable to CloudTech Systems for Cloud Hosting is fully verified."

    data_dir = os.path.join(BASE_DIR, "data")
    fair_file = os.path.join(data_dir, "fair_decision_log.json")
    with open(fair_file, "r") as f:
        fair_decisions = json.load(f)

    result = pipeline.run_full_guardrail_cycle(
        user_input_with_pii=user_input,
        simulated_llm_output=llm_output,
        reference_source_doc=source_doc,
        historical_decisions=fair_decisions,
    )

    audit = result["audit_record"]
    print(f"Audit Record ID        : {audit.record_id}")
    print(f"Timestamp              : {audit.timestamp}")
    print(f"Privacy PII Redactions : {audit.privacy_redactions_made} items masked")
    print(f"Grounding Passed       : {audit.grounding_passed} (Citation Score: {audit.citation_score:.2f})")
    print(f"Fairness Passed        : {audit.fairness_passed} (DIR: {audit.disparate_impact_ratio:.3f})")
    print(f"Final Decision         : {audit.overall_compliance_decision}")
    print("-" * 115)
    print("Responsible AI Proof of Concept execution finished successfully with 100% deterministic reproducibility.\n")


def main():
    parser = argparse.ArgumentParser(description="Day 26 Responsible AI Guardrail POC CLI")
    parser.add_argument(
        "--mode",
        choices=["all", "privacy", "grounding", "fairness", "pipeline"],
        default="all",
        help="Demonstration mode (default: all)",
    )
    args = parser.parse_args()

    print_banner()

    if args.mode in ["all", "privacy"]:
        demo_privacy_masking()
    if args.mode in ["all", "grounding"]:
        demo_hallucination_verification()
    if args.mode in ["all", "fairness"]:
        demo_fairness_audit()
    if args.mode in ["all", "pipeline"]:
        demo_full_pipeline()


if __name__ == "__main__":
    main()
