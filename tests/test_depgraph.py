"""Tests for mw depgraph command."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
from depgraph import extract_imports, scan_project, detect_cycles, format_ascii, format_dot, format_json, main


def test_extract_imports_basic(tmp_path):
    f = tmp_path / "example.py"
    f.write_text("import os\nimport json\nfrom pathlib import Path\n")
    local, ext = extract_imports(f)
    assert "os" in ext
    assert "json" in ext
    assert "pathlib" in ext


def test_extract_imports_relative(tmp_path):
    f = tmp_path / "example.py"
    f.write_text("from . import utils\nfrom .config import X\n")
    local, ext = extract_imports(f)
    assert "utils" in local or "config" in local


def test_scan_project(tmp_path):
    (tmp_path / "main.py").write_text("import os\nprint('hello')\n")
    (tmp_path / "utils.py").write_text("import json\ndef helper(): pass\n")
    graph = scan_project(tmp_path)
    assert len(graph) == 2
    assert "main" in graph
    assert "utils" in graph


def test_detect_no_cycles():
    graph = {
        "a": {"local_deps": ["b"]},
        "b": {"local_deps": []},
    }
    cycles = detect_cycles(graph)
    assert len(cycles) == 0


def test_format_ascii():
    graph = {"mod": {"local_deps": ["config"], "loc": 100}}
    output = format_ascii(graph)
    assert "mod" in output
    assert "config" in output


def test_format_dot():
    graph = {"mod": {"local_deps": ["config"], "loc": 100}}
    output = format_dot(graph, "test")
    assert "digraph" in output
    assert "mod" in output


def test_format_json():
    graph = {"mod": {"local_deps": [], "loc": 50}}
    output = format_json(graph)
    assert '"mod"' in output


def test_main_help(capsys):
    main(["--help"])
    captured = capsys.readouterr()
    assert "depgraph" in captured.out.lower() or "dependency" in captured.out.lower()
