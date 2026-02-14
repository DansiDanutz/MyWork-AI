#!/usr/bin/env python3
"""Tests for tools/marketplace_upload_previews.py"""

import pytest
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

try:
    import marketplace_upload_previews
except ImportError:
    pytest.skip("Cannot import marketplace_upload_previews", allow_module_level=True)


def test_main_exists():
    """Verify main is callable."""
    assert callable(getattr(marketplace_upload_previews, "main", None))
