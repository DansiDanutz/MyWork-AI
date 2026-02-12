#!/usr/bin/env python3
"""Tests for api_server.py"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from tools.api_server import (
    run_mw, get_projects_list, get_brain_stats,
    search_brain, get_git_log, get_metrics, ALLOWED_COMMANDS,
)


def test_run_mw_status():
    """mw status should succeed."""
    result = run_mw(["status"], timeout=15)
    assert result["success"] is True
    assert "MyWork" in result["stdout"] or "HEALTHY" in result["stdout"]


def test_run_mw_invalid_command():
    """Invalid command should still return dict."""
    result = run_mw(["nonexistent_command_xyz"], timeout=10)
    assert isinstance(result, dict)
    assert "success" in result


def test_get_projects_list():
    """Should return a list."""
    projects = get_projects_list()
    assert isinstance(projects, list)


def test_get_brain_stats():
    """Should return dict with expected keys."""
    stats = get_brain_stats()
    assert "entries" in stats
    assert "categories" in stats
    assert "size_kb" in stats


def test_search_brain_empty():
    """Search with unlikely term returns empty."""
    results = search_brain("xyznonexistent12345")
    assert isinstance(results, list)
    assert len(results) == 0


def test_get_git_log():
    """Should return list of commits."""
    commits = get_git_log(5)
    assert isinstance(commits, list)
    if commits:
        assert "hash" in commits[0]
        assert "message" in commits[0]


def test_get_metrics():
    """Should return metrics dict."""
    m = get_metrics()
    assert "test_count" in m
    assert "framework_version" in m
    assert m["framework_version"] == "2.1.0"
    assert "uptime_seconds" in m


def test_allowed_commands_whitelist():
    """Whitelist should contain expected commands."""
    assert "status" in ALLOWED_COMMANDS
    assert "doctor" in ALLOWED_COMMANDS
    assert "rm" not in ALLOWED_COMMANDS
    assert "deploy" not in ALLOWED_COMMANDS


def test_run_mw_timeout():
    """Timeout should be handled gracefully."""
    result = run_mw(["status"], timeout=1)
    assert isinstance(result, dict)


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
