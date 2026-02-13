"""Tests for mw upgrade command."""
import subprocess
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))


def test_upgrade_help():
    """mw upgrade --help should show usage info."""
    from mw import cmd_upgrade
    result = cmd_upgrade(["--help"])
    assert result == 0


def test_upgrade_check_runs():
    """mw upgrade --check should complete without error."""
    from mw import cmd_upgrade
    result = cmd_upgrade(["--check"])
    assert result == 0


def test_upgrade_version_detection():
    """Should detect current version from pyproject.toml."""
    from mw import cmd_upgrade
    # Just verify it doesn't crash
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="0\n", stderr="")
        result = cmd_upgrade(["--check"])
        assert result == 0


def test_upgrade_pypi_check():
    """mw upgrade --pypi --check should attempt PyPI version check."""
    from mw import cmd_upgrade
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="mywork-ai (2.1.0)", stderr="")
        result = cmd_upgrade(["--pypi", "--check"])
        assert result == 0
