#!/usr/bin/env python3
"""
Comprehensive Tour Testing Script
================================
Tests all tour steps by simulating user input
"""

import os
import sys
import subprocess
from pathlib import Path

def test_tour_steps():
    """Test individual tour components without full interactive mode."""
    
    results = {"passed": [], "failed": [], "warnings": []}
    
    print("🧪 Testing MyWork-AI Tour Components...")
    print("=" * 50)
    
    # Test 1: mw status (used in tour step 2)
    print("\n1. Testing: mw status")
    try:
        result = subprocess.run([sys.executable, "-m", "tools.mw", "status"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and ("✅" in result.stdout or "healthy" in result.stdout.lower()):
            results["passed"].append("mw status - works correctly")
            print("   ✅ PASS: mw status works")
        else:
            results["failed"].append(f"mw status - exit code {result.returncode}")
            print(f"   ❌ FAIL: mw status returned {result.returncode}")
    except Exception as e:
        results["failed"].append(f"mw status - exception: {e}")
        print(f"   ❌ ERROR: {e}")

    # Test 2: mw projects (used in tour step 3)
    print("\n2. Testing: mw projects")
    try:
        result = subprocess.run([sys.executable, "-m", "tools.mw", "projects"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            results["passed"].append("mw projects - lists projects successfully")
            print("   ✅ PASS: mw projects works")
            # Check if it shows some projects or a helpful message
            if result.stdout.strip():
                print(f"   📊 Found output: {len(result.stdout.strip().splitlines())} lines")
            else:
                results["warnings"].append("mw projects - no output (might be empty)")
        else:
            results["failed"].append(f"mw projects - exit code {result.returncode}")
            print(f"   ❌ FAIL: mw projects returned {result.returncode}")
    except Exception as e:
        results["failed"].append(f"mw projects - exception: {e}")
        print(f"   ❌ ERROR: {e}")

    # Test 3: mw new (used in tour step 4)  
    print("\n3. Testing: mw new test-tour-project basic")
    try:
        # Create project in /tmp to avoid cluttering
        os.chdir("/tmp")
        result = subprocess.run([sys.executable, "-m", "tools.mw", "new", "test-tour-project", "basic"], 
                              capture_output=True, text=True, timeout=15,
                              cwd="/home/Memo1981/MyWork-AI")
        if result.returncode == 0 and "Project created" in result.stdout:
            results["passed"].append("mw new - creates projects successfully")
            print("   ✅ PASS: mw new creates project")
            # Verify project was actually created
            if Path("/tmp/test-tour-project").exists():
                print("   ✅ Project directory exists")
            else:
                results["warnings"].append("mw new - project directory not found")
        else:
            results["failed"].append(f"mw new - exit code {result.returncode}")
            print(f"   ❌ FAIL: mw new returned {result.returncode}")
            if result.stderr:
                print(f"   📝 Error output: {result.stderr.strip()}")
    except Exception as e:
        results["failed"].append(f"mw new - exception: {e}")
        print(f"   ❌ ERROR: {e}")

    # Test 4: mw brain stats (used in tour step 5)
    print("\n4. Testing: mw brain stats")
    try:
        os.chdir("/home/Memo1981/MyWork-AI")
        result = subprocess.run([sys.executable, "-m", "tools.mw", "brain", "stats"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            results["passed"].append("mw brain stats - shows knowledge vault stats")
            print("   ✅ PASS: mw brain stats works")
        else:
            results["failed"].append(f"mw brain stats - exit code {result.returncode}")
            print(f"   ❌ FAIL: mw brain stats returned {result.returncode}")
    except Exception as e:
        results["failed"].append(f"mw brain stats - exception: {e}")
        print(f"   ❌ ERROR: {e}")

    # Test 5: mw doctor --quick (used in tour step 6)
    print("\n5. Testing: mw doctor --quick")
    try:
        result = subprocess.run([sys.executable, "-m", "tools.mw", "doctor", "--quick"], 
                              capture_output=True, text=True, timeout=20)
        if result.returncode == 0:
            results["passed"].append("mw doctor --quick - runs diagnostics")
            print("   ✅ PASS: mw doctor --quick works")
        else:
            # Doctor might return non-zero for issues, but still be functional
            if "ERROR" not in result.stdout.upper() and "FAILED" not in result.stdout.upper():
                results["warnings"].append("mw doctor --quick - returned non-zero but seems functional")
                print(f"   ⚠️ WARNING: doctor returned {result.returncode} but appears functional")
            else:
                results["failed"].append(f"mw doctor --quick - serious errors detected")
                print(f"   ❌ FAIL: doctor has serious errors")
    except Exception as e:
        results["failed"].append(f"mw doctor --quick - exception: {e}")
        print(f"   ❌ ERROR: {e}")

    # Test 6: Tour help and guidance
    print("\n6. Testing: mw tour --help")
    try:
        result = subprocess.run([sys.executable, "-m", "tools.mw", "tour", "--help"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and "tour" in result.stdout.lower():
            results["passed"].append("mw tour --help - shows help information")
            print("   ✅ PASS: tour help works")
        else:
            results["failed"].append("mw tour --help - no help available")
            print("   ❌ FAIL: tour help not working")
    except Exception as e:
        results["warnings"].append(f"mw tour --help - might not have help: {e}")
        print(f"   ⚠️ WARNING: tour help might not be implemented: {e}")

    # Final Summary
    print("\n" + "=" * 50)
    print("🏁 TOUR TESTING SUMMARY")
    print("=" * 50)
    
    print(f"✅ PASSED ({len(results['passed'])}):")
    for item in results["passed"]:
        print(f"   • {item}")
        
    if results["warnings"]:
        print(f"\n⚠️ WARNINGS ({len(results['warnings'])}):")
        for item in results["warnings"]:
            print(f"   • {item}")
            
    if results["failed"]:
        print(f"\n❌ FAILED ({len(results['failed'])}):")
        for item in results["failed"]:
            print(f"   • {item}")
    else:
        print("\n🎉 All critical tour components are working!")
        
    print(f"\nOverall: {len(results['passed'])} passed, {len(results['warnings'])} warnings, {len(results['failed'])} failed")
    
    return len(results['failed']) == 0

if __name__ == "__main__":
    os.chdir("/home/Memo1981/MyWork-AI")
    success = test_tour_steps()
    sys.exit(0 if success else 1)