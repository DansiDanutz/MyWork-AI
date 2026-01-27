#!/usr/bin/env python3
"""
Automated Markdownlint Scheduler
Runs markdownlint fixes every 15 minutes and commits changes automatically.

Usage:
    python3 tools/auto_lint_scheduler.py          # Run once
    python3 tools/auto_lint_scheduler.py --daemon # Run continuously every 15 minutes
"""

import os
import sys
import time
import subprocess
import argparse
from datetime import datetime
from pathlib import Path


def run_command(command: list, cwd: str = ".") -> tuple[bool, str]:
    """Run a command and return success status and output."""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)


def check_git_status() -> tuple[bool, int]:
    """Check if there are uncommitted markdown changes."""
    success, output = run_command(["git", "status", "--porcelain"])
    if not success:
        return False, 0

    # Count markdown files with changes
    md_changes = sum(1 for line in output.split('\n') if line.strip().endswith('.md'))
    return True, md_changes


def run_lint_fixer() -> tuple[bool, dict]:
    """Run the auto lint fixer and return results."""
    script_path = Path(__file__).parent / "auto_lint_fixer.py"

    success, output = run_command(["python3", str(script_path)])

    if not success:
        return False, {"error": output}

    # Parse output for summary
    results = {"files_processed": 0, "files_fixed": 0, "total_fixes": {}}

    for line in output.split('\n'):
        if "Files processed:" in line:
            results["files_processed"] = int(line.split(":")[-1].strip())
        elif "Files fixed:" in line:
            results["files_fixed"] = int(line.split(":")[-1].strip())
        elif "• MD" in line and "(" in line:
            # Parse fix counts like "• MD022 (Headings without blank lines): 123"
            parts = line.split(":")
            if len(parts) >= 2:
                rule = parts[0].split("•")[-1].split("(")[0].strip()
                count = int(parts[-1].strip())
                results["total_fixes"][rule] = count

    return True, results


def commit_changes(results: dict) -> bool:
    """Commit the linting fixes to git."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Create detailed commit message
    total_fixes = sum(results["total_fixes"].values())

    commit_msg = f"fix(auto-lint): resolve {total_fixes} markdownlint violations [{timestamp}]\n\n"

    if results["total_fixes"]:
        commit_msg += "Automatic fixes applied:\n"
        for rule, count in results["total_fixes"].items():
            rule_descriptions = {
                'MD022': 'headings without blank lines',
                'MD032': 'lists without blank lines',
                'MD031': 'code blocks without blank lines',
                'MD047': 'missing trailing newlines',
                'MD058': 'tables without blank lines'
            }
            description = rule_descriptions.get(rule, 'various violations')
            commit_msg += f"- {rule}: {count} ({description})\n"

    commit_msg += f"\nFiles: {results['files_fixed']}/{results['files_processed']} modified\nScheduled run: every 15 minutes"

    # Stage markdown files only
    success1, _ = run_command(["git", "add", "*.md", "**/*.md"])

    # Commit with message
    success2, output = run_command(["git", "commit", "-m", commit_msg])

    if success2:
        print(f"✅ Committed {total_fixes} fixes")
        return True
    else:
        if "nothing to commit" in output:
            print("ℹ️  No changes to commit")
            return True
        else:
            print(f"❌ Commit failed: {output}")
            return False


def run_single_cycle() -> bool:
    """Run a single lint-fix-commit cycle."""
    print(f"🔍 [{datetime.now().strftime('%H:%M:%S')}] Checking for markdown lint issues...")

    # Check if there are any changes first
    git_ok, changes = check_git_status()
    if not git_ok:
        print("❌ Error checking git status")
        return False

    # Run lint fixer
    success, results = run_lint_fixer()
    if not success:
        print(f"❌ Lint fixer failed: {results.get('error', 'Unknown error')}")
        return False

    # Check results
    total_fixes = sum(results.get("total_fixes", {}).values())
    files_fixed = results.get("files_fixed", 0)

    if total_fixes == 0:
        print("✨ No markdownlint violations found")
        return True

    print(f"🔧 Fixed {total_fixes} violations in {files_fixed} files")

    # Show summary
    for rule, count in results.get("total_fixes", {}).items():
        print(f"   • {rule}: {count}")

    # Commit changes
    return commit_changes(results)


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Automated markdownlint fixer")
    parser.add_argument(
        '--daemon',
        action='store_true',
        help='Run continuously every 15 minutes'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=900,  # 15 minutes in seconds
        help='Interval between runs in seconds (default: 900)'
    )

    args = parser.parse_args()

    if not args.daemon:
        # Single run
        success = run_single_cycle()
        sys.exit(0 if success else 1)

    # Daemon mode
    print(f"🤖 Starting automated lint fixer (every {args.interval//60} minutes)")
    print("   Press Ctrl+C to stop")

    try:
        while True:
            run_single_cycle()
            print(f"⏰ Sleeping for {args.interval//60} minutes...")
            time.sleep(args.interval)

    except KeyboardInterrupt:
        print("\n👋 Stopping automated lint fixer")
    except Exception as e:
        print(f"\n❌ Error in daemon mode: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()