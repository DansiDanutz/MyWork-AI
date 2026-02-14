"""Tests for enhanced mw init command with auto-detection."""

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
from mw import _detect_project_type, cmd_init


class TestDetectProjectType:
    """Test project type auto-detection."""

    def test_detect_python_pip(self, tmp_path):
        (tmp_path / "requirements.txt").write_text("fastapi>=0.100\nuvicorn\n")
        info = _detect_project_type(tmp_path)
        assert info["language"] == "python"
        assert info["framework"] == "FastAPI"
        assert info["package_manager"] == "pip"

    def test_detect_python_poetry(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text('[tool.poetry]\nname="test"\n')
        (tmp_path / "poetry.lock").write_text("")
        info = _detect_project_type(tmp_path)
        assert info["language"] == "python"
        assert info["package_manager"] == "poetry"

    def test_detect_python_django(self, tmp_path):
        (tmp_path / "requirements.txt").write_text("Django>=4.0\n")
        info = _detect_project_type(tmp_path)
        assert info["framework"] == "Django"

    def test_detect_python_flask(self, tmp_path):
        (tmp_path / "requirements.txt").write_text("flask>=2.0\n")
        info = _detect_project_type(tmp_path)
        assert info["framework"] == "Flask"

    def test_detect_node_nextjs(self, tmp_path):
        pkg = {"dependencies": {"next": "14.0.0", "react": "18.0.0"}}
        (tmp_path / "package.json").write_text(json.dumps(pkg))
        info = _detect_project_type(tmp_path)
        assert "node" in info["language"]
        assert info["framework"] == "Next.js"

    def test_detect_node_express(self, tmp_path):
        pkg = {"dependencies": {"express": "4.18.0"}}
        (tmp_path / "package.json").write_text(json.dumps(pkg))
        info = _detect_project_type(tmp_path)
        assert info["framework"] == "Express.js"

    def test_detect_node_pnpm(self, tmp_path):
        pkg = {"dependencies": {}}
        (tmp_path / "package.json").write_text(json.dumps(pkg))
        (tmp_path / "pnpm-lock.yaml").write_text("")
        info = _detect_project_type(tmp_path)
        assert info["package_manager"] == "pnpm"

    def test_detect_go(self, tmp_path):
        (tmp_path / "go.mod").write_text("module example.com/test\n")
        info = _detect_project_type(tmp_path)
        assert "go" in info["language"]

    def test_detect_rust(self, tmp_path):
        (tmp_path / "Cargo.toml").write_text('[package]\nname="test"\n')
        info = _detect_project_type(tmp_path)
        assert "rust" in info["language"]

    def test_detect_tests_exist(self, tmp_path):
        (tmp_path / "tests").mkdir()
        info = _detect_project_type(tmp_path)
        assert info["has_tests"] is True

    def test_detect_no_tests(self, tmp_path):
        info = _detect_project_type(tmp_path)
        assert info["has_tests"] is False

    def test_detect_ci_github(self, tmp_path):
        (tmp_path / ".github" / "workflows").mkdir(parents=True)
        info = _detect_project_type(tmp_path)
        assert info["has_ci"] is True

    def test_detect_docker(self, tmp_path):
        (tmp_path / "Dockerfile").write_text("FROM python:3.12\n")
        info = _detect_project_type(tmp_path)
        assert info["has_docker"] is True

    def test_detect_unknown(self, tmp_path):
        info = _detect_project_type(tmp_path)
        assert info["language"] == "unknown"
        assert any("No recognized" in r for r in info["recommendations"])

    def test_detect_multilang(self, tmp_path):
        (tmp_path / "requirements.txt").write_text("flask\n")
        pkg = {"dependencies": {"react": "18.0.0", "vite": "5.0.0"}}
        (tmp_path / "package.json").write_text(json.dumps(pkg))
        info = _detect_project_type(tmp_path)
        assert "python" in info["language"]
        assert "node" in info["language"]

    def test_recommendations_no_git(self, tmp_path):
        info = _detect_project_type(tmp_path)
        assert any("git init" in r for r in info["recommendations"])

    def test_recommendations_no_ci(self, tmp_path):
        (tmp_path / "requirements.txt").write_text("flask\n")
        info = _detect_project_type(tmp_path)
        assert any("CI/CD" in r for r in info["recommendations"])

    def test_detect_nestjs(self, tmp_path):
        pkg = {"dependencies": {"@nestjs/core": "10.0.0"}}
        (tmp_path / "package.json").write_text(json.dumps(pkg))
        info = _detect_project_type(tmp_path)
        assert info["framework"] == "NestJS"

    def test_detect_svelte(self, tmp_path):
        pkg = {"dependencies": {"svelte": "4.0.0"}}
        (tmp_path / "package.json").write_text(json.dumps(pkg))
        info = _detect_project_type(tmp_path)
        assert info["framework"] == "Svelte"

    def test_detect_sveltekit(self, tmp_path):
        pkg = {"dependencies": {"@sveltejs/kit": "2.0.0", "svelte": "4.0.0"}}
        (tmp_path / "package.json").write_text(json.dumps(pkg))
        info = _detect_project_type(tmp_path)
        assert info["framework"] == "SvelteKit"

    def test_detect_vue(self, tmp_path):
        pkg = {"dependencies": {"vue": "3.0.0"}}
        (tmp_path / "package.json").write_text(json.dumps(pkg))
        info = _detect_project_type(tmp_path)
        assert info["framework"] == "Vue.js"


class TestCmdInit:
    """Test mw init command."""

    def test_init_creates_mw_dir(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = cmd_init([])
        assert result == 0
        assert (tmp_path / ".mw").exists()
        assert (tmp_path / ".mw" / "config.json").exists()

    def test_init_creates_gsd_plan(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cmd_init([])
        assert (tmp_path / ".mw" / "gsd" / "PLAN.md").exists()

    def test_init_creates_env(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cmd_init([])
        assert (tmp_path / ".env").exists()

    def test_init_refuses_if_exists(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".mw").mkdir()
        result = cmd_init([])
        assert result == 1

    def test_init_force_reinitializes(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".mw").mkdir()
        result = cmd_init(["--force"])
        assert result == 0

    def test_init_minimal(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = cmd_init(["--minimal"])
        assert result == 0
        config = json.loads((tmp_path / ".mw" / "config.json").read_text())
        assert config["type"] == "unknown"

    def test_init_config_has_detected_info(self, tmp_path, monkeypatch):
        (tmp_path / "requirements.txt").write_text("fastapi\n")
        monkeypatch.chdir(tmp_path)
        cmd_init([])
        config = json.loads((tmp_path / ".mw" / "config.json").read_text())
        assert config["type"] == "python"
        assert config["framework"] == "FastAPI"

    def test_init_help(self):
        result = cmd_init(["--help"])
        assert result == 0
