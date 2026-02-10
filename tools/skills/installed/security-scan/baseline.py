#!/usr/bin/env python3
"""
Security Scan Skill - Baseline Management
========================================
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

def main():
    """Update security baseline."""
    print("📋 Updating security baseline...")
    
    # Run scan to get current findings
    scan_script = Path(__file__).parent / "scan.py"
    result = subprocess.run([sys.executable, str(scan_script), "."], 
                          capture_output=True, text=True)
    
    # Save as baseline
    baseline_path = Path(".security_baseline.json")
    baseline_data = {
        "timestamp": datetime.now().isoformat(),
        "scan_output": result.stdout,
        "return_code": result.returncode,
        "note": "Security baseline - findings below this line are considered acceptable"
    }
    
    with open(baseline_path, 'w') as f:
        json.dump(baseline_data, f, indent=2)
    
    print(f"✅ Security baseline saved to: {baseline_path}")
    print("💡 Future scans will only show new issues")
    return 0

if __name__ == '__main__':
    sys.exit(main())