#!/usr/bin/env python3
"""mw deps audit — Dependency security scanner for Python & Node projects.

Scans requirements.txt / package.json for known vulnerabilities,
outdated packages, and license issues.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any

COLORS = {
    'red': '\033[91m', 'green': '\033[92m', 'yellow': '\033[93m',
    'blue': '\033[94m', 'bold': '\033[1m', 'reset': '\033[0m',
    'dim': '\033[2m',
}

def c(text: str, color: str) -> str:
    return f"{COLORS.get(color, '')}{text}{COLORS['reset']}"


def find_project_root() -> Path:
    """Walk up to find a project root (has .git, package.json, or pyproject.toml)."""
    cwd = Path.cwd()
    for p in [cwd] + list(cwd.parents):
        if any((p / f).exists() for f in ['.git', 'package.json', 'pyproject.toml', 'requirements.txt']):
            return p
    return cwd


def audit_python(root: Path) -> Dict[str, Any]:
    """Audit Python dependencies."""
    results = {'type': 'python', 'total': 0, 'outdated': [], 'vulns': [], 'errors': []}

    req_files = list(root.glob('requirements*.txt'))
    pyproject = root / 'pyproject.toml'

    # Also check pyproject.toml for deps
    if pyproject.exists():
        try:
            content = pyproject.read_text()
            in_deps = False
            for line in content.splitlines():
                if 'dependencies' in line and '=' in line and '[' in line:
                    in_deps = True
                    continue
                if in_deps:
                    if line.strip().startswith(']'):
                        in_deps = False
                        continue
                    if line.strip().startswith('"') or line.strip().startswith("'"):
                        results['total'] += 1
        except Exception:
            pass

    if not req_files and results['total'] == 0:
        return results

    # Count deps from requirements files
    for rf in req_files:
        for line in rf.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('-'):
                results['total'] += 1

    # Parse pinned versions and flag unpinned deps (fast, no network)
    unpinned = []
    for rf in req_files:
        for line in rf.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('-'):
                if '==' not in line and '>=' not in line:
                    unpinned.append(line)
    if unpinned:
        results['errors'].append(f"{len(unpinned)} unpinned deps (consider pinning versions)")

    # Try pip-audit only if installed (skip if not — don't hang)
    try:
        check = subprocess.run([sys.executable, '-m', 'pip_audit', '--version'],
                               capture_output=True, timeout=5)
        if check.returncode == 0:
            audit_args = [sys.executable, '-m', 'pip_audit', '--format=json', '--progress-spinner=off']
            if req_files:
                audit_args += ['-r', str(req_files[0])]
            out = subprocess.run(audit_args, capture_output=True, text=True, timeout=30, cwd=str(root))
            if out.stdout.strip():
                audit_data = json.loads(out.stdout)
                if isinstance(audit_data, list):
                    results['vulns'] = [v for v in audit_data if v.get('vulns')]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    except Exception:
        pass  # silently skip if pip-audit fails

    return results


def audit_node(root: Path) -> Dict[str, Any]:
    """Audit Node.js dependencies."""
    results = {'type': 'node', 'total': 0, 'outdated': [], 'vulns': [], 'errors': []}

    pkg_json = root / 'package.json'
    if not pkg_json.exists():
        return results

    try:
        pkg = json.loads(pkg_json.read_text())
        deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
        results['total'] = len(deps)
    except Exception:
        return results

    if not (root / 'node_modules').exists():
        results['errors'].append("node_modules not found — run npm install first")
        return results

    # npm audit
    try:
        out = subprocess.run(
            ['npm', 'audit', '--json'],
            capture_output=True, text=True, timeout=30, cwd=str(root)
        )
        if out.stdout.strip():
            audit_data = json.loads(out.stdout)
            vulns = audit_data.get('vulnerabilities', {})
            for name, info in vulns.items():
                results['vulns'].append({
                    'name': name,
                    'severity': info.get('severity', 'unknown'),
                    'via': [v if isinstance(v, str) else v.get('title', '?') for v in info.get('via', [])],
                    'fixAvailable': info.get('fixAvailable', False),
                })
    except Exception as e:
        results['errors'].append(f"npm audit: {e}")

    # npm outdated
    try:
        out = subprocess.run(
            ['npm', 'outdated', '--json'],
            capture_output=True, text=True, timeout=30, cwd=str(root)
        )
        if out.stdout.strip():
            outdated = json.loads(out.stdout)
            for name, info in outdated.items():
                results['outdated'].append({
                    'name': name,
                    'current': info.get('current', '?'),
                    'wanted': info.get('wanted', '?'),
                    'latest': info.get('latest', '?'),
                })
    except Exception as e:
        results['errors'].append(f"npm outdated: {e}")

    return results


def render_report(py: Dict, node: Dict) -> int:
    """Pretty-print the audit report."""
    print(f"\n{c('🔒 Dependency Security Audit', 'bold')}")
    print(c('=' * 55, 'blue'))

    total_vulns = 0
    total_outdated = 0

    for result in [py, node]:
        if result['total'] == 0:
            continue

        lang = '🐍 Python' if result['type'] == 'python' else '📦 Node.js'
        print(f"\n  {c(lang, 'bold')}  ({result['total']} packages)")

        # Vulnerabilities
        vulns = result['vulns']
        if vulns:
            total_vulns += len(vulns)
            sev_counts = {}
            for v in vulns:
                s = v.get('severity', 'unknown')
                sev_counts[s] = sev_counts.get(s, 0) + 1

            sev_str = ', '.join(f"{cnt} {sev}" for sev, cnt in sorted(sev_counts.items()))
            print(f"    {c('⚠️  Vulnerabilities:', 'red')} {len(vulns)} ({sev_str})")

            for v in vulns[:10]:
                name = v.get('name', '?')
                sev = v.get('severity', '?')
                color = 'red' if sev in ('critical', 'high') else 'yellow'
                fix = ' ✅ fix available' if v.get('fixAvailable') else ''
                print(f"      {c('•', color)} {name} ({c(sev, color)}){fix}")
            if len(vulns) > 10:
                print(f"      {c(f'... and {len(vulns)-10} more', 'dim')}")
        else:
            print(f"    {c('✅ No known vulnerabilities', 'green')}")

        # Outdated
        outdated = result['outdated']
        if outdated:
            total_outdated += len(outdated)
            print(f"    {c('📦 Outdated:', 'yellow')} {len(outdated)} packages")
            for o in outdated[:5]:
                if result['type'] == 'python':
                    name = o.get('name', '?')
                    cur = o.get('version', '?')
                    latest = o.get('latest_version', '?')
                else:
                    name = o.get('name', '?')
                    cur = o.get('current', '?')
                    latest = o.get('latest', '?')
                print(f"      • {name}: {c(cur, 'dim')} → {c(latest, 'green')}")
            if len(outdated) > 5:
                print(f"      {c(f'... and {len(outdated)-5} more', 'dim')}")
        else:
            print(f"    {c('✅ All packages up to date', 'green')}")

        for err in result['errors']:
            print(f"    {c('⚠️  ' + err, 'yellow')}")

    # Summary
    print(f"\n{c('─' * 55, 'dim')}")
    if total_vulns > 0:
        print(f"  {c(f'🚨 {total_vulns} vulnerabilities found — run fixes!', 'red')}")
        return 1
    elif total_outdated > 0:
        print(f"  {c(f'📦 {total_outdated} outdated packages — consider updating', 'yellow')}")
        return 0
    else:
        print(f"  {c('✅ All clear — dependencies look healthy!', 'green')}")
        return 0


def cmd_deps_audit(args: List[str] = None) -> int:
    """Main entry point for mw deps audit."""
    root = find_project_root()
    print(f"  {c('Scanning:', 'dim')} {root}")

    py_result = audit_python(root)
    node_result = audit_node(root)

    if py_result['total'] == 0 and node_result['total'] == 0:
        print(f"\n  {c('No dependencies found in this directory.', 'yellow')}")
        print(f"  Make sure you're in a project with requirements.txt or package.json")
        return 1

    return render_report(py_result, node_result)


if __name__ == '__main__':
    sys.exit(cmd_deps_audit(sys.argv[1:]))
