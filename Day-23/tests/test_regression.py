"""
Day 23 — Cross-Project Regression & Integration Tests
Confirms that earlier days' services and frameworks (Days 17, 20, 21, 22)
remain completely intact, functional, and uncompromised by Day 23 LangGraph implementation.
"""

import sys
import os
import subprocess
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_day17_regression_imports():
    """Verify Day 17 FastAPI RAG modules remain importable in isolated process."""
    day17_dir = os.path.join(REPO_ROOT, "Day-17")
    if os.path.exists(day17_dir):
        cmd = [sys.executable, "-c", "import app.main; assert app.main.app is not None"]
        proc = subprocess.run(cmd, cwd=day17_dir, capture_output=True, text=True)
        assert proc.returncode == 0, f"Day 17 import failed: {proc.stderr}"


def test_day20_regression_imports():
    """Verify Day 20 Function Calling and Tool Engine modules remain importable in isolated process."""
    day20_dir = os.path.join(REPO_ROOT, "Day-20")
    if os.path.exists(day20_dir):
        cmd = [sys.executable, "-c", "from app.engine import FunctionCallingEngine; assert FunctionCallingEngine is not None"]
        proc = subprocess.run(cmd, cwd=day20_dir, capture_output=True, text=True)
        assert proc.returncode == 0, f"Day 20 import failed: {proc.stderr}"


def test_day21_regression_imports():
    """Verify Day 21 Async FastAPI service and dependencies remain importable in isolated process."""
    day21_dir = os.path.join(REPO_ROOT, "Day-21")
    if os.path.exists(day21_dir):
        cmd = [sys.executable, "-c", "import app.main; from app.services.async_service import AsyncDataService; assert app.main.app is not None"]
        proc = subprocess.run(cmd, cwd=day21_dir, capture_output=True, text=True)
        assert proc.returncode == 0, f"Day 21 import failed: {proc.stderr}"


def test_day22_regression_workflow():
    """Verify Day 22 Multi-Agent workflow runs cleanly and preserves exact facts."""
    day22_dir = os.path.join(REPO_ROOT, "Day-22")
    if os.path.exists(day22_dir):
        cmd = [
            sys.executable,
            "-c",
            "from app.workflow import MultiAgentWorkflowEngine; "
            "from app.schemas import WorkflowStatus; "
            "wf = MultiAgentWorkflowEngine(); "
            "resp = wf.run('leave policy'); "
            "assert resp.status == WorkflowStatus.COMPLETED; "
            "assert '1.5' in resp.final_report.markdown_output"
        ]
        proc = subprocess.run(cmd, cwd=day22_dir, capture_output=True, text=True)
        assert proc.returncode == 0, f"Day 22 workflow failed: {proc.stderr}"
