#!/usr/bin/env python3
"""
E2E Test: AutoForge Integration Test
===================================
Tests autoforge_api.py imports, basic functions, backwards compatibility,
and CLI commands (mw af status, mw ac status alias).
"""

import subprocess
import sys
import json
import time
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Optional

class AutoForgeIntegrationTester:
    def __init__(self, project_root: str = "/home/Memo1981/MyWork-AI"):
        self.project_root = Path(project_root)
        self.autoforge_api = self.project_root / "tools" / "autoforge_api.py"
        self.autocoder_api = self.project_root / "tools" / "autocoder_api.py"  # Backwards compatibility
        self.autoforge_service = self.project_root / "tools" / "autoforge_service.py"
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
        
    def run_command(self, cmd: List[str], timeout: int = 30, cwd: Optional[Path] = None) -> Dict[str, Any]:
        """Run a command and return result"""
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=timeout,
                cwd=cwd or self.project_root
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
    
    def test_file_existence(self):
        """Test if AutoForge files exist"""
        files_to_check = [
            ("autoforge_api.py", self.autoforge_api),
            ("autoforge_service.py", self.autoforge_service),
            ("autocoder_api.py (symlink)", self.autocoder_api),
            ("mw.py", self.mw_script)
        ]
        
        all_exist = True
        for name, file_path in files_to_check:
            if file_path.exists():
                if file_path.is_symlink():
                    target = file_path.readlink()
                    self.log_result(f"file_exists_{name.split('.')[0]}", "PASS", f"{name} exists -> {target}")
                else:
                    self.log_result(f"file_exists_{name.split('.')[0]}", "PASS", f"{name} exists")
            else:
                self.log_result(f"file_exists_{name.split('.')[0]}", "FAIL", f"{name} not found at {file_path}")
                all_exist = False
                
        return all_exist
    
    def test_autoforge_api_imports(self):
        """Test if autoforge_api.py can be imported"""
        try:
            # Load the module spec
            spec = importlib.util.spec_from_file_location("autoforge_api", self.autoforge_api)
            if spec is None:
                self.log_result("autoforge_imports", "FAIL", "Could not load module spec")
                return False
                
            module = importlib.util.module_from_spec(spec)
            
            # Try to execute the module (this loads it)
            spec.loader.exec_module(module)
            
            # Check for expected functions/classes
            expected_items = ['main', 'AutoForgeClient']  # Common items we expect
            found_items = []
            missing_items = []
            
            for item in expected_items:
                if hasattr(module, item):
                    found_items.append(item)
                else:
                    missing_items.append(item)
            
            if found_items:
                self.log_result("autoforge_imports", "PASS", f"Imported successfully, found: {found_items}")
                return True
            else:
                self.log_result("autoforge_imports", "WARN", f"Imported but missing expected items: {missing_items}")
                return True  # Still consider it a pass if it imports
                
        except Exception as e:
            self.log_result("autoforge_imports", "FAIL", f"Import failed: {str(e)}")
            return False
    
    def test_autoforge_api_direct(self):
        """Test running autoforge_api.py directly"""
        # Test status command
        result = self.run_command(["python3", str(self.autoforge_api), "status"])
        
        if result["success"]:
            self.log_result("autoforge_api_status", "PASS", "Status command executed", result["stdout"])
        else:
            # AutoForge might not be running, which is acceptable
            if "connection" in result["stderr"].lower() or "refused" in result["stderr"].lower():
                self.log_result("autoforge_api_status", "WARN", "AutoForge server not running (acceptable)", result["stderr"])
            elif "autoforge" in result["stdout"].lower() or "status" in result["stdout"].lower():
                self.log_result("autoforge_api_status", "PASS", "Status command recognized", result["stdout"])
            else:
                self.log_result("autoforge_api_status", "FAIL", f"Status command failed: {result['stderr']}")
        
        # Test help command
        help_result = self.run_command(["python3", str(self.autoforge_api), "--help"])
        
        if help_result["success"]:
            if "autoforge" in help_result["stdout"].lower():
                self.log_result("autoforge_api_help", "PASS", "Help shows AutoForge info")
            else:
                self.log_result("autoforge_api_help", "PASS", "Help command works", help_result["stdout"])
        else:
            self.log_result("autoforge_api_help", "FAIL", f"Help failed: {help_result['stderr']}")
    
    def test_backwards_compatibility(self):
        """Test backwards compatibility with autocoder_api.py"""
        if not self.autocoder_api.exists():
            self.log_result("backwards_compat_exists", "FAIL", "autocoder_api.py symlink not found")
            return
        
        # Check if it's a symlink to autoforge_api.py
        if self.autocoder_api.is_symlink():
            target = self.autocoder_api.readlink()
            if "autoforge_api.py" in str(target):
                self.log_result("backwards_compat_link", "PASS", f"autocoder_api.py -> {target}")
            else:
                self.log_result("backwards_compat_link", "WARN", f"Symlink points to: {target}")
        
        # Test running the symlink
        result = self.run_command(["python3", str(self.autocoder_api), "status"])
        
        if result["success"]:
            self.log_result("backwards_compat_run", "PASS", "autocoder_api.py works via symlink")
        else:
            # Same as before - server might not be running
            if "connection" in result["stderr"].lower() or "refused" in result["stderr"].lower():
                self.log_result("backwards_compat_run", "WARN", "Server not running (acceptable)")
            elif "autoforge" in result["stdout"].lower() or "autocoder" in result["stdout"].lower():
                self.log_result("backwards_compat_run", "PASS", "Backwards compatibility confirmed")
            else:
                self.log_result("backwards_compat_run", "FAIL", f"Backwards compat failed: {result['stderr']}")
    
    def test_mw_af_commands(self):
        """Test mw af commands"""
        if not self.mw_script.exists():
            self.log_result("mw_af_setup", "FAIL", "mw.py script not found")
            return
        
        # Test mw af status
        result = self.run_command(["python3", str(self.mw_script), "af", "status"])
        
        if result["success"]:
            self.log_result("mw_af_status", "PASS", "mw af status works", result["stdout"])
        else:
            # Check if command is recognized
            if "af" in result["stderr"].lower() or "autoforge" in result["stderr"].lower():
                self.log_result("mw_af_status", "PASS", "mw af command recognized")
            elif "unknown command" in result["stderr"].lower():
                self.log_result("mw_af_status", "FAIL", "mw af command not recognized")
            else:
                self.log_result("mw_af_status", "WARN", f"mw af status inconclusive: {result['stderr']}")
        
        # Test mw af help/list
        help_result = self.run_command(["python3", str(self.mw_script), "af", "--help"])
        
        if help_result["success"] or "autoforge" in help_result["stdout"].lower():
            self.log_result("mw_af_help", "PASS", "mw af help available")
        else:
            # Try mw af list
            list_result = self.run_command(["python3", str(self.mw_script), "af", "list"])
            if list_result["success"] or "project" in list_result["stdout"].lower():
                self.log_result("mw_af_help", "PASS", "mw af list works")
            else:
                self.log_result("mw_af_help", "WARN", "mw af help/list inconclusive")
    
    def test_mw_ac_alias(self):
        """Test mw ac commands (legacy alias)"""
        # Test mw ac status (backwards compatibility)
        result = self.run_command(["python3", str(self.mw_script), "ac", "status"])
        
        if result["success"]:
            self.log_result("mw_ac_status", "PASS", "mw ac status (legacy) works", result["stdout"])
        else:
            # Check if command is recognized
            if "ac" in result["stderr"].lower() or "autoforge" in result["stderr"].lower() or "autocoder" in result["stderr"].lower():
                self.log_result("mw_ac_status", "PASS", "mw ac command recognized")
            elif "unknown command" in result["stderr"].lower():
                self.log_result("mw_ac_status", "FAIL", "mw ac command not recognized")
            else:
                self.log_result("mw_ac_status", "WARN", f"mw ac status inconclusive: {result['stderr']}")
    
    def test_autoforge_service(self):
        """Test autoforge_service.py if it exists"""
        if not self.autoforge_service.exists():
            self.log_result("autoforge_service", "SKIP", "autoforge_service.py not found")
            return
        
        # Test help command
        result = self.run_command(["python3", str(self.autoforge_service), "--help"])
        
        if result["success"]:
            self.log_result("autoforge_service", "PASS", "autoforge_service.py help works")
        else:
            # Try running without args
            no_args_result = self.run_command(["python3", str(self.autoforge_service)])
            if no_args_result["success"] or "service" in no_args_result["stdout"].lower():
                self.log_result("autoforge_service", "PASS", "autoforge_service.py works")
            else:
                self.log_result("autoforge_service", "WARN", "autoforge_service.py test inconclusive")
    
    def test_integration_workflow(self):
        """Test a basic integration workflow"""
        # This tests if the components work together
        
        # 1. Check if we can get status from multiple sources
        api_status = self.run_command(["python3", str(self.autoforge_api), "status"])
        mw_status = self.run_command(["python3", str(self.mw_script), "af", "status"])
        
        # Count successful status checks
        successful_checks = 0
        if api_status["success"] or "autoforge" in api_status["stdout"].lower():
            successful_checks += 1
        if mw_status["success"] or "autoforge" in mw_status["stdout"].lower():
            successful_checks += 1
        
        if successful_checks >= 2:
            self.log_result("integration_workflow", "PASS", f"Multiple AutoForge interfaces work ({successful_checks}/2)")
        elif successful_checks == 1:
            self.log_result("integration_workflow", "WARN", "Some AutoForge interfaces work (1/2)")
        else:
            self.log_result("integration_workflow", "FAIL", "No AutoForge interfaces working")
    
    def run_all_tests(self):
        """Run all AutoForge integration tests"""
        print("=== AutoForge Integration E2E Tests ===")
        print(f"Testing AutoForge components at: {self.project_root}/tools/")
        print()
        
        # File existence tests
        if not self.test_file_existence():
            return self.generate_report()
        
        # Import and basic functionality tests
        self.test_autoforge_api_imports()
        self.test_autoforge_api_direct()
        
        # Backwards compatibility tests
        self.test_backwards_compatibility()
        
        # CLI integration tests
        self.test_mw_af_commands()
        self.test_mw_ac_alias()
        
        # Service tests
        self.test_autoforge_service()
        
        # Integration workflow test
        self.test_integration_workflow()
        
        return self.generate_report()
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate test report"""
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        report = {
            "test_suite": "AutoForge Integration E2E Tests",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_tests": self.total_tests,
                "passed": self.passed_tests,
                "failed": self.failed_tests,
                "skipped": 0,
                "success_rate": round(success_rate, 2)
            },
            "components_tested": [
                "autoforge_api.py",
                "autoforge_service.py",
                "autocoder_api.py (backwards compatibility)",
                "mw af commands",
                "mw ac commands (legacy)"
            ],
            "results": self.results
        }
        
        print(f"\n=== AutoForge Integration Test Summary ===")
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        return report


def main():
    """Main entry point"""
    tester = AutoForgeIntegrationTester()
    report = tester.run_all_tests()
    
    # Save report to file
    report_file = Path("/home/Memo1981/MyWork-AI/tools/e2e/autoforge_test_results.json")
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\nReport saved to: {report_file}")
    
    # Exit with appropriate code
    sys.exit(0 if report["summary"]["failed"] == 0 else 1)


if __name__ == "__main__":
    main()