#!/usr/bin/env python3
"""Tests for tools/brain_graph.py"""

import pytest
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

try:
    import brain_graph
except ImportError:
    pytest.skip("Cannot import brain_graph", allow_module_level=True)


def test_print_ascii_graph_exists():
    """Verify print_ascii_graph is callable."""
    assert callable(getattr(brain_graph, "print_ascii_graph", None))

def test_cmd_graph_exists():
    """Verify cmd_graph is callable."""
    assert callable(getattr(brain_graph, "cmd_graph", None))

def test_cmd_related_exists():
    """Verify cmd_related is callable."""
    assert callable(getattr(brain_graph, "cmd_related", None))

def test_cmd_cluster_exists():
    """Verify cmd_cluster is callable."""
    assert callable(getattr(brain_graph, "cmd_cluster", None))

def test_cmd_connections_exists():
    """Verify cmd_connections is callable."""
    assert callable(getattr(brain_graph, "cmd_connections", None))

def test_cmd_network_stats_exists():
    """Verify cmd_network_stats is callable."""
    assert callable(getattr(brain_graph, "cmd_network_stats", None))

def test_cmd_export_graph_exists():
    """Verify cmd_export_graph is callable."""
    assert callable(getattr(brain_graph, "cmd_export_graph", None))

def test_main_exists():
    """Verify main is callable."""
    assert callable(getattr(brain_graph, "main", None))
