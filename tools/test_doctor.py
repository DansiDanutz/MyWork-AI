#!/usr/bin/env python3
"""
Test Doctor — Find and fix hanging/broken tests
================================================
Runs each test file individually with a timeout to identify
which tests hang, crash, or fail.

Usage:
    python3 test_doctor.py                  # Scan all tests
    python3 test_doctor.py --timeout 10     # Custom timeout per file
    python3 test_doctor.py --fix            # Auto-skip hanging tests
    python3 test_doctor.py --report         # Generate JSON report
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

try:
    from config import MYWORK_ROOT
except ImportError:
    def _get_mywork_root() -> Path:
        if env_root := os.environ.get("MYWORK_ROOT"):
            return Path(env_root)
        script_dir = Path(__file__).resolve().parent
        if script_dir.name == "tools":
            return script_dir.parent
        return Path.home() / "MyWork"
    MYWORK_ROOT = _get_mywork_root()


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    DIM = "\033[90m"
    END = "\033[0m"


def run_test_file(test_file: Path, timeout: int = 8) -> Dict[str, Any]:
    """Run a single test file and return results."""
    start = time.time()
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(test_file), "-x", "--timeout=5", "-q", "--tb=line"],
            capture_output=True, text=True, timeout=timeout,
            cwd=str(MYWORK_ROOT)
        )
        elapsed = time.time() - start
        output = result.stdout + result.stderr
        
        # Parse results
        if result.returncode == 0:
            # Count passed
            for line in output.split("\n"):
                if "passed" in line:
                    import re
                    m = re.search(r"(\d+) passed", line)
                    count = int(m.group(1)) if m else 0
                    return {"status": "passed", "tests": count, "time": elapsed, "output": ""}
            return {"status": "passed", "tests": 0, "time": elapsed, "output": ""}
        elif result.returncode == 5:
            return {"status": "no_tests", "tests": 0, "time": elapsed, "output": ""}
        else:
            # Extract failure info
            failures = []
            for line in output.split("\n"):
                if "FAILED" in line or "ERROR" in line:
                    failures.append(line.strip())
            return {"status": "failed", "tests": 0, "time": elapsed, "output": "\n".join(failures[-3:])}
    
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start
        return {"status": "hanging", "tests": 0, "time": elapsed, "output": f"Timed out after {timeout}s"}


def scan_tests(timeout: int = 8, report: bool = False, fix: bool = False) -> Dict[str, Any]:
    """Scan all test files and categorize them."""
    tests_dir = MYWORK_ROOT / "tests"
    if not tests_dir.exists():
        print(f"{Colors.RED}No tests/ directory found{Colors.END}")
        return {}
    
    test_files = sorted(tests_dir.glob("test_*.py"))
    total = len(test_files)
    
    print(f"{Colors.BOLD}🩺 Test Doctor — Scanning {total} test files{Colors.END}")
    print(f"{Colors.DIM}   Timeout: {timeout}s per file{Colors.END}\n")
    
    results = {"passed": [], "failed": [], "hanging": [], "no_tests": [], "errors": []}
    total_tests = 0
    
    for i, tf in enumerate(test_files, 1):
        name = tf.name
        print(f"  [{i:3d}/{total}] {name:45s} ", end="", flush=True)
        
        r = run_test_file(tf, timeout)
        status = r["status"]
        
        if status == "passed":
            total_tests += r["tests"]
            print(f"{Colors.GREEN}✓ {r['tests']:3d} tests ({r['time']:.1f}s){Colors.END}")
            results["passed"].append(name)
        elif status == "no_tests":
            print(f"{Colors.DIM}  — no tests{Colors.END}")
            results["no_tests"].append(name)
        elif status == "hanging":
            print(f"{Colors.RED}⏰ HANGING (>{timeout}s){Colors.END}")
            results["hanging"].append(name)
        elif status == "failed":
            print(f"{Colors.YELLOW}✗ FAILED{Colors.END}")
            if r["output"]:
                for line in r["output"].split("\n")[:2]:
                    print(f"      {Colors.DIM}{line}{Colors.END}")
            results["failed"].append({"file": name, "output": r["output"]})
    
    # Summary
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}📊 Summary{Colors.END}")
    print(f"  {Colors.GREEN}✓ Passed:  {len(results['passed']):3d} files ({total_tests} tests){Colors.END}")
    print(f"  {Colors.YELLOW}✗ Failed:  {len(results['failed']):3d} files{Colors.END}")
    print(f"  {Colors.RED}⏰ Hanging: {len(results['hanging']):3d} files{Colors.END}")
    print(f"  {Colors.DIM}  Empty:   {len(results['no_tests']):3d} files{Colors.END}")
    
    if results["hanging"]:
        print(f"\n{Colors.RED}{Colors.BOLD}🚨 Hanging Tests:{Colors.END}")
        for name in results["hanging"]:
            print(f"  • {name}")
        if fix:
            print(f"\n{Colors.YELLOW}Generating skip markers...{Colors.END}")
            _generate_skip_conftest(results["hanging"])
    
    if results["failed"]:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  Failed Tests:{Colors.END}")
        for item in results["failed"]:
            print(f"  • {item['file']}")
    
    if report:
        report_path = MYWORK_ROOT / ".tmp" / "test_doctor_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "total_files": total,
            "total_tests": total_tests,
            "passed_files": len(results["passed"]),
            "failed_files": len(results["failed"]),
            "hanging_files": len(results["hanging"]),
            "empty_files": len(results["no_tests"]),
            "hanging": results["hanging"],
            "failed": [f["file"] if isinstance(f, dict) else f for f in results["failed"]],
        }
        report_path.write_text(json.dumps(report_data, indent=2))
        print(f"\n{Colors.BLUE}📄 Report saved: {report_path}{Colors.END}")
    
    return results


def _generate_skip_conftest(hanging_files: List[str]):
    """Generate a conftest snippet to skip hanging tests."""
    print("\nAdd to conftest.py to skip hanging tests:")
    print(f"{Colors.DIM}# Auto-generated by test_doctor.py{Colors.END}")
    for name in hanging_files:
        module = name.replace(".py", "")
        print(f'collect_ignore_glob = ["{name}"]  # hanging')


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Test Doctor — find hanging/broken tests")
    parser.add_argument("--timeout", type=int, default=8, help="Timeout per test file (default: 8s)")
    parser.add_argument("--report", action="store_true", help="Generate JSON report")
    parser.add_argument("--fix", action="store_true", help="Generate skip markers for hanging tests")
    args = parser.parse_args()
    
    scan_tests(timeout=args.timeout, report=args.report, fix=args.fix)


if __name__ == "__main__":
    main()
