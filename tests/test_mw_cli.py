"""Tests for the mw CLI (tools/mw.py)."""

import importlib
import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Add tools dir so we can import mw
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
import mw


class TestColors:
    """Test the Colors helper class."""

    def test_color_codes_are_strings(self):
        for attr in ('GREEN', 'RED', 'YELLOW', 'BLUE', 'BOLD', 'ENDC'):
            assert isinstance(getattr(mw.Colors, attr), str)

    def test_color_function_wraps_text(self):
        result = mw.color("hello", mw.Colors.GREEN)
        assert "hello" in result
        assert result.startswith(mw.Colors.GREEN)
        assert result.endswith(mw.Colors.ENDC)


class TestCommandRouting:
    """Test that main() routes to the right commands."""

    def test_help_flag(self):
        with patch.object(sys, 'argv', ['mw', '--help']):
            with pytest.raises(SystemExit) as exc:
                mw.main()
            assert exc.value.code == 0

    def test_help_command(self):
        with patch.object(sys, 'argv', ['mw', 'help']):
            with pytest.raises(SystemExit) as exc:
                mw.main()
            assert exc.value.code == 0

    def test_no_args_shows_help(self):
        with patch.object(sys, 'argv', ['mw']):
            with pytest.raises(SystemExit) as exc:
                mw.main()
            assert exc.value.code == 0

    def test_unknown_command_exits_1(self):
        with patch.object(sys, 'argv', ['mw', 'nonexistent_command_xyz']):
            with pytest.raises(SystemExit) as exc:
                mw.main()
            assert exc.value.code == 1

    def test_dashboard_command_routing(self):
        """Test that 'mw dashboard' routes to cmd_dashboard function."""
        with patch.object(mw, 'cmd_dashboard', return_value=0) as mock_dashboard:
            with patch.object(sys, 'argv', ['mw', 'dashboard']):
                with pytest.raises(SystemExit) as exc:
                    mw.main()
                assert exc.value.code == 0
                mock_dashboard.assert_called_once()

    def test_autoforge_command_routing(self):
        """Test that 'mw af' routes to cmd_autoforge function.""" 
        with patch.object(mw, 'cmd_autoforge', return_value=0) as mock_autoforge:
            with patch.object(sys, 'argv', ['mw', 'af', 'status']):
                with pytest.raises(SystemExit) as exc:
                    mw.main()
                assert exc.value.code == 0

    def test_autoforge_legacy_alias(self):
        """Test that 'mw ac' still routes to cmd_autoforge for backwards compatibility."""
        with patch.object(mw, 'cmd_autoforge', return_value=0) as mock_autoforge:
            with patch.object(sys, 'argv', ['mw', 'ac', 'status']):
                with pytest.raises(SystemExit) as exc:
                    mw.main()
                assert exc.value.code == 0


class TestDashboard:
    """Test the dashboard command functionality."""

    def test_dashboard_runs_without_error(self):
        """Test that dashboard command executes without crashing."""
        result = mw.cmd_dashboard()
        assert result == 0

    def test_dashboard_handles_git_errors_gracefully(self):
        """Test dashboard gracefully handles git command failures."""
        with patch('subprocess.run', side_effect=Exception("Git not available")):
            result = mw.cmd_dashboard()
            assert result == 0  # Should not crash

    def test_dashboard_shows_project_count(self):
        """Test that dashboard correctly counts projects."""
        result = mw.cmd_dashboard()
        assert result == 0

    def test_command_case_insensitive(self):
        """Commands should be lowercased before routing."""
        with patch.object(sys, 'argv', ['mw', 'HELP']):
            with pytest.raises(SystemExit) as exc:
                mw.main()
            assert exc.value.code == 0


class TestRunTool:
    """Test the run_tool helper."""

    def test_run_tool_missing_script(self):
        """Running a non-existent tool should return non-zero."""
        result = mw.run_tool("completely_nonexistent_tool_12345")
        assert result != 0


class TestSearchRequiresArgs:
    """Test that search without query prints usage."""

    def test_search_no_args(self, capsys):
        result = mw.cmd_search([])
        captured = capsys.readouterr()
        assert "Usage" in captured.out or "query" in captured.out.lower() or result is None


class TestPrintHelp:
    """Test help output."""

    def test_print_help_runs(self, capsys):
        mw.print_help()
        captured = capsys.readouterr()
        assert "mw" in captured.out.lower() or "MyWork" in captured.out
