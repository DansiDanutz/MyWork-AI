"""Tests for mw deps command."""
import os
import sys
import json
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
from mw import cmd_deps


@pytest.fixture
def pip_project(tmp_path, monkeypatch):
    """Create a project with requirements.txt."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "requirements.txt").write_text("flask==3.0.0\nrequests>=2.31.0\npytest\n# comment\n")
    return tmp_path


@pytest.fixture
def npm_project(tmp_path, monkeypatch):
    """Create a project with package.json."""
    monkeypatch.chdir(tmp_path)
    pkg = {
        "name": "test-proj",
        "version": "1.0.0",
        "dependencies": {"express": "^4.18.0", "lodash": "^4.17.21"},
        "devDependencies": {"jest": "^29.0.0", "eslint": "^8.0.0"}
    }
    (tmp_path / "package.json").write_text(json.dumps(pkg))
    return tmp_path


@pytest.fixture
def empty_project(tmp_path, monkeypatch):
    """Project with no dependency files."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_deps_no_project(empty_project):
    """Should return 1 when no dep files found."""
    assert cmd_deps([]) == 1


def test_deps_overview_pip(pip_project):
    """Should show Python deps overview."""
    assert cmd_deps([]) == 0


def test_deps_overview_npm(npm_project):
    """Should show Node.js deps overview."""
    assert cmd_deps([]) == 0


def test_deps_list_pip(pip_project, capsys):
    """Should list pip dependencies."""
    assert cmd_deps(["list"]) == 0
    out = capsys.readouterr().out
    assert "flask" in out
    assert "requests" in out
    assert "pytest" in out


def test_deps_list_npm(npm_project, capsys):
    """Should list npm dependencies."""
    assert cmd_deps(["list"]) == 0
    out = capsys.readouterr().out
    assert "express" in out
    assert "lodash" in out


def test_deps_list_npm_dev(npm_project, capsys):
    """Should show dev deps."""
    assert cmd_deps(["list"]) == 0
    out = capsys.readouterr().out
    assert "2 prod" in out or "express" in out


def test_deps_size(pip_project):
    """Should work even with no dep dirs."""
    assert cmd_deps(["size"]) == 0


def test_deps_export_pip(pip_project):
    """Should attempt export."""
    assert cmd_deps(["export"]) == 0


def test_deps_cleanup(pip_project):
    """Should run cleanup."""
    assert cmd_deps(["cleanup"]) == 0


def test_deps_tree(pip_project):
    """Should run tree."""
    assert cmd_deps(["tree"]) == 0


@pytest.mark.slow
@pytest.mark.timeout(30)
def test_deps_outdated_pip(pip_project):
    """Should run outdated check."""
    assert cmd_deps(["outdated"]) == 0


@pytest.mark.slow
@pytest.mark.timeout(30)
def test_deps_audit_pip(pip_project):
    """Should run audit."""
    assert cmd_deps(["audit"]) == 0


@pytest.mark.slow
@pytest.mark.timeout(30)
def test_deps_licenses(pip_project):
    """Should run license check."""
    assert cmd_deps(["licenses"]) == 0


def test_deps_why(pip_project):
    """Should handle why subcommand."""
    assert cmd_deps(["why", "flask"]) == 0


def test_deps_unknown_subcmd(pip_project):
    """Unknown subcmd falls to overview."""
    assert cmd_deps(["nonexistent"]) == 0
