#!/usr/bin/env python3
"""Tests for tools/project_registry.py"""

import pytest
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

try:
    import project_registry
except ImportError:
    pytest.skip("Cannot import project_registry", allow_module_level=True)


def test_scan_projects_exists():
    """Verify scan_projects is callable."""
    assert callable(getattr(project_registry, "scan_projects", None))

def test_load_registry_exists():
    """Verify load_registry is callable."""
    assert callable(getattr(project_registry, "load_registry", None))

def test_format_flags_exists():
    """Verify format_flags is callable."""
    assert callable(getattr(project_registry, "format_flags", None))

def test_cmd_list_exists():
    """Verify cmd_list is callable."""
    assert callable(getattr(project_registry, "cmd_list", None))

def test_cmd_show_exists():
    """Verify cmd_show is callable."""
    assert callable(getattr(project_registry, "cmd_show", None))

def test_cmd_stats_exists():
    """Verify cmd_stats is callable."""
    assert callable(getattr(project_registry, "cmd_stats", None))

def test_cmd_export_exists():
    """Verify cmd_export is callable."""
    assert callable(getattr(project_registry, "cmd_export", None))

def test_main_exists():
    """Verify main is callable."""
    assert callable(getattr(project_registry, "main", None))
