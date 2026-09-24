"""
Day 22 — Multi-Agent Research Assistant CLI Runner
Interactive demonstration script executing the 5-agent collaborative workflow:
Coordinator -> Research Agent -> Analyzer Agent -> Critic Agent (Revision Loop) -> Writer Agent
"""

import sys
import os
import argparse
import json

# Ensure Day-22 root is on sys.path
DAY22_DIR = os.path.dirname(os.path.abspath(__file__))
if DAY22_DIR not in sys.path:
    sys.path.insert(0, DAY22_DIR)

from app.workflow import MultiAgentWorkflowEngine


DEMO_QUERIES = [
    {
        "id": "1",
        "title": "Remote Work & Core Collaboration Hours (HR & InfoSec)",
        "query": "What are the corporate guidelines regarding remote work, hardware allowances, and core collaboration hours?"
    },
    {
        "id": "2",
        "title": "Engineering Standards & CI/CD SLA Verification (Eng & QA)",
        "query": "What are the engineering onboarding protocols, peer review requirements, and QA latency performance SLAs?"
    },
    {
        "id": "3",
        "title": "AI Model Governance & Incident Escalation (AI & SRE)",
        "query": "What are our mandatory AI safety principles, human oversight escalation triggers, and Sev-1 incident post-mortem requirements?"
    }
]


def print_banner():
    print("=" * 80)
    print("  LINKIFIC ENTERPRISE AI SERVICE — DAY 22")
    print("  Multi-Agent Research Assistant (5-Agent Collaborative Workflow)")
    print("=" * 80)
    print("Agent Topology:")
    print("  1. Coordinator Agent [Planning & Workflow State Orchestration]")
    print("  2. Research Agent    [Evidence Gathering & Corpus Retrieval]")
    print("  3. Analyzer Agent    [Insight Derivation & Thematic Synthesis]")
    print("  4. Critic Agent      [Adversarial Verification & Revision Quality Gate]")
    print("  5. Writer Agent      [Executive Report Generation & Citation Traceability]")
    print("=" * 80)


def run_demo(query: str, max_revisions: int = 2):
    print(f"\n[INIT] Initiating Multi-Agent Workflow Engine...")
    print(f"[QUERY] Target Research Brief: '{query}'")
    print(f"[CONFIG] Max Revisions Allowed: {max_revisions}\n")

    engine = MultiAgentWorkflowEngine(max_revisions=max_revisions)
    response = engine.run(query=query)

    print("\n" + "=" * 80)
    print(f"WORKFLOW EXECUTION SUMMARY: {response.workflow_id}")
    print("=" * 80)
    print(f"Status:            {response.status.value.upper()}")
    print(f"Execution Time:    {response.execution_time_seconds:.3f} seconds")
    print(f"Critic Approved:   {'YES' if response.critic_approved else 'NO (Circuit Breaker Override)'}")
    print(f"Revision Cycles:   {response.total_revisions}")
    print(f"Audit Events:      {response.audit_events_count} messages transmitted")
    
    if response.warnings:
        print(f"Warnings ({len(response.warnings)}):")
        for w in response.warnings:
            print(f"  - {w}")

    print("\n" + "-" * 80)
    print("EXECUTION MILESTONES")
    print("-" * 80)
    for m in response.execution_plan.milestones:
        print(f"Step {m.step_number}: [{m.assigned_agent.value}] {m.task_id} -> {m.description}")

    if response.final_report:
        report = response.final_report
        print("\n" + "=" * 80)
        print(f"FINAL DELIVERABLE: {report.title}")
        print("=" * 80)
        print(f"\nEXECUTIVE SUMMARY:\n{report.executive_summary}\n")

        print("SECTIONS & GROUNDED CITATIONS:")
        for sec in report.sections:
            cites = f" [Cited: {', '.join(sec.cited_sources)}]" if sec.cited_sources else ""
            print(f"\n### {sec.title}{cites}")
            print(sec.content)

        print("\nEVIDENCE TRACEABILITY MATRIX:")
        for ins_id, sids in report.evidence_traceability_matrix.items():
            print(f"  - {ins_id} -> Sources: {', '.join(sids)}")

        print("\nLIMITATIONS & OPERATIONAL BOUNDARIES:")
        for lim in report.limitations:
            print(f"  - {lim}")

        print("\nSTRATEGIC RECOMMENDATIONS:")
        for rec in report.recommendations:
            print(f"  - {rec}")
    else:
        print("\n[WARN] No final report generated due to workflow failure.")

    print("\n" + "=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Run Linkific Multi-Agent Research Assistant (Day 22)")
    parser.add_argument("--query", type=str, default=None, help="Custom research query to process")
    parser.add_argument("--demo", type=str, default="1", choices=["1", "2", "3"], help="Select pre-packaged demo query (1, 2, or 3)")
    parser.add_argument("--max-revisions", type=int, default=2, help="Max Critic revision rounds (default: 2)")

    args = parser.parse_args()

    print_banner()

    if args.query:
        target_query = args.query
    else:
        selected_demo = next(d for d in DEMO_QUERIES if d["id"] == args.demo)
        print(f"Executing Pre-Configured Scenario #{selected_demo['id']}: {selected_demo['title']}")
        target_query = selected_demo["query"]

    run_demo(query=target_query, max_revisions=args.max_revisions)


if __name__ == "__main__":
    main()
