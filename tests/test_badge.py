"""Tests for mw badge command."""
import json
import tempfile
from pathlib import Path
import pytest
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
from badge import (
    detect_version, count_tests, shields_url,
    generate_badges, format_badges_md, update_readme,
)


# Reuse bump_version from release if needed
def test_shields_url():
    url = shields_url("version", "v2.1.0", "blue")
    assert "img.shields.io" in url
    assert "version" in url
    assert "v2.1.0" in url
    assert "blue" in url


def test_shields_url_encodes_spaces():
    url = shields_url("lines of code", "10k+", "green")
    assert "lines%20of%20code" in url
    assert "10k%2B" in url


def test_detect_version_pyproject(tmp_path):
    (tmp_path / "pyproject.toml").write_text('version = "1.2.3"')
    assert detect_version(tmp_path) == "1.2.3"


def test_detect_version_package_json(tmp_path):
    (tmp_path / "package.json").write_text(json.dumps({"version": "3.0.0"}))
    assert detect_version(tmp_path) == "3.0.0"


def test_detect_version_none(tmp_path):
    assert detect_version(tmp_path) is None


def test_count_tests_finds_functions(tmp_path):
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_foo.py").write_text(
        "def test_one(): pass\ndef test_two(): pass\ndef helper(): pass\n"
    )
    assert count_tests(tmp_path) == 2


def test_count_tests_empty(tmp_path):
    assert count_tests(tmp_path) == 0


def test_generate_badges_minimal(tmp_path):
    (tmp_path / "pyproject.toml").write_text('version = "0.1.0"')
    badges = generate_badges(tmp_path)
    names = [b["name"] for b in badges]
    assert "version" in names
    assert "platform" in names


def test_format_badges_md():
    badges = [
        {"label": "ver", "url": "https://example.com/badge.svg"},
        {"label": "tests", "url": "https://example.com/tests.svg"},
    ]
    md = format_badges_md(badges)
    assert "![ver]" in md
    assert "![tests]" in md


def test_update_readme_inserts_badges(tmp_path):
    (tmp_path / "README.md").write_text("# My Project\n\nSome text.\n")
    (tmp_path / "pyproject.toml").write_text('version = "1.0.0"')
    badges = [{"label": "v", "url": "https://img.shields.io/badge/v-1.0.0-blue", "name": "version", "value": "v1.0.0", "color": "blue"}]
    update_readme(tmp_path, badges)
    content = (tmp_path / "README.md").read_text()
    assert "badges-start" in content
    assert "shields.io" in content


def test_update_readme_replaces_existing(tmp_path):
    (tmp_path / "README.md").write_text(
        "# Proj\n<!-- badges-start -->\nOLD\n<!-- badges-end -->\nText\n"
    )
    badges = [{"label": "new", "url": "https://new.svg", "name": "new", "value": "1", "color": "green"}]
    update_readme(tmp_path, badges)
    content = (tmp_path / "README.md").read_text()
    assert "OLD" not in content
    assert "new.svg" in content
    assert "Text" in content
