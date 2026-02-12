"""Tests for changelog_gen.py"""
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.changelog_gen import parse_commit, group_commits, format_markdown, get_stats


def _make_commit(subject, body=""):
    return {"hash": "abc123def", "short": "abc123d", "subject": subject,
            "author": "test", "date": "2026-02-12T10:00:00+00:00", "body": body, "breaking": False}


def test_parse_feat():
    c = parse_commit(_make_commit("feat: add login page"))
    assert c["type"] == "feat"
    assert c["description"] == "add login page"
    assert c["scope"] is None


def test_parse_scoped():
    c = parse_commit(_make_commit("fix(auth): resolve token expiry"))
    assert c["type"] == "fix"
    assert c["scope"] == "auth"
    assert c["description"] == "resolve token expiry"


def test_parse_breaking():
    c = parse_commit(_make_commit("feat!: remove legacy API"))
    assert c["breaking"] is True


def test_parse_breaking_body():
    c = parse_commit(_make_commit("feat: new API", "BREAKING CHANGE: old API removed"))
    assert c["breaking"] is True


def test_parse_non_conventional():
    c = parse_commit(_make_commit("random commit message"))
    assert c["type"] == "other"
    assert c["description"] == "random commit message"


def test_group_commits():
    commits = [
        _make_commit("feat: feature A"),
        _make_commit("feat: feature B"),
        _make_commit("fix: bug fix"),
        _make_commit("docs: update readme"),
    ]
    groups, breaking = group_commits(commits)
    assert len(groups["feat"]) == 2
    assert len(groups["fix"]) == 1
    assert len(groups["docs"]) == 1
    assert len(breaking) == 0


def test_group_breaking():
    commits = [_make_commit("feat!: breaking change")]
    groups, breaking = group_commits(commits)
    assert len(breaking) == 1


def test_format_markdown():
    commits = [_make_commit("feat: cool feature"), _make_commit("fix: a bug")]
    groups, breaking = group_commits(commits)
    stats = get_stats(commits)
    md = format_markdown(groups, breaking, "Test", stats)
    assert "# Test" in md
    assert "cool feature" in md
    assert "a bug" in md
    assert "Features" in md
    assert "Bug Fixes" in md


def test_stats():
    commits = [
        _make_commit("feat: a"),
        _make_commit("fix: b"),
        {**_make_commit("docs: c"), "author": "other"},
    ]
    stats = get_stats(commits)
    assert stats["total"] == 3
    assert stats["authors"] == 2
    assert stats["types"]["feat"] == 1


def test_json_output():
    from tools.changelog_gen import format_json
    commits = [_make_commit("feat: new thing")]
    groups, breaking = group_commits(commits)
    stats = get_stats(commits)
    result = json.loads(format_json(groups, breaking, stats))
    assert "changes" in result
    assert result["stats"]["total"] == 1
