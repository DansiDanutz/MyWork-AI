#!/usr/bin/env python3
"""
Comprehensive Command Testing for MyWork-AI
===========================================
Tests all GROUP 2 Dev Tools commands systematically.
"""

import subprocess
import sys
import time
import json
from pathlib import Path

# GROUP 2 - Dev Tools Commands to test
COMMANDS_TO_TEST = [
    # AI Commands
    "mw ai",
    "mw ai ask",
    "mw ai explain",
    "mw ai fix", 
    "mw ai refactor",
    "mw ai test",
    "mw ai commit",
    "mw ai review",
    "mw ai doc",
    "mw ai changelog",
    "mw ai optimize",
    "mw ai refactor-static",
    "mw ai generate",
    "mw ai chat",
    "mw ai providers",
    "mw ai models",
    
    # Brain Commands
    "mw brain",
    "mw brain list",
    "mw brain search",
    "mw brain add",
    "mw brain export",
    
    # Other Dev Tools
    "mw context",
    "mw ctx",
    "mw todo",
    "mw lint",
    "mw test",
    "mw watch",
    "mw pair", 
    "mw check",
]

class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

def test_command(command, test_type, extra_args=None):
    """Test a command with different scenarios."""
    full_cmd = command.split()
    if extra_args:
        full_cmd.extend(extra_args)
    
    print(f"  {Colors.CYAN}Testing: {' '.join(full_cmd)} ({test_type}){Colors.RESET}")
    
    try:
        # Use timeout to prevent hanging
        result = subprocess.run(
            full_cmd,
            capture_output=True,
            text=True,
            timeout=10,
            cwd="/home/Memo1981/MyWork-AI"
        )
        
        return {
            "command": ' '.join(full_cmd),
            "test_type": test_type,
            "returncode": result.returncode,
            "stdout": result.stdout[:500] if result.stdout else "",  # Truncate long output
            "stderr": result.stderr[:500] if result.stderr else "",
            "status": "completed",
            "timeout": False
        }
    except subprocess.TimeoutExpired:
        return {
            "command": ' '.join(full_cmd),
            "test_type": test_type,
            "returncode": -1,
            "stdout": "",
            "stderr": "TIMEOUT",
            "status": "timeout",
            "timeout": True
        }
    except Exception as e:
        return {
            "command": ' '.join(full_cmd),
            "test_type": test_type,
            "returncode": -2,
            "stdout": "",
            "stderr": str(e),
            "status": "exception",
            "timeout": False
        }

def main():
    """Run comprehensive command testing."""
    print(f"{Colors.BOLD}{Colors.BLUE}🧪 MyWork-AI Comprehensive Command Testing{Colors.RESET}")
    print(f"{Colors.BLUE}Testing {len(COMMANDS_TO_TEST)} commands with multiple scenarios{Colors.RESET}\n")
    
    results = []
    failed_commands = []
    
    for command in COMMANDS_TO_TEST:
        print(f"{Colors.BOLD}{Colors.YELLOW}Testing: {command}{Colors.RESET}")
        
        # Test 1: No arguments
        result1 = test_command(command, "no_args")
        results.append(result1)
        
        # Test 2: --help
        result2 = test_command(command, "help", ["--help"])
        results.append(result2)
        
        # Test 3: Invalid arguments (for subcommands that take args)
        if any(subcmd in command for subcmd in ["ask", "explain", "fix", "search", "add"]):
            if "ask" in command:
                result3 = test_command(command, "invalid_args", [""])
            elif "explain" in command or "fix" in command:
                result3 = test_command(command, "invalid_args", ["nonexistent_file.txt"])
            elif "search" in command:
                result3 = test_command(command, "invalid_args", [])
            elif "add" in command:
                result3 = test_command(command, "invalid_args", [])
            else:
                result3 = test_command(command, "invalid_args", ["invalid_argument_123"])
            results.append(result3)
        
        # Check for failures
        if any(r["returncode"] not in [0, 1] or r["timeout"] or "traceback" in r["stderr"].lower() 
               for r in [result1, result2] + ([result3] if 'result3' in locals() else [])):
            failed_commands.append(command)
            print(f"    {Colors.RED}❌ Issues found{Colors.RESET}")
        else:
            print(f"    {Colors.GREEN}✅ Basic tests passed{Colors.RESET}")
        
        print()
        
        # Small delay to avoid overwhelming the system
        time.sleep(0.1)
    
    # Summary
    print(f"\n{Colors.BOLD}{Colors.BLUE}📊 Test Results Summary{Colors.RESET}")
    print(f"Commands tested: {len(COMMANDS_TO_TEST)}")
    print(f"Failed commands: {len(failed_commands)}")
    
    if failed_commands:
        print(f"\n{Colors.RED}❌ Commands with issues:{Colors.RESET}")
        for cmd in failed_commands:
            print(f"  - {cmd}")
    
    # Detailed failure analysis
    print(f"\n{Colors.BOLD}{Colors.YELLOW}🔍 Detailed Issues{Colors.RESET}")
    
    for result in results:
        if (result["returncode"] not in [0, 1] or 
            result["timeout"] or 
            "traceback" in result["stderr"].lower() or
            "syntaxerror" in result["stderr"].lower()):
            
            status_icon = "⏰" if result["timeout"] else "💥" if "traceback" in result["stderr"].lower() else "❌"
            print(f"\n{status_icon} {result['command']} ({result['test_type']})")
            print(f"    Return code: {result['returncode']}")
            if result["stderr"]:
                print(f"    Error: {result['stderr'][:200]}...")
            if result["timeout"]:
                print(f"    {Colors.YELLOW}TIMEOUT: Command took >10 seconds{Colors.RESET}")
    
    # Save detailed results
    results_file = Path("test_results.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n{Colors.CYAN}📄 Detailed results saved to: {results_file}{Colors.RESET}")
    
    return len(failed_commands)

if __name__ == "__main__":
    failed_count = main()
    sys.exit(failed_count)