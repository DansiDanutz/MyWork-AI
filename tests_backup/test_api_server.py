#!/usr/bin/env python3
"""Tests for tools/api_server.py"""

import pytest
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

try:
    import api_server
except ImportError:
    pytest.skip("Cannot import api_server", allow_module_level=True)


def test_run_mw_exists():
    """Verify run_mw is callable."""
    assert callable(getattr(api_server, "run_mw", None))

def test_get_projects_list_exists():
    """Verify get_projects_list is callable."""
    assert callable(getattr(api_server, "get_projects_list", None))

def test_get_brain_stats_exists():
    """Verify get_brain_stats is callable."""
    assert callable(getattr(api_server, "get_brain_stats", None))

def test_search_brain_exists():
    """Verify search_brain is callable."""
    assert callable(getattr(api_server, "search_brain", None))

def test_get_git_log_exists():
    """Verify get_git_log is callable."""
    assert callable(getattr(api_server, "get_git_log", None))

def test_get_metrics_exists():
    """Verify get_metrics is callable."""
    assert callable(getattr(api_server, "get_metrics", None))

def test_create_app_exists():
    """Verify create_app is callable."""
    assert callable(getattr(api_server, "create_app", None))

def test_serve_exists():
    """Verify serve is callable."""
    assert callable(getattr(api_server, "serve", None))
