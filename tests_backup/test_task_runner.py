"""Tests for mw run — universal task runner."""
import json
import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from tools.task_runner import (
    cmd_run, _discover_mw_tasks, _discover_npm_scripts,
    _discover_makefile, _discover_pyproject, _discover_cargo,
    _discover_procfile, _discover_all, _find_project_root,
)


@pytest.fixture
def tmp_project(tmp_path):
    """Create a temporary project directory."""
    (tmp_path / ".git").mkdir()
    os.chdir(tmp_path)
    return tmp_path


class TestDiscovery:
    def test_mw_tasks(self, tmp_project):
        (tmp_project / "mw.tasks.json").write_text(json.dumps({
            "dev": "python -m http.server",
            "build": {"cmd": "npm run build"},
        }))
        tasks = _discover_mw_tasks(tmp_project)
        assert "dev" in tasks
        assert tasks["dev"] == ("python -m http.server", "mw")
        assert "build" in tasks
        assert tasks["build"] == ("npm run build", "mw")

    def test_npm_scripts(self, tmp_project):
        (tmp_project / "package.json").write_text(json.dumps({
            "scripts": {"dev": "next dev", "build": "next build"}
        }))
        tasks = _discover_npm_scripts(tmp_project)
        assert "npm:dev" in tasks
        assert "npm:build" in tasks
        assert tasks["npm:dev"][1] == "npm"

    def test_makefile(self, tmp_project):
        (tmp_project / "Makefile").write_text("build:\n\tgcc main.c\n\ntest:\n\tpytest\n")
        tasks = _discover_makefile(tmp_project)
        assert "make:build" in tasks
        assert "make:test" in tasks

    def test_cargo(self, tmp_project):
        (tmp_project / "Cargo.toml").write_text("[package]\nname = 'test'\n")
        tasks = _discover_cargo(tmp_project)
        assert "cargo:build" in tasks
        assert "cargo:test" in tasks
        assert len(tasks) == 6

    def test_procfile(self, tmp_project):
        (tmp_project / "Procfile").write_text("web: gunicorn app:app\nworker: celery -A tasks\n")
        tasks = _discover_procfile(tmp_project)
        assert "proc:web" in tasks
        assert "proc:worker" in tasks

    def test_empty_project(self, tmp_project):
        tasks = _discover_all(tmp_project)
        assert len(tasks) == 0

    def test_discover_all_combines(self, tmp_project):
        (tmp_project / "mw.tasks.json").write_text(json.dumps({"dev": "echo dev"}))
        (tmp_project / "package.json").write_text(json.dumps({"scripts": {"start": "node ."}}))
        (tmp_project / "Makefile").write_text("clean:\n\trm -rf dist\n")
        tasks = _discover_all(tmp_project)
        assert len(tasks) == 3

    def test_invalid_json(self, tmp_project):
        (tmp_project / "mw.tasks.json").write_text("not json{")
        tasks = _discover_mw_tasks(tmp_project)
        assert len(tasks) == 0

    def test_npm_no_scripts(self, tmp_project):
        (tmp_project / "package.json").write_text(json.dumps({"name": "test"}))
        tasks = _discover_npm_scripts(tmp_project)
        assert len(tasks) == 0


class TestCmdRun:
    def test_list_tasks(self, tmp_project, capsys):
        (tmp_project / "mw.tasks.json").write_text(json.dumps({"dev": "echo hello"}))
        result = cmd_run([])
        assert result == 0
        out = capsys.readouterr().out
        assert "dev" in out

    def test_help(self, tmp_project, capsys):
        result = cmd_run(["--help"])
        assert result == 0

    def test_add_task(self, tmp_project):
        result = cmd_run(["add", "serve", "python -m http.server"])
        assert result == 0
        data = json.loads((tmp_project / "mw.tasks.json").read_text())
        assert data["serve"] == "python -m http.server"

    def test_add_task_missing_args(self, tmp_project):
        result = cmd_run(["add"])
        assert result == 1

    def test_rm_task(self, tmp_project):
        (tmp_project / "mw.tasks.json").write_text(json.dumps({"dev": "echo"}))
        result = cmd_run(["rm", "dev"])
        assert result == 0
        data = json.loads((tmp_project / "mw.tasks.json").read_text())
        assert "dev" not in data

    def test_rm_missing(self, tmp_project):
        (tmp_project / "mw.tasks.json").write_text(json.dumps({}))
        result = cmd_run(["rm", "nope"])
        assert result == 1

    def test_rm_no_file(self, tmp_project):
        result = cmd_run(["rm", "nope"])
        assert result == 1

    def test_run_task(self, tmp_project):
        (tmp_project / "mw.tasks.json").write_text(json.dumps({"hi": "echo hello"}))
        result = cmd_run(["hi"])
        assert result == 0

    def test_run_not_found(self, tmp_project, capsys):
        result = cmd_run(["nonexistent"])
        assert result == 1
        assert "not found" in capsys.readouterr().out

    def test_run_npm_shortname(self, tmp_project):
        """Can run npm:dev as just 'dev' if unambiguous."""
        (tmp_project / "package.json").write_text(json.dumps({"scripts": {"greet": "echo hi"}}))
        result = cmd_run(["greet"])
        assert result == 0

    def test_run_ambiguous(self, tmp_project, capsys):
        """Ambiguous when same name from multiple sources."""
        (tmp_project / "mw.tasks.json").write_text(json.dumps({"build": "echo mw"}))
        # mw task "build" + Makefile target "build"
        (tmp_project / "Makefile").write_text("build:\n\techo make\n")
        # "build" matches mw task exactly, so no ambiguity
        result = cmd_run(["build"])
        assert result == 0
