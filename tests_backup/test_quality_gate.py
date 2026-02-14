"""Tests for mw check (quality gate)."""

import json
import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


@pytest.fixture
def tmp_project(tmp_path):
    """Create a temporary project directory."""
    (tmp_path / ".git").mkdir()
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_example.py").write_text("def test_ok(): pass\n")
    return tmp_path


def test_check_help(capsys):
    from tools.quality_gate import cmd_check
    result = cmd_check(["--help"])
    assert result == 0
    out = capsys.readouterr().out
    assert "Quality Gate" in out
    assert "--quick" in out


def test_detect_project_python(tmp_project):
    from tools.quality_gate import _detect_project
    info = _detect_project(str(tmp_project))
    assert info["python"] is True
    assert info["git"] is True
    assert info["has_tests"] is True
    assert info["node"] is False


def test_detect_project_node(tmp_path):
    from tools.quality_gate import _detect_project
    (tmp_path / "package.json").write_text('{"name":"test"}')
    (tmp_path / "__tests__").mkdir()
    info = _detect_project(str(tmp_path))
    assert info["node"] is True
    assert info["has_tests"] is True
    assert info["python"] is False


def test_detect_project_empty(tmp_path):
    from tools.quality_gate import _detect_project
    info = _detect_project(str(tmp_path))
    assert info["python"] is False
    assert info["node"] is False
    assert info["git"] is False


def test_run_check_command_not_found():
    from tools.quality_gate import _run_check
    passed, output, dur = _run_check("test", ["nonexistent_command_xyz"])
    assert passed is None
    assert "not found" in output


def test_run_check_timeout():
    from tools.quality_gate import _run_check
    passed, output, dur = _run_check("test", ["sleep", "10"], timeout=1)
    assert passed is False
    assert "Timed out" in output


def test_check_quick_mode(tmp_project, capsys):
    from tools.quality_gate import cmd_check
    os.chdir(tmp_project)
    result = cmd_check(["--quick", str(tmp_project)])
    out = capsys.readouterr().out
    assert "Quality Gate" in out
    # Quick mode should not run tests
    assert "Test" not in out or "skipped" in out


def test_check_git_no_repo(tmp_path, capsys):
    from tools.quality_gate import _check_git, _detect_project
    project = _detect_project(str(tmp_path))
    tool, passed, detail, dur = _check_git(project)
    assert passed is None


def test_install_hook(tmp_project, capsys):
    from tools.quality_gate import _install_hook
    result = _install_hook(str(tmp_project))
    assert result == 0
    hook = tmp_project / ".git" / "hooks" / "pre-commit"
    assert hook.exists()
    assert "mw check" in hook.read_text()
    assert os.access(hook, os.X_OK)


def test_install_hook_no_git(tmp_path, capsys):
    from tools.quality_gate import _install_hook
    result = _install_hook(str(tmp_path))
    assert result == 1


def test_check_json_output(tmp_project, capsys):
    from tools.quality_gate import cmd_check
    os.chdir(tmp_project)
    cmd_check(["--quick", "--json", str(tmp_project)])
    out = capsys.readouterr().out
    # Find JSON in output
    json_start = out.find("{")
    assert json_start >= 0
    data = json.loads(out[json_start:])
    assert "grade" in data
    assert "checks" in data
    assert isinstance(data["checks"], list)
