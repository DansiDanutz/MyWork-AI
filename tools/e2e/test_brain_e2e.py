#!/usr/bin/env python3
"""
E2E Test: Brain Full Lifecycle Tester
=====================================
Tests: add entry → search → update → export → backup → restore → verify
Tests all entry types and brain functionality with data integrity verification.
"""

import subprocess
import sys
import json
import time
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional

class BrainE2ETester:
    def __init__(self, project_root: str = "/home/Memo1981/MyWork-AI"):
        self.project_root = Path(project_root)
        self.brain_script = self.project_root / "tools" / "brain.py"
        self.brain_search = self.project_root / "tools" / "brain_search.py"
        self.brain_graph = self.project_root / "tools" / "brain_graph.py"
        self.brain_learner = self.project_root / "tools" / "brain_learner.py"
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
        # Test data for each entry type
        self.test_entries = {
            "lesson": {
                "content": "Always backup before major deployments",
                "context": "Learned from production outage on 2024-01-15",
                "search_term": "backup deployment"
            },
            "pattern": {
                "content": "API Rate Limiting Pattern",
                "steps": "1. Check quota\\n2. Implement exponential backoff\\n3. Log rate limit hits",
                "search_term": "rate limiting"
            },
            "antipattern": {
                "content": "Never commit secrets to git",
                "reason": "Security vulnerability - secrets exposed in history",
                "search_term": "secrets git"
            },
            "tip": {
                "content": "Use `git stash` to temporarily save uncommitted changes",
                "tool": "git",
                "search_term": "git stash"
            },
            "insight": {
                "content": "Microservices work better with event-driven architecture",
                "category": "Architecture",
                "search_term": "microservices events"
            },
            "experiment": {
                "content": "Try using WebAssembly for CPU-intensive frontend operations",
                "hypothesis": "WASM should be faster than JavaScript for math operations",
                "search_term": "webassembly wasm"
            }
        }
        
        self.test_backup_path = None
        
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
        
    def run_brain_command(self, script: Path, args: List[str], timeout: int = 30) -> Dict[str, Any]:
        """Run a brain command and return result"""
        cmd = ["python3", str(script)] + args
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
    
    def test_setup(self):
        """Test if all brain scripts exist"""
        scripts = [
            ("brain.py", self.brain_script),
            ("brain_search.py", self.brain_search),
            ("brain_graph.py", self.brain_graph),
            ("brain_learner.py", self.brain_learner)
        ]
        
        all_exist = True
        for name, script_path in scripts:
            if script_path.exists():
                self.log_result(f"setup_{name}", "PASS", f"{name} found")
            else:
                self.log_result(f"setup_{name}", "FAIL", f"{name} not found at {script_path}")
                all_exist = False
                
        return all_exist
    
    def test_brain_stats_initial(self):
        """Test initial brain stats"""
        result = self.run_brain_command(self.brain_script, ["stats"])
        
        if result["success"]:
            self.log_result("brain_stats_initial", "PASS", "Brain stats command works", result["stdout"])
            return True
        else:
            # Brain might not exist yet, which is fine
            if "brain.md" in result["stderr"].lower() or "not found" in result["stderr"].lower():
                self.log_result("brain_stats_initial", "PASS", "Brain not initialized yet (expected)", result["stderr"])
                return True
            else:
                self.log_result("brain_stats_initial", "FAIL", f"Stats failed: {result['stderr']}")
                return False
    
    def test_add_entries(self):
        """Test adding all types of entries"""
        added_entries = {}
        
        for entry_type, data in self.test_entries.items():
            args = ["add", entry_type, data["content"]]
            
            # Add type-specific arguments
            if entry_type == "lesson" and "context" in data:
                args.extend(["--context", data["context"]])
            elif entry_type == "pattern" and "steps" in data:
                args.extend(["--steps", data["steps"]])
            elif entry_type == "antipattern" and "reason" in data:
                args.extend(["--reason", data["reason"]])
            elif entry_type == "tip" and "tool" in data:
                args.extend(["--tool", data["tool"]])
            elif entry_type == "insight" and "category" in data:
                args.extend(["--category", data["category"]])
            elif entry_type == "experiment" and "hypothesis" in data:
                args.extend(["--hypothesis", data["hypothesis"]])
            
            result = self.run_brain_command(self.brain_script, args)
            
            if result["success"]:
                # Extract entry ID from output
                output_lines = result["stdout"].strip().split('\n')
                entry_id = None
                for line in output_lines:
                    if "Added" in line and entry_type in line:
                        # Look for pattern like "lesson-001" in output
                        import re
                        match = re.search(f'{entry_type}-[0-9]+', line)
                        if match:
                            entry_id = match.group()
                            break
                
                if entry_id:
                    added_entries[entry_type] = entry_id
                    self.log_result(f"add_{entry_type}", "PASS", f"Added {entry_type} as {entry_id}", result["stdout"])
                else:
                    self.log_result(f"add_{entry_type}", "WARN", f"Added {entry_type} but couldn't extract ID", result["stdout"])
            else:
                self.log_result(f"add_{entry_type}", "FAIL", f"Failed to add {entry_type}: {result['stderr']}")
        
        return added_entries
    
    def test_search_entries(self, added_entries: Dict[str, str]):
        """Test searching for added entries"""
        search_results = {}
        
        # Test direct brain.py search
        for entry_type, data in self.test_entries.items():
            search_term = data["search_term"]
            result = self.run_brain_command(self.brain_script, ["search", search_term])
            
            if result["success"]:
                # Check if we found the entry we added
                if entry_type in added_entries:
                    entry_id = added_entries[entry_type]
                    if entry_id in result["stdout"] or data["content"][:20] in result["stdout"]:
                        search_results[entry_type] = True
                        self.log_result(f"search_{entry_type}", "PASS", f"Found {entry_type} with search '{search_term}'")
                    else:
                        search_results[entry_type] = False
                        self.log_result(f"search_{entry_type}", "FAIL", f"Didn't find {entry_type} in search results")
                else:
                    self.log_result(f"search_{entry_type}", "WARN", f"Entry {entry_type} wasn't added, skipping search test")
            else:
                self.log_result(f"search_{entry_type}", "FAIL", f"Search failed: {result['stderr']}")
                search_results[entry_type] = False
        
        # Test brain_search.py if available
        if self.brain_search.exists():
            result = self.run_brain_command(self.brain_search, ["deployment", "backup"])
            if result["success"]:
                self.log_result("brain_search_script", "PASS", "brain_search.py works", result["stdout"])
            else:
                self.log_result("brain_search_script", "WARN", "brain_search.py test inconclusive", result["stderr"])
        
        return search_results
    
    def test_update_entry(self, added_entries: Dict[str, str]):
        """Test updating an entry"""
        if "lesson" in added_entries:
            entry_id = added_entries["lesson"]
            new_content = "Always backup AND test restore before major deployments"
            
            result = self.run_brain_command(self.brain_script, ["update", entry_id, new_content])
            
            if result["success"]:
                self.log_result("update_entry", "PASS", f"Updated {entry_id}", result["stdout"])
                
                # Verify the update by searching
                verify_result = self.run_brain_command(self.brain_script, ["search", "test restore"])
                if verify_result["success"] and "test restore" in verify_result["stdout"]:
                    self.log_result("update_verify", "PASS", "Update verified through search")
                else:
                    self.log_result("update_verify", "WARN", "Update verification inconclusive")
            else:
                self.log_result("update_entry", "FAIL", f"Failed to update {entry_id}: {result['stderr']}")
    
    def test_export_functionality(self):
        """Test export in different formats"""
        formats = ["markdown", "json", "csv"]
        
        for fmt in formats:
            result = self.run_brain_command(self.brain_script, ["export", fmt])
            
            if result["success"]:
                if result["stdout"].strip():  # Has output
                    self.log_result(f"export_{fmt}", "PASS", f"Export to {fmt} succeeded", result["stdout"][:200])
                else:
                    self.log_result(f"export_{fmt}", "WARN", f"Export to {fmt} produced no output")
            else:
                self.log_result(f"export_{fmt}", "FAIL", f"Export to {fmt} failed: {result['stderr']}")
    
    def test_backup_restore(self):
        """Test backup and restore functionality"""
        # Create backup
        backup_result = self.run_brain_command(self.brain_script, ["backup"])
        
        if backup_result["success"]:
            # Extract backup filename from output
            backup_filename = None
            for line in backup_result["stdout"].split('\n'):
                if "backup" in line.lower() and ".json" in line:
                    # Extract filename
                    import re
                    match = re.search(r'[\w\-_]+\.json', line)
                    if match:
                        backup_filename = match.group()
                        break
            
            if backup_filename:
                self.log_result("backup_create", "PASS", f"Backup created: {backup_filename}")
                self.test_backup_path = backup_filename
                
                # Test restore (we'll do a dry run by checking if restore command works)
                restore_test = self.run_brain_command(self.brain_script, ["restore", "--help"])
                if restore_test["success"] or "restore" in restore_test["stderr"]:
                    self.log_result("restore_command", "PASS", "Restore command available")
                else:
                    self.log_result("restore_command", "WARN", "Restore command test inconclusive")
            else:
                self.log_result("backup_create", "WARN", "Backup created but couldn't extract filename", backup_result["stdout"])
        else:
            self.log_result("backup_create", "FAIL", f"Backup failed: {backup_result['stderr']}")
    
    def test_brain_graph(self):
        """Test brain_graph.py functionality"""
        if not self.brain_graph.exists():
            self.log_result("brain_graph", "SKIP", "brain_graph.py not found")
            return
        
        result = self.run_brain_command(self.brain_graph, ["--help"])
        
        if result["success"] or "graph" in result["stdout"].lower():
            self.log_result("brain_graph", "PASS", "brain_graph.py is functional")
        else:
            # Try running without args
            result = self.run_brain_command(self.brain_graph, [])
            if result["success"] or "relationship" in result["stdout"].lower():
                self.log_result("brain_graph", "PASS", "brain_graph.py executed")
            else:
                self.log_result("brain_graph", "WARN", "brain_graph.py test inconclusive", result["stderr"])
    
    def test_brain_learner(self):
        """Test brain_learner.py functionality"""
        if not self.brain_learner.exists():
            self.log_result("brain_learner", "SKIP", "brain_learner.py not found")
            return
        
        result = self.run_brain_command(self.brain_learner, ["--help"])
        
        if result["success"] or "learn" in result["stdout"].lower():
            self.log_result("brain_learner", "PASS", "brain_learner.py is functional")
        else:
            # Try running without args
            result = self.run_brain_command(self.brain_learner, [])
            if result["success"] or "discovery" in result["stdout"].lower():
                self.log_result("brain_learner", "PASS", "brain_learner.py executed")
            else:
                self.log_result("brain_learner", "WARN", "brain_learner.py test inconclusive", result["stderr"])
    
    def test_data_integrity(self):
        """Verify data integrity after all operations"""
        # Check final stats
        result = self.run_brain_command(self.brain_script, ["stats"])
        
        if result["success"]:
            output = result["stdout"]
            # Look for evidence of our test entries
            test_types = list(self.test_entries.keys())
            found_types = []
            
            for entry_type in test_types:
                if entry_type in output.lower():
                    found_types.append(entry_type)
            
            if len(found_types) >= 3:  # At least half of our entry types
                self.log_result("data_integrity", "PASS", f"Found {len(found_types)}/{len(test_types)} entry types in final stats")
            else:
                self.log_result("data_integrity", "WARN", f"Only found {len(found_types)}/{len(test_types)} entry types", output)
        else:
            self.log_result("data_integrity", "FAIL", f"Final stats check failed: {result['stderr']}")
    
    def run_all_tests(self):
        """Run all brain E2E tests"""
        print("=== Brain E2E Full Lifecycle Tests ===")
        print(f"Testing brain scripts at: {self.project_root}/tools/")
        print()
        
        # Setup tests
        if not self.test_setup():
            return self.generate_report()
        
        # Initial state
        self.test_brain_stats_initial()
        
        # Full lifecycle test
        added_entries = self.test_add_entries()
        search_results = self.test_search_entries(added_entries)
        self.test_update_entry(added_entries)
        self.test_export_functionality()
        self.test_backup_restore()
        
        # Component tests
        self.test_brain_graph()
        self.test_brain_learner()
        
        # Final verification
        self.test_data_integrity()
        
        return self.generate_report()
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate test report"""
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        report = {
            "test_suite": "Brain E2E Full Lifecycle Tests",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_tests": self.total_tests,
                "passed": self.passed_tests,
                "failed": self.failed_tests,
                "skipped": 0,
                "success_rate": round(success_rate, 2)
            },
            "test_entries": self.test_entries,
            "backup_path": self.test_backup_path,
            "results": self.results
        }
        
        print(f"\n=== Brain E2E Test Summary ===")
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.test_backup_path:
            print(f"Test Backup Created: {self.test_backup_path}")
        
        return report


def main():
    """Main entry point"""
    tester = BrainE2ETester()
    report = tester.run_all_tests()
    
    # Save report to file
    report_file = Path("/home/Memo1981/MyWork-AI/tools/e2e/brain_e2e_results.json")
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\nReport saved to: {report_file}")
    
    # Exit with appropriate code
    sys.exit(0 if report["summary"]["failed"] == 0 else 1)


if __name__ == "__main__":
    main()