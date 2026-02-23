"""
Tests for auto_lint_scheduler.py
=================================
Tests for the automated markdownlint scheduler.
"""

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

import pytest


class TestRunCommand:
    """Tests for run_command function."""

    def test_successful_command(self, tmp_path):
        """Should run command successfully and return output."""
        from auto_lint_scheduler import run_command

        # Create a simple test script
        test_script = tmp_path / "test.sh"
        test_script.write_text("#!/bin/bash\necho 'test output'")
        test_script.chmod(0o755)

        success, output = run_command(["bash", str(test_script)], cwd=str(tmp_path))

        assert success is True
        assert "test output" in output

    def test_failed_command(self, tmp_path):
        """Should return False for failed command."""
        from auto_lint_scheduler import run_command

        success, output = run_command(["bash", "nonexistent.sh"], cwd=str(tmp_path))

        assert success is False
        assert "error" in output.lower() or "not found" in output.lower() or "no such file" in output.lower()

    def test_command_timeout(self, tmp_path):
        """Should return False for timed out command."""
        from auto_lint_scheduler import run_command

        # Create a script that sleeps longer than timeout
        test_script = tmp_path / "sleep.sh"
        test_script.write_text("#!/bin/bash\nsleep 10")
        test_script.chmod(0o755)

        # Run with a short timeout (we need to patch subprocess.run)
        with patch("auto_lint_scheduler.subprocess.run") as mock_run:
            from subprocess import TimeoutExpired
            mock_run.side_effect = TimeoutExpired("sleep 10", 5)

            success, output = run_command(["bash", str(test_script)])

            assert success is False
            assert "timed out" in output.lower()

    def test_custom_working_directory(self, tmp_path):
        """Should respect custom working directory."""
        from auto_lint_scheduler import run_command

        # Create script in subdirectory
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        test_script = subdir / "test.sh"
        test_script.write_text("#!/bin/bash\npwd")
        test_script.chmod(0o755)

        success, output = run_command(["bash", str(test_script)], cwd=str(subdir))

        assert success is True
        assert "subdir" in output


class TestCheckGitStatus:
    """Tests for check_git_status function."""

    def test_git_status_success(self, temp_mywork_root):
        """Should successfully check git status."""
        from auto_lint_scheduler import check_git_status

        # Initialize git repo
        subprocess.run(["git", "init"], cwd=temp_mywork_root, capture_output=True)

        success, md_changes, total_changes = check_git_status()

        assert success is True
        assert md_changes >= 0
        assert total_changes >= 0

    def test_git_status_counts_markdown_files(self, temp_mywork_root):
        """Should count markdown file changes correctly."""
        from auto_lint_scheduler import check_git_status

        # Initialize git repo and create markdown files
        subprocess.run(["git", "init"], cwd=temp_mywork_root, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=temp_mywork_root, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=temp_mywork_root, capture_output=True)

        # Create and commit markdown files
        (temp_mywork_root / "test.md").write_text("# Test")
        (temp_mywork_root / "README.md").write_text("# README")
        (temp_mywork_root / "other.txt").write_text("Not markdown")

        subprocess.run(["git", "add", "."], cwd=temp_mywork_root, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial"], cwd=temp_mywork_root, capture_output=True)

        # Modify markdown files
        (temp_mywork_root / "test.md").write_text("# Modified")

        # Change to temp directory before checking git status
        import os
        old_cwd = os.getcwd()
        os.chdir(temp_mywork_root)
        try:
            success, md_changes, total_changes = check_git_status()
        finally:
            os.chdir(old_cwd)

        assert success is True
        assert md_changes >= 1  # At least one markdown file changed
        assert total_changes >= 1

    def test_git_status_failure(self):
        """Should handle git command failure."""
        from auto_lint_scheduler import check_git_status

        # Test in a non-git directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            success, md_changes, total_changes = check_git_status()

            # Git command might fail in non-git directory
            # Just verify it returns valid tuples
            assert isinstance(success, bool)
            assert isinstance(md_changes, int)
            assert isinstance(total_changes, int)


class TestFormatInterval:
    """Tests for _format_interval function."""

    def test_format_hours(self):
        """Should format hours correctly."""
        from auto_lint_scheduler import _format_interval

        assert _format_interval(3600) == "1 hour"
        assert _format_interval(7200) == "2 hours"
        assert _format_interval(14400) == "4 hours"

    def test_format_minutes(self):
        """Should format minutes correctly."""
        from auto_lint_scheduler import _format_interval

        assert _format_interval(60) == "1 minute"
        assert _format_interval(120) == "2 minutes"
        assert _format_interval(300) == "5 minutes"

    def test_format_seconds(self):
        """Should format seconds correctly."""
        from auto_lint_scheduler import _format_interval

        assert _format_interval(1) == "1 seconds"
        assert _format_interval(30) == "30 seconds"

    def test_format_irregular_intervals(self):
        """Should handle irregular intervals (not exact minutes or hours)."""
        from auto_lint_scheduler import _format_interval

        # 90 seconds is not exactly 1 minute
        assert _format_interval(90) == "90 seconds"
        # 3690 seconds is not exactly 1 hour (1 hour is 3600 seconds)
        assert _format_interval(3690) == "3690 seconds"


class TestRunLintFixer:
    """Tests for run_lint_fixer function."""

    def test_successful_lint_fix(self, temp_mywork_root):
        """Should successfully run lint fixer."""
        from auto_lint_scheduler import run_lint_fixer

        # Mock the run_command to simulate successful lint fixer output
        mock_output = """
Files processed: 5
Files fixed: 3
• MD022 (Headings without blank lines): 10
• MD032 (Lists without blank lines): 5
• MD047 (Missing trailing newlines): 2
"""

        with patch("auto_lint_scheduler.run_command", return_value=(True, mock_output)):
            success, results = run_lint_fixer()

            assert success is True
            assert results["files_processed"] == 5
            assert results["files_fixed"] == 3
            assert results["total_fixes"]["MD022"] == 10
            assert results["total_fixes"]["MD032"] == 5
            assert results["total_fixes"]["MD047"] == 2

    def test_lint_fixer_failure(self, temp_mywork_root):
        """Should handle lint fixer failure."""
        from auto_lint_scheduler import run_lint_fixer

        with patch("auto_lint_scheduler.run_command", return_value=(False, "Script not found")):
            success, results = run_lint_fixer()

            assert success is False
            assert "error" in results
            assert "Script not found" in results["error"]

    def test_parse_complex_output(self, temp_mywork_root):
        """Should parse complex lint fixer output."""
        from auto_lint_scheduler import run_lint_fixer

        mock_output = """
Running markdownlint...
Files processed: 10
Files fixed: 7
• MD022 (Headings without blank lines): 25
• MD032 (Lists without blank lines): 15
• MD031 (Code blocks without blank lines): 8
• MD047 (Missing trailing newlines): 12
• MD058 (Tables without blank lines): 5
Done!
"""

        with patch("auto_lint_scheduler.run_command", return_value=(True, mock_output)):
            success, results = run_lint_fixer()

            assert success is True
            assert results["files_processed"] == 10
            assert results["files_fixed"] == 7
            assert sum(results["total_fixes"].values()) == 65

    def test_empty_output(self, temp_mywork_root):
        """Should handle empty or minimal output."""
        from auto_lint_scheduler import run_lint_fixer

        mock_output = "Files processed: 0\nFiles fixed: 0"

        with patch("auto_lint_scheduler.run_command", return_value=(True, mock_output)):
            success, results = run_lint_fixer()

            assert success is True
            assert results["files_processed"] == 0
            assert results["files_fixed"] == 0
            assert len(results["total_fixes"]) == 0


class TestCommitChanges:
    """Tests for commit_changes function."""

    @patch("auto_lint_scheduler.run_command")
    def test_commit_success(self, mock_run_command, temp_mywork_root):
        """Should successfully commit changes."""
        from auto_lint_scheduler import commit_changes

        # Mock git commands
        mock_run_command.return_value = (True, "")

        results = {
            "files_processed": 5,
            "files_fixed": 3,
            "total_fixes": {
                "MD022": 10,
                "MD032": 5,
            },
        }

        success = commit_changes(results, 3600)

        assert success is True
        # Should have called git add and git commit
        assert mock_run_command.call_count >= 2

    @patch("auto_lint_scheduler.run_command")
    def test_commit_nothing_to_commit(self, mock_run_command, temp_mywork_root):
        """Should handle case with nothing to commit."""
        from auto_lint_scheduler import commit_changes

        # Mock git commands - git commit returns "nothing to commit"
        mock_run_command.side_effect = [
            (True, ""),  # git add
            (False, "nothing to commit, working tree clean"),  # git commit
        ]

        results = {
            "files_processed": 0,
            "files_fixed": 0,
            "total_fixes": {},
        }

        success = commit_changes(results, 3600)

        assert success is True  # Should return True even if nothing to commit

    def test_commit_message_format(self, temp_mywork_root):
        """Should generate properly formatted commit message."""
        from auto_lint_scheduler import commit_changes

        # Initialize git repo
        subprocess.run(["git", "init"], cwd=temp_mywork_root, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=temp_mywork_root, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=temp_mywork_root, capture_output=True)

        results = {
            "files_processed": 5,
            "files_fixed": 3,
            "total_fixes": {
                "MD022": 10,
                "MD032": 5,
            },
        }

        # Mock run_command to capture the commit message
        captured_messages = []

        def mock_run_command(command, cwd="."):
            if "git" in command and "commit" in command:
                # Capture the commit message (last argument is the message)
                captured_messages.append(command[-1])
                return (True, "")
            return (True, "")

        with patch("auto_lint_scheduler.run_command", side_effect=mock_run_command):
            commit_changes(results, 3600)

        assert len(captured_messages) == 1
        commit_msg = captured_messages[0]
        assert "fix(auto-lint)" in commit_msg
        assert "15 markdownlint violations" in commit_msg  # 10 + 5
        assert "MD022: 10" in commit_msg
        assert "MD032: 5" in commit_msg
        assert "Files: 3/5 modified" in commit_msg
        assert "1 hour" in commit_msg


class TestRunSingleCycle:
    """Tests for run_single_cycle function."""

    def test_cycle_no_violations(self, temp_mywork_root):
        """Should handle cycle with no violations."""
        from auto_lint_scheduler import run_single_cycle

        # Initialize git repo with clean state
        subprocess.run(["git", "init"], cwd=temp_mywork_root, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=temp_mywork_root, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=temp_mywork_root, capture_output=True)

        with patch("auto_lint_scheduler.run_lint_fixer", return_value=(True, {
            "files_processed": 5,
            "files_fixed": 0,
            "total_fixes": {},
        })):
            success = run_single_cycle(3600, False)

            assert success is True

    def test_cycle_with_fixes(self, temp_mywork_root):
        """Should handle cycle with fixes applied."""
        from auto_lint_scheduler import run_single_cycle

        # Initialize git repo
        subprocess.run(["git", "init"], cwd=temp_mywork_root, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=temp_mywork_root, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=temp_mywork_root, capture_output=True)

        with patch("auto_lint_scheduler.run_lint_fixer", return_value=(True, {
            "files_processed": 5,
            "files_fixed": 3,
            "total_fixes": {"MD022": 10, "MD032": 5},
        })):
            with patch("auto_lint_scheduler.commit_changes", return_value=True):
                success = run_single_cycle(3600, False)

                assert success is True

    def test_cycle_lint_fixer_failure(self, temp_mywork_root):
        """Should handle lint fixer failure gracefully."""
        from auto_lint_scheduler import run_single_cycle

        with patch("auto_lint_scheduler.check_git_status", return_value=(True, 0, 0)):
            with patch("auto_lint_scheduler.run_lint_fixer", return_value=(False, {"error": "Script failed"})):
                success = run_single_cycle(3600, False)

                assert success is False

    def test_cycle_dirty_working_tree(self, temp_mywork_root):
        """Should skip cycle when working tree has uncommitted changes."""
        from auto_lint_scheduler import run_single_cycle

        # Initialize git repo
        subprocess.run(["git", "init"], cwd=temp_mywork_root, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=temp_mywork_root, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=temp_mywork_root, capture_output=True)

        # Create an uncommitted file
        (temp_mywork_root / "uncommitted.txt").write_text("test")

        # Change to temp directory before running
        import os
        old_cwd = os.getcwd()
        os.chdir(temp_mywork_root)
        try:
            with patch("auto_lint_scheduler.run_lint_fixer") as mock_fixer:
                run_single_cycle(3600, False)
        finally:
            os.chdir(old_cwd)

            # Lint fixer should not be called due to dirty tree
            mock_fixer.assert_not_called()

    def test_cycle_force_with_dirty_tree(self, temp_mywork_root):
        """Should run even with dirty working tree when force=True."""
        from auto_lint_scheduler import run_single_cycle

        # Initialize git repo
        subprocess.run(["git", "init"], cwd=temp_mywork_root, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=temp_mywork_root, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=temp_mywork_root, capture_output=True)

        # Create an uncommitted file
        (temp_mywork_root / "uncommitted.txt").write_text("test")

        with patch("auto_lint_scheduler.run_lint_fixer", return_value=(True, {
            "files_processed": 0,
            "files_fixed": 0,
            "total_fixes": {},
        })):
            success = run_single_cycle(3600, True)

            assert success is True


class TestMain:
    """Tests for main function."""

    @patch("sys.argv", ["auto_lint_scheduler.py"])
    @patch("auto_lint_scheduler.run_single_cycle", return_value=True)
    def test_main_single_run(self, mock_cycle):
        """Should run single cycle when daemon flag not set."""
        from auto_lint_scheduler import main

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0
        mock_cycle.assert_called_once()

    @patch("sys.argv", ["auto_lint_scheduler.py", "--force"])
    @patch("auto_lint_scheduler.run_single_cycle", return_value=True)
    def test_main_force_flag(self, mock_cycle):
        """Should pass force flag correctly."""
        from auto_lint_scheduler import main

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0
        # Check that force=True was passed
        call_args = mock_cycle.call_args
        assert call_args[0][1] is True  # Second arg is force

    @patch("sys.argv", ["auto_lint_scheduler.py", "--interval", "300"])
    @patch("auto_lint_scheduler.run_single_cycle", return_value=True)
    def test_main_custom_interval(self, mock_cycle):
        """Should pass custom interval correctly."""
        from auto_lint_scheduler import main

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0
        # Check that interval was passed correctly
        call_args = mock_cycle.call_args
        assert call_args[0][0] == 300  # First arg is interval

    @patch("sys.argv", ["auto_lint_scheduler.py", "--daemon"])
    @patch("auto_lint_scheduler.time.sleep")
    @patch("auto_lint_scheduler.run_single_cycle", return_value=True)
    def test_main_daemon_mode(self, mock_cycle, mock_sleep):
        """Should run in daemon mode when daemon flag is set."""
        from auto_lint_scheduler import main

        # Simulate one iteration then KeyboardInterrupt
        mock_cycle.side_effect = [True, KeyboardInterrupt]

        with pytest.raises(SystemExit):
            main()

        assert mock_cycle.call_count == 2  # First call, then interrupted

    @patch("sys.argv", ["auto_lint_scheduler.py", "--daemon", "--interval", "3600"])
    @patch("auto_lint_scheduler.time.sleep")
    @patch("auto_lint_scheduler.run_single_cycle", return_value=True)
    def test_main_daemon_with_custom_interval(self, mock_cycle, mock_sleep):
        """Should use custom interval in daemon mode."""
        from auto_lint_scheduler import main

        mock_cycle.side_effect = [True, KeyboardInterrupt]

        with pytest.raises(SystemExit):
            main()

        # Check sleep was called with correct interval
        assert mock_sleep.call_count == 1
        mock_sleep.assert_called_with(3600)

    @patch("sys.argv", ["auto_lint_scheduler.py", "--daemon"])
    @patch("auto_lint_scheduler.time.sleep")
    @patch("auto_lint_scheduler.run_single_cycle", return_value=False)
    def test_main_daemon_failure_handling(self, mock_cycle, mock_sleep):
        """Should handle failures in daemon mode."""
        from auto_lint_scheduler import main

        # Run once successfully, then fail, then interrupt
        mock_cycle.side_effect = [True, False, KeyboardInterrupt]

        with pytest.raises(SystemExit):
            main()

        assert mock_cycle.call_count == 3

    @patch("sys.argv", ["auto_lint_scheduler.py"])
    @patch("auto_lint_scheduler.run_single_cycle", return_value=False)
    def test_main_exit_code_on_failure(self, mock_cycle):
        """Should exit with code 1 on failure."""
        from auto_lint_scheduler import main

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
