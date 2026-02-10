#!/usr/bin/env python3
"""
Deploy Check Skill - Report Generator
====================================
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

def generate_report():
    """Generate detailed deployment readiness report."""
    # Run deployment checks for all environments
    check_script = Path(__file__).parent / "check.py"
    environments = ["development", "staging", "production"]
    
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "project_path": str(Path.cwd()),
        "environments": {}
    }
    
    print("📊 Deployment Readiness Report")
    print("=" * 60)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Project: {Path.cwd().name}")
    print()
    
    for env in environments:
        print(f"\n🌍 Environment: {env.upper()}")
        print("-" * 40)
        
        # Run checks for this environment
        result = subprocess.run([sys.executable, str(check_script), env], 
                              capture_output=True, text=True)
        
        report_data["environments"][env] = {
            "exit_code": result.returncode,
            "output": result.stdout,
            "ready": result.returncode == 0
        }
        
        if result.returncode == 0:
            print("✅ Ready for deployment")
        else:
            print("❌ Not ready for deployment")
            
        # Show key stats from output
        lines = result.stdout.split('\n')
        for line in lines:
            if 'Passed:' in line or 'Warnings:' in line or 'Failed:' in line:
                print(f"   {line}")
    
    # Overall readiness assessment
    print(f"\n🎯 Overall Assessment")
    print("=" * 60)
    
    prod_ready = report_data["environments"]["production"]["ready"]
    staging_ready = report_data["environments"]["staging"]["ready"] 
    dev_ready = report_data["environments"]["development"]["ready"]
    
    if prod_ready:
        print("🚀 PRODUCTION READY - All checks passed!")
    elif staging_ready:
        print("⚠️  STAGING READY - Production deployment needs fixes")
    elif dev_ready:
        print("🚧 DEVELOPMENT READY - Staging and production need work")
    else:
        print("🛑 NOT READY - Basic checks failing")
    
    # Save detailed report
    report_file = Path("deployment-report.json")
    with open(report_file, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    return 0

def main():
    """Main report function."""
    return generate_report()

if __name__ == '__main__':
    sys.exit(main())