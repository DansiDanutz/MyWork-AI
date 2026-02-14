#!/usr/bin/env python3
"""Tests for tools/auto_lint_fixer.py"""

import pytest
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

try:
    import auto_lint_fixer
except ImportError:
    pytest.skip("Cannot import auto_lint_fixer", allow_module_level=True)


def test_run_markdownlint_exists():
    """Verify run_markdownlint is callable."""
    assert callable(getattr(auto_lint_fixer, "run_markdownlint", None))

def test_fix_md022_headings_exists():
    """Verify fix_md022_headings is callable."""
    assert callable(getattr(auto_lint_fixer, "fix_md022_headings", None))

def test_fix_md032_lists_exists():
    """Verify fix_md032_lists is callable."""
    assert callable(getattr(auto_lint_fixer, "fix_md032_lists", None))

def test_fix_md031_fences_exists():
    """Verify fix_md031_fences is callable."""
    assert callable(getattr(auto_lint_fixer, "fix_md031_fences", None))

def test_fix_md047_trailing_newline_exists():
    """Verify fix_md047_trailing_newline is callable."""
    assert callable(getattr(auto_lint_fixer, "fix_md047_trailing_newline", None))

def test_fix_md058_tables_exists():
    """Verify fix_md058_tables is callable."""
    assert callable(getattr(auto_lint_fixer, "fix_md058_tables", None))

def test_fix_md040_code_language_exists():
    """Verify fix_md040_code_language is callable."""
    assert callable(getattr(auto_lint_fixer, "fix_md040_code_language", None))

def test_detect_code_language_exists():
    """Verify detect_code_language is callable."""
    assert callable(getattr(auto_lint_fixer, "detect_code_language", None))

def test_fix_md013_line_length_exists():
    """Verify fix_md013_line_length is callable."""
    assert callable(getattr(auto_lint_fixer, "fix_md013_line_length", None))

def test_wrap_table_line_exists():
    """Verify wrap_table_line is callable."""
    assert callable(getattr(auto_lint_fixer, "wrap_table_line", None))
