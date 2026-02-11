#!/usr/bin/env python3
"""Tests for Brain Semantic Search — Phase 9."""

import json
import os
import sys
import tempfile
from pathlib import Path

# Ensure tools/ is importable
sys.path.insert(0, os.path.dirname(__file__))

from brain_semantic import (
    tokenize, compute_tf, compute_idf, tfidf_vector, cosine_similarity,
    SearchIndex, quality_score, track_provenance, get_provenance,
    load_provenance, save_provenance, PROVENANCE_FILE
)

passed = 0
failed = 0

def test(name):
    global passed, failed
    def decorator(fn):
        global passed, failed
        try:
            fn()
            print(f"✅ {name}")
            passed += 1
        except Exception as e:
            print(f"❌ {name}: {e}")
            failed += 1
    return decorator


@test("tokenize basic")
def _():
    tokens = tokenize("The quick brown fox jumps over the lazy dog")
    assert "quick" in tokens
    assert "the" not in tokens  # stop word
    assert "brown" in tokens


@test("tokenize removes short words")
def _():
    tokens = tokenize("I am a big fan")
    assert "i" not in tokens
    assert "big" in tokens
    assert "fan" in tokens


@test("TF computation")
def _():
    tf = compute_tf(["hello", "world", "hello"])
    assert abs(tf["hello"] - 2/3) < 0.01
    assert abs(tf["world"] - 1/3) < 0.01


@test("IDF computation")
def _():
    docs = [["hello", "world"], ["hello", "foo"], ["bar", "baz"]]
    idf = compute_idf(docs)
    assert idf["hello"] < idf["bar"]  # hello in 2 docs, bar in 1


@test("cosine similarity - identical")
def _():
    v = {"a": 1.0, "b": 2.0}
    sim = cosine_similarity(v, v)
    assert abs(sim - 1.0) < 0.01


@test("cosine similarity - orthogonal")
def _():
    v1 = {"a": 1.0}
    v2 = {"b": 1.0}
    sim = cosine_similarity(v1, v2)
    assert sim == 0.0


@test("cosine similarity - partial overlap")
def _():
    v1 = {"a": 1.0, "b": 1.0}
    v2 = {"a": 1.0, "c": 1.0}
    sim = cosine_similarity(v1, v2)
    assert 0.0 < sim < 1.0


@test("SearchIndex search")
def _():
    entries = [
        {"id": "1", "content": "Python API error handling best practices", "type": "pattern", "tags": ["python"]},
        {"id": "2", "content": "Docker container deployment guide", "type": "lesson", "tags": ["docker"]},
        {"id": "3", "content": "Python exception handling patterns", "type": "pattern", "tags": ["python"]},
    ]
    idx = SearchIndex()
    idx.build(entries)
    results = idx.search("python error handling")
    assert len(results) > 0
    # First result should be about python error handling
    assert results[0][0]["id"] in ("1", "3")


@test("SearchIndex no results")
def _():
    entries = [{"id": "1", "content": "Docker deployment", "type": "lesson"}]
    idx = SearchIndex()
    idx.build(entries)
    results = idx.search("quantum physics astronomy")
    assert len(results) == 0


@test("SearchIndex find duplicates")
def _():
    entries = [
        {"id": "1", "content": "Always validate input before processing API requests"},
        {"id": "2", "content": "Always validate input before processing API calls"},
        {"id": "3", "content": "Docker containers are useful for deployment"},
    ]
    idx = SearchIndex()
    idx.build(entries)
    dupes = idx.find_duplicates(threshold=0.7)
    assert len(dupes) >= 1
    ids = {dupes[0][0]["id"], dupes[0][1]["id"]}
    assert ids == {"1", "2"}


@test("quality score - complete entry")
def _():
    entry = {
        "content": "Always validate API input to prevent injection attacks and data corruption",
        "context": "Learned after a production incident",
        "tags": ["security", "api"],
        "status": "TESTED",
        "date_updated": "2026-02-10",
        "references": 5,
    }
    sc = quality_score(entry)
    assert sc["completeness"] == 100
    assert sc["reliability"] == 90
    assert sc["overall"] > 70


@test("quality score - minimal entry")
def _():
    entry = {"content": "Hi", "status": "EXPERIMENTAL"}
    sc = quality_score(entry)
    assert sc["completeness"] < 60
    assert sc["reliability"] == 50
    assert sc["overall"] < 50


@test("quality score - deprecated entry")
def _():
    entry = {"content": "Old stuff", "status": "DEPRECATED"}
    sc = quality_score(entry)
    assert sc["reliability"] == 10


@test("provenance tracking")
def _():
    # Use temp file
    import brain_semantic
    old_file = brain_semantic.PROVENANCE_FILE
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write('{}')
        brain_semantic.PROVENANCE_FILE = Path(f.name)
    try:
        track_provenance("test-001", "created", "memo", "initial creation")
        track_provenance("test-001", "updated", "dexter", "added context")
        events = get_provenance("test-001")
        assert len(events) == 2
        assert events[0]["action"] == "created"
        assert events[1]["actor"] == "dexter"
    finally:
        brain_semantic.PROVENANCE_FILE = old_file
        os.unlink(f.name)


@test("empty brain graceful")
def _():
    idx = SearchIndex()
    idx.build([])
    results = idx.search("anything")
    assert results == []
    dupes = idx.find_duplicates()
    assert dupes == []


print(f"\n{'🎉' if failed == 0 else '💥'} {passed}/{passed + failed} brain semantic tests passed!")
if failed:
    sys.exit(1)
