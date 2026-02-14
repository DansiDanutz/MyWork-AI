#!/usr/bin/env python3
"""Tests for tools/auto_linting_agent.py"""

import pytest
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

try:
    import auto_linting_agent
except ImportError:
    pytest.skip("Cannot import auto_linting_agent", allow_module_level=True)


def test_main_exists():
    """Verify main is callable."""
    assert callable(getattr(auto_linting_agent, "main", None))
