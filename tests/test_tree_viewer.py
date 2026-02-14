"""Tests for mw tree command."""
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from tools.tree_viewer import build_tree, cmd_tree, human_size, get_icon


def test_human_size():
    assert human_size(0) == "0B"
    assert human_size(512) == "512B"
    assert human_size(1024) == "1.0K"
    assert human_size(1048576) == "1.0M"
    assert human_size(1073741824) == "1.0G"


def test_get_icon_directory():
    assert get_icon("src", True) == "📁"


def test_get_icon_python():
    assert get_icon("main.py", False) == "🐍"


def test_get_icon_js():
    assert get_icon("index.js", False) == "📜"


def test_get_icon_readme():
    assert get_icon("README.md", False) == "📖"


def test_get_icon_dockerfile():
    assert get_icon("Dockerfile", False) == "🐳"


def test_get_icon_unknown():
    assert get_icon("data.xyz", False) == "📄"


def test_build_tree_basic():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "file.py").write_text("hello")
        (root / "sub").mkdir()
        (root / "sub" / "nested.js").write_text("world")

        lines, stats = build_tree(root, max_depth=3, show_all=True)
        assert stats["files"] == 2
        assert stats["dirs"] == 1
        assert any("file.py" in l for l in lines)
        assert any("nested.js" in l for l in lines)


def test_build_tree_depth_limit():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "a").mkdir()
        (root / "a" / "b").mkdir()
        (root / "a" / "b" / "deep.txt").write_text("deep")

        lines, stats = build_tree(root, max_depth=1, show_all=True)
        assert stats["dirs"] == 1  # only 'a'
        assert stats["files"] == 0  # deep.txt is beyond depth


def test_build_tree_dirs_only():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "file.txt").write_text("x")
        (root / "subdir").mkdir()

        lines, stats = build_tree(root, max_depth=3, show_all=True, dirs_only=True)
        assert stats["files"] == 0
        assert stats["dirs"] == 1


def test_build_tree_filter_ext():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "a.py").write_text("x")
        (root / "b.js").write_text("y")
        (root / "c.py").write_text("z")

        lines, stats = build_tree(root, max_depth=3, show_all=True, filter_ext=".py")
        assert stats["files"] == 2


def test_build_tree_show_size():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "big.txt").write_text("x" * 2048)

        lines, stats = build_tree(root, max_depth=3, show_all=True, show_size=True)
        assert stats["total_size"] == 2048


def test_cmd_tree_help(capsys):
    ret = cmd_tree(["--help"])
    assert ret == 0


def test_cmd_tree_json(capsys):
    ret = cmd_tree(["--json", "--depth", "1"])
    assert ret == 0
    out = capsys.readouterr().out
    data = __import__("json").loads(out)
    assert "dirs" in data
    assert "files" in data


def test_cmd_tree_bad_path(capsys):
    ret = cmd_tree(["/nonexistent_path_xyz"])
    assert ret == 1
