#!/usr/bin/env python3
"""Tests for tools/test_brain_semantic.py"""

import pytest
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

try:
    import test_brain_semantic
except ImportError:
    pytest.skip("Cannot import test_brain_semantic", allow_module_level=True)


def test_test_exists():
    """Verify test is callable."""
    assert callable(getattr(test_brain_semantic, "test", None))
