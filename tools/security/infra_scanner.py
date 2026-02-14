#!/usr/bin/env python3
"""
Infrastructure Security Scanner
===============================
Scans local system for security configuration issues.
"""

import json
import os
import stat
import subprocess
from pathlib import Path
from typing import Dict, List, Optional


class InfraSecurityFinding:
    def __init__(self, category: str, severity: str, issue: str, details: str = "", recommendation: str = ""):
        self.category = category
        self.severity = severity
        self.issue = issue
        self.details = details
        self.recommendation = recommendation

    def to_dict(self):
        return {
            'category': self.category,
            'severity': self.severity,
            'issue': self.issue,
            'details': self.details,
            'recommendation': self.recommendation
        }


class InfrastructureScanner:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.findings = []

    def run_command(self, command: List[str]) -> str:
        """Run a system command and return output."""
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=30)
            return result.stdout.strip()
        except Exception as e:
            print(f"Error running command {' '.join(command)}: {e}")
            return ""

    def scan_open_ports(self):
        """Scan for open ports that might be security risks."""
        print("🔍 Scanning open ports...")
        
        # Use ss to list listening ports
        output = self.run_command(['ss', '-tlnp'])
        
        if not output:
            return
        
        lines = output.split('\n')
        suspicious_ports = []
        
        for line in lines:
            if 'LISTEN' in line:
                # Parse port information
                parts = line.split()
                if len(parts) >= 4:
                    local_address = parts[3]
                    
                    # Extract port number
                    if ':' in local_address:
                        port = local_address.split(':')[-1]
                        
                        # Check for potentially risky ports
                        if port.isdigit():
                            port_num = int(port)
                            
                            # Database ports
                            if port_num in [3306, 5432, 27017, 6379, 11211]:
                                suspicious_ports.append((port_num, "Database service exposed"))
                            
                            # Debug/development ports
                            elif port_num in [8080, 8000, 3000, 5000, 8888, 9000]:
                                if '0.0.0.0' in local_address or '::' in local_address:
                                    suspicious_ports.append((port_num, "Development server exposed to all interfaces"))
                            
                            # SSH on non-standard ports
                            elif port_num == 22 and '0.0.0.0' in local_address:
                                suspicious_ports.append((port_num, "SSH exposed to all interfaces"))
        
        for port, issue in suspicious_ports:
            finding = InfraSecurityFinding(
                category='Network',
                severity='MEDIUM',
                issue=f'Port {port}: {issue}',
                details=f'Port {port} is listening and may pose a security risk',
                recommendation='Review if this port needs to be publicly accessible'
            )
            self.findings.append(finding)

    def scan_file_permissions(self):
        """Scan for files with insecure permissions."""
        print("🔍 Scanning file permissions...")
        
        sensitive_paths = [
            '/etc/passwd',
            '/etc/shadow',
            '/etc/ssh/sshd_config',
            '/home/*/.ssh',
            os.path.expanduser('~/.ssh'),
            self.repo_path / '.env',
            self.repo_path / '.env.local',
        ]
        
        # Also scan for world-readable files in the repository
        for file_path in self.repo_path.rglob('*'):
            if file_path.is_file():
                try:
                    file_stat = file_path.stat()
                    mode = file_stat.st_mode
                    
                    # Check if world-readable
                    if mode & stat.S_IROTH:
                        # Check if it's a sensitive file
                        name_lower = file_path.name.lower()
                        if any(pattern in name_lower for pattern in [
                            '.env', 'secret', 'password', 'key', 'token', 'credential'
                        ]):
                            finding = InfraSecurityFinding(
                                category='File Permissions',
                                severity='HIGH',
                                issue=f'Sensitive file is world-readable: {file_path.relative_to(self.repo_path)}',
                                details=f'File permissions: {oct(mode)[-3:]}',
                                recommendation='Remove world-read permissions (chmod o-r)'
                            )
                            self.findings.append(finding)
                    
                    # Check if world-writable
                    if mode & stat.S_IWOTH:
                        finding = InfraSecurityFinding(
                            category='File Permissions',
                            severity='CRITICAL',
                            issue=f'File is world-writable: {file_path.relative_to(self.repo_path)}',
                            details=f'File permissions: {oct(mode)[-3:]}',
                            recommendation='Remove world-write permissions (chmod o-w)'
                        )
                        self.findings.append(finding)
                        
                except Exception:
                    pass

    def scan_ssh_config(self):
        """Scan SSH configuration for security issues."""
        print("🔍 Scanning SSH configuration...")
        
        ssh_config_paths = [
            '/etc/ssh/sshd_config',
            Path.home() / '.ssh/config',
        ]
        
        for config_path in ssh_config_paths:
            if not Path(config_path).exists():
                continue
                
            try:
                with open(config_path, 'r') as f:
                    config_content = f.read().lower()
                
                # Check for insecure configurations
                security_checks = [
                    ('passwordauthentication yes', 'Password authentication enabled', 'MEDIUM'),
                    ('permitrootlogin yes', 'Root login permitted', 'HIGH'),
                    ('permitemptypasswords yes', 'Empty passwords permitted', 'CRITICAL'),
                    ('protocol 1', 'Insecure SSH protocol 1 enabled', 'HIGH'),
                    ('x11forwarding yes', 'X11 forwarding enabled', 'LOW'),
                ]
                
                for pattern, issue, severity in security_checks:
                    if pattern in config_content:
                        finding = InfraSecurityFinding(
                            category='SSH Configuration',
                            severity=severity,
                            issue=issue,
                            details=f'Found in {config_path}',
                            recommendation='Review SSH configuration for security best practices'
                        )
                        self.findings.append(finding)
                        
            except Exception as e:
                print(f"Error reading SSH config {config_path}: {e}")

    def scan_running_services(self):
        """Scan for potentially risky running services."""
        print("🔍 Scanning running services...")
        
        # Get list of running services
        output = self.run_command(['ps', 'aux'])
        
        if not output:
            return
        
        risky_services = [
            ('telnetd', 'Telnet daemon running', 'HIGH'),
            ('ftpd', 'FTP daemon running', 'MEDIUM'),
            ('rshd', 'RSH daemon running', 'HIGH'),
            ('fingerd', 'Finger daemon running', 'MEDIUM'),
        ]
        
        lines = output.lower().split('\n')
        
        for service, issue, severity in risky_services:
            for line in lines:
                if service in line and 'grep' not in line:
                    finding = InfraSecurityFinding(
                        category='Running Services',
                        severity=severity,
                        issue=issue,
                        details=f'Process found in ps output: {line.strip()}',
                        recommendation=f'Consider disabling {service} if not needed'
                    )
                    self.findings.append(finding)
                    break

    def scan_git_security(self):
        """Scan git configuration for security issues."""
        print("🔍 Scanning git security...")
        
        # Check if .env files are tracked in git
        try:
            os.chdir(self.repo_path)
            
            # Check if .env files are in git history
            env_in_git = self.run_command(['git', 'log', '--all', '--full-history', '--', '*.env'])
            
            if env_in_git:
                finding = InfraSecurityFinding(
                    category='Git Security',
                    severity='HIGH',
                    issue='.env files found in git history',
                    details='Environment files may contain secrets in git history',
                    recommendation='Remove .env files from git history and add to .gitignore'
                )
                self.findings.append(finding)
            
            # Check .gitignore for common patterns
            gitignore_path = self.repo_path / '.gitignore'
            if gitignore_path.exists():
                with open(gitignore_path, 'r') as f:
                    gitignore_content = f.read().lower()
                
                important_patterns = [
                    '.env',
                    '*.key',
                    '*.pem',
                    'secrets.json',
                    'credentials.json',
                ]
                
                missing_patterns = []
                for pattern in important_patterns:
                    if pattern not in gitignore_content:
                        missing_patterns.append(pattern)
                
                if missing_patterns:
                    finding = InfraSecurityFinding(
                        category='Git Security',
                        severity='MEDIUM',
                        issue='Important patterns missing from .gitignore',
                        details=f'Missing patterns: {", ".join(missing_patterns)}',
                        recommendation='Add sensitive file patterns to .gitignore'
                    )
                    self.findings.append(finding)
            else:
                finding = InfraSecurityFinding(
                    category='Git Security',
                    severity='MEDIUM',
                    issue='No .gitignore file found',
                    details='Repository lacks .gitignore file',
                    recommendation='Create .gitignore to prevent committing sensitive files'
                )
                self.findings.append(finding)
                
        except Exception as e:
            print(f"Error scanning git security: {e}")

    def scan_environment_variables(self):
        """Scan for sensitive information in environment variables."""
        print("🔍 Scanning environment variables...")
        
        env_vars = dict(os.environ)
        sensitive_patterns = [
            'password', 'secret', 'key', 'token', 'credential',
            'api_key', 'private_key', 'access_key'
        ]
        
        for var_name, var_value in env_vars.items():
            var_name_lower = var_name.lower()
            
            # Check if environment variable name contains sensitive terms
            if any(pattern in var_name_lower for pattern in sensitive_patterns):
                # Don't log the actual value for security
                finding = InfraSecurityFinding(
                    category='Environment Variables',
                    severity='LOW',
                    issue=f'Sensitive environment variable detected: {var_name}',
                    details='Environment variable name suggests sensitive content',
                    recommendation='Ensure sensitive env vars are properly secured'
                )
                self.findings.append(finding)

    def scan_world_readable_files(self):
        """Scan for world-readable sensitive files."""
        print("🔍 Scanning for world-readable sensitive files...")
        
        # Common sensitive file patterns
        sensitive_files = [
            '*.pem',
            '*.key',
            '*.p12',
            '*.pfx',
            '*private*',
            '*secret*',
            '*credential*',
        ]
        
        for pattern in sensitive_files:
            for file_path in self.repo_path.rglob(pattern):
                if file_path.is_file():
                    try:
                        file_stat = file_path.stat()
                        mode = file_stat.st_mode
                        
                        if mode & (stat.S_IROTH | stat.S_IRGRP):
                            finding = InfraSecurityFinding(
                                category='File Permissions',
                                severity='HIGH',
                                issue=f'Sensitive file readable by others: {file_path.relative_to(self.repo_path)}',
                                details=f'File permissions: {oct(mode)[-3:]}',
                                recommendation='Restrict file permissions (chmod 600)'
                            )
                            self.findings.append(finding)
                            
                    except Exception:
                        pass

    def run_all_scans(self):
        """Run all infrastructure security scans."""
        print(f"🚀 Starting infrastructure security scans for: {self.repo_path}")
        
        self.scan_open_ports()
        self.scan_file_permissions()
        self.scan_ssh_config()
        self.scan_running_services()
        self.scan_git_security()
        self.scan_environment_variables()
        self.scan_world_readable_files()
        
        print(f"\n✅ Infrastructure security scans complete")
        return self.findings

    def generate_report(self) -> str:
        """Generate infrastructure security report."""
        if not self.findings:
            return "✅ No infrastructure security issues found!"

        # Group findings by severity and category
        by_severity = {'CRITICAL': [], 'HIGH': [], 'MEDIUM': [], 'LOW': []}
        by_category = {}
        
        for finding in self.findings:
            by_severity[finding.severity].append(finding)
            if finding.category not in by_category:
                by_category[finding.category] = []
            by_category[finding.category].append(finding)

        report = []
        report.append("# Infrastructure Security Scan Results")
        report.append(f"**Total Issues Found:** {len(self.findings)}")
        report.append("")

        # Summary by severity
        for severity, findings in by_severity.items():
            if findings:
                report.append(f"**{severity}:** {len(findings)} issues")

        report.append("")

        # Summary by category
        report.append("## Issues by Category")
        for category, findings in by_category.items():
            report.append(f"**{category}:** {len(findings)} issues")
        report.append("")

        # Detailed findings by severity
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            if by_severity[severity]:
                report.append(f"## {severity} Severity Issues")
                report.append("")
                
                for finding in by_severity[severity]:
                    report.append(f"### {finding.category}: {finding.issue}")
                    if finding.details:
                        report.append(f"**Details:** {finding.details}")
                    if finding.recommendation:
                        report.append(f"**Recommendation:** {finding.recommendation}")
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
    
    scanner = InfrastructureScanner(repo_path)
    findings = scanner.run_all_scans()
    
    print(f"\n🔍 Infrastructure Security Scan Complete")
    print(f"Found {len(findings)} infrastructure issues")
    
    # Save results
    output_dir = Path(repo_path) / "tools" / "security"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    scanner.save_results(str(output_dir / "infrastructure_scan_results.json"))
    
    # Print summary
    if findings:
        by_severity = {}
        for finding in findings:
            by_severity[finding.severity] = by_severity.get(finding.severity, 0) + 1
        
        print("\nSummary by severity:")
        for severity, count in by_severity.items():
            print(f"  {severity}: {count}")
    else:
        print("✅ No infrastructure issues found!")


if __name__ == "__main__":
    from pathlib import Path
    main()