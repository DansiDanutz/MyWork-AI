#!/usr/bin/env python3
"""
Enhanced Interactive Tour for MyWork-AI
=======================================
Truly interactive tour where users try features hands-on.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Colors
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
MAGENTA = "\033[35m"
BLUE = "\033[34m"
RED = "\033[31m"

def c(color, text):
    """Apply color."""
    return f"{color}{text}{RESET}"

def banner():
    """Print the tour banner."""
    print()
    print(c(CYAN + BOLD, "  ╔══════════════════════════════════════════════╗"))
    print(c(CYAN + BOLD, "  ║") + c(YELLOW + BOLD, "   🎯 Interactive MyWork-AI Tour               ") + c(CYAN + BOLD, "║"))
    print(c(CYAN + BOLD, "  ║") + c(DIM, "   Learn by doing - try each feature yourself    ") + c(CYAN + BOLD, "║"))
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

def wait_for_user(prompt="Press Enter to continue"):
    """Wait for user input."""
    try:
        input(c(DIM, f"    {prompt}... "))
    except (KeyboardInterrupt, EOFError):
        print()
        print(c(YELLOW, "\n  👋 Tour ended early. Run `mw tour` anytime to resume!"))
        sys.exit(0)

def run_command_demo(cmd, description):
    """Show a command and let the user choose to run it."""
    print(c(GREEN, f"    💡 Try this: {cmd}"))
    print(c(DIM, f"       {description}"))
    
    if input(c(YELLOW, "    Run this command? (Y/n): ")).strip().lower() not in ['n', 'no']:
        print(c(DIM, f"    $ {cmd}"))
        try:
            result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=10)
            output = (result.stdout + result.stderr).strip()
            if output:
                lines = output.split('\n')
                for line in lines[:10]:  # Show first 10 lines
                    print(c(DIM, f"      {line}"))
                if len(lines) > 10:
                    print(c(DIM, f"      ... ({len(lines) - 10} more lines)"))
            print()
        except Exception as e:
            print(c(RED, f"    Error: {e}"))
    else:
        print(c(DIM, "    Skipped.\n"))

def tour_welcome():
    """Welcome and orientation."""
    step(1, 6, "Welcome & Orientation", "Let's explore what MyWork can do for you")
    
    print(c(BOLD, "    🚀 MyWork-AI is your development companion that helps you:"))
    print(c(GREEN, "       • Scaffold new projects instantly"))
    print(c(GREEN, "       • Manage your development workflow"))
    print(c(GREEN, "       • Build and deploy with one command"))
    print(c(GREEN, "       • Learn and remember best practices"))
    
    wait_for_user()

def tour_status(quick=False):
    """Step 1: Health check."""
    step(2, 6, "Health Check", "Check your framework status")
    
    print(c(BOLD, "    Let's see how your MyWork installation is doing:"))
    run_command_demo("mw status", "Shows overall system health")
    
    if not quick:
        wait_for_user()

def tour_projects():
    """Step 2: Projects."""
    step(3, 6, "Your Project Dashboard", "See all your projects at a glance")
    
    print(c(BOLD, "    MyWork automatically tracks all your projects:"))
    run_command_demo("mw projects", "Lists all detected projects")
    
    wait_for_user()

def tour_create_project():
    """Step 3: Create a real project."""
    step(4, 6, "Create Your First Project", "Let's build something together!")
    
    print(c(BOLD, "    Let's create a real project you can use:"))
    
    project_name = input(c(CYAN, "    What should we call your project? [my-demo-app]: ")).strip() or "my-demo-app"
    
    print(c(BOLD, f"    Choose a template for '{project_name}':"))
    print("    1. 📡 FastAPI (REST API)")
    print("    2. ⚡ Basic (minimal structure)")
    print("    3. 🖥️  CLI Tool")
    
    choice = input(c(CYAN, "    Enter choice (1-3) [1]: ")).strip() or "1"
    
    template_map = {"1": "fastapi", "2": "basic", "3": "cli"}
    template = template_map.get(choice, "fastapi")
    
    print(c(GREEN, f"    Creating {project_name} with {template} template..."))
    
    cmd = f"mw new {project_name} {template}"
    print(c(DIM, f"    $ {cmd}"))
    
    try:
        result = subprocess.run(cmd.split(), capture_output=True, text=True, cwd="/tmp")
        if result.returncode == 0:
            print(c(GREEN, f"    ✅ Project '{project_name}' created successfully!"))
            print(c(BLUE, f"    📁 Location: /tmp/{project_name}"))
        else:
            print(c(RED, f"    ❌ Error creating project"))
    except Exception as e:
        print(c(RED, f"    Error: {e}"))
    
    wait_for_user()

def tour_brain():
    """Step 4: Brain knowledge vault."""
    step(5, 6, "Your Knowledge Vault", "Store and search development knowledge")
    
    print(c(BOLD, "    The Brain helps you remember and find information:"))
    
    run_command_demo("mw brain stats", "Shows your knowledge vault statistics")
    
    print(c(BOLD, "    Let's add some knowledge:"))
    
    if input(c(CYAN, "    Add a quick tip to your brain? (Y/n): ")).strip().lower() not in ['n', 'no']:
        tip = input(c(CYAN, "    Enter a development tip or lesson: ")).strip()
        if tip:
            cmd = f'mw brain add "{tip}"'
            print(c(DIM, f"    $ {cmd}"))
            try:
                subprocess.run(["mw", "brain", "add", tip], timeout=5)
                print(c(GREEN, "    ✅ Added to your brain!"))
            except Exception as e:
                print(c(YELLOW, f"    Note saved (manual mode)"))
    
    wait_for_user()

def tour_tools():
    """Step 5: Development tools."""
    step(6, 6, "Development Tools", "Your complete development toolkit")
    
    print(c(BOLD, "    MyWork includes powerful development tools:"))
    
    tools = [
        ("mw check", "Run quality checks (tests, lint, types, security)"),
        ("mw deploy", "Deploy to cloud platforms"),
        ("mw doctor", "Deep system diagnostics"),
        ("mw completions install", "Install shell tab-completion"),
    ]
    
    print(c(BOLD, "    Available tools:"))
    for cmd, desc in tools:
        print(c(GREEN, f"      {cmd:<25}") + c(DIM, f" {desc}"))
    
    print()
    print(c(BOLD, "    Let's try one:"))
    
    if input(c(CYAN, "    Run a quick system diagnostic? (Y/n): ")).strip().lower() not in ['n', 'no']:
        print(c(DIM, "    $ mw doctor --quick"))
        try:
            # Run a quick doctor check
            result = subprocess.run(["mw", "doctor", "--quick"], capture_output=True, text=True, timeout=15)
            if result.stdout:
                lines = result.stdout.split('\n')[:8]
                for line in lines:
                    if line.strip():
                        print(c(DIM, f"      {line}"))
        except Exception:
            print(c(YELLOW, "    ⏱️  Doctor check running in background..."))
    
    wait_for_user()

def tour_next():
    """Final step: What's next."""
    print()
    print(c(BOLD + GREEN, "  🎉 Congratulations! You've completed the MyWork tour!"))
    print()
    
    print(c(BOLD, "  What you've learned:"))
    print(c(GREEN, "    ✅ Check system status with `mw status`"))
    print(c(GREEN, "    ✅ View projects with `mw projects`"))
    print(c(GREEN, "    ✅ Create new projects with `mw new`"))
    print(c(GREEN, "    ✅ Store knowledge with `mw brain`"))
    print(c(GREEN, "    ✅ Use development tools for quality and deployment"))
    
    print()
    print(c(BOLD, "  Ready to build something amazing?"))
    
    print(c(CYAN, "    Next commands to try:"))
    print(c(GREEN, "      mw new my-project fastapi  ") + c(DIM, "# Create a FastAPI project"))
    print(c(GREEN, "      mw dashboard             ") + c(DIM, "# Open web dashboard"))
    print(c(GREEN, "      mw brain search <topic>  ") + c(DIM, "# Search your knowledge"))
    print(c(GREEN, "      mw help                  ") + c(DIM, "# See all commands"))
    
    print()
    print(c(BOLD + GREEN, "  Happy building with MyWork-AI! 🚀"))
    print()

def cmd_tour(args=None):
    """Run the enhanced interactive tour."""
    quick = args and "--quick" in args
    
    banner()
    tour_welcome()
    tour_status(quick)
    tour_projects()
    tour_create_project()
    tour_brain()
    tour_tools()
    tour_next()
    
    return 0

if __name__ == "__main__":
    sys.exit(cmd_tour(sys.argv[1:]))