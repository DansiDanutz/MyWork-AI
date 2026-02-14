#!/usr/bin/env python3
"""Tests for tools/smoke_test_task_tracker.py"""

import pytest
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

try:
    import smoke_test_task_tracker
except ImportError:
    pytest.skip("Cannot import smoke_test_task_tracker", allow_module_level=True)


def test_fetch_exists():
    """Verify fetch is callable."""
    assert callable(getattr(smoke_test_task_tracker, "fetch", None))

def test_assert_ok_exists():
    """Verify assert_ok is callable."""
    assert callable(getattr(smoke_test_task_tracker, "assert_ok", None))

def test_main_exists():
    """Verify main is callable."""
    assert callable(getattr(smoke_test_task_tracker, "main", None))
