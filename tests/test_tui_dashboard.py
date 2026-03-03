"""
Tests for TUI Dashboard Module
================================
Phase 3: Testing & Reliability — Dashboard unit tests.
"""

import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

import tui_dashboard


class TestGetProjects:
    """Tests for get_projects() function."""

    def test_returns_list(self, temp_mywork_root):
        with patch.object(tui_dashboard, "FRAMEWORK_ROOT", str(temp_mywork_root)):
            result = tui_dashboard.get_projects()
            assert isinstance(result, list)

    def test_finds_project_directories(self, temp_mywork_root):
        (temp_mywork_root / "projects" / "alpha").mkdir(parents=True)
        (temp_mywork_root / "projects" / "beta").mkdir(parents=True)
        with patch.object(tui_dashboard, "FRAMEWORK_ROOT", str(temp_mywork_root)):
            result = tui_dashboard.get_projects()
            names = [p["name"] for p in result]
            assert "alpha" in names
            assert "beta" in names

    def test_ignores_dotdirs(self, temp_mywork_root):
        (temp_mywork_root / "projects" / ".hidden").mkdir(parents=True)
        (temp_mywork_root / "projects" / "visible").mkdir(parents=True)
        with patch.object(tui_dashboard, "FRAMEWORK_ROOT", str(temp_mywork_root)):
            result = tui_dashboard.get_projects()
            names = [p["name"] for p in result]
            assert ".hidden" not in names
            assert "visible" in names

    def test_project_has_required_keys(self, temp_mywork_root):
        (temp_mywork_root / "projects" / "myproj").mkdir(parents=True)
        with patch.object(tui_dashboard, "FRAMEWORK_ROOT", str(temp_mywork_root)):
            result = tui_dashboard.get_projects()
            proj = [p for p in result if p["name"] == "myproj"][0]
            assert "name" in proj
            assert "path" in proj
            assert "type" in proj
            assert proj["type"] == "project"

    def test_empty_projects_dir(self, temp_mywork_root):
        with patch.object(tui_dashboard, "FRAMEWORK_ROOT", str(temp_mywork_root)):
            result = tui_dashboard.get_projects()
            # Should return empty or only current dir project
            project_types = [p["type"] for p in result]
            assert "project" not in project_types

    def test_detects_current_dir_with_main_py(self, temp_mywork_root, tmp_path):
        (tmp_path / "main.py").write_text("# main")
        with patch.object(tui_dashboard, "FRAMEWORK_ROOT", str(temp_mywork_root)):
            with patch("tui_dashboard.Path.cwd", return_value=tmp_path):
                result = tui_dashboard.get_projects()
                current = [p for p in result if p["type"] == "current"]
                assert len(current) == 1


class TestGetGitInfo:
    """Tests for get_git_info() function."""

    def test_returns_dict_with_expected_keys(self):
        result = tui_dashboard.get_git_info("/nonexistent")
        assert "branch" in result
        assert "changed" in result
        assert "commits" in result
        assert "last" in result

    def test_returns_fallback_on_error(self):
        result = tui_dashboard.get_git_info("/nonexistent/path/xyz")
        assert result["branch"] == "?"
        assert result["changed"] == 0
        assert result["commits"] == 0

    @patch("tui_dashboard.subprocess.run")
    def test_parses_git_output(self, mock_run):
        # Mock all 4 subprocess calls
        mock_run.side_effect = [
            MagicMock(stdout="main\n"),       # branch
            MagicMock(stdout="M file.py\n"),  # status
            MagicMock(stdout="42\n"),          # rev-list
            MagicMock(stdout="2 hours ago\n"),  # log
        ]
        result = tui_dashboard.get_git_info("/some/path")
        assert result["branch"] == "main"
        assert result["changed"] == 1
        assert result["commits"] == 42
        assert result["last"] == "2 hours ago"


class TestGetFrameworkStats:
    """Tests for get_framework_stats() function."""

    def test_returns_dict_with_required_keys(self, temp_mywork_root):
        with patch.object(tui_dashboard, "FRAMEWORK_ROOT", str(temp_mywork_root)):
            result = tui_dashboard.get_framework_stats()
            assert "version" in result
            assert "commands" in result
            assert "projects" in result

    def test_parses_version_from_pyproject(self, temp_mywork_root):
        pyproject = temp_mywork_root / "pyproject.toml"
        pyproject.write_text('[project]\nname = "mywork"\nversion = "1.2.3"\n')
        with patch.object(tui_dashboard, "FRAMEWORK_ROOT", str(temp_mywork_root)):
            result = tui_dashboard.get_framework_stats()
            assert result["version"] == "1.2.3"

    def test_counts_projects(self, temp_mywork_root):
        (temp_mywork_root / "projects" / "a").mkdir(parents=True)
        (temp_mywork_root / "projects" / "b").mkdir(parents=True)
        with patch.object(tui_dashboard, "FRAMEWORK_ROOT", str(temp_mywork_root)):
            result = tui_dashboard.get_framework_stats()
            assert result["projects"] == 2

    def test_handles_missing_pyproject(self, temp_mywork_root):
        with patch.object(tui_dashboard, "FRAMEWORK_ROOT", str(temp_mywork_root)):
            result = tui_dashboard.get_framework_stats()
            assert result["version"] == "?"


class TestGetMarketplaceStats:
    """Tests for get_marketplace_stats() function."""

    @patch("tui_dashboard.subprocess.run")
    def test_parses_product_list(self, mock_run):
        import json
        products = [
            {"name": "P1", "status": "active", "price": 29.99},
            {"name": "P2", "status": "active", "price": 49.99},
            {"name": "P3", "status": "draft", "price": 19.99},
        ]
        mock_run.return_value = MagicMock(stdout=json.dumps(products))
        result = tui_dashboard.get_marketplace_stats()
        assert result["products"] == 2
        assert result["total_value"] == "$79.98"

    @patch("tui_dashboard.subprocess.run")
    def test_handles_api_failure(self, mock_run):
        mock_run.side_effect = Exception("Connection refused")
        result = tui_dashboard.get_marketplace_stats()
        assert result["products"] == "?"
        assert result["total_value"] == "?"

    @patch("tui_dashboard.subprocess.run")
    def test_handles_empty_response(self, mock_run):
        mock_run.return_value = MagicMock(stdout="[]")
        result = tui_dashboard.get_marketplace_stats()
        assert result["products"] == 0
        assert result["total_value"] == "$0.00"


class TestBuildPanels:
    """Tests for build_* panel functions."""

    @patch("tui_dashboard.get_framework_stats")
    def test_build_header_returns_panel(self, mock_stats):
        mock_stats.return_value = {"version": "1.0.0", "commands": 10, "tests": 5, "projects": 3}
        from rich.panel import Panel
        result = tui_dashboard.build_header()
        assert isinstance(result, Panel)

    def test_build_quick_actions_returns_panel(self):
        from rich.panel import Panel
        result = tui_dashboard.build_quick_actions()
        assert isinstance(result, Panel)

    @patch("tui_dashboard.get_projects")
    @patch("tui_dashboard.get_git_info")
    def test_build_projects_panel_returns_panel(self, mock_git, mock_projects):
        from rich.panel import Panel
        mock_projects.return_value = [
            {"name": "test-proj", "path": "/tmp/test", "type": "project"}
        ]
        mock_git.return_value = {"branch": "main", "changed": 0, "commits": 10, "last": "now"}
        result = tui_dashboard.build_projects_panel()
        assert isinstance(result, Panel)

    @patch("tui_dashboard.get_projects")
    @patch("tui_dashboard.get_git_info")
    def test_build_projects_panel_empty(self, mock_git, mock_projects):
        from rich.panel import Panel
        mock_projects.return_value = []
        result = tui_dashboard.build_projects_panel()
        assert isinstance(result, Panel)

    @patch("tui_dashboard.get_marketplace_stats")
    def test_build_marketplace_panel_returns_panel(self, mock_stats):
        from rich.panel import Panel
        mock_stats.return_value = {"products": 5, "total_value": "$100.00"}
        result = tui_dashboard.build_marketplace_panel()
        assert isinstance(result, Panel)

    @patch("tui_dashboard.get_git_info")
    def test_build_system_panel_returns_panel(self, mock_git):
        from rich.panel import Panel
        mock_git.return_value = {"branch": "main", "changed": 0, "commits": 50, "last": "1h ago"}
        result = tui_dashboard.build_system_panel()
        assert isinstance(result, Panel)


class TestCmdTui:
    """Tests for cmd_tui() entry point."""

    def test_help_flag(self, capsys):
        result = tui_dashboard.cmd_tui(["-h"])
        assert result == 0

    def test_help_long_flag(self, capsys):
        result = tui_dashboard.cmd_tui(["--help"])
        assert result == 0
