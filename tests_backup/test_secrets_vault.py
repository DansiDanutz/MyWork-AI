#!/usr/bin/env python3
"""Tests for tools/secrets_vault.py"""

import pytest
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

try:
    import secrets_vault
except ImportError:
    pytest.skip("Cannot import secrets_vault", allow_module_level=True)


def test_cmd_set_exists():
    """Verify cmd_set is callable."""
    assert callable(getattr(secrets_vault, "cmd_set", None))

def test_cmd_get_exists():
    """Verify cmd_get is callable."""
    assert callable(getattr(secrets_vault, "cmd_get", None))

def test_cmd_list_exists():
    """Verify cmd_list is callable."""
    assert callable(getattr(secrets_vault, "cmd_list", None))

def test_cmd_delete_exists():
    """Verify cmd_delete is callable."""
    assert callable(getattr(secrets_vault, "cmd_delete", None))

def test_cmd_inject_exists():
    """Verify cmd_inject is callable."""
    assert callable(getattr(secrets_vault, "cmd_inject", None))

def test_cmd_export_exists():
    """Verify cmd_export is callable."""
    assert callable(getattr(secrets_vault, "cmd_export", None))

def test_cmd_import_env_exists():
    """Verify cmd_import_env is callable."""
    assert callable(getattr(secrets_vault, "cmd_import_env", None))

def test_cmd_audit_exists():
    """Verify cmd_audit is callable."""
    assert callable(getattr(secrets_vault, "cmd_audit", None))

def test_cmd_secrets_exists():
    """Verify cmd_secrets is callable."""
    assert callable(getattr(secrets_vault, "cmd_secrets", None))
