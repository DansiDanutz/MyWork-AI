#!/usr/bin/env python3
"""
Performance benchmarks for MyWork CLI.

Tests that core operations complete within acceptable time limits
to ensure good user experience.
"""

import pytest
import subprocess
import time
import sys
from pathlib import Path
import tempfile
import os

# Add tools directory to path for imports  
tools_dir = Path(__file__).parent.parent / "tools"
sys.path.insert(0, str(tools_dir))


class TestCLIPerformance:
    """Test CLI startup and command performance."""
    
    def setup_method(self):
        """Set up test environment."""
        self.test_env = os.environ.copy()
        self.test_env["MYWORK_ROOT"] = str(Path.cwd())
        self.timeout_limit = 10  # Generous timeout for CI environments
        
    def run_mw_command_timed(self, args: list) -> tuple[subprocess.CompletedProcess, float]:
        """Run mw command and measure execution time."""
        cmd = [sys.executable, str(tools_dir / "mw.py")] + args
        
        start_time = time.time()
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=self.test_env,
            timeout=self.timeout_limit
        )
        end_time = time.time()
        
        execution_time = end_time - start_time
        return result, execution_time
        
    def test_cli_startup_time_under_2_seconds(self):
        """Test that CLI startup time is under 2 seconds."""
        result, execution_time = self.run_mw_command_timed(["--help"])
        
        # Should complete successfully
        assert result.returncode == 0, f"Help command failed: {result.stderr}"
        
        # Should complete in under 2 seconds
        assert execution_time < 2.0, f"CLI startup too slow: {execution_time:.2f}s (limit: 2.0s)"
        
        # Should produce help output
        assert len(result.stdout) > 100, "Help output too short"
        
    def test_status_command_performance(self):
        """Test that status command completes quickly."""
        result, execution_time = self.run_mw_command_timed(["status"])
        
        # Should complete (may have warnings/errors in test env)
        assert result.returncode in [0, 1], f"Unexpected return code: {result.returncode}"
        
        # Should complete in reasonable time (under 3 seconds)
        assert execution_time < 3.0, f"Status check too slow: {execution_time:.2f}s (limit: 3.0s)"
        
        print(f"✓ Status command completed in {execution_time:.2f}s")
        
    def test_projects_command_performance(self):
        """Test that projects listing is fast."""
        result, execution_time = self.run_mw_command_timed(["projects"])
        
        # Should complete 
        assert result.returncode in [0, 1], f"Unexpected return code: {result.returncode}"
        
        # Should be fast (under 2 seconds)
        assert execution_time < 2.0, f"Projects listing too slow: {execution_time:.2f}s (limit: 2.0s)"
        
        print(f"✓ Projects command completed in {execution_time:.2f}s")
        
    def test_help_commands_are_instant(self):
        """Test that help commands are nearly instant."""
        help_commands = [
            ["status", "--help"],
            ["new", "--help"], 
            ["projects", "--help"],
            ["brain", "--help"]
        ]
        
        for cmd_args in help_commands:
            result, execution_time = self.run_mw_command_timed(cmd_args)
            
            # Should complete successfully
            assert result.returncode == 0, f"Help command {' '.join(cmd_args)} failed: {result.stderr}"
            
            # Help should be very fast (under 0.5 seconds)
            assert execution_time < 0.5, f"Help {' '.join(cmd_args)} too slow: {execution_time:.2f}s"
            
            print(f"✓ Help {' '.join(cmd_args)} completed in {execution_time:.2f}s")


class TestBrainPerformance:
    """Test brain search performance."""
    
    def setup_method(self):
        """Set up test environment."""
        self.test_env = os.environ.copy()
        self.test_env["MYWORK_ROOT"] = str(Path.cwd())
        self.timeout_limit = 10
        
    def run_brain_command_timed(self, args: list) -> tuple[subprocess.CompletedProcess, float]:
        """Run brain command and measure execution time."""
        cmd = [sys.executable, str(tools_dir / "mw.py"), "brain"] + args
        
        start_time = time.time()
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=self.test_env,
            timeout=self.timeout_limit
        )
        end_time = time.time()
        
        execution_time = end_time - start_time
        return result, execution_time
        
    def test_brain_search_under_1_second(self):
        """Test that brain search completes under 1 second."""
        result, execution_time = self.run_brain_command_timed(["search", "test"])
        
        # Should complete (may not find results in test env)
        assert result.returncode in [0, 1], f"Brain search failed: {result.stderr}"
        
        # Should be fast (under 1 second)
        assert execution_time < 1.0, f"Brain search too slow: {execution_time:.2f}s (limit: 1.0s)"
        
        print(f"✓ Brain search completed in {execution_time:.2f}s")
        
    def test_brain_stats_performance(self):
        """Test that brain stats is fast."""
        result, execution_time = self.run_brain_command_timed(["stats"])
        
        # Should complete
        assert result.returncode in [0, 1], f"Brain stats failed: {result.stderr}"
        
        # Should be fast (under 1 second)
        assert execution_time < 1.0, f"Brain stats too slow: {execution_time:.2f}s (limit: 1.0s)"
        
        print(f"✓ Brain stats completed in {execution_time:.2f}s")


class TestScaffoldPerformance:
    """Test scaffold/project creation performance."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_env = os.environ.copy()
        self.test_env["MYWORK_ROOT"] = self.temp_dir
        self.timeout_limit = 15  # Scaffold can be slower due to file creation
        
    def run_scaffold_command_timed(self, args: list) -> tuple[subprocess.CompletedProcess, float]:
        """Run scaffold command and measure execution time."""
        cmd = [sys.executable, str(tools_dir / "scaffold.py")] + args
        
        # Ensure projects directory exists
        projects_dir = Path(self.temp_dir) / "projects"
        projects_dir.mkdir(parents=True, exist_ok=True)
        
        start_time = time.time()
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=self.test_env,
            timeout=self.timeout_limit
        )
        end_time = time.time()
        
        execution_time = end_time - start_time
        return result, execution_time
        
    def test_basic_scaffold_under_3_seconds(self):
        """Test that basic project creation is under 3 seconds."""
        result, execution_time = self.run_scaffold_command_timed(["new", "test-perf", "basic"])
        
        # Should complete successfully
        assert result.returncode == 0, f"Basic scaffold failed: {result.stderr}"
        
        # Should complete in under 3 seconds
        assert execution_time < 3.0, f"Basic scaffold too slow: {execution_time:.2f}s (limit: 3.0s)"
        
        # Verify project was created
        project_path = Path(self.temp_dir) / "projects" / "test-perf"
        assert project_path.exists(), "Project directory not created"
        
        print(f"✓ Basic scaffold completed in {execution_time:.2f}s")
        
    def test_fastapi_scaffold_reasonable_time(self):
        """Test that FastAPI project creation is reasonably fast."""
        result, execution_time = self.run_scaffold_command_timed(["new", "test-api", "fastapi"])
        
        # Should complete successfully
        assert result.returncode == 0, f"FastAPI scaffold failed: {result.stderr}"
        
        # Should complete in reasonable time (under 5 seconds)
        assert execution_time < 5.0, f"FastAPI scaffold too slow: {execution_time:.2f}s (limit: 5.0s)"
        
        # Verify key files were created
        project_path = Path(self.temp_dir) / "projects" / "test-api"
        assert project_path.exists(), "Project directory not created"
        assert (project_path / "backend" / "main.py").exists(), "Main FastAPI file not created"
        
        print(f"✓ FastAPI scaffold completed in {execution_time:.2f}s")
        
    def test_template_listing_fast(self):
        """Test that template listing is very fast."""
        result, execution_time = self.run_scaffold_command_timed(["list"])
        
        # Should complete successfully
        assert result.returncode == 0, f"Template listing failed: {result.stderr}"
        
        # Should be very fast (under 0.5 seconds)
        assert execution_time < 0.5, f"Template listing too slow: {execution_time:.2f}s (limit: 0.5s)"
        
        # Should show templates
        assert "Available Templates" in result.stdout, "Template listing output missing"
        
        print(f"✓ Template listing completed in {execution_time:.2f}s")


class TestOverallPerformance:
    """Test overall system performance characteristics."""
    
    def setup_method(self):
        """Set up test environment."""
        self.test_env = os.environ.copy()
        self.test_env["MYWORK_ROOT"] = str(Path.cwd())
        
    def test_multiple_commands_no_slowdown(self):
        """Test that running multiple commands doesn't cause slowdown."""
        commands = [
            ["status"],
            ["projects"], 
            ["brain", "stats"],
            ["--help"]
        ]
        
        execution_times = []
        
        for cmd_args in commands:
            cmd = [sys.executable, str(tools_dir / "mw.py")] + cmd_args
            
            start_time = time.time()
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=self.test_env,
                timeout=10
            )
            end_time = time.time()
            
            execution_time = end_time - start_time
            execution_times.append(execution_time)
            
            # Each command should complete
            assert result.returncode in [0, 1], f"Command {' '.join(cmd_args)} failed"
        
        # No command should be dramatically slower than others (no memory leaks, etc.)
        avg_time = sum(execution_times) / len(execution_times)
        max_time = max(execution_times)
        
        # Max time shouldn't be more than 3x the average (some variance is expected)
        assert max_time <= avg_time * 3, f"Command performance inconsistent: avg={avg_time:.2f}s, max={max_time:.2f}s"
        
        print(f"✓ Command performance consistent: avg={avg_time:.2f}s, max={max_time:.2f}s")
        
    def test_concurrent_command_handling(self):
        """Test that system can handle concurrent commands reasonably."""
        import threading
        import queue
        
        def run_command(cmd_args, result_queue):
            """Run command and put result in queue."""
            cmd = [sys.executable, str(tools_dir / "mw.py")] + cmd_args
            
            start_time = time.time()
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=self.test_env,
                timeout=10
            )
            end_time = time.time()
            
            execution_time = end_time - start_time
            result_queue.put((cmd_args, result, execution_time))
        
        # Run multiple commands concurrently
        commands = [
            ["--help"],
            ["status"],
            ["projects"]
        ]
        
        threads = []
        result_queue = queue.Queue()
        
        # Start all commands
        start_time = time.time()
        for cmd_args in commands:
            thread = threading.Thread(target=run_command, args=(cmd_args, result_queue))
            thread.start()
            threads.append(thread)
        
        # Wait for all to complete
        for thread in threads:
            thread.join(timeout=15)  # Generous timeout
        
        total_time = time.time() - start_time
        
        # Collect results
        results = []
        while not result_queue.empty():
            results.append(result_queue.get())
        
        # All commands should complete
        assert len(results) == len(commands), f"Not all commands completed: {len(results)}/{len(commands)}"
        
        # Concurrent execution should be faster than sequential
        # (though this is a basic test since commands might not actually run concurrently)
        max_individual_time = max(exec_time for _, _, exec_time in results)
        assert total_time <= max_individual_time + 2, f"Concurrent execution inefficient: total={total_time:.2f}s"
        
        print(f"✓ Concurrent commands completed in {total_time:.2f}s")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])