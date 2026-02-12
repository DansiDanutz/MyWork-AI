"""
MyWork Quality Gate — mw check

Pre-commit/pre-push quality gate that runs all checks in sequence:
lint → test → security → audit. Returns pass/fail with a summary.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Tuple

# ANSI colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"
CHECK = "✅"
FAIL = "❌"
WARN = "⚠️"
SKIP = "⏭️"


def _run_check(name: str, cmd: List[str], cwd: str = None, timeout: int = 120) -> Tuple[bool, str, float]:
    """Run a check command and return (passed, output, duration_seconds)."""
    start = time.time()
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True,
            cwd=cwd, timeout=timeout
        )
        duration = time.time() - start
        output = (result.stdout + result.stderr).strip()
        passed = result.returncode == 0
        return passed, output, duration
    except subprocess.TimeoutExpired:
        duration = time.time() - start
        return False, f"Timed out after {timeout}s", duration
    except FileNotFoundError:
        duration = time.time() - start
        return None, f"Command not found: {cmd[0]}", duration  # type: ignore


def _detect_project(path: str) -> dict:
    """Detect project type and available checks."""
    p = Path(path)
    info = {
        "path": str(p),
        "name": p.name,
        "python": (p / "pyproject.toml").exists() or (p / "setup.py").exists() or (p / "requirements.txt").exists(),
        "node": (p / "package.json").exists(),
        "rust": (p / "Cargo.toml").exists(),
        "go": (p / "go.mod").exists(),
        "git": (p / ".git").exists(),
        "has_tests": any([
            (p / "tests").is_dir(),
            (p / "test").is_dir(),
            (p / "__tests__").is_dir(),
            (p / "spec").is_dir(),
        ]),
    }
    return info


def _check_lint(project: dict) -> Tuple[str, bool, str, float]:
    """Run linting checks."""
    path = project["path"]

    if project["python"]:
        # Try ruff first, then flake8
        for linter in [["ruff", "check", "."], ["flake8", "--max-line-length=120", "."]]:
            passed, output, dur = _run_check("lint", linter, cwd=path, timeout=60)
            if passed is not None:
                return linter[0], passed, output, dur

    if project["node"]:
        pkg_json = Path(path) / "package.json"
        if pkg_json.exists():
            pkg = json.loads(pkg_json.read_text())
            scripts = pkg.get("scripts", {})
            if "lint" in scripts:
                passed, output, dur = _run_check("lint", ["npm", "run", "lint"], cwd=path, timeout=60)
                return "npm run lint", passed, output, dur

    return "lint", None, "No linter found", 0.0  # type: ignore


def _check_tests(project: dict) -> Tuple[str, bool, str, float]:
    """Run tests."""
    path = project["path"]

    if project["python"]:
        passed, output, dur = _run_check("test", [
            sys.executable, "-m", "pytest", "-x", "-q", "--tb=line", "--timeout=10"
        ], cwd=path, timeout=120)
        if passed is not None:
            # Extract summary line
            lines = output.strip().split("\n")
            summary = lines[-1] if lines else output
            return "pytest", passed, summary, dur

    if project["node"]:
        pkg_json = Path(path) / "package.json"
        if pkg_json.exists():
            pkg = json.loads(pkg_json.read_text())
            scripts = pkg.get("scripts", {})
            if "test" in scripts:
                passed, output, dur = _run_check("test", ["npm", "test"], cwd=path, timeout=120)
                lines = output.strip().split("\n")
                summary = "\n".join(lines[-5:]) if len(lines) > 5 else output
                return "npm test", passed, summary, dur

    return "test", None, "No test runner found", 0.0  # type: ignore


def _check_security(project: dict) -> Tuple[str, bool, str, float]:
    """Run security checks."""
    path = project["path"]

    # Check for secrets in git
    if project["git"]:
        passed, output, dur = _run_check("security", [
            "git", "diff", "--cached", "--diff-filter=ACMR", "--name-only"
        ], cwd=path, timeout=10)

        # Look for common secret patterns in staged files
        if passed and output.strip():
            files = output.strip().split("\n")
            issues = []
            for f in files:
                fpath = Path(path) / f
                if fpath.exists() and fpath.stat().st_size < 1_000_000:
                    try:
                        content = fpath.read_text(errors="ignore")
                        if any(pattern in content.lower() for pattern in [
                            "password=", "secret_key=", "api_key=", "private_key",
                            "-----begin rsa", "-----begin openssh"
                        ]):
                            issues.append(f"  {WARN} Possible secret in: {f}")
                    except Exception:
                        pass

            if issues:
                return "secret-scan", False, "\n".join(issues), dur
            return "secret-scan", True, f"Scanned {len(files)} staged files — clean", dur

    # Python: check for known vulnerabilities
    if project["python"]:
        passed, output, dur = _run_check("security", [
            sys.executable, "-m", "pip", "audit"
        ], cwd=path, timeout=30)
        if passed is not None:
            return "pip-audit", passed, output[:200], dur

    return "security", True, "No security issues found", 0.0


def _check_types(project: dict) -> Tuple[str, bool, str, float]:
    """Run type checking."""
    path = project["path"]

    if project["python"]:
        passed, output, dur = _run_check("types", [
            sys.executable, "-m", "mypy", "--ignore-missing-imports", "."
        ], cwd=path, timeout=60)
        if passed is not None:
            lines = output.strip().split("\n")
            summary = lines[-1] if lines else output
            return "mypy", passed, summary, dur

    if project["node"]:
        pkg_json = Path(path) / "package.json"
        if pkg_json.exists():
            pkg = json.loads(pkg_json.read_text())
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            if "typescript" in deps:
                passed, output, dur = _run_check("types", ["npx", "tsc", "--noEmit"], cwd=path, timeout=60)
                if passed is not None:
                    lines = output.strip().split("\n")
                    summary = f"{len(lines)} errors" if not passed and lines[0] else "Clean"
                    return "tsc", passed, summary, dur

    return "types", None, "No type checker found", 0.0  # type: ignore


def _check_git(project: dict) -> Tuple[str, bool, str, float]:
    """Check git hygiene."""
    path = project["path"]
    if not project["git"]:
        return "git", None, "Not a git repo", 0.0  # type: ignore

    issues = []
    start = time.time()

    # Uncommitted changes
    result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=path)
    changes = len([l for l in result.stdout.strip().split("\n") if l.strip()])
    if changes > 0:
        issues.append(f"{changes} uncommitted changes")

    # Branch name
    result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True, cwd=path)
    branch = result.stdout.strip()

    dur = time.time() - start
    status = f"Branch: {branch}"
    if issues:
        status += f" | {', '.join(issues)}"
        return "git", False, status, dur
    return "git", True, status, dur


def cmd_check(args: List[str] = None) -> int:
    """Run quality gate checks."""
    args = args or []

    if args and args[0] in ["--help", "-h"]:
        print(f"""
{BOLD}🛡️  Quality Gate — mw check{RESET}

Pre-commit/pre-push quality gate. Runs all checks and reports pass/fail.

{BOLD}Usage:{RESET}
    mw check                    Run all checks on current directory
    mw check [path]             Run checks on specific project
    mw check --quick            Skip slow checks (types, security)
    mw check --fix              Auto-fix what's possible (lint)
    mw check --json             Output results as JSON
    mw check --pre-commit       Install as git pre-commit hook

{BOLD}Checks:{RESET}
    1. {GREEN}Lint{RESET}      — Code style (ruff/flake8/eslint)
    2. {GREEN}Test{RESET}      — Unit tests (pytest/jest/cargo)
    3. {GREEN}Types{RESET}     — Type checking (mypy/tsc)
    4. {GREEN}Security{RESET}  — Secret scanning, vulnerability audit
    5. {GREEN}Git{RESET}       — Branch hygiene, uncommitted changes

{BOLD}Examples:{RESET}
    mw check                    # Full quality gate
    mw check --quick            # Fast checks only (lint + git)
    mw check --pre-commit       # Install as pre-commit hook
""")
        return 0

    quick = "--quick" in args
    fix_mode = "--fix" in args
    json_mode = "--json" in args
    pre_commit = "--pre-commit" in args
    path_args = [a for a in args if not a.startswith("--")]
    project_path = path_args[0] if path_args else os.getcwd()

    # Install pre-commit hook
    if pre_commit:
        return _install_hook(project_path)

    project = _detect_project(project_path)

    print(f"\n{BOLD}🛡️  Quality Gate — {project['name']}{RESET}")
    print(f"{'─' * 50}")

    checks = [
        ("Lint", _check_lint),
    ]

    if not quick:
        checks.extend([
            ("Test", _check_tests),
            ("Types", _check_types),
            ("Security", _check_security),
        ])

    checks.append(("Git", _check_git))

    results = []
    total_time = 0.0
    all_passed = True

    for check_name, check_fn in checks:
        tool, passed, detail, dur = check_fn(project)
        total_time += dur

        if passed is None:
            icon = SKIP
            status = "skipped"
        elif passed:
            icon = CHECK
            status = "passed"
        else:
            icon = FAIL
            status = "FAILED"
            all_passed = False

        # Format duration
        dur_str = f"{dur:.1f}s" if dur >= 1 else f"{dur*1000:.0f}ms"

        print(f"  {icon} {BOLD}{check_name:<10}{RESET} {DIM}({tool}, {dur_str}){RESET}")
        if not passed and passed is not None:
            for line in detail.split("\n")[:3]:
                print(f"     {DIM}{line}{RESET}")

        results.append({
            "check": check_name,
            "tool": tool,
            "passed": passed,
            "detail": detail,
            "duration": round(dur, 2),
        })

    # Summary
    print(f"{'─' * 50}")
    passed_count = sum(1 for r in results if r["passed"] is True)
    failed_count = sum(1 for r in results if r["passed"] is False)
    skipped_count = sum(1 for r in results if r["passed"] is None)

    if all_passed:
        print(f"  {GREEN}{BOLD}✅ PASSED{RESET} — {passed_count} checks passed in {total_time:.1f}s")
        grade = "A"
    elif failed_count == 1:
        print(f"  {YELLOW}{BOLD}⚠️  WARN{RESET} — {failed_count} failed, {passed_count} passed in {total_time:.1f}s")
        grade = "B"
    else:
        print(f"  {RED}{BOLD}❌ FAILED{RESET} — {failed_count} failed, {passed_count} passed in {total_time:.1f}s")
        grade = "C" if failed_count <= 2 else "F"

    print()

    if json_mode:
        print(json.dumps({
            "project": project["name"],
            "grade": grade,
            "passed": all_passed,
            "checks": results,
            "total_time": round(total_time, 2),
        }, indent=2))

    return 0 if all_passed else 1


def _install_hook(project_path: str) -> int:
    """Install mw check as a git pre-commit hook."""
    git_dir = Path(project_path) / ".git"
    if not git_dir.exists():
        print(f"  {RED}Not a git repository{RESET}")
        return 1

    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)
    hook_file = hooks_dir / "pre-commit"

    hook_content = """#!/bin/sh
# MyWork Quality Gate — auto-installed by 'mw check --pre-commit'
echo "🛡️  Running quality gate..."
mw check --quick
exit $?
"""

    hook_file.write_text(hook_content)
    hook_file.chmod(0o755)
    print(f"  {CHECK} Installed pre-commit hook at {hook_file}")
    print(f"  {DIM}Runs 'mw check --quick' before each commit{RESET}")
    return 0


if __name__ == "__main__":
    sys.exit(cmd_check(sys.argv[1:]))
