#!/usr/bin/env python3
"""Tests for tools/switch_llm_provider.py"""

import pytest
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

try:
    import switch_llm_provider
except ImportError:
    pytest.skip("Cannot import switch_llm_provider", allow_module_level=True)


def test_load_env_file_exists():
    """Verify load_env_file is callable."""
    assert callable(getattr(switch_llm_provider, "load_env_file", None))

def test_get_env_key_exists():
    """Verify get_env_key is callable."""
    assert callable(getattr(switch_llm_provider, "get_env_key", None))

def test_read_env_exists():
    """Verify read_env is callable."""
    assert callable(getattr(switch_llm_provider, "read_env", None))

def test_write_env_exists():
    """Verify write_env is callable."""
    assert callable(getattr(switch_llm_provider, "write_env", None))

def test_get_current_provider_exists():
    """Verify get_current_provider is callable."""
    assert callable(getattr(switch_llm_provider, "get_current_provider", None))

def test_resolve_env_vars_exists():
    """Verify resolve_env_vars is callable."""
    assert callable(getattr(switch_llm_provider, "resolve_env_vars", None))

def test_switch_provider_exists():
    """Verify switch_provider is callable."""
    assert callable(getattr(switch_llm_provider, "switch_provider", None))

def test_list_providers_exists():
    """Verify list_providers is callable."""
    assert callable(getattr(switch_llm_provider, "list_providers", None))

def test_main_exists():
    """Verify main is callable."""
    assert callable(getattr(switch_llm_provider, "main", None))
