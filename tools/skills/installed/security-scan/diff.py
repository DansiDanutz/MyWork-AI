#!/usr/bin/env python3
"""
Security Scan Skill - Diff Scanner  
=================================
Show only new security issues since last baseline.
"""

import json
import subprocess
import sys
from pathlib import Path

def main():
    """Show security diff since baseline."""
    baseline_path = Path(".security_baseline.json")
    
    if not baseline_path.exists():
        print("❌ No security baseline found. Run: mw skills run security-scan baseline")
        return 1
    
    print("🔍 Scanning for new security issues...")
    
    # Load baseline
    with open(baseline_path) as f:
        baseline = json.load(f)
    
    # Run current scan
    scan_script = Path(__file__).parent / "scan.py"
    result = subprocess.run([sys.executable, str(scan_script), "."], 
                          capture_output=True, text=True)
    
    print(f"\n📊 Security Diff Report")
    print("=" * 50)
    print(f"Baseline from: {baseline.get('timestamp', 'unknown')}")
    print(f"Current scan: {Path.cwd()}")
    
    # Simple diff (in a real implementation, we'd parse and compare findings)
    if result.stdout == baseline.get('scan_output', ''):
        print("✅ No new security issues since baseline")
        return 0
    else:
        print("🔴 New security issues detected!")
        print("\nCurrent scan output:")
        print(result.stdout)
        return 1

if __name__ == '__main__':
    sys.exit(main())