"""Tests for mw audit command."""
import os
import sys
import json
import tempfile
import subprocess
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from mw import cmd_audit


@pytest.fixture
def sample_project(tmp_path):
    """Create a sample project for auditing."""
    # Source files
    (tmp_path / "main.py").write_text("print('hello')\n" * 10)
    (tmp_path / "utils.py").write_text("def helper(): pass\n" * 5)
    # Tests
    test_dir = tmp_path / "tests"
    test_dir.mkdir()
    (test_dir / "test_main.py").write_text("def test_hello(): assert True\n")
    # Docs
    (tmp_path / "README.md").write_text("# My Project\n")
    (tmp_path / "LICENSE").write_text("MIT\n")
    (tmp_path / "CHANGELOG.md").write_text("# Changes\n")
    # Deps
    (tmp_path / "requirements.txt").write_text("flask==2.0.0\nrequests==2.28.0\n")
    # Git
    (tmp_path / ".gitignore").write_text("__pycache__/\n")
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init", "--allow-empty"], cwd=tmp_path,
                   capture_output=True, env={**os.environ, "GIT_AUTHOR_NAME": "test",
                   "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "test",
                   "GIT_COMMITTER_EMAIL": "t@t"})
    return tmp_path


def test_audit_help(capsys):
    """Test --help flag."""
    result = cmd_audit(["--help"])
    assert result == 0
    out = capsys.readouterr().out
    assert "audit" in out.lower() or "Audit" in out or "AUDIT" in out


def test_audit_sample_project(capsys, sample_project):
    """Test audit on a well-structured project."""
    result = cmd_audit([str(sample_project)])
    assert result == 0
    out = capsys.readouterr().out
    assert "Code Health" in out
    assert "Tests" in out
    assert "Documentation" in out
    assert "Overall Grade" in out


def test_audit_json_output(capsys, sample_project):
    """Test JSON output mode."""
    result = cmd_audit([str(sample_project), "--json"])
    assert result == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "grade" in data
    assert "categories" in data
    assert "findings" in data
    assert data["score"] > 0


def test_audit_quick_mode(capsys, sample_project):
    """Test quick mode skips slow checks."""
    result = cmd_audit([str(sample_project), "--quick"])
    assert result == 0
    out = capsys.readouterr().out
    assert "Overall Grade" in out


def test_audit_empty_dir(capsys, tmp_path):
    """Test audit on empty directory."""
    result = cmd_audit([str(tmp_path)])
    assert result == 0
    out = capsys.readouterr().out
    assert "No source code" in out or "Overall Grade" in out


def test_audit_nonexistent_dir(capsys):
    """Test audit on non-existent path."""
    result = cmd_audit(["/tmp/does_not_exist_audit_test"])
    assert result == 1


def test_audit_security_env_file(capsys, sample_project):
    """Test that .env file is flagged."""
    (sample_project / ".env").write_text("SECRET=abc123\n")
    result = cmd_audit([str(sample_project), "--json"])
    assert result == 0
    data = json.loads(capsys.readouterr().out)
    assert any(".env" in f for f in data["findings"])


def test_audit_no_readme(capsys, tmp_path):
    """Test missing README is flagged."""
    (tmp_path / "app.py").write_text("x = 1\n")
    result = cmd_audit([str(tmp_path), "--json"])
    assert result == 0
    data = json.loads(capsys.readouterr().out)
    assert any("README" in f for f in data["findings"])


def test_audit_secret_detection(capsys, tmp_path):
    """Test secret pattern detection in non-quick mode."""
    (tmp_path / "config.py").write_text('api_key = "sk-abcdefghijklmnopqrstuvwxyz1234567890ABCD"\n')
    (tmp_path / "README.md").write_text("# test\n")
    result = cmd_audit([str(tmp_path), "--json"])
    assert result == 0
    data = json.loads(capsys.readouterr().out)
    # Should detect sk- pattern
    assert data["categories"]["Security"]["secrets_found"] >= 1


def test_audit_grade_is_letter(capsys, sample_project):
    """Test grade is a valid letter."""
    result = cmd_audit([str(sample_project), "--json"])
    assert result == 0
    data = json.loads(capsys.readouterr().out)
    assert data["grade"] in ["A", "B", "C", "D", "F"]
