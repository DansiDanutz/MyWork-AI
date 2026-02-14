#!/usr/bin/env python3
"""Tests for tools/watch.py"""

import pytest
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

try:
    import watch
except ImportError:
    pytest.skip("Cannot import watch", allow_module_level=True)


def test_detect_project_type_exists():
    """Verify detect_project_type is callable."""
    assert callable(getattr(watch, "detect_project_type", None))

def test_detect_test_command_exists():
    """Verify detect_test_command is callable."""
    assert callable(getattr(watch, "detect_test_command", None))

def test_detect_lint_command_exists():
    """Verify detect_lint_command is callable."""
    assert callable(getattr(watch, "detect_lint_command", None))

def test_detect_build_command_exists():
    """Verify detect_build_command is callable."""
    assert callable(getattr(watch, "detect_build_command", None))

def test_get_watchable_extensions_exists():
    """Verify get_watchable_extensions is callable."""
    assert callable(getattr(watch, "get_watchable_extensions", None))

def test_get_file_hash_exists():
    """Verify get_file_hash is callable."""
    assert callable(getattr(watch, "get_file_hash", None))

def test_scan_files_exists():
    """Verify scan_files is callable."""
    assert callable(getattr(watch, "scan_files", None))

def test_find_related_test_exists():
    """Verify find_related_test is callable."""
    assert callable(getattr(watch, "find_related_test", None))

def test_run_command_exists():
    """Verify run_command is callable."""
    assert callable(getattr(watch, "run_command", None))

def test_print_banner_exists():
    """Verify print_banner is callable."""
    assert callable(getattr(watch, "print_banner", None))
