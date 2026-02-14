"""Tests for mw snapshot command."""
import json
import os
import sys
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.mw import cmd_snapshot


def test_snapshot_capture(tmp_path):
    """Test basic snapshot capture."""
    # Create a minimal project
    (tmp_path / "main.py").write_text("print('hello')\nprint('world')\n")
    (tmp_path / "test_main.py").write_text("def test_hello(): pass\n")
    (tmp_path / "package.json").write_text('{"dependencies": {"react": "^18"}}')

    os.chdir(tmp_path)
    result = cmd_snapshot([str(tmp_path)])
    assert result == 0

    snap_dir = tmp_path / ".mw" / "snapshots"
    assert snap_dir.exists()
    snaps = list(snap_dir.glob("*.json"))
    assert len(snaps) == 1

    data = json.loads(snaps[0].read_text())
    assert data["lines_of_code"] >= 2
    assert data["file_count"] >= 1
    assert data["test_count"] >= 1
    assert data["dependency_count"] >= 1
    assert "project" in data
    assert "timestamp" in data


def test_snapshot_history_empty(tmp_path):
    """Test history with no snapshots."""
    os.chdir(tmp_path)
    result = cmd_snapshot(["history", str(tmp_path)])
    assert result == 1


def test_snapshot_compare_insufficient(tmp_path):
    """Test compare with less than 2 snapshots."""
    os.chdir(tmp_path)
    result = cmd_snapshot(["compare", str(tmp_path)])
    assert result == 1


def test_snapshot_help():
    """Test snapshot help."""
    result = cmd_snapshot(["--help"])
    assert result == 0


def test_snapshot_history_with_data(tmp_path):
    """Test history after capturing snapshots."""
    (tmp_path / "app.py").write_text("x = 1\n")
    os.chdir(tmp_path)

    cmd_snapshot([str(tmp_path)])
    # Capture a second one
    (tmp_path / "app2.py").write_text("y = 2\n")
    cmd_snapshot([str(tmp_path)])

    result = cmd_snapshot(["history", str(tmp_path)])
    assert result == 0


def test_snapshot_compare_with_data(tmp_path):
    """Test compare with 2 snapshots."""
    (tmp_path / "app.py").write_text("x = 1\n")
    os.chdir(tmp_path)
    cmd_snapshot([str(tmp_path)])

    (tmp_path / "app2.py").write_text("y = 2\nz = 3\n")
    cmd_snapshot([str(tmp_path)])

    result = cmd_snapshot(["compare", str(tmp_path)])
    assert result == 0
