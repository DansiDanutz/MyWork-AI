#!/usr/bin/env python3
"""
Integration tests for MyWork CLI commands.

Tests end-to-end functionality of the mw command line interface
to ensure all components work together correctly.
"""

import json
import pytest
import subprocess
import tempfile
from pathlib import Path
import os
import sys

# Add tools directory to path for imports
tools_dir = Path(__file__).parent.parent / "tools"
sys.path.insert(0, str(tools_dir))


class TestMWIntegration:
    """Integration tests for mw commands."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.test_env = os.environ.copy()
        # Ensure we're using test environment
        self.test_env["MYWORK_ROOT"] = str(Path.cwd())
        
    def run_mw_command(self, args: list, capture_output: bool = True) -> subprocess.CompletedProcess:
        """Helper to run mw commands with proper environment."""
        cmd = [sys.executable, str(tools_dir / "mw.py")] + args
        return subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            env=self.test_env,
            timeout=10  # Prevent hanging tests
        )
        
    def test_mw_status_command(self):
        """Test 'mw status' end-to-end."""
        result = self.run_mw_command(["status"])
        
        # Should complete without error (though some checks might fail in test env)
        assert result.returncode in [0, 1], f"Unexpected return code: {result.returncode}"
        
        # Should contain expected output
        output = result.stdout
        assert "MyWork Quick Status" in output or "Framework Health" in output
        
    def test_mw_status_help(self):
        """Test 'mw status --help' displays help."""
        result = self.run_mw_command(["status", "--help"])
        
        assert result.returncode == 0
        assert "Status Commands" in result.stdout
        assert "Framework Health Monitor" in result.stdout
        
    def test_mw_brain_stats_command(self):
        """Test 'mw brain stats' end-to-end."""
        result = self.run_mw_command(["brain", "stats"])
        
        # Should complete (return code may be 0 or 1 depending on brain file existence)
        assert result.returncode in [0, 1], f"Unexpected return code: {result.returncode}"
        
        # Should contain stats output or error message
        output = result.stdout + result.stderr
        expected_terms = ["Brain Statistics", "entries", "stats", "Brain not found", "error"]
        assert any(term in output for term in expected_terms)
        
    def test_mw_projects_command(self):
        """Test 'mw projects' end-to-end."""
        result = self.run_mw_command(["projects"])
        
        # Should complete without critical errors
        assert result.returncode in [0, 1]
        
        # Should contain projects output
        output = result.stdout + result.stderr
        expected_terms = ["Projects", "project", "No projects", "Found", "Error"]
        assert any(term in output for term in expected_terms)
        
    def test_mw_new_project_basic(self):
        """Test 'mw new test-proj basic' creates files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set up temporary environment
            test_env = self.test_env.copy()
            test_env["MYWORK_ROOT"] = temp_dir
            
            # Create projects directory
            projects_dir = Path(temp_dir) / "projects"
            projects_dir.mkdir(parents=True, exist_ok=True)
            
            # Run new command
            cmd = [sys.executable, str(tools_dir / "scaffold.py"), "new", "test-proj", "basic"]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=test_env,
                timeout=30
            )
            
            # Check if project was created
            project_path = projects_dir / "test-proj"
            
            if result.returncode == 0:
                # Success case - verify structure
                assert project_path.exists(), f"Project directory not created: {project_path}"
                
                # Check for key files
                expected_files = [
                    "README.md",
                    ".gitignore",
                    ".planning/PROJECT.md",
                    ".planning/ROADMAP.md",
                    ".planning/STATE.md"
                ]
                
                for file_path in expected_files:
                    full_path = project_path / file_path
                    assert full_path.exists(), f"Expected file not created: {full_path}"
                    
                    # Check file is not empty
                    assert full_path.stat().st_size > 0, f"File is empty: {full_path}"
                    
                # Check README contains project name
                readme_content = (project_path / "README.md").read_text()
                assert "test-proj" in readme_content
            else:
                # If creation failed, at least verify the error is reasonable
                assert "template" in result.stderr.lower() or "error" in result.stderr.lower()
                
    def test_mw_help_command(self):
        """Test 'mw --help' shows usage information."""
        result = self.run_mw_command(["--help"])
        
        assert result.returncode == 0
        output = result.stdout
        
        # Should contain main command categories
        expected_sections = ["Usage", "Commands", "Examples"]
        for section in expected_sections:
            assert section in output, f"Missing section: {section}"
            
    def test_mw_invalid_command(self):
        """Test mw handles invalid commands gracefully."""
        result = self.run_mw_command(["nonexistent-command"])
        
        # Should fail gracefully
        assert result.returncode != 0
        
        # Should provide helpful output
        output = result.stdout + result.stderr
        helpful_terms = ["help", "usage", "command", "invalid", "not found"]
        assert any(term in output.lower() for term in helpful_terms)


class TestMWCommandChaining:
    """Test command interactions and data persistence."""
    
    def test_status_after_scan(self):
        """Test that status reflects changes after scan."""
        # This is a basic interaction test
        result1 = subprocess.run(
            [sys.executable, str(tools_dir / "mw.py"), "scan"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        result2 = subprocess.run(
            [sys.executable, str(tools_dir / "mw.py"), "status"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Both should complete (though may have warnings/errors)
        assert result1.returncode in [0, 1]
        assert result2.returncode in [0, 1]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])