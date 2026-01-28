#!/usr/bin/env python3
"""
Auto-Linting Agent - Continuously monitors and fixes linting issues
Part of the MyWork Framework

Features:
- Watches files for changes
- Runs appropriate linters
- Auto-fixes common issues
- Supports multiple linting tools
- Integrates with Git workflows
"""

import os
import sys
import time
import json
import subprocess
import threading
import fnmatch
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

@dataclass
class LintResult:
    """Result of a linting operation"""
    file_path: str
    tool: str
    issues_found: int
    issues_fixed: int
    success: bool
    messages: List[str]
    timestamp: str

@dataclass
class LintConfig:
    """Configuration for linting tools"""
    markdownlint: bool = True
    pylint: bool = True
    eslint: bool = True
    prettier: bool = True
    black: bool = True
    flake8: bool = True
    auto_fix: bool = True
    ignore_patterns: List[str] = None

    def __post_init__(self):
        if self.ignore_patterns is None:
            self.ignore_patterns = [
                "node_modules/**",
                ".git/**",
                "venv/**",
                ".venv/**",
                "__pycache__/**",
                "*.pyc",
                ".tmp/**",
                "dist/**",
                "build/**"
            ]

class AutoLintingAgent:
    """Main auto-linting agent class"""

    def __init__(self, root_dir: str = None, config: LintConfig = None):
        self.root_dir = Path(root_dir or os.getcwd()).resolve()
        self.config = config or LintConfig()
        self.results: List[LintResult] = []
        self.observer = None
        self.running = False
        self.stats = {
            'files_processed': 0,
            'total_issues_found': 0,
            'total_issues_fixed': 0,
            'last_run': None
        }

        # Load existing auto_lint_fixer
        self.framework_tools = self.root_dir / "tools"
        if (self.framework_tools / "auto_lint_fixer.py").exists():
            sys.path.insert(0, str(self.framework_tools))
            try:
                from auto_lint_fixer import AutoLintFixer
                self.markdown_fixer = AutoLintFixer(str(self.root_dir))
                print(f"✅ Loaded existing AutoLintFixer")
            except Exception as e:
                print(f"⚠️  Could not load AutoLintFixer: {e}")
                self.markdown_fixer = None
        else:
            self.markdown_fixer = None

    def should_ignore_file(self, file_path: str) -> bool:
        """Check if file should be ignored based on patterns"""
        try:
            # Try to get relative path
            rel_path = str(Path(file_path).relative_to(self.root_dir))
        except ValueError:
            # File is not in the project directory - use the full path
            rel_path = str(Path(file_path))

        # Normalize path separators for consistent matching
        rel_path = rel_path.replace('\\', '/')

        for pattern in self.config.ignore_patterns:
            # Convert glob pattern to handle both file and directory matching
            if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(Path(file_path).name, pattern):
                return True

            # Special handling for directory patterns like "node_modules/**"
            if pattern.endswith('/**'):
                dir_pattern = pattern[:-3]  # Remove "/**"
                if dir_pattern in rel_path.split('/'):
                    return True

        return False

    def get_linting_tools_for_file(self, file_path: str) -> List[str]:
        """Determine which linting tools to use for a file"""
        tools = []
        ext = Path(file_path).suffix.lower()

        if ext == '.md' and self.config.markdownlint:
            tools.append('markdownlint')
        elif ext == '.py':
            if self.config.black:
                tools.append('black')
            if self.config.flake8:
                tools.append('flake8')
            if self.config.pylint:
                tools.append('pylint')
        elif ext in ['.js', '.ts', '.jsx', '.tsx']:
            if self.config.eslint:
                tools.append('eslint')
            if self.config.prettier:
                tools.append('prettier')
        elif ext in ['.json', '.yaml', '.yml']:
            if self.config.prettier:
                tools.append('prettier')

        return tools

    def run_markdownlint(self, file_path: str) -> LintResult:
        """Run markdownlint and fix issues"""
        if self.markdown_fixer:
            try:
                # Use the existing AutoLintFixer
                issues_fixed = self.markdown_fixer.fix_file(file_path)
                return LintResult(
                    file_path=file_path,
                    tool='markdownlint',
                    issues_found=issues_fixed,
                    issues_fixed=issues_fixed,
                    success=True,
                    messages=[f"Fixed {issues_fixed} markdown issues"],
                    timestamp=datetime.now().isoformat()
                )
            except Exception as e:
                return LintResult(
                    file_path=file_path,
                    tool='markdownlint',
                    issues_found=0,
                    issues_fixed=0,
                    success=False,
                    messages=[f"Error: {e}"],
                    timestamp=datetime.now().isoformat()
                )

        # Fallback to command-line markdownlint
        try:
            cmd = ['markdownlint', '--fix', file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            issues_fixed = result.stdout.count('fixed') if result.stdout else 0

            return LintResult(
                file_path=file_path,
                tool='markdownlint',
                issues_found=issues_fixed,
                issues_fixed=issues_fixed,
                success=result.returncode == 0,
                messages=[result.stdout, result.stderr] if result.stderr else [result.stdout],
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            return LintResult(
                file_path=file_path,
                tool='markdownlint',
                issues_found=0,
                issues_fixed=0,
                success=False,
                messages=[f"Error: {e}"],
                timestamp=datetime.now().isoformat()
            )

    def run_black(self, file_path: str) -> LintResult:
        """Run Black Python formatter"""
        try:
            cmd = ['black', '--quiet', file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            return LintResult(
                file_path=file_path,
                tool='black',
                issues_found=1 if result.returncode != 0 else 0,
                issues_fixed=1 if result.returncode == 0 else 0,
                success=True,  # Black always succeeds if it can format
                messages=['Formatted with Black'] if result.returncode == 0 else ['No changes needed'],
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            return LintResult(
                file_path=file_path,
                tool='black',
                issues_found=0,
                issues_fixed=0,
                success=False,
                messages=[f"Error: {e}"],
                timestamp=datetime.now().isoformat()
            )

    def run_prettier(self, file_path: str) -> LintResult:
        """Run Prettier formatter"""
        try:
            cmd = ['npx', 'prettier', '--write', file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            return LintResult(
                file_path=file_path,
                tool='prettier',
                issues_found=1 if 'unchanged' not in result.stderr else 0,
                issues_fixed=1 if 'unchanged' not in result.stderr else 0,
                success=result.returncode == 0,
                messages=[result.stdout or 'Formatted with Prettier'],
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            return LintResult(
                file_path=file_path,
                tool='prettier',
                issues_found=0,
                issues_fixed=0,
                success=False,
                messages=[f"Error: {e}"],
                timestamp=datetime.now().isoformat()
            )

    def run_eslint(self, file_path: str) -> LintResult:
        """Run ESLint with auto-fix"""
        try:
            cmd = ['npx', 'eslint', '--fix', file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            # ESLint outputs errors to stderr and fixes to stdout
            issues_found = result.stderr.count('error') + result.stderr.count('warning')
            issues_fixed = result.stdout.count('fixed') if result.stdout else 0

            return LintResult(
                file_path=file_path,
                tool='eslint',
                issues_found=issues_found,
                issues_fixed=issues_fixed,
                success=result.returncode == 0,
                messages=[result.stdout, result.stderr] if result.stderr else [result.stdout or 'No issues found'],
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            return LintResult(
                file_path=file_path,
                tool='eslint',
                issues_found=0,
                issues_fixed=0,
                success=False,
                messages=[f"Error: {e}"],
                timestamp=datetime.now().isoformat()
            )

    def run_flake8(self, file_path: str) -> LintResult:
        """Run Flake8 (checking only, no auto-fix)"""
        try:
            cmd = ['flake8', file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            issues_found = len([line for line in result.stdout.split('\n') if line.strip()])

            return LintResult(
                file_path=file_path,
                tool='flake8',
                issues_found=issues_found,
                issues_fixed=0,  # Flake8 doesn't auto-fix
                success=result.returncode == 0,
                messages=[result.stdout] if result.stdout else ['No issues found'],
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            return LintResult(
                file_path=file_path,
                tool='flake8',
                issues_found=0,
                issues_fixed=0,
                success=False,
                messages=[f"Error: {e}"],
                timestamp=datetime.now().isoformat()
            )

    def lint_file(self, file_path: str) -> List[LintResult]:
        """Lint a single file with appropriate tools"""
        if self.should_ignore_file(file_path):
            return []

        if not os.path.exists(file_path):
            return []

        tools = self.get_linting_tools_for_file(file_path)
        results = []

        for tool in tools:
            if tool == 'markdownlint':
                result = self.run_markdownlint(file_path)
            elif tool == 'black':
                result = self.run_black(file_path)
            elif tool == 'prettier':
                result = self.run_prettier(file_path)
            elif tool == 'eslint':
                result = self.run_eslint(file_path)
            elif tool == 'flake8':
                result = self.run_flake8(file_path)
            else:
                continue

            results.append(result)

            # Update stats
            self.stats['total_issues_found'] += result.issues_found
            self.stats['total_issues_fixed'] += result.issues_fixed

        if results:
            self.stats['files_processed'] += 1
            self.stats['last_run'] = datetime.now().isoformat()

        return results

    def lint_directory(self, directory: str = None) -> List[LintResult]:
        """Lint all files in a directory"""
        directory = directory or self.root_dir
        all_results = []

        print(f"🔍 Scanning directory: {directory}")

        for root, dirs, files in os.walk(directory):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if not self.should_ignore_file(os.path.join(root, d))]

            for file in files:
                file_path = os.path.join(root, file)

                if self.should_ignore_file(file_path):
                    continue

                results = self.lint_file(file_path)
                all_results.extend(results)

                if results:
                    issues_found = sum(r.issues_found for r in results)
                    issues_fixed = sum(r.issues_fixed for r in results)

                    if issues_fixed > 0:
                        print(f"🔧 {file}: Fixed {issues_fixed}/{issues_found} issues")

        return all_results

    def save_results(self, results: List[LintResult]):
        """Save linting results to JSON file"""
        results_file = self.root_dir / ".planning" / "linting_results.json"
        results_file.parent.mkdir(exist_ok=True)

        # Convert results to dictionaries
        results_data = [asdict(r) for r in results]

        # Load existing results if any
        existing_results = []
        if results_file.exists():
            try:
                with open(results_file, 'r') as f:
                    existing_results = json.load(f)
            except:
                existing_results = []

        # Add new results
        all_results = existing_results + results_data

        # Keep only last 1000 results
        if len(all_results) > 1000:
            all_results = all_results[-1000:]

        with open(results_file, 'w') as f:
            json.dump(all_results, f, indent=2)

    def print_summary(self, results: List[LintResult]):
        """Print summary of linting results"""
        if not results:
            print("✅ No linting issues found!")
            return

        total_found = sum(r.issues_found for r in results)
        total_fixed = sum(r.issues_fixed for r in results)

        tools_used = set(r.tool for r in results)
        files_processed = len(set(r.file_path for r in results))

        print(f"\n📊 Linting Summary:")
        print(f"   Files processed: {files_processed}")
        print(f"   Tools used: {', '.join(tools_used)}")
        print(f"   Issues found: {total_found}")
        print(f"   Issues fixed: {total_fixed}")
        print(f"   Success rate: {(total_fixed/total_found*100) if total_found > 0 else 100:.1f}%")

class LintingEventHandler(FileSystemEventHandler):
    """File system event handler for watching file changes"""

    def __init__(self, agent: AutoLintingAgent):
        super().__init__()
        self.agent = agent
        self.last_modified = {}

    def on_modified(self, event):
        if event.is_directory:
            return

        file_path = event.src_path

        # Debounce rapid file changes
        now = time.time()
        if file_path in self.last_modified:
            if now - self.last_modified[file_path] < 2.0:  # 2 second debounce
                return
        self.last_modified[file_path] = now

        # Check if we should lint this file
        if not self.agent.should_ignore_file(file_path):
            tools = self.agent.get_linting_tools_for_file(file_path)
            if tools:
                print(f"🔄 File changed: {file_path}")
                results = self.agent.lint_file(file_path)
                if results:
                    self.agent.save_results(results)
                    issues_fixed = sum(r.issues_fixed for r in results)
                    if issues_fixed > 0:
                        print(f"✅ Auto-fixed {issues_fixed} issues")

def main():
    """Main CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Auto-Linting Agent for MyWork Framework')
    parser.add_argument('--watch', action='store_true', help='Watch files for changes')
    parser.add_argument('--scan', action='store_true', help='Scan all files once')
    parser.add_argument('--file', help='Lint specific file')
    parser.add_argument('--dir', help='Lint specific directory')
    parser.add_argument('--config', help='Path to config file')
    parser.add_argument('--stats', action='store_true', help='Show stats')

    args = parser.parse_args()

    # Load config
    config = LintConfig()
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config_data = json.load(f)
            config = LintConfig(**config_data)

    # Create agent
    agent = AutoLintingAgent(config=config)

    if args.stats:
        print(f"📊 Auto-Linting Agent Stats:")
        print(f"   Root directory: {agent.root_dir}")
        print(f"   Files processed: {agent.stats['files_processed']}")
        print(f"   Total issues found: {agent.stats['total_issues_found']}")
        print(f"   Total issues fixed: {agent.stats['total_issues_fixed']}")
        print(f"   Last run: {agent.stats['last_run'] or 'Never'}")
        return

    if args.file:
        # Lint specific file
        results = agent.lint_file(args.file)
        agent.print_summary(results)
        agent.save_results(results)

    elif args.dir:
        # Lint specific directory
        results = agent.lint_directory(args.dir)
        agent.print_summary(results)
        agent.save_results(results)

    elif args.scan:
        # Scan all files once
        print("🔍 Scanning all files for linting issues...")
        results = agent.lint_directory()
        agent.print_summary(results)
        agent.save_results(results)

    elif args.watch:
        # Watch mode
        print("👁️  Starting Auto-Linting Agent in watch mode...")
        print(f"   Root: {agent.root_dir}")
        print("   Press Ctrl+C to stop")

        event_handler = LintingEventHandler(agent)
        observer = Observer()
        observer.schedule(event_handler, str(agent.root_dir), recursive=True)
        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n⚠️  Stopping Auto-Linting Agent...")
            observer.stop()
        observer.join()

    else:
        # Default: scan once
        print("🚀 Auto-Linting Agent - Running default scan")
        results = agent.lint_directory()
        agent.print_summary(results)
        agent.save_results(results)

if __name__ == "__main__":
    main()