"""Tests for mw bench — Code Benchmarking."""

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from tools.bench import (
    analyze, format_table, format_md, compare_results,
    ensure_dir, get_memory_mb,
)


class TestAnalyze:
    def test_basic_stats(self):
        times = [0.1, 0.2, 0.15, 0.12, 0.18]
        result = analyze(times, "test_func")
        assert result["label"] == "test_func"
        assert result["runs"] == 5
        assert 0.1 <= result["min_ms"] <= 0.2
        assert 0.1 <= result["max_ms"] <= 0.2
        assert 0.1 <= result["mean_ms"] <= 0.2
        assert "median_ms" in result

    def test_single_run(self):
        result = analyze([0.5], "single")
        assert result["runs"] == 1
        assert result["min_ms"] == 0.5
        assert result["max_ms"] == 0.5


class TestFormatTable:
    def test_renders_string(self):
        result = analyze([0.1, 0.2], "demo")
        table = format_table(result)
        assert isinstance(table, str)
        assert "demo" in table


class TestFormatMd:
    def test_renders_markdown(self):
        result = analyze([0.1, 0.2], "demo")
        md = format_md(result)
        assert isinstance(md, str)
        assert "demo" in md


class TestCompareResults:
    def test_compare(self):
        a = analyze([0.1, 0.2], "a")
        b = analyze([0.3, 0.4], "b")
        comp = compare_results(a, b)
        assert isinstance(comp, str)


class TestBaseline:
    def test_save_load_roundtrip(self, tmp_path):
        result = analyze([0.1], "test")
        baseline_file = tmp_path / "baseline_mytest.json"
        baseline_file.write_text(json.dumps(result))
        loaded = json.loads(baseline_file.read_text())
        assert loaded["label"] == "test"
