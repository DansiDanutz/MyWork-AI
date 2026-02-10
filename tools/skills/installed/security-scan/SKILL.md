# security-scan

**Description:** Advanced security scanning skill that wraps and extends the existing MyWork-AI security scanner

**Version:** 1.0.0

**Author:** MyWork-AI Framework

## Dependencies

- python3
- mywork-ai
- existing security scanner

## Commands

### scan

**Script:** scan.py
**Usage:** mw skills run security-scan scan [path]

Perform comprehensive security scan on specified path or current directory.

### baseline

**Script:** baseline.py
**Usage:** mw skills run security-scan baseline

Update security baseline to ignore current findings.

### diff

**Script:** diff.py
**Usage:** mw skills run security-scan diff

Show only new security issues since last baseline.

### report

**Script:** report.py
**Usage:** mw skills run security-scan report [format]

Generate detailed security report (json, html, sarif).

### help

**Script:** help.py
**Usage:** mw skills run security-scan help

Show detailed help and usage information.

## Features

- Comprehensive vulnerability scanning
- Secret detection (API keys, passwords, tokens)
- Dependency vulnerability analysis  
- Code injection pattern detection
- Baseline management for CI/CD
- Multiple output formats
- Integration with existing security tools

## Configuration

Edit `config.json` to customize scan rules, severity levels, and integrations.