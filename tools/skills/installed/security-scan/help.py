#!/usr/bin/env python3
"""
Security Scan Skill - Help
=========================
"""

def main():
    """Show security scan skill help."""
    print("""
🔒 Security Scan Skill Help
==========================

Advanced security scanning that wraps and extends the existing 
MyWork-AI security scanner with additional capabilities.

COMMANDS:
  scan [path]      - Perform comprehensive security scan
  baseline         - Update security baseline (ignore current findings)  
  diff             - Show only new issues since last baseline
  report [format]  - Generate detailed report (json, html, sarif)
  help             - Show this help

EXAMPLES:
  mw skills run security-scan scan
  mw skills run security-scan scan src/
  mw skills run security-scan baseline
  mw skills run security-scan diff
  mw skills run security-scan report html > security-report.html

SECURITY CHECKS:
• Secret detection (API keys, passwords, tokens)
• Hardcoded credentials identification
• Vulnerable dependency analysis
• Code injection pattern detection
• Cryptographic weakness detection
• Shell injection risks
• Unsafe deserialization patterns

BASELINE WORKFLOW:
1. Run initial scan: mw skills run security-scan scan
2. Review and fix critical issues
3. Set baseline: mw skills run security-scan baseline
4. Future scans only show NEW issues: mw skills run security-scan diff

CI/CD INTEGRATION:
Use the 'sarif' report format for integration with GitHub Security:
  mw skills run security-scan report sarif > security.sarif

For more details, see the SKILL.md documentation.
""")
    return 0

if __name__ == '__main__':
    exit(main())