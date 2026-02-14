#!/usr/bin/env python3
"""Tests for tools/error_handling_improvements.py"""

import pytest
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

try:
    import error_handling_improvements
except ImportError:
    pytest.skip("Cannot import error_handling_improvements", allow_module_level=True)


def test_enhanced_error_decorator_exists():
    """Verify enhanced_error_decorator is callable."""
    assert callable(getattr(error_handling_improvements, "enhanced_error_decorator", None))
