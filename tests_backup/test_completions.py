"""Tests for mw completions command."""
import subprocess
import sys
from pathlib import Path

MW_PATH = str(Path(__file__).parent.parent / "tools" / "mw.py")


def run_mw(*args):
    return subprocess.run(
        [sys.executable, MW_PATH] + list(args),
        capture_output=True, text=True, timeout=10
    )


class TestCompletions:
    def test_help(self):
        r = run_mw("completions", "--help")
        assert r.returncode == 0
        assert "Shell Completions" in r.stdout

    def test_bash(self):
        r = run_mw("completions", "bash")
        assert r.returncode == 0
        assert "_mw_completions" in r.stdout
        assert "complete -F _mw_completions mw" in r.stdout
        assert "brain" in r.stdout

    def test_zsh(self):
        r = run_mw("completions", "zsh")
        assert r.returncode == 0
        assert "#compdef mw" in r.stdout
        assert "_mw" in r.stdout

    def test_fish(self):
        r = run_mw("completions", "fish")
        assert r.returncode == 0
        assert "complete -c mw" in r.stdout
        assert "__fish_use_subcommand" in r.stdout

    def test_unknown_shell(self):
        r = run_mw("completions", "powershell")
        assert r.returncode == 1
        assert "Unknown shell" in r.stdout

    def test_no_args(self):
        r = run_mw("completions")
        assert r.returncode == 0
        assert "Shell Completions" in r.stdout

    def test_bash_has_subcommands(self):
        r = run_mw("completions", "bash")
        assert r.returncode == 0
        # Check that subcommands are present for key commands
        assert "brain)" in r.stdout
        assert "git)" in r.stdout
        assert "ai)" in r.stdout
        assert "deploy)" in r.stdout

    def test_fish_has_subcommands(self):
        r = run_mw("completions", "fish")
        assert r.returncode == 0
        assert "__fish_seen_subcommand_from brain" in r.stdout
        assert "__fish_seen_subcommand_from git" in r.stdout
