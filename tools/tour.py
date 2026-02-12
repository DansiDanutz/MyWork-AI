#!/usr/bin/env python3
"""MyWork-AI Interactive Tour — onboard new users in 2 minutes.

Usage:
    mw tour [--quick] [--no-color]

Walks users through the framework's key features interactively,
running real commands and showing real output along the way.
"""

import os
import re
import subprocess
import sys
import time
from pathlib import Path

FRAMEWORK_ROOT = Path(__file__).parent.parent

# ANSI colors
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
MAGENTA = "\033[35m"
BLUE = "\033[34m"
RED = "\033[31m"
BG_BLUE = "\033[44m"
BG_GREEN = "\033[42m"
BG_MAGENTA = "\033[45m"

NO_COLOR = False


def c(color, text):
    """Apply color if enabled."""
    if NO_COLOR:
        return text
    return f"{color}{text}{RESET}"


def banner():
    """Print the tour banner."""
    print()
    print(c(CYAN + BOLD, "  ╔══════════════════════════════════════════════╗"))
    print(c(CYAN + BOLD, "  ║") + c(YELLOW + BOLD, "   🚀 Welcome to the MyWork-AI Tour!          ") + c(CYAN + BOLD, "║"))
    print(c(CYAN + BOLD, "  ║") + c(DIM, "   2 minutes to see what you can build          ") + c(CYAN + BOLD, "║"))
    print(c(CYAN + BOLD, "  ╚══════════════════════════════════════════════╝"))
    print()


def step(num, total, title, description):
    """Print a tour step header."""
    progress = "█" * num + "░" * (total - num)
    print()
    print(c(DIM, f"  [{progress}] Step {num}/{total}"))
    print(c(BOLD + MAGENTA, f"  ▸ {title}"))
    print(c(DIM, f"    {description}"))
    print()


def run_mw(cmd, show_cmd=True, max_lines=15):
    """Run an mw command and show output."""
    if show_cmd:
        print(c(GREEN, f"    $ mw {cmd}"))
        print()
    try:
        result = subprocess.run(
            [sys.executable, str(FRAMEWORK_ROOT / "tools" / "mw.py"), *cmd.split()],
            capture_output=True, text=True, cwd=str(FRAMEWORK_ROOT), timeout=15,
            env={**os.environ, "FORCE_COLOR": "0"}
        )
        output = result.stdout + result.stderr
        # Strip ANSI
        output = re.sub(r'\x1b\[[0-9;]*m', '', output)
        lines = output.strip().split("\n")
        for line in lines[:max_lines]:
            print(c(DIM, f"    {line}"))
        if len(lines) > max_lines:
            print(c(DIM, f"    ... ({len(lines) - max_lines} more lines)"))
    except subprocess.TimeoutExpired:
        print(c(RED, "    (timed out)"))
    except Exception as e:
        print(c(RED, f"    Error: {e}"))
    print()


def pause(quick=False):
    """Pause between steps."""
    if quick:
        time.sleep(0.3)
        return
    try:
        input(c(DIM, "    Press Enter to continue... "))
    except (KeyboardInterrupt, EOFError):
        print()
        print(c(YELLOW, "\n  👋 Tour ended early. Run `mw tour` anytime to resume!"))
        sys.exit(0)


def tour_status(quick):
    """Step 1: Health check."""
    step(1, 6, "Health Check", "See your framework status at a glance")
    run_mw("status")
    pause(quick)


def tour_projects(quick):
    """Step 2: Projects."""
    step(2, 6, "Your Projects", "MyWork tracks all your projects automatically")
    run_mw("projects")
    pause(quick)


def tour_brain(quick):
    """Step 3: Brain knowledge vault."""
    step(3, 6, "Brain — Your Knowledge Vault",
         "Store and search knowledge. It grows as you work.")
    run_mw("brain stats")
    print(c(CYAN, "    💡 Try: mw brain add \"React hooks best practices\" --tag react"))
    print(c(CYAN, "           mw brain search \"react hooks\""))
    print()
    pause(quick)


def tour_scaffold(quick):
    """Step 4: Project scaffolding."""
    step(4, 6, "Create Projects Instantly",
         "Scaffold production-ready apps with one command")
    templates = [
        ("mw new myapp api", "REST API (FastAPI + Docker + tests)"),
        ("mw new myapp webapp", "Next.js web app (React + Tailwind)"),
        ("mw new myapp cli", "CLI tool (Click + config + packaging)"),
        ("mw new myapp lib", "Python library (PyPI-ready)"),
        ("mw new myapp fullstack", "Full-stack (API + frontend + DB)"),
        ("mw new myapp ml", "ML pipeline (training + inference)"),
    ]
    for cmd, desc in templates:
        print(c(GREEN, f"    $ {cmd}") + c(DIM, f"  — {desc}"))
    print()
    pause(quick)


def tour_dev(quick):
    """Step 5: Development tools."""
    step(5, 6, "Development Superpowers",
         "Test, lint, deploy, monitor — all from one CLI")
    tools = [
        ("mw test", "Universal test runner (auto-detects framework)"),
        ("mw lint", "Code quality scanning"),
        ("mw check", "Quality gate (tests + lint + types + security)"),
        ("mw deploy", "Deploy to Vercel/Railway/Render/Docker"),
        ("mw ci", "Generate CI/CD pipelines"),
        ("mw env", "Manage environment variables (masked)"),
        ("mw monitor", "Track deployments and health"),
        ("mw security scan", "Vulnerability + secret scanning"),
        ("mw plugin install <url>", "Extend with community plugins"),
    ]
    for cmd, desc in tools:
        print(c(GREEN, f"    {cmd:<30}") + c(DIM, f" {desc}"))
    print()
    pause(quick)


def tour_next(quick):
    """Step 6: What's next."""
    step(6, 6, "You're Ready! 🎉", "Here's how to keep going")
    print(c(BOLD, "    Quick start:"))
    print(c(CYAN, "      mw new my-project api    ") + c(DIM, "Create your first project"))
    print(c(CYAN, "      mw doctor                ") + c(DIM, "Full system diagnostics"))
    print(c(CYAN, "      mw serve                 ") + c(DIM, "Open web dashboard"))
    print(c(CYAN, "      mw guide                 ") + c(DIM, "Interactive workflow guide"))
    print()
    print(c(BOLD, "    Resources:"))
    print(c(DIM, "      📖 Docs:    ") + c(BLUE, "https://github.com/DansiDanutz/MyWork-AI"))
    print(c(DIM, "      🐛 Issues:  ") + c(BLUE, "https://github.com/DansiDanutz/MyWork-AI/issues"))
    print(c(DIM, "      💬 Discord: ") + c(BLUE, "Coming soon"))
    print()
    print(c(GREEN + BOLD, "    ✅ Tour complete! Happy building! 🔧"))
    print()


def cmd_tour(args=None):
    """Run the interactive tour."""
    global NO_COLOR
    quick = False
    if args:
        if "--quick" in args:
            quick = True
        if "--no-color" in args:
            NO_COLOR = True

    banner()
    tour_status(quick)
    tour_projects(quick)
    tour_brain(quick)
    tour_scaffold(quick)
    tour_dev(quick)
    tour_next(quick)
    return 0


if __name__ == "__main__":
    sys.exit(cmd_tour(sys.argv[1:]))
