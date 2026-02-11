#!/usr/bin/env python3
"""
Dependency Checker
==================
Check all project dependencies for outdated/vulnerable packages.

Usage:
    python3 dep_checker.py [options]
    python3 dep_checker.py --project <project-name>
    python3 dep_checker.py --help

Options:
    --project <name>    Check specific project only
    --fix              Auto-update outdated packages (use with caution)
    --security-only    Only check for security vulnerabilities
    --format json      Output in JSON format
    --help             Show this help

Examples:
    python3 dep_checker.py                    # Check all projects
    python3 dep_checker.py --project my-api   # Check specific project
    python3 dep_checker.py --security-only    # Security vulnerabilities only
    python3 dep_checker.py --fix              # Auto-update outdated packages
"""

import os
import sys
import json
import subprocess
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import re

try:
    from config import MYWORK_ROOT, PROJECTS_DIR
except ImportError:
    def _get_mywork_root() -> Path:
        if env_root := os.environ.get("MYWORK_ROOT"):
            return Path(env_root)
        script_dir = Path(__file__).resolve().parent
        if script_dir.name == "tools":
            potential_root = script_dir.parent
            if (potential_root / "CLAUDE.md").exists():
                return potential_root
        return Path.home() / "MyWork"
    
    MYWORK_ROOT = _get_mywork_root()
    PROJECTS_DIR = MYWORK_ROOT / "projects"

class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"

def color(text: str, color_code: str) -> str:
    """Apply color to text."""
    return f"{color_code}{text}{Colors.ENDC}"

class DependencyChecker:
    """Check project dependencies for updates and vulnerabilities."""
    
    def __init__(self):
        self.cache_dir = MYWORK_ROOT / ".tmp" / "dep_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_duration = timedelta(hours=6)  # Cache for 6 hours
    
    def get_cache_file(self, key: str) -> Path:
        """Get cache file path for a key."""
        return self.cache_dir / f"{key}.json"
    
    def is_cache_valid(self, cache_file: Path) -> bool:
        """Check if cache file is still valid."""
        if not cache_file.exists():
            return False
        
        try:
            stat = cache_file.stat()
            cache_time = datetime.fromtimestamp(stat.st_mtime)
            return datetime.now() - cache_time < self.cache_duration
        except:
            return False
    
    def get_cached_data(self, key: str) -> Optional[Dict]:
        """Get cached data if valid."""
        cache_file = self.get_cache_file(key)
        if self.is_cache_valid(cache_file):
            try:
                return json.loads(cache_file.read_text())
            except:
                pass
        return None
    
    def set_cached_data(self, key: str, data: Dict) -> None:
        """Store data in cache."""
        cache_file = self.get_cache_file(key)
        try:
            cache_file.write_text(json.dumps(data, indent=2))
        except:
            pass
    
    def check_python_packages(self, requirements_file: Path) -> Dict[str, Any]:
        """Check Python packages for updates and vulnerabilities."""
        if not requirements_file.exists():
            return {"error": "Requirements file not found"}
        
        print(f"   🐍 Checking Python packages in {requirements_file.name}...")
        
        try:
            content = requirements_file.read_text()
            packages = []
            
            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Parse package name and version
                if '==' in line:
                    pkg_name, current_version = line.split('==', 1)
                elif '>=' in line:
                    pkg_name = line.split('>=', 1)[0]
                    current_version = "unknown"
                elif '~=' in line:
                    pkg_name = line.split('~=', 1)[0]
                    current_version = "unknown"
                else:
                    pkg_name = line
                    current_version = "unknown"
                
                pkg_name = pkg_name.strip()
                if pkg_name:
                    packages.append({
                        "name": pkg_name,
                        "current_version": current_version.strip(),
                        "line": line
                    })
            
            results = {
                "type": "python",
                "total_packages": len(packages),
                "outdated": [],
                "vulnerable": [],
                "errors": []
            }
            
            # Check each package
            for pkg in packages:
                try:
                    # Check for updates using PyPI API
                    latest_info = self.get_pypi_package_info(pkg["name"])
                    if latest_info:
                        pkg["latest_version"] = latest_info.get("version", "unknown")
                        pkg["homepage"] = latest_info.get("homepage", "")
                        pkg["summary"] = latest_info.get("summary", "")
                        
                        if pkg["current_version"] != "unknown" and pkg["current_version"] != pkg["latest_version"]:
                            results["outdated"].append(pkg)
                    
                    # Check for vulnerabilities (simplified check)
                    vuln_info = self.check_python_vulnerabilities(pkg["name"], pkg["current_version"])
                    if vuln_info:
                        pkg["vulnerabilities"] = vuln_info
                        results["vulnerable"].append(pkg)
                
                except Exception as e:
                    results["errors"].append(f"Error checking {pkg['name']}: {str(e)}")
            
            return results
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_pypi_package_info(self, package_name: str) -> Optional[Dict]:
        """Get package info from PyPI API."""
        cache_key = f"pypi_{package_name}"
        cached_data = self.get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        try:
            url = f"https://pypi.org/pypi/{package_name}/json"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                info = {
                    "version": data["info"]["version"],
                    "homepage": data["info"]["home_page"] or "",
                    "summary": data["info"]["summary"] or "",
                    "author": data["info"]["author"] or "",
                }
                self.set_cached_data(cache_key, info)
                return info
        except:
            pass
        
        return None
    
    def check_python_vulnerabilities(self, package_name: str, version: str) -> List[Dict]:
        """Check for known vulnerabilities (simplified)."""
        # In a real implementation, this would check against a vulnerability database
        # For now, just return empty list as a placeholder
        return []
    
    def check_nodejs_packages(self, package_json_path: Path) -> Dict[str, Any]:
        """Check Node.js packages for updates and vulnerabilities."""
        if not package_json_path.exists():
            return {"error": "package.json not found"}
        
        print(f"   📦 Checking Node.js packages in {package_json_path.name}...")
        
        try:
            package_data = json.loads(package_json_path.read_text())
            dependencies = package_data.get("dependencies", {})
            dev_dependencies = package_data.get("devDependencies", {})
            
            all_deps = {**dependencies, **dev_dependencies}
            
            results = {
                "type": "nodejs",
                "total_packages": len(all_deps),
                "outdated": [],
                "vulnerable": [],
                "errors": []
            }
            
            project_dir = package_json_path.parent
            
            # Check for outdated packages using npm outdated
            try:
                result = subprocess.run(
                    ["npm", "outdated", "--json"],
                    cwd=project_dir,
                    capture_output=True,
                    text=True
                )
                
                if result.stdout:
                    outdated_data = json.loads(result.stdout)
                    for pkg_name, info in outdated_data.items():
                        results["outdated"].append({
                            "name": pkg_name,
                            "current_version": info.get("current", "unknown"),
                            "wanted_version": info.get("wanted", "unknown"),
                            "latest_version": info.get("latest", "unknown"),
                            "location": info.get("location", "")
                        })
            
            except subprocess.CalledProcessError:
                pass
            except json.JSONDecodeError:
                pass
            except Exception as e:
                results["errors"].append(f"Error checking outdated packages: {str(e)}")
            
            # Check for vulnerabilities using npm audit
            try:
                result = subprocess.run(
                    ["npm", "audit", "--json"],
                    cwd=project_dir,
                    capture_output=True,
                    text=True
                )
                
                if result.stdout:
                    audit_data = json.loads(result.stdout)
                    vulnerabilities = audit_data.get("vulnerabilities", {})
                    
                    for pkg_name, vuln_info in vulnerabilities.items():
                        if vuln_info.get("severity") in ["moderate", "high", "critical"]:
                            results["vulnerable"].append({
                                "name": pkg_name,
                                "severity": vuln_info.get("severity", "unknown"),
                                "title": vuln_info.get("title", ""),
                                "url": vuln_info.get("url", ""),
                                "range": vuln_info.get("range", "")
                            })
            
            except subprocess.CalledProcessError:
                pass
            except json.JSONDecodeError:
                pass
            except Exception as e:
                results["errors"].append(f"Error checking vulnerabilities: {str(e)}")
            
            return results
            
        except Exception as e:
            return {"error": str(e)}
    
    def check_project_dependencies(self, project_path: Path) -> Dict[str, Any]:
        """Check all dependencies for a single project."""
        project_name = project_path.name
        print(f"🔍 Checking dependencies for project: {color(project_name, Colors.BOLD)}")
        
        results = {
            "project_name": project_name,
            "project_path": str(project_path),
            "timestamp": datetime.now().isoformat(),
            "dependency_files": [],
            "summary": {
                "total_packages": 0,
                "outdated_packages": 0,
                "vulnerable_packages": 0,
                "errors": 0
            }
        }
        
        # Check Python dependencies
        python_files = ["requirements.txt", "pyproject.toml", "Pipfile"]
        for py_file in python_files:
            file_path = project_path / py_file
            if file_path.exists():
                if py_file == "requirements.txt":
                    dep_result = self.check_python_packages(file_path)
                    if "error" not in dep_result:
                        results["dependency_files"].append(dep_result)
                        results["summary"]["total_packages"] += dep_result["total_packages"]
                        results["summary"]["outdated_packages"] += len(dep_result["outdated"])
                        results["summary"]["vulnerable_packages"] += len(dep_result["vulnerable"])
                        results["summary"]["errors"] += len(dep_result["errors"])
        
        # Check Node.js dependencies
        package_json = project_path / "package.json"
        if package_json.exists():
            dep_result = self.check_nodejs_packages(package_json)
            if "error" not in dep_result:
                results["dependency_files"].append(dep_result)
                results["summary"]["total_packages"] += dep_result["total_packages"]
                results["summary"]["outdated_packages"] += len(dep_result["outdated"])
                results["summary"]["vulnerable_packages"] += len(dep_result["vulnerable"])
                results["summary"]["errors"] += len(dep_result["errors"])
        
        return results
    
    def print_project_results(self, results: Dict[str, Any], security_only: bool = False) -> None:
        """Print results for a single project."""
        project_name = results["project_name"]
        summary = results["summary"]
        
        print(f"\n📊 Results for {color(project_name, Colors.BOLD)}:")
        print(f"   📦 Total packages: {summary['total_packages']}")
        
        if not security_only:
            if summary['outdated_packages'] > 0:
                print(f"   ⚠️  Outdated packages: {color(str(summary['outdated_packages']), Colors.YELLOW)}")
            else:
                print(f"   ✅ Outdated packages: 0")
        
        if summary['vulnerable_packages'] > 0:
            print(f"   🚨 Vulnerable packages: {color(str(summary['vulnerable_packages']), Colors.RED)}")
        else:
            print(f"   ✅ Vulnerable packages: 0")
        
        if summary['errors'] > 0:
            print(f"   ❌ Errors: {summary['errors']}")
        
        # Show detailed results
        for dep_file in results["dependency_files"]:
            dep_type = dep_file["type"]
            
            if not security_only and dep_file["outdated"]:
                print(f"\n   📋 Outdated {dep_type} packages:")
                for pkg in dep_file["outdated"][:5]:  # Show max 5
                    current = pkg.get("current_version", "unknown")
                    latest = pkg.get("latest_version", "unknown")
                    print(f"     • {pkg['name']}: {current} → {latest}")
                if len(dep_file["outdated"]) > 5:
                    print(f"     ... and {len(dep_file['outdated']) - 5} more")
            
            if dep_file["vulnerable"]:
                print(f"\n   🚨 Vulnerable {dep_type} packages:")
                for pkg in dep_file["vulnerable"]:
                    severity = pkg.get("severity", "unknown")
                    severity_color = Colors.RED if severity == "critical" else Colors.YELLOW
                    print(f"     • {pkg['name']}: {color(severity.upper(), severity_color)}")
                    if pkg.get("title"):
                        print(f"       {pkg['title']}")
            
            if dep_file["errors"]:
                print(f"\n   ❌ Errors checking {dep_type} packages:")
                for error in dep_file["errors"]:
                    print(f"     • {error}")
    
    def fix_outdated_packages(self, project_path: Path, results: Dict[str, Any]) -> bool:
        """Attempt to fix outdated packages."""
        print(f"\n🔧 Attempting to fix outdated packages in {results['project_name']}...")
        
        fixed_any = False
        
        for dep_file in results["dependency_files"]:
            if not dep_file["outdated"]:
                continue
            
            dep_type = dep_file["type"]
            
            if dep_type == "nodejs":
                try:
                    print("   📦 Updating Node.js packages...")
                    result = subprocess.run(
                        ["npm", "update"],
                        cwd=project_path,
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        print("   ✅ Node.js packages updated")
                        fixed_any = True
                    else:
                        print(f"   ❌ Failed to update Node.js packages: {result.stderr}")
                
                except Exception as e:
                    print(f"   ❌ Error updating Node.js packages: {e}")
            
            elif dep_type == "python":
                print("   🐍 Python package auto-update not implemented (use pip-tools or poetry)")
        
        return fixed_any
    
    def check_all_projects(self, security_only: bool = False, fix_mode: bool = False) -> List[Dict[str, Any]]:
        """Check dependencies for all projects."""
        if not PROJECTS_DIR.exists():
            print(f"{Colors.RED}❌ Projects directory not found: {PROJECTS_DIR}{Colors.ENDC}")
            return []
        
        projects = [p for p in PROJECTS_DIR.iterdir() if p.is_dir() and not p.name.startswith('.')]
        
        if not projects:
            print(f"{Colors.YELLOW}⚠️ No projects found in {PROJECTS_DIR}{Colors.ENDC}")
            return []
        
        print(f"{Colors.BOLD}🔍 Checking dependencies for {len(projects)} projects...{Colors.ENDC}")
        
        all_results = []
        
        for project_path in sorted(projects):
            # Skip projects without dependency files
            has_deps = any([
                (project_path / f).exists() 
                for f in ["requirements.txt", "package.json", "pyproject.toml", "Pipfile"]
            ])
            
            if not has_deps:
                continue
            
            try:
                results = self.check_project_dependencies(project_path)
                all_results.append(results)
                
                # Print results
                self.print_project_results(results, security_only)
                
                # Fix if requested
                if fix_mode and (results["summary"]["outdated_packages"] > 0):
                    self.fix_outdated_packages(project_path, results)
            
            except Exception as e:
                print(f"❌ Error checking {project_path.name}: {e}")
        
        return all_results
    
    def print_summary(self, all_results: List[Dict[str, Any]], security_only: bool = False) -> None:
        """Print overall summary."""
        if not all_results:
            return
        
        total_projects = len(all_results)
        total_packages = sum(r["summary"]["total_packages"] for r in all_results)
        total_outdated = sum(r["summary"]["outdated_packages"] for r in all_results)
        total_vulnerable = sum(r["summary"]["vulnerable_packages"] for r in all_results)
        total_errors = sum(r["summary"]["errors"] for r in all_results)
        
        print(f"\n{Colors.BOLD}{Colors.BLUE}📊 Overall Summary{Colors.ENDC}")
        print(f"{Colors.BLUE}{'=' * 50}{Colors.ENDC}")
        print(f"   📂 Projects checked: {total_projects}")
        print(f"   📦 Total packages: {total_packages}")
        
        if not security_only:
            if total_outdated > 0:
                print(f"   ⚠️  Total outdated: {color(str(total_outdated), Colors.YELLOW)}")
            else:
                print(f"   ✅ Total outdated: 0")
        
        if total_vulnerable > 0:
            print(f"   🚨 Total vulnerable: {color(str(total_vulnerable), Colors.RED)}")
        else:
            print(f"   ✅ Total vulnerable: 0")
        
        if total_errors > 0:
            print(f"   ❌ Total errors: {total_errors}")
        
        # Recommendations
        print(f"\n{Colors.BOLD}💡 Recommendations:{Colors.ENDC}")
        if total_vulnerable > 0:
            print(f"   🚨 {Colors.RED}URGENT: Address security vulnerabilities immediately{Colors.ENDC}")
        
        if not security_only and total_outdated > 0:
            print(f"   ⚠️  Consider updating outdated packages")
            print(f"   🔧 Use 'mw dep-check --fix' to auto-update (use with caution)")
        
        if total_errors > 0:
            print(f"   🔍 Investigate errors in dependency checking")
        
        if total_vulnerable == 0 and total_outdated == 0 and total_errors == 0:
            print(f"   🎉 {Colors.GREEN}All dependencies look good!{Colors.ENDC}")

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Check project dependencies for updates and vulnerabilities")
    parser.add_argument("--project", help="Check specific project only")
    parser.add_argument("--fix", action="store_true", help="Auto-update outdated packages (use with caution)")
    parser.add_argument("--security-only", action="store_true", help="Only check for security vulnerabilities")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    
    args = parser.parse_args()
    
    checker = DependencyChecker()
    
    if args.project:
        # Check specific project
        project_path = PROJECTS_DIR / args.project
        if not project_path.exists():
            print(f"{Colors.RED}❌ Project not found: {args.project}{Colors.ENDC}")
            return 1
        
        results = checker.check_project_dependencies(project_path)
        
        if args.format == "json":
            print(json.dumps(results, indent=2))
        else:
            checker.print_project_results(results, args.security_only)
            
            if args.fix and results["summary"]["outdated_packages"] > 0:
                checker.fix_outdated_packages(project_path, results)
    
    else:
        # Check all projects
        all_results = checker.check_all_projects(args.security_only, args.fix)
        
        if args.format == "json":
            print(json.dumps(all_results, indent=2))
        else:
            checker.print_summary(all_results, args.security_only)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())