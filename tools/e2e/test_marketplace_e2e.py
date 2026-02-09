#!/usr/bin/env python3
"""
E2E Test: Marketplace Smoke Tests
=================================
Tests live endpoints for frontend and backend services.
Verifies response codes, content types, broken links, response times, and SSL certificates.
"""

import requests
import sys
import json
import time
import ssl
import socket
from pathlib import Path
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin, urlparse
import warnings

# Disable SSL warnings for testing
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

class MarketplaceE2ETester:
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
        # Endpoints to test
        self.frontend_base = "https://frontend-hazel-ten-17.vercel.app"
        self.backend_base = "https://mywork-ai-production.up.railway.app"
        
        self.frontend_endpoints = [
            "/",  # home
            "/products",  # products page
            "/pricing",  # pricing page
            "/status"  # status page
        ]
        
        self.backend_endpoints = [
            "/health",  # health check
            "/api/products"  # API products
        ]
        
        # Request timeout and retry settings
        self.timeout = 30
        self.max_retries = 2
        
    def log_result(self, test_name: str, status: str, message: str = "", details: Dict = None):
        """Log a test result"""
        self.total_tests += 1
        if status == "PASS":
            self.passed_tests += 1
        elif status == "FAIL":
            self.failed_tests += 1
            
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "details": details or {},
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.results.append(result)
        print(f"[{status}] {test_name}: {message}")
        if details:
            for key, value in details.items():
                if isinstance(value, (int, float, str)) and len(str(value)) < 100:
                    print(f"  {key}: {value}")
        
    def make_request(self, url: str, method: str = "GET") -> Dict[str, Any]:
        """Make HTTP request with error handling and timing"""
        start_time = time.time()
        
        try:
            response = requests.request(
                method=method,
                url=url,
                timeout=self.timeout,
                verify=False,  # Skip SSL verification for testing
                allow_redirects=True,
                headers={
                    'User-Agent': 'MyWork-AI E2E Tester'
                }
            )
            
            end_time = time.time()
            response_time = round((end_time - start_time) * 1000, 2)  # Convert to ms
            
            return {
                "success": True,
                "status_code": response.status_code,
                "response_time_ms": response_time,
                "content_type": response.headers.get('content-type', 'unknown'),
                "content_length": len(response.content),
                "headers": dict(response.headers),
                "content": response.text[:1000],  # First 1KB for inspection
                "url": response.url,  # Final URL after redirects
                "error": None
            }
            
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": f"Request timed out after {self.timeout}s",
                "response_time_ms": self.timeout * 1000
            }
        except requests.exceptions.ConnectionError as e:
            return {
                "success": False,
                "error": f"Connection error: {str(e)}",
                "response_time_ms": None
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Request failed: {str(e)}",
                "response_time_ms": None
            }
    
    def test_ssl_certificate(self, hostname: str):
        """Test SSL certificate validity"""
        try:
            # Parse hostname from URL if full URL provided
            if hostname.startswith('http'):
                hostname = urlparse(hostname).netloc
            
            # Create SSL context
            context = ssl.create_default_context()
            
            # Connect and get certificate
            with socket.create_connection((hostname, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Check expiry
                    not_after = cert.get('notAfter')
                    subject = dict(x[0] for x in cert['subject'])
                    
                    self.log_result(f"ssl_cert_{hostname.replace('.', '_')}", "PASS", 
                                  f"SSL certificate valid until {not_after}",
                                  {"subject": subject.get('commonName', 'unknown'), "expires": not_after})
                    
        except Exception as e:
            self.log_result(f"ssl_cert_{hostname.replace('.', '_')}", "FAIL", 
                          f"SSL certificate check failed: {str(e)}")
    
    def test_frontend_endpoints(self):
        """Test frontend endpoints"""
        print(f"\n--- Testing Frontend: {self.frontend_base} ---")
        
        for endpoint in self.frontend_endpoints:
            url = urljoin(self.frontend_base, endpoint)
            result = self.make_request(url)
            
            test_name = f"frontend_{endpoint.strip('/') or 'home'}"
            
            if not result["success"]:
                self.log_result(test_name, "FAIL", f"Request failed: {result['error']}")
                continue
            
            status_code = result["status_code"]
            response_time = result["response_time_ms"]
            content_type = result["content_type"]
            
            # Determine test result
            if status_code == 200:
                status = "PASS"
                message = f"OK ({response_time}ms)"
            elif 300 <= status_code < 400:
                status = "PASS" 
                message = f"Redirect ({status_code}, {response_time}ms)"
            elif status_code == 404 and endpoint in ["/status"]:  # Some endpoints might not exist
                status = "WARN"
                message = f"Not found (acceptable for {endpoint})"
            else:
                status = "FAIL"
                message = f"HTTP {status_code} ({response_time}ms)"
            
            details = {
                "url": url,
                "status_code": status_code,
                "response_time_ms": response_time,
                "content_type": content_type,
                "content_length": result["content_length"]
            }
            
            # Check for common issues
            if response_time > 5000:  # > 5 seconds
                details["warning"] = "Slow response time"
            
            if "html" in content_type.lower():
                # Basic HTML validation
                content = result["content"].lower()
                if "<html" in content or "<!doctype" in content:
                    details["html_structure"] = "valid"
                else:
                    details["html_structure"] = "questionable"
            
            self.log_result(test_name, status, message, details)
    
    def test_backend_endpoints(self):
        """Test backend API endpoints"""
        print(f"\n--- Testing Backend: {self.backend_base} ---")
        
        for endpoint in self.backend_endpoints:
            url = urljoin(self.backend_base, endpoint)
            result = self.make_request(url)
            
            test_name = f"backend_{endpoint.strip('/').replace('/', '_')}"
            
            if not result["success"]:
                self.log_result(test_name, "FAIL", f"Request failed: {result['error']}")
                continue
            
            status_code = result["status_code"]
            response_time = result["response_time_ms"]
            content_type = result["content_type"]
            
            # Determine test result
            if status_code == 200:
                status = "PASS"
                message = f"OK ({response_time}ms)"
            elif status_code == 404 and "api" not in endpoint:  # Some endpoints might not exist
                status = "WARN"
                message = f"Not found (acceptable for {endpoint})"
            else:
                status = "FAIL"
                message = f"HTTP {status_code} ({response_time}ms)"
            
            details = {
                "url": url,
                "status_code": status_code,
                "response_time_ms": response_time,
                "content_type": content_type,
                "content_length": result["content_length"]
            }
            
            # Check response content for API endpoints
            if "api" in endpoint and "json" in content_type.lower():
                try:
                    # Try to parse JSON response
                    json_content = json.loads(result["content"])
                    details["json_valid"] = True
                    details["json_keys"] = list(json_content.keys()) if isinstance(json_content, dict) else "array"
                except:
                    details["json_valid"] = False
            
            # Check for health check specific content
            if endpoint == "/health":
                content = result["content"].lower()
                if "ok" in content or "healthy" in content or "status" in content:
                    details["health_response"] = "valid"
                else:
                    details["health_response"] = "unexpected"
            
            self.log_result(test_name, status, message, details)
    
    def test_performance(self):
        """Test response times for key endpoints"""
        print("\n--- Performance Testing ---")
        
        key_urls = [
            (self.frontend_base, "frontend_home"),
            (urljoin(self.backend_base, "/health"), "backend_health")
        ]
        
        for url, name in key_urls:
            # Make multiple requests to get average response time
            times = []
            
            for i in range(3):
                result = self.make_request(url)
                if result["success"] and result.get("response_time_ms"):
                    times.append(result["response_time_ms"])
                time.sleep(1)  # Small delay between requests
            
            if times:
                avg_time = sum(times) / len(times)
                min_time = min(times)
                max_time = max(times)
                
                if avg_time < 2000:  # < 2 seconds
                    status = "PASS"
                    message = f"Good performance (avg: {avg_time:.1f}ms)"
                elif avg_time < 5000:  # < 5 seconds
                    status = "WARN"
                    message = f"Acceptable performance (avg: {avg_time:.1f}ms)"
                else:
                    status = "FAIL"
                    message = f"Slow performance (avg: {avg_time:.1f}ms)"
                
                details = {
                    "average_ms": round(avg_time, 1),
                    "min_ms": round(min_time, 1),
                    "max_ms": round(max_time, 1),
                    "requests": len(times)
                }
                
                self.log_result(f"performance_{name}", status, message, details)
            else:
                self.log_result(f"performance_{name}", "FAIL", "Could not measure performance")
    
    def test_broken_links(self):
        """Check for obvious broken links in homepage"""
        print("\n--- Broken Link Detection ---")
        
        # Get homepage content
        result = self.make_request(self.frontend_base)
        
        if not result["success"]:
            self.log_result("broken_links", "SKIP", "Could not fetch homepage for link checking")
            return
        
        content = result["content"]
        
        # Simple regex to find links (basic implementation)
        import re
        
        # Find href attributes
        href_pattern = r'href=["\']([^"\']+)["\']'
        links = re.findall(href_pattern, content)
        
        # Test a few internal links
        internal_links = [link for link in links if not link.startswith('http') and not link.startswith('#')]
        internal_links = internal_links[:5]  # Test first 5 to avoid too many requests
        
        broken_count = 0
        tested_count = 0
        
        for link in internal_links:
            if link.startswith('/'):
                test_url = urljoin(self.frontend_base, link)
                link_result = self.make_request(test_url)
                tested_count += 1
                
                if not link_result["success"] or link_result["status_code"] >= 400:
                    broken_count += 1
        
        if tested_count == 0:
            self.log_result("broken_links", "SKIP", "No internal links found to test")
        elif broken_count == 0:
            self.log_result("broken_links", "PASS", f"No broken links found (tested {tested_count})")
        else:
            self.log_result("broken_links", "WARN", f"{broken_count}/{tested_count} links may be broken")
    
    def test_ssl_certificates(self):
        """Test SSL certificates for both domains"""
        print("\n--- SSL Certificate Testing ---")
        
        domains = [
            urlparse(self.frontend_base).netloc,
            urlparse(self.backend_base).netloc
        ]
        
        for domain in domains:
            self.test_ssl_certificate(domain)
    
    def run_all_tests(self):
        """Run all marketplace smoke tests"""
        print("=== Marketplace E2E Smoke Tests ===")
        print(f"Frontend: {self.frontend_base}")
        print(f"Backend: {self.backend_base}")
        print()
        
        # Test endpoints
        self.test_frontend_endpoints()
        self.test_backend_endpoints()
        
        # Performance tests
        self.test_performance()
        
        # Additional checks
        self.test_broken_links()
        self.test_ssl_certificates()
        
        return self.generate_report()
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate test report"""
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        # Calculate service availability
        frontend_tests = [r for r in self.results if r["test"].startswith("frontend_")]
        backend_tests = [r for r in self.results if r["test"].startswith("backend_")]
        
        frontend_up = len([t for t in frontend_tests if t["status"] == "PASS"])
        backend_up = len([t for t in backend_tests if t["status"] == "PASS"])
        
        report = {
            "test_suite": "Marketplace E2E Smoke Tests",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "endpoints_tested": {
                "frontend": {
                    "base_url": self.frontend_base,
                    "endpoints": self.frontend_endpoints,
                    "availability": f"{frontend_up}/{len(frontend_tests)}" if frontend_tests else "0/0"
                },
                "backend": {
                    "base_url": self.backend_base,
                    "endpoints": self.backend_endpoints,
                    "availability": f"{backend_up}/{len(backend_tests)}" if backend_tests else "0/0"
                }
            },
            "summary": {
                "total_tests": self.total_tests,
                "passed": self.passed_tests,
                "failed": self.failed_tests,
                "skipped": 0,
                "success_rate": round(success_rate, 2)
            },
            "results": self.results
        }
        
        print(f"\n=== Marketplace Test Summary ===")
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Frontend Availability: {frontend_up}/{len(frontend_tests) if frontend_tests else 0}")
        print(f"Backend Availability: {backend_up}/{len(backend_tests) if backend_tests else 0}")
        
        return report


def main():
    """Main entry point"""
    tester = MarketplaceE2ETester()
    report = tester.run_all_tests()
    
    # Save report to file
    report_file = Path("/home/Memo1981/MyWork-AI/tools/e2e/marketplace_test_results.json")
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\nReport saved to: {report_file}")
    
    # Exit with appropriate code
    sys.exit(0 if report["summary"]["failed"] == 0 else 1)


if __name__ == "__main__":
    main()