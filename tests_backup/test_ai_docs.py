#!/usr/bin/env python3
"""Tests for tools/ai_docs.py"""

import pytest
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

try:
    import ai_docs
except ImportError:
    pytest.skip("Cannot import ai_docs", allow_module_level=True)


def test_call_openrouter_api_exists():
    """Verify call_openrouter_api is callable."""
    assert callable(getattr(ai_docs, "call_openrouter_api", None))

def test_scan_project_exists():
    """Verify scan_project is callable."""
    assert callable(getattr(ai_docs, "scan_project", None))

def test_analyze_file_exists():
    """Verify analyze_file is callable."""
    assert callable(getattr(ai_docs, "analyze_file", None))

def test_detect_language_exists():
    """Verify detect_language is callable."""
    assert callable(getattr(ai_docs, "detect_language", None))

def test_extract_functions_exists():
    """Verify extract_functions is callable."""
    assert callable(getattr(ai_docs, "extract_functions", None))

def test_extract_classes_exists():
    """Verify extract_classes is callable."""
    assert callable(getattr(ai_docs, "extract_classes", None))

def test_extract_imports_exists():
    """Verify extract_imports is callable."""
    assert callable(getattr(ai_docs, "extract_imports", None))

def test_extract_dependencies_exists():
    """Verify extract_dependencies is callable."""
    assert callable(getattr(ai_docs, "extract_dependencies", None))

def test_detect_frameworks_exists():
    """Verify detect_frameworks is callable."""
    assert callable(getattr(ai_docs, "detect_frameworks", None))

def test_find_entry_points_exists():
    """Verify find_entry_points is callable."""
    assert callable(getattr(ai_docs, "find_entry_points", None))
