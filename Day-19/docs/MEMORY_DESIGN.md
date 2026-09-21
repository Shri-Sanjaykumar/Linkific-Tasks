# Memory Architecture & State Checkpointing — Day 19

## 1. Architectural Memory Taxonomy

In LangGraph workflows, memory operates across three distinct operational tiers:

```
+-----------------------------------------------------------------------+
|  Tier 1: Graph Execution State (Volatile / Node-to-Node)              |
|  - Managed via WorkflowState(TypedDict)                               |
|  - Passed directly from node to node during a single invocation       |
|  - Ephemeral: Resets turn-specific counters on each new invocation    |
+-----------------------------------------------------------------------+
                                   │
                                   ▼
+-----------------------------------------------------------------------+
|  Tier 2: Short-Term Thread Checkpoint Memory (Session-Level)          |
|  - Managed via langgraph.checkpoint.memory.InMemorySaver             |
|  - Scoped by configurable `thread_id`                                 |
|  - Preserves `conversation_history` across multiple turns             |
|  - Survives across multiple graph.invoke() calls in the same process  |
+-----------------------------------------------------------------------+
                                   │
                                   ▼
+-----------------------------------------------------------------------+
|  Tier 3: Long-Term Persistent Storage (Enterprise / Production)       |
|  - E.g., PostgresSaver, RedisSaver, DynamoDBSaver                    |
|  - Survives process crashes, server restarts, and container scaling   |
|  - Out of scope for this local educational prototype                  |
+-----------------------------------------------------------------------+
```

---

## 2. Checkpointer Mechanics: `InMemorySaver`

- **Class Usage:** We utilize `langgraph.checkpoint.memory.InMemorySaver` as the primary checkpointer class. (`MemorySaver` is retained as a backwards-compatible alias).
- **Compilation Binding:**
  ```python
  from langgraph.checkpoint.memory import InMemorySaver
  from app.workflow import create_workflow

  checkpointer = InMemorySaver()
  graph = create_workflow().compile(checkpointer=checkpointer)
  ```
- **Thread Invocation:**
  ```python
  config = {"configurable": {"thread_id": "session-101"}}
  result = graph.invoke({"question": "..."}, config=config)
  ```

---

## 3. History Preservation in `initialize_state`

A common defect in naive LangGraph implementations is overwriting existing conversation history on every call:

```python
# DEFECTIVE APPROACH: Overwrites restored checkpoint state!
def initialize_state(state):
    return {"conversation_history": []}
```

Our implementation explicitly preserves restored conversation history:

```python
# CORRECT IMPLEMENTATION in app/nodes.py:
def initialize_state(state: WorkflowState) -> Dict[str, Any]:
    raw_question = state.get("question", "")
    question = clean_text(raw_question)
    
    # Restore existing session history from checkpointer
    existing_history = list(state.get("conversation_history") or [])
    existing_trace = list(state.get("execution_trace") or [])

    return {
        "question": question,
        "original_question": question,
        "retrieval_query": question,
        "conversation_history": existing_history,       # Preserved!
        "execution_trace": existing_trace + [...],      # Preserved!
        "retrieval_attempts": 0,                        # Reset for this turn
        "status": "initialized",
        ...
    }
```

---

## 4. Multi-Turn Demonstration

| Turn | User Input | State In History | State Out History | Refined Search Query |
|:---:|:---|:---:|:---:|:---|
| **Turn 1** | *"What are the steps in the onboarding process?"* | `[]` (0 items) | `[Turn 1]` (1 item) | `"What are the steps in the onboarding process?"` |
| **Turn 2** | *"What should I complete first?"* | `[Turn 1]` (1 item) | `[Turn 1, Turn 2]` (2 items) | `"onboarding complete first"` (expanded with Turn 1 topic) |

When a different `thread_id` is supplied (e.g., `session-999`), `InMemorySaver` provides a fresh checkpoint with an empty history.
