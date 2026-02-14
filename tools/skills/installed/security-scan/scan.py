#!/usr/bin/env python3
"""
Security Scan Skill - Main Scanner
=================================
Advanced security scanning that wraps the existing MyWork-AI security scanner.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class SecurityScanner:
    def __init__(self, path: str = "."):
        self.path = Path(path).resolve()
        self.findings = []
        self.stats = {
            'files_scanned': 0,
            'vulnerabilities': 0,
            'secrets_found': 0,
            'high_severity': 0,
            'critical_severity': 0
        }
        
        # Try to find existing security scanner
        mywork_root = self._find_mywork_root()
        self.existing_scanner = mywork_root / "tools" / "security" / "security_scanner.py"
        
    def _find_mywork_root(self) -> Path:
        """Find MyWork-AI root directory."""
        current = Path.cwd()
        while current != current.parent:
            if (current / "CLAUDE.md").exists():
                return current
            current = current.parent
        # Fallback
        return Path(os.environ.get('MYWORK_ROOT', Path.home() / 'MyWork-AI'))

    def scan(self) -> Dict[str, Any]:
        """Perform comprehensive security scan."""
        print(f"🔒 Starting security scan of: {self.path}")
        
        # Run existing scanner if available
        if self.existing_scanner.exists():
            self._run_existing_scanner()
        
        # Additional security checks
        self._scan_secrets()
        self._scan_dependencies()
        self._scan_code_patterns()
        
        self._print_summary()
        
        return {
            'findings': self.findings,
            'stats': self.stats,
            'path': str(self.path),
            'timestamp': datetime.now().isoformat()
        }

    def _run_existing_scanner(self):
        """Run the existing MyWork-AI security scanner."""
        try:
            print("🔍 Running existing MyWork-AI security scanner...")
            result = subprocess.run([
                sys.executable, 
                str(self.existing_scanner),
                str(self.path)
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("✅ Existing scanner completed successfully")
                # Try to parse output if JSON
                try:
                    scanner_data = json.loads(result.stdout)
                    if isinstance(scanner_data, dict) and 'findings' in scanner_data:
                        self.findings.extend(scanner_data['findings'])
                        self._update_stats_from_findings(scanner_data['findings'])
                except json.JSONDecodeError:
                    # Not JSON, treat as text findings
                    if result.stdout.strip():
                        self.findings.append({
                            'type': 'scanner_output',
                            'severity': 'info',
                            'message': 'Existing scanner output',
                            'details': result.stdout.strip()
                        })
            else:
                print(f"⚠️ Existing scanner returned error code: {result.returncode}")
                if result.stderr:
                    print(f"Error: {result.stderr}")
                    
        except subprocess.TimeoutExpired:
            print("⚠️ Existing scanner timed out")
        except Exception as e:
            print(f"⚠️ Error running existing scanner: {e}")

    def _scan_secrets(self):
        """Scan for hardcoded secrets and sensitive data."""
        print("🔍 Scanning for secrets...")
        
        secret_patterns = [
            (r'password\s*[=:]\s*["\'][^"\']{8,}["\']', 'high', 'Hardcoded password'),
            (r'api[_-]?key\s*[=:]\s*["\'][^"\']{20,}["\']', 'critical', 'API key in code'),
            (r'secret[_-]?key\s*[=:]\s*["\'][^"\']{20,}["\']', 'critical', 'Secret key in code'),
            (r'token\s*[=:]\s*["\'][^"\']{20,}["\']', 'high', 'Auth token in code'),
            (r'-----BEGIN\s+PRIVATE\s+KEY-----', 'critical', 'Private key in code'),
            (r'-----BEGIN\s+RSA\s+PRIVATE\s+KEY-----', 'critical', 'RSA private key'),
            (r'sk-[a-zA-Z0-9]{32,}', 'critical', 'OpenAI API key pattern'),
            (r'xoxb-[a-zA-Z0-9]{10,}', 'critical', 'Slack bot token'),
            (r'ghp_[a-zA-Z0-9]{36}', 'critical', 'GitHub personal access token'),
        ]
        
        for file_path in self.path.rglob('*'):
            if not self._should_scan_file(file_path):
                continue
                
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                self.stats['files_scanned'] += 1
                
                for pattern, severity, message in secret_patterns:
                    import re
                    matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        self._add_finding(file_path, line_num, severity, 'secret', message, match.group())
                        
            except Exception as e:
                continue

    def _scan_dependencies(self):
        """Scan for known vulnerable dependencies."""
        print("🔍 Scanning dependencies...")
        
        # Look for common dependency files
        dep_files = [
            'requirements.txt',
            'package.json', 
            'Pipfile',
            'composer.json',
            'pom.xml'
        ]
        
        for dep_file in dep_files:
            dep_path = self.path / dep_file
            if dep_path.exists():
                self._scan_dependency_file(dep_path)

    def _scan_dependency_file(self, dep_path: Path):
        """Scan a specific dependency file."""
        try:
            content = dep_path.read_text()
            
            # Known vulnerable patterns (simplified)
            vulnerable_patterns = [
                (r'django\s*[<>=]*\s*[12]\.[0-9]', 'high', 'Old Django version with known vulnerabilities'),
                (r'flask\s*[<>=]*\s*0\.[0-9]', 'medium', 'Old Flask version'),
                (r'requests\s*[<>=]*\s*2\.[0-9]\.[0-9]', 'low', 'Check requests version for vulnerabilities'),
                (r'lodash.*[<>=]*\s*[34]\.[0-9]', 'medium', 'Lodash version may have prototype pollution'),
            ]
            
            import re
            for pattern, severity, message in vulnerable_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    self._add_finding(dep_path, 0, severity, 'dependency', message)
                    
        except Exception as e:
            pass

    def _scan_code_patterns(self):
        """Scan for insecure code patterns."""
        print("🔍 Scanning code patterns...")
        
        code_patterns = [
            (r'eval\s*\(.*\)', 'critical', 'Use of eval() - code injection risk'),  # noqa: security
            (r'exec\s*\(.*\)', 'critical', 'Use of exec() - code injection risk'),  # noqa: security
            (r'subprocess\.call\([^)]*shell\s*=\s*True', 'high', 'Shell injection risk'),
            (r'os\.system\s*\(', 'high', 'Command injection risk'),
            (r'input\s*\(.*\).*eval', 'critical', 'User input passed to eval'),
            (r'pickle\.loads?\s*\(', 'medium', 'Pickle deserialization risk'),
            (r'yaml\.load\s*\([^,)]*\)', 'medium', 'Unsafe YAML loading'),
            (r'random\.random\(\).*password', 'medium', 'Weak random for security purposes'),
            (r'md5\s*\(', 'low', 'MD5 is cryptographically broken'),
            (r'sha1\s*\(', 'low', 'SHA1 is cryptographically weak'),
        ]
        
        for file_path in self.path.rglob('*.py'):
            if not self._should_scan_file(file_path):
                continue
                
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                lines = content.split('\n')
                
                import re
                for i, line in enumerate(lines, 1):
                    for pattern, severity, message in code_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            self._add_finding(file_path, i, severity, 'code_pattern', message, line.strip())
                            
            except Exception as e:
                continue

    def _should_scan_file(self, file_path: Path) -> bool:
        """Check if file should be scanned."""
        if not file_path.is_file():
            return False
            
        # Skip binary files and common ignore patterns
        skip_patterns = [
            '.git/',
            '__pycache__/',
            'node_modules/',
            '.venv/',
            'venv/',
            '.pyc',
            '.so',
            '.dll',
            '.exe',
            '.jpg',
            '.png',
            '.gif',
            '.pdf'
        ]
        
        file_str = str(file_path)
        for pattern in skip_patterns:
            if pattern in file_str:
                return False
                
        return True

    def _add_finding(self, file_path: Path, line: int, severity: str, finding_type: str, 
                    message: str, details: str = ""):
        """Add a security finding."""
        self.findings.append({
            'file': str(file_path.relative_to(self.path)) if file_path != self.path else str(file_path.name),
            'line': line,
            'severity': severity,
            'type': finding_type,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        
        # Update stats
        if severity == 'critical':
            self.stats['critical_severity'] += 1
        elif severity == 'high':
            self.stats['high_severity'] += 1
            
        self.stats['vulnerabilities'] += 1
        if finding_type == 'secret':
            self.stats['secrets_found'] += 1

    def _update_stats_from_findings(self, findings: List[Dict]):
        """Update stats from existing scanner findings."""
        for finding in findings:
            severity = finding.get('severity', 'medium')
            if severity == 'critical':
                self.stats['critical_severity'] += 1
            elif severity == 'high':
                self.stats['high_severity'] += 1
            self.stats['vulnerabilities'] += 1

    def _print_summary(self):
        """Print scan summary."""
        print(f"\n🔒 Security Scan Summary")
        print("=" * 50)
        print(f"Files scanned: {self.stats['files_scanned']}")
        print(f"Vulnerabilities: {self.stats['vulnerabilities']}")
        print(f"Secrets found: {self.stats['secrets_found']}")
        print(f"Critical severity: {self.stats['critical_severity']}")
        print(f"High severity: {self.stats['high_severity']}")
        
        if self.findings:
            print(f"\n🔴 Security Findings:")
            for finding in sorted(self.findings, key=lambda x: (x['severity'], x['file'], x['line'])):
                print(f"  {finding['file']}:{finding['line']} [{finding['severity'].upper()}] {finding['message']}")
                if finding.get('details'):
                    print(f"    Details: {finding['details'][:100]}...")
        else:
            print("✅ No security issues found!")


def main():
    """Main scan function."""
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    
    scanner = SecurityScanner(path)
    result = scanner.scan()
    
    # Exit with error code if critical/high severity issues found
    return 1 if (result['stats']['critical_severity'] > 0 or 
                result['stats']['high_severity'] > 0) else 0

if __name__ == '__main__':
    sys.exit(main())