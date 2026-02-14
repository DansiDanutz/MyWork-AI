#!/usr/bin/env python3
"""Tests for tools/autoforge_service.py"""

import pytest
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

try:
    import autoforge_service
except ImportError:
    pytest.skip("Cannot import autoforge_service", allow_module_level=True)


def test_get_autoforge_python_exists():
    """Verify get_autoforge_python is callable."""
    assert callable(getattr(autoforge_service, "get_autoforge_python", None))

def test_generate_plist_exists():
    """Verify generate_plist is callable."""
    assert callable(getattr(autoforge_service, "generate_plist", None))

def test_setup_exists():
    """Verify setup is callable."""
    assert callable(getattr(autoforge_service, "setup", None))

def test_run_cmd_exists():
    """Verify run_cmd is callable."""
    assert callable(getattr(autoforge_service, "run_cmd", None))

def test_is_loaded_exists():
    """Verify is_loaded is callable."""
    assert callable(getattr(autoforge_service, "is_loaded", None))

def test_is_running_exists():
    """Verify is_running is callable."""
    assert callable(getattr(autoforge_service, "is_running", None))

def test_get_pid_exists():
    """Verify get_pid is callable."""
    assert callable(getattr(autoforge_service, "get_pid", None))

def test_install_exists():
    """Verify install is callable."""
    assert callable(getattr(autoforge_service, "install", None))

def test_start_exists():
    """Verify start is callable."""
    assert callable(getattr(autoforge_service, "start", None))

def test_stop_exists():
    """Verify stop is callable."""
    assert callable(getattr(autoforge_service, "stop", None))
