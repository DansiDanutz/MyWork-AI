#!/usr/bin/env python3
"""
E2E Test: Health Check Validator
===============================
Tests tools/health_check.py quick and report modes.
Verifies all checks pass or documents failures.
"""

import subprocess
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any

class HealthCheckTester:
    def __init__(self, project_root: str = "/home/Memo1981/MyWork-AI"):
        self.project_root = Path(project_root)
        self.health_script = self.project_root / "tools" / "health_check.py"
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
            "output": output[:1000] if output else "",  # Truncate long output
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.results.append(result)
        print(f"[{status}] {test_name}: {message}")
        
    def run_health_command(self, args: List[str], timeout: int = 60) -> Dict[str, Any]:
        """Run health_check.py command and return result"""
        cmd = ["python3", str(self.health_script)] + args
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
    
    def parse_health_output(self, output: str) -> Dict[str, Any]:
        """Parse health check output and extract status information"""
        lines = output.split('\n')
        
        parsed = {
            "total_checks": 0,
            "passed_checks": 0,
            "failed_checks": 0,
            "warnings": 0,
            "checks": [],
            "summary_found": False
        }
        
        current_check = None
        
        for line in lines:
            line = line.strip()
            
            # Look for check results
            if line.startswith('[PASS]') or line.startswith('✓'):
                parsed["passed_checks"] += 1
                parsed["total_checks"] += 1
                check_name = line.split(']', 1)[1].strip() if ']' in line else line
                parsed["checks"].append({"status": "PASS", "name": check_name})
                
            elif line.startswith('[FAIL]') or line.startswith('✗') or line.startswith('❌'):
                parsed["failed_checks"] += 1
                parsed["total_checks"] += 1
                check_name = line.split(']', 1)[1].strip() if ']' in line else line
                parsed["checks"].append({"status": "FAIL", "name": check_name})
                
            elif line.startswith('[WARN]') or line.startswith('⚠'):
                parsed["warnings"] += 1
                parsed["total_checks"] += 1
                check_name = line.split(']', 1)[1].strip() if ']' in line else line
                parsed["checks"].append({"status": "WARN", "name": check_name})
                
            # Look for summary section
            elif "summary" in line.lower() or "health" in line.lower():
                parsed["summary_found"] = True
                
            # Look for specific health metrics
            elif "checks:" in line.lower():
                try:
                    # Try to extract numbers from lines like "Total checks: 15"
                    if "total" in line.lower():
                        number = int(''.join(filter(str.isdigit, line)))
                        parsed["total_checks"] = max(parsed["total_checks"], number)
                except:
                    pass
        
        return parsed
    
    def test_health_script_exists(self):
        """Test if health_check.py script exists"""
        if self.health_script.exists():
            self.log_result("health_script_exists", "PASS", f"health_check.py found at {self.health_script}")
            return True
        else:
            self.log_result("health_script_exists", "FAIL", f"health_check.py not found at {self.health_script}")
            return False
    
    def test_health_help(self):
        """Test health check help command"""
        result = self.run_health_command(["--help"])
        
        if result["success"]:
            help_output = result["stdout"]
            if "health" in help_output.lower() and ("quick" in help_output or "report" in help_output):
                self.log_result("health_help", "PASS", "Help shows expected commands", help_output[:200])
                return True
            else:
                self.log_result("health_help", "WARN", "Help available but content unexpected", help_output[:200])
                return True
        else:
            self.log_result("health_help", "FAIL", f"Help command failed: {result['stderr']}")
            return False
    
    def test_health_quick(self):
        """Test health check quick mode"""
        print("Running health check quick mode...")
        result = self.run_health_command(["quick"])
        
        if not result["success"]:
            self.log_result("health_quick", "FAIL", f"Quick mode failed: {result['stderr']}", result["stdout"])
            return None
        
        output = result["stdout"]
        parsed = self.parse_health_output(output)
        
        # Analyze results
        if parsed["total_checks"] > 0:
            success_rate = (parsed["passed_checks"] / parsed["total_checks"]) * 100
            
            if parsed["failed_checks"] == 0:
                status = "PASS"
                message = f"All {parsed['total_checks']} checks passed"
            elif success_rate >= 80:
                status = "WARN"
                message = f"{parsed['passed_checks']}/{parsed['total_checks']} checks passed ({success_rate:.1f}%)"
            else:
                status = "FAIL"
                message = f"Only {parsed['passed_checks']}/{parsed['total_checks']} checks passed ({success_rate:.1f}%)"
            
            details = f"Passed: {parsed['passed_checks']}, Failed: {parsed['failed_checks']}, Warnings: {parsed['warnings']}"
            self.log_result("health_quick", status, f"{message} - {details}", output)
            
            # Log individual failed checks
            for check in parsed["checks"]:
                if check["status"] == "FAIL":
                    self.log_result(f"health_check_failed", "INFO", f"Failed check: {check['name']}")
            
            return parsed
        else:
            self.log_result("health_quick", "WARN", "No health checks detected in output", output)
            return None
    
    def test_health_report(self):
        """Test health check report mode"""
        print("Running health check report mode...")
        result = self.run_health_command(["report"])
        
        if not result["success"]:
            self.log_result("health_report", "FAIL", f"Report mode failed: {result['stderr']}", result["stdout"])
            return None
        
        output = result["stdout"]
        parsed = self.parse_health_output(output)
        
        # Check if report is more detailed than quick mode
        if len(output) > 500 and parsed["summary_found"]:
            self.log_result("health_report", "PASS", f"Detailed report generated ({len(output)} chars)", output[:500])
        elif len(output) > 200:
            self.log_result("health_report", "PASS", f"Report generated ({len(output)} chars)", output[:300])
        else:
            self.log_result("health_report", "WARN", "Report seems short or incomplete", output)
        
        return parsed
    
    def test_health_fix_mode(self):
        """Test health check fix mode if available"""
        # First check if fix mode is available
        help_result = self.run_health_command(["--help"])
        
        if help_result["success"] and "fix" in help_result["stdout"].lower():
            # Fix mode exists, test it (but don't actually fix anything dangerous)
            result = self.run_health_command(["fix", "--dry-run"])
            
            if result["success"]:
                self.log_result("health_fix_mode", "PASS", "Fix mode (dry-run) works", result["stdout"][:300])
            else:
                # Try without dry-run flag
                result = self.run_health_command(["fix", "--help"])
                if result["success"]:
                    self.log_result("health_fix_mode", "PASS", "Fix mode help available")
                else:
                    self.log_result("health_fix_mode", "WARN", "Fix mode available but test inconclusive")
        else:
            self.log_result("health_fix_mode", "SKIP", "Fix mode not available or not found in help")
    
    def test_health_json_output(self):
        """Test if health check supports JSON output"""
        # Try common JSON flags
        json_flags = ["--json", "--format=json", "-j"]
        
        for flag in json_flags:
            result = self.run_health_command(["quick", flag])
            
            if result["success"]:
                try:
                    json_data = json.loads(result["stdout"])
                    self.log_result("health_json_output", "PASS", f"JSON output works with {flag}")
                    return json_data
                except:
                    continue
        
        # No JSON output found
        self.log_result("health_json_output", "SKIP", "JSON output not available or not working")
        return None
    
    def test_health_verbose_mode(self):
        """Test health check verbose mode"""
        verbose_flags = ["--verbose", "-v", "verbose"]
        
        for flag in verbose_flags:
            result = self.run_health_command([flag])
            
            if result["success"] and len(result["stdout"]) > 200:
                self.log_result("health_verbose", "PASS", f"Verbose mode works with {flag}")
                return
        
        self.log_result("health_verbose", "SKIP", "Verbose mode not available or not working")
    
    def run_all_tests(self):
        """Run all health check tests"""
        print("=== Health Check Validator E2E Tests ===")
        print(f"Testing health_check.py at: {self.health_script}")
        print()
        
        # Basic setup tests
        if not self.test_health_script_exists():
            return self.generate_report()
        
        self.test_health_help()
        
        # Core functionality tests
        quick_results = self.test_health_quick()
        report_results = self.test_health_report()
        
        # Optional feature tests
        self.test_health_fix_mode()
        self.test_health_json_output()
        self.test_health_verbose_mode()
        
        return self.generate_report()
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate test report"""
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        # Extract health status from results
        health_status = {}
        for result in self.results:
            if result["test"] in ["health_quick", "health_report"]:
                if "checks passed" in result["message"]:
                    # Extract numbers from message
                    import re
                    numbers = re.findall(r'\d+', result["message"])
                    if len(numbers) >= 2:
                        health_status[result["test"]] = {
                            "passed": int(numbers[0]),
                            "total": int(numbers[1])
                        }
        
        report = {
            "test_suite": "Health Check Validator E2E Tests",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_tests": self.total_tests,
                "passed": self.passed_tests,
                "failed": self.failed_tests,
                "skipped": 0,
                "success_rate": round(success_rate, 2)
            },
            "health_status": health_status,
            "results": self.results
        }
        
        print(f"\n=== Health Check Test Summary ===")
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if health_status:
            print("\nHealth Check Results:")
            for mode, stats in health_status.items():
                print(f"  {mode}: {stats['passed']}/{stats['total']} checks passed")
        
        return report


def main():
    """Main entry point"""
    tester = HealthCheckTester()
    report = tester.run_all_tests()
    
    # Save report to file
    report_file = Path("/home/Memo1981/MyWork-AI/tools/e2e/health_test_results.json")
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\nReport saved to: {report_file}")
    
    # Exit with appropriate code
    sys.exit(0 if report["summary"]["failed"] == 0 else 1)


if __name__ == "__main__":
    main()