"""Tests for mw bench — Project Benchmarking."""

import json
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from tools.bench import (
    cmd_bench, run_benchmarks, _detect_project_type,
    _count_files, _get_dep_count, _get_dir_size_mb,
    _load_history, _save_history, _format_delta,
)


class TestDetectProjectType:
    def test_node(self, tmp_path):
        (tmp_path / "package.json").write_text("{}")
        assert _detect_project_type(str(tmp_path)) == "node"

    def test_python(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("")
        assert _detect_project_type(str(tmp_path)) == "python"

    def test_rust(self, tmp_path):
        (tmp_path / "Cargo.toml").write_text("")
        assert _detect_project_type(str(tmp_path)) == "rust"

    def test_go(self, tmp_path):
        (tmp_path / "go.mod").write_text("")
        assert _detect_project_type(str(tmp_path)) == "go"

    def test_unknown(self, tmp_path):
        assert _detect_project_type(str(tmp_path)) == "unknown"


class TestCountFiles:
    def test_counts_python(self, tmp_path):
        (tmp_path / "main.py").write_text("print(1)")
        (tmp_path / "util.py").write_text("x=1")
        (tmp_path / "readme.md").write_text("hi")
        counts = _count_files(str(tmp_path))
        assert counts.get(".py") == 2
        assert ".md" not in counts

    def test_skips_node_modules(self, tmp_path):
        nm = tmp_path / "node_modules" / "pkg"
        nm.mkdir(parents=True)
        (nm / "index.js").write_text("x")
        (tmp_path / "app.js").write_text("y")
        counts = _count_files(str(tmp_path))
        assert counts.get(".js") == 1


class TestGetDepCount:
    def test_node_deps(self, tmp_path):
        pkg = {"dependencies": {"a": "1", "b": "2"}, "devDependencies": {"c": "3"}}
        (tmp_path / "package.json").write_text(json.dumps(pkg))
        assert _get_dep_count(str(tmp_path), "node") == 3

    def test_python_deps(self, tmp_path):
        (tmp_path / "requirements.txt").write_text("flask\nrequests\n# comment\n")
        assert _get_dep_count(str(tmp_path), "python") == 2

    def test_no_deps(self, tmp_path):
        assert _get_dep_count(str(tmp_path), "unknown") == 0


class TestHistory:
    def test_save_and_load(self, tmp_path):
        data = [{"timestamp": "2026-01-01", "metrics": {"test": 1}}]
        _save_history(str(tmp_path), data)
        loaded = _load_history(str(tmp_path))
        assert loaded == data

    def test_empty_history(self, tmp_path):
        assert _load_history(str(tmp_path)) == []


class TestFormatDelta:
    def test_no_change(self):
        result = _format_delta(100, 100)
        assert "no change" in result

    def test_increase(self):
        result = _format_delta(120, 100, lower_is_better=True)
        assert "↑" in result
        assert "20.0%" in result

    def test_decrease(self):
        result = _format_delta(80, 100, lower_is_better=True)
        assert "↓" in result

    def test_none_values(self):
        assert _format_delta(None, 100) == ""
        assert _format_delta(100, None) == ""


class TestRunBenchmarks:
    def test_basic_run(self, tmp_path):
        (tmp_path / "main.py").write_text("print('hello')\n")
        results = run_benchmarks(str(tmp_path))
        assert "timestamp" in results
        assert "metrics" in results
        assert results["metrics"]["total_source_files"] == 1
        assert results["metrics"]["lines_of_code"] == 1


class TestCmdBench:
    def test_help(self, capsys):
        result = cmd_bench(["--help"])
        assert result == 0

    def test_run(self, tmp_path, capsys):
        (tmp_path / "app.py").write_text("x = 1\n")
        result = cmd_bench(["run", str(tmp_path)])
        assert result == 0
        out = capsys.readouterr().out
        assert "Benchmark saved" in out

    def test_history_empty(self, tmp_path, capsys):
        os.chdir(tmp_path)
        result = cmd_bench(["history", str(tmp_path)])
        assert result == 0

    def test_compare_insufficient(self, tmp_path, capsys):
        os.chdir(tmp_path)
        result = cmd_bench(["compare"])
        assert result == 0
        out = capsys.readouterr().out
        assert "Need at least 2" in out
