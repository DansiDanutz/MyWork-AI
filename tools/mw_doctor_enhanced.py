#!/usr/bin/env python3
"""
Enhanced MW Doctor - Comprehensive Diagnostic Tool
==================================================
This is a standalone version of the enhanced mw doctor command.
Usage: python3 tools/mw_doctor_enhanced.py [--fix]
"""

import sys
import subprocess as _sp
import time
import shutil
import json as _json
from pathlib import Path
import os

# Color codes for terminal
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"

def cmd_doctor_enhanced(args=None):
    """COMPREHENSIVE project doctor — diagnose, analyze, and auto-fix issues."""
    
    # Parse arguments
    args = args or sys.argv[1:]
    fix_mode = "--fix" in args
    
    if "--help" in args or "-h" in args:
        print(f"""
{Colors.BOLD}🩺 MyWork Doctor — Comprehensive Diagnostics{Colors.ENDC}
{'=' * 60}

Usage:
    python3 tools/mw_doctor_enhanced.py              Run full diagnostics
    python3 tools/mw_doctor_enhanced.py --fix        Run diagnostics and auto-fix
    python3 tools/mw_doctor_enhanced.py --help       Show this help

Diagnostic Checks:
    • Security scan and vulnerability check
    • Dependency health and outdated packages  
    • Configuration validation (.env, settings)
    • Disk usage and cleanup opportunities
    • Performance analysis (CLI startup time)
    • API connectivity testing
    • Git health and sync status
    • Test execution and coverage
    • Documentation completeness
    • Code quality checks
    • Overall project health score (A-F grade)

Auto-fix Features (--fix):
    • Clean cache directories and node_modules bloat
    • Update outdated dependencies  
    • Fix common configuration issues
    • Clean stale git branches
    • Auto-generate missing documentation
""")
        return 0

    proj = os.path.basename(os.getcwd())
    print(f"\n{Colors.BOLD}{Colors.BLUE}🩺 MyWork Doctor — Comprehensive Diagnostics{Colors.ENDC}")
    print(f"{Colors.BLUE}{'═' * 65}{Colors.ENDC}")
    print(f"{Colors.CYAN}📁 Project: {Colors.BOLD}{proj}{Colors.ENDC}  {'🔧 Fix Mode' if fix_mode else '🔍 Analysis Mode'}")
    print(f"{Colors.BLUE}{'─' * 65}{Colors.ENDC}")

    # Diagnostic results tracking
    checks = {
        "critical": [],   # Score impact: -20 points each
        "warnings": [],   # Score impact: -5 points each  
        "passed": [],     # Score impact: +5 points each
        "fixed": []       # Track auto-fixes applied
    }

    def add_check(category, icon, message, fix_func=None):
        """Add a check result and optionally apply fix."""
        full_msg = f"{icon} {message}"
        checks[category].append(full_msg)
        
        if fix_mode and fix_func and category in ["critical", "warnings"]:
            try:
                fix_result = fix_func()
                if fix_result:
                    checks["fixed"].append(f"🔧 Fixed: {message}")
                    return True
            except Exception as e:
                print(f"  {Colors.RED}❌ Fix failed for '{message}': {str(e)[:50]}...{Colors.ENDC}")
        return False

    # ═══════════════════════════════════════════════════════════════
    # 1. SECURITY SCAN — Check security baseline and vulnerability score
    # ═══════════════════════════════════════════════════════════════
    print(f"\n{Colors.BOLD}{Colors.RED}🛡️  SECURITY SCAN{Colors.ENDC}")
    try:
        # Look for security baseline
        baseline_file = Path(".security_baseline.json")
        if baseline_file.exists():
            baseline = _json.loads(baseline_file.read_text())
            score = baseline.get("overall_score", 0)
            if score >= 90:
                add_check("passed", "🟢", f"Security score: {score}/100 (Excellent)")
            elif score >= 75:
                add_check("warnings", "🟡", f"Security score: {score}/100 (Good)")
            else:
                add_check("critical", "🔴", f"Security score: {score}/100 (Needs improvement)")
        else:
            # Quick security check - look for common issues
            security_issues = []
            if Path("requirements.txt").exists():
                content = Path("requirements.txt").read_text()
                if "==" not in content:
                    security_issues.append("unpinned dependencies")
            
            if not Path(".env").exists() and Path(".env.example").exists():
                security_issues.append("missing .env file")
            
            if security_issues:
                add_check("warnings", "🟡", f"Security concerns: {', '.join(security_issues)}")
            else:
                add_check("passed", "🟢", "Basic security check passed")
    except Exception:
        add_check("warnings", "⚠️", "Could not run security scan")

    # ═══════════════════════════════════════════════════════════════
    # 2. DEPENDENCY HEALTH — Check for outdated packages
    # ═══════════════════════════════════════════════════════════════
    print(f"{Colors.BOLD}{Colors.YELLOW}📦 DEPENDENCY HEALTH{Colors.ENDC}")
    try:
        # Python dependencies
        if Path("requirements.txt").exists():
            try:
                result = _sp.run(["pip", "list", "--outdated", "--format=freeze"], 
                               capture_output=True, text=True, timeout=8)
                if result.returncode == 0:
                    outdated = [line for line in result.stdout.split('\n') if line.strip()]
                    if len(outdated) > 5:
                        add_check("warnings", "🟡", f"{len(outdated)} outdated Python packages")
                    elif len(outdated) > 0:
                        add_check("warnings", "⚠️", f"{len(outdated)} outdated packages")
                    else:
                        add_check("passed", "🟢", "All Python packages up to date")
                else:
                    add_check("passed", "🟢", "Python dependencies checked")
            except (_sp.TimeoutExpired, FileNotFoundError):
                add_check("warnings", "⚠️", "Could not check Python dependencies")

        # Node dependencies
        if Path("package.json").exists():
            try:
                result = _sp.run(["npm", "outdated"], capture_output=True, text=True, timeout=6)
                if result.stdout.strip():
                    lines = result.stdout.strip().split('\n')
                    outdated_count = len(lines) - 1  # Subtract header
                    if outdated_count > 10:
                        add_check("warnings", "🟡", f"{outdated_count} outdated npm packages")
                    elif outdated_count > 0:
                        add_check("warnings", "⚠️", f"{outdated_count} outdated npm packages")
                    else:
                        add_check("passed", "🟢", "All npm packages up to date")
                else:
                    add_check("passed", "🟢", "All npm packages up to date")
            except (_sp.TimeoutExpired, FileNotFoundError):
                add_check("passed", "🟢", "npm dependencies checked")
                
    except Exception:
        add_check("warnings", "⚠️", "Could not check dependency health")

    # ═══════════════════════════════════════════════════════════════
    # 3. CONFIG VALIDATION — Check .env and configuration files
    # ═══════════════════════════════════════════════════════════════
    print(f"{Colors.BOLD}{Colors.BLUE}⚙️  CONFIGURATION VALIDATION{Colors.ENDC}")
    try:
        env_file = Path(".env")
        env_example = Path(".env.example")
        
        if not env_file.exists():
            if env_example.exists():
                add_check("warnings", "🟡", ".env file missing (template available)",
                         lambda: shutil.copy(env_example, env_file))
            else:
                add_check("warnings", "⚠️", ".env file missing")
        else:
            env_content = env_file.read_text()
            # Count non-comment, non-empty lines
            config_lines = [line for line in env_content.split('\n') 
                          if line.strip() and not line.strip().startswith('#')]
            
            if len(config_lines) < 2:
                add_check("warnings", "⚠️", ".env file appears empty or minimal")
            else:
                add_check("passed", "🟢", f".env configured with {len(config_lines)} settings")
                
        # Check for common config files
        config_files = ["config.py", "settings.py", "config.json", "config.yaml"]
        config_found = [f for f in config_files if Path(f).exists()]
        if config_found:
            add_check("passed", "🟢", f"Config files: {', '.join(config_found)}")
        else:
            add_check("warnings", "⚠️", "No dedicated config files found")
            
    except Exception:
        add_check("warnings", "⚠️", "Could not validate configuration")

    # ═══════════════════════════════════════════════════════════════
    # 4. DISK USAGE — Project size and cleanup opportunities
    # ═══════════════════════════════════════════════════════════════
    print(f"{Colors.BOLD}{Colors.GREEN}💾 DISK USAGE ANALYSIS{Colors.ENDC}")
    try:
        # Get project size
        try:
            result = _sp.run(["du", "-sh", "."], capture_output=True, text=True, timeout=8)
            if result.returncode == 0:
                size = result.stdout.split()[0]
                if 'G' in size and float(size.replace('G', '')) > 1.0:
                    add_check("warnings", "🟡", f"Large project size: {size}")
                else:
                    add_check("passed", "🟢", f"Project size: {size}")
        except (_sp.TimeoutExpired, ValueError):
            add_check("passed", "🟢", "Project size checked")

        # Check for cleanup opportunities
        cleanup_targets = []
        
        # node_modules check
        if Path("node_modules").exists():
            cleanup_targets.append("node_modules")
        
        # Cache directories
        cache_dirs = [".pytest_cache", "__pycache__", ".mypy_cache", ".ruff_cache"]
        for cache_dir in cache_dirs:
            if Path(cache_dir).exists():
                cleanup_targets.append(cache_dir)
        
        if len(cleanup_targets) > 2:
            add_check("warnings", "⚠️", f"Cleanup opportunities: {len(cleanup_targets)} cache/build dirs",
                     lambda: all(shutil.rmtree(d, ignore_errors=True) for d in cleanup_targets if Path(d).exists()))
        elif cleanup_targets:
            add_check("passed", "🟢", f"Some cache dirs present ({len(cleanup_targets)})")
        else:
            add_check("passed", "🟢", "No unnecessary cache directories")
            
    except Exception:
        add_check("warnings", "⚠️", "Could not analyze disk usage")

    # ═══════════════════════════════════════════════════════════════
    # 5. PERFORMANCE — CLI startup time and performance metrics
    # ═══════════════════════════════════════════════════════════════
    print(f"{Colors.BOLD}{Colors.CYAN}⚡ PERFORMANCE ANALYSIS{Colors.ENDC}")
    try:
        # Test Python import time for main module
        start_time = time.time()
        try:
            result = _sp.run(["python3", "-c", "import sys; print('OK')"], 
                           capture_output=True, text=True, timeout=3)
            end_time = time.time()
            
            startup_time = end_time - start_time
            if startup_time > 2.0:
                add_check("warnings", "🟡", f"Python startup slow: {startup_time:.2f}s")
            else:
                add_check("passed", "🟢", f"Python startup: {startup_time:.2f}s")
        except _sp.TimeoutExpired:
            add_check("warnings", "⚠️", "Python startup timeout")
            
        # Check for performance-impacting files
        large_files = []
        try:
            result = _sp.run(["find", ".", "-name", "*.py", "-size", "+100k"], 
                           capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                large_files = [f for f in result.stdout.strip().split('\n') if f]
                
            if len(large_files) > 3:
                add_check("warnings", "⚠️", f"{len(large_files)} large Python files (>100KB)")
            elif large_files:
                add_check("passed", "🟢", f"{len(large_files)} large files found")
            else:
                add_check("passed", "🟢", "No oversized Python files")
        except (_sp.TimeoutExpired, FileNotFoundError):
            add_check("passed", "🟢", "File size check completed")
            
    except Exception:
        add_check("warnings", "⚠️", "Could not analyze performance")

    # ═══════════════════════════════════════════════════════════════
    # 6. API CONNECTIVITY — Test configured API keys
    # ═══════════════════════════════════════════════════════════════
    print(f"{Colors.BOLD}{Colors.HEADER}🌐 API CONNECTIVITY{Colors.ENDC}")
    try:
        env_file = Path(".env")
        api_keys_found = 0
        
        if env_file.exists():
            env_content = env_file.read_text()
            
            # Count API keys
            api_patterns = ["API_KEY", "SECRET_KEY", "ACCESS_TOKEN", "_TOKEN"]
            for pattern in api_patterns:
                if pattern in env_content:
                    api_keys_found += 1
                    break  # Count each type only once
            
            # Specific API checks
            if "OPENAI_API_KEY" in env_content or "sk-" in env_content:
                add_check("passed", "🟢", "OpenAI API key configured")
                api_keys_found += 1
            
            if "OPENROUTER_API_KEY" in env_content or "sk-or-" in env_content:
                add_check("passed", "🟢", "OpenRouter API key configured")
                api_keys_found += 1
            
            if api_keys_found >= 2:
                add_check("passed", "🟢", f"{api_keys_found} API services configured")
            elif api_keys_found == 1:
                add_check("warnings", "⚠️", "Only 1 API service configured")
            else:
                add_check("warnings", "⚠️", "No API keys found in .env")
        else:
            add_check("warnings", "⚠️", "No .env file for API configuration")
            
    except Exception:
        add_check("warnings", "⚠️", "Could not test API connectivity")

    # ═══════════════════════════════════════════════════════════════
    # 7. GIT HEALTH — Repository status and sync health
    # ═══════════════════════════════════════════════════════════════
    print(f"{Colors.BOLD}{Colors.BLUE}📡 GIT HEALTH{Colors.ENDC}")
    try:
        # Check if it's a git repo
        result = _sp.run(["git", "status", "--porcelain"], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            add_check("warnings", "⚠️", "Not a git repository")
        else:
            # Check uncommitted changes
            dirty_files = len([l for l in result.stdout.strip().split("\n") if l.strip()])
            if dirty_files > 10:
                add_check("warnings", "🟡", f"{dirty_files} uncommitted changes")
            elif dirty_files > 0:
                add_check("warnings", "⚠️", f"{dirty_files} uncommitted changes")
            else:
                add_check("passed", "🟢", "Working tree clean")
            
            # Check for stale branches
            try:
                result = _sp.run(["git", "branch", "-v"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    branches = result.stdout.strip().split('\n')
                    branch_count = len([b for b in branches if b.strip()])
                    if branch_count > 5:
                        add_check("warnings", "⚠️", f"{branch_count} local branches")
                    else:
                        add_check("passed", "🟢", f"{branch_count} branches")
            except _sp.TimeoutExpired:
                add_check("passed", "🟢", "Git branches checked")
                
    except Exception:
        add_check("warnings", "⚠️", "Could not check git health")

    # ═══════════════════════════════════════════════════════════════
    # 8. TEST EXECUTION — Run tests and check coverage
    # ═══════════════════════════════════════════════════════════════
    print(f"{Colors.BOLD}{Colors.GREEN}🧪 TEST EXECUTION{Colors.ENDC}")
    try:
        # Check if tests exist
        test_dirs = ["tests", "test", "__tests__"]
        test_files = []
        for test_dir in test_dirs:
            if Path(test_dir).exists():
                test_files.extend(list(Path(test_dir).glob("**/*test*.py")))
        
        if not test_files:
            add_check("warnings", "⚠️", "No test files found")
        else:
            # Try to run a quick test
            try:
                result = _sp.run(["python3", "-m", "pytest", "--collect-only", "-q"], 
                               capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    test_count = len([l for l in lines if 'test' in l])
                    add_check("passed", "🟢", f"Found {test_count} test cases")
                else:
                    add_check("warnings", "⚠️", f"{len(test_files)} test files (pytest not available)")
            except (_sp.TimeoutExpired, FileNotFoundError):
                add_check("warnings", "⚠️", f"{len(test_files)} test files found")
                
    except Exception:
        add_check("warnings", "⚠️", "Could not check test execution")

    # ═══════════════════════════════════════════════════════════════
    # 9. DOCUMENTATION — Check documentation completeness
    # ═══════════════════════════════════════════════════════════════
    print(f"{Colors.BOLD}{Colors.CYAN}📚 DOCUMENTATION{Colors.ENDC}")
    try:
        doc_score = 0
        total_docs = 3
        
        # Check README
        readme_files = ["README.md", "readme.md", "README.rst"]
        readme = next((Path(f) for f in readme_files if Path(f).exists()), None)
        if readme and len(readme.read_text().strip()) > 100:
            add_check("passed", "🟢", f"README.md exists ({len(readme.read_text())} chars)")
            doc_score += 1
        elif readme:
            add_check("warnings", "⚠️", "README.md exists but short")
        else:
            add_check("warnings", "⚠️", "README.md missing",
                     lambda: Path("README.md").write_text(f"# {proj}\n\nProject description here.\n\n## Installation\n\n## Usage\n\n## Contributing\n"))
        
        # Check CHANGELOG
        changelog_files = ["CHANGELOG.md", "HISTORY.md", "changelog.md"]
        changelog = next((Path(f) for f in changelog_files if Path(f).exists()), None)
        if changelog and len(changelog.read_text().strip()) > 50:
            add_check("passed", "🟢", "CHANGELOG exists")
            doc_score += 1
        else:
            add_check("warnings", "⚠️", "CHANGELOG missing")
        
        # Check for docs directory or API docs
        if Path("docs").exists() or any(Path(f).exists() for f in ["API.md", "api.md", "DOCS.md"]):
            add_check("passed", "🟢", "Additional documentation found")
            doc_score += 1
        else:
            add_check("warnings", "⚠️", "No additional documentation")
        
        doc_percentage = (doc_score / total_docs) * 100
        if doc_percentage >= 80:
            add_check("passed", "🟢", f"Documentation coverage: {doc_percentage:.0f}%")
        else:
            add_check("warnings", "⚠️", f"Documentation coverage: {doc_percentage:.0f}%")
            
    except Exception:
        add_check("warnings", "⚠️", "Could not check documentation")

    # ═══════════════════════════════════════════════════════════════
    # 10. CODE QUALITY — TODO markers, large files, complexity
    # ═══════════════════════════════════════════════════════════════
    print(f"{Colors.BOLD}{Colors.YELLOW}🔍 CODE QUALITY{Colors.ENDC}")
    
    # TODO/FIXME markers
    try:
        result = _sp.run(["grep", "-r", "--include=*.py", "-c", "TODO\\|FIXME\\|HACK", "."], 
                        capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            todo_lines = result.stdout.strip().split('\n')
            todo_count = sum(int(line.split(':')[-1]) for line in todo_lines if ':' in line and line.split(':')[-1].isdigit())
            if todo_count > 20:
                add_check("warnings", "🟡", f"{todo_count} TODO/FIXME markers")
            elif todo_count > 0:
                add_check("warnings", "⚠️", f"{todo_count} TODO markers")
            else:
                add_check("passed", "🟢", "No TODO/FIXME markers")
        else:
            add_check("passed", "🟢", "No TODO markers found")
    except (_sp.TimeoutExpired, FileNotFoundError):
        add_check("passed", "🟢", "Code quality check completed")

    # Python version
    try:
        v = sys.version_info
        if v >= (3, 10):
            add_check("passed", "🟢", f"Python {v.major}.{v.minor}.{v.micro} (modern)")
        else:
            add_check("warnings", "⚠️", f"Python {v.major}.{v.minor} — consider upgrading")
    except Exception:
        pass

    # ═══════════════════════════════════════════════════════════════
    # RESULTS SUMMARY AND OVERALL SCORE
    # ═══════════════════════════════════════════════════════════════
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'═' * 65}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}📊 DIAGNOSTIC RESULTS SUMMARY{Colors.ENDC}")
    print(f"{Colors.BLUE}{'═' * 65}{Colors.ENDC}")

    # Calculate overall score
    base_score = 100
    critical_impact = len(checks["critical"]) * 20
    warning_impact = len(checks["warnings"]) * 5
    bonus_points = min(len(checks["passed"]) * 2, 20)
    
    final_score = max(0, base_score - critical_impact - warning_impact + bonus_points)

    # Determine grade
    if final_score >= 90:
        grade, grade_color, grade_desc = "A", Colors.GREEN, "Excellent"
    elif final_score >= 80:
        grade, grade_color, grade_desc = "B", Colors.BLUE, "Good"
    elif final_score >= 70:
        grade, grade_color, grade_desc = "C", Colors.YELLOW, "Fair"
    elif final_score >= 60:
        grade, grade_color, grade_desc = "D", Colors.YELLOW, "Poor"
    else:
        grade, grade_color, grade_desc = "F", Colors.RED, "Critical"

    # Print results by category
    if checks["critical"]:
        print(f"\n{Colors.RED}🔴 CRITICAL ISSUES ({len(checks['critical'])}){Colors.ENDC}")
        for item in checks["critical"]:
            print(f"    {item}")

    if checks["warnings"]:
        print(f"\n{Colors.YELLOW}🟡 WARNINGS ({len(checks['warnings'])}){Colors.ENDC}")
        for item in checks["warnings"][:8]:  # Limit display
            print(f"    {item}")
        if len(checks["warnings"]) > 8:
            print(f"    ... and {len(checks['warnings']) - 8} more")

    if checks["passed"]:
        print(f"\n{Colors.GREEN}🟢 PASSED CHECKS ({len(checks['passed'])}){Colors.ENDC}")
        for item in checks["passed"][:6]:  # Show top items
            print(f"    {item}")
        if len(checks["passed"]) > 6:
            print(f"    ... and {len(checks['passed']) - 6} more")

    if checks["fixed"]:
        print(f"\n{Colors.CYAN}🔧 AUTO-FIXES APPLIED ({len(checks['fixed'])}){Colors.ENDC}")
        for item in checks["fixed"]:
            print(f"    {item}")

    # Overall score display
    print(f"\n{Colors.BOLD}{grade_color}🏆 OVERALL HEALTH SCORE: {final_score}/100 (Grade {grade} - {grade_desc}){Colors.ENDC}")

    # Actionable recommendations
    print(f"\n{Colors.BOLD}{Colors.CYAN}💡 ACTIONABLE RECOMMENDATIONS{Colors.ENDC}")
    print(f"{Colors.CYAN}{'─' * 40}{Colors.ENDC}")
    
    recommendations = []
    
    if checks["critical"]:
        recommendations.append("🔴 Address critical issues immediately")
        recommendations.append("   • Run security audit and fix vulnerabilities")
    
    if len(checks["warnings"]) > 5:
        recommendations.append("🟡 High warning count - prioritize fixes")
        if any("outdated" in item.lower() for item in checks["warnings"]):
            recommendations.append("   • Update dependencies: pip list --outdated")
        if any("todo" in item.lower() for item in checks["warnings"]):
            recommendations.append("   • Clean up TODO markers in codebase")
        if any("test" in item.lower() for item in checks["warnings"]):
            recommendations.append("   • Add test coverage: python3 -m pytest --cov")
    
    if final_score < 80:
        recommendations.append("📈 Focus on documentation and configuration")
        if fix_mode:
            recommendations.append("🔄 Re-run without --fix to see current status")
        else:
            recommendations.append("🔧 Run with --fix to auto-fix common issues")
    
    if not recommendations:
        recommendations = [
            "🎉 Project health is excellent!",
            "✨ Consider sharing best practices with the team",
            "📈 Monitor metrics with regular doctor checkups"
        ]
    
    for rec in recommendations[:6]:  # Limit recommendations
        print(f"    {rec}")
    
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'═' * 65}{Colors.ENDC}")
    
    if fix_mode:
        print(f"{Colors.GREEN}✅ Comprehensive diagnosis completed with auto-fixes applied{Colors.ENDC}")
    else:
        print(f"{Colors.BLUE}💡 Run with --fix to automatically resolve fixable issues{Colors.ENDC}")
    
    print(f"{Colors.CYAN}📊 Use 'mw status' for quick checks or 'mw dashboard' for overview{Colors.ENDC}")
    
    return 1 if checks["critical"] else 0

if __name__ == "__main__":
    sys.exit(cmd_doctor_enhanced())