#!/usr/bin/env python3
"""Tests for Brain Quality Scoring & Deduplication Engine (Phase 9)."""

import sys
import os
import json
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from brain_quality import QualityScorer, DuplicateDetector, ProvenanceTracker, quality_report


class FakeEntry:
    """Minimal brain entry for testing."""
    def __init__(self, id, content, context=None, tags=None, status=None,
                 entry_type=None, created=None):
        self.id = id
        self.content = content
        self.context = context or ""
        self.tags = tags or []
        self.status = status
        self.entry_type = entry_type or "pattern"
        self.created = created or datetime.now().isoformat()


class FakeBrain:
    """Minimal brain manager for testing."""
    def __init__(self, entries=None):
        self.entries = {}
        if entries:
            for e in entries:
                self.entries[e.id] = e
        self._saved = False

    def save(self):
        self._saved = True


# --- QualityScorer Tests ---

class TestQualityScorer:

    def test_score_high_quality_entry(self):
        entry = FakeEntry(
            id="e1",
            content="A comprehensive guide to deploying microservices with Docker and Kubernetes. " * 10,
            context="Production deployment patterns for cloud-native apps",
            tags=["docker", "kubernetes", "deployment", "devops"],
            status="TESTED",
            created=datetime.now().isoformat(),
        )
        brain = FakeBrain([entry])
        scorer = QualityScorer(brain)
        result = scorer.score_entry(entry)
        assert result["total"] >= 60
        assert result["grade"] in ("A", "B")

    def test_score_low_quality_entry(self):
        entry = FakeEntry(
            id="e2",
            content="todo",
            created=(datetime.now() - timedelta(days=180)).isoformat(),
        )
        brain = FakeBrain([entry])
        scorer = QualityScorer(brain)
        result = scorer.score_entry(entry)
        assert result["total"] < 40
        assert result["grade"] in ("D", "F")

    def test_score_all_returns_sorted(self):
        entries = [
            FakeEntry("a", "short"),
            FakeEntry("b", "A detailed entry with lots of context " * 15,
                      context="ctx", tags=["x", "y", "z"], status="TESTED"),
        ]
        brain = FakeBrain(entries)
        scorer = QualityScorer(brain)
        results = scorer.score_all()
        assert len(results) == 2
        assert results[0]["total"] >= results[1]["total"]

    def test_grade_boundaries(self):
        brain = FakeBrain()
        scorer = QualityScorer(brain)
        assert scorer._grade(85) == "A"
        assert scorer._grade(70) == "B"
        assert scorer._grade(55) == "C"
        assert scorer._grade(40) == "D"
        assert scorer._grade(20) == "F"

    def test_recency_scoring(self):
        recent = FakeEntry("r", "content " * 50, created=datetime.now().isoformat())
        old = FakeEntry("o", "content " * 50,
                       created=(datetime.now() - timedelta(days=120)).isoformat())
        brain = FakeBrain([recent, old])
        scorer = QualityScorer(brain)
        r_score = scorer.score_entry(recent)
        o_score = scorer.score_entry(old)
        assert r_score["breakdown"]["recency"] > o_score["breakdown"]["recency"]

    def test_empty_brain(self):
        brain = FakeBrain()
        scorer = QualityScorer(brain)
        assert scorer.score_all() == []


# --- DuplicateDetector Tests ---

class TestDuplicateDetector:

    def test_exact_duplicates(self):
        entries = [
            FakeEntry("a", "Deploy with Docker compose up -d"),
            FakeEntry("b", "Deploy with Docker compose up -d"),
        ]
        brain = FakeBrain(entries)
        detector = DuplicateDetector(brain)
        dupes = detector.find_duplicates()
        assert len(dupes) == 1
        assert dupes[0]["type"] == "exact"
        assert dupes[0]["similarity"] == 1.0

    def test_fuzzy_duplicates(self):
        entries = [
            FakeEntry("a", "Deploy the application using Docker compose"),
            FakeEntry("b", "Deploy the application with Docker compose up"),
        ]
        brain = FakeBrain(entries)
        detector = DuplicateDetector(brain)
        dupes = detector.find_duplicates(threshold=0.6)
        assert len(dupes) >= 1
        assert dupes[0]["type"] == "fuzzy"

    def test_no_duplicates(self):
        entries = [
            FakeEntry("a", "Python is a programming language"),
            FakeEntry("b", "Kubernetes orchestrates containers at scale"),
        ]
        brain = FakeBrain(entries)
        detector = DuplicateDetector(brain)
        dupes = detector.find_duplicates()
        assert len(dupes) == 0

    def test_dedupe_dry_run(self):
        entries = [
            FakeEntry("a", "Same content here", tags=["x"], status="TESTED"),
            FakeEntry("b", "Same content here"),
        ]
        brain = FakeBrain(entries)
        detector = DuplicateDetector(brain)
        result = detector.dedupe(dry_run=True)
        assert result["dry_run"] is True
        assert result["duplicates_found"] == 1
        assert len(brain.entries) == 2  # Not actually removed

    def test_dedupe_apply(self):
        entries = [
            FakeEntry("a", "Duplicate entry text", tags=["x"], status="TESTED"),
            FakeEntry("b", "Duplicate entry text"),
        ]
        brain = FakeBrain(entries)
        detector = DuplicateDetector(brain)
        result = detector.dedupe(dry_run=False)
        assert result["dry_run"] is False
        assert len(result["removed"]) == 1
        assert brain._saved is True


# --- ProvenanceTracker Tests ---

class TestProvenanceTracker:

    def test_record_and_get(self, tmp_path):
        brain = FakeBrain()
        with patch("brain_quality.get_mywork_root", return_value=str(tmp_path)):
            tracker = ProvenanceTracker(brain)
            tracker.record_creation("e1", "memo")
            tracker.record_access("e1", "dexter")
            prov = tracker.get_provenance("e1")
            assert prov["created_by"] == "memo"
            assert prov["access_count"] == 1
            assert "dexter" in prov["accessors"]

    def test_report_empty(self, tmp_path):
        brain = FakeBrain()
        with patch("brain_quality.get_mywork_root", return_value=str(tmp_path)):
            tracker = ProvenanceTracker(brain)
            report = tracker.report()
            assert report["total_tracked"] == 0

    def test_multiple_accesses(self, tmp_path):
        brain = FakeBrain()
        with patch("brain_quality.get_mywork_root", return_value=str(tmp_path)):
            tracker = ProvenanceTracker(brain)
            tracker.record_access("e1", "user1")
            tracker.record_access("e1", "user2")
            tracker.record_access("e1", "user1")
            prov = tracker.get_provenance("e1")
            assert prov["access_count"] == 3
            assert len(prov["accessors"]) == 2


# --- Quality Report Tests ---

class TestQualityReport:

    def test_report_with_entries(self):
        entries = [
            FakeEntry("a", "A solid entry " * 20, tags=["x"], status="TESTED"),
            FakeEntry("b", "tiny"),
        ]
        brain = FakeBrain(entries)
        report = quality_report(brain)
        assert "BRAIN QUALITY REPORT" in report
        assert "Total entries: 2" in report

    def test_report_empty(self):
        brain = FakeBrain()
        report = quality_report(brain)
        assert "No entries to score" in report
