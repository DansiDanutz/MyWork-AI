#!/usr/bin/env python3
"""Tests for tools/brain_learner.py"""

import pytest
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

try:
    import brain_learner
except ImportError:
    pytest.skip("Cannot import brain_learner", allow_module_level=True)


def test_run_daily_learning_exists():
    """Verify run_daily_learning is callable."""
    assert callable(getattr(brain_learner, "run_daily_learning", None))

def test_run_weekly_learning_exists():
    """Verify run_weekly_learning is callable."""
    assert callable(getattr(brain_learner, "run_weekly_learning", None))

def test_run_discover_exists():
    """Verify run_discover is callable."""
    assert callable(getattr(brain_learner, "run_discover", None))

def test_main_exists():
    """Verify main is callable."""
    assert callable(getattr(brain_learner, "main", None))
