#!/usr/bin/env python3
"""
Code Review Skill - Help
=======================
"""

def main():
    """Show code review skill help."""
    print("""
🔍 Code Review Skill Help
========================

This skill provides automated code review capabilities with quality,
security, and best practice analysis.

COMMANDS:
  review [path]     - Perform code review (default: current directory)
  report [format]   - Generate report (text, json, html)
  config           - Configure review settings
  help             - Show this help

EXAMPLES:
  mw skills run code-review review src/
  mw skills run code-review report html > report.html
  mw skills run code-review config

FEATURES:
• Security vulnerability detection
• Performance anti-pattern identification  
• Code style validation
• Documentation coverage analysis
• Complexity metrics
• Git integration for diff-based reviews

CONFIGURATION:
Edit the config.json file to customize:
• Enabled check types
• File extensions to review
• Ignore patterns
• Severity thresholds
• Style preferences

For more details, see the SKILL.md documentation.
""")
    return 0

if __name__ == '__main__':
    exit(main())