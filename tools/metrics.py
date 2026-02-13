#!/usr/bin/env python3
"""
mw metrics — Code Metrics Dashboard
====================================
Analyzes any project for lines of code, complexity, file distribution,
test coverage estimation, code quality score, and tech debt indicators.

Usage:
    mw metrics [path] [--json] [--format=compact|full] [--compare=<snapshot>]
"""

import os
import sys
import json
import re
import ast
import time
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional

# Language detection by extension
LANG_MAP = {
    '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript', '.tsx': 'TypeScript (JSX)',
    '.jsx': 'JavaScript (JSX)', '.go': 'Go', '.rs': 'Rust', '.java': 'Java',
    '.rb': 'Ruby', '.php': 'PHP', '.c': 'C', '.cpp': 'C++', '.h': 'C/C++ Header',
    '.cs': 'C#', '.swift': 'Swift', '.kt': 'Kotlin', '.scala': 'Scala',
    '.sh': 'Shell', '.bash': 'Shell', '.zsh': 'Shell', '.fish': 'Shell',
    '.html': 'HTML', '.css': 'CSS', '.scss': 'SCSS', '.less': 'LESS',
    '.sql': 'SQL', '.md': 'Markdown', '.yaml': 'YAML', '.yml': 'YAML',
    '.json': 'JSON', '.toml': 'TOML', '.xml': 'XML', '.vue': 'Vue',
    '.svelte': 'Svelte', '.dart': 'Dart', '.lua': 'Lua', '.r': 'R',
    '.R': 'R', '.zig': 'Zig', '.nim': 'Nim', '.ex': 'Elixir', '.exs': 'Elixir',
}

SKIP_DIRS = {
    'node_modules', '.git', '__pycache__', '.venv', 'venv', 'env',
    '.tox', '.mypy_cache', '.pytest_cache', 'dist', 'build', '.next',
    'target', 'vendor', '.cargo', 'coverage', '.coverage', 'htmlcov',
    '.egg-info', '*.egg-info', '.idea', '.vscode',
}

TEST_PATTERNS = [
    r'test_', r'_test\.', r'\.test\.', r'\.spec\.', r'tests/', r'__tests__/',
    r'spec/', r'_spec\.', r'\.spec\.',
]


def should_skip(path: str) -> bool:
    parts = Path(path).parts
    return any(p in SKIP_DIRS or p.endswith('.egg-info') for p in parts)


def count_lines(filepath: str) -> Tuple[int, int, int]:
    """Returns (total, code, blank) line counts."""
    try:
        with open(filepath, 'r', errors='ignore') as f:
            lines = f.readlines()
    except (OSError, UnicodeDecodeError):
        return 0, 0, 0

    total = len(lines)
    blank = sum(1 for l in lines if not l.strip())
    code = total - blank
    return total, code, blank


def is_test_file(filepath: str) -> bool:
    fp = filepath.lower()
    return any(re.search(p, fp) for p in TEST_PATTERNS)


def python_complexity(filepath: str) -> Dict:
    """Analyze Python file complexity using AST."""
    try:
        with open(filepath, 'r', errors='ignore') as f:
            tree = ast.parse(f.read(), filename=filepath)
    except Exception:
        return {'functions': 0, 'classes': 0, 'avg_complexity': 0}

    functions = 0
    classes = 0
    complexities = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            functions += 1
            # McCabe-like: count branches
            cc = 1
            for child in ast.walk(node):
                if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler,
                                      ast.With, ast.Assert, ast.comprehension)):
                    cc += 1
                elif isinstance(child, ast.BoolOp):
                    cc += len(child.values) - 1
            complexities.append(cc)
        elif isinstance(node, ast.ClassDef):
            classes += 1

    avg = sum(complexities) / len(complexities) if complexities else 0
    return {
        'functions': functions,
        'classes': classes,
        'avg_complexity': round(avg, 1),
        'max_complexity': max(complexities) if complexities else 0,
        'high_complexity_count': sum(1 for c in complexities if c > 10),
    }


def detect_tech_debt(filepath: str) -> List[str]:
    """Find TODO/FIXME/HACK/XXX markers."""
    markers = []
    try:
        with open(filepath, 'r', errors='ignore') as f:
            for i, line in enumerate(f, 1):
                for tag in ('TODO', 'FIXME', 'HACK', 'XXX', 'DEPRECATED'):
                    if tag in line:
                        markers.append(f"{filepath}:{i}: {tag}")
                        break
    except OSError:
        pass
    return markers


def analyze_project(root: str) -> Dict:
    """Full project analysis."""
    root = os.path.abspath(root)
    lang_stats = defaultdict(lambda: {'files': 0, 'total': 0, 'code': 0, 'blank': 0})
    test_files = 0
    test_lines = 0
    source_files = 0
    source_lines = 0
    all_complexities = []
    tech_debt = []
    largest_files = []
    file_count = 0

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.endswith('.egg-info')]
        rel_dir = os.path.relpath(dirpath, root)

        if should_skip(rel_dir):
            continue

        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in LANG_MAP:
                continue

            filepath = os.path.join(dirpath, fname)
            rel_path = os.path.relpath(filepath, root)

            if should_skip(rel_path):
                continue

            lang = LANG_MAP[ext]
            total, code, blank = count_lines(filepath)

            if total == 0:
                continue

            file_count += 1
            lang_stats[lang]['files'] += 1
            lang_stats[lang]['total'] += total
            lang_stats[lang]['code'] += code
            lang_stats[lang]['blank'] += blank

            is_test = is_test_file(rel_path)
            if is_test:
                test_files += 1
                test_lines += code
            else:
                source_files += 1
                source_lines += code

            largest_files.append((code, rel_path))

            # Python complexity
            if ext == '.py':
                cx = python_complexity(filepath)
                if cx['functions'] > 0:
                    all_complexities.append(cx)

            # Tech debt
            if ext in ('.py', '.js', '.ts', '.tsx', '.jsx', '.go', '.rs', '.java'):
                debt = detect_tech_debt(filepath)
                tech_debt.extend(debt)

    largest_files.sort(reverse=True)
    largest_files = largest_files[:10]

    # Calculate quality score (0-100)
    score = 100
    total_code = sum(s['code'] for s in lang_stats.values())

    # Deduct for low test ratio
    if source_lines > 0:
        test_ratio = test_lines / source_lines
        if test_ratio < 0.1:
            score -= 15
        elif test_ratio < 0.3:
            score -= 5

    # Deduct for tech debt
    debt_per_kloc = (len(tech_debt) / (total_code / 1000)) if total_code > 1000 else 0
    if debt_per_kloc > 10:
        score -= 15
    elif debt_per_kloc > 5:
        score -= 8
    elif debt_per_kloc > 2:
        score -= 3

    # Deduct for high complexity
    high_cx = sum(c.get('high_complexity_count', 0) for c in all_complexities)
    if high_cx > 10:
        score -= 15
    elif high_cx > 5:
        score -= 8
    elif high_cx > 0:
        score -= 3

    avg_cx = 0
    if all_complexities:
        avg_cx = sum(c['avg_complexity'] for c in all_complexities) / len(all_complexities)

    score = max(0, min(100, score))

    return {
        'root': root,
        'file_count': file_count,
        'languages': dict(lang_stats),
        'total_lines': sum(s['total'] for s in lang_stats.values()),
        'total_code': total_code,
        'total_blank': sum(s['blank'] for s in lang_stats.values()),
        'source_files': source_files,
        'source_lines': source_lines,
        'test_files': test_files,
        'test_lines': test_lines,
        'test_ratio': round(test_lines / source_lines, 2) if source_lines > 0 else 0,
        'tech_debt_count': len(tech_debt),
        'tech_debt_per_kloc': round(debt_per_kloc, 1),
        'avg_complexity': round(avg_cx, 1),
        'high_complexity_functions': high_cx,
        'largest_files': [(c, p) for c, p in largest_files],
        'quality_score': score,
        'quality_grade': 'A' if score >= 90 else 'B' if score >= 75 else 'C' if score >= 60 else 'D' if score >= 40 else 'F',
    }


def print_report(data: Dict, compact: bool = False):
    """Pretty-print metrics report."""
    print(f"\n\033[1m📊 Code Metrics: {os.path.basename(data['root'])}\033[0m")
    print("=" * 60)

    # Quality badge
    grade = data['quality_grade']
    score = data['quality_score']
    grade_colors = {'A': '\033[92m', 'B': '\033[92m', 'C': '\033[93m', 'D': '\033[91m', 'F': '\033[91m'}
    color = grade_colors.get(grade, '')
    print(f"\n  Quality: {color}{grade} ({score}/100)\033[0m")

    # Summary
    print(f"\n\033[1m📁 Overview\033[0m")
    print(f"  Files:        {data['file_count']:,}")
    print(f"  Total lines:  {data['total_lines']:,}")
    print(f"  Code lines:   {data['total_code']:,}")
    print(f"  Blank lines:  {data['total_blank']:,}")

    # Languages
    print(f"\n\033[1m🔤 Languages\033[0m")
    langs = sorted(data['languages'].items(), key=lambda x: x[1]['code'], reverse=True)
    for lang, stats in langs[:10]:
        pct = (stats['code'] / data['total_code'] * 100) if data['total_code'] > 0 else 0
        bar = '█' * int(pct / 3) + '░' * (33 - int(pct / 3))
        print(f"  {lang:<20} {stats['code']:>6} lines ({pct:4.1f}%) {bar} [{stats['files']} files]")

    # Testing
    print(f"\n\033[1m🧪 Testing\033[0m")
    print(f"  Test files:   {data['test_files']}")
    print(f"  Test lines:   {data['test_lines']:,}")
    print(f"  Test ratio:   {data['test_ratio']:.0%} (test lines / source lines)")

    # Complexity (Python)
    if data['avg_complexity'] > 0:
        print(f"\n\033[1m🧠 Complexity (Python)\033[0m")
        print(f"  Avg cyclomatic: {data['avg_complexity']}")
        hc = data['high_complexity_functions']
        hc_color = '\033[91m' if hc > 5 else '\033[93m' if hc > 0 else '\033[92m'
        print(f"  High complexity (>10): {hc_color}{hc}\033[0m")

    # Tech debt
    print(f"\n\033[1m🔧 Tech Debt\033[0m")
    print(f"  Markers:      {data['tech_debt_count']} (TODO/FIXME/HACK/XXX)")
    print(f"  Per 1K lines: {data['tech_debt_per_kloc']}")

    if not compact:
        # Largest files
        print(f"\n\033[1m📏 Largest Files\033[0m")
        for code_lines, path in data['largest_files'][:7]:
            print(f"  {code_lines:>6} lines  {path}")

    print()


def cmd_metrics(args: list = None) -> int:
    """Entry point for mw metrics."""
    args = args or []
    path = '.'
    as_json = False
    compact = False

    for a in args:
        if a == '--json':
            as_json = True
        elif a == '--compact':
            compact = True
        elif not a.startswith('-'):
            path = a

    if not os.path.isdir(path):
        print(f"Error: '{path}' is not a directory")
        return 1

    start = time.time()
    data = analyze_project(path)
    data['analysis_time'] = round(time.time() - start, 2)

    if as_json:
        print(json.dumps(data, indent=2))
    else:
        print_report(data, compact=compact)
        print(f"  ⏱️  Analyzed in {data['analysis_time']}s")

    return 0


if __name__ == '__main__':
    sys.exit(cmd_metrics(sys.argv[1:]))
