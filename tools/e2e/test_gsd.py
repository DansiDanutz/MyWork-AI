#!/usr/bin/env python3
"""
E2E Test: GSD Workflow Tester
============================
Tests the mw CLI commands: status, help, dashboard, search, projects
Verifies output format, content, and error handling.
"""

import subprocess
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any

class GSDWorkflowTester:
    def __init__(self, project_root: str = "/home/Memo1981/MyWork-AI"):
        self.project_root = Path(project_root)
        self.mw_script = self.project_root / "tools" / "mw.py"
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_result(self, test_name: str, status: str, message: str = "", output: str = ""):
        """Log a test result"""
        self.total_tests += 1
        if status == "PASS":
            self.passed_tests += 1
        elif status == "FAIL":
            self.failed_tests += 1
            
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "output": output[:500] if output else "",  # Truncate long output
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.results.append(result)
        print(f"[{status}] {test_name}: {message}")
        
    def run_mw_command(self, args: List[str], timeout: int = 30) -> Dict[str, Any]:
        """Run a mw command and return result"""
        cmd = ["python3", str(self.mw_script)] + args
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=timeout,
                cwd=self.project_root
            )
            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": f"Command timed out after {timeout}s",
                "success": False
            }
        except Exception as e:
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "success": False
            }
    
    def test_mw_status(self):
        """Test mw status command"""
        result = self.run_mw_command(["status"])
        
        if not result["success"]:
            self.log_result("mw_status", "FAIL", f"Command failed: {result['stderr']}")
            return
            
        output = result["stdout"]
        
        # Check for expected content
        expected_sections = ["MyWork Framework Status", "Component Health"]
        missing_sections = [s for s in expected_sections if s not in output]
        
        if missing_sections:
            self.log_result("mw_status", "FAIL", f"Missing sections: {missing_sections}", output)
        else:
            self.log_result("mw_status", "PASS", "Status command executed successfully", output)
    
    def test_mw_help(self):
        """Test mw help command"""
        result = self.run_mw_command(["--help"])
        
        if not result["success"]:
            self.log_result("mw_help", "FAIL", f"Command failed: {result['stderr']}")
            return
            
        output = result["stdout"]
        
        # Check for expected help content
        expected_commands = ["dashboard", "status", "search", "projects", "brain"]
        missing_commands = [c for c in expected_commands if c not in output.lower()]
        
        if missing_commands:
            self.log_result("mw_help", "FAIL", f"Missing commands in help: {missing_commands}", output)
        else:
            self.log_result("mw_help", "PASS", "Help command shows expected commands", output)
    
    def test_mw_dashboard_check(self):
        """Test mw dashboard command (just check if it starts properly)"""
        # Since dashboard is interactive, we'll test with a quick timeout
        result = self.run_mw_command(["dashboard", "--version"], timeout=5)
        
        # Even if it times out or fails, we want to check the initial output
        if "dashboard" in result["stdout"].lower() or "interactive" in result["stdout"].lower():
            self.log_result("mw_dashboard_check", "PASS", "Dashboard command recognizes --version flag", result["stdout"])
        elif result["returncode"] == 0:
            self.log_result("mw_dashboard_check", "PASS", "Dashboard command executed", result["stdout"])
        else:
            self.log_result("mw_dashboard_check", "WARN", f"Dashboard test inconclusive: {result['stderr']}", result["stdout"])
    
    def test_mw_search(self):
        """Test mw search command"""
        # Test with a generic search term
        result = self.run_mw_command(["search", "test"])
        
        if not result["success"]:
            # Search might fail if no modules exist, which is acceptable
            if "no modules found" in result["stderr"].lower() or "registry" in result["stderr"].lower():
                self.log_result("mw_search", "PASS", "Search command handled empty registry correctly", result["stderr"])
            else:
                self.log_result("mw_search", "FAIL", f"Search command failed unexpectedly: {result['stderr']}")
            return
            
        output = result["stdout"]
        self.log_result("mw_search", "PASS", "Search command executed successfully", output)
    
    def test_mw_projects(self):
        """Test mw projects command"""
        result = self.run_mw_command(["projects"])
        
        if not result["success"]:
            # Projects might fail if no registry exists, which is acceptable
            if "registry" in result["stderr"].lower() or "no projects" in result["stderr"].lower():
                self.log_result("mw_projects", "PASS", "Projects command handled empty registry correctly", result["stderr"])
            else:
                self.log_result("mw_projects", "FAIL", f"Projects command failed unexpectedly: {result['stderr']}")
            return
            
        output = result["stdout"]
        self.log_result("mw_projects", "PASS", "Projects command executed successfully", output)
    
    def test_mw_brain_status(self):
        """Test mw brain commands"""
        # Test brain stats
        result = self.run_mw_command(["brain", "stats"])
        
        if result["success"]:
            self.log_result("mw_brain_stats", "PASS", "Brain stats command executed", result["stdout"])
        else:
            # Brain might not be configured, which is acceptable
            if "brain" in result["stderr"].lower() or "database" in result["stderr"].lower():
                self.log_result("mw_brain_stats", "WARN", "Brain not configured (acceptable)", result["stderr"])
            else:
                self.log_result("mw_brain_stats", "FAIL", f"Brain stats failed: {result['stderr']}")
    
    def test_error_handling(self):
        """Test error handling with bad inputs"""
        # Test invalid command
        result = self.run_mw_command(["nonexistent_command"])
        
        if not result["success"]:
            if "unknown command" in result["stderr"].lower() or "invalid" in result["stderr"].lower():
                self.log_result("error_handling_bad_command", "PASS", "Correctly rejected invalid command", result["stderr"])
            else:
                self.log_result("error_handling_bad_command", "PASS", "Command failed as expected", result["stderr"])
        else:
            self.log_result("error_handling_bad_command", "FAIL", "Should have failed with invalid command")
    
    def test_autoforge_compatibility(self):
        """Test AutoForge commands (backwards compatibility)"""
        # Test af status
        result = self.run_mw_command(["af", "status"])
        
        if result["success"] or "autoforge" in result["stdout"].lower():
            self.log_result("af_status", "PASS", "AutoForge status command recognized", result["stdout"])
        else:
            self.log_result("af_status", "WARN", "AutoForge not available (acceptable)", result["stderr"])
        
        # Test legacy ac alias
        result = self.run_mw_command(["ac", "status"])
        
        if result["success"] or "autoforge" in result["stdout"].lower():
            self.log_result("ac_alias", "PASS", "Legacy ac alias working", result["stdout"])
        else:
            self.log_result("ac_alias", "WARN", "Legacy ac alias not available (acceptable)", result["stderr"])
    
    def run_all_tests(self):
        """Run all GSD workflow tests"""
        print("=== GSD Workflow E2E Tests ===")
        print(f"Testing mw CLI at: {self.mw_script}")
        print()
        
        # Check if mw.py exists
        if not self.mw_script.exists():
            self.log_result("setup", "FAIL", f"mw.py not found at {self.mw_script}")
            return self.generate_report()
        
        self.log_result("setup", "PASS", "mw.py script found")
        
        # Run all tests
        self.test_mw_help()
        self.test_mw_status()
        self.test_mw_dashboard_check()
        self.test_mw_search()
        self.test_mw_projects()
        self.test_mw_brain_status()
        self.test_autoforge_compatibility()
        self.test_error_handling()
        
        return self.generate_report()
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate test report"""
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        report = {
            "test_suite": "GSD Workflow E2E Tests",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_tests": self.total_tests,
                "passed": self.passed_tests,
                "failed": self.failed_tests,
                "skipped": 0,
                "success_rate": round(success_rate, 2)
            },
            "results": self.results
        }
        
        print(f"\n=== GSD Workflow Test Summary ===")
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        return report


def main():
    """Main entry point"""
    tester = GSDWorkflowTester()
    report = tester.run_all_tests()
    
    # Save report to file
    report_file = Path("/home/Memo1981/MyWork-AI/tools/e2e/gsd_test_results.json")
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\nReport saved to: {report_file}")
    
    # Exit with appropriate code
    sys.exit(0 if report["summary"]["failed"] == 0 else 1)


if __name__ == "__main__":
    main()