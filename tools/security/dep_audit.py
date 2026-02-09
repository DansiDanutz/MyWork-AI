#!/usr/bin/env python3
"""
Dependency Security Auditor
============================
Checks package dependencies for known vulnerabilities and outdated versions.
"""

import json
import os
import re
import subprocess
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class DependencyFinding:
    def __init__(self, package: str, version: str, severity: str, issue: str, recommendation: str = ""):
        self.package = package
        self.version = version
        self.severity = severity
        self.issue = issue
        self.recommendation = recommendation

    def to_dict(self):
        return {
            'package': self.package,
            'version': self.version,
            'severity': self.severity,
            'issue': self.issue,
            'recommendation': self.recommendation
        }


class DependencyAuditor:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.findings = []
        
        # Known vulnerable versions (basic set - in production this would be much more comprehensive)
        self.known_vulnerabilities = {
            'requests': {
                '2.25.0': {'severity': 'HIGH', 'issue': 'CVE-2021-33503: ReDoS vulnerability'},
                '2.24.0': {'severity': 'MEDIUM', 'issue': 'CVE-2020-26137: HTTP header injection'},
            },
            'flask': {
                '1.0.0': {'severity': 'HIGH', 'issue': 'CVE-2019-1010083: Path traversal'},
                '0.12.0': {'severity': 'CRITICAL', 'issue': 'CVE-2018-1000656: Denial of service'},
            },
            'django': {
                '3.0.0': {'severity': 'HIGH', 'issue': 'CVE-2020-7471: SQL injection'},
                '2.2.0': {'severity': 'MEDIUM', 'issue': 'CVE-2019-19844: Account hijack via password reset'},
            },
            'pillow': {
                '8.1.0': {'severity': 'HIGH', 'issue': 'CVE-2021-25290: Buffer overflow'},
                '7.0.0': {'severity': 'CRITICAL', 'issue': 'CVE-2020-5313: Buffer overflow'},
            },
            'pyyaml': {
                '5.3.0': {'severity': 'CRITICAL', 'issue': 'CVE-2020-1747: Arbitrary code execution'},
                '3.13': {'severity': 'CRITICAL', 'issue': 'CVE-2017-18342: Arbitrary code execution'},
            },
            'httpx': {
                '0.20.0': {'severity': 'MEDIUM', 'issue': 'Potential SSRF vulnerabilities in early versions'},
            },
        }

    def parse_requirements_txt(self, file_path: Path) -> List[Tuple[str, str]]:
        """Parse requirements.txt file and extract package names and versions."""
        packages = []
        
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    # Handle different version specifiers
                    for operator in ['==', '>=', '<=', '>', '<', '~=', '!=']:
                        if operator in line:
                            package, version = line.split(operator, 1)
                            packages.append((package.strip(), version.strip()))
                            break
                    else:
                        # No version specified
                        packages.append((line.strip(), 'latest'))
                        
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            
        return packages

    def parse_setup_py(self, file_path: Path) -> List[Tuple[str, str]]:
        """Parse setup.py file and extract dependencies."""
        packages = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Look for install_requires or requirements
            patterns = [
                r'install_requires\s*=\s*\[(.*?)\]',
                r'requirements\s*=\s*\[(.*?)\]',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    deps_str = match.group(1)
                    # Extract quoted strings
                    for dep_match in re.finditer(r'["\']([^"\']+)["\']', deps_str):
                        dep = dep_match.group(1).strip()
                        if dep and not dep.startswith('#'):
                            # Parse package name and version
                            for operator in ['==', '>=', '<=', '>', '<', '~=', '!=']:
                                if operator in dep:
                                    package, version = dep.split(operator, 1)
                                    packages.append((package.strip(), version.strip()))
                                    break
                            else:
                                packages.append((dep.strip(), 'latest'))
                                
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            
        return packages

    def check_pip_audit(self) -> List[DependencyFinding]:
        """Try to use pip-audit if available."""
        findings = []
        
        try:
            # Check if pip-audit is available
            result = subprocess.run(['pip', 'show', 'pip-audit'], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                print("pip-audit not installed, skipping automated vulnerability check")
                return findings
            
            # Run pip-audit
            result = subprocess.run(['pip-audit', '--format=json', '--desc'], 
                                  capture_output=True, text=True, 
                                  cwd=self.repo_path)
            
            if result.returncode == 0 and result.stdout:
                audit_data = json.loads(result.stdout)
                
                for vuln in audit_data.get('vulnerabilities', []):
                    finding = DependencyFinding(
                        package=vuln.get('package', ''),
                        version=vuln.get('installed_version', ''),
                        severity='HIGH',
                        issue=f"CVE: {vuln.get('id', '')}: {vuln.get('description', '')}",
                        recommendation=f"Upgrade to {vuln.get('fixed_versions', ['latest'])[0]}"
                    )
                    findings.append(finding)
                    
        except Exception as e:
            print(f"Error running pip-audit: {e}")
            
        return findings

    def check_pypi_latest(self, package_name: str, current_version: str) -> Optional[str]:
        """Check PyPI for the latest version of a package."""
        try:
            url = f"https://pypi.org/pypi/{package_name}/json"
            
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())
                latest_version = data['info']['version']
                return latest_version
                
        except Exception as e:
            print(f"Error checking PyPI for {package_name}: {e}")
            return None

    def version_compare(self, version1: str, version2: str) -> int:
        """Compare two version strings. Returns -1 if v1 < v2, 0 if equal, 1 if v1 > v2."""
        try:
            # Simple version comparison (not fully semantic versioning compliant)
            v1_parts = [int(x) for x in version1.split('.') if x.isdigit()]
            v2_parts = [int(x) for x in version2.split('.') if x.isdigit()]
            
            # Pad with zeros
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))
            
            for i in range(max_len):
                if v1_parts[i] < v2_parts[i]:
                    return -1
                elif v1_parts[i] > v2_parts[i]:
                    return 1
            return 0
            
        except Exception:
            # Fallback to string comparison
            return -1 if version1 < version2 else (1 if version1 > version2 else 0)

    def audit_dependencies(self) -> List[DependencyFinding]:
        """Audit all dependencies for vulnerabilities and outdated versions."""
        print(f"Auditing dependencies in: {self.repo_path}")
        
        all_packages = []
        findings = []
        
        # Find and parse dependency files
        req_files = list(self.repo_path.rglob('requirements*.txt'))
        setup_files = list(self.repo_path.glob('setup.py'))
        pyproject_files = list(self.repo_path.glob('pyproject.toml'))
        
        print(f"Found {len(req_files)} requirements files, {len(setup_files)} setup.py files")
        
        # Parse requirements.txt files
        for req_file in req_files:
            packages = self.parse_requirements_txt(req_file)
            all_packages.extend(packages)
            print(f"Found {len(packages)} dependencies in {req_file}")
        
        # Parse setup.py files
        for setup_file in setup_files:
            packages = self.parse_setup_py(setup_file)
            all_packages.extend(packages)
            print(f"Found {len(packages)} dependencies in {setup_file}")
        
        # Remove duplicates
        unique_packages = list(set(all_packages))
        print(f"Total unique packages: {len(unique_packages)}")
        
        # Check for known vulnerabilities
        for package, version in unique_packages:
            if package in self.known_vulnerabilities:
                vuln_versions = self.known_vulnerabilities[package]
                
                # Check if current version is vulnerable
                for vuln_version, vuln_info in vuln_versions.items():
                    if version == vuln_version or version == 'latest':
                        finding = DependencyFinding(
                            package=package,
                            version=version,
                            severity=vuln_info['severity'],
                            issue=vuln_info['issue'],
                            recommendation="Update to a patched version"
                        )
                        findings.append(finding)
            
            # Check if package is outdated (only for packages with specific versions)
            if version != 'latest' and not any(op in version for op in ['>', '<', '~']):
                latest_version = self.check_pypi_latest(package, version)
                if latest_version and self.version_compare(version, latest_version) < 0:
                    # Package is outdated
                    finding = DependencyFinding(
                        package=package,
                        version=version,
                        severity='LOW',
                        issue=f"Outdated version (latest: {latest_version})",
                        recommendation=f"Consider updating to {latest_version}"
                    )
                    findings.append(finding)
        
        # Try pip-audit for additional checks
        pip_audit_findings = self.check_pip_audit()
        findings.extend(pip_audit_findings)
        
        self.findings = findings
        return findings

    def generate_report(self) -> str:
        """Generate dependency audit report."""
        if not self.findings:
            return "✅ No dependency security issues found!"

        # Group findings by severity
        by_severity = {'CRITICAL': [], 'HIGH': [], 'MEDIUM': [], 'LOW': []}
        for finding in self.findings:
            by_severity[finding.severity].append(finding)

        report = []
        report.append("# Dependency Security Audit Results")
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
                    report.append(f"### {finding.package} v{finding.version}")
                    report.append(f"**Issue:** {finding.issue}")
                    if finding.recommendation:
                        report.append(f"**Recommendation:** {finding.recommendation}")
                    report.append("")

        return '\n'.join(report)

    def save_results(self, output_path: str):
        """Save audit results to JSON file."""
        results = {
            'audit_time': os.popen('date -Iseconds').read().strip(),
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
    
    auditor = DependencyAuditor(repo_path)
    findings = auditor.audit_dependencies()
    
    print(f"\n🔍 Dependency Audit Complete")
    print(f"Found {len(findings)} dependency issues")
    
    # Save results
    output_dir = Path(repo_path) / "tools" / "security"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    auditor.save_results(str(output_dir / "dependency_audit_results.json"))
    
    # Print summary
    if findings:
        by_severity = {}
        for finding in findings:
            by_severity[finding.severity] = by_severity.get(finding.severity, 0) + 1
        
        print("\nSummary by severity:")
        for severity, count in by_severity.items():
            print(f"  {severity}: {count}")
    else:
        print("✅ No dependency issues found!")


if __name__ == "__main__":
    main()