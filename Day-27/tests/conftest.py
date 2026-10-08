"""Pytest configuration and pythonpath resolution for Day 27."""

import sys
from pathlib import Path

# Add Day-27 directory to sys.path so 'app' package resolves cleanly
DAY27_DIR = Path(__file__).resolve().parent.parent
if str(DAY27_DIR) not in sys.path:
    sys.path.insert(0, str(DAY27_DIR))
