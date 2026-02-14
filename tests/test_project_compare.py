#!/usr/bin/env python3
"""Tests for tools/project_compare.py"""

import pytest
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

try:
    import project_compare
except ImportError:
    pytest.skip("Cannot import project_compare", allow_module_level=True)


def test_color_exists():
    """Verify color is callable."""
    assert callable(getattr(project_compare, "color", None))

def test_analyze_project_exists():
    """Verify analyze_project is callable."""
    assert callable(getattr(project_compare, "analyze_project", None))

def test_format_number_exists():
    """Verify format_number is callable."""
    assert callable(getattr(project_compare, "format_number", None))

def test_format_size_exists():
    """Verify format_size is callable."""
    assert callable(getattr(project_compare, "format_size", None))

def test_print_comparison_exists():
    """Verify print_comparison is callable."""
    assert callable(getattr(project_compare, "print_comparison", None))

def test_resolve_project_path_exists():
    """Verify resolve_project_path is callable."""
    assert callable(getattr(project_compare, "resolve_project_path", None))

def test_main_exists():
    """Verify main is callable."""
    assert callable(getattr(project_compare, "main", None))
