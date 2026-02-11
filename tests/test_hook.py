"""Tests for mw hook — git hooks management."""
import os
import sys
import stat
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
from mw import cmd_hook


@pytest.fixture
def git_repo(tmp_path):
    """Create a temporary git repository."""
    subprocess.run(["git", "init", str(tmp_path)], capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(old_cwd)


def test_hook_list_empty(git_repo, capsys):
    """List hooks in repo with no hooks installed."""
    result = cmd_hook(["list"])
    assert result == 0
    out = capsys.readouterr().out
    assert "0 hooks active" in out


def test_hook_install_all(git_repo, capsys):
    """Install all recommended hooks."""
    result = cmd_hook(["install"])
    assert result == 0
    out = capsys.readouterr().out
    assert "pre-commit" in out
    assert "commit-msg" in out
    assert "pre-push" in out
    assert "post-merge" in out
    # Verify files exist
    hooks_dir = git_repo / ".git" / "hooks"
    assert (hooks_dir / "pre-commit").exists()
    assert (hooks_dir / "commit-msg").exists()
    assert (hooks_dir / "pre-push").exists()
    assert (hooks_dir / "post-merge").exists()


def test_hook_install_single(git_repo, capsys):
    """Install a single hook."""
    result = cmd_hook(["install", "pre-commit"])
    assert result == 0
    hooks_dir = git_repo / ".git" / "hooks"
    assert (hooks_dir / "pre-commit").exists()
    assert not (hooks_dir / "commit-msg").exists()


def test_hook_install_backup(git_repo, capsys):
    """Installing over existing hook creates backup."""
    hooks_dir = git_repo / ".git" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    (hooks_dir / "pre-commit").write_text("#!/bin/bash\necho old")
    cmd_hook(["install", "pre-commit"])
    out = capsys.readouterr().out
    assert "Backed up" in out
    assert (hooks_dir / "pre-commit.backup").exists()
    assert "old" in (hooks_dir / "pre-commit.backup").read_text()


def test_hook_remove(git_repo, capsys):
    """Remove an installed hook."""
    cmd_hook(["install", "pre-commit"])
    capsys.readouterr()
    result = cmd_hook(["remove", "pre-commit"])
    assert result == 0
    hooks_dir = git_repo / ".git" / "hooks"
    assert not (hooks_dir / "pre-commit").exists()


def test_hook_remove_restores_backup(git_repo, capsys):
    """Removing hook restores backup if it exists."""
    hooks_dir = git_repo / ".git" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    (hooks_dir / "pre-commit").write_text("#!/bin/bash\necho old")
    cmd_hook(["install", "pre-commit"])
    capsys.readouterr()
    cmd_hook(["remove", "pre-commit"])
    out = capsys.readouterr().out
    assert "Restored" in out
    assert (hooks_dir / "pre-commit").exists()
    assert "old" in (hooks_dir / "pre-commit").read_text()


def test_hook_remove_missing(git_repo, capsys):
    """Remove a hook that doesn't exist."""
    result = cmd_hook(["remove", "pre-commit"])
    out = capsys.readouterr().out
    assert "not installed" in out


def test_hook_remove_no_args(git_repo, capsys):
    """Remove without args shows usage."""
    result = cmd_hook(["remove"])
    assert result == 1


def test_hook_create(git_repo, capsys):
    """Create a custom hook template."""
    result = cmd_hook(["create", "post-commit"])
    assert result == 0
    hooks_dir = git_repo / ".git" / "hooks"
    hook = hooks_dir / "post-commit"
    assert hook.exists()
    assert os.access(hook, os.X_OK)
    assert "MyWork-AI" in hook.read_text()


def test_hook_create_already_exists(git_repo, capsys):
    """Cannot create hook that already exists."""
    cmd_hook(["create", "post-commit"])
    capsys.readouterr()
    result = cmd_hook(["create", "post-commit"])
    assert result == 1
    out = capsys.readouterr().out
    assert "already exists" in out


def test_hook_create_invalid(git_repo, capsys):
    """Cannot create non-standard hook."""
    result = cmd_hook(["create", "not-a-hook"])
    assert result == 1
    out = capsys.readouterr().out
    assert "not a standard" in out


def test_hook_status_healthy(git_repo, capsys):
    """Status shows healthy when all recommended hooks installed."""
    cmd_hook(["install"])
    capsys.readouterr()
    result = cmd_hook(["status"])
    assert result == 0
    out = capsys.readouterr().out
    assert "4 hooks active" in out
    assert "healthy" in out


def test_hook_status_suggestions(git_repo, capsys):
    """Status shows suggestions when hooks missing."""
    result = cmd_hook(["status"])
    assert result == 0
    out = capsys.readouterr().out
    assert "suggestions" in out


def test_hook_run_missing(git_repo, capsys):
    """Run a hook that doesn't exist."""
    result = cmd_hook(["run", "pre-commit"])
    assert result == 1


def test_hook_run_no_args(git_repo, capsys):
    """Run without args shows usage."""
    result = cmd_hook(["run"])
    assert result == 1


def test_hook_unknown_subcommand(git_repo, capsys):
    """Unknown subcommand shows error."""
    result = cmd_hook(["foobar"])
    assert result == 1
    out = capsys.readouterr().out
    assert "Unknown" in out


def test_hook_executable_permission(git_repo):
    """Installed hooks are executable."""
    cmd_hook(["install", "pre-commit"])
    hook = git_repo / ".git" / "hooks" / "pre-commit"
    assert os.access(hook, os.X_OK)


def test_hook_contains_mywork_marker(git_repo):
    """Installed hooks contain MyWork-AI marker for identification."""
    cmd_hook(["install", "pre-commit"])
    hook = git_repo / ".git" / "hooks" / "pre-commit"
    assert "# MyWork-AI" in hook.read_text()


def test_hook_install_unknown_template(git_repo, capsys):
    """Installing hook with no template shows warning."""
    result = cmd_hook(["install", "post-commit"])
    out = capsys.readouterr().out
    assert "No template" in out
