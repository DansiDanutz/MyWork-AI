#!/usr/bin/env python3
"""Tests for tools/project_archive.py"""

import pytest
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

try:
    import project_archive
except ImportError:
    pytest.skip("Cannot import project_archive", allow_module_level=True)


def test_color_exists():
    """Verify color is callable."""
    assert callable(getattr(project_archive, "color", None))

def test_resolve_project_path_exists():
    """Verify resolve_project_path is callable."""
    assert callable(getattr(project_archive, "resolve_project_path", None))

def test_main_exists():
    """Verify main is callable."""
    assert callable(getattr(project_archive, "main", None))
