#!/usr/bin/env python3
"""Tests for tools/metrics.py"""

import pytest
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

try:
    import metrics
except ImportError:
    pytest.skip("Cannot import metrics", allow_module_level=True)


def test_should_skip_exists():
    """Verify should_skip is callable."""
    assert callable(getattr(metrics, "should_skip", None))

def test_count_lines_exists():
    """Verify count_lines is callable."""
    assert callable(getattr(metrics, "count_lines", None))

def test_is_test_file_exists():
    """Verify is_test_file is callable."""
    assert callable(getattr(metrics, "is_test_file", None))

def test_python_complexity_exists():
    """Verify python_complexity is callable."""
    assert callable(getattr(metrics, "python_complexity", None))

def test_detect_tech_debt_exists():
    """Verify detect_tech_debt is callable."""
    assert callable(getattr(metrics, "detect_tech_debt", None))

def test_analyze_project_exists():
    """Verify analyze_project is callable."""
    assert callable(getattr(metrics, "analyze_project", None))

def test_print_report_exists():
    """Verify print_report is callable."""
    assert callable(getattr(metrics, "print_report", None))

def test_cmd_metrics_exists():
    """Verify cmd_metrics is callable."""
    assert callable(getattr(metrics, "cmd_metrics", None))
