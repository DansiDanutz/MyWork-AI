#!/usr/bin/env python3
"""
Deploy Check Skill - Help
========================
"""

def main():
    """Show deploy check skill help."""
    print("""
🚀 Deploy Check Skill Help
=========================

Pre-deployment checklist and validation skill ensuring production 
readiness with comprehensive checks across environments.

COMMANDS:
  check [env]      - Run deployment checklist (default: production)
  config           - Configure checklist rules and settings
  report           - Generate multi-environment readiness report  
  help             - Show this help

ENVIRONMENTS:
  development      - Basic checks, less strict requirements
  staging          - Production-like checks with SSL validation
  production       - Full security, performance, and backup checks

EXAMPLES:
  mw skills run deploy-check check
  mw skills run deploy-check check staging  
  mw skills run deploy-check config
  mw skills run deploy-check report

CHECKLIST CATEGORIES:
• Git Status - Clean repository, no uncommitted changes
• Required Files - README, dependencies, configuration
• Environment - Proper .env setup, variable management
• Dependencies - Version pinning, security updates
• Security - Baseline scans, credential management
• Performance - Build scripts, static file optimization
• Documentation - README, CHANGELOG, API docs
• SSL/TLS - Certificate configuration (staging/production)
• Backup Strategy - Data backup and recovery (production)

CONFIGURATION:
Customize checks per environment:
• required_files: Files that must exist
• strict: Enable stricter validation rules
• ssl_required: Enforce SSL/TLS configuration
• backup_required: Require backup strategy

CI/CD INTEGRATION:
Use in deployment pipelines:
  mw skills run deploy-check check production && deploy.sh

EXIT CODES:
• 0 - All checks passed, ready to deploy
• 1 - Failed checks, deployment not recommended

For more details, see the SKILL.md documentation.
""")
    return 0

if __name__ == '__main__':
    exit(main())