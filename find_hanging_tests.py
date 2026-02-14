#!/usr/bin/env python3
"""Find hanging tests by running each one individually."""

import subprocess
import sys
from pathlib import Path
import glob
import time

def test_file(test_file):
    """Test a single file with timeout."""
    print(f"Testing {test_file}...", end=" ", flush=True)
    
    try:
        start = time.time()
        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_file, "-q", "--tb=short", "--timeout=5"],
            capture_output=True,
            text=True,
            timeout=10,  # Hard timeout
            cwd="/home/Memo1981/MyWork-AI"
        )
        duration = time.time() - start
        
        if result.returncode == 0:
            print(f"✅ PASS ({duration:.1f}s)")
            return "pass"
        else:
            print(f"❌ FAIL ({duration:.1f}s)")
            return "fail"
            
    except subprocess.TimeoutExpired:
        print(f"🔥 HANG (>10s)")
        return "hang"
    except Exception as e:
        print(f"💥 ERROR: {e}")
        return "error"

if __name__ == "__main__":
    test_files = sorted(glob.glob("/home/Memo1981/MyWork-AI/tests/test_*.py"))
    
    passed = []
    failed = []
    hanging = []
    errors = []
    
    for test_file_path in test_files:
        result = test_file(test_file_path)
        
        if result == "pass":
            passed.append(test_file)
        elif result == "fail":
            failed.append(test_file)
        elif result == "hang":
            hanging.append(test_file)
        else:
            errors.append(test_file)
    
    print(f"\n📊 RESULTS:")
    print(f"✅ Passed: {len(passed)}")
    print(f"❌ Failed: {len(failed)}")  
    print(f"🔥 Hanging: {len(hanging)}")
    print(f"💥 Errors: {len(errors)}")
    
    if hanging:
        print(f"\n🔥 Hanging tests to remove:")
        for test in hanging:
            print(f"  {Path(test).name}")