#!/usr/bin/env python3
"""
Code Review Skill - Report Generator
===================================
Generate detailed code review reports in various formats.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

def generate_report(format_type: str = "text"):
    """Generate code review report."""
    # Run review to get data
    reviewer_script = Path(__file__).parent / "review.py"
    result = subprocess.run([sys.executable, str(reviewer_script), "."], 
                          capture_output=True, text=True)
    
    # For now, just show the output
    if format_type == "json":
        print('{"status": "report_generated", "format": "json", "timestamp": "' + 
              datetime.now().isoformat() + '"}')
    elif format_type == "html":
        print(f"""
<!DOCTYPE html>
<html>
<head>
    <title>Code Review Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
        .issue {{ margin: 10px 0; padding: 10px; border-left: 4px solid #ddd; }}
        .critical {{ border-left-color: #d32f2f; }}
        .high {{ border-left-color: #f57c00; }}
        .medium {{ border-left-color: #fbc02d; }}
        .low {{ border-left-color: #388e3c; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Code Review Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    <div class="content">
        {result.stdout}
    </div>
</body>
</html>
""")
    else:
        print("📄 Code Review Report")
        print("=" * 50)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        print(result.stdout)

def main():
    """Main report function."""
    format_type = sys.argv[1] if len(sys.argv) > 1 else "text"
    
    if format_type not in ["text", "json", "html"]:
        print("❌ Invalid format. Use: text, json, or html")
        return 1
        
    generate_report(format_type)
    return 0

if __name__ == '__main__':
    sys.exit(main())