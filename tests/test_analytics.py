"""Tests for analytics engine."""
import pytest
from pathlib import Path
from tools.analytics import (
    analyze_languages, analyze_complexity, analyze_security,
    analyze_deps, analyze_git_trends, get_project_root
)


def test_get_project_root():
    root = get_project_root()
    assert root.exists()
    assert (root / ".git").exists() or (root / "setup.py").exists()


def test_analyze_languages():
    root = get_project_root()
    langs = analyze_languages(root)
    assert isinstance(langs, dict)
    assert "Python" in langs
    assert langs["Python"] > 0


def test_analyze_complexity():
    root = get_project_root()
    cx = analyze_complexity(root)
    assert cx["total_files"] > 0
    assert cx["total_lines"] > 0
    assert isinstance(cx["large_files"], list)
    assert isinstance(cx["long_functions"], list)
    assert isinstance(cx["todo_fixme_count"], int)


def test_analyze_security():
    root = get_project_root()
    sec = analyze_security(root)
    assert 0 <= sec["score"] <= 100
    assert isinstance(sec["issues"], list)
    assert isinstance(sec["env_ignored"], bool)


def test_analyze_deps():
    root = get_project_root()
    deps = analyze_deps(root)
    assert "python" in deps
    assert "node" in deps


def test_analyze_git_trends():
    root = get_project_root()
    trends = analyze_git_trends(root)
    assert "available" in trends
    if trends["available"]:
        assert "total_commits_30d" in trends
        assert "current_streak" in trends
        assert trends["total_commits_30d"] >= 0


def test_complexity_avg_lines():
    root = get_project_root()
    cx = analyze_complexity(root)
    expected_avg = cx["total_lines"] / max(cx["total_files"], 1)
    assert abs(cx["avg_lines_per_file"] - round(expected_avg, 1)) < 0.2


def test_security_env_example_exists():
    root = get_project_root()
    sec = analyze_security(root)
    # MyWork-AI should have .env.example
    assert sec["has_env_example"] is True
