# Error Handling Notes & Failure Modes — Day 19

## 1. Structured Error Handling Matrix

The workflow enforces explicit error detection, isolation, and recovery across all eight execution stages:

| Failure Scenario | Detection Point | Detection Logic | Recovery Action | Final System Behavior |
|:---|:---|:---|:---|:---|
| **Empty Question** | `initialize_state` (Node 1) | `len(question.strip()) == 0` | Immediate rejection; bypass retrieval nodes | Returns `FALLBACK_EMPTY_INPUT`; status `fallback_completed` |
| **Whitespace Question** | `initialize_state` (Node 1) | Cleaned string is empty | Immediate rejection; bypass retrieval nodes | Returns `FALLBACK_EMPTY_INPUT`; status `fallback_completed` |
| **Short Question (< 3 chars)** | `initialize_state` (Node 1) | `len(question) < 3` | Immediate rejection | Returns `FALLBACK_EMPTY_INPUT`; status `fallback_completed` |
| **Retriever Exception** | `retrieve_documents` (Node 2) | `try ... except Exception` block | Error caught, status set to `retrieval_error`, error logged | Routes via `route_after_retrieval` to `handle_failure`; returns `FALLBACK_RETRIEVAL_ERROR` |
| **Insufficient Context (Pass 1)** | `validate_context` (Node 3) | `max_score < 0.45` | Routes via `route_after_validation` to query refiner | Modifies query terms and cycles back to `retrieve_documents` |
| **Retry Limit Reached** | `route_after_validation` | `retrieval_attempts > max_retries` | Halts cyclic loop | Routes to `handle_failure`; returns `FALLBACK_NO_CONTEXT` |
| **Generation Exception** | `generate_answer` (Node 5) | `try ... except Exception` block | Error caught, status set to `generation_error` | Routes via `route_after_generation` to `handle_failure`; returns `FALLBACK_GENERATION_ERROR` |
| **Duplicate Memory Append** | `update_memory` (Node 7) | Check last turn against current Q&A | Suppresses duplicate entries during retries | Preserves single clean history record per user turn |

---

## 2. Defensive Design Principles

1. **No Silent Exception Swallowing:**
   Every `try/except` block captures the exact exception string and writes it to `state["error_message"]` and `state["execution_trace"]`.
2. **No Stack Trace Exposure:**
   End users are never exposed to Python tracebacks or raw database errors. Internal errors are mapped to polite, actionable fallback messages.
3. **Strict Loop Bounding:**
   Every cycle through the graph increments `retrieval_attempts`. The conditional edge checks `attempts <= max_retries`, guaranteeing termination within 3 total attempts.
4. **Non-Destructive Test Hooks:**
   The retriever includes `set_simulate_error(True/False)` for automated testing of network/database outages without altering actual configuration files.
