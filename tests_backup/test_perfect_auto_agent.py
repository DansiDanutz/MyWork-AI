#!/usr/bin/env python3
"""Tests for tools/perfect_auto_agent.py"""

import pytest
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

try:
    import perfect_auto_agent
except ImportError:
    pytest.skip("Cannot import perfect_auto_agent", allow_module_level=True)


def test_main_exists():
    """Verify main is callable."""
    assert callable(getattr(perfect_auto_agent, "main", None))
