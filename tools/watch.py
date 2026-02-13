#!/usr/bin/env python3
"""
mw watch — Smart File Watcher with Auto-Test
=============================================
Watches project files and automatically runs relevant tests when changes are detected.

Usage:
    mw watch                    Watch current directory, auto-run tests
    mw watch --test-cmd "pytest" Override test command
    mw watch --dir src/         Watch specific directory
    mw watch --lint             Also run linting on changes
    mw watch --build            Also run build on changes
    mw watch --debounce 500     Debounce delay in ms (default: 300)
"""

import os
import sys
import time
import subprocess
import hashlib
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Set, Optional, List

# ANSI colors
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
RESET = "\033[0m"
CLEAR_LINE = "\033[2K\r"

# File extensions to watch by language
WATCH_PATTERNS = {
    "python": {".py"},
    "javascript": {".js", ".jsx", ".ts", ".tsx"},
    "rust": {".rs"},
    "go": {".go"},
    "ruby": {".rb"},
    "java": {".java"},
    "css": {".css", ".scss", ".less"},
    "html": {".html", ".htm"},
}

# Test commands by detection
TEST_COMMANDS = {
    "pytest.ini": "python -m pytest -x --tb=short",
    "pyproject.toml": "python -m pytest -x --tb=short",
    "setup.py": "python -m pytest -x --tb=short",
    "package.json": "npm test",
    "Cargo.toml": "cargo test",
    "go.mod": "go test ./...",
    "Gemfile": "bundle exec rspec",
    "Makefile": "make test",
}

LINT_COMMANDS = {
    "pyproject.toml": "python -m ruff check --fix",
    ".flake8": "python -m flake8",
    "package.json": "npm run lint",
    "Cargo.toml": "cargo clippy",
    ".eslintrc.json": "npx eslint --fix",
    ".eslintrc.js": "npx eslint --fix",
}

BUILD_COMMANDS = {
    "package.json": "npm run build",
    "Cargo.toml": "cargo build",
    "go.mod": "go build ./...",
    "Makefile": "make build",
    "pyproject.toml": "python -m build",
}


def detect_project_type(directory: str) -> str:
    """Detect project type from config files."""
    for marker, _ in TEST_COMMANDS.items():
        if os.path.exists(os.path.join(directory, marker)):
            return marker
    return ""


def detect_test_command(directory: str) -> str:
    """Auto-detect the test command."""
    for marker, cmd in TEST_COMMANDS.items():
        if os.path.exists(os.path.join(directory, marker)):
            return cmd
    return ""


def detect_lint_command(directory: str) -> str:
    """Auto-detect the lint command."""
    for marker, cmd in LINT_COMMANDS.items():
        if os.path.exists(os.path.join(directory, marker)):
            return cmd
    return ""


def detect_build_command(directory: str) -> str:
    """Auto-detect the build command."""
    for marker, cmd in BUILD_COMMANDS.items():
        if os.path.exists(os.path.join(directory, marker)):
            return cmd
    return ""


def get_watchable_extensions(directory: str) -> Set[str]:
    """Determine which file extensions to watch."""
    extensions = set()
    for lang, exts in WATCH_PATTERNS.items():
        for ext in exts:
            # Check if any files with this extension exist
            for root, _, files in os.walk(directory):
                if any(skip in root for skip in ["node_modules", ".git", "__pycache__", "dist", "build", ".venv", "venv"]):
                    continue
                if any(f.endswith(ext) for f in files):
                    extensions.update(exts)
                    break
    return extensions if extensions else {".py", ".js", ".ts", ".tsx", ".jsx"}


def get_file_hash(filepath: str) -> str:
    """Get MD5 hash of file contents."""
    try:
        with open(filepath, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except (OSError, IOError):
        return ""


def scan_files(directory: str, extensions: Set[str]) -> Dict[str, str]:
    """Scan directory and return {filepath: hash} dict."""
    files = {}
    skip_dirs = {"node_modules", ".git", "__pycache__", "dist", "build", ".venv", "venv", ".next", ".cache", "coverage"}
    
    for root, dirs, filenames in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for fname in filenames:
            if any(fname.endswith(ext) for ext in extensions):
                fpath = os.path.join(root, fname)
                files[fpath] = get_file_hash(fpath)
    return files


def find_related_test(changed_file: str, directory: str) -> Optional[str]:
    """Find test file related to a changed source file."""
    basename = Path(changed_file).stem
    parent = Path(changed_file).parent
    
    # Common test file patterns
    test_patterns = [
        f"test_{basename}.py",
        f"{basename}_test.py",
        f"{basename}.test.ts",
        f"{basename}.test.tsx",
        f"{basename}.test.js",
        f"{basename}.test.jsx",
        f"{basename}.spec.ts",
        f"{basename}.spec.tsx",
        f"{basename}.spec.js",
    ]
    
    # Check in same directory
    for pattern in test_patterns:
        test_path = parent / pattern
        if test_path.exists():
            return str(test_path)
    
    # Check in tests/ or __tests__/ directory
    for test_dir in ["tests", "__tests__", "test", "spec"]:
        for pattern in test_patterns:
            test_path = Path(directory) / test_dir / pattern
            if test_path.exists():
                return str(test_path)
    
    return None


def run_command(cmd: str, label: str, directory: str) -> bool:
    """Run a shell command and return success status."""
    print(f"\n{CYAN}▶ {label}:{RESET} {DIM}{cmd}{RESET}")
    start = time.time()
    
    result = subprocess.run(
        cmd, shell=True, cwd=directory,
        capture_output=False,
        timeout=120
    )
    
    elapsed = time.time() - start
    
    if result.returncode == 0:
        print(f"{GREEN}✓ {label} passed{RESET} {DIM}({elapsed:.1f}s){RESET}")
        return True
    else:
        print(f"{RED}✗ {label} failed{RESET} {DIM}({elapsed:.1f}s){RESET}")
        return False


def print_banner(directory: str, test_cmd: str, extensions: Set[str], lint: bool, build: bool):
    """Print startup banner."""
    print(f"\n{BOLD}{CYAN}🔍 mw watch — Smart File Watcher{RESET}")
    print(f"{'─' * 50}")
    print(f"  {DIM}Directory:{RESET}  {directory}")
    print(f"  {DIM}Test cmd:{RESET}   {test_cmd or '(none detected)'}")
    print(f"  {DIM}Watching:{RESET}   {', '.join(sorted(extensions))}")
    if lint:
        print(f"  {DIM}Lint:{RESET}      enabled")
    if build:
        print(f"  {DIM}Build:{RESET}     enabled")
    print(f"{'─' * 50}")
    print(f"  {DIM}Press Ctrl+C to stop{RESET}\n")


def main(args: List[str] = None) -> int:
    parser = argparse.ArgumentParser(description="Smart file watcher with auto-test")
    parser.add_argument("--test-cmd", help="Override test command")
    parser.add_argument("--dir", default=".", help="Directory to watch")
    parser.add_argument("--lint", action="store_true", help="Also run linter")
    parser.add_argument("--build", action="store_true", help="Also run build")
    parser.add_argument("--debounce", type=int, default=300, help="Debounce delay in ms")
    parser.add_argument("--focused", action="store_true", help="Only run related test file")
    
    opts = parser.parse_args(args or [])
    directory = os.path.abspath(opts.dir)
    
    if not os.path.isdir(directory):
        print(f"{RED}Error: {directory} is not a directory{RESET}")
        return 1
    
    extensions = get_watchable_extensions(directory)
    test_cmd = opts.test_cmd or detect_test_command(directory)
    lint_cmd = detect_lint_command(directory) if opts.lint else ""
    build_cmd = detect_build_command(directory) if opts.build else ""
    
    print_banner(directory, test_cmd, extensions, opts.lint, opts.build)
    
    # Initial scan
    prev_state = scan_files(directory, extensions)
    run_count = 0
    pass_count = 0
    fail_count = 0
    
    debounce_s = opts.debounce / 1000.0
    
    try:
        while True:
            time.sleep(debounce_s)
            current_state = scan_files(directory, extensions)
            
            # Find changes
            changed = []
            for fpath, fhash in current_state.items():
                if fpath not in prev_state or prev_state[fpath] != fhash:
                    changed.append(fpath)
            
            # Check for deleted files
            deleted = set(prev_state.keys()) - set(current_state.keys())
            
            if changed or deleted:
                run_count += 1
                now = datetime.now().strftime("%H:%M:%S")
                
                # Show what changed
                for f in changed:
                    rel = os.path.relpath(f, directory)
                    status = "modified" if f in prev_state else "created"
                    print(f"{YELLOW}● {now}{RESET} {status}: {BOLD}{rel}{RESET}")
                
                for f in deleted:
                    rel = os.path.relpath(f, directory)
                    print(f"{RED}● {now}{RESET} deleted: {BOLD}{rel}{RESET}")
                
                all_passed = True
                
                # Run lint if enabled
                if lint_cmd:
                    if not run_command(lint_cmd, "Lint", directory):
                        all_passed = False
                
                # Run tests
                if test_cmd:
                    if opts.focused and len(changed) == 1:
                        related = find_related_test(changed[0], directory)
                        if related:
                            focused_cmd = f"{test_cmd.split()[0]} {related}"
                            if not run_command(focused_cmd, "Test (focused)", directory):
                                all_passed = False
                        else:
                            if not run_command(test_cmd, "Test", directory):
                                all_passed = False
                    else:
                        if not run_command(test_cmd, "Test", directory):
                            all_passed = False
                
                # Run build if enabled
                if build_cmd:
                    if not run_command(build_cmd, "Build", directory):
                        all_passed = False
                
                if all_passed:
                    pass_count += 1
                    print(f"\n{GREEN}{'━' * 40}")
                    print(f"  ✅ All checks passed (run #{run_count})")
                    print(f"{'━' * 40}{RESET}\n")
                else:
                    fail_count += 1
                    print(f"\n{RED}{'━' * 40}")
                    print(f"  ❌ Some checks failed (run #{run_count})")
                    print(f"{'━' * 40}{RESET}\n")
                
                prev_state = current_state
            else:
                prev_state = current_state
    
    except KeyboardInterrupt:
        print(f"\n\n{CYAN}📊 Session Summary{RESET}")
        print(f"  Runs: {run_count}  |  ✅ {pass_count}  |  ❌ {fail_count}")
        print(f"  {DIM}Goodbye!{RESET}\n")
        return 0


if __name__ == "__main__":
    sys.exit(main())
