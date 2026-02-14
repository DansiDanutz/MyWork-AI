#!/usr/bin/env python3
"""Tests for tools/n8n_api.py"""

import pytest
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

try:
    import n8n_api
except ImportError:
    pytest.skip("Cannot import n8n_api", allow_module_level=True)


def test_get_headers_exists():
    """Verify get_headers is callable."""
    assert callable(getattr(n8n_api, "get_headers", None))

def test_list_workflows_exists():
    """Verify list_workflows is callable."""
    assert callable(getattr(n8n_api, "list_workflows", None))

def test_get_workflow_exists():
    """Verify get_workflow is callable."""
    assert callable(getattr(n8n_api, "get_workflow", None))

def test_create_workflow_exists():
    """Verify create_workflow is callable."""
    assert callable(getattr(n8n_api, "create_workflow", None))

def test_update_workflow_exists():
    """Verify update_workflow is callable."""
    assert callable(getattr(n8n_api, "update_workflow", None))

def test_delete_workflow_exists():
    """Verify delete_workflow is callable."""
    assert callable(getattr(n8n_api, "delete_workflow", None))

def test_activate_workflow_exists():
    """Verify activate_workflow is callable."""
    assert callable(getattr(n8n_api, "activate_workflow", None))

def test_deactivate_workflow_exists():
    """Verify deactivate_workflow is callable."""
    assert callable(getattr(n8n_api, "deactivate_workflow", None))

def test_execute_workflow_exists():
    """Verify execute_workflow is callable."""
    assert callable(getattr(n8n_api, "execute_workflow", None))

def test_trigger_webhook_exists():
    """Verify trigger_webhook is callable."""
    assert callable(getattr(n8n_api, "trigger_webhook", None))
