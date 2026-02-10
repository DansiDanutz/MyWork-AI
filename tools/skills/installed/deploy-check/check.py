#!/usr/bin/env python3
"""
Deploy Check Skill - Pre-deployment Checklist
============================================
Comprehensive deployment readiness validation.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple

class DeploymentChecker:
    def __init__(self, environment: str = "production"):
        self.environment = environment
        self.project_root = Path.cwd()
        self.checks = []
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        
        # Load configuration
        config_path = Path(os.environ.get('SKILL_PATH', '.')) / 'config.json'
        if config_path.exists():
            with open(config_path) as f:
                self.config = json.load(f)
        else:
            self.config = self._default_config()

    def _default_config(self) -> Dict[str, Any]:
        """Default deployment check configuration."""
        return {
            "environments": {
                "development": {"strict": False, "ssl_required": False},
                "staging": {"strict": True, "ssl_required": True},
                "production": {"strict": True, "ssl_required": True, "backup_required": True}
            },
            "required_files": [
                "README.md",
                ".env.example",
                "requirements.txt"
            ],
            "security_checks": True,
            "performance_checks": True,
            "documentation_checks": True,
            "git_checks": True
        }

    def run_checks(self) -> Dict[str, Any]:
        """Run all deployment checks."""
        print(f"🚀 Running deployment checklist for: {self.environment}")
        print("=" * 60)
        
        env_config = self.config["environments"].get(self.environment, {})
        
        # Core checks
        self._check_git_status()
        self._check_required_files()
        self._check_environment_files()
        self._check_dependencies()
        
        # Conditional checks based on environment
        if self.config.get("security_checks", True):
            self._check_security()
        
        if self.config.get("performance_checks", True):
            self._check_performance()
            
        if self.config.get("documentation_checks", True):
            self._check_documentation()
            
        if env_config.get("ssl_required", False):
            self._check_ssl_config()
            
        if env_config.get("backup_required", False):
            self._check_backup_strategy()
            
        self._print_summary()
        
        return {
            'environment': self.environment,
            'checks': self.checks,
            'summary': {
                'passed': self.passed,
                'failed': self.failed,
                'warnings': self.warnings,
                'total': len(self.checks)
            },
            'ready_to_deploy': self.failed == 0,
            'timestamp': datetime.now().isoformat()
        }

    def _check_git_status(self):
        """Check git repository status."""
        try:
            # Check if repo is clean
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                if result.stdout.strip():
                    self._add_check("Git Status", "failed", 
                                  "Repository has uncommitted changes", 
                                  "Commit or stash changes before deployment")
                else:
                    self._add_check("Git Status", "passed", "Repository is clean")
                    
                # Check for untracked files that should be committed
                untracked = [line for line in result.stdout.split('\n') 
                           if line.startswith('??') and not any(ignore in line 
                           for ignore in ['.pyc', '__pycache__', '.env', 'node_modules'])]
                if untracked:
                    self._add_check("Untracked Files", "warning", 
                                  f"Found {len(untracked)} untracked files",
                                  "Review and commit important files")
                                  
            else:
                self._add_check("Git Status", "failed", "Not a git repository")
                
        except FileNotFoundError:
            self._add_check("Git Status", "failed", "Git not installed")

    def _check_required_files(self):
        """Check for required project files."""
        required = self.config.get("required_files", [])
        
        for filename in required:
            filepath = self.project_root / filename
            if filepath.exists():
                # Check if file has content
                if filepath.stat().st_size > 0:
                    self._add_check(f"Required File: {filename}", "passed", "File exists and has content")
                else:
                    self._add_check(f"Required File: {filename}", "warning", "File exists but is empty")
            else:
                self._add_check(f"Required File: {filename}", "failed", "File missing")

    def _check_environment_files(self):
        """Check environment configuration."""
        env_file = self.project_root / ".env"
        env_example = self.project_root / ".env.example"
        
        if not env_example.exists():
            self._add_check("Environment Template", "warning", 
                          ".env.example not found", 
                          "Create template for environment variables")
        else:
            self._add_check("Environment Template", "passed", ".env.example exists")
            
        if self.environment == "production":
            if env_file.exists():
                self._add_check("Production .env", "warning", 
                              ".env file exists in production", 
                              "Use environment variables instead of .env file")
            else:
                self._add_check("Production .env", "passed", "No .env file (using env vars)")
        else:
            if env_file.exists():
                self._add_check("Development .env", "passed", ".env file exists")
            else:
                self._add_check("Development .env", "warning", ".env file missing")

    def _check_dependencies(self):
        """Check dependency configuration."""
        # Python dependencies
        req_file = self.project_root / "requirements.txt"
        if req_file.exists():
            try:
                content = req_file.read_text()
                deps = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
                
                if deps:
                    self._add_check("Python Dependencies", "passed", f"Found {len(deps)} dependencies")
                    
                    # Check for version pinning in production
                    if self.environment == "production":
                        unpinned = [dep for dep in deps if not any(char in dep for char in ['==', '>=', '<=', '~='])]
                        if unpinned:
                            self._add_check("Dependency Pinning", "warning", 
                                          f"{len(unpinned)} unpinned dependencies", 
                                          "Pin versions for production stability")
                        else:
                            self._add_check("Dependency Pinning", "passed", "All dependencies pinned")
                else:
                    self._add_check("Python Dependencies", "warning", "requirements.txt is empty")
                    
            except Exception as e:
                self._add_check("Python Dependencies", "failed", f"Error reading requirements.txt: {e}")
        else:
            self._add_check("Python Dependencies", "warning", "requirements.txt not found")
            
        # Node.js dependencies
        package_json = self.project_root / "package.json"
        if package_json.exists():
            try:
                with open(package_json) as f:
                    package_data = json.load(f)
                    
                deps = package_data.get('dependencies', {})
                dev_deps = package_data.get('devDependencies', {})
                
                if deps:
                    self._add_check("Node.js Dependencies", "passed", f"Found {len(deps)} dependencies")
                    
                if self.environment == "production" and dev_deps:
                    self._add_check("Dev Dependencies", "passed", 
                                  "Dev dependencies separated correctly")
                    
            except json.JSONDecodeError:
                self._add_check("Node.js Dependencies", "failed", "Invalid package.json")
        
    def _check_security(self):
        """Run security checks."""
        # Check for security scanner results
        security_baseline = self.project_root / ".security_baseline.json"
        if security_baseline.exists():
            self._add_check("Security Baseline", "passed", "Security baseline established")
        else:
            self._add_check("Security Baseline", "warning", 
                          "No security baseline found", 
                          "Run: mw skills run security-scan baseline")
            
        # Check for common security files
        security_files = [
            (".gitignore", "Sensitive files ignored"),
            (".env", "Should not exist in production" if self.environment == "production" else None)
        ]
        
        for filename, message in security_files:
            if message:
                filepath = self.project_root / filename
                if filepath.exists():
                    if filename == ".env" and self.environment == "production":
                        self._add_check("Security: .env", "warning", message)
                    else:
                        self._add_check(f"Security: {filename}", "passed", message)

    def _check_performance(self):
        """Check performance considerations."""
        # Check for production optimizations
        if self.environment == "production":
            # Look for build scripts
            package_json = self.project_root / "package.json"
            if package_json.exists():
                try:
                    with open(package_json) as f:
                        data = json.load(f)
                        scripts = data.get('scripts', {})
                        
                    if 'build' in scripts:
                        self._add_check("Build Script", "passed", "Build script configured")
                    else:
                        self._add_check("Build Script", "warning", "No build script found")
                        
                except Exception:
                    pass
                    
            # Check for static file optimization
            static_dirs = ['static', 'assets', 'public']
            optimized = False
            for static_dir in static_dirs:
                if (self.project_root / static_dir).exists():
                    optimized = True
                    break
                    
            if optimized:
                self._add_check("Static Files", "passed", "Static file directory found")

    def _check_documentation(self):
        """Check documentation completeness."""
        docs = [
            ("README.md", "Project documentation"),
            ("CHANGELOG.md", "Change history"),
            ("docs/", "Detailed documentation")
        ]
        
        for doc_path, description in docs:
            path = self.project_root / doc_path
            if path.exists():
                if path.is_file() and path.stat().st_size > 100:  # At least some content
                    self._add_check(f"Documentation: {doc_path}", "passed", description)
                elif path.is_dir() and any(path.iterdir()):  # Non-empty directory
                    self._add_check(f"Documentation: {doc_path}", "passed", description)
                else:
                    self._add_check(f"Documentation: {doc_path}", "warning", f"{description} exists but minimal")
            else:
                severity = "warning" if doc_path != "README.md" else "failed"
                self._add_check(f"Documentation: {doc_path}", severity, f"{description} missing")

    def _check_ssl_config(self):
        """Check SSL/TLS configuration."""
        # This is a placeholder - in real implementation, would check server config
        self._add_check("SSL/TLS Config", "warning", 
                      "Manual verification required", 
                      "Ensure SSL certificates are valid and configured")

    def _check_backup_strategy(self):
        """Check backup strategy."""
        # Look for backup configuration files
        backup_files = [
            "backup.sh",
            "backup.py", 
            ".github/workflows/backup.yml",
            "docker-compose.backup.yml"
        ]
        
        has_backup = False
        for backup_file in backup_files:
            if (self.project_root / backup_file).exists():
                has_backup = True
                break
                
        if has_backup:
            self._add_check("Backup Strategy", "passed", "Backup configuration found")
        else:
            self._add_check("Backup Strategy", "failed", 
                          "No backup strategy configured", 
                          "Configure automated backups for production")

    def _add_check(self, name: str, status: str, message: str, recommendation: str = ""):
        """Add a check result."""
        check = {
            'name': name,
            'status': status,
            'message': message,
            'recommendation': recommendation,
            'timestamp': datetime.now().isoformat()
        }
        
        self.checks.append(check)
        
        if status == "passed":
            self.passed += 1
            status_icon = "✅"
        elif status == "failed":
            self.failed += 1
            status_icon = "❌"
        else:  # warning
            self.warnings += 1
            status_icon = "⚠️"
            
        print(f"{status_icon} {name}: {message}")
        if recommendation:
            print(f"   💡 {recommendation}")

    def _print_summary(self):
        """Print deployment check summary."""
        print(f"\n🚀 Deployment Readiness Summary ({self.environment})")
        print("=" * 60)
        print(f"✅ Passed: {self.passed}")
        print(f"⚠️  Warnings: {self.warnings}")
        print(f"❌ Failed: {self.failed}")
        print(f"📊 Total: {len(self.checks)}")
        
        if self.failed == 0:
            if self.warnings == 0:
                print("\n🎉 All checks passed! Ready to deploy! 🚀")
            else:
                print(f"\n✅ Ready to deploy (with {self.warnings} warnings)")
        else:
            print(f"\n🛑 NOT ready to deploy - {self.failed} failed checks")


def main():
    """Main deployment check function."""
    environment = sys.argv[1] if len(sys.argv) > 1 else "production"
    
    if environment not in ["development", "staging", "production"]:
        print(f"⚠️ Unknown environment: {environment}")
        print("Valid environments: development, staging, production")
        environment = "production"  # Default to strictest
    
    checker = DeploymentChecker(environment)
    result = checker.run_checks()
    
    # Exit with error code if not ready to deploy
    return 0 if result['ready_to_deploy'] else 1

if __name__ == '__main__':
    sys.exit(main())