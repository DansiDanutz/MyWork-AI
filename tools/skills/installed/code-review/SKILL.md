# code-review

**Description:** Automated code review skill that analyzes code quality, patterns, and best practices

**Version:** 1.0.0

**Author:** MyWork-AI Framework

## Dependencies

- python3
- mywork-ai
- git

## Commands

### review

**Script:** review.py
**Usage:** mw skills run code-review review [path]

Perform automated code review on specified path or current directory.

### report

**Script:** report.py  
**Usage:** mw skills run code-review report [format]

Generate detailed code review report in specified format (text, json, html).

### config

**Script:** config.py
**Usage:** mw skills run code-review config

Configure code review rules and preferences.

### help

**Script:** help.py
**Usage:** mw skills run code-review help

Show detailed help and usage information.

## Features

- Code quality analysis
- Best practices validation  
- Security pattern detection
- Performance anti-pattern identification
- Documentation coverage analysis
- Git integration for diff-based reviews

## Configuration

Edit `config.json` to customize review rules, severity levels, and output preferences.