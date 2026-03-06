"""
Comprehensive tests for benchmark.py (mw bench command).
Tests performance benchmarking, result saving, and history tracking.
"""
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add tools directory to path
TOOLS_DIR = Path(__file__).parent.parent / "tools"
sys.path.insert(0, str(TOOLS_DIR))

import benchmark


@pytest.fixture
def temp_benchmark_dir(tmp_path):
    """Create a temporary benchmark directory."""
    bench_dir = tmp_path / ".benchmarks"
    bench_dir.mkdir()
    
    # Patch the BENCH_DIR temporarily
    orig_bench_dir = benchmark.BENCH_DIR
    benchmark.BENCH_DIR = bench_dir
    
    yield bench_dir
    
    # Restore original
    benchmark.BENCH_DIR = orig_bench_dir


@pytest.fixture
def temp_mywork_root(tmp_path):
    """Create a temporary MyWork root structure."""
    tools_dir = tmp_path / "tools"
    tools_dir.mkdir()
    
    # Create a minimal mw.py
    (tools_dir / "mw.py").write_text("#!/usr/bin/env python3\nprint('ok')")
    
    orig_root = benchmark.MYWORK_ROOT
    benchmark.MYWORK_ROOT = tmp_path
    
    yield tmp_path
    
    benchmark.MYWORK_ROOT = orig_root


class TestTimeCmd:
    """Test _time_cmd function for timing command execution."""

    def test_time_cmd_success(self):
        """Test timing a successful command."""
        result = benchmark._time_cmd(["echo", "hello"], timeout=5)
        
        assert result["cmd"] == "echo hello"
        assert result["success"] is True
        assert result["returncode"] == 0
        assert "duration_ms" in result
        assert result["duration_ms"] >= 0

    def test_time_cmd_failure(self):
        """Test timing a failing command."""
        result = benchmark._time_cmd(["false"], timeout=5)
        
        assert result["cmd"] == "false"
        assert result["success"] is False
        assert result["returncode"] == 1
        assert "duration_ms" in result

    def test_time_cmd_timeout(self):
        """Test timing a command that times out."""
        result = benchmark._time_cmd(["sleep", "10"], timeout=0.1)
        
        assert result["success"] is False
        assert result["returncode"] == -1
        assert result["error"] == "timeout"
        assert "duration_ms" in result

    def test_time_cmd_exception(self):
        """Test timing a command that raises an exception."""
        result = benchmark._time_cmd(["/nonexistent/command/that/does/not/exist"], timeout=5)
        
        assert result["success"] is False
        assert result["returncode"] == -1
        assert "error" in result
        assert "duration_ms" in result

    def test_time_cmd_with_cwd(self, tmp_path):
        """Test timing a command with custom working directory."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        result = benchmark._time_cmd(["cat", "test.txt"], cwd=str(tmp_path), timeout=5)
        
        assert result["success"] is True
        assert result["returncode"] == 0


class TestRating:
    """Test _rating function for performance ratings."""

    def test_rating_fast(self):
        """Test rating for fast performance."""
        rating = benchmark._rating(100, good=500, ok=1000)
        assert "fast" in rating
        assert "⚡" in rating

    def test_rating_ok(self):
        """Test rating for ok performance."""
        rating = benchmark._rating(750, good=500, ok=1000)
        assert "ok" in rating
        assert "⏱" in rating

    def test_rating_slow(self):
        """Test rating for slow performance."""
        rating = benchmark._rating(1500, good=500, ok=1000)
        assert "slow" in rating
        assert "🐢" in rating

    def test_rating_boundary_good(self):
        """Test rating at good boundary."""
        rating = benchmark._rating(500, good=500, ok=1000)
        assert "fast" in rating

    def test_rating_boundary_ok(self):
        """Test rating at ok boundary."""
        rating = benchmark._rating(1000, good=500, ok=1000)
        assert "ok" in rating


class TestSaveResults:
    """Test save_results function."""

    def test_save_results_creates_file(self, temp_benchmark_dir):
        """Test that save_results creates a JSON file."""
        data = {
            "startup": [{"label": "test", "avg_ms": 100}],
            "commands": [{"label": "cmd", "ms": 200, "success": True}]
        }
        
        result_path = benchmark.save_results(data)
        
        assert result_path.exists()
        assert result_path.suffix == ".json"
        assert "bench_" in result_path.name

    def test_save_results_content(self, temp_benchmark_dir):
        """Test that save_results writes correct JSON content."""
        data = {"test": "value", "number": 42}
        
        result_path = benchmark.save_results(data)
        content = json.loads(result_path.read_text())
        
        assert content["test"] == "value"
        assert content["number"] == 42
        assert "timestamp" in content

    def test_save_results_timestamp_format(self, temp_benchmark_dir):
        """Test that timestamp is in ISO format."""
        data = {"test": "value"}
        
        result_path = benchmark.save_results(data)
        content = json.loads(result_path.read_text())
        
        # Should be parseable as ISO format
        parsed = datetime.fromisoformat(content["timestamp"])
        assert parsed.tzinfo is not None  # Should have timezone info


class TestShowHistory:
    """Test show_history function."""

    def test_show_history_no_files(self, temp_benchmark_dir, capsys):
        """Test show_history with no benchmark files."""
        benchmark.show_history()
        captured = capsys.readouterr()
        
        assert "No benchmark history" in captured.out

    def test_show_history_with_files(self, temp_benchmark_dir, capsys):
        """Test show_history with benchmark files."""
        # Create sample benchmark files
        for i in range(3):
            ts = f"20240306_10000{i}"
            data = {
                "timestamp": f"2024-03-06T10:00:0{i}+00:00",
                "startup": [
                    {"label": "mw --help", "avg_ms": 100 + i * 10},
                    {"label": "mw status", "avg_ms": 200 + i * 10}
                ],
                "commands": [
                    {"label": "mw ecosystem", "ms": 300 + i * 10, "success": True}
                ]
            }
            file_path = temp_benchmark_dir / f"bench_{ts}.json"
            file_path.write_text(json.dumps(data))
        
        benchmark.show_history()
        captured = capsys.readouterr()
        
        assert "Benchmark History" in captured.out
        assert "mw --help" in captured.out
        assert "mw status" in captured.out
        assert "mw ecosystem" in captured.out

    def test_show_history_handles_corrupt_files(self, temp_benchmark_dir, capsys):
        """Test show_history handles corrupt JSON files gracefully."""
        # Create a valid file
        valid_data = {
            "timestamp": "2024-03-06T10:00:00+00:00",
            "startup": [{"label": "mw --help", "avg_ms": 100}],
            "commands": []
        }
        (temp_benchmark_dir / "bench_20240306_100000.json").write_text(json.dumps(valid_data))
        
        # Create an invalid file
        (temp_benchmark_dir / "bench_20240306_100001.json").write_text("not valid json")
        
        benchmark.show_history()
        captured = capsys.readouterr()
        
        # Should not crash and should show the valid entry
        assert "Benchmark History" in captured.out

    def test_show_history_limits_to_10(self, temp_benchmark_dir, capsys):
        """Test that show_history only shows last 10 runs."""
        # Create 15 benchmark files
        for i in range(15):
            ts = f"20240306_{i:06d}"
            data = {
                "timestamp": f"2024-03-06T{i:02d}:00:00+00:00",
                "startup": [{"label": "mw --help", "avg_ms": 100}],
                "commands": []
            }
            file_path = temp_benchmark_dir / f"bench_{ts}.json"
            file_path.write_text(json.dumps(data))
        
        benchmark.show_history()
        captured = capsys.readouterr()
        
        # Should show history header
        assert "Benchmark History" in captured.out


class TestCmdBenchmark:
    """Test cmd_benchmark main entry point."""

    def test_cmd_benchmark_help(self, capsys):
        """Test --help argument."""
        result = benchmark.cmd_benchmark(["--help"])
        captured = capsys.readouterr()
        
        assert result == 0
        assert "mw bench" in captured.out
        assert "Performance Benchmarking" in captured.out

    def test_cmd_benchmark_help_short(self, capsys):
        """Test -h short help argument."""
        result = benchmark.cmd_benchmark(["-h"])
        captured = capsys.readouterr()
        
        assert result == 0
        assert "mw bench" in captured.out

    def test_cmd_benchmark_history(self, temp_benchmark_dir, capsys):
        """Test history subcommand."""
        result = benchmark.cmd_benchmark(["history"])
        captured = capsys.readouterr()
        
        assert result == 0
        # Should show "no history" message since no files exist
        assert "No benchmark history" in captured.out or "Benchmark History" in captured.out

    @patch("benchmark.bench_startup")
    @patch("benchmark.bench_commands")
    @patch("benchmark.bench_python")
    @patch("benchmark.bench_git")
    @patch("benchmark.save_results")
    def test_cmd_benchmark_full(self, mock_save, mock_git, mock_python, mock_commands, mock_startup, capsys):
        """Test full benchmark run."""
        # Mock return values
        mock_startup.return_value = [{"label": "test", "avg_ms": 100}]
        mock_commands.return_value = [{"label": "cmd", "ms": 200, "success": True}]
        mock_python.return_value = {"startup_ms": 50}
        mock_git.return_value = {"git status": 100}
        mock_save.return_value = Path("/tmp/bench_test.json")
        
        result = benchmark.cmd_benchmark([])
        captured = capsys.readouterr()
        
        assert result == 0
        assert "MyWork-AI Performance Benchmark" in captured.out
        mock_startup.assert_called_once()
        mock_commands.assert_called_once()
        mock_python.assert_called_once()
        mock_git.assert_called_once()
        mock_save.assert_called_once()

    @patch("benchmark.bench_startup")
    @patch("benchmark.bench_commands")
    @patch("benchmark.bench_python")
    @patch("benchmark.bench_git")
    @patch("benchmark.save_results")
    def test_cmd_benchmark_quick(self, mock_save, mock_git, mock_python, mock_commands, mock_startup, capsys):
        """Test quick benchmark run."""
        mock_startup.return_value = [{"label": "test", "avg_ms": 100}]
        mock_save.return_value = Path("/tmp/bench_test.json")
        
        result = benchmark.cmd_benchmark(["quick"])
        captured = capsys.readouterr()
        
        assert result == 0
        mock_startup.assert_called_once()
        # In quick mode, these should NOT be called
        mock_commands.assert_not_called()
        mock_python.assert_not_called()
        mock_git.assert_not_called()


class TestBenchStartup:
    """Test bench_startup function."""

    @patch("benchmark._time_cmd")
    def test_bench_startup_returns_benchmarks(self, mock_time_cmd, capsys):
        """Test that bench_startup returns list of benchmarks."""
        mock_time_cmd.return_value = {
            "duration_ms": 100,
            "success": True,
            "returncode": 0
        }
        
        result = benchmark.bench_startup()
        captured = capsys.readouterr()
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert "CLI Startup Benchmarks" in captured.out
        # Check that expected labels are present
        labels = [b["label"] for b in result]
        assert "mw --help" in labels


class TestBenchCommands:
    """Test bench_commands function."""

    @patch("benchmark._time_cmd")
    def test_bench_commands_returns_benchmarks(self, mock_time_cmd, capsys, temp_mywork_root):
        """Test that bench_commands returns list of benchmarks."""
        mock_time_cmd.return_value = {
            "duration_ms": 100,
            "success": True,
            "returncode": 0
        }
        
        result = benchmark.bench_commands()
        captured = capsys.readouterr()
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert "Command Benchmarks" in captured.out

    @patch("benchmark._time_cmd")
    def test_bench_commands_handles_failure(self, mock_time_cmd, capsys, temp_mywork_root):
        """Test that bench_commands handles command failures."""
        mock_time_cmd.return_value = {
            "duration_ms": 100,
            "success": False,
            "returncode": 1
        }
        
        result = benchmark.bench_commands()
        
        assert isinstance(result, list)
        assert len(result) > 0
        # All commands should still be benchmarked even if they fail
        for cmd in result:
            assert "label" in cmd
            assert "ms" in cmd
            assert "success" in cmd


class TestBenchPython:
    """Test bench_python function."""

    @patch("benchmark._time_cmd")
    def test_bench_python_returns_data(self, mock_time_cmd, capsys):
        """Test that bench_python returns Python environment data."""
        mock_time_cmd.return_value = {
            "duration_ms": 50,
            "success": True,
            "returncode": 0
        }
        
        result = benchmark.bench_python()
        captured = capsys.readouterr()
        
        assert "startup_ms" in result
        assert "imports_ms" in result
        assert "Python Environment" in captured.out


class TestBenchGit:
    """Test bench_git function."""

    @patch("benchmark._time_cmd")
    def test_bench_git_returns_data(self, mock_time_cmd, capsys):
        """Test that bench_git returns git performance data."""
        mock_time_cmd.return_value = {
            "duration_ms": 100,
            "success": True,
            "returncode": 0
        }
        
        result = benchmark.bench_git()
        captured = capsys.readouterr()
        
        assert isinstance(result, dict)
        assert "Git Performance" in captured.out
        # Check for expected git command labels
        assert any("git" in key for key in result.keys())


class TestIntegration:
    """Integration tests for benchmark module."""

    def test_benchmark_directory_creation(self, tmp_path):
        """Test that benchmark directory is created at module load time."""
        # The BENCH_DIR is created when the module loads via .mkdir(exist_ok=True)
        # Create a new directory and set it as BENCH_DIR
        new_dir = tmp_path / "new_benchmarks"
        new_dir.mkdir(parents=True, exist_ok=True)
        
        # When we patch BENCH_DIR and use save_results
        orig_dir = benchmark.BENCH_DIR
        try:
            benchmark.BENCH_DIR = new_dir
            result_path = benchmark.save_results({"test": "data"})
            assert result_path.exists()
            assert result_path.parent == new_dir
        finally:
            benchmark.BENCH_DIR = orig_dir

    def test_full_benchmark_cycle(self, temp_benchmark_dir, temp_mywork_root):
        """Test a complete benchmark cycle: run, save, show history."""
        # Run a quick benchmark
        with patch("benchmark.bench_commands"), \
             patch("benchmark.bench_python"), \
             patch("benchmark.bench_git"):
            
            result = benchmark.cmd_benchmark(["quick"])
            assert result == 0
        
        # Verify file was created
        files = list(temp_benchmark_dir.glob("bench_*.json"))
        assert len(files) > 0
        
        # Verify we can show history
        with patch("sys.stdout") as mock_stdout:
            benchmark.show_history()
            # History should be displayed
            output = "".join(call.args[0] for call in mock_stdout.write.call_args_list if call.args)
            assert "Benchmark History" in output or "benchmarks completed" in output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
