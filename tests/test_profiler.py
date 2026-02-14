"""Tests for mw profile — Command Profiler."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from tools.profiler import profile_command, format_stats


class TestProfileCommand:
    def test_echo(self):
        stats = profile_command("echo test")
        assert stats["exit_code"] == 0
        assert stats["wall_time_s"] < 5
        assert stats["max_rss_mb"] >= 0
        assert stats["stdout_lines"] == 1

    def test_failing_command(self):
        stats = profile_command("false")
        assert stats["exit_code"] != 0

    def test_verbose(self):
        stats = profile_command("echo hello", verbose=True)
        assert "stdout" in stats
        assert "hello" in stats["stdout"]


class TestFormatStats:
    def test_success(self):
        stats = profile_command("echo ok")
        output = format_stats(stats)
        assert "✅" in output
        assert "Wall time" in output

    def test_error(self):
        output = format_stats({"error": "boom"})
        assert "❌" in output
        assert "boom" in output
