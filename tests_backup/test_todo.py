"""Tests for mw todo command."""
import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
from mw import cmd_todo


@pytest.fixture
def tmp_project(tmp_path):
    """Create a temp project with various TODO comments."""
    py_file = tmp_path / "app.py"
    py_file.write_text(
        "# TODO: implement login\n"
        "def login():\n"
        "    pass  # FIXME: broken auth\n"
        "# HACK: temporary workaround\n"
        "# NOTE: this is documented\n"
        "x = 1  # XXX: danger zone\n"
    )
    js_file = tmp_path / "index.js"
    js_file.write_text(
        "// TODO: add error handling\n"
        "// OPTIMIZE: slow query here\n"
    )
    return tmp_path


def test_todo_basic(tmp_project, capsys):
    """Test basic scanning finds all tags."""
    result = cmd_todo([str(tmp_project)])
    captured = capsys.readouterr()
    assert "7 actionable comments" in captured.out
    assert result == 0


def test_todo_stats(tmp_project, capsys):
    """Test --stats mode shows counts."""
    result = cmd_todo([str(tmp_project), "--stats"])
    captured = capsys.readouterr()
    assert "Todo Stats" in captured.out
    assert "TODO" in captured.out
    assert result == 0


def test_todo_json(tmp_project, capsys):
    """Test --json output is valid JSON."""
    result = cmd_todo([str(tmp_project), "--json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["total"] == 7
    assert "TODO" in data["by_tag"]
    assert len(data["items"]) == 7
    assert result == 0


def test_todo_filter_tag(tmp_project, capsys):
    """Test --tag filters to specific tag."""
    result = cmd_todo([str(tmp_project), "--tag", "FIXME"])
    captured = capsys.readouterr()
    assert "1 actionable comments" in captured.out
    assert result == 0


def test_todo_filter_tag_none(tmp_project, capsys):
    """Test --tag with no matches."""
    result = cmd_todo([str(tmp_project), "--tag", "REFACTOR"])
    captured = capsys.readouterr()
    assert "clean codebase" in captured.out
    assert result == 0


def test_todo_empty_dir(tmp_path, capsys):
    """Test scanning empty directory."""
    result = cmd_todo([str(tmp_path)])
    captured = capsys.readouterr()
    assert "clean codebase" in captured.out
    assert result == 0


def test_todo_bad_path(capsys):
    """Test non-existent path returns error."""
    result = cmd_todo(["/nonexistent/path"])
    captured = capsys.readouterr()
    assert "not found" in captured.out
    assert result == 1


def test_todo_help(capsys):
    """Test --help output."""
    result = cmd_todo(["--help"])
    captured = capsys.readouterr()
    assert "Todo Scanner" in captured.out
    assert result == 0


def test_todo_skips_node_modules(tmp_path, capsys):
    """Test that node_modules is skipped."""
    nm = tmp_path / "node_modules" / "pkg"
    nm.mkdir(parents=True)
    (nm / "index.js").write_text("// TODO: should be skipped\n")
    result = cmd_todo([str(tmp_path)])
    captured = capsys.readouterr()
    assert "clean codebase" in captured.out
    assert result == 0
