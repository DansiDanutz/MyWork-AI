#!/usr/bin/env python3
"""
MyWork-AI TUI Dashboard — Rich terminal UI for project management.
Uses 'rich' library for a beautiful, interactive terminal dashboard.
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.columns import Columns
    from rich.text import Text
    from rich.live import Live
    from rich.prompt import Prompt, Confirm
    from rich import box
except ImportError:
    print("Install rich: pip install rich")
    sys.exit(1)

console = Console()
FRAMEWORK_ROOT = os.environ.get("MYWORK_ROOT", str(Path.home() / "MyWork-AI"))


def get_projects():
    """Scan for projects."""
    projects = []
    proj_dir = Path(FRAMEWORK_ROOT) / "projects"
    if proj_dir.exists():
        for p in proj_dir.iterdir():
            if p.is_dir() and not p.name.startswith("."):
                projects.append({"name": p.name, "path": str(p), "type": "project"})
    # Also check current directory
    cwd = Path.cwd()
    if (cwd / "main.py").exists() or (cwd / "package.json").exists():
        projects.insert(0, {"name": f"{cwd.name} (current)", "path": str(cwd), "type": "current"})
    return projects


def get_git_info(path="."):
    """Get git status for a path."""
    try:
        branch = subprocess.run(["git", "branch", "--show-current"],
                              capture_output=True, text=True, cwd=path, timeout=5).stdout.strip()
        status = subprocess.run(["git", "status", "--porcelain"],
                              capture_output=True, text=True, cwd=path, timeout=5).stdout
        commits = subprocess.run(["git", "rev-list", "--count", "HEAD"],
                               capture_output=True, text=True, cwd=path, timeout=5).stdout.strip()
        last = subprocess.run(["git", "log", "-1", "--format=%cr"],
                            capture_output=True, text=True, cwd=path, timeout=5).stdout.strip()
        changed = len([l for l in status.strip().split("\n") if l])
        return {"branch": branch, "changed": changed, "commits": int(commits or 0), "last": last}
    except Exception:
        return {"branch": "?", "changed": 0, "commits": 0, "last": "?"}


def get_framework_stats():
    """Get MyWork-AI framework statistics."""
    stats = {"version": "?", "commands": 0, "tests": 0, "projects": 0}
    try:
        toml = Path(FRAMEWORK_ROOT) / "pyproject.toml"
        if toml.exists():
            for line in toml.read_text().splitlines():
                if line.strip().startswith("version"):
                    stats["version"] = line.split("=")[1].strip().strip('"')
                    break
    except Exception:
        pass

    # Count commands from dispatch
    try:
        mw_path = Path(FRAMEWORK_ROOT) / "tools" / "mw.py"
        if mw_path.exists():
            content = mw_path.read_text()
            # Count unique command entries in dispatch
            import re
            cmds = set(re.findall(r'"(\w[\w-]*)"\s*:\s*lambda', content))
            stats["commands"] = len(cmds)
    except Exception:
        pass

    # Count projects
    proj_dir = Path(FRAMEWORK_ROOT) / "projects"
    if proj_dir.exists():
        stats["projects"] = len([d for d in proj_dir.iterdir() if d.is_dir()])

    return stats


def get_marketplace_stats():
    """Get marketplace product stats."""
    try:
        r = subprocess.run(
            ["curl", "-s", "https://mywork-ai-production.up.railway.app/api/products",
             "-H", "Accept: application/json"],
            capture_output=True, text=True, timeout=10
        )
        products = json.loads(r.stdout)
        if isinstance(products, list):
            active = [p for p in products if p.get("status") == "active"]
            total_value = sum(float(p.get("price", 0)) for p in active)
            return {"products": len(active), "total_value": f"${total_value:.2f}"}
    except Exception:
        pass
    return {"products": "?", "total_value": "?"}


def build_header():
    """Build the dashboard header."""
    stats = get_framework_stats()
    header_text = Text()
    header_text.append("  ⚡ MyWork-AI Dashboard", style="bold cyan")
    header_text.append(f"  v{stats['version']}", style="dim")
    header_text.append(f"  |  {stats['commands']} commands", style="green")
    header_text.append(f"  |  {datetime.now().strftime('%Y-%m-%d %H:%M')}", style="dim")
    return Panel(header_text, style="cyan", box=box.DOUBLE)


def build_quick_actions():
    """Build quick actions panel."""
    actions = Table(show_header=False, box=None, padding=(0, 2))
    actions.add_column("Key", style="bold yellow", width=5)
    actions.add_column("Action", style="white")
    actions.add_row("[n]", "New project")
    actions.add_row("[p]", "Plan project")
    actions.add_row("[e]", "Execute plan")
    actions.add_row("[d]", "Deploy")
    actions.add_row("[s]", "Sell (marketplace)")
    actions.add_row("[t]", "Run tests")
    actions.add_row("[g]", "Git status")
    actions.add_row("[h]", "Health check")
    actions.add_row("[q]", "Quit")
    return Panel(actions, title="⌨ Quick Actions", border_style="yellow")


def build_projects_panel():
    """Build projects list panel."""
    projects = get_projects()
    table = Table(show_header=True, box=box.SIMPLE, padding=(0, 1))
    table.add_column("#", style="dim", width=3)
    table.add_column("Project", style="bold white")
    table.add_column("Branch", style="cyan")
    table.add_column("Changes", style="yellow")
    table.add_column("Last Commit", style="dim")

    for i, proj in enumerate(projects[:8], 1):
        git = get_git_info(proj["path"])
        changes = f"[red]{git['changed']} files[/red]" if git["changed"] > 0 else "[green]clean[/green]"
        table.add_row(str(i), proj["name"], git["branch"], changes, git["last"])

    if not projects:
        table.add_row("-", "[dim]No projects found[/dim]", "", "", "")

    return Panel(table, title="📂 Projects", border_style="blue")


def build_marketplace_panel():
    """Build marketplace stats panel."""
    stats = get_marketplace_stats()
    content = Text()
    content.append(f"  🏪 Products: ", style="white")
    content.append(f"{stats['products']}\n", style="bold green")
    content.append(f"  💰 Catalog:  ", style="white")
    content.append(f"{stats['total_value']}\n", style="bold cyan")
    content.append(f"  🌐 ", style="white")
    content.append("frontend-hazel-ten-17.vercel.app", style="dim underline")
    return Panel(content, title="🏪 Marketplace", border_style="magenta")


def build_system_panel():
    """Build system info panel."""
    git = get_git_info(FRAMEWORK_ROOT)
    content = Text()
    content.append(f"  📍 {FRAMEWORK_ROOT}\n", style="dim")
    content.append(f"  🌿 Branch: ", style="white")
    content.append(f"{git['branch']}\n", style="cyan")
    content.append(f"  📝 Commits: ", style="white")
    content.append(f"{git['commits']}\n", style="green")
    content.append(f"  🕐 Last: ", style="white")
    content.append(f"{git['last']}\n", style="dim")
    content.append(f"  🐍 Python {sys.version.split()[0]}", style="dim")
    return Panel(content, title="⚙ System", border_style="green")


def run_dashboard():
    """Main dashboard loop."""
    console.clear()

    # Build layout
    console.print(build_header())
    console.print()

    cols = Columns([build_quick_actions(), build_marketplace_panel(), build_system_panel()],
                   equal=True, expand=True)
    console.print(cols)
    console.print()
    console.print(build_projects_panel())

    console.print()
    console.print("[dim]─" * 60 + "[/dim]")

    # Interactive loop
    while True:
        try:
            choice = Prompt.ask(
                "\n[bold yellow]⚡ Action[/bold yellow]",
                choices=["n", "p", "e", "d", "s", "t", "g", "h", "q", "r"],
                default="q"
            )
        except (KeyboardInterrupt, EOFError):
            break

        if choice == "q":
            console.print("[dim]Goodbye! 👋[/dim]")
            break
        elif choice == "r":
            console.clear()
            console.print(build_header())
            console.print()
            cols = Columns([build_quick_actions(), build_marketplace_panel(), build_system_panel()],
                          equal=True, expand=True)
            console.print(cols)
            console.print()
            console.print(build_projects_panel())
        elif choice == "n":
            desc = Prompt.ask("[cyan]Describe your project[/cyan]")
            if desc:
                console.print(f"[blue]Running: mw new --ai \"{desc}\"[/blue]")
                os.system(f'python3 {FRAMEWORK_ROOT}/tools/mw.py new --ai "{desc}"')
        elif choice == "p":
            desc = Prompt.ask("[cyan]Describe your project idea[/cyan]")
            if desc:
                console.print(f"[blue]Running: mw plan \"{desc}\"[/blue]")
                os.system(f'python3 {FRAMEWORK_ROOT}/tools/mw.py plan "{desc}"')
        elif choice == "e":
            phase = Prompt.ask("[cyan]Which phase?[/cyan]", default="all")
            os.system(f'python3 {FRAMEWORK_ROOT}/tools/mw.py execute {phase}')
        elif choice == "d":
            os.system(f'python3 {FRAMEWORK_ROOT}/tools/mw.py deploy')
        elif choice == "s":
            os.system(f'python3 {FRAMEWORK_ROOT}/tools/mw.py marketplace')
        elif choice == "t":
            os.system(f'python3 {FRAMEWORK_ROOT}/tools/mw.py test')
        elif choice == "g":
            os.system(f'python3 {FRAMEWORK_ROOT}/tools/mw.py git status')
        elif choice == "h":
            os.system(f'python3 {FRAMEWORK_ROOT}/tools/mw.py doctor')

    return 0


def cmd_tui(args=None):
    """Entry point for mw tui."""
    if args and args[0] in ("-h", "--help"):
        console.print("""
[bold]mw tui — Interactive Terminal Dashboard[/bold]
========================================
Usage: mw tui

One-key actions for your entire workflow:
  [n]ew project  [p]lan  [e]xecute  [d]eploy  [s]ell  [t]est  [g]it  [h]ealth
""")
        return 0
    return run_dashboard()


if __name__ == "__main__":
    cmd_tui(sys.argv[1:])
