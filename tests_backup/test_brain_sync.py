#!/usr/bin/env python3
"""Tests for tools/brain_sync.py"""

import pytest
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

try:
    import brain_sync
except ImportError:
    pytest.skip("Cannot import brain_sync", allow_module_level=True)


def test_export_payload_exists():
    """Verify export_payload is callable."""
    assert callable(getattr(brain_sync, "export_payload", None))

def test_push_entries_exists():
    """Verify push_entries is callable."""
    assert callable(getattr(brain_sync, "push_entries", None))

def test_main_exists():
    """Verify main is callable."""
    assert callable(getattr(brain_sync, "main", None))
