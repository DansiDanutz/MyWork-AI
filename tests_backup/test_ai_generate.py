"""Tests for mw ai generate command."""
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

# Add tools to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

from ai_assistant import cmd_ai_generate


def test_generate_help():
    """Test --help returns 0."""
    result = cmd_ai_generate(["--help"])
    assert result == 0


def test_generate_missing_args():
    """Test missing args returns 1."""
    result = cmd_ai_generate(["onlyfile.py"])
    assert result == 1


def test_generate_dry_run(tmp_path, monkeypatch):
    """Test --dry-run doesn't write file."""
    monkeypatch.chdir(tmp_path)
    with patch("ai_assistant._call_llm", return_value="print('hello')"):
        result = cmd_ai_generate(["--dry-run", "test.py", "hello world script"])
    assert result == 0
    assert not (tmp_path / "test.py").exists()


def test_generate_writes_file(tmp_path, monkeypatch):
    """Test file is actually written."""
    monkeypatch.chdir(tmp_path)
    with patch("ai_assistant._call_llm", return_value="print('hello')"):
        result = cmd_ai_generate(["test.py", "hello world script"])
    assert result == 0
    assert (tmp_path / "test.py").exists()
    assert "hello" in (tmp_path / "test.py").read_text()


def test_generate_creates_subdirectories(tmp_path, monkeypatch):
    """Test parent directories are created."""
    monkeypatch.chdir(tmp_path)
    with patch("ai_assistant._call_llm", return_value="export const x = 1;"):
        result = cmd_ai_generate(["src/utils/helpers.ts", "utility helpers"])
    assert result == 0
    assert (tmp_path / "src" / "utils" / "helpers.ts").exists()


def test_generate_strips_markdown_fences(tmp_path, monkeypatch):
    """Test markdown fences are stripped."""
    monkeypatch.chdir(tmp_path)
    code_with_fences = "```python\nprint('hi')\n```"
    with patch("ai_assistant._call_llm", return_value=code_with_fences):
        result = cmd_ai_generate(["test.py", "hi script"])
    assert result == 0
    content = (tmp_path / "test.py").read_text()
    assert "```" not in content
    assert "print('hi')" in content


def test_generate_shell_executable(tmp_path, monkeypatch):
    """Test .sh files are made executable."""
    monkeypatch.chdir(tmp_path)
    with patch("ai_assistant._call_llm", return_value="#!/bin/bash\necho hi"):
        result = cmd_ai_generate(["test.sh", "echo script"])
    assert result == 0
    filepath = tmp_path / "test.sh"
    assert filepath.exists()
    assert os.access(filepath, os.X_OK)


def test_generate_model_flag(tmp_path, monkeypatch):
    """Test --model flag is parsed."""
    monkeypatch.chdir(tmp_path)
    with patch("ai_assistant._call_llm", return_value="x = 1") as mock:
        result = cmd_ai_generate(["--model", "claude", "t.py", "test"])
    assert result == 0
    # Check model was passed
    call_kwargs = mock.call_args
    assert "claude" in str(call_kwargs) or "anthropic" in str(call_kwargs)
