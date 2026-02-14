#!/usr/bin/env python3
"""Tests for tools/test_brain_webhook.py"""

import pytest
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

try:
    import test_brain_webhook
except ImportError:
    pytest.skip("Cannot import test_brain_webhook", allow_module_level=True)


def test_run_brain_webhook_test_exists():
    """Verify run_brain_webhook_test is callable."""
    assert callable(getattr(test_brain_webhook, "run_brain_webhook_test", None))
