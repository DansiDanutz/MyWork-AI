#!/usr/bin/env python3
"""Tests for tools/auto_lint_scheduler.py"""

import pytest
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

try:
    import auto_lint_scheduler
except ImportError:
    pytest.skip("Cannot import auto_lint_scheduler", allow_module_level=True)


def test_run_command_exists():
    """Verify run_command is callable."""
    assert callable(getattr(auto_lint_scheduler, "run_command", None))

def test_check_git_status_exists():
    """Verify check_git_status is callable."""
    assert callable(getattr(auto_lint_scheduler, "check_git_status", None))

def test_run_lint_fixer_exists():
    """Verify run_lint_fixer is callable."""
    assert callable(getattr(auto_lint_scheduler, "run_lint_fixer", None))

def test_commit_changes_exists():
    """Verify commit_changes is callable."""
    assert callable(getattr(auto_lint_scheduler, "commit_changes", None))

def test_run_single_cycle_exists():
    """Verify run_single_cycle is callable."""
    assert callable(getattr(auto_lint_scheduler, "run_single_cycle", None))

def test_main_exists():
    """Verify main is callable."""
    assert callable(getattr(auto_lint_scheduler, "main", None))
