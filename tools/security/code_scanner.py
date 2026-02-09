#!/usr/bin/env python3
"""
Code Security Scanner
=====================
Scans all Python files in the repository for security vulnerabilities.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple


class SecurityFinding:
    def __init__(self, severity: str, file_path: str, line_num: int, description: str, code_snippet: str = ""):
        self.severity = severity
        self.file_path = file_path
        self.line_num = line_num
        self.description = description
        self.code_snippet = code_snippet

    def to_dict(self):
        return {
            'severity': self.severity,
            'file': self.file_path,
            'line': self.line_num,
            'description': self.description,
            'code_snippet': self.code_snippet
        }


class CodeSecurityScanner:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.findings = []
        
        # Security patterns to search for
        self.patterns = {
            'hardcoded_secrets': {
                'severity': 'CRITICAL',
                'patterns': [
                    (r'["\'][A-Za-z0-9]{20,}["\']', 'Potential hardcoded API key or token'),
                    (r'password\s*=\s*["\'][^"\']+["\']', 'Hardcoded password'),
                    (r'api_key\s*=\s*["\'][^"\']+["\']', 'Hardcoded API key'),
                    (r'secret\s*=\s*["\'][^"\']+["\']', 'Hardcoded secret'),
                    (r'token\s*=\s*["\'][^"\']+["\']', 'Hardcoded token'),
                    (r'sk-[A-Za-z0-9]{20,}', 'OpenAI-style secret key'),
                    (r'AIza[0-9A-Za-z-_]{35}', 'Google API key'),
                    (r'AKIA[0-9A-Z]{16}', 'AWS Access Key ID'),
                ]
            },
            'code_injection': {
                'severity': 'CRITICAL',
                'patterns': [
                    (r'\beval\s*\(', 'Use of eval() function - code injection risk'),
                    (r'\bexec\s*\(', 'Use of exec() function - code injection risk'),
                    (r'__import__\s*\(.*input\(', 'Dynamic import with user input'),
                ]
            },
            'command_injection': {
                'severity': 'HIGH',
                'patterns': [
                    (r'os\.system\s*\(', 'Use of os.system() - command injection risk'),
                    (r'subprocess.*shell\s*=\s*True', 'subprocess with shell=True - command injection risk'),
                    (r'popen\s*\(', 'Use of popen() - command injection risk'),
                ]
            },
            'sql_injection': {
                'severity': 'HIGH',
                'patterns': [
                    (r'["\'].*%.*["\'].*%', 'String formatting in SQL query - SQL injection risk'),
                    (r'["\'].*\+.*["\'].*cursor', 'String concatenation in SQL query'),
                    (r'execute\s*\([^)]*%[^)]*\)', 'SQL execute with string formatting'),
                    (r'f["\'].*SELECT.*{.*}.*["\']', 'f-string in SQL query'),
                ]
            },
            'pickle_usage': {
                'severity': 'HIGH',
                'patterns': [
                    (r'pickle\.loads?\s*\(', 'Pickle deserialization - potential remote code execution'),
                    (r'cPickle\.loads?\s*\(', 'cPickle deserialization - potential remote code execution'),
                    (r'dill\.loads?\s*\(', 'Dill deserialization - potential remote code execution'),
                ]
            },
            'insecure_http': {
                'severity': 'MEDIUM',
                'patterns': [
                    (r'http://[^/\s]+', 'Insecure HTTP URL - should use HTTPS'),
                    (r'["\']http://.*["\']', 'Hardcoded HTTP URL'),
                ]
            },
            'debug_info': {
                'severity': 'LOW',
                'patterns': [
                    (r'print\s*\(.*password.*\)', 'Print statement with password'),
                    (r'print\s*\(.*secret.*\)', 'Print statement with secret'),
                    (r'print\s*\(.*token.*\)', 'Print statement with token'),
                    (r'print\s*\(.*key.*\)', 'Print statement with key'),
                    (r'logger.*password', 'Logger statement with password'),
                    (r'logger.*secret', 'Logger statement with secret'),
                ]
            }
        }

    def scan_file(self, file_path: Path) -> List[SecurityFinding]:
        """Scan a single Python file for security issues."""
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return findings

        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Skip comments and empty lines for most checks
            if line_stripped.startswith('#') or not line_stripped:
                continue
                
            # Check each pattern category
            for category, config in self.patterns.items():
                for pattern, description in config['patterns']:
                    if re.search(pattern, line, re.IGNORECASE):
                        # Filter out obvious false positives
                        if self._is_false_positive(line, pattern, category, file_path):
                            continue
                            
                        finding = SecurityFinding(
                            severity=config['severity'],
                            file_path=str(file_path.relative_to(self.repo_path)),
                            line_num=line_num,
                            description=description,
                            code_snippet=line.strip()
                        )
                        findings.append(finding)

        return findings

    def _is_false_positive(self, line: str, pattern: str, category: str, file_path: Path = None) -> bool:
        """Filter out obvious false positives."""
        line_lower = line.lower()
        
        # Skip the scanner's own file to avoid false positives from pattern definitions
        if file_path and file_path.name == 'code_scanner.py':
            if category in ['code_injection', 'command_injection', 'insecure_http']:
                # Skip patterns that are just definitions in the scanner itself
                if any(word in line_lower for word in ['patterns', 'severity', 'description']):
                    return True
        
        # Skip obvious examples, tests, and documentation
        if any(word in line_lower for word in ['example', 'test', 'demo', 'placeholder', 'xxx', 'yyy']):
            return True
            
        # For hardcoded secrets, skip obvious non-secrets
        if category == 'hardcoded_secrets':
            if any(word in line_lower for word in [
                'your_api_key', 'your_secret', 'your_token', 'your_password',
                'enter_your', 'replace_with', 'config', 'env', 'environ'
            ]):
                return True
                
        # For HTTP URLs, allow localhost and documentation URLs
        if category == 'insecure_http':
            if any(word in line_lower for word in ['localhost', '127.0.0.1', 'example.com', 'httpbin.org']):
                return True
                
        return False

    def scan_repository(self) -> List[SecurityFinding]:
        """Scan all Python files in the repository."""
        print(f"Scanning repository: {self.repo_path}")
        
        # Find all Python files
        python_files = list(self.repo_path.rglob('*.py'))
        print(f"Found {len(python_files)} Python files")
        
        all_findings = []
        
        for file_path in python_files:
            # Skip virtual environments and cache directories
            if any(skip in str(file_path) for skip in ['.venv', '__pycache__', '.git', 'venv', 'env']):
                continue
                
            findings = self.scan_file(file_path)
            all_findings.extend(findings)
            
            if findings:
                print(f"Found {len(findings)} issues in {file_path.relative_to(self.repo_path)}")

        self.findings = all_findings
        return all_findings

    def generate_report(self) -> str:
        """Generate a security report."""
        if not self.findings:
            return "✅ No security issues found!"

        # Group findings by severity
        by_severity = {'CRITICAL': [], 'HIGH': [], 'MEDIUM': [], 'LOW': []}
        for finding in self.findings:
            by_severity[finding.severity].append(finding)

        report = []
        report.append("# Code Security Scan Results")
        report.append(f"**Total Issues Found:** {len(self.findings)}")
        report.append("")

        # Summary by severity
        for severity, findings in by_severity.items():
            if findings:
                report.append(f"**{severity}:** {len(findings)} issues")

        report.append("")

        # Detailed findings by severity
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            if by_severity[severity]:
                report.append(f"## {severity} Severity Issues")
                report.append("")
                
                for finding in by_severity[severity]:
                    report.append(f"### {finding.file_path}:{finding.line_num}")
                    report.append(f"**Issue:** {finding.description}")
                    report.append(f"**Code:** `{finding.code_snippet}`")
                    report.append("")

        return '\n'.join(report)

    def save_results(self, output_path: str):
        """Save scan results to JSON file."""
        results = {
            'scan_time': os.popen('date -Iseconds').read().strip(),
            'repository': str(self.repo_path),
            'total_findings': len(self.findings),
            'findings': [finding.to_dict() for finding in self.findings]
        }
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Results saved to: {output_path}")


def main():
    import sys
    
    if len(sys.argv) > 1:
        repo_path = sys.argv[1]
    else:
        repo_path = "/home/Memo1981/MyWork-AI"
    
    scanner = CodeSecurityScanner(repo_path)
    findings = scanner.scan_repository()
    
    print(f"\n🔍 Security Scan Complete")
    print(f"Found {len(findings)} potential security issues")
    
    # Save results
    output_dir = Path(repo_path) / "tools" / "security"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    scanner.save_results(str(output_dir / "code_scan_results.json"))
    
    # Print summary
    if findings:
        by_severity = {}
        for finding in findings:
            by_severity[finding.severity] = by_severity.get(finding.severity, 0) + 1
        
        print("\nSummary by severity:")
        for severity, count in by_severity.items():
            print(f"  {severity}: {count}")
    else:
        print("✅ No security issues found!")


if __name__ == "__main__":
    main()