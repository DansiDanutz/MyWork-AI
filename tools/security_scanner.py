#!/usr/bin/env python3
"""MyWork Security Scanner - Detect secrets, vulnerabilities, and security issues."""

import os
import re
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Patterns for detecting hardcoded secrets
SECRET_PATTERNS = [
    (r'(?:api[_-]?key|apikey)\s*[=:]\s*["\']([a-zA-Z0-9_\-]{20,})["\']', "API Key"),
    (r'(?:secret|password|passwd|pwd)\s*[=:]\s*["\']([^"\']{8,})["\']', "Password/Secret"),
    (r'(?:token)\s*[=:]\s*["\']([a-zA-Z0-9_\-]{20,})["\']', "Token"),
    (r'(?:aws_access_key_id)\s*[=:]\s*["\']?(AKIA[0-9A-Z]{16})["\']?', "AWS Access Key"),
    (r'(?:aws_secret_access_key)\s*[=:]\s*["\']?([a-zA-Z0-9/+=]{40})["\']?', "AWS Secret Key"),
    (r'sk-[a-zA-Z0-9]{20,}', "OpenAI/Stripe API Key"),
    (r'ghp_[a-zA-Z0-9]{36}', "GitHub Personal Access Token"),
    (r'glpat-[a-zA-Z0-9\-]{20}', "GitLab Personal Access Token"),
    (r'xox[bporsm]-[a-zA-Z0-9\-]{10,}', "Slack Token"),
    (r'-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----', "Private Key"),
    (r'(?:postgres|mysql|mongodb)://[^\s"\']+:[^\s"\']+@', "Database Connection String"),
    (r'Bearer\s+[a-zA-Z0-9_\-\.]{20,}', "Bearer Token"),
]

# Files/dirs to skip
SKIP_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', '.tox', 'dist', 'build', '.egg-info'}
SKIP_FILES = {'.env.example', 'security_scanner.py', 'test_security_scanner.py'}
SCAN_EXTENSIONS = {'.py', '.js', '.ts', '.jsx', '.tsx', '.json', '.yaml', '.yml', '.toml', '.cfg', '.ini', '.conf', '.sh', '.env', '.md'}


def scan_secrets(project_path: str, verbose: bool = False) -> list:
    """Scan project for hardcoded secrets."""
    findings = []
    project = Path(project_path)
    
    for root, dirs, files in os.walk(project):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        
        for fname in files:
            if fname in SKIP_FILES:
                continue
            fpath = Path(root) / fname
            if fpath.suffix not in SCAN_EXTENSIONS and not fname.startswith('.env'):
                continue
            
            try:
                content = fpath.read_text(errors='ignore')
            except (PermissionError, OSError):
                continue
            
            for line_num, line in enumerate(content.splitlines(), 1):
                # Skip comments
                stripped = line.strip()
                if stripped.startswith('#') or stripped.startswith('//'):
                    continue
                
                for pattern, secret_type in SECRET_PATTERNS:
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        rel_path = str(fpath.relative_to(project))
                        secret_value = match.group(0)
                        masked = secret_value[:8] + '...' + secret_value[-4:] if len(secret_value) > 16 else '***'
                        findings.append({
                            'type': secret_type,
                            'file': rel_path,
                            'line': line_num,
                            'masked_value': masked,
                            'severity': 'HIGH'
                        })
    
    return findings


def scan_permissions(project_path: str) -> list:
    """Check for overly permissive file permissions."""
    findings = []
    project = Path(project_path)
    
    for root, dirs, files in os.walk(project):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fname in files:
            fpath = Path(root) / fname
            try:
                mode = oct(fpath.stat().st_mode)[-3:]
                if mode[2] in ('6', '7') and fpath.suffix in {'.py', '.sh', '.env', '.key', '.pem'}:
                    findings.append({
                        'type': 'World-readable/writable',
                        'file': str(fpath.relative_to(project)),
                        'detail': f'Permissions: {mode}',
                        'severity': 'MEDIUM'
                    })
            except OSError:
                continue
    
    return findings


def scan_dependencies(project_path: str) -> list:
    """Check for known vulnerable dependency patterns."""
    findings = []
    project = Path(project_path)
    
    # Check for pip-audit / npm audit availability
    req_file = project / 'requirements.txt'
    if req_file.exists():
        try:
            result = subprocess.run(
                ['pip-audit', '-r', str(req_file), '--format', 'json'],
                capture_output=True, text=True, timeout=60, cwd=project_path
            )
            if result.returncode == 0:
                vulns = json.loads(result.stdout)
                for v in vulns.get('dependencies', []):
                    for vuln in v.get('vulns', []):
                        findings.append({
                            'type': 'Vulnerable Dependency',
                            'package': v['name'],
                            'version': v['version'],
                            'vuln_id': vuln.get('id', 'unknown'),
                            'severity': 'HIGH'
                        })
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            pass
    
    pkg_json = project / 'package.json'
    if pkg_json.exists():
        try:
            result = subprocess.run(
                ['npm', 'audit', '--json'],
                capture_output=True, text=True, timeout=60, cwd=project_path
            )
            audit_data = json.loads(result.stdout)
            for vuln_name, vuln_info in audit_data.get('vulnerabilities', {}).items():
                findings.append({
                    'type': 'Vulnerable Dependency',
                    'package': vuln_name,
                    'severity_level': vuln_info.get('severity', 'unknown').upper(),
                    'severity': 'HIGH' if vuln_info.get('severity') in ('high', 'critical') else 'MEDIUM'
                })
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            pass
    
    return findings


def scan_gitignore(project_path: str) -> list:
    """Check if sensitive files are properly gitignored."""
    findings = []
    project = Path(project_path)
    gitignore = project / '.gitignore'
    
    sensitive_patterns = ['.env', '*.pem', '*.key', '*.p12', 'credentials.json', 'secrets.json', '*.sqlite', '*.db']
    
    if gitignore.exists():
        content = gitignore.read_text()
        for pattern in sensitive_patterns:
            if pattern not in content:
                findings.append({
                    'type': 'Missing .gitignore entry',
                    'detail': f'"{pattern}" not in .gitignore',
                    'severity': 'MEDIUM'
                })
    else:
        findings.append({
            'type': 'No .gitignore',
            'detail': 'Project has no .gitignore file',
            'severity': 'HIGH'
        })
    
    return findings


def scan_code_patterns(project_path: str) -> list:
    """Scan for dangerous code patterns."""
    findings = []
    project = Path(project_path)
    
    dangerous_patterns = [
        (r'\beval\s*\(', 'eval() usage', 'MEDIUM'),
        (r'\bexec\s*\(', 'exec() usage', 'MEDIUM'),
        (r'subprocess\.call\([^)]*shell\s*=\s*True', 'shell=True in subprocess', 'MEDIUM'),
        (r'os\.system\s*\(', 'os.system() usage', 'LOW'),
        (r'pickle\.loads?\s*\(', 'Unsafe pickle deserialization', 'HIGH'),
        (r'yaml\.load\s*\([^)]*\)(?!.*Loader)', 'Unsafe YAML load (no Loader)', 'MEDIUM'),
        (r'__import__\s*\(', 'Dynamic import', 'LOW'),
        (r'markupsafe|safe\s*=\s*True|autoescape\s*=\s*False', 'Potential XSS', 'MEDIUM'),
        (r'CORS\s*\(\s*app\s*\)', 'Unrestricted CORS', 'MEDIUM'),
        (r'verify\s*=\s*False', 'SSL verification disabled', 'HIGH'),
    ]
    
    for root, dirs, files in os.walk(project):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fname in files:
            fpath = Path(root) / fname
            if fpath.suffix not in {'.py', '.js', '.ts'}:
                continue
            try:
                content = fpath.read_text(errors='ignore')
            except (PermissionError, OSError):
                continue
            
            for line_num, line in enumerate(content.splitlines(), 1):
                for pattern, desc, severity in dangerous_patterns:
                    if re.search(pattern, line):
                        findings.append({
                            'type': desc,
                            'file': str(fpath.relative_to(project)),
                            'line': line_num,
                            'severity': severity
                        })
    
    return findings


def full_scan(project_path: str, verbose: bool = False) -> dict:
    """Run all security scans on a project."""
    project_path = os.path.abspath(project_path)
    
    results = {
        'project': project_path,
        'timestamp': datetime.now().isoformat(),
        'secrets': scan_secrets(project_path, verbose),
        'permissions': scan_permissions(project_path),
        'dependencies': scan_dependencies(project_path),
        'gitignore': scan_gitignore(project_path),
        'code_patterns': scan_code_patterns(project_path),
    }
    
    # Summary
    total = sum(len(v) for k, v in results.items() if isinstance(v, list))
    high = sum(1 for k, v in results.items() if isinstance(v, list) for f in v if f.get('severity') == 'HIGH')
    medium = sum(1 for k, v in results.items() if isinstance(v, list) for f in v if f.get('severity') == 'MEDIUM')
    low = sum(1 for k, v in results.items() if isinstance(v, list) for f in v if f.get('severity') == 'LOW')
    
    results['summary'] = {
        'total_findings': total,
        'high': high,
        'medium': medium,
        'low': low,
        'score': max(0, 100 - (high * 15) - (medium * 5) - (low * 2))
    }
    
    return results


def print_report(results: dict):
    """Print a formatted security report."""
    summary = results['summary']
    score = summary['score']
    
    # Score color
    if score >= 80:
        grade = '🟢 A'
    elif score >= 60:
        grade = '🟡 B'
    elif score >= 40:
        grade = '🟠 C'
    else:
        grade = '🔴 D'
    
    print(f"\n{'='*60}")
    print(f"  🔒 MyWork Security Report")
    print(f"{'='*60}")
    print(f"  Project: {results['project']}")
    print(f"  Date:    {results['timestamp'][:19]}")
    print(f"  Score:   {score}/100 {grade}")
    print(f"{'='*60}")
    print(f"  Findings: {summary['total_findings']} total")
    print(f"    🔴 HIGH:   {summary['high']}")
    print(f"    🟡 MEDIUM: {summary['medium']}")
    print(f"    🟢 LOW:    {summary['low']}")
    print(f"{'='*60}\n")
    
    sections = [
        ('secrets', '🔑 Hardcoded Secrets'),
        ('permissions', '📂 File Permissions'),
        ('dependencies', '📦 Vulnerable Dependencies'),
        ('gitignore', '📋 .gitignore Issues'),
        ('code_patterns', '⚠️  Dangerous Code Patterns'),
    ]
    
    for key, title in sections:
        findings = results[key]
        if not findings:
            print(f"  {title}: ✅ Clean")
            continue
        
        print(f"  {title}: {len(findings)} issue(s)")
        for f in findings[:10]:  # Limit output
            severity = f.get('severity', '?')
            icon = '🔴' if severity == 'HIGH' else '🟡' if severity == 'MEDIUM' else '🟢'
            file_info = f.get('file', '')
            line_info = f':L{f["line"]}' if 'line' in f else ''
            detail = f.get('detail', f.get('masked_value', f.get('package', '')))
            print(f"    {icon} [{f.get('type', '?')}] {file_info}{line_info} — {detail}")
        if len(findings) > 10:
            print(f"    ... and {len(findings) - 10} more")
        print()
    
    if score >= 80:
        print("  💪 Good security posture! Keep it up.\n")
    elif score >= 60:
        print("  ⚡ Some issues to address. Fix HIGH severity first.\n")
    else:
        print("  🚨 Significant security issues found. Remediate immediately.\n")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='MyWork Security Scanner')
    parser.add_argument('command', nargs='?', default='scan', choices=['scan', 'secrets', 'deps', 'patterns', 'report'])
    parser.add_argument('path', nargs='?', default='.')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--save', help='Save report to file')
    args = parser.parse_args()
    
    project_path = os.path.abspath(args.path)
    
    if args.command == 'secrets':
        findings = scan_secrets(project_path, args.verbose)
        if args.json:
            print(json.dumps(findings, indent=2))
        else:
            for f in findings:
                print(f"🔴 [{f['type']}] {f['file']}:L{f['line']} — {f['masked_value']}")
            print(f"\n{len(findings)} secret(s) found.")
    
    elif args.command == 'deps':
        findings = scan_dependencies(project_path)
        if args.json:
            print(json.dumps(findings, indent=2))
        else:
            for f in findings:
                print(f"📦 {f.get('package', '?')} — {f.get('vuln_id', f.get('severity_level', '?'))}")
            print(f"\n{len(findings)} vulnerability(ies) found.")
    
    elif args.command == 'patterns':
        findings = scan_code_patterns(project_path)
        if args.json:
            print(json.dumps(findings, indent=2))
        else:
            for f in findings:
                print(f"⚠️  [{f['type']}] {f['file']}:L{f['line']}")
            print(f"\n{len(findings)} pattern(s) found.")
    
    else:  # scan or report
        results = full_scan(project_path, args.verbose)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print_report(results)
        
        if args.save:
            with open(args.save, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"  📄 Report saved to {args.save}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
