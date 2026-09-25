"""
Day 23: Multi-Agent System CLI Execution Harness
Linkific Enterprise AI Service
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

from app.graph import MultiAgentWorkflowEngine
from app.schemas import WorkflowRequest, WorkflowStatus
from app.config import config

DEMO_SCENARIOS = [
    {
        "id": "1",
        "title": "Corporate Leave, Remote Work & Core Hours (HR & InfoSec)",
        "query": "What are the corporate guidelines regarding remote work, hardware allowances, and core collaboration hours?",
        "mode": "streamlined"
    },
    {
        "id": "2",
        "title": "Cloud Infrastructure, Kubernetes & Disaster Recovery (DevOps)",
        "query": "What are the infrastructure requirements for Kubernetes orchestration, RTO/RPO targets, and Terraform state encryption?",
        "mode": "streamlined"
    },
    {
        "id": "3",
        "title": "Comprehensive Multi-Domain Policy & Incident Response Audit",
        "query": "What are the protocols for Severity 1 production incident escalation, CI/CD code review SLAs, and test coverage gates?",
        "mode": "comprehensive"
    }
]


def print_banner():
    print("=" * 80)
    print("  LINKIFIC ENTERPRISE AI SERVICE — DAY 23")
    print("  LangGraph Multi-Agent System Implementation")
    print("=" * 80)
    print("Graph Architecture & Agent Roles:")
    print("  1. Coordinator Agent [Planning, Milestone Routing & Final Egress]")
    print("  2. Research Agent    [Enterprise Corpus Retrieval & Provenance Tracking]")
    print("  3. Analyzer Agent    [Thematic Synthesis & Cross-Policy Correlations]")
    print("  4. Critic Agent      [Adversarial Verification & Numerical Quality Gate]")
    print("  5. Writer Agent      [Executive Intelligence Briefing & Traceability]")
    print("  6. Error Handler     [Fault Recovery & Diagnostic Telemetry]")
    print("=" * 80)


def run_scenario(query: str, mode: str = "streamlined", save_log: bool = True):
    print(f"\n[INIT] Executing LangGraph Workflow in '{mode.upper()}' Mode...")
    print(f"[QUERY] Target Research Brief: '{query}'\n")

    engine = MultiAgentWorkflowEngine()
    request = WorkflowRequest(query=query, mode=mode)
    response = engine.execute(request)

    print("=" * 80)
    print(f"WORKFLOW EXECUTION SUMMARY: {response.workflow_id}")
    print("=" * 80)
    print(f"Status:            {response.status.value.upper()}")
    print(f"Execution Time:    {response.execution_time_seconds:.3f} seconds")
    print(f"Critic Approved:   {'YES' if response.critic_approved else 'NO'}")
    print(f"Milestones Track:  {len(response.milestones)} completed")
    print(f"Communication Log: {len(response.communication_log)} messages exchanged")
    print("-" * 80)

    print("\n--------------------------------------------------------------------------------")
    print("EXECUTION MILESTONES")
    print("--------------------------------------------------------------------------------")
    for m in response.milestones:
        print(f"Step {m.step_number}: [{m.assigned_agent.value}] {m.name} -> {m.status.upper()}")

    print("\n--------------------------------------------------------------------------------")
    print("MULTI-AGENT COMMUNICATION LOG")
    print("--------------------------------------------------------------------------------")
    for idx, msg in enumerate(response.communication_log, 1):
        print(f"Hop #{idx} [{msg.timestamp[11:19]} UTC] | {msg.sender.value} --> {msg.recipient.value}")
        print(f"       Type:    {msg.message_type.value.upper()}")
        print(f"       Summary: {msg.summary}")
        if msg.payload:
            payload_preview = json.dumps(msg.payload, indent=None)
            if len(payload_preview) > 100:
                payload_preview = payload_preview[:97] + "..."
            print(f"       Payload: {payload_preview}")
        print()

    print("=" * 80)
    print("FINAL DELIVERABLE: " + (response.executive_report.title if response.executive_report else "Response"))
    print("=" * 80)
    if response.executive_report:
        rep = response.executive_report
        print(f"\nEXECUTIVE SUMMARY:\n{rep.executive_summary}\n")

        print("SECTIONS & GROUNDED CITATIONS:")
        for sec in rep.sections:
            cites = f" [Cited: {', '.join(sec.cited_sources)}]" if sec.cited_sources else ""
            print(f"\n### {sec.title}{cites}")
            print(sec.content)

        print("\nEVIDENCE TRACEABILITY MATRIX:")
        for claim_id, sids in rep.evidence_traceability_matrix.items():
            print(f"  - {claim_id} -> Sources: {', '.join(sids)}")

        print("\nLIMITATIONS & OPERATIONAL BOUNDARIES:")
        for lim in rep.limitations:
            print(f"  - {lim}")

        print("\nSTRATEGIC RECOMMENDATIONS:")
        for rec in rep.recommendations:
            print(f"  - {rec}")
    else:
        print(f"\nFINAL ANSWER:\n{response.final_answer}\n")

    print("\n" + "=" * 80)

    # Save communication log if requested
    if save_log:
        log_path = Path(config.communication_log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        serialized_log = [msg.model_dump() for msg in response.communication_log]
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(serialized_log, f, indent=2)
        print(f"[AUDIT] Saved {len(serialized_log)} message records to: {log_path}")

        # Also write sample interaction trace
        trace_path = config.base_dir / "examples" / "sample_interaction_trace.json"
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        with open(trace_path, "w", encoding="utf-8") as f:
            json.dump(response.model_dump(), f, indent=2)
        print(f"[AUDIT] Saved full serialized trace to: {trace_path}")

    return response


def main():
    parser = argparse.ArgumentParser(description="Run Linkific LangGraph Multi-Agent System (Day 23)")
    parser.add_argument("--query", "-q", type=str, default=None, help="Custom research query to process")
    parser.add_argument("--mode", "-m", type=str, default="streamlined", choices=["streamlined", "comprehensive"], help="Pipeline execution topology")
    parser.add_argument("--scenario", "--demo", "-s", dest="scenario", type=str, default="1", choices=["1", "2", "3"], help="Select pre-packaged scenario (1, 2, or 3)")
    parser.add_argument("--all", action="store_true", help="Execute all 3 pre-packaged scenarios consecutively")
    parser.add_argument("--interactive", "-i", action="store_true", help="Launch interactive multi-turn session")

    args = parser.parse_args()

    print_banner()

    if args.interactive:
        print("\n[INTERACTIVE MODE] Type your research query (or 'exit' to quit):")
        while True:
            try:
                user_q = input("\nEnter research query > ").strip()
                if user_q.lower() in ("exit", "quit", "q"):
                    print("Exiting interactive mode.")
                    break
                if not user_q:
                    continue
                run_scenario(user_q, mode=args.mode)
            except (KeyboardInterrupt, EOFError):
                break
    elif args.all:
        for sc in DEMO_SCENARIOS:
            print(f"\nExecuting Pre-Configured Scenario #{sc['id']}: {sc['title']}")
            run_scenario(sc["query"], mode=sc["mode"])
    elif args.query:
        run_scenario(args.query, mode=args.mode)
    else:
        sc = next(s for s in DEMO_SCENARIOS if s["id"] == args.scenario)
        print(f"\nExecuting Pre-Configured Scenario #{sc['id']}: {sc['title']}")
        run_scenario(sc["query"], mode=sc["mode"])


if __name__ == "__main__":
    main()
