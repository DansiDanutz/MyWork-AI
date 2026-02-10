# deploy-check

**Description:** Pre-deployment checklist and validation skill ensuring production readiness

**Version:** 1.0.0

**Author:** MyWork-AI Framework

## Dependencies

- python3
- mywork-ai
- git

## Commands

### check

**Script:** check.py
**Usage:** mw skills run deploy-check check [environment]

Run comprehensive pre-deployment checklist for specified environment.

### config

**Script:** config.py
**Usage:** mw skills run deploy-check config

Configure deployment checklist rules and environment settings.

### report

**Script:** report.py
**Usage:** mw skills run deploy-check report

Generate detailed deployment readiness report.

### help

**Script:** help.py
**Usage:** mw skills run deploy-check help

Show detailed help and usage information.

## Features

- Environment configuration validation
- Security checklist verification
- Performance benchmarking
- Dependency analysis
- Database migration checks
- SSL/TLS configuration validation
- Backup verification
- Monitoring setup confirmation
- Documentation completeness check

## Environments

- development
- staging  
- production
- custom (configurable)

## Configuration

Edit `config.json` to customize checklist items, environment requirements, and validation thresholds.