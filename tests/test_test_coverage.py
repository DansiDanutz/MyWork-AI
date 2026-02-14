#!/usr/bin/env python3
"""Tests for tools/test_coverage.py"""

import pytest
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

try:
    import test_coverage
except ImportError:
    pytest.skip("Cannot import test_coverage", allow_module_level=True)


def test_get_project_root_exists():
    """Verify get_project_root is callable."""
    assert callable(getattr(test_coverage, "get_project_root", None))

def test_discover_tools_exists():
    """Verify discover_tools is callable."""
    assert callable(getattr(test_coverage, "discover_tools", None))

def test_discover_tests_exists():
    """Verify discover_tests is callable."""
    assert callable(getattr(test_coverage, "discover_tests", None))

def test_count_test_functions_exists():
    """Verify count_test_functions is callable."""
    assert callable(getattr(test_coverage, "count_test_functions", None))

def test_count_functions_exists():
    """Verify count_functions is callable."""
    assert callable(getattr(test_coverage, "count_functions", None))

def test_analyze_exists():
    """Verify analyze is callable."""
    assert callable(getattr(test_coverage, "analyze", None))

def test_scaffold_test_exists():
    """Verify scaffold_test is callable."""
    assert callable(getattr(test_coverage, "scaffold_test", None))

def test_print_bar_exists():
    """Verify print_bar is callable."""
    assert callable(getattr(test_coverage, "print_bar", None))

def test_main_exists():
    """Verify main is callable."""
    assert callable(getattr(test_coverage, "main", None))
