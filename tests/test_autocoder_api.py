#!/usr/bin/env python3
"""Tests for tools/autocoder_api.py"""

import pytest
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

try:
    import autocoder_api
except ImportError:
    pytest.skip("Cannot import autocoder_api", allow_module_level=True)


def test_get_autoforge_python_exists():
    """Verify get_autoforge_python is callable."""
    assert callable(getattr(autocoder_api, "get_autoforge_python", None))

def test_start_server_exists():
    """Verify start_server is callable."""
    assert callable(getattr(autocoder_api, "start_server", None))

def test_open_ui_exists():
    """Verify open_ui is callable."""
    assert callable(getattr(autocoder_api, "open_ui", None))

def test_get_progress_exists():
    """Verify get_progress is callable."""
    assert callable(getattr(autocoder_api, "get_progress", None))

def test_notify_webhook_exists():
    """Verify notify_webhook is callable."""
    assert callable(getattr(autocoder_api, "notify_webhook", None))

def test_main_exists():
    """Verify main is callable."""
    assert callable(getattr(autocoder_api, "main", None))
