#!/usr/bin/env python3
"""Tests for tools/lint_watcher.py"""

import pytest
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

try:
    import lint_watcher
except ImportError:
    pytest.skip("Cannot import lint_watcher", allow_module_level=True)


def test_get_pid_exists():
    """Verify get_pid is callable."""
    assert callable(getattr(lint_watcher, "get_pid", None))

def test_is_running_exists():
    """Verify is_running is callable."""
    assert callable(getattr(lint_watcher, "is_running", None))

def test_start_exists():
    """Verify start is callable."""
    assert callable(getattr(lint_watcher, "start", None))

def test_stop_exists():
    """Verify stop is callable."""
    assert callable(getattr(lint_watcher, "stop", None))

def test_status_exists():
    """Verify status is callable."""
    assert callable(getattr(lint_watcher, "status", None))

def test_restart_exists():
    """Verify restart is callable."""
    assert callable(getattr(lint_watcher, "restart", None))

def test_logs_exists():
    """Verify logs is callable."""
    assert callable(getattr(lint_watcher, "logs", None))

def test_main_exists():
    """Verify main is callable."""
    assert callable(getattr(lint_watcher, "main", None))
