"""Cross-day regression test suite verifying stability of Days 20-26 modules."""

import os
import pytest

ROOT_DIR = r"C:\projects\linkific\internship"


def test_day26_responsible_ai_suite_exists():
    """Verify Day 26 Responsible AI deliverables and code integrity."""
    day26_path = os.path.join(ROOT_DIR, "Day-26")
    assert os.path.exists(os.path.join(day26_path, "run_responsible_ai.py"))
    assert os.path.exists(os.path.join(day26_path, "app", "models.py"))
    assert os.path.exists(os.path.join(day26_path, "app", "guardrails"))
    assert os.path.exists(os.path.join(day26_path, "docs", "CASE_STUDY_REPORT.md"))
    assert os.path.exists(os.path.join(day26_path, "docs", "RESPONSIBLE_AI_GUIDELINES.md"))
    assert os.path.exists(os.path.join(day26_path, "docs", "RESPONSIBLE_AI_SUMMARY.md"))
    assert os.path.exists(os.path.join(day26_path, "tests"))


def test_day25_benchmark_suite_exists():
    """Verify Day 25 Multi-Provider LLM Benchmark code integrity."""
    day25_path = os.path.join(ROOT_DIR, "Day-25")
    assert os.path.exists(os.path.join(day25_path, "run_benchmark.py"))
    assert os.path.exists(os.path.join(day25_path, "app", "database.py"))
    assert os.path.exists(os.path.join(day25_path, "app", "cost_calculator.py"))
    assert os.path.exists(os.path.join(day25_path, "tests"))


def test_day24_fastapi_and_docker_exist():
    """Verify Day 24 Production AI API and Docker configs."""
    day24_path = os.path.join(ROOT_DIR, "Day-24")
    assert os.path.exists(os.path.join(day24_path, "run_service.py"))
    assert os.path.exists(os.path.join(day24_path, "app"))
    assert os.path.exists(os.path.join(day24_path, "tests"))
    assert os.path.exists(os.path.join(day24_path, "Dockerfile"))
    assert os.path.exists(os.path.join(day24_path, "docker-compose.yml"))


def test_day23_multi_agent_system_exists():
    """Verify Day 23 Multi-Agent architecture files."""
    day23_path = os.path.join(ROOT_DIR, "Day-23")
    assert os.path.exists(os.path.join(day23_path, "run_agents.py"))
    assert os.path.exists(os.path.join(day23_path, "app"))
    assert os.path.exists(os.path.join(day23_path, "tests"))


def test_day22_celery_and_tasks_exist():
    """Verify Day 22 Celery asynchronous task modules."""
    day22_path = os.path.join(ROOT_DIR, "Day-22")
    assert os.path.exists(day22_path)
    assert os.path.exists(os.path.join(day22_path, "tests"))


def test_day21_database_and_crud_exist():
    """Verify Day 21 SQLAlchemy database CRUD modules."""
    day21_path = os.path.join(ROOT_DIR, "Day-21")
    assert os.path.exists(day21_path)
    assert os.path.exists(os.path.join(day21_path, "tests"))


def test_day20_advanced_rag_exists():
    """Verify Day 20 Advanced RAG modules."""
    day20_path = os.path.join(ROOT_DIR, "Day-20")
    assert os.path.exists(day20_path)
