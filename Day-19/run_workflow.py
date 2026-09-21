"""
CLI, Interactive Session, and Scenario Runner for Day 19 LangGraph Stateful Workflow.
Supports:
1. Interactive multi-turn Q&A sessions with thread memory persistence (--interactive)
2. Automated execution of all 5 verification scenarios (--run-all-scenarios)
3. Single ad-hoc queries (--query)
"""

import sys
import os
import json
import argparse
from typing import Dict, Any, Optional, Callable

# Ensure Day-19 is on Python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from app import compile_workflow, get_in_memory_checkpointer, LocalDocumentRetriever
from app.memory import get_thread_config, InMemorySaver

EXIT_COMMANDS = {"exit", "quit", "q"}

def run_interactive_session(
    thread_id: str = "interactive-session",
    checkpointer: Optional[InMemorySaver] = None,
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print
) -> None:
    """
    Run an interactive multi-turn question-answering session.
    Preserves conversation memory across unlimited questions by reusing the same thread ID.
    Supports clean exit commands ('exit', 'quit', 'q') and safely handles blank inputs.
    """
    cp = checkpointer or get_in_memory_checkpointer()
    graph = compile_workflow(checkpointer=cp)
    config = get_thread_config(thread_id)

    output_fn("\n" + "="*80)
    output_fn("DAY 19: LANGGRAPH INTERACTIVE DOCUMENT ASSISTANT")
    output_fn("="*80)
    output_fn(f"Session Thread ID : {thread_id}")
    output_fn("Documentation Corpus: Synthetic Organizational Policies (Onboarding, Leave, Training, SDLC)")
    output_fn("Exit Commands       : 'exit', 'quit', or 'q' to safely end session.")
    output_fn("="*80 + "\n")

    turn_count = 0

    while True:
        try:
            raw_input = input_fn("User > ")
        except (EOFError, KeyboardInterrupt):
            output_fn("\n\n[Session Interrupted] Closing interactive Q&A session. Goodbye!\n")
            break

        cleaned_input = raw_input.strip()

        # 1. Exit command handling: stop safely without running graph or producing errors
        if cleaned_input.lower() in EXIT_COMMANDS:
            output_fn("\n[Session Ended] Interactive Q&A session closed. Goodbye!\n")
            break

        # 2. Blank input handling: prompt user without invoking graph
        if not cleaned_input:
            output_fn("[Notice] Question cannot be blank. Please enter a question or type 'exit' to quit.\n")
            continue

        turn_count += 1
        output_fn(f"\n[Processing Turn {turn_count} in thread '{thread_id}']...")

        try:
            result = graph.invoke({"question": cleaned_input}, config=config)
            status = result.get("status", "unknown")
            answer = result.get("answer", "")
            sources = result.get("sources", [])
            attempts = result.get("retrieval_attempts", 1)
            history_len = len(result.get("conversation_history", []))

            output_fn(f"\nAssistant (Status: {status} | Attempts: {attempts} | History: {history_len} turns):")
            output_fn("-" * 70)
            output_fn(answer)
            output_fn("-" * 70)
            if sources:
                output_fn(f"Sources Cited: {', '.join(sources)}")
            output_fn("")
        except Exception as exc:
            output_fn(f"\n[Error] An unexpected error occurred during execution: {exc}\n")

def run_scenario_1_normal() -> Dict[str, Any]:
    print("\n" + "="*80)
    print("SCENARIO 1: Normal Question (Employee Onboarding Steps)")
    print("="*80)
    
    cp = get_in_memory_checkpointer()
    graph = compile_workflow(checkpointer=cp)
    config = get_thread_config("thread-scenario-1")
    
    question = "What are the steps in the onboarding process?"
    print(f"User Query: {question}")
    
    result = graph.invoke({"question": question}, config=config)
    
    print(f"Status: {result.get('status')}")
    print(f"Context Sufficient: {result.get('context_sufficient')}")
    print(f"Retrieval Attempts: {result.get('retrieval_attempts')}")
    print(f"Sources Cited: {result.get('sources')}")
    print("\nSynthesized Answer:\n" + result.get("answer", ""))
    
    return result

def run_scenario_2_training() -> Dict[str, Any]:
    print("\n" + "="*80)
    print("SCENARIO 2: Training Policy Question (Submission Guidelines & Attendance)")
    print("="*80)
    
    cp = get_in_memory_checkpointer()
    graph = compile_workflow(checkpointer=cp)
    config = get_thread_config("thread-scenario-2")
    
    question = "What are the training attendance criteria and task submission deadlines?"
    print(f"User Query: {question}")
    
    result = graph.invoke({"question": question}, config=config)
    
    print(f"Status: {result.get('status')}")
    print(f"Context Sufficient: {result.get('context_sufficient')}")
    print(f"Retrieval Attempts: {result.get('retrieval_attempts')}")
    print(f"Sources Cited: {result.get('sources')}")
    print("\nSynthesized Answer:\n" + result.get("answer", ""))
    
    return result

def run_scenario_3_insufficient() -> Dict[str, Any]:
    print("\n" + "="*80)
    print("SCENARIO 3: Insufficient Context & Out-of-Domain (Weather on Mars)")
    print("="*80)
    
    cp = get_in_memory_checkpointer()
    graph = compile_workflow(checkpointer=cp)
    config = get_thread_config("thread-scenario-3")
    
    question = "What is the weather on Mars tomorrow?"
    print(f"User Query: {question}")
    
    result = graph.invoke({"question": question}, config=config)
    
    print(f"Status: {result.get('status')}")
    print(f"Context Sufficient: {result.get('context_sufficient')}")
    print(f"Retrieval Attempts: {result.get('retrieval_attempts')}")
    print(f"Error / Fallback Reason: {result.get('error_message')}")
    print("\nFallback Answer:\n" + result.get("answer", ""))
    
    return result

def run_scenario_4_retrieval_failure() -> Dict[str, Any]:
    print("\n" + "="*80)
    print("SCENARIO 4: Controlled Retrieval Failure & Graceful Recovery")
    print("="*80)
    
    retriever = LocalDocumentRetriever.get_instance()
    retriever.set_simulate_error(True)
    
    try:
        cp = get_in_memory_checkpointer()
        graph = compile_workflow(checkpointer=cp)
        config = get_thread_config("thread-scenario-4")
        
        question = "How do I request annual earned leave?"
        print(f"User Query: {question}")
        print("Note: Injected simulated retriever connection error.")
        
        result = graph.invoke({"question": question}, config=config)
        
        print(f"Status: {result.get('status')}")
        print(f"Context Sufficient: {result.get('context_sufficient')}")
        print(f"Error Message: {result.get('error_message')}")
        print("\nSafe Fallback Answer:\n" + result.get("answer", ""))
        
        return result
    finally:
        retriever.set_simulate_error(False)

def run_scenario_5_memory_followup() -> Dict[str, Any]:
    print("\n" + "="*80)
    print("SCENARIO 5: Multi-Turn Conversation with Thread-Based Checkpoint Memory")
    print("="*80)
    
    cp = get_in_memory_checkpointer()
    graph = compile_workflow(checkpointer=cp)
    thread_id = "thread-multi-turn-005"
    config = get_thread_config(thread_id)
    
    # Turn 1
    q1 = "What are the steps in the onboarding process?"
    print(f"\n[Turn 1] Question: {q1}")
    res1 = graph.invoke({"question": q1}, config=config)
    print(f"[Turn 1] Status: {res1.get('status')} | History Length: {len(res1.get('conversation_history', []))}")
    print(f"[Turn 1] Answer Preview: {res1.get('answer', '')[:100]}...")
    
    # Turn 2
    q2 = "What should I complete first?"
    print(f"\n[Turn 2] Question: {q2}")
    res2 = graph.invoke({"question": q2}, config=config)
    print(f"[Turn 2] Status: {res2.get('status')} | History Length: {len(res2.get('conversation_history', []))}")
    print(f"[Turn 2] Refined Query: {res2.get('retrieval_query')}")
    print(f"[Turn 2] Answer Preview: {res2.get('answer', '')[:100]}...")
    
    return {
        "thread_id": thread_id,
        "turn_1": res1,
        "turn_2": res2
    }

def export_artifacts(results: Dict[str, Any]) -> None:
    examples_dir = os.path.join(CURRENT_DIR, "examples")
    outputs_dir = os.path.join(CURRENT_DIR, "outputs")
    os.makedirs(examples_dir, exist_ok=True)
    os.makedirs(outputs_dir, exist_ok=True)
    
    with open(os.path.join(examples_dir, "normal_question.json"), "w", encoding="utf-8") as f:
        json.dump(results["scenario_1"], f, indent=2)
        
    with open(os.path.join(examples_dir, "insufficient_context.json"), "w", encoding="utf-8") as f:
        json.dump(results["scenario_3"], f, indent=2)
        
    with open(os.path.join(examples_dir, "retry_recovery.json"), "w", encoding="utf-8") as f:
        json.dump({
            "scenario": "insufficient_context_with_retries",
            "retrieval_attempts": results["scenario_3"].get("retrieval_attempts"),
            "max_retries": results["scenario_3"].get("max_retries"),
            "final_status": results["scenario_3"].get("status"),
            "execution_trace": results["scenario_3"].get("execution_trace")
        }, f, indent=2)
        
    with open(os.path.join(examples_dir, "memory_followup.json"), "w", encoding="utf-8") as f:
        json.dump(results["scenario_5"], f, indent=2)

    trace_path = os.path.join(outputs_dir, "execution_trace.md")
    with open(trace_path, "w", encoding="utf-8") as f:
        f.write("# Day 19 LangGraph Execution Trace Report\n\n")
        f.write("Generated from live execution of the 5 manual verification scenarios.\n\n")
        
        for name, data in [
            ("Scenario 1: Normal Question", results["scenario_1"]),
            ("Scenario 2: Training Guidelines", results["scenario_2"]),
            ("Scenario 3: Insufficient Context & Safe Fallback", results["scenario_3"]),
            ("Scenario 4: Controlled Retrieval Error Recovery", results["scenario_4"]),
            ("Scenario 5 (Turn 1): Multi-turn Memory Initiation", results["scenario_5"]["turn_1"]),
            ("Scenario 5 (Turn 2): Multi-turn Memory Follow-up", results["scenario_5"]["turn_2"]),
        ]:
            f.write(f"## {name}\n\n")
            f.write(f"- **Input Question:** {data.get('original_question') or data.get('question')}\n")
            f.write(f"- **Final Status:** `{data.get('status')}`\n")
            f.write(f"- **Context Sufficient:** `{data.get('context_sufficient')}`\n")
            f.write(f"- **Retrieval Attempts:** `{data.get('retrieval_attempts')}` (max retries: {data.get('max_retries')})\n")
            f.write(f"- **Sources Cited:** {data.get('sources', [])}\n\n")
            f.write("### Execution Trace:\n```text\n")
            for step in data.get("execution_trace", []):
                f.write(f"  -> {step}\n")
            f.write("```\n\n")
            f.write("### Final Answer / Fallback:\n")
            f.write(f"> {data.get('answer', '').replace(chr(10), chr(10) + '> ')}\n\n")
            f.write("---\n\n")

    print("\n[SUCCESS] Successfully exported JSON snapshots to examples/ and trace report to outputs/execution_trace.md")

def main():
    parser = argparse.ArgumentParser(description="Day 19 LangGraph Workflow Runner & Interactive Assistant")
    parser.add_argument("--interactive", action="store_true", help="Start an interactive multi-turn Q&A session")
    parser.add_argument("--run-all-scenarios", action="store_true", help="Execute all 5 scenarios and export traces")
    parser.add_argument("--query", type=str, help="Run single question query")
    parser.add_argument("--thread-id", type=str, default="my-session", help="Thread ID for session memory")
    args = parser.parse_args()

    if args.interactive:
        run_interactive_session(thread_id=args.thread_id)
    elif args.run_all_scenarios:
        s1 = run_scenario_1_normal()
        s2 = run_scenario_2_training()
        s3 = run_scenario_3_insufficient()
        s4 = run_scenario_4_retrieval_failure()
        s5 = run_scenario_5_memory_followup()
        
        all_results = {
            "scenario_1": s1,
            "scenario_2": s2,
            "scenario_3": s3,
            "scenario_4": s4,
            "scenario_5": s5
        }
        export_artifacts(all_results)
    elif args.query:
        cp = get_in_memory_checkpointer()
        graph = compile_workflow(checkpointer=cp)
        cfg = get_thread_config(args.thread_id)
        res = graph.invoke({"question": args.query}, config=cfg)
        print("\nWorkflow Result:")
        print(f"Status: {res.get('status')}")
        print(f"Answer:\n{res.get('answer')}")
    else:
        # Default behavior if run without args: launch interactive session
        print("No specific mode specified. Launching interactive Q&A session...")
        run_interactive_session(thread_id=args.thread_id)

if __name__ == "__main__":
    main()
