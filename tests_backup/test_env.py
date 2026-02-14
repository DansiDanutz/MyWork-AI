"""Tests for mw env command."""
import os
import sys
import pytest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
from mw import cmd_env


@pytest.fixture
def env_dir(tmp_path, monkeypatch):
    """Create a temp dir with .env and .env.example."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


def _write(path, content):
    path.write_text(content)


class TestEnvStatus:
    def test_status_no_env(self, env_dir, capsys):
        result = cmd_env([])
        assert result == 0
        out = capsys.readouterr().out
        assert "Not found" in out

    def test_status_with_env(self, env_dir, capsys):
        _write(env_dir / ".env", "KEY=value\nSECRET=abc123\n")
        result = cmd_env([])
        assert result == 0
        out = capsys.readouterr().out
        assert "2" in out  # 2 variables


class TestEnvList:
    def test_list_masked(self, env_dir, capsys):
        _write(env_dir / ".env", "API_KEY=sk-abc123def456\n")
        result = cmd_env(["list"])
        assert result == 0
        out = capsys.readouterr().out
        assert "API_KEY" in out
        assert "sk-abc123def456" not in out  # masked

    def test_list_show(self, env_dir, capsys):
        _write(env_dir / ".env", "API_KEY=sk-abc123def456\n")
        result = cmd_env(["list", "--show"])
        assert result == 0
        out = capsys.readouterr().out
        assert "sk-abc123def456" in out

    def test_list_no_file(self, env_dir, capsys):
        result = cmd_env(["list"])
        assert result == 1


class TestEnvGet:
    def test_get_existing(self, env_dir, capsys):
        _write(env_dir / ".env", "MY_VAR=hello\n")
        result = cmd_env(["get", "MY_VAR"])
        assert result == 0
        assert "hello" in capsys.readouterr().out

    def test_get_missing(self, env_dir, capsys):
        _write(env_dir / ".env", "MY_VAR=hello\n")
        result = cmd_env(["get", "NOPE"])
        assert result == 1

    def test_get_no_key(self, env_dir, capsys):
        result = cmd_env(["get"])
        assert result == 1


class TestEnvSet:
    def test_set_new(self, env_dir, capsys):
        _write(env_dir / ".env", "EXISTING=val\n")
        result = cmd_env(["set", "NEW_KEY=new_val"])
        assert result == 0
        content = (env_dir / ".env").read_text()
        assert "NEW_KEY=new_val" in content
        assert "EXISTING=val" in content

    def test_set_update(self, env_dir, capsys):
        _write(env_dir / ".env", "KEY=old\n")
        result = cmd_env(["set", "KEY=new"])
        assert result == 0
        content = (env_dir / ".env").read_text()
        assert "KEY=new" in content
        assert "KEY=old" not in content

    def test_set_two_args(self, env_dir, capsys):
        _write(env_dir / ".env", "")
        result = cmd_env(["set", "KEY", "VALUE"])
        assert result == 0
        assert "KEY=VALUE" in (env_dir / ".env").read_text()


class TestEnvRm:
    def test_rm_existing(self, env_dir, capsys):
        _write(env_dir / ".env", "A=1\nB=2\n")
        result = cmd_env(["rm", "A"])
        assert result == 0
        content = (env_dir / ".env").read_text()
        assert "A=" not in content
        assert "B=2" in content

    def test_rm_missing(self, env_dir, capsys):
        _write(env_dir / ".env", "A=1\n")
        result = cmd_env(["rm", "NOPE"])
        assert result == 1


class TestEnvDiff:
    def test_diff_all_present(self, env_dir, capsys):
        _write(env_dir / ".env.example", "A=\nB=\n")
        _write(env_dir / ".env", "A=val1\nB=val2\n")
        result = cmd_env(["diff"])
        assert result == 0
        out = capsys.readouterr().out
        assert "✅" in out

    def test_diff_missing(self, env_dir, capsys):
        _write(env_dir / ".env.example", "A=\nB=\nC=\n")
        _write(env_dir / ".env", "A=val1\n")
        result = cmd_env(["diff"])
        assert result == 0
        out = capsys.readouterr().out
        assert "missing" in out

    def test_diff_no_example(self, env_dir, capsys):
        result = cmd_env(["diff"])
        assert result == 1


class TestEnvValidate:
    def test_validate_all_set(self, env_dir, capsys):
        _write(env_dir / ".env.example", "A=\nB=\n")
        _write(env_dir / ".env", "A=1\nB=2\n")
        result = cmd_env(["validate"])
        assert result == 0

    def test_validate_missing(self, env_dir, capsys):
        _write(env_dir / ".env.example", "A=\nB=\nC=\n")
        _write(env_dir / ".env", "A=1\n")
        result = cmd_env(["validate"])
        assert result == 1


class TestEnvExport:
    def test_export_shell(self, env_dir, capsys):
        _write(env_dir / ".env", "KEY=val\n")
        result = cmd_env(["export"])
        assert result == 0
        assert 'export KEY="val"' in capsys.readouterr().out

    def test_export_docker(self, env_dir, capsys):
        _write(env_dir / ".env", "KEY=val\n")
        result = cmd_env(["export", "--format=docker"])
        assert result == 0
        assert "-e KEY=val" in capsys.readouterr().out

    def test_export_json(self, env_dir, capsys):
        _write(env_dir / ".env", "KEY=val\n")
        result = cmd_env(["export", "--format=json"])
        assert result == 0
        out = capsys.readouterr().out
        assert '"KEY"' in out


class TestEnvInit:
    def test_init_creates(self, env_dir, capsys):
        _write(env_dir / ".env.example", "A=default\nB=\n")
        result = cmd_env(["init"])
        assert result == 0
        assert (env_dir / ".env").exists()

    def test_init_exists(self, env_dir, capsys):
        _write(env_dir / ".env", "A=1\n")
        _write(env_dir / ".env.example", "A=\n")
        result = cmd_env(["init"])
        assert result == 0  # warns but doesn't overwrite
        assert (env_dir / ".env").read_text() == "A=1\n"
