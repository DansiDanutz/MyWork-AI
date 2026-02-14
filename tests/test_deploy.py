#!/usr/bin/env python3
"""Tests for tools/deploy.py"""

import pytest
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

try:
    import deploy
except ImportError:
    pytest.skip("Cannot import deploy", allow_module_level=True)


def test_print_project_info_exists():
    """Verify print_project_info is callable."""
    assert callable(getattr(deploy, "print_project_info", None))

def test_main_exists():
    """Verify main is callable."""
    assert callable(getattr(deploy, "main", None))
