#!/usr/bin/env python3
"""MyWork Test Coverage Analyzer — find untested tools and scaffold tests.

Usage:
    mw test-coverage                Show coverage summary
    mw test-coverage --detail       Show per-file breakdown
    mw test-coverage --scaffold     Generate missing test files
    mw test-coverage --json         Output as JSON
    mw test-coverage --min N        Fail if coverage % < N (for CI)
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def get_project_root() -> Path:
    """Find project root (where tools/ lives)."""
    return Path(__file__).resolve().parent.parent


def discover_tools(root: Path) -> List[str]:
    """Find all tool modules in tools/."""
    tools_dir = root / "tools"
    skip = {"__init__", "__pycache__", "_template", "mw"}
    tools = []
    for f in sorted(tools_dir.glob("*.py")):
        name = f.stem
        if name.startswith("_") and name != "_template":
            continue
        if name in skip:
            continue
        tools.append(name)
    return tools


def discover_tests(root: Path) -> Dict[str, Path]:
    """Find all test files, mapped by the tool name they test."""
    tests_dir = root / "tests"
    mapping = {}
    if not tests_dir.exists():
        return mapping
    for f in sorted(tests_dir.glob("test_*.py")):
        # test_foo.py -> foo
        tool_name = f.stem[5:]  # strip "test_"
        mapping[tool_name] = f
    return mapping


def count_test_functions(test_file: Path) -> int:
    """Count test functions/methods in a test file."""
    try:
        content = test_file.read_text()
        return len(re.findall(r'^\s*def\s+test_', content, re.MULTILINE))
    except Exception:
        return 0


def count_functions(tool_file: Path) -> int:
    """Count public functions in a tool file."""
    try:
        content = tool_file.read_text()
        return len(re.findall(r'^def\s+(?!_)\w+', content, re.MULTILINE))
    except Exception:
        return 0


def analyze(root: Path) -> dict:
    """Full coverage analysis."""
    tools = discover_tools(root)
    tests = discover_tests(root)
    tools_dir = root / "tools"

    covered = []
    uncovered = []
    details = []

    for tool in tools:
        tool_path = tools_dir / f"{tool}.py"
        num_funcs = count_functions(tool_path)
        
        if tool in tests:
            num_tests = count_test_functions(tests[tool])
            covered.append(tool)
            details.append({
                "tool": tool,
                "has_test": True,
                "functions": num_funcs,
                "test_count": num_tests,
                "test_file": str(tests[tool].relative_to(root)),
            })
        else:
            uncovered.append(tool)
            details.append({
                "tool": tool,
                "has_test": False,
                "functions": num_funcs,
                "test_count": 0,
                "test_file": None,
            })

    total = len(tools)
    pct = round(len(covered) / total * 100, 1) if total > 0 else 0

    return {
        "total_tools": total,
        "covered": len(covered),
        "uncovered": len(uncovered),
        "coverage_pct": pct,
        "covered_list": covered,
        "uncovered_list": uncovered,
        "details": details,
    }


def scaffold_test(root: Path, tool_name: str) -> str:
    """Generate a basic test file for a tool."""
    tool_path = root / "tools" / f"{tool_name}.py"
    
    # Extract public functions
    funcs = []
    try:
        content = tool_path.read_text()
        funcs = re.findall(r'^def\s+((?!_)\w+)', content, re.MULTILINE)
    except Exception:
        pass

    lines = [
        f'#!/usr/bin/env python3',
        f'"""Tests for tools/{tool_name}.py"""',
        f'',
        f'import pytest',
        f'import sys',
        f'from pathlib import Path',
        f'',
        f'# Add tools to path',
        f'sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))',
        f'',
    ]

    # Try to import
    lines.append(f'try:')
    lines.append(f'    import {tool_name}')
    lines.append(f'except ImportError:')
    lines.append(f'    pytest.skip("Cannot import {tool_name}", allow_module_level=True)')
    lines.append(f'')

    if funcs:
        for func in funcs[:10]:  # Cap at 10 to keep manageable
            lines.append(f'')
            lines.append(f'def test_{func}_exists():')
            lines.append(f'    """Verify {func} is callable."""')
            lines.append(f'    assert callable(getattr({tool_name}, "{func}", None))')
    else:
        lines.append(f'')
        lines.append(f'def test_module_imports():')
        lines.append(f'    """Verify module can be imported."""')
        lines.append(f'    assert {tool_name} is not None')

    lines.append(f'')
    return '\n'.join(lines)


def print_bar(pct: float, width: int = 30) -> str:
    """Create a progress bar."""
    filled = int(width * pct / 100)
    bar = '█' * filled + '░' * (width - filled)
    if pct >= 80:
        color = '\033[92m'  # green
    elif pct >= 50:
        color = '\033[93m'  # yellow
    else:
        color = '\033[91m'  # red
    return f'{color}{bar}\033[0m {pct}%'


def main(args: list = None) -> int:
    args = args or sys.argv[1:]
    root = get_project_root()
    
    show_detail = '--detail' in args or '-d' in args
    do_scaffold = '--scaffold' in args
    as_json = '--json' in args
    min_val = None
    
    if '--min' in args:
        idx = args.index('--min')
        if idx + 1 < len(args):
            try:
                min_val = float(args[idx + 1])
            except ValueError:
                pass

    result = analyze(root)

    if as_json:
        print(json.dumps(result, indent=2))
        if min_val and result['coverage_pct'] < min_val:
            return 1
        return 0

    # Pretty print
    pct = result['coverage_pct']
    print()
    print('\033[1m  📊 Test Coverage Report\033[0m')
    print('  ' + '─' * 48)
    print(f'  Tools:     {result["total_tools"]}')
    print(f'  Tested:    \033[92m{result["covered"]}\033[0m')
    print(f'  Untested:  \033[91m{result["uncovered"]}\033[0m')
    print(f'  Coverage:  {print_bar(pct)}')
    print()

    if show_detail:
        print('  \033[1mPer-tool breakdown:\033[0m')
        print(f'  {"Tool":<30} {"Tests":<8} {"Funcs":<8} {"Status"}')
        print('  ' + '─' * 58)
        for d in result['details']:
            status = '\033[92m✓\033[0m' if d['has_test'] else '\033[91m✗\033[0m'
            print(f'  {d["tool"]:<30} {d["test_count"]:<8} {d["functions"]:<8} {status}')
        print()

    if result['uncovered_list']:
        print(f'  \033[93mUntested tools ({result["uncovered"]}):\033[0m')
        for i, name in enumerate(result['uncovered_list']):
            if i < 15:
                print(f'    • {name}')
            elif i == 15:
                print(f'    ... and {len(result["uncovered_list"]) - 15} more')
                break
        print()

    if do_scaffold:
        tests_dir = root / 'tests'
        tests_dir.mkdir(exist_ok=True)
        created = 0
        for name in result['uncovered_list']:
            test_path = tests_dir / f'test_{name}.py'
            if not test_path.exists():
                content = scaffold_test(root, name)
                test_path.write_text(content)
                created += 1
                print(f'  \033[92m✓\033[0m Created tests/test_{name}.py')
        if created:
            print(f'\n  \033[92mScaffolded {created} test files.\033[0m Run: pytest tests/')
        else:
            print(f'  All test files already exist.')
        print()

    if min_val and pct < min_val:
        print(f'  \033[91m✗ Coverage {pct}% is below minimum {min_val}%\033[0m')
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
