#!/usr/bin/env python3
"""
MyWork Command Line Interface (mw)
==================================
Unified interface for all MyWork framework tools.

Usage:
    mw <command> [options]

Commands:
    status          Quick health check of all components
    update          Check and apply updates (GSD, Autocoder, n8n)
    search <query>  Search module registry for reusable code
    new <name>      Create a new project (see: mw new --help)
    scan            Scan all projects and update module registry
    fix             Auto-fix common issues
    report          Generate detailed health report
    doctor          Full system diagnostics

Project Commands:
    mw projects     List all projects
    mw open <name>  Open project in VS Code
    mw cd <name>    Print cd command for project

Autocoder Commands:
    mw ac start <project>    Start Autocoder for project
    mw ac stop               Stop Autocoder
    mw ac status             Check Autocoder status
    mw ac ui                 Open Autocoder UI

n8n Commands:
    mw n8n list              List n8n workflows
    mw n8n status            Check n8n connection

Brain Commands:
    mw brain search <query>  Search knowledge vault
    mw brain add <content>   Quick add a lesson
    mw brain review          Show entries needing attention
    mw brain stats           Brain statistics
    mw brain learn           Discover new learnings automatically
    mw brain learn-deep      Weekly deep analysis

Examples:
    mw status                # Quick overview
    mw search "auth"         # Find authentication modules
    mw new my-app fastapi    # Create FastAPI project
    mw ac start my-app       # Start Autocoder
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Optional

# Configuration
MYWORK_ROOT = Path("/Users/dansidanutz/Desktop/MyWork")
TOOLS_DIR = MYWORK_ROOT / "tools"
PROJECTS_DIR = MYWORK_ROOT / "projects"

# Color codes for terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def color(text: str, color_code: str) -> str:
    """Apply color to text."""
    return f"{color_code}{text}{Colors.ENDC}"


def run_tool(tool_name: str, args: List[str] = None) -> int:
    """Run a MyWork tool with arguments."""
    tool_path = TOOLS_DIR / f"{tool_name}.py"
    if not tool_path.exists():
        print(f"{Colors.RED}Tool not found: {tool_name}{Colors.ENDC}")
        return 1

    cmd = ["python3", str(tool_path)] + (args or [])
    return subprocess.call(cmd)


def cmd_status():
    """Quick status check."""
    print(f"\n{Colors.BOLD}🔍 MyWork Quick Status{Colors.ENDC}")
    print("=" * 50)
    return run_tool("health_check", ["quick"])


def cmd_update(args: List[str]):
    """Check and apply updates."""
    if not args:
        args = ["check"]
    return run_tool("auto_update", args)


def cmd_search(args: List[str]):
    """Search module registry."""
    if not args:
        print("Usage: mw search <query>")
        return 1
    return run_tool("module_registry", ["search"] + args)


def cmd_new(args: List[str]):
    """Create new project."""
    if not args:
        print("Usage: mw new <name> [template]")
        print("\nTemplates: basic, fastapi, nextjs, fullstack, cli, automation")
        return 1
    return run_tool("scaffold", ["new"] + args)


def cmd_scan():
    """Scan projects for modules."""
    print(f"\n{Colors.BOLD}🔍 Scanning projects for modules...{Colors.ENDC}")
    return run_tool("module_registry", ["scan"])


def cmd_fix():
    """Auto-fix issues."""
    return run_tool("health_check", ["fix"])


def cmd_report():
    """Generate health report."""
    return run_tool("health_check", ["report"])


def cmd_doctor():
    """Full system diagnostics."""
    return run_tool("health_check")


def cmd_projects():
    """List all projects."""
    print(f"\n{Colors.BOLD}📁 MyWork Projects{Colors.ENDC}")
    print("=" * 50)

    if not PROJECTS_DIR.exists():
        print(f"{Colors.RED}Projects directory not found{Colors.ENDC}")
        return 1

    projects = [
        p for p in PROJECTS_DIR.iterdir()
        if p.is_dir() and not p.name.startswith((".", "_"))
    ]

    if not projects:
        print("No projects found. Create one with: mw new <name>")
        return 0

    for project in sorted(projects):
        # Check if it has GSD state
        has_gsd = (project / ".planning" / "STATE.md").exists()
        gsd_status = "✅" if has_gsd else "⚪"

        # Check for start script
        has_start = (project / "start.sh").exists() or (project / "start.bat").exists()
        start_status = "🚀" if has_start else ""

        print(f"   {gsd_status} {project.name} {start_status}")

    print(f"\n   Total: {len(projects)} projects")
    return 0


def cmd_open(args: List[str]):
    """Open project in VS Code."""
    if not args:
        print("Usage: mw open <project-name>")
        return 1

    project_name = args[0]
    project_path = PROJECTS_DIR / project_name

    if not project_path.exists():
        print(f"{Colors.RED}Project not found: {project_name}{Colors.ENDC}")
        return 1

    subprocess.call(["code", str(project_path)])
    print(f"✅ Opened {project_name} in VS Code")
    return 0


def cmd_cd(args: List[str]):
    """Print cd command for project."""
    if not args:
        print("Usage: mw cd <project-name>")
        return 1

    project_name = args[0]
    project_path = PROJECTS_DIR / project_name

    if not project_path.exists():
        print(f"{Colors.RED}Project not found: {project_name}{Colors.ENDC}")
        return 1

    print(f"cd {project_path}")
    return 0


def cmd_autocoder(args: List[str]):
    """Autocoder commands."""
    if not args:
        print("Usage: mw ac <start|stop|status|ui> [project]")
        return 1

    subcmd = args[0]

    if subcmd == "start":
        if len(args) < 2:
            print("Usage: mw ac start <project-name>")
            return 1
        return run_tool("autocoder_api", ["start", args[1]])

    elif subcmd == "stop":
        return run_tool("autocoder_api", ["stop"])

    elif subcmd == "status":
        return run_tool("autocoder_api", ["status"])

    elif subcmd == "ui":
        return run_tool("autocoder_api", ["ui"])

    else:
        print(f"Unknown autocoder command: {subcmd}")
        return 1


def cmd_n8n(args: List[str]):
    """n8n commands."""
    if not args:
        print("Usage: mw n8n <list|status>")
        return 1

    subcmd = args[0]

    if subcmd == "list":
        return run_tool("n8n_api", ["--action", "list"])

    elif subcmd == "status":
        # Quick check of n8n connection
        return run_tool("n8n_api", ["--action", "health"])

    else:
        print(f"Unknown n8n command: {subcmd}")
        return 1


def cmd_brain(args: List[str]):
    """Brain knowledge vault commands."""
    if not args:
        print("Usage: mw brain <search|add|review|stats|list>")
        return 1

    subcmd = args[0]
    remaining = args[1:]

    if subcmd == "search":
        if not remaining:
            print("Usage: mw brain search <query>")
            return 1
        return run_tool("brain", ["search"] + remaining)

    elif subcmd == "add":
        if not remaining:
            print("Usage: mw brain add <what you learned>")
            return 1
        return run_tool("brain", ["remember"] + remaining)

    elif subcmd == "review":
        return run_tool("brain", ["review"])

    elif subcmd == "stats":
        return run_tool("brain", ["stats"])

    elif subcmd == "list":
        return run_tool("brain", ["list"] + remaining)

    elif subcmd == "cleanup":
        return run_tool("brain", ["cleanup"])

    elif subcmd == "learn":
        return run_tool("brain_learner", ["daily"])

    elif subcmd == "learn-deep":
        return run_tool("brain_learner", ["weekly"])

    elif subcmd == "discover":
        return run_tool("brain_learner", ["discover"])

    else:
        print(f"Unknown brain command: {subcmd}")
        return 1


def print_help():
    """Print help message."""
    print(__doc__)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print_help()
        sys.exit(0)

    command = sys.argv[1].lower()
    args = sys.argv[2:]

    # Command routing
    commands = {
        "status": lambda: cmd_status(),
        "update": lambda: cmd_update(args),
        "search": lambda: cmd_search(args),
        "new": lambda: cmd_new(args),
        "scan": lambda: cmd_scan(),
        "fix": lambda: cmd_fix(),
        "report": lambda: cmd_report(),
        "doctor": lambda: cmd_doctor(),
        "projects": lambda: cmd_projects(),
        "open": lambda: cmd_open(args),
        "cd": lambda: cmd_cd(args),
        "ac": lambda: cmd_autocoder(args),
        "autocoder": lambda: cmd_autocoder(args),
        "n8n": lambda: cmd_n8n(args),
        "brain": lambda: cmd_brain(args),
        "remember": lambda: cmd_brain(["add"] + args),  # Shortcut
        "help": lambda: print_help() or 0,
        "-h": lambda: print_help() or 0,
        "--help": lambda: print_help() or 0,
    }

    if command in commands:
        sys.exit(commands[command]() or 0)
    else:
        print(f"{Colors.RED}Unknown command: {command}{Colors.ENDC}")
        print("Run 'mw help' for usage information")
        sys.exit(1)


if __name__ == "__main__":
    main()
