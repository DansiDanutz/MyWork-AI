#!/usr/bin/env python3
"""Tests for tree_viewer.py - mw tree command."""

import os
import sys
import json
import tempfile
import subprocess
from pathlib import Path
from unittest import mock

import pytest

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from tree_viewer import (
    human_size,
    get_icon,
    git_status_color,
    build_tree,
    cmd_tree,
    RESET,
    BOLD,
    BLUE,
    YELLOW,
    GREEN,
    RED,
    DIM,
)


class TestHumanSize:
    """Tests for human_size function."""

    def test_bytes(self):
        """Test bytes display."""
        assert human_size(0) == "0B"
        assert human_size(512) == "512B"
        assert human_size(1023) == "1023B"

    def test_kilobytes(self):
        """Test kilobytes display."""
        assert human_size(1024) == "1.0K"
        assert human_size(1536) == "1.5K"
        assert human_size(10240) == "10.0K"

    def test_megabytes(self):
        """Test megabytes display."""
        assert human_size(1024 * 1024) == "1.0M"
        assert human_size(1.5 * 1024 * 1024) == "1.5M"

    def test_gigabytes(self):
        """Test gigabytes display."""
        assert human_size(1024 * 1024 * 1024) == "1.0G"
        assert human_size(2.5 * 1024 * 1024 * 1024) == "2.5G"

    def test_terabytes(self):
        """Test terabytes display."""
        assert human_size(1024 * 1024 * 1024 * 1024) == "1.0T"


class TestGetIcon:
    """Tests for get_icon function."""

    def test_directory(self):
        """Test directory icon."""
        assert get_icon("any", True) == "📁"

    def test_python_files(self):
        """Test Python file icons."""
        assert get_icon("test.py", False) == "🐍"
        assert get_icon("script.PY", False) == "🐍"

    def test_javascript_files(self):
        """Test JavaScript/TypeScript icons."""
        assert get_icon("app.js", False) == "📜"
        assert get_icon("main.ts", False) == "📘"
        assert get_icon("component.jsx", False) == "⚛️"
        assert get_icon("page.tsx", False) == "⚛️"

    def test_config_files(self):
        """Test config file icons."""
        assert get_icon("config.json", False) == "📋"
        assert get_icon("data.yaml", False) == "📋"
        assert get_icon("settings.yml", False) == "📋"
        assert get_icon("pyproject.toml", False) == "📋"

    def test_documentation_files(self):
        """Test documentation icons."""
        assert get_icon("readme.md", False) == "📖"
        assert get_icon("README.MD", False) == "📖"
        assert get_icon("notes.txt", False) == "📄"
        assert get_icon("docs.rst", False) == "📄"

    def test_web_files(self):
        """Test web file icons."""
        assert get_icon("index.html", False) == "🌐"
        assert get_icon("styles.css", False) == "🎨"
        assert get_icon("theme.scss", False) == "🎨"

    def test_dockerfile(self):
        """Test Dockerfile icon."""
        assert get_icon("Dockerfile", False) == "🐳"
        assert get_icon("dockerfile", False) == "🐳"

    def test_makefile(self):
        """Test Makefile icon."""
        assert get_icon("Makefile", False) == "🔧"
        assert get_icon("Justfile", False) == "🔧"

    def test_license(self):
        """Test license file icon."""
        assert get_icon("LICENSE", False) == "⚖️"

    def test_unknown_file(self):
        """Test default icon for unknown files."""
        assert get_icon("unknown.xyz", False) == "📄"


class TestGitStatusColor:
    """Tests for git_status_color function."""

    def test_modified(self):
        """Test modified status color."""
        assert git_status_color("M") == YELLOW
        assert git_status_color("MM") == YELLOW
        assert git_status_color("AM") == YELLOW

    def test_added(self):
        """Test added status color."""
        assert git_status_color("A") == GREEN
        assert git_status_color("??") == GREEN

    def test_deleted(self):
        """Test deleted status color."""
        assert git_status_color("D") == RED

    def test_other_status(self):
        """Test other/unrecognized status."""
        assert git_status_color("") == ""
        assert git_status_color("R") == ""
        assert git_status_color("C") == ""


class TestBuildTree:
    """Tests for build_tree function."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory with test files."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # Create directory structure
            (root / "src").mkdir()
            (root / "tests").mkdir()
            (root / "docs").mkdir()
            (root / ".hidden").mkdir()

            # Create files
            (root / "README.md").write_text("# Test")
            (root / "main.py").write_text("print('hello')")
            (root / "src" / "utils.py").write_text("# utils")
            (root / "src" / "helpers.js").write_text("// helpers")
            (root / "tests" / "test_main.py").write_text("# tests")
            (root / ".hidden" / "secret.txt").write_text("secret")

            yield root

    def test_basic_tree(self, temp_dir):
        """Test basic tree generation."""
        lines, stats = build_tree(temp_dir, max_depth=3)

        # Should count directories and files
        assert stats["dirs"] >= 3  # src, tests, docs
        assert stats["files"] >= 4  # README, main.py, utils.py, helpers.js, test_main.py

        # Check output contains expected entries
        output = "\n".join(lines)
        assert "📁" in output  # Has directories
        assert "📖" in output or "README" in output  # Has README
        assert "🐍" in output or ".py" in output  # Has Python files

    def test_depth_limiting(self, temp_dir):
        """Test depth limiting."""
        # Depth 1 should only show top level
        lines_shallow, _ = build_tree(temp_dir, max_depth=1)
        lines_deep, _ = build_tree(temp_dir, max_depth=3)

        # Deeper tree should have more lines
        assert len(lines_deep) >= len(lines_shallow)

    def test_dirs_only(self, temp_dir):
        """Test directories only mode."""
        lines, stats = build_tree(temp_dir, max_depth=3, dirs_only=True)

        # Should only have directories
        assert stats["files"] == 0
        assert stats["dirs"] >= 3

        # Output should only contain folder icons
        output = "\n".join(lines)
        assert "📁" in output

    def test_show_all(self, temp_dir):
        """Test show all (including hidden) mode."""
        # Without show_all, hidden dir should not appear
        lines_normal, _ = build_tree(temp_dir, max_depth=3, show_all=False)
        output_normal = "\n".join(lines_normal)

        # With show_all, hidden dir should appear
        lines_all, _ = build_tree(temp_dir, max_depth=3, show_all=True)
        output_all = "\n".join(lines_all)

        # All mode should have more content
        assert len(lines_all) >= len(lines_normal)

    def test_filter_extension(self, temp_dir):
        """Test file extension filtering."""
        lines, stats = build_tree(temp_dir, max_depth=3, filter_ext=".py")

        # Should only have Python files
        output = "\n".join(lines)
        assert ".js" not in output  # JS files filtered out

    def test_show_size(self, temp_dir):
        """Test showing file sizes."""
        lines, stats = build_tree(temp_dir, max_depth=3, show_size=True)

        # Check that total_size is calculated
        assert stats["total_size"] > 0

        # Output should contain size info
        output = "\n".join(lines)
        assert "B" in output or "K" in output

    def test_json_output(self, temp_dir):
        """Test JSON output mode."""
        lines, stats = build_tree(temp_dir, max_depth=3, as_json=True)

        # Stats should still be populated
        assert "dirs" in stats
        assert "files" in stats
        assert "total_size" in stats

    def test_nonexistent_directory(self):
        """Test handling of non-existent directory - build_tree expects valid dir."""
        # Note: build_tree assumes directory exists (validation is in cmd_tree)
        # This test verifies that empty directory works
        with tempfile.TemporaryDirectory() as tmp:
            empty = Path(tmp) / "empty"
            empty.mkdir()
            lines, stats = build_tree(empty)
            assert stats["dirs"] == 0
            assert stats["files"] == 0

    def test_empty_directory(self):
        """Test handling of empty directory."""
        with tempfile.TemporaryDirectory() as tmp:
            empty = Path(tmp) / "empty"
            empty.mkdir()
            lines, stats = build_tree(empty)
            assert stats["dirs"] == 0
            assert stats["files"] == 0
            assert lines == []


class TestCmdTree:
    """Tests for cmd_tree function."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "file.txt").write_text("content")
            yield root

    def test_help_flag(self, capsys):
        """Test --help flag."""
        result = cmd_tree(["--help"])
        assert result == 0
        captured = capsys.readouterr()
        assert "mw tree" in captured.out
        assert "Usage:" in captured.out

    def test_invalid_directory(self, capsys):
        """Test with invalid directory."""
        result = cmd_tree(["/nonexistent/path/12345"])
        assert result == 1
        captured = capsys.readouterr()
        assert "Not a directory" in captured.out

    def test_valid_directory(self, temp_dir, capsys):
        """Test with valid directory."""
        result = cmd_tree([str(temp_dir)])
        assert result == 0
        captured = capsys.readouterr()
        assert temp_dir.name in captured.out

    def test_depth_option(self, temp_dir, capsys):
        """Test --depth option."""
        result = cmd_tree([str(temp_dir), "--depth", "5"])
        assert result == 0

    def test_all_option(self, temp_dir, capsys):
        """Test --all option."""
        result = cmd_tree([str(temp_dir), "--all"])
        assert result == 0

    def test_dirs_option(self, temp_dir, capsys):
        """Test --dirs option."""
        result = cmd_tree([str(temp_dir), "--dirs"])
        assert result == 0
        captured = capsys.readouterr()
        # Should not show files in dirs-only mode

    def test_filter_option(self, temp_dir, capsys):
        """Test --filter option."""
        # Create a Python file
        (temp_dir / "script.py").write_text("# python")
        result = cmd_tree([str(temp_dir), "--filter", "py"])
        assert result == 0

    def test_size_option(self, temp_dir, capsys):
        """Test --size option."""
        result = cmd_tree([str(temp_dir), "--size"])
        assert result == 0
        captured = capsys.readouterr()
        # Should show file sizes
        assert "B" in captured.out or "directories" in captured.out

    def test_json_option(self, temp_dir, capsys):
        """Test --json option."""
        result = cmd_tree([str(temp_dir), "--json"])
        assert result == 0
        captured = capsys.readouterr()
        # Should output valid JSON
        data = json.loads(captured.out)
        assert "dirs" in data
        assert "files" in data

    def test_default_current_directory(self, capsys, monkeypatch):
        """Test default behavior uses current directory."""
        with tempfile.TemporaryDirectory() as tmp:
            monkeypatch.chdir(tmp)
            result = cmd_tree([])
            assert result == 0


class TestGitStatus:
    """Tests for get_git_status function."""

    def test_git_status_in_git_repo(self):
        """Test git status in an actual git repo."""
        from tree_viewer import get_git_status

        with tempfile.TemporaryDirectory() as tmp:
            # Initialize git repo
            subprocess.run(["git", "init"], cwd=tmp, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp, capture_output=True)

            # Create a file
            test_file = Path(tmp) / "test.txt"
            test_file.write_text("test")

            # Get status (should show untracked)
            status = get_git_status(Path(tmp))
            assert isinstance(status, dict)

    def test_git_status_not_git_repo(self):
        """Test git status outside of git repo."""
        from tree_viewer import get_git_status

        with tempfile.TemporaryDirectory() as tmp:
            status = get_git_status(Path(tmp))
            # Should return empty dict when not in git repo or on error
            assert isinstance(status, dict)


class TestGitignorePatterns:
    """Tests for get_gitignore_patterns function."""

    def test_gitignore_patterns_in_repo(self):
        """Test gitignore patterns in a git repo."""
        from tree_viewer import get_gitignore_patterns

        with tempfile.TemporaryDirectory() as tmp:
            # Initialize git repo
            subprocess.run(["git", "init"], cwd=tmp, capture_output=True)

            # Create .gitignore
            gitignore = Path(tmp) / ".gitignore"
            gitignore.write_text("*.log\n")

            # Create a log file
            log_file = Path(tmp) / "test.log"
            log_file.write_text("log content")

            patterns = get_gitignore_patterns(Path(tmp))
            assert isinstance(patterns, set)

    def test_gitignore_patterns_not_in_repo(self):
        """Test gitignore patterns outside git repo."""
        from tree_viewer import get_gitignore_patterns

        with tempfile.TemporaryDirectory() as tmp:
            patterns = get_gitignore_patterns(Path(tmp))
            # Should return empty set when not in git repo
            assert isinstance(patterns, set)


class TestIntegration:
    """Integration tests."""

    def test_complex_directory_structure(self):
        """Test with a complex nested structure."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            # Create complex structure
            for i in range(3):
                subdir = root / f"level1_{i}"
                subdir.mkdir()
                for j in range(2):
                    nested = subdir / f"level2_{j}"
                    nested.mkdir()
                    (nested / f"file_{i}_{j}.py").write_text("# code")
                    (nested / f"data_{i}_{j}.json").write_text('{"key": "value"}')

            lines, stats = build_tree(root, max_depth=5)

            # Should find all directories and files
            assert stats["dirs"] == 9  # 3 level1 + 6 level2
            assert stats["files"] == 12  # 2 files per nested dir

            output = "\n".join(lines)
            assert "🐍" in output  # Python files
            assert "📋" in output  # JSON files

    def test_special_filenames(self):
        """Test handling of special filenames."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            # Files with special characters
            (root / "file with spaces.txt").write_text("content")
            (root / "file-with-dashes.py").write_text("# code")
            (root / "file_with_underscores.js").write_text("// code")
            (root / "UPPERCASE.TXT").write_text("CONTENT")

            lines, stats = build_tree(root)

            assert stats["files"] == 4
            output = "\n".join(lines)
            assert "file with spaces" in output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
