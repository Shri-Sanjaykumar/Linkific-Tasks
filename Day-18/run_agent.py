"""
Day 18 — Interactive AI Agent CLI Runner
Allows users to run benchmark queries, test custom inquiries,
or enter an interactive Q&A session with the Document Research Assistant Agent.

Usage:
  python run_agent.py                     # Interactive mode
  python run_agent.py --demo              # Run the 3 official benchmark queries
  python run_agent.py --query "your question"  # Run a single query
"""

import sys
import argparse
from agent import DocumentResearchAgent


def print_response(res):
    print("\n" + "=" * 75)
    print(f"QUESTION: {res.question}")
    print("=" * 75)
    print(f"STATUS:   {res.status}")
    print(f"TOOLS:    {', '.join(res.tools_used)}")
    print(f"SOURCES:  {', '.join(res.sources) if res.sources else 'None (Safe Refusal / Out-of-Domain)'}")
    print("-" * 75)
    print("ANSWER:")
    print(f"  {res.answer}")
    print("-" * 75)
    print("REACT EXECUTION TRACE:")
    for i, step in enumerate(res.execution_trace, 1):
        state = step.get("state", "")
        tool = step.get("tool") or "-"
        act = step.get("action_or_plan", "")
        obs = step.get("observation")
        dec = step.get("decision")
        print(f"  [{i}] {state:7s} | Tool: {tool:17s} | {act}")
        if obs:
            print(f"               Observation: {obs}")
        if dec:
            print(f"               Decision:    {dec}")
    print("=" * 75 + "\n")


def run_demo():
    print("\n>>> RUNNING DAY 18 OFFICIAL BENCHMARK DEMO (5 BENCHMARK SCENARIOS)...")
    agent = DocumentResearchAgent()
    demo_queries = [
        "What is the leave policy?",
        "What are the training requirements?",
        "What is the company's stock price?",
        "Look up DOC-WORKFLOW-004 in detail",
        "Who is the author and version of DOC-ONBOARD-002?"
    ]
    for q in demo_queries:
        res = agent.run(q)
        print_response(res)


def interactive_mode():
    print("\n" + "=" * 75)
    print("  Linkific Document Research Assistant Agent (Day 18)")
    print("  Type your question below (or 'exit' / 'quit' to stop).")
    print("=" * 75 + "\n")
    agent = DocumentResearchAgent()
    while True:
        try:
            q = input("Question > ").strip()
            if not q:
                continue
            if q.lower() in ("exit", "quit", "q"):
                print("Exiting Document Research Assistant Agent. Goodbye!")
                break
            res = agent.run(q)
            print_response(res)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break


def main():
    parser = argparse.ArgumentParser(description="Day 18 Document Research Assistant Agent")
    parser.add_argument("--demo", action="store_true", help="Run the 3 benchmark queries")
    parser.add_argument("--query", "-q", type=str, help="Run a single question")
    args = parser.parse_args()

    if args.demo:
        run_demo()
    elif args.query:
        agent = DocumentResearchAgent()
        res = agent.run(args.query)
        print_response(res)
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
