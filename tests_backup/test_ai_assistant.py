"""Tests for mw ai — AI Assistant commands."""

import json
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from tools.ai_assistant import (
    cmd_ai, cmd_ai_ask, cmd_ai_explain, cmd_ai_fix,
    cmd_ai_refactor, cmd_ai_test, cmd_ai_commit,
    _get_provider_key, _read_file, _get_git_diff,
)


class TestCmdAi:
    """Test main cmd_ai dispatcher."""

    def test_no_args_shows_help(self, capsys):
        result = cmd_ai([])
        assert result == 0
        out = capsys.readouterr().out
        assert "AI Assistant" in out
        assert "mw ai ask" in out

    def test_unknown_subcommand_treated_as_question(self):
        """Unknown subcommands are treated as questions (convenience shortcut)."""
        with patch("tools.ai_assistant._call_llm", return_value="mocked answer"):
            result = cmd_ai(["nonexistent"])
            assert result == 0

    def test_dispatches_ask(self):
        with patch("tools.ai_assistant.cmd_ai_ask", return_value=0) as m:
            cmd_ai(["ask", "hello"])
            m.assert_called_once_with(["hello"])

    def test_dispatches_explain(self):
        with patch("tools.ai_assistant.cmd_ai_explain", return_value=0) as m:
            cmd_ai(["explain", "file.py"])
            m.assert_called_once_with(["file.py"])

    def test_dispatches_fix(self):
        with patch("tools.ai_assistant.cmd_ai_fix", return_value=0) as m:
            cmd_ai(["fix", "file.py"])
            m.assert_called_once_with(["file.py"])

    def test_dispatches_refactor(self):
        with patch("tools.ai_assistant.cmd_ai_refactor", return_value=0) as m:
            cmd_ai(["refactor", "file.py"])
            m.assert_called_once_with(["file.py"])

    def test_dispatches_test(self):
        with patch("tools.ai_assistant.cmd_ai_test", return_value=0) as m:
            cmd_ai(["test", "file.py"])
            m.assert_called_once_with(["file.py"])

    def test_dispatches_commit(self):
        with patch("tools.ai_assistant.cmd_ai_commit", return_value=0) as m:
            cmd_ai(["commit"])
            m.assert_called_once_with([])


class TestGetApiKey:
    """Test API key retrieval."""

    def test_from_env(self):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
            assert _get_provider_key("openrouter") == "test-key"

    def test_from_config(self, tmp_path):
        config = tmp_path / ".mywork" / "config.json"
        config.parent.mkdir(parents=True)
        config.write_text(json.dumps({"openrouter_api_key": "cfg-key"}))
        with patch.dict(os.environ, {}, clear=True):
            with patch("tools.ai_assistant._load_env"):
                with patch("tools.ai_assistant.Path.home", return_value=tmp_path):
                    assert _get_provider_key("openrouter") == "cfg-key"

    def test_no_key_returns_none(self, tmp_path):
        with patch.dict(os.environ, {}, clear=True):
            with patch("tools.ai_assistant._load_env"):
                with patch("tools.ai_assistant.Path.home", return_value=tmp_path):
                    assert _get_provider_key("openrouter") is None


class TestReadFile:
    """Test file reading."""

    def test_reads_file(self, tmp_path):
        f = tmp_path / "test.py"
        f.write_text("print('hello')")
        content = _read_file(str(f))
        assert content == "print('hello')"

    def test_missing_file(self, capsys):
        result = _read_file("/nonexistent/file.py")
        assert result is None
        assert "not found" in capsys.readouterr().out


class TestAskCommand:
    """Test mw ai ask."""

    def test_no_args(self, capsys):
        result = cmd_ai_ask([])
        assert result == 1
        assert "Usage" in capsys.readouterr().out

    @patch("tools.ai_assistant._call_llm", return_value="The answer is 42")
    def test_ask_question(self, mock_llm, capsys):
        result = cmd_ai_ask(["How", "do", "I", "test?"])
        assert result == 0
        assert "42" in capsys.readouterr().out
        mock_llm.assert_called_once()
        assert "How do I test?" in mock_llm.call_args[0][0]


class TestExplainCommand:
    """Test mw ai explain."""

    def test_no_args(self, capsys):
        result = cmd_ai_explain([])
        assert result == 1

    @patch("tools.ai_assistant._call_llm", return_value="This code prints hello")
    def test_explain_file(self, mock_llm, tmp_path, capsys):
        f = tmp_path / "test.py"
        f.write_text("print('hello')")
        result = cmd_ai_explain([str(f)])
        assert result == 0
        assert "prints hello" in capsys.readouterr().out

    @patch("tools.ai_assistant._call_llm", return_value="Lines explained")
    def test_explain_with_lines(self, mock_llm, tmp_path, capsys):
        f = tmp_path / "test.py"
        f.write_text("line1\nline2\nline3\nline4\nline5")
        result = cmd_ai_explain([str(f), "--lines", "2-4"])
        assert result == 0
        # Check it only sent lines 2-4
        prompt = mock_llm.call_args[0][0]
        assert "line2" in prompt
        assert "line4" in prompt


class TestFixCommand:
    """Test mw ai fix."""

    def test_no_args(self, capsys):
        result = cmd_ai_fix([])
        assert result == 1

    @patch("tools.ai_assistant._call_llm", return_value="Fixed the bug")
    def test_fix_file(self, mock_llm, tmp_path, capsys):
        f = tmp_path / "buggy.py"
        f.write_text("def broken():\n  return 1/0")
        result = cmd_ai_fix([str(f)])
        assert result == 0
        assert "Fixed" in capsys.readouterr().out

    @patch("tools.ai_assistant._call_llm", return_value="Fixed error")
    def test_fix_with_error(self, mock_llm, tmp_path, capsys):
        f = tmp_path / "buggy.py"
        f.write_text("x = 1/0")
        result = cmd_ai_fix([str(f), "--error", "ZeroDivisionError"])
        assert result == 0
        prompt = mock_llm.call_args[0][0]
        assert "ZeroDivisionError" in prompt

    @patch("tools.ai_assistant._get_git_diff", return_value="+ new line")
    @patch("tools.ai_assistant._call_llm", return_value="Diff looks good")
    def test_fix_diff(self, mock_llm, mock_diff, capsys):
        result = cmd_ai_fix(["--diff"])
        assert result == 0
        assert "good" in capsys.readouterr().out


class TestCommitCommand:
    """Test mw ai commit."""

    @patch("tools.ai_assistant._get_git_diff", return_value="(no changes)")
    def test_no_changes(self, mock_diff, capsys):
        result = cmd_ai_commit([])
        assert result == 1
        assert "No changes" in capsys.readouterr().out

    @patch("tools.ai_assistant._get_git_diff", return_value="+ added stuff")
    @patch("tools.ai_assistant._call_llm", return_value="feat: add stuff")
    def test_generates_message(self, mock_llm, mock_diff, capsys):
        result = cmd_ai_commit([])
        assert result == 0
        out = capsys.readouterr().out
        assert "feat: add stuff" in out


class TestReviewCommand:
    """Test mw ai review."""

    @patch("tools.ai_assistant._get_git_diff", return_value="")
    def test_no_changes(self, mock_diff, capsys):
        from tools.ai_assistant import cmd_ai_review
        result = cmd_ai_review([])
        assert result == 0
        assert "No changes" in capsys.readouterr().out

    @patch("tools.ai_assistant._get_git_diff", return_value="+ added line\n- removed line")
    @patch("tools.ai_assistant._call_llm", return_value="🟢 Good: clean changes")
    def test_review_diff(self, mock_llm, mock_diff, capsys):
        from tools.ai_assistant import cmd_ai_review
        result = cmd_ai_review([])
        assert result == 0
        out = capsys.readouterr().out
        assert "Good" in out

    @patch("tools.ai_assistant._get_git_diff", return_value="big diff " * 2000)
    @patch("tools.ai_assistant._call_llm", return_value="truncated review")
    def test_truncates_large_diff(self, mock_llm, mock_diff, capsys):
        from tools.ai_assistant import cmd_ai_review
        result = cmd_ai_review([])
        assert result == 0
        prompt = mock_llm.call_args[0][0]
        assert "truncated" in prompt


class TestDocCommand:
    """Test mw ai doc."""

    def test_no_args(self, capsys):
        from tools.ai_assistant import cmd_ai_doc
        result = cmd_ai_doc([])
        assert result == 1
        assert "Usage" in capsys.readouterr().out

    @patch("tools.ai_assistant._call_llm", return_value='def foo():\n    """Documented."""')
    def test_doc_file(self, mock_llm, tmp_path, capsys):
        from tools.ai_assistant import cmd_ai_doc
        f = tmp_path / "code.py"
        f.write_text("def foo(): pass")
        result = cmd_ai_doc([str(f)])
        assert result == 0
        assert "Generating docs" in capsys.readouterr().out


class TestChangelogCommand:
    """Test mw ai changelog."""

    @patch("subprocess.run")
    def test_no_commits(self, mock_run, capsys):
        from tools.ai_assistant import cmd_ai_changelog
        mock_run.return_value = type("R", (), {"stdout": ""})()
        result = cmd_ai_changelog([])
        assert result == 0
        assert "No commits" in capsys.readouterr().out

    @patch("tools.ai_assistant._call_llm", return_value="### Added\n- Feature X")
    @patch("subprocess.run")
    def test_generates_changelog(self, mock_run, mock_llm, capsys):
        from tools.ai_assistant import cmd_ai_changelog
        mock_run.return_value = type("R", (), {"stdout": "abc123 feat: add X\ndef456 fix: bug Y"})()
        result = cmd_ai_changelog([])
        assert result == 0
        assert "Added" in capsys.readouterr().out
