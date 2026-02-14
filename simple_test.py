#!/usr/bin/env python3
"""
Simple Command Test - Focus on Error Handling
"""

import subprocess
import sys
from pathlib import Path

def test_command_help(cmd):
    """Test if command shows help when run with no args or invalid args."""
    print(f"Testing: {cmd}")
    
    # Test no args
    try:
        result = subprocess.run(
            cmd.split(),
            capture_output=True,
            text=True,
            timeout=5,
            cwd="/home/Memo1981/MyWork-AI"
        )
        
        if result.returncode == 0:
            print(f"  ✅ No args: Shows help (exit 0)")
        elif result.returncode == 1:
            print(f"  ✅ No args: Proper error message (exit 1)")
        else:
            print(f"  ⚠️  No args: Exit code {result.returncode}")
            if "traceback" in result.stderr.lower():
                print(f"    ❌ TRACEBACK in stderr!")
                print(f"    Error: {result.stderr[:200]}")
        
    except subprocess.TimeoutExpired:
        print(f"  ⏰ No args: TIMEOUT (hanging command)")
    except Exception as e:
        print(f"  💥 No args: Exception: {e}")
    
    print()

def main():
    print("🧪 Testing basic error handling for GROUP 2 commands\n")
    
    # Focus on commands that should show help, not hang
    quick_commands = [
        "mw ai",
        "mw ai ask",
        "mw ai explain", 
        "mw ai fix",
        "mw brain",
        "mw brain search",
        "mw context",
        "mw lint",
        "mw todo",
        "mw check",
    ]
    
    for cmd in quick_commands:
        test_command_help(cmd)
    
    print("Done! Check for any tracebacks or hanging commands above.")

if __name__ == "__main__":
    main()