#!/usr/bin/env python3
"""Tests for mw ci — CI/CD pipeline generator."""
import os
import json
import tempfile
import pytest
from pathlib import Path

# Import the module
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
from mw_ci import ProjectAnalyzer, GitHubActionsGenerator, GitLabCIGenerator, main


class TestProjectAnalyzer:
    def test_detect_python_project(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text('''
[project]
requires-python = ">=3.9"
dependencies = ["fastapi", "pytest"]
''')
        (tmp_path / "tests").mkdir()
        a = ProjectAnalyzer(str(tmp_path)).analyze()
        assert "python" in a["languages"]
        assert "fastapi" in a["frameworks"]
        assert a["has_tests"]

    def test_detect_node_project(self, tmp_path):
        (tmp_path / "package.json").write_text(json.dumps({
            "dependencies": {"react": "^18", "next": "^14"},
            "devDependencies": {"jest": "^29"},
            "scripts": {"test": "jest", "build": "next build", "lint": "eslint ."}
        }))
        a = ProjectAnalyzer(str(tmp_path)).analyze()
        assert "node" in a["languages"]
        assert "nextjs" in a["frameworks"]
        assert a["has_tests"]

    def test_detect_go_project(self, tmp_path):
        (tmp_path / "go.mod").write_text("module example.com/test\ngo 1.21\n")
        a = ProjectAnalyzer(str(tmp_path)).analyze()
        assert "go" in a["languages"]
        assert a["has_tests"]

    def test_detect_rust_project(self, tmp_path):
        (tmp_path / "Cargo.toml").write_text('[package]\nname = "test"\n')
        a = ProjectAnalyzer(str(tmp_path)).analyze()
        assert "rust" in a["languages"]

    def test_detect_docker(self, tmp_path):
        (tmp_path / "Dockerfile").write_text("FROM python:3.11\n")
        (tmp_path / "pyproject.toml").write_text('[project]\nrequires-python = ">=3.11"\n')
        a = ProjectAnalyzer(str(tmp_path)).analyze()
        assert a["docker"]

    def test_detect_vercel(self, tmp_path):
        (tmp_path / "vercel.json").write_text("{}")
        (tmp_path / "package.json").write_text(json.dumps({"dependencies": {"react": "^18"}}))
        a = ProjectAnalyzer(str(tmp_path)).analyze()
        assert "vercel" in a["deploy_targets"]

    def test_detect_pnpm(self, tmp_path):
        (tmp_path / "package.json").write_text(json.dumps({"dependencies": {}}))
        (tmp_path / "pnpm-lock.yaml").write_text("")
        a = ProjectAnalyzer(str(tmp_path)).analyze()
        assert "pnpm" in a["package_managers"]

    def test_empty_project(self, tmp_path):
        a = ProjectAnalyzer(str(tmp_path)).analyze()
        assert a["languages"] == []

    def test_detect_poetry(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text('[tool.poetry]\nname = "test"\n')
        a = ProjectAnalyzer(str(tmp_path)).analyze()
        assert "poetry" in a["package_managers"]


class TestGitHubActionsGenerator:
    def test_python_workflow(self):
        analysis = {
            "languages": ["python"],
            "frameworks": ["fastapi"],
            "package_managers": ["pip"],
            "has_tests": True,
            "test_commands": ["pytest"],
            "build_commands": ["pip install -r requirements.txt"],
            "lint_commands": [],
            "docker": False,
            "node_version": None,
            "python_version": "3.11",
            "env_vars": [],
            "services": [],
            "deploy_targets": [],
        }
        output = GitHubActionsGenerator().generate(analysis)
        assert "name: CI" in output
        assert "actions/checkout@v4" in output
        assert "setup-python@v5" in output
        assert "pytest" in output

    def test_node_workflow(self):
        analysis = {
            "languages": ["node"],
            "frameworks": ["nextjs", "react"],
            "package_managers": ["npm"],
            "has_tests": True,
            "test_commands": ["npm test"],
            "build_commands": ["npm run build"],
            "lint_commands": ["npm run lint"],
            "docker": False,
            "node_version": "20",
            "python_version": None,
            "env_vars": [],
            "services": [],
            "deploy_targets": ["vercel"],
        }
        output = GitHubActionsGenerator().generate(analysis)
        assert "setup-node@v4" in output
        assert "npm run build" in output
        assert "Deploy to Vercel" in output

    def test_go_workflow(self):
        analysis = {
            "languages": ["go"],
            "frameworks": [],
            "package_managers": [],
            "has_tests": True,
            "test_commands": ["go test ./..."],
            "build_commands": ["go build ./..."],
            "lint_commands": [],
            "docker": False,
            "node_version": None,
            "python_version": None,
            "env_vars": [],
            "services": [],
            "deploy_targets": [],
        }
        output = GitHubActionsGenerator().generate(analysis)
        assert "setup-go@v5" in output
        assert "go test" in output


class TestGitLabCIGenerator:
    def test_python_pipeline(self):
        analysis = {
            "languages": ["python"],
            "frameworks": [],
            "package_managers": ["pip"],
            "has_tests": True,
            "test_commands": ["pytest"],
            "build_commands": ["pip install -r requirements.txt"],
            "lint_commands": [],
            "docker": False,
            "node_version": None,
            "python_version": "3.11",
            "env_vars": [],
            "services": [],
            "deploy_targets": [],
        }
        output = GitLabCIGenerator().generate(analysis)
        assert "stages:" in output
        assert "image: python:3.11" in output
        assert "pytest" in output


class TestCLI:
    def test_help(self, capsys):
        main(["--help"])
        out = capsys.readouterr().out
        assert "CI/CD Generator" in out

    def test_list_templates(self, capsys):
        main(["list-templates"])
        out = capsys.readouterr().out
        assert "python" in out
        assert "node" in out

    def test_generate_dry_run(self, tmp_path, capsys):
        (tmp_path / "pyproject.toml").write_text('[project]\nrequires-python = ">=3.11"\n')
        (tmp_path / "tests").mkdir()
        main(["generate", "--dry-run", "--path", str(tmp_path)])
        out = capsys.readouterr().out
        assert "Preview" in out

    def test_generate_writes_file(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text('[project]\nrequires-python = ">=3.11"\n')
        (tmp_path / "tests").mkdir()
        main(["generate", "--path", str(tmp_path)])
        assert (tmp_path / ".github" / "workflows" / "ci.yml").exists()

    def test_no_overwrite_without_force(self, tmp_path, capsys):
        (tmp_path / "pyproject.toml").write_text('[project]\nrequires-python = ">=3.11"\n')
        (tmp_path / "tests").mkdir()
        (tmp_path / ".github" / "workflows").mkdir(parents=True)
        (tmp_path / ".github" / "workflows" / "ci.yml").write_text("existing")
        result = main(["generate", "--path", str(tmp_path)])
        assert result == 1  # should fail

    def test_force_overwrite(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text('[project]\nrequires-python = ">=3.11"\n')
        (tmp_path / "tests").mkdir()
        (tmp_path / ".github" / "workflows").mkdir(parents=True)
        (tmp_path / ".github" / "workflows" / "ci.yml").write_text("existing")
        main(["generate", "--path", str(tmp_path), "--force"])
        content = (tmp_path / ".github" / "workflows" / "ci.yml").read_text()
        assert "Auto-generated by MyWork CI" in content
