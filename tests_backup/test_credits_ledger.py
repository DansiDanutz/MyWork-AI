#!/usr/bin/env python3
"""Tests for tools/credits_ledger.py"""

import pytest
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

try:
    import credits_ledger
except ImportError:
    pytest.skip("Cannot import credits_ledger", allow_module_level=True)


def test_main_exists():
    """Verify main is callable."""
    assert callable(getattr(credits_ledger, "main", None))
