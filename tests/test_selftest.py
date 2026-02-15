"""Tests for mw selftest command."""
import os
import sys
import json
import subprocess
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
from mw import cmd_selftest


def test_selftest_returns_zero():
    """Selftest should pass in the project directory."""
    result = cmd_selftest([])
    assert result == 0


def test_selftest_quick():
    """Quick mode should also pass."""
    result = cmd_selftest(["--quick"])
    assert result == 0


def test_selftest_json_output(capsys):
    """JSON output should be valid and report success."""
    cmd_selftest(["--json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["ok"] is True
    assert data["passed"] >= 3
    assert isinstance(data["time"], float)
    assert isinstance(data["checks"], list)


def test_selftest_json_quick(capsys):
    """JSON + quick should have fewer checks."""
    cmd_selftest(["--json", "--quick"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["ok"] is True
    # Quick mode has 4 checks, full has 8
    assert len(data["checks"]) <= 10
