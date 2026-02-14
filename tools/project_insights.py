#!/usr/bin/env python3
"""
Project Insights — Smart analysis of your codebase
===================================================
Generates actionable insights: code quality trends, tech debt hotspots,
dependency freshness, and contributor patterns.

Usage:
    mw insights              Show all insights
    mw insights --debt       Focus on tech debt
    mw insights --hotspots   Show change hotspots
    mw insights --summary    One-line summary
"""

import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

MYWORK_ROOT = Path(os.environ.get("MYWORK_ROOT", Path(__file__).parent.parent))

# ANSI colors
class C:
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    DIM = "\033[2m"
    END = "\033[0m"


def git(cmd: str, cwd=None) -> str:
    """Run a git command and return stdout."""
    try:
        r = subprocess.run(
            f"git {cmd}", shell=True, capture_output=True, text=True,
            cwd=cwd or MYWORK_ROOT, timeout=10
        )
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def analyze_tech_debt() -> dict:
    """Find TODO/FIXME/HACK/XXX markers across the codebase."""
    markers = defaultdict(list)
    pattern = re.compile(r'#\s*(TODO|FIXME|HACK|XXX|BUG|WORKAROUND)\b[:\s]*(.*)', re.IGNORECASE)
    
    for root, dirs, files in os.walk(MYWORK_ROOT):
        dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', '__pycache__', 'venv', '.venv', 'dist', 'build'}]
        for f in files:
            if not f.endswith(('.py', '.js', '.ts', '.tsx', '.jsx')):
                continue
            fp = Path(root) / f
            try:
                for i, line in enumerate(fp.read_text(errors='ignore').splitlines(), 1):
                    m = pattern.search(line)
                    if m:
                        rel = fp.relative_to(MYWORK_ROOT)
                        markers[m.group(1).upper()].append({
                            'file': str(rel),
                            'line': i,
                            'text': m.group(2).strip()[:80],
                        })
            except Exception:
                continue
    return dict(markers)


def analyze_hotspots(days: int = 30) -> list:
    """Find files that change most frequently (churn = bugs)."""
    since = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    log = git(f'log --since="{since}" --name-only --pretty=format:')
    if not log:
        return []
    
    counts = Counter(f for f in log.splitlines() if f.strip() and not f.startswith('.'))
    return counts.most_common(15)


def analyze_complexity_hotspots() -> list:
    """Find functions that are too long (>50 lines)."""
    long_funcs = []
    
    for root, dirs, files in os.walk(MYWORK_ROOT / "tools"):
        dirs[:] = [d for d in dirs if d not in {'__pycache__', '.git'}]
        for f in files:
            if not f.endswith('.py'):
                continue
            fp = Path(root) / f
            try:
                lines = fp.read_text(errors='ignore').splitlines()
                func_name = None
                func_start = 0
                indent = 0
                
                for i, line in enumerate(lines):
                    m = re.match(r'^(\s*)def (\w+)', line)
                    if m:
                        if func_name and (i - func_start) > 50:
                            long_funcs.append((func_name, f, i - func_start))
                        func_name = m.group(2)
                        func_start = i
                        indent = len(m.group(1))
                
                if func_name and (len(lines) - func_start) > 50:
                    long_funcs.append((func_name, f, len(lines) - func_start))
            except Exception:
                continue
    
    long_funcs.sort(key=lambda x: -x[2])
    return long_funcs[:15]


def analyze_test_coverage() -> dict:
    """Check which tool files have corresponding tests."""
    tools = set()
    tests = set()
    
    tools_dir = MYWORK_ROOT / "tools"
    tests_dir = MYWORK_ROOT / "tests"
    
    if tools_dir.exists():
        for f in tools_dir.iterdir():
            if f.suffix == '.py' and not f.name.startswith('_'):
                tools.add(f.stem)
    
    if tests_dir.exists():
        for f in tests_dir.iterdir():
            if f.name.startswith('test_') and f.suffix == '.py':
                tested = f.stem.replace('test_', '')
                tests.add(tested)
    
    covered = tools & tests
    uncovered = tools - tests
    
    return {
        'total_tools': len(tools),
        'tested': len(covered),
        'untested': sorted(uncovered),
        'coverage_pct': round(len(covered) / max(len(tools), 1) * 100, 1),
    }


def analyze_contributor_patterns(days: int = 30) -> dict:
    """Analyze who's contributing what."""
    since = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    log = git(f'log --since="{since}" --format="%an|%aI" --shortstat')
    if not log:
        return {}
    
    contributors = defaultdict(lambda: {'commits': 0, 'days_active': set()})
    lines = log.splitlines()
    
    for line in lines:
        if '|' in line and '20' in line:
            parts = line.split('|')
            if len(parts) == 2:
                name = parts[0].strip()
                try:
                    date = parts[1][:10]
                    contributors[name]['commits'] += 1
                    contributors[name]['days_active'].add(date)
                except Exception:
                    pass
    
    result = {}
    for name, data in contributors.items():
        result[name] = {
            'commits': data['commits'],
            'active_days': len(data['days_active']),
        }
    return result


def generate_health_grade(debt: dict, hotspots: list, coverage: dict) -> tuple:
    """Generate an overall project health grade A-F."""
    score = 100
    reasons = []
    
    # Tech debt penalty
    total_debt = sum(len(v) for v in debt.values())
    if total_debt > 100:
        score -= 20
        reasons.append(f"{total_debt} tech debt markers")
    elif total_debt > 50:
        score -= 10
        reasons.append(f"{total_debt} tech debt markers")
    
    # Test coverage penalty
    if coverage['coverage_pct'] < 50:
        score -= 25
        reasons.append(f"Only {coverage['coverage_pct']}% test coverage")
    elif coverage['coverage_pct'] < 75:
        score -= 10
        reasons.append(f"{coverage['coverage_pct']}% test coverage")
    
    # Churn penalty (high churn = instability)
    if hotspots and hotspots[0][1] > 50:
        score -= 15
        reasons.append(f"High churn: {hotspots[0][0]} changed {hotspots[0][1]}x")
    
    grade = 'A' if score >= 90 else 'B' if score >= 75 else 'C' if score >= 60 else 'D' if score >= 40 else 'F'
    return grade, score, reasons


def print_insights(args=None):
    """Main entry point — display all insights."""
    args = args or []
    
    if '--help' in args or '-h' in args:
        print(__doc__)
        return 0
    
    summary_only = '--summary' in args
    debt_only = '--debt' in args
    hotspots_only = '--hotspots' in args
    
    # Gather data
    debt = analyze_tech_debt()
    hotspots = analyze_hotspots()
    complexity = analyze_complexity_hotspots()
    coverage = analyze_test_coverage()
    contributors = analyze_contributor_patterns()
    grade, score, reasons = generate_health_grade(debt, hotspots, coverage)
    
    if summary_only:
        grade_color = C.GREEN if grade in 'AB' else C.YELLOW if grade == 'C' else C.RED
        print(f"{grade_color}{C.BOLD}Grade: {grade} ({score}/100){C.END} — {', '.join(reasons) if reasons else 'Looking good!'}")
        return 0
    
    # Header
    grade_color = C.GREEN if grade in 'AB' else C.YELLOW if grade == 'C' else C.RED
    print(f"\n{C.BOLD}{C.CYAN}🔍 Project Insights — MyWork-AI{C.END}")
    print(f"{C.DIM}{'─' * 55}{C.END}")
    print(f"  {C.BOLD}Health Grade: {grade_color}{grade} ({score}/100){C.END}")
    if reasons:
        for r in reasons:
            print(f"  {C.DIM}⚠ {r}{C.END}")
    print()
    
    if not hotspots_only:
        # Tech Debt
        total_debt = sum(len(v) for v in debt.values())
        print(f"{C.BOLD}{C.YELLOW}📋 Tech Debt ({total_debt} items){C.END}")
        for marker, items in sorted(debt.items(), key=lambda x: -len(x[1])):
            emoji = {'TODO': '📝', 'FIXME': '🔧', 'HACK': '⚡', 'XXX': '❌', 'BUG': '🐛', 'WORKAROUND': '🔄'}.get(marker, '📌')
            print(f"  {emoji} {marker}: {len(items)}")
            if not debt_only:
                for item in items[:3]:
                    print(f"     {C.DIM}{item['file']}:{item['line']} — {item['text']}{C.END}")
                if len(items) > 3:
                    print(f"     {C.DIM}... and {len(items) - 3} more{C.END}")
        print()
    
    if not debt_only:
        # Change Hotspots
        print(f"{C.BOLD}{C.RED}🔥 Change Hotspots (30d){C.END}")
        for fname, count in hotspots[:10]:
            bar = '█' * min(count // 3, 20)
            print(f"  {C.DIM}{count:3d}{C.END} {bar} {fname}")
        print()
        
        # Complexity Hotspots
        if complexity:
            print(f"{C.BOLD}{C.BLUE}🏗️  Long Functions (>50 lines){C.END}")
            for func, fname, lines in complexity[:8]:
                color = C.RED if lines > 200 else C.YELLOW if lines > 100 else C.DIM
                print(f"  {color}{lines:4d} lines{C.END}  {func}() in {fname}")
            print()
    
    # Test Coverage
    print(f"{C.BOLD}{C.GREEN}🧪 Test Coverage{C.END}")
    pct = coverage['coverage_pct']
    bar_filled = int(pct / 5)
    bar = f"{'█' * bar_filled}{'░' * (20 - bar_filled)}"
    color = C.GREEN if pct >= 75 else C.YELLOW if pct >= 50 else C.RED
    print(f"  {color}{bar} {pct}%{C.END} ({coverage['tested']}/{coverage['total_tools']} tools tested)")
    if coverage['untested'][:5]:
        print(f"  {C.DIM}Untested: {', '.join(coverage['untested'][:5])}{C.END}")
    print()
    
    # Contributors
    if contributors:
        print(f"{C.BOLD}{C.CYAN}👥 Contributors (30d){C.END}")
        for name, data in sorted(contributors.items(), key=lambda x: -x[1]['commits']):
            print(f"  {name}: {data['commits']} commits, {data['active_days']} active days")
        print()
    
    return 0


def cmd_insights(args=None):
    """Entry point for mw insights."""
    return print_insights(args)


if __name__ == "__main__":
    sys.exit(print_insights(sys.argv[1:]))
