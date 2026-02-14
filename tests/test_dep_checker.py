#!/usr/bin/env python3
"""Tests for tools/dep_checker.py"""

import pytest
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

try:
    import dep_checker
except ImportError:
    pytest.skip("Cannot import dep_checker", allow_module_level=True)


def test_color_exists():
    """Verify color is callable."""
    assert callable(getattr(dep_checker, "color", None))

def test_main_exists():
    """Verify main is callable."""
    assert callable(getattr(dep_checker, "main", None))
