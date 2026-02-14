#!/usr/bin/env python3
"""Tests for tools/brain_semantic.py"""

import pytest
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

try:
    import brain_semantic
except ImportError:
    pytest.skip("Cannot import brain_semantic", allow_module_level=True)


def test_tokenize_exists():
    """Verify tokenize is callable."""
    assert callable(getattr(brain_semantic, "tokenize", None))

def test_compute_tf_exists():
    """Verify compute_tf is callable."""
    assert callable(getattr(brain_semantic, "compute_tf", None))

def test_compute_idf_exists():
    """Verify compute_idf is callable."""
    assert callable(getattr(brain_semantic, "compute_idf", None))

def test_tfidf_vector_exists():
    """Verify tfidf_vector is callable."""
    assert callable(getattr(brain_semantic, "tfidf_vector", None))

def test_cosine_similarity_exists():
    """Verify cosine_similarity is callable."""
    assert callable(getattr(brain_semantic, "cosine_similarity", None))

def test_load_brain_entries_exists():
    """Verify load_brain_entries is callable."""
    assert callable(getattr(brain_semantic, "load_brain_entries", None))

def test_entry_text_exists():
    """Verify entry_text is callable."""
    assert callable(getattr(brain_semantic, "entry_text", None))

def test_quality_score_exists():
    """Verify quality_score is callable."""
    assert callable(getattr(brain_semantic, "quality_score", None))

def test_load_provenance_exists():
    """Verify load_provenance is callable."""
    assert callable(getattr(brain_semantic, "load_provenance", None))

def test_save_provenance_exists():
    """Verify save_provenance is callable."""
    assert callable(getattr(brain_semantic, "save_provenance", None))
