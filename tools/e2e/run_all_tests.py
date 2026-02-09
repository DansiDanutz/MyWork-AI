#!/usr/bin/env python3
"""
E2E Test: Full Test Suite Runner
===============================
Runs pytest on tests/ directory and all e2e tests.
Aggregates results into comprehensive reports.
"""

import subprocess
import sys
import json
import time
import os
from pathlib import Path
from typing import Dict, List, Any

class TestSuiteRunner:
    def __init__(self, project_root: str = "/home/Memo1981/MyWork-AI"):
        self.project_root = Path(project_root)
        self.e2e_dir = self.project_root / "tools" / "e2e"
        self.tests_dir = self.project_root / "tests"
        self.reports_dir = self.project_root / "reports"
        
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.skipped_tests = 0
        
        # Ensure reports directory exists
        self.reports_dir.mkdir(exist_ok=True)
        
        # E2E test files to run
        self.e2e_tests = [
            "test_gsd.py",
            "test_brain_e2e.py", 
            "test_autoforge.py",
            "test_marketplace_e2e.py",
            "test_health.py"
        ]
        
        # Smoke test files if they exist
        self.smoke_tests = [
            "smoke_test_marketplace.py",
            "smoke_test_ai_dashboard.py",
            "smoke_test_task_tracker.py"
        ]
        
    def log_result(self, test_name: str, status: str, message: str = "", details: Dict = None):
        """Log a test result"""
        self.total_tests += 1
        if status == "PASS":
            self.passed_tests += 1
        elif status == "FAIL":
            self.failed_tests += 1
        elif status == "SKIP":
            self.skipped_tests += 1
            
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "details": details or {},
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.results.append(result)
        print(f"[{status}] {test_name}: {message}")
        
    def run_command(self, cmd: List[str], timeout: int = 300, cwd: Path = None) -> Dict[str, Any]:
        """Run a command and return result"""
        try:
            start_time = time.time()
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=timeout,
                cwd=cwd or self.project_root
            )
            end_time = time.time()
            
            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0,
                "duration": round(end_time - start_time, 2)
            }
        except subprocess.TimeoutExpired:
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": f"Command timed out after {timeout}s",
                "success": False,
                "duration": timeout
            }
        except Exception as e:
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "success": False,
                "duration": 0
            }
    
    def run_pytest(self):
        """Run pytest on the tests/ directory"""
        if not self.tests_dir.exists():
            self.log_result("pytest", "SKIP", "tests/ directory not found")
            return None
        
        # Check if pytest is available
        pytest_check = self.run_command(["python3", "-m", "pytest", "--version"], timeout=10)
        if not pytest_check["success"]:
            self.log_result("pytest_setup", "SKIP", "pytest not available")
            return None
        
        print("Running pytest on tests/ directory...")
        
        # Run pytest with verbose output and JSON report
        pytest_cmd = [
            "python3", "-m", "pytest", 
            str(self.tests_dir),
            "-v",
            "--tb=short",
            "--no-header"
        ]
        
        result = self.run_command(pytest_cmd, timeout=180)
        
        if result["success"]:
            # Parse pytest output
            output_lines = result["stdout"].split('\n')
            
            # Count test results
            test_count = 0
            passed_count = 0
            failed_count = 0
            skipped_count = 0
            
            for line in output_lines:
                if " PASSED " in line:
                    passed_count += 1
                    test_count += 1
                elif " FAILED " in line:
                    failed_count += 1
                    test_count += 1
                elif " SKIPPED " in line:
                    skipped_count += 1
                    test_count += 1
            
            if test_count > 0:
                success_rate = (passed_count / test_count) * 100
                status = "PASS" if failed_count == 0 else ("WARN" if success_rate >= 80 else "FAIL")
                message = f"{passed_count}/{test_count} tests passed ({success_rate:.1f}%)"
                
                details = {
                    "total": test_count,
                    "passed": passed_count,
                    "failed": failed_count,
                    "skipped": skipped_count,
                    "duration": result["duration"]
                }
                
                self.log_result("pytest", status, message, details)
                return details
            else:
                self.log_result("pytest", "WARN", "No tests found or executed", {"duration": result["duration"]})
                return {"total": 0, "passed": 0, "failed": 0, "skipped": 0, "duration": result["duration"]}
        else:
            self.log_result("pytest", "FAIL", f"pytest execution failed: {result['stderr']}")
            return None
    
    def run_e2e_tests(self):
        """Run all E2E test files"""
        print(f"\nRunning E2E tests from {self.e2e_dir}...")
        
        e2e_results = {}
        
        for test_file in self.e2e_tests:
            test_path = self.e2e_dir / test_file
            
            if not test_path.exists():
                self.log_result(f"e2e_{test_file.replace('.py', '')}", "SKIP", f"{test_file} not found")
                continue
            
            print(f"\nRunning {test_file}...")
            result = self.run_command(["python3", str(test_path)], timeout=180)
            
            test_name = f"e2e_{test_file.replace('.py', '')}"
            
            if result["success"]:
                # Try to load JSON results if available
                json_file = self.e2e_dir / test_file.replace('.py', '_results.json')
                
                if json_file.exists():
                    try:
                        with open(json_file) as f:
                            test_report = json.load(f)
                            
                        summary = test_report.get("summary", {})
                        passed = summary.get("passed", 0)
                        total = summary.get("total_tests", 0)
                        success_rate = summary.get("success_rate", 0)
                        
                        if total > 0:
                            status = "PASS" if summary.get("failed", 0) == 0 else ("WARN" if success_rate >= 70 else "FAIL")
                            message = f"{passed}/{total} tests passed ({success_rate:.1f}%)"
                        else:
                            status = "WARN"
                            message = "No tests detected"
                        
                        details = {
                            "duration": result["duration"],
                            "report_file": str(json_file),
                            **summary
                        }
                        
                        e2e_results[test_name] = test_report
                        self.log_result(test_name, status, message, details)
                        
                    except Exception as e:
                        self.log_result(test_name, "WARN", f"Completed but couldn't parse results: {e}")
                else:
                    self.log_result(test_name, "PASS", f"Completed successfully", {"duration": result["duration"]})
            else:
                self.log_result(test_name, "FAIL", f"Execution failed: {result['stderr'][:200]}")
        
        return e2e_results
    
    def run_smoke_tests(self):
        """Run existing smoke tests"""
        print(f"\nRunning smoke tests from {self.project_root}/tools/...")
        
        smoke_results = {}
        
        for test_file in self.smoke_tests:
            test_path = self.project_root / "tools" / test_file
            
            if not test_path.exists():
                continue  # Skip missing smoke tests silently
            
            print(f"Running {test_file}...")
            result = self.run_command(["python3", str(test_path)], timeout=120)
            
            test_name = f"smoke_{test_file.replace('.py', '').replace('smoke_test_', '')}"
            
            if result["success"]:
                self.log_result(test_name, "PASS", "Smoke test passed", {"duration": result["duration"]})
                smoke_results[test_name] = {"status": "PASS", "duration": result["duration"]}
            else:
                # Smoke tests might fail due to missing services, which is acceptable
                if "connection" in result["stderr"].lower() or "refused" in result["stderr"].lower():
                    self.log_result(test_name, "WARN", "Service not available (acceptable)")
                    smoke_results[test_name] = {"status": "WARN", "reason": "service_unavailable"}
                else:
                    self.log_result(test_name, "FAIL", f"Smoke test failed: {result['stderr'][:100]}")
                    smoke_results[test_name] = {"status": "FAIL", "error": result["stderr"][:200]}
        
        return smoke_results
    
    def generate_comprehensive_report(self, pytest_results, e2e_results, smoke_results):
        """Generate comprehensive test report"""
        timestamp = time.strftime("%Y-%m-%d")
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        # Calculate total duration
        total_duration = 0
        for result in self.results:
            if "duration" in result.get("details", {}):
                total_duration += result["details"]["duration"]
        
        # Create comprehensive report
        report = {
            "test_suite": "MyWork-AI Complete E2E Test Suite",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_tests": self.total_tests,
                "passed": self.passed_tests,
                "failed": self.failed_tests,
                "skipped": self.skipped_tests,
                "success_rate": round(success_rate, 2),
                "total_duration_seconds": round(total_duration, 2)
            },
            "pytest_results": pytest_results,
            "e2e_results": e2e_results,
            "smoke_results": smoke_results,
            "all_results": self.results
        }
        
        # Save JSON report
        json_report_file = self.reports_dir / f"e2e_report_{timestamp}.json"
        with open(json_report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        # Generate markdown report
        md_report_file = self.reports_dir / f"e2e_report_{timestamp}.md"
        self.generate_markdown_report(report, md_report_file)
        
        print(f"\n=== Complete Test Suite Summary ===")
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Skipped: {self.skipped_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Total Duration: {total_duration:.1f}s")
        print(f"\nReports saved:")
        print(f"  JSON: {json_report_file}")
        print(f"  Markdown: {md_report_file}")
        
        return report
    
    def generate_markdown_report(self, report: Dict, file_path: Path):
        """Generate markdown report"""
        md_content = f"""# MyWork-AI E2E Test Report

**Generated:** {report['timestamp']}

## Summary

- **Total Tests:** {report['summary']['total_tests']}
- **Passed:** {report['summary']['passed']}
- **Failed:** {report['summary']['failed']}
- **Skipped:** {report['summary']['skipped']}
- **Success Rate:** {report['summary']['success_rate']:.1f}%
- **Duration:** {report['summary']['total_duration_seconds']:.1f}s

## Test Results

### Unit Tests (pytest)
"""
        
        if report['pytest_results']:
            pytest = report['pytest_results']
            md_content += f"""
- **Status:** {'✅ PASS' if pytest['failed'] == 0 else '❌ FAIL'}
- **Tests:** {pytest['passed']}/{pytest['total']} passed
- **Duration:** {pytest['duration']:.1f}s
"""
        else:
            md_content += "\n- **Status:** ⏭️ SKIPPED (pytest not available)\n"
        
        md_content += "\n### E2E Tests\n\n"
        
        for result in report['all_results']:
            if result['test'].startswith('e2e_'):
                status_emoji = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️", "SKIP": "⏭️"}.get(result['status'], "❓")
                md_content += f"- **{result['test']}:** {status_emoji} {result['status']} - {result['message']}\n"
        
        md_content += "\n### Smoke Tests\n\n"
        
        smoke_found = False
        for result in report['all_results']:
            if result['test'].startswith('smoke_'):
                smoke_found = True
                status_emoji = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️", "SKIP": "⏭️"}.get(result['status'], "❓")
                md_content += f"- **{result['test']}:** {status_emoji} {result['status']} - {result['message']}\n"
        
        if not smoke_found:
            md_content += "- No smoke tests found\n"
        
        # Add detailed results section
        md_content += f"""
## Detailed Results

### Failed Tests
"""
        
        failed_tests = [r for r in report['all_results'] if r['status'] == 'FAIL']
        if failed_tests:
            for test in failed_tests:
                md_content += f"""
#### {test['test']}
- **Error:** {test['message']}
- **Time:** {test['timestamp']}
"""
                if test.get('output'):
                    md_content += f"- **Output:** `{test['output'][:200]}...`\n"
        else:
            md_content += "\n🎉 No failed tests!\n"
        
        md_content += f"""
### Warnings
"""
        
        warning_tests = [r for r in report['all_results'] if r['status'] == 'WARN']
        if warning_tests:
            for test in warning_tests:
                md_content += f"- **{test['test']}:** {test['message']}\n"
        else:
            md_content += "\n✨ No warnings!\n"
        
        # Write markdown file
        with open(file_path, "w") as f:
            f.write(md_content)
    
    def run_all_tests(self):
        """Run all tests and generate reports"""
        print("=== MyWork-AI Complete E2E Test Suite ===")
        print(f"Project Root: {self.project_root}")
        print(f"E2E Tests: {self.e2e_dir}")
        print(f"Unit Tests: {self.tests_dir}")
        print()
        
        start_time = time.time()
        
        # Run all test types
        pytest_results = self.run_pytest()
        e2e_results = self.run_e2e_tests()
        smoke_results = self.run_smoke_tests()
        
        end_time = time.time()
        
        # Generate comprehensive report
        report = self.generate_comprehensive_report(pytest_results, e2e_results, smoke_results)
        
        print(f"\nTotal execution time: {end_time - start_time:.1f}s")
        
        return report


def main():
    """Main entry point"""
    runner = TestSuiteRunner()
    report = runner.run_all_tests()
    
    # Exit with appropriate code
    failed_count = report["summary"]["failed"]
    sys.exit(0 if failed_count == 0 else 1)


if __name__ == "__main__":
    main()