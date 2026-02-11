"""Tests for mw perf — Project Performance Analyzer."""
import os
import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from tools.perf_analyzer import (
    find_project_root, detect_stack, analyze_dependencies,
    analyze_file_structure, analyze_code_quality, generate_tips, format_size, run
)

def test_format_size():
    assert format_size(0) == "0.0B"
    assert format_size(1024) == "1.0KB"
    assert format_size(1048576) == "1.0MB"
    assert "GB" in format_size(1073741824)

def test_detect_stack_node():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "package.json").write_text('{"dependencies":{"next":"14.0.0"}}')
        stack = detect_stack(Path(d))
        assert stack["lang"] == "node"
        assert stack["framework"] == "Next.js"

def test_detect_stack_python():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "pyproject.toml").write_text("[project]\nname='test'")
        stack = detect_stack(Path(d))
        assert stack["lang"] == "python"

def test_detect_stack_rust():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "Cargo.toml").write_text("[package]\nname='test'")
        stack = detect_stack(Path(d))
        assert stack["lang"] == "rust"

def test_detect_stack_go():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "go.mod").write_text("module test")
        stack = detect_stack(Path(d))
        assert stack["lang"] == "go"

def test_detect_stack_unknown():
    with tempfile.TemporaryDirectory() as d:
        stack = detect_stack(Path(d))
        assert stack["lang"] == "unknown"

def test_analyze_dependencies_node():
    with tempfile.TemporaryDirectory() as d:
        pkg = {"dependencies": {"react": "18", "moment": "2", "lodash": "4"}, "devDependencies": {"jest": "29"}}
        (Path(d) / "package.json").write_text(json.dumps(pkg))
        stack = {"lang": "node", "pkg_manager": "npm"}
        deps = analyze_dependencies(Path(d), stack)
        assert deps["total"] == 4
        assert deps["prod"] == 3
        assert deps["dev"] == 1
        assert len(deps["heavy"]) == 2  # moment + lodash

def test_analyze_dependencies_python():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "requirements.txt").write_text("flask>=2.0\nrequests\n# comment\npytest")
        stack = {"lang": "python", "pkg_manager": "pip"}
        deps = analyze_dependencies(Path(d), stack)
        assert deps["total"] == 3

def test_analyze_file_structure():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "a.py").write_text("print('hi')")
        (Path(d) / "b.js").write_text("console.log('hi')")
        (Path(d) / "empty.txt").write_text("")
        stats = analyze_file_structure(Path(d))
        assert stats["total_files"] == 3
        assert stats["empty_files"] == 1

def test_analyze_code_quality():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "main.py").write_text("# TODO fix this\nx = 1\n# FIXME broken\ny = 2\n")
        stack = {"lang": "python"}
        q = analyze_code_quality(Path(d), stack)
        assert q["todo_count"] == 1
        assert q["fixme_count"] == 1
        assert q["code_lines"] >= 2

def test_generate_tips_clean():
    tips = generate_tips({}, {"total": 5}, {"empty_files": 0}, {"todo_count": 0, "fixme_count": 0})
    assert any("healthy" in t[1].lower() for t in tips)

def test_generate_tips_heavy_deps():
    deps = {"total": 60, "heavy": [{"name": "moment", "alternative": "dayjs"}]}
    tips = generate_tips({}, deps, {"empty_files": 0}, {"todo_count": 0, "fixme_count": 0})
    assert any("moment" in t[1] for t in tips)

def test_find_project_root():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "package.json").write_text("{}")
        sub = Path(d) / "src" / "deep"
        sub.mkdir(parents=True)
        root = find_project_root(str(sub))
        assert root == Path(d)

def test_run_help(capsys):
    run(["--help"])
    out = capsys.readouterr().out
    assert "Performance Analyzer" in out

def test_run_on_project():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "pyproject.toml").write_text("[project]\nname='test'")
        (Path(d) / "main.py").write_text("print('hello')\n")
        result = run([d])
        assert result == 0
