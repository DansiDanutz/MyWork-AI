"""Tests for mw pair — pair programming command."""
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from tools.pair_session import (
    detect_project_type,
    scan_files,
    get_file_context,
    show_history,
    cmd_pair,
    WATCH_EXTENSIONS,
    IGNORE_PATTERNS,
    PAIR_DIR,
)


class TestDetectProjectType:
    def test_node_project(self, tmp_path):
        (tmp_path / "package.json").write_text('{"dependencies": {"react": "^18"}}')
        info = detect_project_type(str(tmp_path))
        assert info["language"] == "javascript/typescript"
        assert info["framework"] == "React"
        assert info["type"] == "node"

    def test_nextjs_project(self, tmp_path):
        (tmp_path / "package.json").write_text('{"dependencies": {"next": "^14"}}')
        info = detect_project_type(str(tmp_path))
        assert info["framework"] == "Next.js"

    def test_nestjs_project(self, tmp_path):
        (tmp_path / "package.json").write_text('{"dependencies": {"@nestjs/core": "^10"}}')
        info = detect_project_type(str(tmp_path))
        assert info["framework"] == "NestJS"

    def test_python_fastapi(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\ndependencies = ["fastapi"]')
        info = detect_project_type(str(tmp_path))
        assert info["language"] == "python"
        assert info["framework"] == "FastAPI"

    def test_python_django(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\ndependencies = ["django"]')
        info = detect_project_type(str(tmp_path))
        assert info["framework"] == "Django"

    def test_rust_project(self, tmp_path):
        (tmp_path / "Cargo.toml").write_text('[package]\nname = "x"')
        info = detect_project_type(str(tmp_path))
        assert info["language"] == "rust"

    def test_go_project(self, tmp_path):
        (tmp_path / "go.mod").write_text('module example.com/x')
        info = detect_project_type(str(tmp_path))
        assert info["language"] == "go"

    def test_unknown_project(self, tmp_path):
        info = detect_project_type(str(tmp_path))
        assert info["type"] == "unknown"


class TestScanFiles:
    def test_finds_python_files(self, tmp_path):
        (tmp_path / "main.py").write_text("print('hi')")
        (tmp_path / "readme.txt").write_text("text")
        files = scan_files(str(tmp_path))
        assert any("main.py" in f for f in files)
        assert not any("readme.txt" in f for f in files)

    def test_ignores_node_modules(self, tmp_path):
        nm = tmp_path / "node_modules" / "pkg"
        nm.mkdir(parents=True)
        (nm / "index.js").write_text("module.exports = {}")
        (tmp_path / "app.js").write_text("const x = 1;")
        files = scan_files(str(tmp_path))
        # No file inside node_modules/ subdirectory should be found
        assert not any(os.sep + "node_modules" + os.sep in f for f in files)
        assert any("app.js" in f for f in files)

    def test_ignores_pycache(self, tmp_path):
        pc = tmp_path / "__pycache__"
        pc.mkdir()
        (pc / "mod.cpython-312.pyc").write_text("")
        files = scan_files(str(tmp_path))
        assert len(files) == 0

    def test_watches_multiple_extensions(self, tmp_path):
        for ext in [".py", ".js", ".ts", ".rs", ".go"]:
            (tmp_path / f"file{ext}").write_text("code")
        files = scan_files(str(tmp_path))
        assert len(files) == 5


class TestGetFileContext:
    def test_reads_file(self, tmp_path):
        f = tmp_path / "test.py"
        f.write_text("x = 1\ny = 2\n")
        ctx = get_file_context(str(f))
        assert "x = 1" in ctx

    def test_truncates_large_files(self, tmp_path):
        f = tmp_path / "big.py"
        f.write_text("\n".join([f"line_{i}" for i in range(500)]))
        ctx = get_file_context(str(f))
        assert "more lines" in ctx

    def test_missing_file(self):
        ctx = get_file_context("/nonexistent/path.py")
        assert ctx == ""


class TestCmdPair:
    def test_help(self, capsys):
        result = cmd_pair(["--help"])
        assert result == 0

    def test_history_empty(self, capsys):
        result = cmd_pair(["history"])
        # Should return 0 regardless of whether sessions exist
        assert result == 0

    def test_invalid_path(self, capsys):
        result = cmd_pair(["--path", "/nonexistent/dir/xyz123"])
        captured = capsys.readouterr()
        assert result == 1
        assert "not found" in captured.out.lower()

    def test_no_provider(self, capsys):
        with patch.dict(os.environ, {}, clear=True):
            with patch("tools.pair_session.get_ai_provider", return_value=None):
                result = cmd_pair(["/tmp"])
                captured = capsys.readouterr()
                assert result == 1
                assert "No AI provider" in captured.out


class TestWatchExtensions:
    def test_common_extensions_included(self):
        for ext in [".py", ".js", ".ts", ".tsx", ".rs", ".go", ".java"]:
            assert ext in WATCH_EXTENSIONS

    def test_config_extensions_included(self):
        for ext in [".yaml", ".yml", ".toml", ".json"]:
            assert ext in WATCH_EXTENSIONS


class TestIgnorePatterns:
    def test_common_ignores(self):
        for pattern in ["node_modules", "__pycache__", ".git", "dist", "build"]:
            assert pattern in IGNORE_PATTERNS
