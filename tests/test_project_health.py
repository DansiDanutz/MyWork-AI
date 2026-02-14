#!/usr/bin/env python3
"""Tests for tools/project_health.py"""

import pytest
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

try:
    import project_health
except ImportError:
    pytest.skip("Cannot import project_health", allow_module_level=True)


def test_print_results_exists():
    """Verify print_results is callable."""
    assert callable(getattr(project_health, "print_results", None))

def test_main_exists():
    """Verify main is callable."""
    assert callable(getattr(project_health, "main", None))
