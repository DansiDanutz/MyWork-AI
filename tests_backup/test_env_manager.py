#!/usr/bin/env python3
"""Tests for tools/env_manager.py"""

import pytest
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

try:
    import env_manager
except ImportError:
    pytest.skip("Cannot import env_manager", allow_module_level=True)


def test_parse_env_file_exists():
    """Verify parse_env_file is callable."""
    assert callable(getattr(env_manager, "parse_env_file", None))

def test_find_env_usage_exists():
    """Verify find_env_usage is callable."""
    assert callable(getattr(env_manager, "find_env_usage", None))

def test_find_env_files_exists():
    """Verify find_env_files is callable."""
    assert callable(getattr(env_manager, "find_env_files", None))

def test_cmd_check_exists():
    """Verify cmd_check is callable."""
    assert callable(getattr(env_manager, "cmd_check", None))

def test_cmd_compare_exists():
    """Verify cmd_compare is callable."""
    assert callable(getattr(env_manager, "cmd_compare", None))

def test_cmd_template_exists():
    """Verify cmd_template is callable."""
    assert callable(getattr(env_manager, "cmd_template", None))

def test_cmd_secrets_exists():
    """Verify cmd_secrets is callable."""
    assert callable(getattr(env_manager, "cmd_secrets", None))

def test_cmd_list_exists():
    """Verify cmd_list is callable."""
    assert callable(getattr(env_manager, "cmd_list", None))

def test_main_exists():
    """Verify main is callable."""
    assert callable(getattr(env_manager, "main", None))
