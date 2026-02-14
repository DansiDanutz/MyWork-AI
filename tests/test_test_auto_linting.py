#!/usr/bin/env python3
"""Tests for tools/test_auto_linting.py"""

import pytest
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

try:
    import test_auto_linting
except ImportError:
    pytest.skip("Cannot import test_auto_linting", allow_module_level=True)


def test_create_test_files_exists():
    """Verify create_test_files is callable."""
    assert callable(getattr(test_auto_linting, "create_test_files", None))

def test_bad_function_exists():
    """Verify bad_function is callable."""
    assert callable(getattr(test_auto_linting, "bad_function", None))

def test_another_function_exists():
    """Verify another_function is callable."""
    assert callable(getattr(test_auto_linting, "another_function", None))

def test_test_agent_import_exists():
    """Verify test_agent_import is callable."""
    assert callable(getattr(test_auto_linting, "test_agent_import", None))

def test_test_config_creation_exists():
    """Verify test_config_creation is callable."""
    assert callable(getattr(test_auto_linting, "test_config_creation", None))

def test_test_file_type_detection_exists():
    """Verify test_file_type_detection is callable."""
    assert callable(getattr(test_auto_linting, "test_file_type_detection", None))

def test_test_ignore_patterns_exists():
    """Verify test_ignore_patterns is callable."""
    assert callable(getattr(test_auto_linting, "test_ignore_patterns", None))

def test_test_markdown_linting_exists():
    """Verify test_markdown_linting is callable."""
    assert callable(getattr(test_auto_linting, "test_markdown_linting", None))

def test_test_directory_scanning_exists():
    """Verify test_directory_scanning is callable."""
    assert callable(getattr(test_auto_linting, "test_directory_scanning", None))

def test_test_results_saving_exists():
    """Verify test_results_saving is callable."""
    assert callable(getattr(test_auto_linting, "test_results_saving", None))
