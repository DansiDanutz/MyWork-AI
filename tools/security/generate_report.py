#!/usr/bin/env python3
"""
Security Audit Report Generator
===============================
Runs all security scanners and generates a comprehensive security audit report.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Import our security scanners
sys.path.insert(0, str(Path(__file__).parent))
from code_scanner import CodeSecurityScanner
from dep_audit import DependencyAuditor
from api_tester import APISecurityTester
from infra_scanner import InfrastructureScanner


class SecurityAuditReportGenerator:
    def __init__(self, repo_path: str, api_url: str = "https://mywork-ai-production.up.railway.app"):
        self.repo_path = Path(repo_path)
        self.api_url = api_url
        self.output_dir = self.repo_path / "tools" / "security"
        self.report_dir = self.repo_path / "reports"
        
        # Create directories if they don't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        self.all_findings = {
            'code': [],
            'dependencies': [],
            'api': [],
            'infrastructure': []
        }

    def run_code_scanner(self):
        """Run code security scanner."""
        print("=" * 60)
        print("🔍 RUNNING CODE SECURITY SCANNER")
        print("=" * 60)
        
        scanner = CodeSecurityScanner(str(self.repo_path))
        findings = scanner.scan_repository()
        scanner.save_results(str(self.output_dir / "code_scan_results.json"))
        
        self.all_findings['code'] = findings
        print(f"Code scanner found {len(findings)} issues")
        return findings

    def run_dependency_auditor(self):
        """Run dependency auditor."""
        print("=" * 60)
        print("🔍 RUNNING DEPENDENCY AUDITOR")
        print("=" * 60)
        
        auditor = DependencyAuditor(str(self.repo_path))
        findings = auditor.audit_dependencies()
        auditor.save_results(str(self.output_dir / "dependency_audit_results.json"))
        
        self.all_findings['dependencies'] = findings
        print(f"Dependency auditor found {len(findings)} issues")
        return findings

    def run_api_tester(self):
        """Run API security tester."""
        print("=" * 60)
        print("🔍 RUNNING API SECURITY TESTER")
        print("=" * 60)
        
        tester = APISecurityTester(self.api_url)
        findings = tester.run_all_tests()
        tester.save_results(str(self.output_dir / "api_security_results.json"))
        
        self.all_findings['api'] = findings
        print(f"API tester found {len(findings)} issues")
        return findings

    def run_infrastructure_scanner(self):
        """Run infrastructure security scanner."""
        print("=" * 60)
        print("🔍 RUNNING INFRASTRUCTURE SCANNER")
        print("=" * 60)
        
        scanner = InfrastructureScanner(str(self.repo_path))
        findings = scanner.run_all_scans()
        scanner.save_results(str(self.output_dir / "infrastructure_scan_results.json"))
        
        self.all_findings['infrastructure'] = findings
        print(f"Infrastructure scanner found {len(findings)} issues")
        return findings

    def calculate_risk_score(self):
        """Calculate overall risk score based on findings."""
        severity_weights = {
            'CRITICAL': 10,
            'HIGH': 7,
            'MEDIUM': 4,
            'LOW': 1
        }
        
        total_score = 0
        total_findings = 0
        
        for category, findings in self.all_findings.items():
            for finding in findings:
                severity = getattr(finding, 'severity', 'LOW')
                total_score += severity_weights.get(severity, 1)
                total_findings += 1
        
        if total_findings == 0:
            return 0, "EXCELLENT"
        
        # Risk level based on average score
        avg_score = total_score / total_findings
        
        if avg_score >= 8:
            risk_level = "CRITICAL"
        elif avg_score >= 6:
            risk_level = "HIGH"
        elif avg_score >= 3:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
            
        return round(avg_score, 2), risk_level

    def generate_executive_summary(self):
        """Generate executive summary."""
        total_findings = sum(len(findings) for findings in self.all_findings.values())
        risk_score, risk_level = self.calculate_risk_score()
        
        # Count by severity across all categories
        severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        
        for category, findings in self.all_findings.items():
            for finding in findings:
                severity = getattr(finding, 'severity', 'LOW')
                severity_counts[severity] += 1
        
        summary = []
        summary.append("# 🔒 Security Audit Executive Summary")
        summary.append("")
        summary.append(f"**Audit Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        summary.append(f"**Repository:** {self.repo_path}")
        summary.append(f"**API Endpoint:** {self.api_url}")
        summary.append("")
        summary.append(f"## 📊 Overall Risk Assessment")
        summary.append(f"**Risk Score:** {risk_score}/10")
        summary.append(f"**Risk Level:** {risk_level}")
        summary.append(f"**Total Findings:** {total_findings}")
        summary.append("")
        
        # Findings breakdown
        summary.append("## 📈 Findings Breakdown")
        summary.append("")
        
        if severity_counts['CRITICAL'] > 0:
            summary.append(f"🚨 **CRITICAL:** {severity_counts['CRITICAL']} issues - Immediate attention required")
        if severity_counts['HIGH'] > 0:
            summary.append(f"⚠️ **HIGH:** {severity_counts['HIGH']} issues - Should be addressed soon")
        if severity_counts['MEDIUM'] > 0:
            summary.append(f"🔶 **MEDIUM:** {severity_counts['MEDIUM']} issues - Address when possible")
        if severity_counts['LOW'] > 0:
            summary.append(f"ℹ️ **LOW:** {severity_counts['LOW']} issues - Best practice improvements")
            
        summary.append("")
        
        # Category breakdown
        summary.append("## 🎯 Issues by Category")
        summary.append("")
        
        category_names = {
            'code': 'Code Security',
            'dependencies': 'Dependencies',
            'api': 'API Security',
            'infrastructure': 'Infrastructure'
        }
        
        for category, findings in self.all_findings.items():
            count = len(findings)
            name = category_names.get(category, category)
            
            if count > 0:
                summary.append(f"**{name}:** {count} issues")
            else:
                summary.append(f"**{name}:** ✅ No issues found")
        
        summary.append("")
        
        # Key recommendations
        summary.append("## 🔧 Key Recommendations")
        summary.append("")
        
        if severity_counts['CRITICAL'] > 0:
            summary.append("1. **URGENT:** Address all CRITICAL severity issues immediately")
        if severity_counts['HIGH'] > 0:
            summary.append("2. **Important:** Review and fix HIGH severity issues")
        
        summary.append("3. Implement automated security scanning in CI/CD pipeline")
        summary.append("4. Regular security audits should be conducted quarterly")
        summary.append("5. Consider implementing security monitoring and alerting")
        
        return '\n'.join(summary)

    def generate_detailed_report(self):
        """Generate detailed security audit report."""
        report = []
        
        # Executive summary
        report.append(self.generate_executive_summary())
        report.append("")
        
        # Detailed findings by category
        category_names = {
            'code': 'Code Security Scanner Results',
            'dependencies': 'Dependency Audit Results',
            'api': 'API Security Test Results',
            'infrastructure': 'Infrastructure Security Scan Results'
        }
        
        for category, findings in self.all_findings.items():
            if not findings:
                continue
                
            report.append("=" * 60)
            report.append(f"# {category_names.get(category, category)}")
            report.append("=" * 60)
            report.append("")
            
            # Group by severity
            by_severity = {'CRITICAL': [], 'HIGH': [], 'MEDIUM': [], 'LOW': []}
            for finding in findings:
                severity = getattr(finding, 'severity', 'LOW')
                by_severity[severity].append(finding)
            
            # Summary for this category
            report.append(f"**Total Issues:** {len(findings)}")
            report.append("")
            
            for severity, sev_findings in by_severity.items():
                if sev_findings:
                    report.append(f"**{severity}:** {len(sev_findings)} issues")
            report.append("")
            
            # Detailed findings
            for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
                if not by_severity[severity]:
                    continue
                    
                report.append(f"## {severity} Severity Issues")
                report.append("")
                
                for i, finding in enumerate(by_severity[severity], 1):
                    if category == 'code':
                        report.append(f"### {i}. {finding.file_path}:{finding.line_num}")
                        report.append(f"**Issue:** {finding.description}")
                        if finding.code_snippet:
                            report.append(f"**Code:** `{finding.code_snippet}`")
                            
                    elif category == 'dependencies':
                        report.append(f"### {i}. {finding.package} v{finding.version}")
                        report.append(f"**Issue:** {finding.issue}")
                        if finding.recommendation:
                            report.append(f"**Recommendation:** {finding.recommendation}")
                            
                    elif category == 'api':
                        report.append(f"### {i}. {finding.endpoint} ({finding.method})")
                        report.append(f"**Issue:** {finding.issue}")
                        if finding.details:
                            report.append(f"**Details:** {finding.details}")
                            
                    elif category == 'infrastructure':
                        report.append(f"### {i}. {finding.category}: {finding.issue}")
                        if finding.details:
                            report.append(f"**Details:** {finding.details}")
                        if finding.recommendation:
                            report.append(f"**Recommendation:** {finding.recommendation}")
                    
                    report.append("")
        
        return '\n'.join(report)

    def save_consolidated_results(self):
        """Save consolidated results to JSON."""
        # Convert findings to dictionaries
        consolidated = {
            'audit_time': datetime.now().isoformat(),
            'repository': str(self.repo_path),
            'api_url': self.api_url,
            'risk_score': self.calculate_risk_score()[0],
            'risk_level': self.calculate_risk_score()[1],
            'total_findings': sum(len(findings) for findings in self.all_findings.values()),
            'findings_by_category': {}
        }
        
        for category, findings in self.all_findings.items():
            consolidated['findings_by_category'][category] = []
            for finding in findings:
                if hasattr(finding, 'to_dict'):
                    consolidated['findings_by_category'][category].append(finding.to_dict())
                else:
                    # Fallback for objects without to_dict method
                    consolidated['findings_by_category'][category].append(str(finding))
        
        output_file = self.output_dir / "consolidated_security_results.json"
        with open(output_file, 'w') as f:
            json.dump(consolidated, f, indent=2)
        
        print(f"Consolidated results saved to: {output_file}")

    def run_full_audit(self):
        """Run complete security audit."""
        print("🚀 STARTING COMPREHENSIVE SECURITY AUDIT")
        print("=" * 60)
        print(f"Repository: {self.repo_path}")
        print(f"API Endpoint: {self.api_url}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print("=" * 60)
        
        try:
            # Run all scanners
            self.run_code_scanner()
            self.run_dependency_auditor()
            self.run_api_tester()
            self.run_infrastructure_scanner()
            
            print("=" * 60)
            print("📊 GENERATING COMPREHENSIVE REPORT")
            print("=" * 60)
            
            # Generate and save report
            report = self.generate_detailed_report()
            
            # Save report
            today = datetime.now().strftime('%Y-%m-%d')
            report_filename = f"security_audit_{today}.md"
            report_path = self.report_dir / report_filename
            
            with open(report_path, 'w') as f:
                f.write(report)
            
            print(f"✅ Comprehensive security audit report saved to: {report_path}")
            
            # Save consolidated JSON results
            self.save_consolidated_results()
            
            # Print summary
            total_findings = sum(len(findings) for findings in self.all_findings.values())
            risk_score, risk_level = self.calculate_risk_score()
            
            print("=" * 60)
            print("🎯 AUDIT SUMMARY")
            print("=" * 60)
            print(f"Total findings: {total_findings}")
            print(f"Risk score: {risk_score}/10")
            print(f"Risk level: {risk_level}")
            
            if total_findings > 0:
                severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
                for findings in self.all_findings.values():
                    for finding in findings:
                        severity = getattr(finding, 'severity', 'LOW')
                        severity_counts[severity] += 1
                
                print("\nBreakdown by severity:")
                for severity, count in severity_counts.items():
                    if count > 0:
                        print(f"  {severity}: {count}")
            
            return report_path, total_findings, risk_level
            
        except Exception as e:
            print(f"❌ Error during security audit: {e}")
            import traceback
            traceback.print_exc()
            return None, 0, "ERROR"


def main():
    if len(sys.argv) > 1:
        repo_path = sys.argv[1]
    else:
        repo_path = "/home/Memo1981/MyWork-AI"
    
    if len(sys.argv) > 2:
        api_url = sys.argv[2]
    else:
        api_url = "https://mywork-ai-production.up.railway.app"
    
    generator = SecurityAuditReportGenerator(repo_path, api_url)
    report_path, findings_count, risk_level = generator.run_full_audit()
    
    if report_path:
        print(f"\n🏁 Security audit complete!")
        print(f"📋 Report: {report_path}")
        print(f"🔍 Found {findings_count} security issues")
        print(f"⚠️ Overall risk level: {risk_level}")
        
        if findings_count > 0:
            print(f"\n📖 Review the detailed report at: {report_path}")
        else:
            print(f"\n✅ No security issues found - excellent work!")
    else:
        print("❌ Security audit failed")
        sys.exit(1)


if __name__ == "__main__":
    main()