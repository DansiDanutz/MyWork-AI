"""Tests for mw ci command — CI/CD pipeline generation."""
import os
import sys
import shutil
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
from mw import cmd_ci


@pytest.fixture
def tmp_project(tmp_path):
    """Create a temporary project directory."""
    return str(tmp_path)


def _make_node_project(path, extras=None):
    """Create a minimal Node.js project."""
    import json
    pkg = {"name": "test", "version": "1.0.0", "scripts": {}, "dependencies": {}, "devDependencies": {}}
    if extras:
        for k, v in extras.items():
            if k in pkg:
                pkg[k].update(v)
    with open(os.path.join(path, "package.json"), "w") as f:
        json.dump(pkg, f)


def _make_python_project(path, use_pyproject=False):
    """Create a minimal Python project."""
    if use_pyproject:
        with open(os.path.join(path, "pyproject.toml"), "w") as f:
            f.write('[project]\nname = "test"\nversion = "1.0.0"\n')
    else:
        with open(os.path.join(path, "requirements.txt"), "w") as f:
            f.write("flask\npytest\n")
    os.makedirs(os.path.join(path, "tests"), exist_ok=True)


class TestCiTemplates:
    def test_templates_returns_zero(self, capsys):
        assert cmd_ci(["templates"]) == 0
        out = capsys.readouterr().out
        assert "GitHub Actions" in out
        assert "GitLab CI" in out

    def test_templates_shows_platforms(self, capsys):
        cmd_ci(["templates"])
        out = capsys.readouterr().out
        assert "--platform github" in out
        assert "--platform gitlab" in out


class TestCiValidate:
    def test_validate_no_ci(self, tmp_project, capsys):
        result = cmd_ci(["validate", tmp_project])
        assert result == 1
        assert "No CI/CD configuration found" in capsys.readouterr().out

    def test_validate_github_actions(self, tmp_project, capsys):
        wf_dir = os.path.join(tmp_project, ".github", "workflows")
        os.makedirs(wf_dir)
        with open(os.path.join(wf_dir, "ci.yml"), "w") as f:
            f.write("name: CI\n")
        result = cmd_ci(["validate", tmp_project])
        assert result == 0
        assert "1 workflow(s) found" in capsys.readouterr().out

    def test_validate_gitlab_ci(self, tmp_project, capsys):
        with open(os.path.join(tmp_project, ".gitlab-ci.yml"), "w") as f:
            f.write("stages:\n  - test\n")
        result = cmd_ci(["validate", tmp_project])
        assert result == 0
        assert "GitLab CI" in capsys.readouterr().out


class TestCiGenerateNode:
    def test_generate_basic_node(self, tmp_project, capsys):
        _make_node_project(tmp_project)
        result = cmd_ci(["generate", tmp_project])
        assert result == 0
        ci_file = os.path.join(tmp_project, ".github", "workflows", "ci.yml")
        assert os.path.exists(ci_file)
        content = open(ci_file).read()
        assert "npm ci" in content
        assert "node" in capsys.readouterr().out.lower()

    def test_generate_node_with_tests(self, tmp_project, capsys):
        _make_node_project(tmp_project, extras={
            "scripts": {"test": "jest"},
            "devDependencies": {"jest": "^29.0.0"}
        })
        result = cmd_ci(["generate", tmp_project])
        assert result == 0
        content = open(os.path.join(tmp_project, ".github", "workflows", "ci.yml")).read()
        assert "npm test" in content

    def test_generate_node_with_lint(self, tmp_project, capsys):
        _make_node_project(tmp_project, extras={
            "scripts": {"lint": "eslint ."},
            "devDependencies": {"eslint": "^8.0.0"}
        })
        cmd_ci(["generate", tmp_project])
        content = open(os.path.join(tmp_project, ".github", "workflows", "ci.yml")).read()
        assert "npm run lint" in content


class TestCiGeneratePython:
    def test_generate_python_requirements(self, tmp_project, capsys):
        _make_python_project(tmp_project)
        result = cmd_ci(["generate", tmp_project])
        assert result == 0
        content = open(os.path.join(tmp_project, ".github", "workflows", "ci.yml")).read()
        assert "pytest" in content
        assert "python" in content.lower()

    def test_generate_python_pyproject(self, tmp_project, capsys):
        _make_python_project(tmp_project, use_pyproject=True)
        result = cmd_ci(["generate", tmp_project])
        assert result == 0
        content = open(os.path.join(tmp_project, ".github", "workflows", "ci.yml")).read()
        assert "pip install -e" in content


class TestCiGenerateGitlab:
    def test_generate_gitlab_node(self, tmp_project, capsys):
        _make_node_project(tmp_project, extras={"scripts": {"test": "jest"}})
        result = cmd_ci(["generate", tmp_project, "--platform", "gitlab"])
        assert result == 0
        ci_file = os.path.join(tmp_project, ".gitlab-ci.yml")
        assert os.path.exists(ci_file)
        content = open(ci_file).read()
        assert "stages:" in content
        assert "npm ci" in content

    def test_generate_gitlab_python(self, tmp_project, capsys):
        _make_python_project(tmp_project)
        result = cmd_ci(["generate", tmp_project, "--platform", "gitlab"])
        assert result == 0
        content = open(os.path.join(tmp_project, ".gitlab-ci.yml")).read()
        assert "pytest" in content


class TestCiEdgeCases:
    def test_unknown_project(self, tmp_project, capsys):
        result = cmd_ci(["generate", tmp_project])
        assert result == 1
        assert "Could not detect" in capsys.readouterr().out

    def test_unknown_subcommand(self, capsys):
        result = cmd_ci(["foobar"])
        assert result == 1

    def test_unsupported_platform(self, tmp_project, capsys):
        _make_node_project(tmp_project)
        result = cmd_ci(["generate", tmp_project, "--platform", "jenkins"])
        assert result == 1
        assert "Unsupported" in capsys.readouterr().out

    def test_docker_detection(self, tmp_project, capsys):
        _make_node_project(tmp_project, extras={"scripts": {"build": "next build"}})
        with open(os.path.join(tmp_project, "Dockerfile"), "w") as f:
            f.write("FROM node:20\n")
        cmd_ci(["generate", tmp_project])
        content = open(os.path.join(tmp_project, ".github", "workflows", "ci.yml")).read()
        assert "docker" in content.lower()
