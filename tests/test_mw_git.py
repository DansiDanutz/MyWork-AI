"""Tests for mw git command."""
import subprocess
import tempfile
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))


@pytest.fixture
def git_repo(tmp_path):
    """Create a temporary git repo for testing."""
    orig = os.getcwd()
    os.chdir(tmp_path)
    subprocess.run(["git", "init"], capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], capture_output=True)
    # Initial commit
    (tmp_path / "README.md").write_text("# Test")
    subprocess.run(["git", "add", "."], capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], capture_output=True)
    yield tmp_path
    os.chdir(orig)


class TestGitStatus:
    def test_status_clean(self, git_repo, capsys):
        from mw import cmd_git
        rc = cmd_git(["status"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "Working tree clean" in out

    def test_status_with_changes(self, git_repo, capsys):
        (git_repo / "new.txt").write_text("hello")
        from mw import cmd_git
        rc = cmd_git(["status"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "Untracked: 1" in out


class TestGitCommit:
    def test_commit_with_message(self, git_repo, capsys):
        (git_repo / "file.txt").write_text("data")
        subprocess.run(["git", "add", "."], capture_output=True)
        from mw import cmd_git
        rc = cmd_git(["commit", "test commit"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "Committed" in out

    def test_commit_auto_message(self, git_repo, capsys):
        (git_repo / "feature.py").write_text("print('hi')")
        subprocess.run(["git", "add", "."], capture_output=True)
        from mw import cmd_git
        rc = cmd_git(["commit"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "Committed" in out

    def test_commit_nothing(self, git_repo, capsys):
        from mw import cmd_git
        rc = cmd_git(["commit"])
        assert rc == 1


class TestGitLog:
    def test_log_default(self, git_repo):
        from mw import cmd_git
        rc = cmd_git(["log"])
        assert rc == 0

    def test_log_limit(self, git_repo):
        from mw import cmd_git
        rc = cmd_git(["log", "5"])
        assert rc == 0


class TestGitBranch:
    def test_list_branches(self, git_repo, capsys):
        from mw import cmd_git
        rc = cmd_git(["branch"])
        assert rc == 0

    def test_create_branch(self, git_repo, capsys):
        from mw import cmd_git
        rc = cmd_git(["branch", "feature-test"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "feature-test" in out


class TestGitDiff:
    def test_diff_no_changes(self, git_repo, capsys):
        from mw import cmd_git
        rc = cmd_git(["diff"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "No changes" in out

    def test_diff_with_changes(self, git_repo, capsys):
        (git_repo / "README.md").write_text("# Updated")
        from mw import cmd_git
        rc = cmd_git(["diff"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "Diff Summary" in out


class TestGitStash:
    def test_stash_and_pop(self, git_repo, capsys):
        (git_repo / "README.md").write_text("# Changed")
        from mw import cmd_git
        rc = cmd_git(["stash"])
        assert rc == 0
        rc = cmd_git(["stash", "pop"])
        assert rc == 0


class TestGitUndo:
    def test_undo_last_commit(self, git_repo, capsys):
        (git_repo / "x.txt").write_text("x")
        subprocess.run(["git", "add", "."], capture_output=True)
        subprocess.run(["git", "commit", "-m", "temp"], capture_output=True)
        from mw import cmd_git
        rc = cmd_git(["undo"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "undone" in out


class TestGitAmend:
    def test_amend_no_edit(self, git_repo, capsys):
        from mw import cmd_git
        rc = cmd_git(["amend"])
        assert rc == 0

    def test_amend_with_message(self, git_repo, capsys):
        from mw import cmd_git
        rc = cmd_git(["amend", "better message"])
        assert rc == 0


class TestGitCleanup:
    def test_cleanup_no_merged(self, git_repo, capsys):
        from mw import cmd_git
        rc = cmd_git(["cleanup"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "Cleaned up" in out


class TestGitPassthrough:
    def test_passthrough_version(self, git_repo):
        from mw import cmd_git
        rc = cmd_git(["--version"])
        assert rc == 0


class TestNotGitRepo:
    def test_not_git_repo(self, tmp_path, capsys):
        orig = os.getcwd()
        os.chdir(tmp_path)
        from mw import cmd_git
        rc = cmd_git(["status"])
        assert rc == 1
        out = capsys.readouterr().out
        assert "Not inside a git" in out
        os.chdir(orig)
