#!/usr/bin/env python3
"""
MyWork Demo Runner — Showcase the framework end-to-end.

Usage:
    mw demo              Run full interactive demo
    mw demo --quick      Quick 30-second highlight reel
    mw demo --record     Save demo output to demo_output.md

Creates a throwaway project, runs every major mw command against it,
and produces a polished narrative showing the framework's power.
"""

import os
import sys
import time
import shutil
import subprocess
import tempfile
from pathlib import Path

FRAMEWORK_ROOT = Path(__file__).parent.parent

# ANSI helpers
def c(text, code): return f"\033[{code}m{text}\033[0m"
def bold(t): return c(t, "1")
def green(t): return c(t, "92")
def cyan(t): return c(t, "96")
def yellow(t): return c(t, "93")
def dim(t): return c(t, "2")
def magenta(t): return c(t, "95")

LOGO = r"""
  ╔══════════════════════════════════════════════════╗
  ║          🚀  MyWork-AI  Live Demo  🚀           ║
  ║     From idea → production in minutes            ║
  ╚══════════════════════════════════════════════════╝
"""

def type_effect(text, delay=0.01):
    """Simulate typing for dramatic effect."""
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def step(num, title, desc=""):
    """Print a demo step header."""
    print()
    print(f"  {bold(cyan(f'Step {num}'))} │ {bold(title)}")
    if desc:
        print(f"          │ {dim(desc)}")
    print(f"          │")

def run_cmd(cmd, cwd=None, show=True, capture=False):
    """Run a command, optionally displaying output."""
    if show:
        print(f"          │ {dim('$')} {yellow(cmd)}")
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            cwd=cwd or str(FRAMEWORK_ROOT), timeout=30,
            env={**os.environ, "TERM": "dumb", "NO_COLOR": "1"}
        )
        output = result.stdout.strip()
        if show and output:
            for line in output.split("\n")[:15]:
                print(f"          │   {line}")
            if len(output.split("\n")) > 15:
                print(f"          │   {dim(f'... ({len(output.split(chr(10)))} lines total)')}")
        if capture:
            return output
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        if show:
            print(f"          │   {dim('(timed out)')}")
        return "" if capture else False

def demo_quick():
    """30-second highlight reel."""
    print(LOGO)
    type_effect("  ⚡ Quick Demo — 30 seconds to see everything\n", 0.02)

    step(1, "Health Check", "Is the framework healthy?")
    run_cmd("python3 tools/mw.py status")

    step(2, "Create a Project", "Scaffold a FastAPI app in seconds")
    demo_dir = tempfile.mkdtemp(prefix="mw_demo_")
    project_name = "demo-api"
    run_cmd(f"python3 tools/mw.py new {project_name} fastapi --dir {demo_dir}")

    step(3, "Project Health", "Instant quality score")
    project_path = os.path.join(demo_dir, project_name)
    if os.path.exists(project_path):
        run_cmd(f"python3 tools/mw.py health {project_name}")

    step(4, "Brain Search", "Knowledge vault lookup")
    run_cmd("python3 tools/mw.py brain stats")

    step(5, "Productivity Recap", "What did we build today?")
    run_cmd("python3 tools/mw.py recap --period today")

    # Cleanup
    shutil.rmtree(demo_dir, ignore_errors=True)

    print()
    print(f"  {green('✅ Demo complete!')} Install: {bold('pip install mywork-ai')}")
    print(f"  {dim('   Learn more: mw guide | mw tour')}")
    print()

def demo_full(record=False):
    """Full interactive demo with all features."""
    output_lines = []

    def log(text):
        print(text)
        if record:
            # Strip ANSI for markdown
            import re
            clean = re.sub(r'\033\[[0-9;]*m', '', text)
            output_lines.append(clean)

    log(LOGO)
    type_effect("  Welcome to the MyWork-AI interactive demo!", 0.02)
    type_effect("  We'll build a real project from scratch.\n", 0.02)
    time.sleep(0.5)

    # Step 1: Status
    step(1, "Framework Status", "Let's make sure everything is running")
    run_cmd("python3 tools/mw.py status")

    # Step 2: Doctor
    step(2, "System Diagnostics", "Deep health check")
    run_cmd("python3 tools/mw.py doctor")

    # Step 3: Create project
    step(3, "Scaffold a Project", "Creating a FastAPI backend from template")
    demo_dir = tempfile.mkdtemp(prefix="mw_demo_")
    run_cmd(f"python3 tools/mw.py new demo-showcase fastapi --dir {demo_dir}")

    # Step 4: Scan
    step(4, "Scan Projects", "Discover and index all projects")
    run_cmd("python3 tools/mw.py projects scan")

    # Step 5: Brain
    step(5, "Knowledge Vault", "Search the brain for patterns")
    run_cmd("python3 tools/mw.py brain stats")
    run_cmd("python3 tools/mw.py brain search 'authentication'")

    # Step 6: Analytics
    step(6, "Code Analytics", "Project metrics and trends")
    run_cmd("python3 tools/mw.py analytics summary")

    # Step 7: Linting
    step(7, "Auto-Linting", "Scan for code quality issues")
    run_cmd("python3 tools/mw.py lint stats")

    # Step 8: AI Features
    step(8, "AI-Powered Tools", "Commit messages, reviews, docs — all AI-generated")
    run_cmd("python3 tools/mw.py ai commit --dry-run 2>/dev/null || echo 'AI commit: generates smart commit messages from your diff'")

    # Step 9: Recap
    step(9, "Productivity Recap", "See your output at a glance")
    run_cmd("python3 tools/mw.py recap --period today")

    # Step 10: Ecosystem
    step(10, "Ecosystem Overview", "All your live apps in one view")
    run_cmd("python3 tools/mw.py ecosystem")

    # Cleanup
    shutil.rmtree(demo_dir, ignore_errors=True)

    print()
    print(f"  ╔══════════════════════════════════════════════════╗")
    print(f"  ║  {green('✅ Demo Complete!')}                                ║")
    print(f"  ║                                                  ║")
    print(f"  ║  {bold('Install:')}  pip install mywork-ai                 ║")
    print(f"  ║  {bold('Setup:')}    mw setup                              ║")
    print(f"  ║  {bold('Learn:')}    mw guide | mw tour                    ║")
    print(f"  ║  {bold('Docs:')}     https://mywork.ai/docs                ║")
    print(f"  ╚══════════════════════════════════════════════════╝")
    print()

    if record and output_lines:
        out_path = FRAMEWORK_ROOT / "demo_output.md"
        with open(out_path, "w") as f:
            f.write("# MyWork-AI Demo Output\n\n")
            f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M')}\n\n")
            f.write("```\n")
            f.write("\n".join(output_lines))
            f.write("\n```\n")
        print(f"  {dim(f'Output saved to {out_path}')}")


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    if "--quick" in args or "-q" in args:
        demo_quick()
    elif "--help" in args or "-h" in args:
        print(__doc__)
    else:
        record = "--record" in args or "-r" in args
        demo_full(record=record)


if __name__ == "__main__":
    main()
