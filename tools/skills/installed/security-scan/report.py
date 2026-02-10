#!/usr/bin/env python3
"""
Security Scan Skill - Report Generator
=====================================
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

def generate_report(format_type: str = "json"):
    """Generate security report in specified format."""
    # Run scan
    scan_script = Path(__file__).parent / "scan.py"
    result = subprocess.run([sys.executable, str(scan_script), "."], 
                          capture_output=True, text=True)
    
    if format_type == "sarif":
        # SARIF format for integration with tools like GitHub
        sarif_report = {
            "version": "2.1.0",
            "$schema": "https://schemastore.azurewebsites.net/schemas/json/sarif-2.1.0.json",
            "runs": [{
                "tool": {
                    "driver": {
                        "name": "MyWork-AI Security Scanner",
                        "version": "1.0.0"
                    }
                },
                "results": [],
                "invocations": [{
                    "executionSuccessful": result.returncode == 0,
                    "endTimeUtc": datetime.now().isoformat()
                }]
            }]
        }
        print(json.dumps(sarif_report, indent=2))
        
    elif format_type == "html":
        print(f"""
<!DOCTYPE html>
<html>
<head>
    <title>Security Scan Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
        .critical {{ background: #ffebee; border-left: 4px solid #d32f2f; padding: 10px; margin: 10px 0; }}
        .high {{ background: #fff3e0; border-left: 4px solid #f57c00; padding: 10px; margin: 10px 0; }}
        .medium {{ background: #fffde7; border-left: 4px solid #fbc02d; padding: 10px; margin: 10px 0; }}
        .low {{ background: #e8f5e8; border-left: 4px solid #388e3c; padding: 10px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔒 Security Scan Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Path: {Path.cwd()}</p>
    </div>
    <div class="content">
        <h2>Scan Results</h2>
        <pre>{result.stdout}</pre>
    </div>
</body>
</html>
""")
    else:
        # JSON format (default)
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "path": str(Path.cwd()),
            "scan_output": result.stdout,
            "exit_code": result.returncode,
            "format": "json"
        }
        print(json.dumps(report_data, indent=2))

def main():
    """Main report function."""
    format_type = sys.argv[1] if len(sys.argv) > 1 else "json"
    
    if format_type not in ["json", "html", "sarif"]:
        print("❌ Invalid format. Use: json, html, or sarif")
        return 1
        
    generate_report(format_type)
    return 0

if __name__ == '__main__':
    sys.exit(main())