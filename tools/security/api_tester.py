#!/usr/bin/env python3
"""
API Security Tester
====================
Tests API endpoints for common security vulnerabilities.
"""

import json
import os
import time
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, List, Optional, Tuple


class APISecurityFinding:
    def __init__(self, endpoint: str, method: str, severity: str, issue: str, details: str = ""):
        self.endpoint = endpoint
        self.method = method
        self.severity = severity
        self.issue = issue
        self.details = details

    def to_dict(self):
        return {
            'endpoint': self.endpoint,
            'method': self.method,
            'severity': self.severity,
            'issue': self.issue,
            'details': self.details
        }


class APISecurityTester:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.findings = []
        
        # Safe test payloads (non-destructive)
        self.sql_payloads = [
            "' OR '1'='1",
            "' UNION SELECT NULL--",
            "'; DROP TABLE users; --",
            "1' OR '1'='1' --",
            "admin'/*",
            "' OR 1=1 #",
        ]
        
        self.xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "';alert('XSS');//",
            "<svg onload=alert('XSS')>",
        ]
        
        self.common_endpoints = [
            '/health',
            '/api/products',
            '/api/status',
            '/api/version',
            '/admin',
            '/debug',
            '/api/users',
            '/api/auth',
            '/api/login',
            '/robots.txt',
            '/.env',
            '/.git/config',
            '/api',
            '/docs',
            '/swagger',
            '/openapi.json',
        ]

    def make_request(self, url: str, method: str = 'GET', data: Optional[str] = None, 
                    headers: Optional[Dict[str, str]] = None, timeout: int = 10) -> Tuple[int, Dict[str, str], str]:
        """Make HTTP request and return status code, headers, and body."""
        try:
            req_headers = {'User-Agent': 'SecurityTester/1.0'}
            if headers:
                req_headers.update(headers)
            
            if method == 'POST' and data:
                data = data.encode('utf-8')
                req_headers['Content-Type'] = 'application/json'
            
            req = urllib.request.Request(url, data=data, headers=req_headers)
            req.get_method = lambda: method
            
            with urllib.request.urlopen(req, timeout=timeout) as response:
                status_code = response.getcode()
                response_headers = dict(response.headers)
                body = response.read().decode('utf-8', errors='ignore')
                return status_code, response_headers, body
                
        except urllib.error.HTTPError as e:
            return e.code, dict(e.headers), e.read().decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"Request error for {url}: {e}")
            return 0, {}, str(e)

    def test_endpoint_discovery(self):
        """Test for exposed endpoints and information disclosure."""
        print("🔍 Testing endpoint discovery...")
        
        for endpoint in self.common_endpoints:
            url = f"{self.base_url}{endpoint}"
            status_code, headers, body = self.make_request(url)
            
            if status_code == 200:
                print(f"  Found: {endpoint} (200 OK)")
                
                # Check for sensitive information in response
                body_lower = body.lower()
                if any(word in body_lower for word in ['password', 'secret', 'token', 'key', 'database']):
                    finding = APISecurityFinding(
                        endpoint=endpoint,
                        method='GET',
                        severity='HIGH',
                        issue='Information disclosure - sensitive data in response',
                        details=f"Response contains sensitive keywords: {url}"
                    )
                    self.findings.append(finding)
                
                # Check for debug information
                if any(word in body_lower for word in ['debug', 'traceback', 'error', 'exception']):
                    finding = APISecurityFinding(
                        endpoint=endpoint,
                        method='GET',
                        severity='MEDIUM',
                        issue='Information disclosure - debug information in response',
                        details=f"Response contains debug information: {url}"
                    )
                    self.findings.append(finding)
                    
            elif status_code == 403:
                print(f"  Forbidden: {endpoint} (403) - endpoint exists but access denied")
            elif status_code == 401:
                print(f"  Unauthorized: {endpoint} (401) - requires authentication")

    def test_security_headers(self):
        """Test for security headers."""
        print("🔍 Testing security headers...")
        
        url = f"{self.base_url}/"
        status_code, headers, body = self.make_request(url)
        
        if status_code == 0:
            return
        
        # Check for important security headers
        security_headers = {
            'X-Frame-Options': 'Missing X-Frame-Options header - clickjacking vulnerability',
            'X-Content-Type-Options': 'Missing X-Content-Type-Options header - MIME sniffing vulnerability',
            'Content-Security-Policy': 'Missing Content-Security-Policy header - XSS vulnerability',
            'Strict-Transport-Security': 'Missing HSTS header - insecure transport',
            'X-XSS-Protection': 'Missing X-XSS-Protection header - XSS vulnerability',
            'Referrer-Policy': 'Missing Referrer-Policy header - information disclosure',
        }
        
        for header, issue in security_headers.items():
            if header.lower() not in [h.lower() for h in headers.keys()]:
                finding = APISecurityFinding(
                    endpoint='/',
                    method='GET',
                    severity='MEDIUM',
                    issue=issue,
                    details=f"Header '{header}' not found in response"
                )
                self.findings.append(finding)
        
        # Check for information disclosure headers
        disclosure_headers = ['Server', 'X-Powered-By', 'X-AspNet-Version']
        for header in disclosure_headers:
            if header.lower() in [h.lower() for h in headers.keys()]:
                finding = APISecurityFinding(
                    endpoint='/',
                    method='GET',
                    severity='LOW',
                    issue=f'Information disclosure in {header} header',
                    details=f"Header '{header}' reveals server information: {headers.get(header, '')}"
                )
                self.findings.append(finding)

    def test_cors(self):
        """Test CORS configuration."""
        print("🔍 Testing CORS configuration...")
        
        test_origins = [
            'https://evil.com',
            'http://evil.com',
            'null',
            '*',
        ]
        
        for origin in test_origins:
            headers = {'Origin': origin}
            status_code, response_headers, body = self.make_request(self.base_url, headers=headers)
            
            cors_origin = response_headers.get('Access-Control-Allow-Origin', '')
            
            if cors_origin == '*':
                finding = APISecurityFinding(
                    endpoint='/',
                    method='GET',
                    severity='HIGH',
                    issue='Overly permissive CORS policy',
                    details='Access-Control-Allow-Origin: * allows any origin'
                )
                self.findings.append(finding)
                break
            elif cors_origin == origin:
                finding = APISecurityFinding(
                    endpoint='/',
                    method='GET',
                    severity='MEDIUM',
                    issue='CORS policy reflects arbitrary origins',
                    details=f'Origin {origin} is reflected in Access-Control-Allow-Origin'
                )
                self.findings.append(finding)

    def test_sql_injection(self):
        """Test for SQL injection vulnerabilities."""
        print("🔍 Testing for SQL injection...")
        
        # Test common endpoints with SQL injection payloads
        test_endpoints = [
            '/api/products',
            '/api/search',
            '/api/users',
        ]
        
        for endpoint in test_endpoints:
            url = f"{self.base_url}{endpoint}"
            
            # Test GET parameters
            for payload in self.sql_payloads:
                test_url = f"{url}?search={urllib.parse.quote(payload)}"
                status_code, headers, body = self.make_request(test_url)
                
                if status_code == 0:
                    continue
                
                # Look for SQL error messages
                error_patterns = [
                    'mysql', 'postgresql', 'sqlite', 'oracle', 'sql syntax',
                    'syntax error', 'database error', 'table doesn\'t exist',
                    'column not found', 'constraint', 'foreign key'
                ]
                
                body_lower = body.lower()
                for pattern in error_patterns:
                    if pattern in body_lower:
                        finding = APISecurityFinding(
                            endpoint=endpoint,
                            method='GET',
                            severity='CRITICAL',
                            issue='Potential SQL injection vulnerability',
                            details=f'SQL error message detected with payload: {payload}'
                        )
                        self.findings.append(finding)
                        break

    def test_xss(self):
        """Test for XSS vulnerabilities."""
        print("🔍 Testing for XSS...")
        
        test_endpoints = [
            '/api/products',
            '/api/search',
        ]
        
        for endpoint in test_endpoints:
            url = f"{self.base_url}{endpoint}"
            
            for payload in self.xss_payloads:
                test_url = f"{url}?q={urllib.parse.quote(payload)}"
                status_code, headers, body = self.make_request(test_url)
                
                if status_code == 0:
                    continue
                
                # Check if payload is reflected in response
                if payload in body or payload.replace('"', '&quot;') in body:
                    finding = APISecurityFinding(
                        endpoint=endpoint,
                        method='GET',
                        severity='HIGH',
                        issue='Potential XSS vulnerability',
                        details=f'Payload reflected in response: {payload}'
                    )
                    self.findings.append(finding)

    def test_rate_limiting(self):
        """Test for rate limiting."""
        print("🔍 Testing rate limiting...")
        
        url = f"{self.base_url}/"
        
        # Make multiple requests quickly
        request_count = 20
        start_time = time.time()
        
        status_codes = []
        for i in range(request_count):
            status_code, headers, body = self.make_request(url)
            status_codes.append(status_code)
            
            # Small delay to avoid overwhelming the server
            time.sleep(0.1)
        
        end_time = time.time()
        
        # Check if any requests were rate limited (429, 503, etc.)
        rate_limited = any(code in [429, 503, 509] for code in status_codes)
        
        if not rate_limited:
            finding = APISecurityFinding(
                endpoint='/',
                method='GET',
                severity='MEDIUM',
                issue='No rate limiting detected',
                details=f'Made {request_count} requests in {end_time - start_time:.2f}s with no rate limiting'
            )
            self.findings.append(finding)

    def test_https_redirect(self):
        """Test if HTTP redirects to HTTPS."""
        if not self.base_url.startswith('https://'):
            return
            
        print("🔍 Testing HTTPS redirect...")
        
        # Test if HTTP version redirects to HTTPS
        http_url = self.base_url.replace('https://', 'http://')
        
        try:
            req = urllib.request.Request(http_url)
            urllib.request.urlopen(req, timeout=10)
            
            # If we get here without exception, there's no redirect to HTTPS
            finding = APISecurityFinding(
                endpoint='/',
                method='GET',
                severity='MEDIUM',
                issue='HTTP endpoint does not redirect to HTTPS',
                details=f'HTTP version accessible at: {http_url}'
            )
            self.findings.append(finding)
            
        except urllib.error.HTTPError as e:
            if e.code in [301, 302, 303, 307, 308]:
                # Good - redirects to HTTPS
                pass
        except Exception:
            # Connection error is expected if HTTP is blocked
            pass

    def run_all_tests(self):
        """Run all security tests."""
        print(f"🚀 Starting API security tests for: {self.base_url}")
        
        self.test_endpoint_discovery()
        self.test_security_headers()
        self.test_cors()
        self.test_sql_injection()
        self.test_xss()
        self.test_rate_limiting()
        self.test_https_redirect()
        
        print(f"\n✅ API security tests complete")
        return self.findings

    def generate_report(self) -> str:
        """Generate API security test report."""
        if not self.findings:
            return f"✅ No API security issues found for {self.base_url}!"

        # Group findings by severity
        by_severity = {'CRITICAL': [], 'HIGH': [], 'MEDIUM': [], 'LOW': []}
        for finding in self.findings:
            by_severity[finding.severity].append(finding)

        report = []
        report.append(f"# API Security Test Results")
        report.append(f"**Base URL:** {self.base_url}")
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
                    report.append(f"### {finding.endpoint} ({finding.method})")
                    report.append(f"**Issue:** {finding.issue}")
                    if finding.details:
                        report.append(f"**Details:** {finding.details}")
                    report.append("")

        return '\n'.join(report)

    def save_results(self, output_path: str):
        """Save test results to JSON file."""
        results = {
            'test_time': os.popen('date -Iseconds').read().strip(),
            'base_url': self.base_url,
            'total_findings': len(self.findings),
            'findings': [finding.to_dict() for finding in self.findings]
        }
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Results saved to: {output_path}")


def main():
    import sys
    
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "https://mywork-ai-production.up.railway.app"
    
    tester = APISecurityTester(base_url)
    findings = tester.run_all_tests()
    
    print(f"\n🔍 API Security Test Complete")
    print(f"Found {len(findings)} security issues")
    
    # Save results
    repo_path = Path(__file__).parent.parent.parent
    output_dir = Path(repo_path) / "tools" / "security"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    tester.save_results(str(output_dir / "api_security_results.json"))
    
    # Print summary
    if findings:
        by_severity = {}
        for finding in findings:
            by_severity[finding.severity] = by_severity.get(finding.severity, 0) + 1
        
        print("\nSummary by severity:")
        for severity, count in by_severity.items():
            print(f"  {severity}: {count}")
    else:
        print("✅ No API security issues found!")


if __name__ == "__main__":
    from pathlib import Path
    main()