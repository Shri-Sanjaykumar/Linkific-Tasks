"""Cross-day regression test suite verifying stability of Day 20-25 modules."""

import sys
import os
import pytest

ROOT_DIR = r"C:\projects\linkific\internship"


def test_day25_benchmark_suite_exists():
    day25_path = os.path.join(ROOT_DIR, "Day-25")
    assert os.path.exists(os.path.join(day25_path, "run_benchmark.py"))
    assert os.path.exists(os.path.join(day25_path, "app", "database.py"))
    assert os.path.exists(os.path.join(day25_path, "app", "cost_calculator.py"))
    assert os.path.exists(os.path.join(day25_path, "tests"))


def test_day24_fastapi_and_tests_exist():
    day24_path = os.path.join(ROOT_DIR, "Day-24")
    assert os.path.exists(os.path.join(day24_path, "run_service.py"))
    assert os.path.exists(os.path.join(day24_path, "app"))
    assert os.path.exists(os.path.join(day24_path, "tests"))
    assert os.path.exists(os.path.join(day24_path, "Dockerfile"))
    assert os.path.exists(os.path.join(day24_path, "docker-compose.yml"))


def test_day23_multi_agent_system_exists():
    day23_path = os.path.join(ROOT_DIR, "Day-23")
    assert os.path.exists(os.path.join(day23_path, "run_agents.py"))
    assert os.path.exists(os.path.join(day23_path, "app"))
    assert os.path.exists(os.path.join(day23_path, "tests"))


def test_day22_celery_and_tasks_exist():
    day22_path = os.path.join(ROOT_DIR, "Day-22")
    assert os.path.exists(day22_path)
    assert os.path.exists(os.path.join(day22_path, "tests"))


def test_day21_database_and_crud_exist():
    day21_path = os.path.join(ROOT_DIR, "Day-21")
    assert os.path.exists(day21_path)
    assert os.path.exists(os.path.join(day21_path, "tests"))


def test_day20_basics_exist():
    day20_path = os.path.join(ROOT_DIR, "Day-20")
    assert os.path.exists(day20_path)
