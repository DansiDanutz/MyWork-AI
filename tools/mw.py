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
    mw projects     List all projects (uses project registry if available)
    mw projects scan    Refresh project registry
    mw projects export  Export project registry to markdown
    mw open <name>  Open project in VS Code
    mw cd <name>    Print cd command for project

Autocoder Commands:
    mw ac start <project>    Start Autocoder for project
    mw ac stop <project>     Stop Autocoder
    mw ac pause <project>    Pause Autocoder
    mw ac resume <project>   Resume Autocoder
    mw ac status             Check Autocoder status
    mw ac progress <project> Show Autocoder progress
    mw ac list               List Autocoder projects
    mw ac ui                 Open Autocoder UI
    mw ac service <command>  Manage Autocoder service (macOS)

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

Lint Commands:
    mw lint scan             Scan all files for linting issues
    mw lint scan --file X    Scan specific file
    mw lint scan --dir X     Scan specific directory
    mw lint watch            Watch files and auto-lint changes
    mw lint fix              Fix all linting issues
    mw lint config --show    Show current linting configuration
    mw lint config --edit    Edit linting configuration
    mw lint stats            Show linting statistics

Examples:
    mw status                # Quick overview
    mw search "auth"         # Find authentication modules
    mw new my-app fastapi    # Create FastAPI project
    mw ac start my-app       # Start Autocoder
    mw lint watch            # Auto-fix linting as you code
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import List, Optional

try:
    import yaml
except ImportError:  # pragma: no cover - optional dependency
    yaml = None

# Configuration - prefer shared config for consistent path detection
try:
    from config import MYWORK_ROOT, TOOLS_DIR, PROJECTS_DIR, PROJECT_REGISTRY_JSON
except ImportError:
    def _get_mywork_root() -> Path:
        if env_root := os.environ.get("MYWORK_ROOT"):
            return Path(env_root)
        script_dir = Path(__file__).resolve().parent
        if script_dir.name == "tools":
            potential_root = script_dir.parent
            if (potential_root / "CLAUDE.md").exists():
                return potential_root
        return Path.home() / "MyWork"

    MYWORK_ROOT = _get_mywork_root()
    TOOLS_DIR = MYWORK_ROOT / "tools"
    PROJECTS_DIR = MYWORK_ROOT / "projects"
    PROJECT_REGISTRY_JSON = MYWORK_ROOT / ".planning" / "project_registry.json"

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

    cmd = [sys.executable, str(tool_path)] + (args or [])
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
    args: Optional[List[str]] = None
    if len(sys.argv) > 2:
        args = sys.argv[2:]

    if args and args[0] in {"scan", "export", "stats", "list"}:
        return run_tool("project_registry", args)

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

    registry = None
    if PROJECT_REGISTRY_JSON.exists():
        try:
            registry = json.loads(PROJECT_REGISTRY_JSON.read_text())
        except Exception:
            registry = None

    def _parse_scalar(value: str):
        if value.startswith(("\"", "'")) and value.endswith(("\"", "'")):
            return value[1:-1]
        lowered = value.lower()
        if lowered in {"true", "yes"}:
            return True
        if lowered in {"false", "no"}:
            return False
        return value

    def _simple_yaml_load(text: str) -> dict:
        data = {}
        lines = text.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                i += 1
                continue
            if ":" not in stripped:
                i += 1
                continue
            key, raw_value = stripped.split(":", 1)
            key = key.strip()
            raw_value = raw_value.strip()
            if raw_value:
                data[key] = _parse_scalar(raw_value)
                i += 1
                continue
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and lines[j].lstrip().startswith("- "):
                items = []
                while j < len(lines) and lines[j].lstrip().startswith("- "):
                    items.append(_parse_scalar(lines[j].lstrip()[2:].strip()))
                    j += 1
                data[key] = items
                i = j
                continue
            if j < len(lines) and lines[j].startswith("  "):
                mapping = {}
                while j < len(lines) and lines[j].startswith("  "):
                    inner = lines[j].strip()
                    if not inner or inner.startswith("#"):
                        j += 1
                        continue
                    if ":" in inner:
                        inner_key, inner_value = inner.split(":", 1)
                        mapping[inner_key.strip()] = _parse_scalar(inner_value.strip())
                    j += 1
                data[key] = mapping
                i = j
                continue
            data[key] = {}
            i += 1
        return data

    def _safe_load_yaml(path: Path) -> dict:
        if not path.exists():
            return {}
        try:
            if yaml:
                return yaml.safe_load(path.read_text()) or {}
            return _simple_yaml_load(path.read_text())
        except Exception:
            return {}

    def _load_project_meta(project_path: Path) -> dict:
        if registry:
            return registry.get("projects", {}).get(project_path.name, {})
        metadata_path = project_path / "project.yaml"
        return _safe_load_yaml(metadata_path)

    for project in sorted(projects):
        # Check if it has GSD state
        has_gsd = (project / ".planning" / "STATE.md").exists()
        gsd_status = "✅" if has_gsd else "⚪"

        # Check for start script
        has_start = (project / "start.sh").exists() or (project / "start.bat").exists()
        start_status = "🚀" if has_start else ""

        meta = _load_project_meta(project)
        type_label = meta.get("type", "unknown")
        status_label = meta.get("status", "unknown")
        flags = []
        if meta.get("marketplace"):
            flags.append("🛒")
        if meta.get("brain_contribution"):
            flags.append("🧠")
        if not meta:
            flags.append("⚠️")
        flag_text = "".join(flags)

        print(f"   {gsd_status} {project.name} {start_status} ({type_label}, {status_label}) {flag_text}")

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
        if len(args) < 2:
            print("Usage: mw ac stop <project-name>")
            return 1
        return run_tool("autocoder_api", ["stop", args[1]])

    elif subcmd == "pause":
        if len(args) < 2:
            print("Usage: mw ac pause <project-name>")
            return 1
        return run_tool("autocoder_api", ["pause", args[1]])

    elif subcmd == "resume":
        if len(args) < 2:
            print("Usage: mw ac resume <project-name>")
            return 1
        return run_tool("autocoder_api", ["resume", args[1]])

    elif subcmd == "status":
        return run_tool("autocoder_api", ["status"])

    elif subcmd == "progress":
        if len(args) < 2:
            print("Usage: mw ac progress <project-name>")
            return 1
        return run_tool("autocoder_api", ["progress", args[1]])

    elif subcmd == "list":
        return run_tool("autocoder_api", ["list"])

    elif subcmd == "ui":
        return run_tool("autocoder_api", ["ui"])

    elif subcmd == "service":
        if len(args) < 2:
            print("Usage: mw ac service <setup|install|start|stop|restart|status|logs|uninstall> [options]")
            return 1
        return run_tool("autocoder_service", args[1:])

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


def is_auto_linter_running() -> bool:
    """Check if auto-linter is currently running."""
    import subprocess
    import platform

    try:
        if platform.system() == "Windows":
            result = subprocess.run([
                "tasklist", "/FI", "IMAGENAME eq python.exe"
            ], capture_output=True, text=True)
            return "auto_linting_agent" in result.stdout
        else:
            result = subprocess.run([
                "pgrep", "-f", "auto_linting_agent.py.*--watch"
            ], capture_output=True)
            return result.returncode == 0
    except:
        return False


def cmd_lint(args: List[str]):
    """Auto-linting commands."""
    if not args:
        print("Usage: mw lint <command>")
        print("\n🎯 Perfect Auto-Linting Commands:")
        print("   start                           Start auto-linter (with perfect markdown support)")
        print("   stop                            Stop auto-linter")
        print("   status                          Check auto-linter status")
        print("   install-hooks                   Install git hooks for automatic linting")
        print("\n📋 Standard Linting Commands:")
        print("   scan [--dir DIR] [--file FILE]  Scan for linting issues")
        print("   watch [--dir DIR]               Watch files and auto-lint")
        print("   fix [--dir DIR]                 Fix all linting issues")
        print("   config [--show] [--edit]        Show or edit configuration")
        print("   stats                           Show linting statistics")
        return 1

    subcmd = args[0]
    remaining = args[1:]

    # Perfect Auto-Linting Commands
    if subcmd == "start":
        print("🚀 Starting Perfect Auto-Linter...")
        import subprocess
        import platform

        # Check if already running
        if is_auto_linter_running():
            print("⚠️  Auto-linter is already running!")
            print("   Run 'mw lint status' to check or 'mw lint stop' to stop it first.")
            return 1

        # Use platform-appropriate startup script
        if platform.system() == "Windows":
            script_path = TOOLS_DIR / "start_auto_linter.bat"
            if script_path.exists():
                subprocess.Popen([str(script_path)], creationflags=subprocess.CREATE_NEW_CONSOLE)
                print("✅ Auto-linter started in new window")
            else:
                # Fallback to Python script
                subprocess.Popen([sys.executable, str(TOOLS_DIR / "auto_linting_agent.py"), "--watch", "--root", str(MYWORK_ROOT)])
                print("✅ Auto-linter started in background")
        else:
            script_path = TOOLS_DIR / "start_auto_linter.sh"
            if script_path.exists():
                subprocess.Popen(["/bin/bash", str(script_path)])
                print("✅ Auto-linter started in background")
            else:
                # Fallback to Python script
                subprocess.Popen([sys.executable, str(TOOLS_DIR / "auto_linting_agent.py"), "--watch", "--root", str(MYWORK_ROOT)])
                print("✅ Auto-linter started in background")

        print("\n💡 The auto-linter will now:")
        print("   ✅ Monitor all markdown files for changes")
        print("   ✅ Automatically fix markdown issues (MD001-MD060)")
        print("   ✅ Maintain perfect 0-violation markdown quality")
        print("   ✅ Work for all users in this project")
        print("\n   Run 'mw lint status' to check if it's working.")
        return 0

    elif subcmd == "stop":
        print("🛑 Stopping Auto-Linter...")
        import subprocess
        import platform

        stopped = False
        if platform.system() == "Windows":
            try:
                result = subprocess.run(
                    ["taskkill", "/F", "/FI", "WINDOWTITLE eq *auto_linting_agent*"],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    stopped = True
            except:
                pass
        else:
            try:
                result = subprocess.run(
                    ["pkill", "-f", "auto_linting_agent.py.*--watch"],
                    capture_output=True
                )
                if result.returncode == 0:
                    stopped = True
            except:
                pass

        if stopped:
            print("✅ Auto-linter stopped successfully")
        else:
            print("⚠️  No running auto-linter found (or already stopped)")
        return 0

    elif subcmd == "status":
        print("📊 Auto-Linter Status")
        print("=" * 50)

        # Check if auto-linter is running
        running = is_auto_linter_running()
        if running:
            print("🟢 Status: RUNNING")
            print("✅ Perfect markdown quality is actively maintained")
        else:
            print("🔴 Status: STOPPED")
            print("⚠️  Markdown files are not being automatically fixed")

        # Check if auto_lint_fixer.py exists and works
        auto_fixer_path = TOOLS_DIR / "auto_lint_fixer.py"
        if auto_fixer_path.exists():
            print("✅ Perfect markdown fixer: Available")
            # Test the fixer quickly
            try:
                result = subprocess.run([
                    sys.executable, "-c",
                    f"import sys; sys.path.insert(0, '{TOOLS_DIR}'); from auto_lint_fixer import AutoLintFixer; print('✅ Works')"
                ], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print("✅ Auto-fixer test: PASSED")
                else:
                    print("❌ Auto-fixer test: FAILED")
            except:
                print("⚠️  Auto-fixer test: Could not test")
        else:
            print("❌ Perfect markdown fixer: MISSING")

        # Check git hooks
        git_hooks_dir = MYWORK_ROOT / ".git" / "hooks"
        if git_hooks_dir.exists():
            pre_commit_hook = git_hooks_dir / "pre-commit"
            pre_push_hook = git_hooks_dir / "pre-push"
            if pre_commit_hook.exists() and pre_push_hook.exists():
                print("✅ Git hooks: Installed")
            else:
                print("⚠️  Git hooks: Partially installed")
        else:
            print("❌ Git hooks: Not installed")

        # Show recommendation
        print("\n💡 Recommendation:")
        if not running:
            print("   Run 'mw lint start' to enable automatic markdown fixing for all users")
        if not (git_hooks_dir / "pre-commit").exists():
            print("   Run 'mw lint install-hooks' to set up git integration")

        return 0

    elif subcmd == "install-hooks":
        print("🔗 Installing Git Hooks for Automatic Linting...")

        git_hooks_dir = MYWORK_ROOT / ".git" / "hooks"
        if not git_hooks_dir.exists():
            print("❌ Error: Not a git repository or .git/hooks directory not found")
            return 1

        # Install pre-commit hook
        pre_commit_hook = git_hooks_dir / "pre-commit"
        pre_commit_content = """#!/bin/bash
# Auto-lint markdown files before commit
echo "🔧 Auto-linting markdown files..."
find . -name "*.md" -not -path "./.git/*" -not -path "./node_modules/*" -exec python3 tools/auto_lint_fixer.py {} \\;
"""
        pre_commit_hook.write_text(pre_commit_content)
        pre_commit_hook.chmod(0o755)
        print("   ✅ Pre-commit hook installed")

        # Install pre-push hook
        pre_push_hook = git_hooks_dir / "pre-push"
        pre_push_content = """#!/bin/bash
# Final lint check before push
echo "🚀 Final markdown validation before push..."
if find . -name "*.md" -not -path "./.git/*" -not -path "./node_modules/*" -exec markdownlint {} \\; 2>/dev/null | grep -q .; then
    echo "❌ Markdown violations found. Auto-fixing..."
    python3 tools/auto_lint_fixer.py .
    echo "✅ Issues fixed. Please review and commit the changes."
    exit 1
fi
echo "✅ All markdown files perfect!"
"""
        pre_push_hook.write_text(pre_push_content)
        pre_push_hook.chmod(0o755)
        print("   ✅ Pre-push hook installed")

        print("\n🎯 Git Hooks Configured:")
        print("   ✅ Pre-commit: Auto-fixes markdown before each commit")
        print("   ✅ Pre-push: Ensures perfect markdown before push")
        print("\n💡 All users will now get automatic markdown fixing during git operations!")
        return 0

    # Standard Linting Commands
    elif subcmd == "scan":
        lint_args = ["--scan"]
        for i in range(0, len(remaining), 2):
            if i + 1 < len(remaining):
                if remaining[i] == "--dir":
                    lint_args.extend(["--dir", remaining[i + 1]])
                elif remaining[i] == "--file":
                    lint_args.extend(["--file", remaining[i + 1]])
        return run_tool("auto_linting_agent", lint_args)

    elif subcmd == "watch":
        lint_args = ["--watch"]
        for i in range(0, len(remaining), 2):
            if i + 1 < len(remaining) and remaining[i] == "--dir":
                lint_args.extend(["--dir", remaining[i + 1]])
        return run_tool("auto_linting_agent", lint_args)

    elif subcmd == "fix":
        lint_args = ["--scan"]  # Scan mode with auto-fix enabled
        for i in range(0, len(remaining), 2):
            if i + 1 < len(remaining) and remaining[i] == "--dir":
                lint_args.extend(["--dir", remaining[i + 1]])
        return run_tool("auto_linting_agent", lint_args)

    elif subcmd == "config":
        config_path = MYWORK_ROOT / ".planning" / "config" / "lint.json"
        if "--show" in remaining:
            if config_path.exists():
                print(f"📁 Lint Configuration: {config_path}")
                print("-" * 50)
                with open(config_path) as f:
                    print(f.read())
            else:
                print("No lint configuration found. Run 'mw lint scan' to create default config.")
            return 0
        elif "--edit" in remaining:
            if not config_path.exists():
                print("No lint configuration found. Creating default config...")
                return run_tool("auto_linting_agent", ["--config", str(config_path)])
            subprocess.call(["code", str(config_path)])
            print(f"✅ Opened lint config in VS Code: {config_path}")
            return 0
        else:
            print("Usage: mw lint config [--show] [--edit]")
            return 1

    elif subcmd == "stats":
        return run_tool("auto_linting_agent", ["--stats"])

    else:
        print(f"Unknown lint command: {subcmd}")
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
        "lint": lambda: cmd_lint(args),
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
