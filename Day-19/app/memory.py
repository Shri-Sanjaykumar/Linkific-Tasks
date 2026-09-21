"""
Thread-scoped checkpoint memory management for Day 19 using LangGraph InMemorySaver.
"""

from typing import Optional, Dict, Any
from langgraph.checkpoint.memory import InMemorySaver
from .workflow import compile_workflow

# Primary checkpointer singleton for interactive sessions
_shared_checkpointer: Optional[InMemorySaver] = None

def get_in_memory_checkpointer() -> InMemorySaver:
    """
    Instantiate or return the shared InMemorySaver checkpointer.
    Note: MemorySaver is retained in LangGraph as an alias for backwards compatibility.
    """
    global _shared_checkpointer
    if _shared_checkpointer is None:
        _shared_checkpointer = InMemorySaver()
    return _shared_checkpointer

def create_workflow_with_memory(checkpointer: Optional[InMemorySaver] = None):
    """
    Build and compile a LangGraph workflow pre-configured with InMemorySaver thread checkpointing.
    """
    cp = checkpointer or get_in_memory_checkpointer()
    return compile_workflow(checkpointer=cp)

def get_thread_config(thread_id: str) -> Dict[str, Any]:
    """
    Construct the LangGraph invocation config dictionary for a given thread_id.
    """
    return {
        "configurable": {
            "thread_id": thread_id
        }
    }
