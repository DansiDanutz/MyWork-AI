#!/usr/bin/env python3
"""Tests for tools/ai_review.py"""

import pytest
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

try:
    import ai_review
except ImportError:
    pytest.skip("Cannot import ai_review", allow_module_level=True)


def test_call_openrouter_api_exists():
    """Verify call_openrouter_api is callable."""
    assert callable(getattr(ai_review, "call_openrouter_api", None))

def test_get_git_diff_exists():
    """Verify get_git_diff is callable."""
    assert callable(getattr(ai_review, "get_git_diff", None))

def test_detect_language_exists():
    """Verify detect_language is callable."""
    assert callable(getattr(ai_review, "detect_language", None))

def test_create_review_prompt_exists():
    """Verify create_review_prompt is callable."""
    assert callable(getattr(ai_review, "create_review_prompt", None))

def test_review_file_exists():
    """Verify review_file is callable."""
    assert callable(getattr(ai_review, "review_file", None))

def test_review_diff_exists():
    """Verify review_diff is callable."""
    assert callable(getattr(ai_review, "review_diff", None))

def test_format_output_exists():
    """Verify format_output is callable."""
    assert callable(getattr(ai_review, "format_output", None))

def test_main_exists():
    """Verify main is callable."""
    assert callable(getattr(ai_review, "main", None))
