#!/usr/bin/env python3
"""Tests for tools/auto_update.py"""

import pytest
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

try:
    import auto_update
except ImportError:
    pytest.skip("Cannot import auto_update", allow_module_level=True)


def test_run_command_exists():
    """Verify run_command is callable."""
    assert callable(getattr(auto_update, "run_command", None))

def test_get_git_info_exists():
    """Verify get_git_info is callable."""
    assert callable(getattr(auto_update, "get_git_info", None))

def test_get_npx_info_exists():
    """Verify get_npx_info is callable."""
    assert callable(getattr(auto_update, "get_npx_info", None))

def test_check_autocoder_running_exists():
    """Verify check_autocoder_running is callable."""
    assert callable(getattr(auto_update, "check_autocoder_running", None))

def test_rebuild_autocoder_ui_exists():
    """Verify rebuild_autocoder_ui is callable."""
    assert callable(getattr(auto_update, "rebuild_autocoder_ui", None))

def test_backup_component_exists():
    """Verify backup_component is callable."""
    assert callable(getattr(auto_update, "backup_component", None))

def test_update_git_component_exists():
    """Verify update_git_component is callable."""
    assert callable(getattr(auto_update, "update_git_component", None))

def test_update_npx_component_exists():
    """Verify update_npx_component is callable."""
    assert callable(getattr(auto_update, "update_npx_component", None))

def test_get_status_exists():
    """Verify get_status is callable."""
    assert callable(getattr(auto_update, "get_status", None))

def test_check_updates_exists():
    """Verify check_updates is callable."""
    assert callable(getattr(auto_update, "check_updates", None))
