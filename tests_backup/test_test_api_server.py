#!/usr/bin/env python3
"""Tests for tools/test_api_server.py"""

import pytest
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

try:
    import test_api_server
except ImportError:
    pytest.skip("Cannot import test_api_server", allow_module_level=True)


def test_test_run_mw_status_exists():
    """Verify test_run_mw_status is callable."""
    assert callable(getattr(test_api_server, "test_run_mw_status", None))

def test_test_run_mw_invalid_command_exists():
    """Verify test_run_mw_invalid_command is callable."""
    assert callable(getattr(test_api_server, "test_run_mw_invalid_command", None))

def test_test_get_projects_list_exists():
    """Verify test_get_projects_list is callable."""
    assert callable(getattr(test_api_server, "test_get_projects_list", None))

def test_test_get_brain_stats_exists():
    """Verify test_get_brain_stats is callable."""
    assert callable(getattr(test_api_server, "test_get_brain_stats", None))

def test_test_search_brain_empty_exists():
    """Verify test_search_brain_empty is callable."""
    assert callable(getattr(test_api_server, "test_search_brain_empty", None))

def test_test_get_git_log_exists():
    """Verify test_get_git_log is callable."""
    assert callable(getattr(test_api_server, "test_get_git_log", None))

def test_test_get_metrics_exists():
    """Verify test_get_metrics is callable."""
    assert callable(getattr(test_api_server, "test_get_metrics", None))

def test_test_allowed_commands_whitelist_exists():
    """Verify test_allowed_commands_whitelist is callable."""
    assert callable(getattr(test_api_server, "test_allowed_commands_whitelist", None))

def test_test_run_mw_timeout_exists():
    """Verify test_run_mw_timeout is callable."""
    assert callable(getattr(test_api_server, "test_run_mw_timeout", None))
