#!/usr/bin/env python3
"""
MyWork Command Line Interface (mw)
==================================
Unified interface for all MyWork framework tools.

Usage:
    mw <command> [options]

Commands:
    dashboard       Interactive framework dashboard with metrics and status
    status          Quick health check of all components
    setup           First-time setup wizard for new users
    guide           Interactive workflow guide and tutorial
    update          Check and apply updates (GSD, AutoForge, n8n)
    search <query>  Search module registry for reusable code
    new <name>      Create a new project (see: mw new --help)
    prompt-enhance  Enhance rough prompts for GSD planning
    scan            Scan all projects and update module registry
    fix             Auto-fix common issues
    report          Generate detailed health report
    doctor          Full system diagnostics
    ecosystem       Show all live app URLs and ecosystem overview
    marketplace     Open marketplace information and links
    links           Show all useful framework links

Project Commands:
    mw projects     List all projects (uses project registry if available)
    mw projects scan    Refresh project registry
    mw projects export  Export project registry to markdown
    mw open <name>  Open project in VS Code
    mw cd <name>    Print cd command for project

AutoForge Commands:
    mw af start <project>    Start AutoForge for project
    mw af stop <project>     Stop AutoForge
    mw af pause <project>    Pause AutoForge
    mw af resume <project>   Resume AutoForge
    mw af status             Check AutoForge status
    mw af progress <project> Show AutoForge progress
    mw af list               List AutoForge projects
    mw af ui                 Open AutoForge UI
    mw af service <command>  Manage AutoForge service (macOS)

Legacy Commands (deprecated but supported):
    mw ac <subcommand>       Alias for AutoForge commands (backwards compatibility)

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

AI Assistant Commands:
    mw ai ask "question"     Ask a coding question
    mw ai explain <file>     Explain code in a file
    mw ai fix <file>         Fix bugs in code
    mw ai refactor <file>    Get refactoring suggestions
    mw ai test <file>        Generate tests for code
    mw ai commit [--push]    Generate commit message from diff

Code Review & Quality Commands:
    mw review <file>         AI-powered code review of specific file
    mw review --diff         Review current git diff
    mw review --staged       Review staged changes
    mw docs generate <proj>  Generate AI documentation for project
    mw health <project>      Score project health (0-100)
    mw deploy <proj> --platform <vercel|railway|render>  Deploy project

Examples:
    mw setup                 # First-time setup wizard
    mw guide                 # Learn the MyWork workflow
    mw status                # Quick health overview  
    mw search "auth"         # Find authentication modules
    mw new my-app fastapi    # Create FastAPI project
    mw prompt-enhance "build a todo app"  # Enhance prompts for GSD
    mw af start my-app       # Start AutoForge
    mw lint watch            # Auto-fix linting as you code
    mw review main.py        # AI code review
    mw docs generate my-app  # Generate documentation
    mw health my-app         # Check project health
    mw deploy my-app --platform vercel  # Deploy to Vercel
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
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def color(text: str, color_code: str) -> str:
    """Apply color to text."""
    return f"{color_code}{text}{Colors.ENDC}"


def validate_input(value: str, name: str, max_length: int = 255, allow_empty: bool = False, 
                  allow_paths: bool = False) -> bool:
    """Validate user input for security and correctness.
    
    Args:
        value: The input value to validate
        name: Name of the input field for error messages
        max_length: Maximum allowed length
        allow_empty: Whether empty strings are allowed
        allow_paths: Whether path characters like / are allowed
        
    Returns:
        True if valid, False if invalid (with error message printed)
    """
    if not allow_empty and not value.strip():
        print(f"{Colors.RED}❌ Error: {name} cannot be empty{Colors.ENDC}")
        return False
    
    if len(value) > max_length:
        print(f"{Colors.RED}❌ Error: {name} too long (max {max_length} chars, got {len(value)}){Colors.ENDC}")
        return False
    
    # Check for path traversal attempts
    if not allow_paths:
        dangerous_patterns = ['../', '..\\', '/./', '/.\\', '/..', '\\..']
        for pattern in dangerous_patterns:
            if pattern in value:
                print(f"{Colors.RED}❌ Error: {name} contains invalid path characters{Colors.ENDC}")
                return False
    
    # Check for null bytes and other dangerous characters
    if '\x00' in value:
        print(f"{Colors.RED}❌ Error: {name} contains null bytes{Colors.ENDC}")
        return False
    
    # Check for potentially dangerous characters in non-path inputs
    if not allow_paths:
        dangerous_chars = ['<', '>', '|', '&', ';', '$', '`']
        for char in dangerous_chars:
            if char in value:
                print(f"{Colors.RED}❌ Error: {name} contains invalid character: '{char}'{Colors.ENDC}")
                return False
    
    return True


def validate_project_name(name: str) -> bool:
    """Validate project name according to MyWork conventions.
    
    Args:
        name: Project name to validate
        
    Returns:
        True if valid, False if invalid (with error message printed)
    """
    if not validate_input(name, "project name", max_length=50):
        return False
    
    # Project name specific validation
    import re
    if not re.match(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$|^[a-z0-9]$', name):
        print(f"{Colors.RED}❌ Error: Invalid project name '{name}'{Colors.ENDC}")
        print(f"{Colors.YELLOW}   Project names must:{Colors.ENDC}")
        print(f"   • Be lowercase letters, numbers, and hyphens only")
        print(f"   • Start and end with a letter or number")
        print(f"   • Not contain spaces or special characters")
        print(f"{Colors.BLUE}   Examples: my-app, api-server, todo-list{Colors.ENDC}")
        return False
    
    return True


def run_tool(tool_name: str, args: List[str] = None) -> int:
    """Run a MyWork tool with arguments.
    
    Args:
        tool_name: Name of the tool to run (without .py extension)
        args: Optional list of arguments to pass to the tool
        
    Returns:
        Exit code from the tool (0 for success, non-zero for error)
    """
    tool_path = TOOLS_DIR / f"{tool_name}.py"
    if not tool_path.exists():
        print(f"{Colors.RED}Tool not found: {tool_name}{Colors.ENDC}")
        return 1

    cmd = [sys.executable, str(tool_path)] + (args or [])
    return subprocess.call(cmd)


def cmd_status(args: Optional[List[str]] = None) -> int:
    """Run a quick health check of all MyWork framework components.
    
    Args:
        args: Command line arguments, supports --help/-h for usage info
        
    Returns:
        Exit code from the health check tool
    """
    if args and (args[0] in ["--help", "-h"]):
        print("""
Status Commands — Framework Health Monitor
==========================================
Usage:
    mw status              Quick health check of all components
    mw status --help       Show this help message

Description:
    Runs a quick health check on MyWork framework components including:
    • GSD Installation
    • AutoForge Installation  
    • n8n-skills
    • Configuration files
    • Project registry
    
Examples:
    mw status              # Check framework health
    mw doctor              # Full system diagnostics
    mw fix                 # Auto-fix common issues
""")
        return 0
    
    print(f"\n{Colors.BOLD}🔍 MyWork Quick Status{Colors.ENDC}")
    print("=" * 50)
    return run_tool("health_check", ["quick"])


def cmd_update(args: List[str]) -> int:
    """Check and apply updates for GSD, AutoForge, and n8n components.
    
    Args:
        args: Update command arguments (defaults to 'check' if empty)
        
    Returns:
        Exit code from the auto_update tool
    """
    if not args:
        args = ["check"]
    return run_tool("auto_update", args)


def cmd_search(args: List[str]) -> int:
    """Search the module registry for reusable code components.
    
    Args:
        args: Search query or --help/-h for usage information
        
    Returns:
        Exit code from the module registry search
    """
    if not args or (len(args) == 1 and args[0] in ["--help", "-h"]):
        print("""
Search Commands — Module Registry Search  
========================================
Usage:
    mw search <query>               Search module registry for reusable code
    mw search --help                Show this help message

Description:
    Search through the module registry to find reusable code components,
    functions, and patterns from existing projects. Helps avoid reinventing
    the wheel by finding code you or others have already written.

Examples:
    mw search "auth"                # Find authentication modules
    mw search "database"            # Find database-related code
    mw search "api client"          # Find API client implementations
    mw search "validation"          # Find validation functions
""")
        return 0
    
    if args[0] in ["--help", "-h"]:
        return 0  # Help already shown above
    
    # Validate search query
    query = " ".join(args)
    if not validate_input(query, "search query", max_length=200, allow_empty=False):
        return 1
        
    return run_tool("module_registry", ["search"] + args)


def cmd_new(args: List[str]) -> int:
    """Create new project."""
    if not args or (len(args) == 1 and args[0] in ["--help", "-h"]):
        print("""
New Project Commands — Project Scaffolding
==========================================
Usage:
    mw new <name> [template]        Create a new project
    mw new --help                   Show this help message

Templates:
    basic                           Basic project structure
    fastapi                         FastAPI web service  
    nextjs                          Next.js web application
    fullstack                       Full-stack web application
    cli                             Command-line interface tool
    automation                      Automation/scripting project

Description:
    Creates a new project with the MyWork framework structure including:
    • Project directory and basic files
    • Planning directory with PROJECT.md and ROADMAP.md
    • GSD (Get Stuff Done) integration
    • Template-specific boilerplate code

Examples:
    mw new my-api fastapi           # Create FastAPI project
    mw new todo-app fullstack       # Create full-stack project  
    mw new backup-tool cli          # Create CLI tool project
    mw new website nextjs           # Create Next.js project
""")
        return 0
    
    if args[0] in ["--help", "-h"]:
        return 0  # Help already shown above
    
    # Validate project name if provided
    if len(args) > 0:
        project_name = args[0]
        if not validate_project_name(project_name):
            return 1
    
    # Validate template name if provided
    if len(args) > 1:
        template = args[1]
        if not validate_input(template, "template name", max_length=50):
            return 1
        
    return run_tool("scaffold", ["new"] + args)


def cmd_scan() -> int:
    """Scan projects for modules."""
    print(f"\n{Colors.BOLD}🔍 Scanning projects for modules...{Colors.ENDC}")
    return run_tool("module_registry", ["scan"])


def cmd_fix() -> int:
    """Auto-fix issues."""
    return run_tool("health_check", ["fix"])


def cmd_report() -> int:
    """Generate health report."""
    return run_tool("health_check", ["report"])


def cmd_doctor() -> int:
    """Full system diagnostics."""
    return run_tool("health_check")


def cmd_dashboard(args: Optional[List[str]] = None) -> None:
    """Interactive framework dashboard with metrics and status."""
    if args and (args[0] in ["--help", "-h"]):
        print("""
Dashboard Commands — Framework Overview
=======================================
Usage:
    mw dashboard                    Show interactive framework dashboard
    mw dashboard --help             Show this help message

Description:
    Displays a comprehensive overview of your MyWork framework including:
    • Framework version and info
    • Project count and status
    • Component status (AutoForge, Brain, n8n, etc.)
    • Recent git activity
    • Disk usage statistics
    • Quick health indicators

Examples:
    mw dashboard                    # Show full dashboard
    mw status                       # Quick health check
    mw doctor                       # Detailed diagnostics
""")
        return 0
        
    import shutil
    import datetime
    from pathlib import Path
    
    # Terminal colors
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    
    def colored_box(title, content, color=CYAN):
        """Create a colored box with title and content."""
        lines = content.strip().split('\n')
        max_width = max(len(line) for line in [title] + lines) + 4
        
        print(f"\n{color}{'╭' + '─' * (max_width - 2) + '╮'}{RESET}")
        print(f"{color}│{BOLD} {title:^{max_width - 4}} {RESET}{color}│{RESET}")
        print(f"{color}├{'─' * (max_width - 2)}┤{RESET}")
        for line in lines:
            print(f"{color}│ {line:<{max_width - 4}} │{RESET}")
        print(f"{color}╰{'─' * (max_width - 2)}╯{RESET}")
    
    def get_git_status():
        """Get recent git activity."""
        try:
            # Get last 3 commits
            result = subprocess.run(
                ["git", "log", "--oneline", "-3"],
                cwd=MYWORK_ROOT,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                commits = result.stdout.strip().split('\n')[:3]
                return '\n'.join(commits) if commits else "No commits found"
            else:
                return "Not a git repository"
        except Exception:
            return "Git not available"
    
    def get_disk_usage():
        """Get disk usage for framework."""
        try:
            total, used, free = shutil.disk_usage(MYWORK_ROOT)
            framework_size = subprocess.run(
                ["du", "-sh", str(MYWORK_ROOT)],
                capture_output=True,
                text=True
            )
            if framework_size.returncode == 0:
                size = framework_size.stdout.split()[0]
                return f"Framework size: {size}\nFree space: {free // (1024**3)}GB"
            else:
                return f"Free space: {free // (1024**3)}GB"
        except Exception:
            return "Unable to get disk usage"
    
    def get_project_count():
        """Get number of projects."""
        try:
            projects_path = MYWORK_ROOT / "projects"
            if projects_path.exists():
                count = len([p for p in projects_path.iterdir() if p.is_dir()])
                return f"{count} projects found"
            else:
                return "Projects directory not found"
        except Exception:
            return "Unable to count projects"
    
    def get_component_status():
        """Check status of framework components."""
        components = {
            "AutoForge API": "autoforge_api.py",
            "Brain": "brain.py", 
            "Health Check": "health_check.py",
            "Module Registry": "module_registry.py",
            "n8n API": "n8n_api.py"
        }
        
        statuses = []
        tools_dir = MYWORK_ROOT / "tools"
        
        for name, filename in components.items():
            file_path = tools_dir / filename
            if file_path.exists():
                statuses.append(f"{GREEN}✓{RESET} {name}")
            else:
                statuses.append(f"{RED}✗{RESET} {name}")
        
        return '\n'.join(statuses)
    
    def get_framework_version():
        """Get framework version."""
        try:
            pyproject_path = MYWORK_ROOT / "pyproject.toml"
            if pyproject_path.exists():
                with open(pyproject_path, 'r') as f:
                    for line in f:
                        if line.startswith('version ='):
                            version = line.split('=')[1].strip().strip('"')
                            return f"MyWork-AI v{version}"
            return "Version not found"
        except Exception:
            return "Unable to get version"
    
    # Main dashboard display
    print(f"\n{BOLD}{BLUE}{'═' * 60}{RESET}")
    print(f"{BOLD}{BLUE} MyWork-AI Framework Dashboard {RESET}")
    print(f"{BOLD}{BLUE}{'═' * 60}{RESET}")
    print(f"{CYAN} Generated at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
    
    # Framework Info
    colored_box("FRAMEWORK INFO", get_framework_version(), BLUE)
    
    # Project Count
    colored_box("PROJECTS", get_project_count(), GREEN)
    
    # Component Status
    colored_box("COMPONENT STATUS", get_component_status(), YELLOW)
    
    # Git Activity  
    colored_box("RECENT GIT ACTIVITY", get_git_status(), CYAN)
    
    # Disk Usage
    colored_box("DISK USAGE", get_disk_usage(), GREEN)
    
    print(f"\n{BOLD}{BLUE}{'═' * 60}{RESET}")
    print(f"{CYAN} Use 'mw status' for quick health check or 'mw doctor' for diagnostics{RESET}")
    print(f"{BOLD}{BLUE}{'═' * 60}{RESET}\n")
    
    return 0


def cmd_projects() -> None:
    """List all projects."""
    args: Optional[List[str]] = None
    if len(sys.argv) > 2:
        args = sys.argv[2:]

    if args and args[0] in {"scan", "export", "stats", "list"}:
        return run_tool("project_registry", args)
    
    if args and args[0] == "health":
        if len(args) < 2:
            print("Usage: mw projects health <project-name>")
            return 1
        return cmd_project_health(args[1])

    print(f"\n{Colors.BOLD}📁 MyWork Projects{Colors.ENDC}")
    print("=" * 50)

    if not PROJECTS_DIR.exists():
        print(f"{Colors.RED}Projects directory not found{Colors.ENDC}")
        return 1

    projects = [
        p for p in PROJECTS_DIR.iterdir() if p.is_dir() and not p.name.startswith((".", "_"))
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
        if value.startswith(('"', "'")) and value.endswith(('"', "'")):
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

        print(
            f"   {gsd_status} {project.name} {start_status} ({type_label}, {status_label}) {flag_text}"
        )

    print(f"\n   Total: {len(projects)} projects")
    return 0


def cmd_project_health(project_name: str) -> int:
    """Check health of a specific project."""
    project_path = PROJECTS_DIR / project_name
    
    if not project_path.exists() or not project_path.is_dir():
        print(f"{Colors.RED}Project '{project_name}' not found{Colors.ENDC}")
        return 1
    
    print(f"{Colors.BOLD}🔍 Health Check for Project: {project_name}{Colors.ENDC}")
    print(f"{Colors.BLUE}{'=' * 60}{Colors.ENDC}")
    
    # Initialize metrics
    metrics = {
        "tests_exists": False,
        "ci_configured": False,
        "docs_complete": False,
        "gitignore_proper": False,
        "dependencies_up_to_date": False
    }
    
    # Check for tests directory
    tests_dirs = ["tests", "spec", "__tests__", "test"]
    metrics["tests_exists"] = any((project_path / t).exists() for t in tests_dirs)
    
    # Check for CI configuration
    ci_files = [".github/workflows", "bitbucket-pipelines.yml", ".gitlab-ci.yml", "Jenkinsfile"]
    metrics["ci_configured"] = any((project_path / f).exists() for f in ci_files)
    
    # Check for documentation
    docs_files = ["README.md", "docs/", "DOCS.md", "API.md"]
    metrics["docs_complete"] = any((project_path / f).exists() for f in docs_files)
    
    # Check .gitignore
    gitignore_path = project_path / ".gitignore"
    metrics["gitignore_proper"] = gitignore_path.exists() and "node_modules" in gitignore_path.read_text()
    
    # Check dependencies (simplified check)
    lock_files = ["package-lock.json", "yarn.lock", "poetry.lock", "requirements.lock"]
    metrics["dependencies_up_to_date"] = any((project_path / f).exists() for f in lock_files)
    
    # Calculate score (20 points per metric)
    score = sum(20 for value in metrics.values() if value)
    
    # Print report
    print(f"{Colors.BOLD}➤ Tests Exist:          {tick_cross(metrics['tests_exists'])}{Colors.ENDC}")
    print(f"{Colors.BOLD}➤ CI Configured:        {tick_cross(metrics['ci_configured'])}{Colors.ENDC}")
    print(f"{Colors.BOLD}➤ Docs Complete:        {tick_cross(metrics['docs_complete'])}{Colors.ENDC}")
    print(f"{Colors.BOLD}➤ .gitignore Proper:    {tick_cross(metrics['gitignore_proper'])}{Colors.ENDC}")
    print(f"{Colors.BOLD}➤ Dependencies Updated: {tick_cross(metrics['dependencies_up_to_date'])}{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}{Colors.YELLOW}🏆 Health Score: {score}/100{Colors.ENDC}")
    
    # Recommendations
    print(f"\n{Colors.BOLD}📌 Recommendations:{Colors.ENDC}")
    if not metrics["tests_exists"]:
        print(f"  • Add tests in /tests directory")
    if not metrics["ci_configured"]:
        print(f"  • Configure CI in .github/workflows/")
    if not metrics["docs_complete"]:
        print(f"  • Improve documentation in README.md")
    if not metrics["gitignore_proper"]:
        print(f"  • Update .gitignore to exclude node_modules/ and other build artifacts")
    if not metrics["dependencies_up_to_date"]:
        print(f"  • Run 'npm install' or 'pip freeze > requirements.txt' to update dependencies")
    
    return 0

def tick_cross(condition: bool) -> str:
    """Return colored tick or cross based on condition."""
    return f"{Colors.GREEN}✓{Colors.ENDC}" if condition else f"{Colors.RED}✗{Colors.ENDC}"


def cmd_open(args: List[str]) -> None:
    """Open project in VS Code."""
    if not args:
        print(f"{Colors.RED}❌ Error: Project name required{Colors.ENDC}")
        print("Usage: mw open <project-name>")
        return 1

    project_name = args[0]
    
    # Validate project name
    if not validate_project_name(project_name):
        return 1
    project_path = PROJECTS_DIR / project_name

    if not project_path.exists():
        print(f"{Colors.RED}Project not found: {project_name}{Colors.ENDC}")
        return 1

    subprocess.call(["code", str(project_path)])
    print(f"✅ Opened {project_name} in VS Code")
    return 0


def cmd_cd(args: List[str]) -> None:
    """Print cd command for project."""
    if not args:
        print(f"{Colors.RED}❌ Error: Project name required{Colors.ENDC}")
        print("Usage: mw cd <project-name>")
        return 1

    project_name = args[0]
    
    # Validate project name
    if not validate_project_name(project_name):
        return 1
    project_path = PROJECTS_DIR / project_name

    if not project_path.exists():
        print(f"{Colors.RED}Project not found: {project_name}{Colors.ENDC}")
        return 1

    print(f"cd {project_path}")
    return 0


def cmd_autoforge(args: List[str]) -> int:
    """AutoForge commands."""
    if not args or (len(args) == 1 and args[0] in ["--help", "-h"]):
        print("""
AutoForge Commands — Autonomous Coding Assistant
================================================
Usage:
    mw af start <project>           Start AutoForge for project
    mw af stop <project>            Stop AutoForge
    mw af pause <project>           Pause AutoForge
    mw af resume <project>          Resume AutoForge
    mw af status                    Check AutoForge status
    mw af progress <project>        Show AutoForge progress
    mw af list                      List AutoForge projects
    mw af ui                        Open AutoForge UI
    mw af service <command>         Manage AutoForge service (macOS)
    mw af --help                    Show this help message

Description:
    AutoForge is an autonomous coding assistant that can handle complex
    development tasks. It integrates with GSD (Get Stuff Done) to execute
    project phases automatically.

Examples:
    mw af start my-app              # Start AutoForge on my-app project
    mw af pause my-app              # Pause development
    mw af resume my-app             # Resume development
    mw af progress my-app           # Check progress
    mw af ui                        # Open web interface

Legacy aliases: ac, autocoder (deprecated but supported)
""")
        return 0

    subcmd = args[0]
    remaining = args[1:]

    # Handle --help for each subcommand
    if len(remaining) > 0 and remaining[0] in ["--help", "-h"]:
        if subcmd == "start":
            print("""
mw af start — Start AutoForge
=============================
Usage: mw af start <project-name>

Description:
    Start AutoForge autonomous development for a project.
    AutoForge will analyze the project and begin development.

Examples:
    mw af start my-webapp
    mw af start api-server
""")
            return 0
        elif subcmd in ["stop", "pause", "resume"]:
            print(f"""
mw af {subcmd} — {subcmd.title()} AutoForge
{'=' * (len(subcmd) + 20)}
Usage: mw af {subcmd} <project-name>

Description:
    {subcmd.title()} AutoForge development for a project.

Examples:
    mw af {subcmd} my-webapp
""")
            return 0

    if subcmd == "start":
        if len(args) < 2:
            print("Usage: mw af start <project-name>")
            return 1
        return run_tool("autoforge_api", ["start", args[1]])

    elif subcmd == "stop":
        if len(args) < 2:
            print("Usage: mw af stop <project-name>")
            return 1
        return run_tool("autoforge_api", ["stop", args[1]])

    elif subcmd == "pause":
        if len(args) < 2:
            print("Usage: mw af pause <project-name>")
            return 1
        return run_tool("autoforge_api", ["pause", args[1]])

    elif subcmd == "resume":
        if len(args) < 2:
            print("Usage: mw af resume <project-name>")
            return 1
        return run_tool("autoforge_api", ["resume", args[1]])

    elif subcmd == "status":
        return run_tool("autoforge_api", ["status"])

    elif subcmd == "progress":
        if len(args) < 2:
            print("Usage: mw af progress <project-name>")
            return 1
        return run_tool("autoforge_api", ["progress", args[1]])

    elif subcmd == "list":
        return run_tool("autoforge_api", ["list"])

    elif subcmd == "ui":
        return run_tool("autoforge_api", ["ui"])

    elif subcmd == "service":
        if len(args) < 2:
            print(
                "Usage: mw af service <setup|install|start|stop|restart|status|logs|uninstall> [options]"
            )
            return 1
        return run_tool("autoforge_service", args[1:])

    else:
        print(f"Unknown autoforge command: {subcmd}")
        return 1


def cmd_n8n(args: List[str]) -> int:
    """n8n commands."""
    if not args or (len(args) == 1 and args[0] in ["--help", "-h"]):
        print("""
n8n Commands — Workflow Automation Manager
==========================================
Usage:
    mw n8n list                     List n8n workflows
    mw n8n status                   Check n8n connection status
    mw n8n --help                   Show this help message

Description:
    Interface with n8n workflow automation platform. Allows you to
    manage and monitor your automation workflows from the MyWork CLI.

Examples:
    mw n8n status                   # Check if n8n is running
    mw n8n list                     # List all workflows
""")
        return 0

    subcmd = args[0]

    if subcmd == "list":
        return run_tool("n8n_api", ["--action", "list"])

    elif subcmd == "status":
        # Quick check of n8n connection
        return run_tool("n8n_api", ["--action", "health"])

    else:
        print(f"Unknown n8n command: {subcmd}")
        return 1


def cmd_brain(args: List[str]) -> int:
    """Brain knowledge vault commands."""
    if not args or (len(args) == 1 and args[0] in ["--help", "-h"]):
        print("""
Brain Commands — Knowledge Vault Manager
=========================================
Usage:
    mw brain search <query>         Search the knowledge vault
    mw brain add <content>          Add a new lesson
    mw brain review                 Show entries needing review
    mw brain stats                  Show brain statistics
    mw brain list                   List all brain entries
    mw brain learn                  Auto-discover learnings (daily)
    mw brain learn-deep             Weekly deep analysis
    mw brain discover               Discover new learnings
    mw brain cleanup                Clean up duplicate entries
    mw brain quality                Quality report (scores + dupes)
    mw brain score                  Score all entries (0-100)
    mw brain dedupe [--apply]       Find/remove duplicates
    mw brain prune [--below N]      Remove low-quality entries
    mw brain semantic <query>       Semantic search (TF-IDF)
    mw brain duplicates             Find near-duplicate entries
    mw brain provenance <id>        Show entry history/provenance
    mw brain reindex                Rebuild semantic search index
    mw brain --help                 Show this help message

Description:
    The Brain is your personal knowledge vault that learns from your work.
    It captures lessons, insights, and patterns from your projects to help
    you avoid repeating mistakes and build on past successes.

Examples:
    mw brain search "deployment"
    mw brain add "Always test before deploying" --context "Learned from outage"
    mw brain review
    mw brain stats
    mw brain learn
""")
        return 0

    subcmd = args[0]
    remaining = args[1:]

    # Handle --help for each subcommand
    if len(remaining) > 0 and remaining[0] in ["--help", "-h"]:
        if subcmd == "search":
            print("""
mw brain search — Search Knowledge Vault
========================================
Usage: mw brain search <query>

Description:
    Search through your accumulated knowledge and lessons.
    Supports fuzzy matching and keyword search.

Examples:
    mw brain search "deployment"
    mw brain search "error handling"
    mw brain search "best practices"
""")
            return 0
        elif subcmd == "add":
            print("""
mw brain add — Add Knowledge Entry
==================================
Usage: mw brain add <content> [--context <context>]

Description:
    Add a new lesson or insight to your knowledge vault.
    Content is automatically categorized and indexed.

Examples:
    mw brain add "Always test before deploying"
    mw brain add "Use environment variables for secrets" --context "Security lesson"
""")
            return 0
        elif subcmd == "review":
            print("""
mw brain review — Review Knowledge
==================================
Usage: mw brain review

Description:
    Show entries that need review or attention.
    Helps you reinforce important lessons.

Examples:
    mw brain review
""")
            return 0

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

    elif subcmd == "quality":
        return run_tool("brain_quality", ["report"])

    elif subcmd == "dedupe":
        apply_flag = ["--apply"] if "--apply" in remaining else []
        return run_tool("brain_quality", ["dedupe"] + apply_flag)

    elif subcmd == "score":
        return run_tool("brain_quality", ["score"])

    elif subcmd == "prune":
        return run_tool("brain_quality", ["prune"] + remaining)

    elif subcmd == "semantic":
        if not remaining:
            print("Usage: mw brain semantic <query>")
            return 1
        return run_tool("brain_semantic", ["search"] + remaining)

    elif subcmd == "duplicates":
        return run_tool("brain_semantic", ["dedupe"] + remaining)

    elif subcmd == "provenance":
        if not remaining:
            print("Usage: mw brain provenance <entry_id>")
            return 1
        return run_tool("brain_semantic", ["provenance"] + remaining)

    elif subcmd == "reindex":
        return run_tool("brain_semantic", ["reindex"])

    else:
        print(f"Unknown brain command: {subcmd}")
        return 1


def is_auto_linter_running() -> bool:
    """Check if auto-lint scheduler is currently running."""
    import subprocess
    import platform

    try:
        if platform.system() == "Windows":
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq python.exe"], capture_output=True, text=True
            )
            return "auto_lint_scheduler" in result.stdout
        else:
            result = subprocess.run(
                ["pgrep", "-f", "auto_lint_scheduler.py.*--daemon"], capture_output=True
            )
            return result.returncode == 0
    except:
        return False


def cmd_credits(args: List[str]) -> int:
    """Credits ledger management — Phase 8 Payments."""
    import subprocess
    script = os.path.join(os.path.dirname(__file__), "credits_ledger.py")
    result = subprocess.run([sys.executable, script] + args)
    return result.returncode


def cmd_lint(args: List[str]) -> int:
    """Auto-linting commands."""
    if not args or (len(args) == 1 and args[0] in ["--help", "-h"]):
        print("""
Lint Commands — Automatic Code Quality Manager
==============================================
🎯 Scheduled Linting Commands:
    mw lint start                   Start lint scheduler (every 4 hours)
    mw lint stop                    Stop lint scheduler  
    mw lint status                  Check scheduler status
    mw lint install-hooks           Install git hooks for automatic linting
    mw lint uninstall-hooks         Remove git hooks

📋 Standard Linting Commands:
    mw lint scan                    Scan all files for linting issues
    mw lint scan --dir <DIR>        Scan specific directory
    mw lint scan --file <FILE>      Scan specific file
    mw lint watch                   Watch files and auto-lint changes
    mw lint watch --dir <DIR>       Watch specific directory
    mw lint fix                     Fix all linting issues
    mw lint fix --dir <DIR>         Fix specific directory
    mw lint config --show           Show current configuration
    mw lint config --edit           Edit configuration
    mw lint stats                   Show linting statistics
    mw lint --help                  Show this help message

Description:
    Automatic linting system that keeps your code clean and consistent.
    Supports scheduled linting, git hooks, and real-time file watching.

Examples:
    mw lint start                   # Start scheduled linting
    mw lint scan --dir src          # Scan src directory
    mw lint watch --dir .           # Watch current directory
    mw lint install-hooks           # Add git hooks for auto-linting
""")
        return 0

    subcmd = args[0]
    remaining = args[1:]

    # Scheduled Auto-Linting Commands
    if subcmd == "start":
        # Use the new lint_watcher.py management tool
        watcher_script = TOOLS_DIR / "lint_watcher.py"
        if watcher_script.exists():
            result = subprocess.run([sys.executable, str(watcher_script), "start"])
            return result.returncode
        else:
            print("❌ Lint watcher tool not found")
            return 1

    elif subcmd == "stop":
        # Use the new lint_watcher.py management tool
        watcher_script = TOOLS_DIR / "lint_watcher.py"
        if watcher_script.exists():
            result = subprocess.run([sys.executable, str(watcher_script), "stop"])
            return result.returncode
        else:
            print("❌ Lint watcher tool not found")
            return 1

    elif subcmd == "status" or subcmd == "restart" or subcmd == "logs":
        # Use the new lint_watcher.py management tool
        watcher_script = TOOLS_DIR / "lint_watcher.py"
        if watcher_script.exists():
            result = subprocess.run([sys.executable, str(watcher_script), subcmd])
            return result.returncode
        else:
            print("❌ Lint watcher tool not found")
            return 1

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

    elif subcmd == "uninstall-hooks":
        print("🧹 Removing Git Hooks for Automatic Linting...")

        git_hooks_dir = MYWORK_ROOT / ".git" / "hooks"
        if not git_hooks_dir.exists():
            print("❌ Error: Not a git repository or .git/hooks directory not found")
            return 1

        removed = False
        for hook_name in ("pre-commit", "pre-push"):
            hook_path = git_hooks_dir / hook_name
            if hook_path.exists():
                hook_path.unlink()
                removed = True
                print(f"✅ Removed {hook_name}")

        if not removed:
            print("ℹ️  No linting hooks found to remove")
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


def cmd_ecosystem(args: Optional[List[str]] = None) -> None:
    """Show all live app URLs and ecosystem overview."""
    if args and (args[0] in ["--help", "-h"]):
        print("""
Ecosystem Commands — Live Apps & Services Overview
==================================================
Usage:
    mw ecosystem                    Show all live app URLs and ecosystem overview
    mw ecosystem --help             Show this help message

Description:
    Displays all live applications and services in the MyWork-AI ecosystem
    with direct links, descriptions, and connection information.

Examples:
    mw ecosystem                    # Show complete ecosystem overview
""")
        return 0
    
    print(f"""
{Colors.BOLD}{Colors.BLUE}🌐 MyWork-AI Ecosystem Overview{Colors.ENDC}
{Colors.BLUE}{'=' * 60}{Colors.ENDC}

{Colors.BOLD}{Colors.GREEN}🛒 Commerce Ecosystem{Colors.ENDC}
{Colors.GREEN}{'─' * 30}{Colors.ENDC}
{color("📱 Marketplace Frontend", Colors.BOLD)}
   🔗 {color("https://frontend-hazel-ten-17.vercel.app", Colors.BLUE)}
   💡 Buy/sell complete projects, browse marketplace

{color("⚙️ Marketplace Backend", Colors.BOLD)}
   🔗 {color("https://mywork-ai-production.up.railway.app", Colors.BLUE)}
   💡 API services, payment processing, MLM system

{Colors.BOLD}{Colors.YELLOW}📊 Analytics Ecosystem{Colors.ENDC}
{Colors.YELLOW}{'─' * 35}{Colors.ENDC}
{color("📈 Dashboard", Colors.BOLD)}
   🔗 {color("https://dashboard-sage-rho.vercel.app", Colors.BLUE)}
   💡 Project analytics and framework overview

{color("🤖 AI Dashboard", Colors.BOLD)}
   🔗 {color("https://ai-dashboard-frontend-rust.vercel.app", Colors.BLUE)}
   💡 AI performance metrics and AutoForge monitoring

{color("📋 Task Tracker", Colors.BOLD)}
   🔗 {color("https://task-tracker-weld-delta.vercel.app", Colors.BLUE)}
   💡 Project management and team collaboration

{Colors.BOLD}{Colors.BLUE}👥 User Ecosystem{Colors.ENDC}
{Colors.BLUE}{'─' * 25}{Colors.ENDC}
{color("👤 User Portal", Colors.BOLD)}
   🔗 {color("https://mywork-user.vercel.app", Colors.BLUE)}
   💡 Account management and user profiles

{color("⚙️ Admin Panel", Colors.BOLD)}
   🔗 {color("https://mywork-admin.vercel.app", Colors.BLUE)}
   💡 Platform administration and oversight

{Colors.BOLD}{Colors.HEADER}🎯 Built With MyWork-AI{Colors.ENDC}
{Colors.HEADER}{'─' * 35}{Colors.ENDC}
{color("🏈 SportsAI", Colors.BOLD)}
   🔗 {color("https://sports-ai-one.vercel.app", Colors.BLUE)}
   💡 AI-powered sports analytics (fullstack template)

{Colors.BOLD}{Colors.GREEN}🔧 Quick Access Commands{Colors.ENDC}
{Colors.GREEN}{'─' * 35}{Colors.ENDC}
   {color("mw marketplace", Colors.BOLD)}     # Marketplace info and links
   {color("mw dashboard", Colors.BOLD)}       # Open dashboard
   {color("mw links", Colors.BOLD)}           # All useful links

{Colors.BLUE}💡 All services work together to create a seamless development experience!{Colors.ENDC}
""")
    return 0


def cmd_marketplace_info(args: Optional[List[str]] = None) -> None:
    """Open marketplace information and links."""
    if args and (args[0] in ["--help", "-h"]):
        print("""
Marketplace Commands — Buy & Sell Projects
==========================================
Usage:
    mw marketplace                  Show marketplace information and links
    mw marketplace --help           Show this help message

Description:
    Provides detailed information about the MyWork-AI marketplace including
    how to buy/sell projects, pricing, and direct links to all marketplace
    services.

Examples:
    mw marketplace                  # Show marketplace overview
""")
        return 0
    
    print(f"""
{Colors.BOLD}{Colors.GREEN}🛒 MyWork-AI Marketplace{Colors.ENDC}
{Colors.GREEN}{'=' * 40}{Colors.ENDC}

{Colors.BOLD}🌟 What is the Marketplace?{Colors.ENDC}
Complete projects marketplace where developers buy and sell ready-to-deploy 
applications, components, and templates. Skip the boilerplate, start with 
proven solutions.

{Colors.BOLD}{Colors.BLUE}📱 Marketplace Frontend{Colors.ENDC}
{Colors.BLUE}{'─' * 30}{Colors.ENDC}
🔗 {color("https://frontend-hazel-ten-17.vercel.app", Colors.BLUE)}

✨ Features:
   • Browse complete projects and components
   • Credit-based payment system with Stripe  
   • Project ratings and reviews
   • Advanced search and filtering
   • Mobile-responsive design

{Colors.BOLD}{Colors.YELLOW}⚙️ Backend Services{Colors.ENDC}
{Colors.YELLOW}{'─' * 25}{Colors.ENDC}
🔗 {color("https://mywork-ai-production.up.railway.app", Colors.BLUE)}

🔧 API Features:
   • JWT authentication and authorization
   • Stripe payment processing
   • MLM referral system (5 levels)
   • Real-time analytics and reporting
   • Notification system

{Colors.BOLD}{Colors.HEADER}💰 How It Works{Colors.ENDC}
{Colors.HEADER}{'─' * 20}{Colors.ENDC}
{Colors.BOLD}For Buyers:{Colors.ENDC}
   1. Purchase credits with Stripe
   2. Browse verified projects
   3. Download source code + documentation
   4. Get 30-day support from seller

{Colors.BOLD}For Sellers:{Colors.ENDC}
   1. List your projects (free)
   2. Set credit pricing
   3. Earn 70% of sale price
   4. Build reputation with ratings
   5. Earn MLM referral commissions

{Colors.BOLD}{Colors.GREEN}🎯 MLM Referral System{Colors.ENDC}
{Colors.GREEN}{'─' * 30}{Colors.ENDC}
Earn from 5 levels of referrals:
   • Level 1 (Direct): {color("15%", Colors.BOLD)} commission
   • Level 2: {color("7%", Colors.BOLD)} commission  
   • Level 3: {color("4%", Colors.BOLD)} commission
   • Level 4: {color("2%", Colors.BOLD)} commission
   • Level 5: {color("2%", Colors.BOLD)} commission

{Colors.BOLD}{Colors.BLUE}🔗 Related Services{Colors.ENDC}
{Colors.BLUE}{'─' * 25}{Colors.ENDC}
   👤 User Portal: {color("https://mywork-user.vercel.app", Colors.BLUE)}
   ⚙️ Admin Panel: {color("https://mywork-admin.vercel.app", Colors.BLUE)}

{Colors.BOLD}{Colors.YELLOW}🚀 Getting Started{Colors.ENDC}
{Colors.YELLOW}{'─' * 25}{Colors.ENDC}
   1. Visit: {color("https://frontend-hazel-ten-17.vercel.app", Colors.BLUE)}
   2. Create account and verify email
   3. Purchase credits or list your first project
   4. Join the community of 1000+ developers!

{Colors.GREEN}💡 Pro tip: Use 'mw ecosystem' to see how marketplace connects with other services{Colors.ENDC}
""")
    return 0


def cmd_links(args: Optional[List[str]] = None) -> None:
    """Show all useful framework links."""
    if args and (args[0] in ["--help", "-h"]):
        print("""
Links Commands — All Useful Framework Links
===========================================
Usage:
    mw links                        Show all useful framework links
    mw links --help                 Show this help message

Description:
    Comprehensive list of all useful links related to the MyWork-AI
    framework including documentation, live apps, community resources,
    and development tools.

Examples:
    mw links                        # Show all links organized by category
""")
        return 0
    
    print(f"""
{Colors.BOLD}{Colors.BLUE}🔗 MyWork-AI Links Directory{Colors.ENDC}
{Colors.BLUE}{'=' * 45}{Colors.ENDC}

{Colors.BOLD}{Colors.GREEN}🌐 Live Applications{Colors.ENDC}
{Colors.GREEN}{'─' * 25}{Colors.ENDC}
📱 Marketplace      {color("https://frontend-hazel-ten-17.vercel.app", Colors.BLUE)}
📊 Dashboard        {color("https://dashboard-sage-rho.vercel.app", Colors.BLUE)}
📋 Task Tracker     {color("https://task-tracker-weld-delta.vercel.app", Colors.BLUE)}
👤 User Portal      {color("https://mywork-user.vercel.app", Colors.BLUE)}
⚙️ Admin Panel      {color("https://mywork-admin.vercel.app", Colors.BLUE)}
🤖 AI Dashboard     {color("https://ai-dashboard-frontend-rust.vercel.app", Colors.BLUE)}
🏈 SportsAI         {color("https://sports-ai-one.vercel.app", Colors.BLUE)}

{Colors.BOLD}{Colors.YELLOW}🔧 Backend Services{Colors.ENDC}
{Colors.YELLOW}{'─' * 25}{Colors.ENDC}
⚙️ API Backend      {color("https://mywork-ai-production.up.railway.app", Colors.BLUE)}

{Colors.BOLD}{Colors.HEADER}📚 Documentation{Colors.ENDC}
{Colors.HEADER}{'─' * 20}{Colors.ENDC}
📖 README.md        Complete framework overview
⚡ QUICK_START.md   Get started in 3 steps  
🏛️ ECOSYSTEM.md     Ecosystem architecture
🤖 CLAUDE.md        Master orchestrator instructions
📝 CHANGELOG.md     Version history and updates
🔒 SECURITY.md      Security policy and reporting
🤝 CONTRIBUTING.md  Contribution guidelines
🎯 STRATEGY.md      Project strategy and roadmap

{Colors.BOLD}{Colors.BLUE}🌍 Community & Support{Colors.ENDC}
{Colors.BLUE}{'─' * 30}{Colors.ENDC}
🐙 GitHub Repository   {color("https://github.com/DansiDanutz/MyWork-AI", Colors.BLUE)}
💬 Discussions         {color("https://github.com/DansiDanutz/MyWork-AI/discussions", Colors.BLUE)}
🐛 Issues              {color("https://github.com/DansiDanutz/MyWork-AI/issues", Colors.BLUE)}
📦 PyPI Package        {color("https://pypi.org/project/mywork-ai/", Colors.BLUE)}

{Colors.BOLD}{Colors.GREEN}🎨 Frontend & Landing{Colors.ENDC}
{Colors.GREEN}{'─' * 30}{Colors.ENDC}
🏠 Landing Page        {color("file://docs/landing/index.html", Colors.BLUE)}
   (Open locally or serve with: python -m http.server 8000)

{Colors.BOLD}{Colors.YELLOW}🛠️ Development Tools{Colors.ENDC}
{Colors.YELLOW}{'─' * 25}{Colors.ENDC}
📊 Framework Health    {color("mw status", Colors.BOLD)}
🔍 Diagnostics        {color("mw doctor", Colors.BOLD)}
📈 Dashboard          {color("mw dashboard", Colors.BOLD)}
🧠 Brain Search       {color("mw brain search <query>", Colors.BOLD)}
🤖 AutoForge          {color("mw af status", Colors.BOLD)}

{Colors.BOLD}{Colors.RED}⚡ Quick Commands{Colors.ENDC}
{Colors.RED}{'─' * 20}{Colors.ENDC}
{color("mw ecosystem", Colors.BOLD)}         # Complete ecosystem overview
{color("mw marketplace", Colors.BOLD)}      # Marketplace details
{color("mw setup", Colors.BOLD)}            # First-time setup
{color("mw guide", Colors.BOLD)}            # Interactive tutorial
{color("mw help", Colors.BOLD)}             # CLI help

{Colors.GREEN}💡 Bookmark these links for easy access to the MyWork-AI ecosystem!{Colors.ENDC}
""")
    return 0


def cmd_setup(args: Optional[List[str]] = None) -> None:
    """Setup command for first-time users."""
    if args and (args[0] in ["--help", "-h"]):
        print("""
Setup Commands — First-Time Setup Guide
=======================================
Usage:
    mw setup                        Run first-time setup wizard
    mw setup --help                 Show this help message

Description:
    Guides new users through initial MyWork framework setup including:
    • Welcome message and introduction
    • Python version verification (>= 3.11)
    • Environment file setup (.env)
    • Planning directory creation
    • Basic health check
    • Next steps guidance

Examples:
    mw setup                        # Run setup wizard
""")
        return 0
        
    import sys
    import platform
    from pathlib import Path
    
    # ASCII Art Welcome
    print(f"""
{Colors.BOLD}{Colors.BLUE}
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║    ███╗   ███╗██╗   ██╗██╗    ██╗ ██████╗ ██████╗ ██╗  ██╗          ║
║    ████╗ ████║╚██╗ ██╔╝██║    ██║██╔═══██╗██╔══██╗██║ ██╔╝          ║
║    ██╔████╔██║ ╚████╔╝ ██║ █╗ ██║██║   ██║██████╔╝█████╔╝           ║
║    ██║╚██╔╝██║  ╚██╔╝  ██║███╗██║██║   ██║██╔══██╗██╔═██╗           ║
║    ██║ ╚═╝ ██║   ██║   ╚███╔███╔╝╚██████╔╝██║  ██║██║  ██╗          ║
║    ╚═╝     ╚═╝   ╚═╝    ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝          ║
║                                                                      ║
║                  Welcome to the MyWork-AI Framework!                 ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
{Colors.ENDC}

{Colors.BOLD}🚀 Let's get you set up for productive development!{Colors.ENDC}
""")
    
    print(f"{Colors.BOLD}Step 1: Python Version Check{Colors.ENDC}")
    print("=" * 40)
    
    python_version = sys.version_info
    if python_version >= (3, 11):
        print(f"{Colors.GREEN}✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} detected (>= 3.11 required){Colors.ENDC}")
    else:
        print(f"{Colors.RED}❌ Python {python_version.major}.{python_version.minor}.{python_version.micro} detected{Colors.ENDC}")
        print(f"{Colors.RED}   MyWork requires Python 3.11 or higher{Colors.ENDC}")
        print(f"{Colors.YELLOW}   Please upgrade Python before continuing{Colors.ENDC}")
        return 1
    
    print(f"\n{Colors.BOLD}Step 2: Environment File Check{Colors.ENDC}")
    print("=" * 40)
    
    env_file = MYWORK_ROOT / ".env"
    env_example = MYWORK_ROOT / ".env.example"
    
    if env_file.exists():
        print(f"{Colors.GREEN}✅ .env file already exists{Colors.ENDC}")
    elif env_example.exists():
        print(f"{Colors.YELLOW}⚠️  Creating .env file from template{Colors.ENDC}")
        env_file.write_text(env_example.read_text())
        print(f"{Colors.GREEN}✅ .env file created from .env.example{Colors.ENDC}")
        print(f"{Colors.BLUE}💡 Edit .env to add your API keys and configuration{Colors.ENDC}")
    else:
        print(f"{Colors.YELLOW}⚠️  Creating basic .env file{Colors.ENDC}")
        env_content = """# MyWork-AI Environment Configuration
# Add your API keys and settings here

# OpenAI API Key (optional)
# OPENAI_API_KEY=your_key_here

# Other API keys as needed
"""
        env_file.write_text(env_content)
        print(f"{Colors.GREEN}✅ Basic .env file created{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}Step 3: Planning Directory Check{Colors.ENDC}")
    print("=" * 40)
    
    planning_dir = MYWORK_ROOT / ".planning"
    if planning_dir.exists():
        print(f"{Colors.GREEN}✅ .planning directory exists{Colors.ENDC}")
    else:
        print(f"{Colors.YELLOW}⚠️  Creating .planning directory{Colors.ENDC}")
        planning_dir.mkdir(exist_ok=True)
        (planning_dir / "config").mkdir(exist_ok=True)
        print(f"{Colors.GREEN}✅ .planning directory created{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}Step 4: Quick Health Check{Colors.ENDC}")
    print("=" * 40)
    
    # Run a basic health check
    tools_check = []
    essential_tools = ["brain.py", "health_check.py", "scaffold.py"]
    
    for tool in essential_tools:
        tool_path = TOOLS_DIR / tool
        if tool_path.exists():
            tools_check.append(f"{Colors.GREEN}✅ {tool}{Colors.ENDC}")
        else:
            tools_check.append(f"{Colors.RED}❌ {tool}{Colors.ENDC}")
    
    for check in tools_check:
        print(f"   {check}")
    
    print(f"\n{Colors.BOLD}Step 5: Next Steps{Colors.ENDC}")
    print("=" * 40)
    print(f"""
{Colors.GREEN}🎉 Setup complete! Here's what to do next:{Colors.ENDC}

{Colors.BOLD}1. Explore the framework:{Colors.ENDC}
   mw dashboard              # See framework overview
   mw status                 # Check health status
   mw guide                  # Interactive workflow guide

{Colors.BOLD}2. Create your first project:{Colors.ENDC}
   mw new my-first-app       # Create a basic project
   mw new api-server fastapi # Create a FastAPI project

{Colors.BOLD}3. Learn about the Brain:{Colors.ENDC}
   mw brain --help           # Knowledge management
   mw brain stats            # See brain statistics

{Colors.BOLD}4. Try AutoForge (optional):{Colors.ENDC}
   mw af --help              # Autonomous coding assistant

{Colors.BLUE}💡 Run 'mw help' anytime to see all available commands{Colors.ENDC}
{Colors.BLUE}🔗 Visit the marketplace to share your projects{Colors.ENDC}

{Colors.BOLD}Happy coding with MyWork-AI! 🚀{Colors.ENDC}
""")
    
    return 0


def cmd_guide(args: Optional[List[str]] = None) -> None:
    """Interactive guide showing the full workflow."""
    if args and (args[0] in ["--help", "-h"]):
        print("""
Guide Commands — Interactive Workflow Guide
===========================================
Usage:
    mw guide                        Show complete workflow guide
    mw guide --help                 Show this help message

Description:
    Interactive guide that walks you through the complete MyWork workflow
    from project creation to marketplace listing. Perfect for learning
    the framework or as a quick reference.

Examples:
    mw guide                        # Show full workflow guide
""")
        return 0
        
    print(f"""
{Colors.BOLD}{Colors.BLUE}MyWork Framework — Getting Started Guide{Colors.ENDC}
{Colors.BLUE}{'=' * 50}{Colors.ENDC}

{Colors.BOLD}🎯 The MyWork Philosophy{Colors.ENDC}
Build once, build right. The MyWork framework guides you through a proven
workflow that ensures quality, maintainability, and success.

{Colors.BOLD}{Colors.GREEN}Step 1: Create a project{Colors.ENDC}
{Colors.GREEN}{'─' * 30}{Colors.ENDC}
Start with a solid foundation using our project scaffolding:

   {Colors.BOLD}$ mw new my-app fullstack{Colors.ENDC}
   
   Available templates:
   • {Colors.BLUE}basic{Colors.ENDC}      - Simple project structure
   • {Colors.BLUE}fastapi{Colors.ENDC}    - FastAPI web service
   • {Colors.BLUE}nextjs{Colors.ENDC}     - Next.js web application  
   • {Colors.BLUE}fullstack{Colors.ENDC} - Complete web application
   • {Colors.BLUE}cli{Colors.ENDC}        - Command-line tool
   • {Colors.BLUE}automation{Colors.ENDC} - Scripting/automation project

{Colors.BOLD}{Colors.GREEN}Step 2: Plan your project (GSD){Colors.ENDC}
{Colors.GREEN}{'─' * 40}{Colors.ENDC}
Review and customize the auto-generated planning documents:

   📁 .planning/PROJECT.md    - Project overview and goals
   📁 .planning/ROADMAP.md    - Phase-by-phase development plan
   
   The GSD (Get Stuff Done) system breaks your project into manageable phases,
   each with clear objectives and deliverables.

{Colors.BOLD}{Colors.GREEN}Step 3: Execute phases{Colors.ENDC}
{Colors.GREEN}{'─' * 25}{Colors.ENDC}
Work through each phase systematically:

   {Colors.BOLD}Phase 1{Colors.ENDC}: Foundation & Setup
   {Colors.BOLD}Phase 2{Colors.ENDC}: Core Features
   {Colors.BOLD}Phase 3{Colors.ENDC}: Advanced Features  
   {Colors.BOLD}Phase 4{Colors.ENDC}: Testing & Polish
   {Colors.BOLD}Phase 5{Colors.ENDC}: Deployment & Documentation

   Track progress with: {Colors.BOLD}mw status{Colors.ENDC}

{Colors.BOLD}{Colors.GREEN}Step 4: AutoForge (optional){Colors.ENDC}
{Colors.GREEN}{'─' * 35}{Colors.ENDC}
For complex builds, let AutoForge handle autonomous coding:

   {Colors.BOLD}$ mw af start my-app{Colors.ENDC}
   
   AutoForge can:
   • Write boilerplate code
   • Implement standard patterns
   • Handle repetitive tasks
   • Follow best practices automatically

{Colors.BOLD}{Colors.GREEN}Step 5: Knowledge Management{Colors.ENDC}
{Colors.GREEN}{'─' * 40}{Colors.ENDC}
Capture learnings in your personal Brain:

   {Colors.BOLD}$ mw brain add "Always validate input data"{Colors.ENDC}
   {Colors.BOLD}$ mw brain search "validation"{Colors.ENDC}
   
   The Brain learns from your work and helps you avoid repeating mistakes.

{Colors.BOLD}{Colors.GREEN}Step 6: Quality Assurance{Colors.ENDC}
{Colors.GREEN}{'─' * 35}{Colors.ENDC}
Ensure code quality with automated linting:

   {Colors.BOLD}$ mw lint scan{Colors.ENDC}        # Check for issues
   {Colors.BOLD}$ mw lint fix{Colors.ENDC}         # Auto-fix problems
   {Colors.BOLD}$ mw lint watch{Colors.ENDC}       # Continuous monitoring

{Colors.BOLD}{Colors.GREEN}Step 7: Marketplace (optional){Colors.ENDC}
{Colors.GREEN}{'─' * 40}{Colors.ENDC}
Share your finished project with the community:

   🛒 List on the MyWork marketplace
   🧠 Contribute learnings to shared knowledge
   📈 Build your developer profile

{Colors.BOLD}{Colors.BLUE}🔄 Continuous Improvement{Colors.ENDC}
{Colors.BLUE}{'─' * 35}{Colors.ENDC}
• Use {Colors.BOLD}mw brain learn{Colors.ENDC} for daily learning extraction
• Run {Colors.BOLD}mw doctor{Colors.ENDC} for health checks  
• Keep {Colors.BOLD}mw dashboard{Colors.ENDC} bookmarked for quick overview

{Colors.BOLD}{Colors.YELLOW}🚀 Ready to start? Try these commands:{Colors.ENDC}

   {Colors.BOLD}mw setup{Colors.ENDC}              # First-time setup
   {Colors.BOLD}mw new tutorial basic{Colors.ENDC} # Create practice project
   {Colors.BOLD}mw dashboard{Colors.ENDC}          # Monitor progress

{Colors.BOLD}Happy building with MyWork-AI! 🎉{Colors.ENDC}
""")
    
    return 0


def cmd_prompt_enhance(args: List[str]) -> None:
    """Enhance user prompts for GSD."""
    if not args or (len(args) == 1 and args[0] in ["--help", "-h"]):
        print("""
Prompt Enhancement — GSD Prompt Optimizer
=========================================
Usage:
    mw prompt-enhance <prompt>      Enhance a rough prompt for GSD
    mw prompt-enhance --help        Show this help message

Description:
    Takes a rough user prompt and enhances it with detailed requirements,
    tech stack suggestions, feature specifications, and constraints.
    Saves the enhanced prompt to .planning/ENHANCED_PROMPT.md for use
    with GSD project planning.

Examples:
    mw prompt-enhance "build me a todo app"
    mw prompt-enhance "create an API for user management"
    mw prompt-enhance "I need a dashboard for analytics"
""")
        return 0
        
    if args[0] in ["--help", "-h"]:
        return 0
        
    prompt = " ".join(args)
    
    print(f"\n{Colors.BOLD}🔧 Enhancing your prompt...{Colors.ENDC}")
    print(f"Original: {Colors.BLUE}{prompt}{Colors.ENDC}\n")
    
    # Enhanced prompt template
    enhanced_prompt = f"""# Enhanced Project Prompt

## Original Request
{prompt}

## Enhanced Requirements

### Core Functionality
- **Primary Purpose**: [Define the main goal and user needs]
- **Key Features**: 
  - Feature 1: [Detailed description]
  - Feature 2: [Detailed description]  
  - Feature 3: [Detailed description]
- **User Stories**:
  - As a [user type], I want to [action] so that [benefit]
  - As a [user type], I want to [action] so that [benefit]

### Technical Specifications

#### Recommended Tech Stack
- **Frontend**: [React, Vue.js, Next.js, or plain HTML/CSS/JS]
- **Backend**: [FastAPI, Express.js, Django, or serverless]
- **Database**: [PostgreSQL, MongoDB, SQLite, or file-based]
- **Authentication**: [JWT, OAuth, or simple sessions]
- **Deployment**: [Vercel, Heroku, Docker, or VPS]

#### Architecture Patterns
- **Structure**: [MVC, microservices, monolithic, or serverless]
- **API Design**: [REST, GraphQL, or RPC]
- **State Management**: [Context, Redux, Vuex, or local state]

### Development Constraints

#### Performance Requirements
- **Response Time**: < 200ms for API calls
- **Load Capacity**: Support X concurrent users
- **Browser Support**: Modern browsers (Chrome, Firefox, Safari, Edge)

#### Security Considerations
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- HTTPS/TLS encryption
- Rate limiting for APIs

#### Quality Standards
- **Code Coverage**: Minimum 80% test coverage
- **Documentation**: API docs and user guides
- **Error Handling**: Graceful error messages
- **Logging**: Comprehensive activity logging

### Project Phases

#### Phase 1: Foundation (Week 1)
- Project setup and configuration
- Basic project structure
- Database schema design
- Authentication system

#### Phase 2: Core Features (Week 2-3)
- Main functionality implementation
- Basic UI/UX design
- API development
- Core business logic

#### Phase 3: Advanced Features (Week 4)
- Additional features and enhancements
- UI polishing and responsiveness
- Performance optimization
- Integration testing

#### Phase 4: Testing & Polish (Week 5)
- Comprehensive testing (unit, integration, E2E)
- Bug fixes and refinements
- Security audit
- Performance tuning

#### Phase 5: Deployment & Documentation (Week 6)
- Production deployment setup
- User documentation
- API documentation
- Monitoring and analytics setup

### Success Criteria
- [ ] All core features implemented and tested
- [ ] Application is responsive and user-friendly
- [ ] Performance meets specified requirements
- [ ] Security best practices implemented
- [ ] Documentation is complete and accurate
- [ ] Successfully deployed to production

### Additional Considerations
- **Scalability**: Plan for future growth
- **Maintenance**: Easy to update and maintain
- **Accessibility**: WCAG 2.1 AA compliance
- **Analytics**: Track user engagement and performance
- **Backup & Recovery**: Data protection strategies

## Next Steps
1. Review and customize this enhanced prompt
2. Create project: `mw new project-name template-name`
3. Update .planning/PROJECT.md with these requirements
4. Begin Phase 1 development
"""

    # Save enhanced prompt
    planning_dir = MYWORK_ROOT / ".planning"
    planning_dir.mkdir(exist_ok=True)
    
    enhanced_file = planning_dir / "ENHANCED_PROMPT.md"
    enhanced_file.write_text(enhanced_prompt)
    
    print(f"{Colors.GREEN}✅ Enhanced prompt saved to: {enhanced_file}{Colors.ENDC}")
    print(f"{Colors.BLUE}📝 Review and customize the enhanced requirements{Colors.ENDC}")
    print(f"{Colors.BLUE}🚀 Ready to create your project with: mw new <name> <template>{Colors.ENDC}")
    
    # Show preview of enhancement
    print(f"\n{Colors.BOLD}Preview of enhancement:{Colors.ENDC}")
    print("-" * 50)
    lines = enhanced_prompt.split('\n')
    for i, line in enumerate(lines[:20]):  # Show first 20 lines
        print(line)
    if len(lines) > 20:
        print(f"... {len(lines) - 20} more lines in {enhanced_file}")
    
    return 0


def cmd_init(args: List[str] = None):
    """Initialize current directory as a MyWork project."""
    import datetime
    if args and (args[0] in ["--help", "-h"]):
        print("""
Init Commands — Initialize MyWork Project
========================================
Usage:
    mw init                         Initialize current directory as MyWork project
    mw init --help                  Show this help message

Description:
    Initialize the current directory as a MyWork project by creating:
    • .mw/ configuration directory
    • .env environment file
    • README.md template
    • Basic project structure

Examples:
    mw init                         # Initialize current directory
""")
        return 0
        
    current_dir = Path.cwd()
    print(f"{Colors.BOLD}🚀 Initializing MyWork project in: {current_dir}{Colors.ENDC}")
    
    # Create .mw config directory
    mw_dir = current_dir / ".mw"
    mw_dir.mkdir(exist_ok=True)
    
    # Create config file
    config_content = {
        "project_name": current_dir.name,
        "created_at": str(datetime.datetime.now()),
        "version": "1.0.0",
        "type": "basic",
        "brain_enabled": True,
        "autoforge_enabled": True
    }
    
    config_file = mw_dir / "config.json"
    config_file.write_text(json.dumps(config_content, indent=2))
    print(f"   ✅ Created .mw/config.json")
    
    # Create .env if it doesn't exist
    env_file = current_dir / ".env"
    if not env_file.exists():
        env_content = """# MyWork Project Environment Variables
# Add your API keys and configuration here

# Development settings
DEBUG=true
ENVIRONMENT=development

# API Keys (optional)
# OPENAI_API_KEY=your_key_here
"""
        env_file.write_text(env_content)
        print(f"   ✅ Created .env file")
    else:
        print(f"   ⚪ .env already exists")
    
    # Create README template if it doesn't exist
    readme_file = current_dir / "README.md"
    if not readme_file.exists():
        readme_content = f"""# {current_dir.name}

A MyWork-AI project.

## Getting Started

This project was initialized with MyWork-AI framework.

### Prerequisites

- Python 3.11+
- MyWork-AI framework: `pip install mywork-ai`

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd {current_dir.name}

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env  # Edit with your settings
```

### Usage

```bash
# Start development
mw status          # Check project health
mw brain --help    # Knowledge management
mw af start .      # Start AutoForge (optional)
```

### MyWork Commands

- `mw status` - Check project health
- `mw brain search <query>` - Search knowledge base
- `mw lint scan` - Code quality check
- `mw dashboard` - Framework overview

## Contributing

This project follows MyWork-AI best practices. See `mw guide` for the complete workflow.

## License

MIT License - see LICENSE file for details.
"""
        readme_file.write_text(readme_content)
        print(f"   ✅ Created README.md template")
    else:
        print(f"   ⚪ README.md already exists")
    
    # Create gitignore if it doesn't exist
    gitignore_file = current_dir / ".gitignore"
    if not gitignore_file.exists():
        gitignore_content = """# MyWork-AI project gitignore

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.env
.venv
env.bak/
venv.bak/

# MyWork
.mw/cache/
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Dependencies
node_modules/
npm-debug.log
yarn-error.log

# Build outputs
dist/
build/
*.egg-info/
"""
        gitignore_file.write_text(gitignore_content)
        print(f"   ✅ Created .gitignore")
    else:
        print(f"   ⚪ .gitignore already exists")
    
    print(f"\n{Colors.GREEN}🎉 Project initialized successfully!{Colors.ENDC}")
    print(f"{Colors.BLUE}Next steps:{Colors.ENDC}")
    print(f"   • Run 'mw status' to check project health")
    print(f"   • Run 'mw guide' for workflow guidance")
    print(f"   • Edit .env with your configuration")
    
    return 0


def cmd_stats(args: List[str] = None):
    """Show framework-wide statistics."""
    if args and (args[0] in ["--help", "-h"]):
        print("""
Stats Commands — Framework Statistics
====================================
Usage:
    mw stats                        Show framework-wide statistics
    mw stats --help                 Show this help message

Description:
    Displays comprehensive statistics about your MyWork framework including:
    • Total projects count
    • Brain entries count
    • Lines of code across all projects
    • Git commits count
    • Framework usage metrics

Examples:
    mw stats                        # Show all statistics
""")
        return 0
    
    print(f"{Colors.BOLD}{Colors.BLUE}📊 MyWork-AI Framework Statistics{Colors.ENDC}")
    print(f"{Colors.BLUE}{'=' * 50}{Colors.ENDC}")
    
    stats = {}
    
    # Count projects
    if PROJECTS_DIR.exists():
        projects = [p for p in PROJECTS_DIR.iterdir() if p.is_dir() and not p.name.startswith('.')]
        stats['projects'] = len(projects)
    else:
        stats['projects'] = 0
    
    # Count brain entries
    brain_file = MYWORK_ROOT / "tools" / "brain_data.json"
    if brain_file.exists():
        try:
            brain_data = json.loads(brain_file.read_text())
            stats['brain_entries'] = len(brain_data.get('entries', []))
        except:
            stats['brain_entries'] = 0
    else:
        stats['brain_entries'] = 0
    
    # Count lines of code (Python files only for performance)
    total_lines = 0
    total_files = 0
    
    for root, dirs, files in os.walk(MYWORK_ROOT):
        # Skip certain directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', 'env']]
        
        for file in files:
            if file.endswith(('.py', '.js', '.jsx', '.ts', '.tsx', '.vue', '.md')):
                file_path = Path(root) / file
                try:
                    lines = len(file_path.read_text().splitlines())
                    total_lines += lines
                    total_files += 1
                except:
                    continue
    
    stats['total_lines'] = total_lines
    stats['total_files'] = total_files
    
    # Count git commits
    try:
        result = subprocess.run(
            ['git', 'rev-list', '--count', 'HEAD'],
            cwd=MYWORK_ROOT,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            stats['git_commits'] = int(result.stdout.strip())
        else:
            stats['git_commits'] = 0
    except:
        stats['git_commits'] = 0
    
    # Framework size
    try:
        result = subprocess.run(['du', '-sh', str(MYWORK_ROOT)], capture_output=True, text=True)
        if result.returncode == 0:
            stats['framework_size'] = result.stdout.split()[0]
        else:
            stats['framework_size'] = 'Unknown'
    except:
        stats['framework_size'] = 'Unknown'
    
    # Display stats in a nice format
    def stat_line(icon, label, value, color=Colors.GREEN):
        return f"   {icon} {Colors.BOLD}{label}:{Colors.ENDC} {color}{value}{Colors.ENDC}"
    
    print(stat_line("📁", "Total Projects", stats['projects']))
    print(stat_line("🧠", "Brain Entries", stats['brain_entries']))
    print(stat_line("📄", "Total Files", stats['total_files']))
    print(stat_line("📝", "Lines of Code", f"{stats['total_lines']:,}"))
    print(stat_line("🔄", "Git Commits", stats['git_commits']))
    print(stat_line("💽", "Framework Size", stats['framework_size']))
    
    # Calculate some metrics
    if stats['projects'] > 0:
        avg_lines_per_project = stats['total_lines'] // stats['projects']
        print(stat_line("📊", "Avg Lines/Project", f"{avg_lines_per_project:,}", Colors.BLUE))
    
    if stats['git_commits'] > 0 and stats['projects'] > 0:
        avg_commits_per_project = stats['git_commits'] // stats['projects']
        print(stat_line("⚡", "Avg Commits/Project", avg_commits_per_project, Colors.BLUE))
    
    print(f"\n{Colors.BLUE}💡 Use 'mw dashboard' for detailed project overview{Colors.ENDC}")
    return 0


def cmd_clean(args: List[str] = None):
    """Clean temporary files across all projects."""
    if args and (args[0] in ["--help", "-h"]):
        print("""
Clean Commands — Clean Temporary Files
=====================================
Usage:
    mw clean                        Clean all temporary files
    mw clean --help                 Show this help message

Description:
    Recursively clean temporary files and directories from all projects:
    • __pycache__/ directories
    • .pytest_cache/ directories
    • node_modules/ directories (with --deep flag)
    • dist/ and build/ directories
    • *.pyc, *.pyo files
    • .DS_Store files

Examples:
    mw clean                        # Clean temp files (safe)
    mw clean --deep                 # Also remove node_modules
    mw clean --dry-run              # Show what would be cleaned
""")
        return 0
    
    import shutil
    
    deep_clean = "--deep" in args
    dry_run = "--dry-run" in args
    
    print(f"{Colors.BOLD}🧹 Cleaning temporary files{' (deep mode)' if deep_clean else ''}...{Colors.ENDC}")
    if dry_run:
        print(f"{Colors.YELLOW}🔍 DRY RUN - showing what would be cleaned{Colors.ENDC}")
    
    cleaned_items = []
    saved_space = 0
    
    # Directories to clean
    temp_dirs = ["__pycache__", ".pytest_cache", "dist", "build", ".coverage"]
    if deep_clean:
        temp_dirs.append("node_modules")
    
    # File patterns to clean
    temp_files = ["*.pyc", "*.pyo", "*.pyd", ".DS_Store", "Thumbs.db", "*.log"]
    
    def get_dir_size(path):
        """Get directory size in bytes."""
        total = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.exists(fp):
                        total += os.path.getsize(fp)
        except:
            pass
        return total
    
    def format_bytes(bytes_val):
        """Format bytes to human readable."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.1f}{unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.1f}TB"
    
    # Clean directories
    for root, dirs, files in os.walk(MYWORK_ROOT):
        # Skip .git directories
        dirs[:] = [d for d in dirs if d != '.git']
        
        for dir_name in dirs[:]:  # Create copy to safely modify
            if dir_name in temp_dirs:
                dir_path = Path(root) / dir_name
                if dir_path.exists():
                    size = get_dir_size(dir_path)
                    if dry_run:
                        print(f"   🗂️  Would remove: {dir_path} ({format_bytes(size)})")
                        cleaned_items.append(dir_path)
                        saved_space += size
                    else:
                        try:
                            shutil.rmtree(dir_path)
                            print(f"   ✅ Removed: {dir_path} ({format_bytes(size)})")
                            cleaned_items.append(dir_path)
                            saved_space += size
                        except Exception as e:
                            print(f"   ❌ Failed to remove {dir_path}: {e}")
    
    # Clean individual files
    for pattern in temp_files:
        for file_path in Path(MYWORK_ROOT).rglob(pattern):
            # Skip .git directories
            if '.git' in file_path.parts:
                continue
            
            try:
                size = file_path.stat().st_size
                if dry_run:
                    print(f"   📄 Would remove: {file_path} ({format_bytes(size)})")
                    cleaned_items.append(file_path)
                    saved_space += size
                else:
                    file_path.unlink()
                    print(f"   ✅ Removed: {file_path} ({format_bytes(size)})")
                    cleaned_items.append(file_path)
                    saved_space += size
            except Exception as e:
                if not dry_run:
                    print(f"   ❌ Failed to remove {file_path}: {e}")
    
    # Summary
    print(f"\n{Colors.BOLD}📊 Cleanup Summary:{Colors.ENDC}")
    print(f"   Items {'would be ' if dry_run else ''}cleaned: {Colors.GREEN}{len(cleaned_items)}{Colors.ENDC}")
    print(f"   Space {'would be ' if dry_run else ''}freed: {Colors.GREEN}{format_bytes(saved_space)}{Colors.ENDC}")
    
    if not dry_run and saved_space > 0:
        print(f"{Colors.GREEN}✅ Cleanup completed successfully!{Colors.ENDC}")
    elif dry_run:
        print(f"{Colors.BLUE}💡 Run 'mw clean' without --dry-run to actually clean{Colors.ENDC}")
    
    return 0


def cmd_backup(args: List[str] = None):
    """Backup all projects and brain data."""
    if args and (args[0] in ["--help", "-h"]):
        print("""
Backup Commands — Framework Backup
==================================
Usage:
    mw backup                       Create timestamped backup
    mw backup --help                Show this help message

Description:
    Creates a timestamped archive containing:
    • All projects in /projects
    • Brain data and configuration
    • Framework configuration
    • Environment files (sanitized)

Examples:
    mw backup                       # Create backup archive
""")
        return 0
    
    import shutil
    import tempfile
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"mywork_backup_{timestamp}"
    
    print(f"{Colors.BOLD}📦 Creating MyWork-AI backup: {backup_name}{Colors.ENDC}")
    
    # Create backups directory if it doesn't exist
    backups_dir = MYWORK_ROOT / "backups"
    backups_dir.mkdir(exist_ok=True)
    
    backup_path = backups_dir / f"{backup_name}.zip"
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / backup_name
            temp_path.mkdir()
            
            # Backup projects
            if PROJECTS_DIR.exists():
                projects_backup = temp_path / "projects"
                shutil.copytree(PROJECTS_DIR, projects_backup)
                print(f"   ✅ Backed up projects directory")
            
            # Backup brain data
            brain_files = ["brain_data.json", "brain.py"]
            for brain_file in brain_files:
                brain_path = TOOLS_DIR / brain_file
                if brain_path.exists():
                    shutil.copy2(brain_path, temp_path)
                    print(f"   ✅ Backed up {brain_file}")
            
            # Backup configuration
            config_dirs = [".planning", "tools"]
            for config_dir in config_dirs:
                source = MYWORK_ROOT / config_dir
                if source.exists():
                    dest = temp_path / config_dir
                    shutil.copytree(source, dest)
                    print(f"   ✅ Backed up {config_dir}")
            
            # Backup environment (sanitized)
            env_file = MYWORK_ROOT / ".env"
            if env_file.exists():
                env_content = env_file.read_text()
                # Sanitize by removing sensitive values
                sanitized_lines = []
                for line in env_content.split('\n'):
                    if '=' in line and not line.strip().startswith('#'):
                        key, _ = line.split('=', 1)
                        sanitized_lines.append(f"{key}=YOUR_VALUE_HERE")
                    else:
                        sanitized_lines.append(line)
                
                sanitized_env = temp_path / ".env.template"
                sanitized_env.write_text('\n'.join(sanitized_lines))
                print(f"   ✅ Backed up .env (sanitized)")
            
            # Create metadata
            metadata = {
                "backup_created": datetime.now().isoformat(),
                "mywork_root": str(MYWORK_ROOT),
                "backup_version": "1.0",
                "included_items": [
                    "projects/",
                    "brain_data.json",
                    ".planning/",
                    "tools/",
                    ".env (sanitized)"
                ]
            }
            
            metadata_file = temp_path / "backup_metadata.json"
            metadata_file.write_text(json.dumps(metadata, indent=2))
            print(f"   ✅ Created backup metadata")
            
            # Create zip archive
            shutil.make_archive(str(backup_path.with_suffix('')), 'zip', temp_dir)
            
        file_size = backup_path.stat().st_size
        size_mb = file_size / (1024 * 1024)
        
        print(f"\n{Colors.GREEN}📦 Backup created successfully!{Colors.ENDC}")
        print(f"   📁 File: {backup_path}")
        print(f"   📊 Size: {size_mb:.1f} MB")
        
        # Clean old backups (keep last 5)
        backup_files = sorted(backups_dir.glob("mywork_backup_*.zip"))
        if len(backup_files) > 5:
            for old_backup in backup_files[:-5]:
                old_backup.unlink()
                print(f"   🗑️  Cleaned old backup: {old_backup.name}")
        
        return 0
        
    except Exception as e:
        print(f"{Colors.RED}❌ Backup failed: {e}{Colors.ENDC}")
        return 1


def cmd_changelog(args: List[str] = None):
    """Generate changelog from git commits."""
    if args and (args[0] in ["--help", "-h"]):
        print("""
Changelog Commands — Auto-generate Changelog
============================================
Usage:
    mw changelog                    Generate changelog from git commits
    mw changelog --help             Show this help message

Description:
    Automatically generates a changelog from git commits using conventional
    commit format. Supports feat:, fix:, docs:, style:, refactor:, test:, chore:

Examples:
    mw changelog                    # Generate and save changelog
""")
        return 0
    
    from datetime import datetime
    
    print(f"{Colors.BOLD}📝 Generating changelog from git commits...{Colors.ENDC}")
    
    try:
        # Get git log with format
        result = subprocess.run([
            'git', 'log', '--pretty=format:%H|%s|%ad|%an', '--date=short'
        ], cwd=MYWORK_ROOT, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"{Colors.RED}❌ Error getting git log: {result.stderr}{Colors.ENDC}")
            return 1
        
        commits = result.stdout.strip().split('\n')
        if not commits or commits == ['']:
            print(f"{Colors.YELLOW}⚠️  No git commits found{Colors.ENDC}")
            return 0
        
        # Parse commits
        changes = {
            'feat': [],
            'fix': [],
            'docs': [],
            'style': [],
            'refactor': [],
            'test': [],
            'chore': [],
            'other': []
        }
        
        for commit in commits:
            if '|' not in commit:
                continue
                
            hash_id, message, date, author = commit.split('|', 3)
            
            # Parse conventional commit format
            commit_type = 'other'
            if ':' in message:
                prefix = message.split(':', 1)[0].lower()
                if prefix in changes:
                    commit_type = prefix
                    message = message.split(':', 1)[1].strip()
            
            changes[commit_type].append({
                'hash': hash_id[:8],
                'message': message,
                'date': date,
                'author': author
            })
        
        # Generate changelog
        changelog_content = f"""# Changelog

All notable changes to MyWork-AI will be documented in this file.

*Generated automatically from git commits on {datetime.now().strftime('%Y-%m-%d')}*

## [Unreleased]

"""
        
        # Add sections for each type
        sections = {
            'feat': '### ✨ Features',
            'fix': '### 🐛 Bug Fixes',
            'docs': '### 📚 Documentation',
            'style': '### 💄 Styling',
            'refactor': '### ♻️ Refactoring',
            'test': '### ✅ Testing',
            'chore': '### 🔧 Maintenance',
            'other': '### 📦 Other Changes'
        }
        
        for change_type, section_title in sections.items():
            if changes[change_type]:
                changelog_content += f"{section_title}\n\n"
                for change in changes[change_type][:10]:  # Limit to 10 per section
                    changelog_content += f"- {change['message']} ({change['hash']})\n"
                changelog_content += "\n"
        
        # Add statistics
        total_commits = sum(len(changes[ct]) for ct in changes)
        changelog_content += f"""---

## Statistics

- **Total commits**: {total_commits}
- **Features**: {len(changes['feat'])}
- **Bug fixes**: {len(changes['fix'])}
- **Documentation**: {len(changes['docs'])}
- **Other changes**: {len(changes['other']) + len(changes['style']) + len(changes['refactor']) + len(changes['test']) + len(changes['chore'])}

Generated by MyWork-AI `mw changelog` command.
"""
        
        # Save changelog
        changelog_file = MYWORK_ROOT / "CHANGELOG_AUTO.md"
        changelog_file.write_text(changelog_content)
        
        print(f"   ✅ Analyzed {total_commits} commits")
        print(f"   ✅ Generated changelog: {changelog_file}")
        print(f"\n{Colors.BOLD}📊 Commit Summary:{Colors.ENDC}")
        for change_type, count in [(ct, len(changes[ct])) for ct in changes if changes[ct]]:
            print(f"   {sections[change_type].split()[1]} {count}")
        
        return 0
        
    except Exception as e:
        print(f"{Colors.RED}❌ Error generating changelog: {e}{Colors.ENDC}")
        return 1


def cmd_test(args: List[str] = None) -> int:
    """Universal test runner — auto-detects project type and runs tests.
    
    Usage:
        mw test                  Auto-detect and run all tests
        mw test --watch          Re-run on file changes (Node only)
        mw test --coverage       Run with coverage reporting
        mw test --verbose        Verbose output
        mw test <path>           Run specific test file/directory
    """
    import shutil

    args = args or []
    
    if args and args[0] in ["--help", "-h"]:
        print("""
🧪 mw test — Universal Test Runner

Usage:
    mw test                  Auto-detect and run all tests
    mw test --watch          Re-run on file changes (Node only)
    mw test --coverage       Run with coverage reporting
    mw test --verbose        Verbose output  
    mw test <path>           Run specific test file/directory

Supported:
    Python   → pytest (or unittest fallback)
    Node.js  → npm test / jest / vitest / mocha
    Rust     → cargo test
    Go       → go test ./...
    Ruby     → bundle exec rspec / rake test
""")
        return 0

    coverage = "--coverage" in args
    verbose = "--verbose" in args or "-v" in args
    watch = "--watch" in args
    
    # Filter flags from args to get paths
    paths = [a for a in args if not a.startswith("-")]
    
    cwd = os.getcwd()
    detected = None
    cmd = None
    
    # Detection order: check project markers
    if os.path.exists(os.path.join(cwd, "pytest.ini")) or \
       os.path.exists(os.path.join(cwd, "setup.py")) or \
       os.path.exists(os.path.join(cwd, "pyproject.toml")) or \
       os.path.exists(os.path.join(cwd, "tests")):
        # Check if it's actually a Python project
        py_files = any(f.endswith('.py') for f in os.listdir(cwd) if os.path.isfile(f))
        has_tests_dir = os.path.exists(os.path.join(cwd, "tests"))
        if py_files or has_tests_dir:
            detected = "Python"
            if shutil.which("pytest"):
                parts = ["pytest"]
                if coverage:
                    parts.append("--cov=.")
                if verbose:
                    parts.append("-v")
                else:
                    parts.append("-q")
                if paths:
                    parts.extend(paths)
                cmd = " ".join(parts)
            else:
                cmd = "python3 -m unittest discover"
                if verbose:
                    cmd += " -v"
                if paths:
                    cmd += f" -s {paths[0]}"

    if not detected and os.path.exists(os.path.join(cwd, "package.json")):
        detected = "Node.js"
        # Check for specific runners
        try:
            with open(os.path.join(cwd, "package.json")) as f:
                import json as _json
                pkg = _json.load(f)
            scripts = pkg.get("scripts", {})
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
        except Exception:
            scripts = {}
            deps = {}

        if "vitest" in deps:
            cmd = "npx vitest run"
            if watch:
                cmd = "npx vitest"
            if coverage:
                cmd += " --coverage"
        elif "jest" in deps:
            cmd = "npx jest"
            if watch:
                cmd += " --watch"
            if coverage:
                cmd += " --coverage"
            if verbose:
                cmd += " --verbose"
        elif "test" in scripts:
            cmd = "npm test"
        else:
            cmd = "npm test"

        if paths and "npx" in (cmd or ""):
            cmd += " " + " ".join(paths)

    if not detected and os.path.exists(os.path.join(cwd, "Cargo.toml")):
        detected = "Rust"
        cmd = "cargo test"
        if verbose:
            cmd += " -- --nocapture"

    if not detected and os.path.exists(os.path.join(cwd, "go.mod")):
        detected = "Go"
        cmd = "go test ./..."
        if verbose:
            cmd += " -v"
        if coverage:
            cmd += " -cover"

    if not detected and (os.path.exists(os.path.join(cwd, "Gemfile")) or 
                          os.path.exists(os.path.join(cwd, "Rakefile"))):
        detected = "Ruby"
        if os.path.exists(os.path.join(cwd, "spec")):
            cmd = "bundle exec rspec"
        else:
            cmd = "rake test"

    if not detected:
        print("❌ Could not detect project type. Supported: Python, Node.js, Rust, Go, Ruby")
        print("   Make sure you're in a project root directory.")
        return 1

    print(f"🧪 Detected: {detected} project")
    print(f"🔧 Running: {cmd}")
    print("─" * 50)
    
    result = os.system(cmd)
    return_code = result >> 8 if os.name != 'nt' else result
    
    print("─" * 50)
    if return_code == 0:
        print(f"✅ All tests passed!")
    else:
        print(f"❌ Tests failed (exit code {return_code})")
    
    return return_code


def cmd_workflow(args: List[str] = None) -> int:
    """Run workflow engine — execute multi-step YAML workflows.
    
    Usage:
        mw workflow <file.yml>           Run a workflow
        mw workflow <file.yml> --dry-run Preview without executing
        mw workflow --list               List available workflows
    """
    args = args or []
    
    if not args or args[0] in ["--help", "-h"]:
        print("""
⚙️  mw workflow — Run Multi-Step Workflows

Usage:
    mw workflow <file.yml>              Run a workflow
    mw workflow <file.yml> --dry-run    Preview without executing
    mw workflow --list                  List available workflows in .workflows/

Workflows are YAML files with steps. See docs for format.
""")
        return 0
    
    # Find workflow_engine.py relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    engine = os.path.join(script_dir, "workflow_engine.py")
    
    if not os.path.exists(engine):
        print("❌ Workflow engine not found.")
        return 1
    
    cmd = f"python3 {engine} " + " ".join(args)
    result = os.system(cmd)
    return result >> 8 if os.name != 'nt' else result


def cmd_analytics_wrapper(args: List[str] = None) -> int:
    """Run project analytics."""
    from tools.analytics import cmd_analytics
    return cmd_analytics(args or [])


def print_help() -> None:
    """Print help message."""
    print(__doc__)


def cmd_docs(args: list) -> int:
    """Auto-generate documentation for a project."""
    from doc_generator import run_docs
    return run_docs(args) or 0


def _cmd_ai_wrapper(args: List[str] = None) -> int:
    """AI assistant command."""
    from tools.ai_assistant import cmd_ai
    return cmd_ai(args or [])


def _cmd_plugin_wrapper(args: List[str] = None) -> int:
    """Plugin management command."""
    from tools.plugin_manager import cmd_plugin
    return cmd_plugin(args or [])


def cmd_config(args: List[str] = None) -> int:
    """Manage framework configuration.

    Usage:
        mw config                     # Show all config
        mw config list                # Same as above
        mw config get <key>           # Get a specific value
        mw config set <key> <value>   # Set a value
        mw config reset               # Reset to defaults
        mw config path                # Show config file path

    Config is stored in ~/.mywork/config.json.
    """
    import json as _json

    args = args or []
    sub = args[0] if args else "list"

    config_dir = Path.home() / ".mywork"
    config_file = config_dir / "config.json"

    DEFAULTS = {
        "theme": "default",
        "editor": "auto",
        "auto_update": True,
        "telemetry": False,
        "default_template": "python-api",
        "git_auto_commit": False,
        "brain_auto_learn": True,
        "plugin_auto_update": False,
        "log_level": "info",
        "max_brain_entries": 1000,
    }

    def _load() -> dict:
        if config_file.exists():
            try:
                return _json.loads(config_file.read_text())
            except Exception:
                return dict(DEFAULTS)
        return dict(DEFAULTS)

    def _save(cfg: dict):
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file.write_text(_json.dumps(cfg, indent=2) + "\n")

    if sub == "path":
        print(f"📁 Config file: {config_file}")
        print(f"   Exists: {'✅ Yes' if config_file.exists() else '❌ No (using defaults)'}")
        return 0

    if sub in ("list", "show"):
        cfg = _load()
        print(f"\n{'='*50}")
        print(f"  ⚙️  MyWork Configuration")
        print(f"{'='*50}")
        for k, v in sorted(cfg.items()):
            default_mark = " (default)" if k in DEFAULTS and cfg.get(k) == DEFAULTS[k] else " *"
            print(f"  {k:<25} = {v}{default_mark}")
        print(f"{'='*50}")
        print(f"  📁 {config_file}")
        return 0

    if sub == "get":
        if len(args) < 2:
            print("❌ Usage: mw config get <key>")
            return 1
        key = args[1]
        cfg = _load()
        if key in cfg:
            print(cfg[key])
            return 0
        elif key in DEFAULTS:
            print(f"{DEFAULTS[key]}  (default)")
            return 0
        else:
            print(f"❌ Unknown config key: {key}")
            print(f"   Available: {', '.join(sorted(DEFAULTS.keys()))}")
            return 1

    if sub == "set":
        if len(args) < 3:
            print("❌ Usage: mw config set <key> <value>")
            return 1
        key, value = args[1], " ".join(args[2:])
        # Type coercion
        if value.lower() in ("true", "yes", "1"):
            value = True
        elif value.lower() in ("false", "no", "0"):
            value = False
        elif value.isdigit():
            value = int(value)
        cfg = _load()
        old = cfg.get(key, "(unset)")
        cfg[key] = value
        _save(cfg)
        print(f"✅ {key}: {old} → {value}")
        return 0

    if sub == "reset":
        _save(dict(DEFAULTS))
        print("✅ Configuration reset to defaults")
        for k, v in sorted(DEFAULTS.items()):
            print(f"  {k:<25} = {v}")
        return 0

    if sub == "rm" or sub == "delete":
        if len(args) < 2:
            print("❌ Usage: mw config rm <key>")
            return 1
        key = args[1]
        cfg = _load()
        if key in cfg:
            del cfg[key]
            _save(cfg)
            if key in DEFAULTS:
                print(f"✅ Removed {key} (will use default: {DEFAULTS[key]})")
            else:
                print(f"✅ Removed {key}")
            return 0
        print(f"❌ Key '{key}' not found")
        return 1

    print(f"❌ Unknown subcommand: {sub}")
    print("   Usage: mw config [list|get|set|reset|rm|path]")
    return 1


def cmd_security(args: list = None) -> int:
    """Run security scanner on project."""
    args = args or []
    try:
        from tools.security_scanner import full_scan, print_report, scan_secrets, scan_code_patterns, scan_dependencies
    except ImportError:
        # Try relative import
        import importlib.util
        spec = importlib.util.spec_from_file_location("security_scanner", 
            os.path.join(os.path.dirname(__file__), "security_scanner.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        full_scan, print_report = mod.full_scan, mod.print_report
        scan_secrets, scan_code_patterns, scan_dependencies = mod.scan_secrets, mod.scan_code_patterns, mod.scan_dependencies

    project_path = os.getcwd()
    
    if not args or args[0] == 'scan':
        results = full_scan(project_path)
        print_report(results)
        return 0
    
    subcmd = args[0]
    if subcmd == 'secrets':
        findings = scan_secrets(project_path)
        for f in findings:
            print(f"🔴 [{f['type']}] {f['file']}:L{f['line']} — {f['masked_value']}")
        print(f"\n{len(findings)} secret(s) found.")
    elif subcmd == 'patterns':
        findings = scan_code_patterns(project_path)
        for f in findings:
            print(f"⚠️  [{f['type']}] {f['file']}:L{f['line']}")
        print(f"\n{len(findings)} pattern(s) found.")
    elif subcmd == 'deps':
        findings = scan_dependencies(project_path)
        for f in findings:
            print(f"📦 {f.get('package', '?')} — {f.get('vuln_id', f.get('severity_level', '?'))}")
        print(f"\n{len(findings)} vulnerability(ies) found.")
    elif subcmd == 'help':
        print("🔒 mw security — Security Scanner")
        print("  mw security          Full scan (all checks)")
        print("  mw security scan     Full scan with report")
        print("  mw security secrets  Scan for hardcoded secrets only")
        print("  mw security patterns Scan for dangerous code patterns")
        print("  mw security deps     Check dependency vulnerabilities")
    else:
        print(f"Unknown security subcommand: {subcmd}")
        print("Run 'mw security help' for usage.")
        return 1
    
    return 0


def cmd_git(args: List[str] = None) -> int:
    """Smart git operations with AI-powered commit messages.

    Usage:
        mw git status                 # Enhanced git status with summary
        mw git commit [message]       # Auto-generate commit message if none given
        mw git log [n]                # Pretty log (default last 10)
        mw git branch [name]          # List or create branch
        mw git diff                   # Summarized diff
        mw git push                   # Push current branch
        mw git pull                   # Pull with rebase
        mw git stash [pop]            # Stash or pop changes
        mw git undo                   # Undo last commit (soft reset)
        mw git amend [message]        # Amend last commit
        mw git cleanup                # Delete merged branches
    """
    import subprocess as _sp
    args = args or ["status"]
    sub = args[0] if args else "status"
    rest = args[1:] if len(args) > 1 else []

    def _run(cmd, capture=True):
        r = _sp.run(cmd, shell=True, capture_output=capture, text=True)
        return r.stdout.strip() if capture else r.returncode

    def _is_git():
        return _run("git rev-parse --is-inside-work-tree") == "true"

    if not _is_git():
        print("❌ Not inside a git repository")
        return 1

    if sub == "status":
        branch = _run("git branch --show-current")
        ahead = _run("git rev-list @{u}..HEAD --count 2>/dev/null") or "?"
        behind = _run("git rev-list HEAD..@{u} --count 2>/dev/null") or "?"
        staged = len([l for l in _run("git diff --cached --name-only").split('\n') if l])
        modified = len([l for l in _run("git diff --name-only").split('\n') if l])
        untracked = len([l for l in _run("git ls-files --others --exclude-standard").split('\n') if l])
        print(f"🌿 Branch: {branch}")
        print(f"📊 Staged: {staged} | Modified: {modified} | Untracked: {untracked}")
        print(f"↑ Ahead: {ahead} | ↓ Behind: {behind}")
        if staged + modified + untracked == 0:
            print("✅ Working tree clean")
        else:
            print("\n📝 Changes:")
            _run("git status --short", capture=False)
        return 0

    elif sub == "commit":
        # Auto-generate commit message from diff if none provided
        if rest:
            msg = " ".join(rest)
        else:
            diff = _run("git diff --cached --stat")
            if not diff:
                # Auto-stage all if nothing staged
                _run("git add -A", capture=False)
                diff = _run("git diff --cached --stat")
            if not diff:
                print("Nothing to commit")
                return 1
            # Generate smart commit message from diff
            files_changed = _run("git diff --cached --name-only")
            diff_summary = _run("git diff --cached --stat")
            # Detect type from file paths
            types = set()
            for f in files_changed.split('\n'):
                if 'test' in f.lower():
                    types.add('test')
                elif 'doc' in f.lower() or 'readme' in f.lower():
                    types.add('docs')
                elif 'fix' in _run(f"git diff --cached -- '{f}' 2>/dev/null").lower()[:500]:
                    types.add('fix')
                else:
                    types.add('feat')
            prefix = sorted(types)[0] if types else 'chore'
            n_files = len([f for f in files_changed.split('\n') if f])
            short_files = ", ".join(files_changed.split('\n')[:3])
            if n_files > 3:
                short_files += f" (+{n_files - 3} more)"
            msg = f"{prefix}: update {short_files}"
        rc = _run(f'git commit -m "{msg}"', capture=False)
        if rc == 0:
            print(f"✅ Committed: {msg}")
        return rc or 0

    elif sub == "log":
        n = rest[0] if rest else "10"
        _run(f'git log --oneline --graph --decorate -n {n}', capture=False)
        return 0

    elif sub == "branch":
        if rest:
            _run(f"git checkout -b {rest[0]}", capture=False)
            print(f"🌿 Created and switched to branch: {rest[0]}")
        else:
            current = _run("git branch --show-current")
            branches = _run("git branch --list").split('\n')
            for b in branches:
                marker = "→ " if b.strip().lstrip('* ') == current else "  "
                print(f"{marker}{b.strip().lstrip('* ')}")
        return 0

    elif sub == "diff":
        stat = _run("git diff --stat")
        if not stat:
            stat = _run("git diff --cached --stat")
        if stat:
            print("📊 Diff Summary:")
            print(stat)
            lines = _run("git diff --shortstat") or _run("git diff --cached --shortstat")
            if lines:
                print(f"\n{lines}")
        else:
            print("No changes")
        return 0

    elif sub == "push":
        branch = _run("git branch --show-current")
        print(f"⬆️ Pushing {branch}...")
        _run(f"git push origin {branch}", capture=False)
        return 0

    elif sub == "pull":
        print("⬇️ Pulling with rebase...")
        _run("git pull --rebase", capture=False)
        return 0

    elif sub == "stash":
        if rest and rest[0] == "pop":
            _run("git stash pop", capture=False)
            print("📦 Stash popped")
        else:
            _run("git stash", capture=False)
            print("📦 Changes stashed")
        return 0

    elif sub == "undo":
        _run("git reset --soft HEAD~1", capture=False)
        print("↩️ Last commit undone (changes preserved)")
        return 0

    elif sub == "amend":
        if rest:
            msg = " ".join(rest)
            _run(f'git commit --amend -m "{msg}"', capture=False)
        else:
            _run("git commit --amend --no-edit", capture=False)
        print("✏️ Last commit amended")
        return 0

    elif sub == "cleanup":
        merged = _run("git branch --merged").split('\n')
        current = _run("git branch --show-current")
        deleted = 0
        for b in merged:
            b = b.strip().lstrip('* ')
            if b and b != current and b not in ('main', 'master', 'develop'):
                _run(f"git branch -d {b}")
                deleted += 1
        print(f"🧹 Cleaned up {deleted} merged branches")
        return 0

    else:
        # Pass through to git
        _run(f"git {sub} {' '.join(rest)}", capture=False)
        return 0


def cmd_hook(args: List[str] = None) -> int:
    """Git hooks management — install, remove, list, and create custom hooks.

    Usage:
        mw hook list                    # List installed hooks and their status
        mw hook install [hook_name]     # Install a hook (or all recommended hooks)
        mw hook remove <hook_name>      # Remove a specific hook
        mw hook run <hook_name>         # Run a hook manually
        mw hook create <hook_name>      # Create a custom hook from template
        mw hook status                  # Show hooks health and recommendations

    Recommended hooks: pre-commit (lint+format), commit-msg (conventional commits),
    pre-push (tests), post-merge (dependency install).
    """
    import subprocess as _sp
    import stat

    args = args or ["list"]
    sub = args[0] if args else "list"
    rest = args[1:] if len(args) > 1 else []

    def _run(cmd, capture=True):
        r = _sp.run(cmd, shell=True, capture_output=capture, text=True)
        return r.stdout.strip() if capture else r.returncode

    def _is_git():
        return _run("git rev-parse --is-inside-work-tree") == "true"

    if not _is_git():
        print("❌ Not inside a git repository")
        return 1

    hooks_dir = Path(_run("git rev-parse --git-dir")) / "hooks"
    hooks_dir.mkdir(exist_ok=True)

    # All standard git hooks
    ALL_HOOKS = [
        "pre-commit", "prepare-commit-msg", "commit-msg", "post-commit",
        "pre-rebase", "post-rewrite", "post-checkout", "post-merge",
        "pre-push", "pre-auto-gc", "post-update",
    ]

    # Hook templates with smart defaults
    HOOK_TEMPLATES = {
        "pre-commit": "#!/bin/bash\n# MyWork-AI pre-commit hook — lint & format check\nset -e\n\necho \"🔍 Running pre-commit checks...\"\n\n# Python: ruff check\nif find . -name \"*.py\" -not -path \"./.git/*\" -not -path \"./venv/*\" | head -1 | grep -q .; then\n    if command -v ruff &>/dev/null; then\n        echo \"  🐍 Ruff lint...\"\n        ruff check --fix . 2>/dev/null || true\n        git add -u\n    elif command -v flake8 &>/dev/null; then\n        echo \"  🐍 Flake8 lint...\"\n        flake8 --max-line-length=120 --exclude=venv,.git . || { echo \"❌ Lint failed\"; exit 1; }\n    fi\nfi\n\n# Node: eslint check\nif [ -f \"package.json\" ]; then\n    if command -v npx &>/dev/null && [ -f \"node_modules/.bin/eslint\" ]; then\n        echo \"  📦 ESLint...\"\n        npx eslint --fix . 2>/dev/null || true\n        git add -u\n    fi\nfi\n\n# Check for secrets/keys\nif git diff --cached --diff-filter=ACM | grep -iE '(api[_-]?key|secret|password|token)\\s*[:=]\\s*.[^\"]{8,}' | grep -v 'example\\|placeholder\\|YOUR_\\|xxx\\|test'; then\n    echo \"⚠️  Possible secret detected! Review before committing.\"\n    exit 1\nfi\n\necho \"✅ Pre-commit passed\"\n",
        "commit-msg": '''#!/bin/bash
# MyWork-AI commit-msg hook — enforce conventional commits
MSG_FILE="$1"
MSG=$(cat "$MSG_FILE")

# Conventional commit pattern: type(scope): description
PATTERN="^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert|security|wip)(\\([a-zA-Z0-9_-]+\\))?(!)?:\\s.{3,}"

if ! echo "$MSG" | grep -qE "$PATTERN"; then
    echo "❌ Commit message doesn't follow Conventional Commits format."
    echo ""
    echo "Format: <type>(<scope>): <description>"
    echo ""
    echo "Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert, security, wip"
    echo "Example: feat(auth): add OAuth2 login support"
    echo "Example: fix: resolve null pointer in dashboard"
    echo ""
    echo "Your message: $MSG"
    exit 1
fi

echo "✅ Commit message OK"
''',
        "pre-push": '''#!/bin/bash
# MyWork-AI pre-push hook — run tests before pushing
set -e

echo "🧪 Running tests before push..."

# Python tests
if [ -d "tests" ] && find tests -name "test_*.py" | head -1 | grep -q .; then
    if command -v pytest &>/dev/null; then
        echo "  🐍 pytest..."
        pytest tests/ --tb=short -q || { echo "❌ Tests failed — push aborted"; exit 1; }
    fi
fi

# Node tests
if [ -f "package.json" ] && grep -q '"test"' package.json 2>/dev/null; then
    echo "  📦 npm test..."
    npm test --silent 2>/dev/null || { echo "❌ Tests failed — push aborted"; exit 1; }
fi

echo "✅ All tests passed — pushing"
''',
        "post-merge": '''#!/bin/bash
# MyWork-AI post-merge hook — auto-install deps after pull
echo "📦 Checking for dependency changes..."

# Python
if git diff HEAD@{1} --name-only | grep -qE "requirements.*\\.txt|setup\\.py|pyproject\\.toml"; then
    echo "  🐍 Python deps changed — installing..."
    pip install -r requirements.txt 2>/dev/null || pip install -e . 2>/dev/null || true
fi

# Node
if git diff HEAD@{1} --name-only | grep -q "package-lock.json\\|yarn.lock\\|pnpm-lock.yaml"; then
    echo "  📦 Node deps changed — installing..."
    if [ -f "pnpm-lock.yaml" ]; then pnpm install
    elif [ -f "yarn.lock" ]; then yarn install
    else npm install
    fi
fi

echo "✅ Dependencies up to date"
''',
    }

    RECOMMENDED = ["pre-commit", "commit-msg", "pre-push", "post-merge"]

    if sub == "list":
        print("🪝 Git Hooks Status\n")
        installed = 0
        for hook in ALL_HOOKS:
            hook_path = hooks_dir / hook
            if hook_path.exists() and not str(hook_path).endswith(".sample"):
                is_mw = "# MyWork-AI" in hook_path.read_text()
                tag = "🟢 MyWork" if is_mw else "🔵 Custom"
                print(f"  {tag}  {hook}")
                installed += 1
            elif hook in RECOMMENDED:
                print(f"  ⚪ {hook} (recommended — run 'mw hook install {hook}')")
        if installed == 0:
            print("  No hooks installed. Run 'mw hook install' for recommended set.")
        print(f"\n📊 {installed} hooks active | {len(RECOMMENDED)} recommended")
        return 0

    elif sub == "install":
        target = rest[0] if rest else None
        hooks_to_install = [target] if target else RECOMMENDED

        for hook_name in hooks_to_install:
            if hook_name not in HOOK_TEMPLATES:
                print(f"⚠️  No template for '{hook_name}' — use 'mw hook create {hook_name}'")
                continue
            hook_path = hooks_dir / hook_name
            if hook_path.exists():
                # Back up existing
                backup = hooks_dir / f"{hook_name}.backup"
                hook_path.rename(backup)
                print(f"  📋 Backed up existing {hook_name} → {hook_name}.backup")

            hook_path.write_text(HOOK_TEMPLATES[hook_name])
            hook_path.chmod(hook_path.stat().st_mode | stat.S_IEXEC)
            print(f"  ✅ Installed {hook_name}")

        print(f"\n🪝 {'All recommended hooks' if not target else target} installed!")
        return 0

    elif sub == "remove":
        if not rest:
            print("❌ Usage: mw hook remove <hook_name>")
            return 1
        hook_name = rest[0]
        hook_path = hooks_dir / hook_name
        if hook_path.exists():
            hook_path.unlink()
            print(f"✅ Removed {hook_name}")
            # Restore backup if exists
            backup = hooks_dir / f"{hook_name}.backup"
            if backup.exists():
                backup.rename(hook_path)
                print(f"  📋 Restored previous {hook_name} from backup")
        else:
            print(f"⚠️  Hook '{hook_name}' not installed")
        return 0

    elif sub == "run":
        if not rest:
            print("❌ Usage: mw hook run <hook_name>")
            return 1
        hook_name = rest[0]
        hook_path = hooks_dir / hook_name
        if not hook_path.exists():
            print(f"❌ Hook '{hook_name}' not installed")
            return 1
        print(f"🏃 Running {hook_name}...")
        return _run(str(hook_path), capture=False)

    elif sub == "create":
        if not rest:
            print("❌ Usage: mw hook create <hook_name>")
            return 1
        hook_name = rest[0]
        if hook_name not in ALL_HOOKS:
            print(f"⚠️  '{hook_name}' is not a standard git hook.")
            print(f"   Standard hooks: {', '.join(ALL_HOOKS)}")
            return 1
        hook_path = hooks_dir / hook_name
        if hook_path.exists():
            print(f"⚠️  Hook '{hook_name}' already exists. Remove it first with 'mw hook remove {hook_name}'")
            return 1
        template = f'''#!/bin/bash
# MyWork-AI {hook_name} hook — custom
# Created by: mw hook create {hook_name}
set -e

echo "🪝 Running {hook_name}..."

# Add your commands here:


echo "✅ {hook_name} passed"
'''
        hook_path.write_text(template)
        hook_path.chmod(hook_path.stat().st_mode | stat.S_IEXEC)
        print(f"✅ Created {hook_name} template at {hook_path}")
        print(f"   Edit it: $EDITOR {hook_path}")
        return 0

    elif sub == "status":
        print("🪝 Hooks Health Check\n")
        issues = []
        installed_hooks = []
        for hook in ALL_HOOKS:
            hook_path = hooks_dir / hook
            if hook_path.exists() and not str(hook_path).endswith(".sample"):
                installed_hooks.append(hook)
                # Check executable
                if not os.access(hook_path, os.X_OK):
                    issues.append(f"  ⚠️  {hook} is not executable (run: chmod +x {hook_path})")
                # Check shebang
                first_line = hook_path.read_text().split('\n')[0] if hook_path.read_text() else ""
                if not first_line.startswith("#!"):
                    issues.append(f"  ⚠️  {hook} missing shebang line")

        for rec in RECOMMENDED:
            if rec not in installed_hooks:
                issues.append(f"  💡 {rec} not installed (recommended)")

        if installed_hooks:
            print(f"✅ {len(installed_hooks)} hooks active: {', '.join(installed_hooks)}")
        else:
            print("⚠️  No hooks installed")

        if issues:
            print(f"\n📋 {len(issues)} suggestions:")
            for issue in issues:
                print(issue)
        else:
            print("\n🎉 All hooks healthy!")

        return 0

    else:
        print(f"❌ Unknown hook subcommand: {sub}")
        print("Usage: mw hook [list|install|remove|run|create|status]")
        return 1


def cmd_version() -> int:
    """Show framework version, Python version, and platform info."""
    import platform
    try:
        pyproject_path = MYWORK_ROOT / "pyproject.toml"
        version = "unknown"
        if pyproject_path.exists():
            with open(pyproject_path, 'r') as f:
                for line in f:
                    if line.startswith('version ='):
                        version = line.split('=')[1].strip().strip('"')
                        break
        print(f"MyWork-AI v{version}")
        print(f"Python {platform.python_version()} on {platform.system()} {platform.machine()}")
        print(f"Install: {MYWORK_ROOT}")
    except Exception as e:
        print(f"MyWork-AI (version check failed: {e})")
    return 0


def cmd_ci(args: List[str] = None) -> int:
    """Generate CI/CD pipeline configurations for projects.
    
    Usage:
        mw ci generate [project_path] [--platform github|gitlab|bitbucket]
        mw ci validate [project_path]
        mw ci templates
    
    Generates CI/CD pipelines based on project type detection.
    """
    args = args or []
    sub = args[0] if args else "generate"
    
    def _detect_project(path: str) -> dict:
        """Detect project type, language, and tools."""
        info = {"path": os.path.abspath(path), "type": "unknown", "lang": [], "tools": [], "features": []}
        
        if os.path.exists(os.path.join(path, "package.json")):
            info["lang"].append("node")
            try:
                import json
                with open(os.path.join(path, "package.json")) as f:
                    pkg = json.load(f)
                scripts = pkg.get("scripts", {})
                deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                if "next" in deps: info["type"] = "nextjs"
                elif "react" in deps: info["type"] = "react"
                elif "vue" in deps: info["type"] = "vue"
                elif "express" in deps: info["type"] = "express"
                else: info["type"] = "node"
                if "typescript" in deps or "ts-node" in deps: info["tools"].append("typescript")
                if "jest" in deps or "vitest" in deps or "mocha" in deps: info["features"].append("test")
                if "eslint" in deps: info["features"].append("lint")
                if "prettier" in deps: info["features"].append("format")
                if "test" in scripts: info["features"].append("test")
                if "lint" in scripts: info["features"].append("lint")
                if "build" in scripts: info["features"].append("build")
            except Exception:
                pass
        
        if os.path.exists(os.path.join(path, "requirements.txt")) or \
           os.path.exists(os.path.join(path, "pyproject.toml")) or \
           os.path.exists(os.path.join(path, "setup.py")):
            info["lang"].append("python")
            if info["type"] == "unknown": info["type"] = "python"
            if os.path.exists(os.path.join(path, "pyproject.toml")):
                info["tools"].append("pyproject")
            for tf in ["pytest.ini", "tox.ini", "tests", "test"]:
                if os.path.exists(os.path.join(path, tf)):
                    info["features"].append("test")
                    break
        
        if os.path.exists(os.path.join(path, "go.mod")):
            info["lang"].append("go"); info["type"] = "go"; info["features"].append("test")
        if os.path.exists(os.path.join(path, "Cargo.toml")):
            info["lang"].append("rust"); info["type"] = "rust"; info["features"].append("test")
        if os.path.exists(os.path.join(path, "Dockerfile")):
            info["tools"].append("docker")
        if os.path.exists(os.path.join(path, "docker-compose.yml")) or \
           os.path.exists(os.path.join(path, "docker-compose.yaml")):
            info["tools"].append("docker-compose")
        
        return info
    
    def _gen_github_actions(info: dict) -> str:
        """Generate GitHub Actions workflow YAML."""
        lines = [
            "name: CI/CD Pipeline",
            "",
            "on:",
            "  push:",
            "    branches: [main, develop]",
            "  pull_request:",
            "    branches: [main]",
            "",
            "jobs:",
        ]
        
        # Build & Test job
        if "node" in info["lang"]:
            node_ver = "20" if info["type"] == "nextjs" else "18"
            lines += [
                "  build-and-test:",
                "    runs-on: ubuntu-latest",
                "    strategy:",
                "      matrix:",
                f"        node-version: [{node_ver}.x]",
                "",
                "    steps:",
                "      - uses: actions/checkout@v4",
                "",
                "      - name: Setup Node.js ${{ matrix.node-version }}",
                "        uses: actions/setup-node@v4",
                "        with:",
                "          node-version: ${{ matrix.node-version }}",
                "          cache: 'npm'",
                "",
                "      - name: Install dependencies",
                "        run: npm ci",
                "",
            ]
            if "lint" in info["features"]:
                lines += [
                    "      - name: Lint",
                    "        run: npm run lint",
                    "",
                ]
            if "test" in info["features"]:
                lines += [
                    "      - name: Test",
                    "        run: npm test",
                    "",
                ]
            if "build" in info["features"]:
                lines += [
                    "      - name: Build",
                    "        run: npm run build",
                    "",
                ]
        
        elif "python" in info["lang"]:
            lines += [
                "  build-and-test:",
                "    runs-on: ubuntu-latest",
                "    strategy:",
                "      matrix:",
                "        python-version: ['3.10', '3.11', '3.12']",
                "",
                "    steps:",
                "      - uses: actions/checkout@v4",
                "",
                "      - name: Setup Python ${{ matrix.python-version }}",
                "        uses: actions/setup-python@v5",
                "        with:",
                "          python-version: ${{ matrix.python-version }}",
                "",
                "      - name: Install dependencies",
                "        run: |",
                "          python -m pip install --upgrade pip",
            ]
            if "pyproject" in info["tools"]:
                lines.append("          pip install -e '.[dev]'")
            else:
                lines += [
                    "          pip install -r requirements.txt",
                    "          pip install pytest pytest-cov flake8",
                ]
            lines.append("")
            lines += [
                "      - name: Lint with flake8",
                "        run: |",
                "          flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics",
                "          flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics",
                "",
                "      - name: Test with pytest",
                "        run: pytest --cov --cov-report=xml -v",
                "",
            ]
        
        elif "go" in info["lang"]:
            lines += [
                "  build-and-test:",
                "    runs-on: ubuntu-latest",
                "    steps:",
                "      - uses: actions/checkout@v4",
                "      - uses: actions/setup-go@v5",
                "        with:",
                "          go-version: '1.22'",
                "      - name: Build",
                "        run: go build -v ./...",
                "      - name: Test",
                "        run: go test -v -race -coverprofile=coverage.out ./...",
                "",
            ]
        
        elif "rust" in info["lang"]:
            lines += [
                "  build-and-test:",
                "    runs-on: ubuntu-latest",
                "    steps:",
                "      - uses: actions/checkout@v4",
                "      - uses: dtolnay/rust-toolchain@stable",
                "      - name: Build",
                "        run: cargo build --verbose",
                "      - name: Test",
                "        run: cargo test --verbose",
                "      - name: Clippy",
                "        run: cargo clippy -- -D warnings",
                "",
            ]
        
        # Docker build job
        if "docker" in info["tools"]:
            lines += [
                "",
                "  docker:",
                "    needs: build-and-test",
                "    runs-on: ubuntu-latest",
                "    if: github.ref == 'refs/heads/main'",
                "    steps:",
                "      - uses: actions/checkout@v4",
                "      - name: Build Docker image",
                "        run: docker build -t ${{ github.repository }}:${{ github.sha }} .",
                "",
            ]
        
        return "\n".join(lines)
    
    def _gen_gitlab_ci(info: dict) -> str:
        """Generate GitLab CI YAML."""
        lines = ["stages:", "  - test", "  - build", "  - deploy", ""]
        if "node" in info["lang"]:
            lines += [
                "test:", "  stage: test", "  image: node:20-alpine", "  script:",
                "    - npm ci",
            ]
            if "lint" in info["features"]: lines.append("    - npm run lint")
            if "test" in info["features"]: lines.append("    - npm test")
            lines.append("")
            if "build" in info["features"]:
                lines += ["build:", "  stage: build", "  image: node:20-alpine",
                          "  script:", "    - npm ci", "    - npm run build",
                          "  artifacts:", "    paths:", "      - dist/", "      - .next/", ""]
        elif "python" in info["lang"]:
            lines += [
                "test:", "  stage: test", "  image: python:3.12-slim", "  script:",
                "    - pip install -r requirements.txt", "    - pip install pytest",
                "    - pytest -v", ""
            ]
        return "\n".join(lines)
    
    if sub == "templates":
        print(f"\n{Colors.BOLD}📋 Available CI/CD Templates{Colors.ENDC}\n")
        templates = [
            ("GitHub Actions", "github", "Most popular, free for public repos"),
            ("GitLab CI", "gitlab", "Built into GitLab, powerful pipelines"),
            ("Bitbucket Pipelines", "bitbucket", "Atlassian ecosystem integration"),
        ]
        for name, key, desc in templates:
            print(f"  {Colors.GREEN}▸ {name}{Colors.ENDC} (--platform {key})")
            print(f"    {Colors.BLUE}{desc}{Colors.ENDC}")
        print(f"\n  {Colors.YELLOW}Supported project types:{Colors.ENDC} Node.js, Python, Go, Rust, Docker")
        print(f"  {Colors.YELLOW}Auto-detected features:{Colors.ENDC} tests, linting, builds, Docker\n")
        return 0
    
    if sub == "validate":
        proj_path = args[1] if len(args) > 1 else "."
        gh_path = os.path.join(proj_path, ".github", "workflows")
        gl_path = os.path.join(proj_path, ".gitlab-ci.yml")
        found = False
        if os.path.isdir(gh_path):
            yamls = [f for f in os.listdir(gh_path) if f.endswith(('.yml', '.yaml'))]
            print(f"{Colors.GREEN}✅ GitHub Actions: {len(yamls)} workflow(s) found{Colors.ENDC}")
            for y in yamls: print(f"   ▸ {y}")
            found = True
        if os.path.exists(gl_path):
            print(f"{Colors.GREEN}✅ GitLab CI: .gitlab-ci.yml found{Colors.ENDC}")
            found = True
        if not found:
            print(f"{Colors.RED}❌ No CI/CD configuration found{Colors.ENDC}")
            print(f"   Run: {Colors.BOLD}mw ci generate{Colors.ENDC}")
            return 1
        return 0
    
    if sub == "generate":
        proj_path = "."
        platform = "github"
        i = 1
        while i < len(args):
            if args[i] == "--platform" and i + 1 < len(args):
                platform = args[i + 1]; i += 2
            elif not args[i].startswith("-"):
                proj_path = args[i]; i += 1
            else:
                i += 1
        
        info = _detect_project(proj_path)
        print(f"\n{Colors.BOLD}🔍 Project Analysis{Colors.ENDC}")
        print(f"  Path:     {info['path']}")
        print(f"  Type:     {Colors.GREEN}{info['type']}{Colors.ENDC}")
        print(f"  Lang:     {', '.join(info['lang']) or 'unknown'}")
        print(f"  Tools:    {', '.join(info['tools']) or 'none detected'}")
        print(f"  Features: {', '.join(set(info['features'])) or 'none detected'}")
        
        if info["type"] == "unknown" and not info["lang"]:
            print(f"\n{Colors.RED}❌ Could not detect project type{Colors.ENDC}")
            print(f"   Ensure you're in a project directory with package.json, requirements.txt, go.mod, or Cargo.toml")
            return 1
        
        if platform == "github":
            content = _gen_github_actions(info)
            out_dir = os.path.join(proj_path, ".github", "workflows")
            out_file = os.path.join(out_dir, "ci.yml")
            os.makedirs(out_dir, exist_ok=True)
        elif platform == "gitlab":
            content = _gen_gitlab_ci(info)
            out_file = os.path.join(proj_path, ".gitlab-ci.yml")
        else:
            print(f"{Colors.RED}❌ Unsupported platform: {platform}{Colors.ENDC}")
            return 1
        
        # Check if file exists
        if os.path.exists(out_file):
            print(f"\n{Colors.YELLOW}⚠️  {out_file} already exists!{Colors.ENDC}")
            print(f"   Overwriting with new configuration...")
        
        with open(out_file, "w") as f:
            f.write(content)
        
        print(f"\n{Colors.GREEN}✅ Generated: {out_file}{Colors.ENDC}")
        print(f"   Platform: {platform.title()}")
        print(f"\n{Colors.BLUE}📝 Next steps:{Colors.ENDC}")
        print(f"   1. Review the generated pipeline: {Colors.BOLD}cat {out_file}{Colors.ENDC}")
        print(f"   2. Customize environment variables and secrets")
        print(f"   3. Commit and push to trigger the pipeline")
        print(f"   4. Validate: {Colors.BOLD}mw ci validate{Colors.ENDC}\n")
        return 0
    
    print(f"{Colors.RED}❌ Unknown ci subcommand: {sub}{Colors.ENDC}")
    print(f"   Usage: mw ci [generate|validate|templates]")
    return 1


def cmd_deploy(args: List[str] = None) -> int:
    """Deploy a project to Vercel, Railway, Render, or Docker.
    
    Usage:
        mw deploy                          # Deploy current directory
        mw deploy <project>                # Deploy named project
        mw deploy <project> --platform X   # Specify platform (vercel|railway|render|docker)
        mw deploy <project> --prod         # Production deploy
        mw deploy <project> --preview      # Preview/staging deploy
        mw deploy --status                 # Check last deployment status
        mw deploy --list                   # List recent deployments
    """
    args = args or []
    
    # Parse flags
    platform = None
    prod = False
    preview = False
    show_status = False
    list_deploys = False
    project_name = None
    token = None
    
    i = 0
    while i < len(args):
        if args[i] == "--platform" and i + 1 < len(args):
            platform = args[i + 1].lower()
            i += 2
        elif args[i] == "--prod":
            prod = True
            i += 1
        elif args[i] == "--preview":
            preview = True
            i += 1
        elif args[i] == "--status":
            show_status = True
            i += 1
        elif args[i] == "--list":
            list_deploys = True
            i += 1
        elif args[i] == "--token" and i + 1 < len(args):
            token = args[i + 1]
            i += 2
        elif not args[i].startswith("-"):
            project_name = args[i]
            i += 1
        else:
            i += 1
    
    # Detect project directory
    project_dir = os.getcwd()
    if project_name:
        # Try to find project in registry
        registry_path = os.path.join(os.path.expanduser("~"), "MyWork-AI", ".planning", "project_registry.json")
        if os.path.exists(registry_path):
            try:
                with open(registry_path) as f:
                    registry = json.load(f)
                for proj in registry.get("projects", []):
                    if proj.get("name", "").lower() == project_name.lower():
                        project_dir = proj.get("path", project_dir)
                        break
            except Exception:
                pass
        # Also check common locations
        for base in [os.path.expanduser("~"), "/home/Memo1981"]:
            candidate = os.path.join(base, project_name)
            if os.path.isdir(candidate):
                project_dir = candidate
                break
    
    print(f"\n{Colors.BOLD}🚀 MyWork Deploy{Colors.ENDC}")
    print(f"{'─' * 50}")
    
    # Auto-detect platform if not specified
    if not platform:
        if os.path.exists(os.path.join(project_dir, "vercel.json")):
            platform = "vercel"
        elif os.path.exists(os.path.join(project_dir, "railway.json")) or os.path.exists(os.path.join(project_dir, "railway.toml")):
            platform = "railway"
        elif os.path.exists(os.path.join(project_dir, "render.yaml")):
            platform = "render"
        elif os.path.exists(os.path.join(project_dir, "Dockerfile")):
            platform = "docker"
        elif os.path.exists(os.path.join(project_dir, "package.json")):
            platform = "vercel"  # Default for Node.js
        elif os.path.exists(os.path.join(project_dir, "requirements.txt")) or os.path.exists(os.path.join(project_dir, "pyproject.toml")):
            platform = "railway"  # Default for Python
        else:
            print(f"{Colors.RED}❌ Could not auto-detect platform. Use --platform <vercel|railway|render|docker>{Colors.ENDC}")
            return 1
    
    print(f"  📁 Project: {Colors.GREEN}{os.path.basename(project_dir)}{Colors.ENDC}")
    print(f"  📍 Path: {project_dir}")
    print(f"  🎯 Platform: {Colors.BLUE}{platform}{Colors.ENDC}")
    print(f"  🏷️  Mode: {'Production' if prod else 'Preview'}")
    print()
    
    # Pre-deploy checks
    print(f"{Colors.YELLOW}⏳ Running pre-deploy checks...{Colors.ENDC}")
    
    checks_passed = True
    
    # Check git status
    try:
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=project_dir, timeout=10)
        uncommitted = result.stdout.strip()
        if uncommitted:
            lines = uncommitted.split("\n")
            print(f"  {Colors.YELLOW}⚠️  {len(lines)} uncommitted changes{Colors.ENDC}")
            if prod:
                print(f"  {Colors.RED}❌ Cannot deploy to production with uncommitted changes{Colors.ENDC}")
                print(f"  {Colors.YELLOW}💡 Commit first or use --preview{Colors.ENDC}")
                return 1
        else:
            print(f"  {Colors.GREEN}✅ Git clean{Colors.ENDC}")
    except Exception:
        print(f"  {Colors.YELLOW}⚠️  Not a git repo or git not available{Colors.ENDC}")
    
    # Check for build errors (Node.js)
    if os.path.exists(os.path.join(project_dir, "package.json")):
        try:
            with open(os.path.join(project_dir, "package.json")) as f:
                pkg = json.load(f)
            if "build" in pkg.get("scripts", {}):
                print(f"  {Colors.YELLOW}⏳ Running build check...{Colors.ENDC}")
                build_result = subprocess.run(
                    ["npm", "run", "build"], capture_output=True, text=True, 
                    cwd=project_dir, timeout=120
                )
                if build_result.returncode != 0:
                    print(f"  {Colors.RED}❌ Build failed!{Colors.ENDC}")
                    # Show last 5 lines of error
                    errors = build_result.stderr.strip().split("\n")[-5:]
                    for line in errors:
                        print(f"     {line}")
                    return 1
                else:
                    print(f"  {Colors.GREEN}✅ Build successful{Colors.ENDC}")
        except (json.JSONDecodeError, FileNotFoundError):
            pass
        except subprocess.TimeoutExpired:
            print(f"  {Colors.YELLOW}⚠️  Build timed out (120s limit){Colors.ENDC}")
    
    # Check for tests
    if os.path.exists(os.path.join(project_dir, "package.json")):
        try:
            with open(os.path.join(project_dir, "package.json")) as f:
                pkg = json.load(f)
            if "test" in pkg.get("scripts", {}) and pkg["scripts"]["test"] != "echo \"Error: no test specified\" && exit 1":
                print(f"  {Colors.YELLOW}⏳ Running tests...{Colors.ENDC}")
                test_result = subprocess.run(
                    ["npm", "test", "--", "--passWithNoTests"], capture_output=True, text=True,
                    cwd=project_dir, timeout=120
                )
                if test_result.returncode == 0:
                    print(f"  {Colors.GREEN}✅ Tests passed{Colors.ENDC}")
                else:
                    print(f"  {Colors.YELLOW}⚠️  Tests failed (continuing anyway for preview){Colors.ENDC}")
                    if prod:
                        print(f"  {Colors.RED}❌ Cannot deploy to production with failing tests{Colors.ENDC}")
                        return 1
        except Exception:
            pass
    
    print()
    
    # Deploy based on platform
    if platform == "vercel":
        return _deploy_vercel(project_dir, prod, token)
    elif platform == "railway":
        return _deploy_railway(project_dir, prod)
    elif platform == "render":
        return _deploy_render(project_dir, prod)
    elif platform == "docker":
        return _deploy_docker(project_dir, prod, project_name or os.path.basename(project_dir))
    else:
        print(f"{Colors.RED}❌ Unknown platform: {platform}{Colors.ENDC}")
        print(f"{Colors.YELLOW}💡 Supported: vercel, railway, render, docker{Colors.ENDC}")
        return 1


def _deploy_vercel(project_dir: str, prod: bool, token: str = None) -> int:
    """Deploy to Vercel."""
    print(f"{Colors.BLUE}☁️  Deploying to Vercel...{Colors.ENDC}")
    
    # Check for vercel CLI
    vercel_check = subprocess.run(["which", "vercel"], capture_output=True, text=True)
    if vercel_check.returncode != 0:
        # Try npx
        print(f"  {Colors.YELLOW}📦 vercel CLI not found, using npx...{Colors.ENDC}")
        vercel_cmd = ["npx", "vercel"]
    else:
        vercel_cmd = ["vercel"]
    
    cmd = vercel_cmd.copy()
    if prod:
        cmd.append("--prod")
    if token:
        cmd.extend(["--token", token])
    cmd.append("--yes")  # Skip prompts
    
    print(f"  {Colors.YELLOW}⏳ Running: {' '.join(cmd)}{Colors.ENDC}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_dir, timeout=300)
        if result.returncode == 0:
            url = result.stdout.strip().split("\n")[-1]
            print(f"\n  {Colors.GREEN}✅ Deployed successfully!{Colors.ENDC}")
            print(f"  {Colors.BOLD}🔗 URL: {url}{Colors.ENDC}")
            
            # Save deployment record
            _save_deploy_record(project_dir, "vercel", url, prod)
            return 0
        else:
            print(f"\n  {Colors.RED}❌ Deployment failed{Colors.ENDC}")
            errors = result.stderr.strip().split("\n")[-5:]
            for line in errors:
                print(f"     {line}")
            return 1
    except subprocess.TimeoutExpired:
        print(f"\n  {Colors.RED}❌ Deployment timed out (5 min limit){Colors.ENDC}")
        return 1


def _deploy_railway(project_dir: str, prod: bool) -> int:
    """Deploy to Railway."""
    print(f"{Colors.BLUE}🚂 Deploying to Railway...{Colors.ENDC}")
    
    railway_check = subprocess.run(["which", "railway"], capture_output=True, text=True)
    if railway_check.returncode != 0:
        print(f"  {Colors.RED}❌ Railway CLI not installed{Colors.ENDC}")
        print(f"  {Colors.YELLOW}💡 Install: npm install -g @railway/cli{Colors.ENDC}")
        return 1
    
    cmd = ["railway", "up"]
    if not prod:
        cmd.append("--detach")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_dir, timeout=300)
        if result.returncode == 0:
            print(f"\n  {Colors.GREEN}✅ Deployed to Railway!{Colors.ENDC}")
            output = result.stdout.strip()
            if output:
                print(f"  {output}")
            _save_deploy_record(project_dir, "railway", "", prod)
            return 0
        else:
            print(f"\n  {Colors.RED}❌ Railway deployment failed{Colors.ENDC}")
            print(f"  {result.stderr.strip()[:200]}")
            return 1
    except subprocess.TimeoutExpired:
        print(f"\n  {Colors.RED}❌ Timed out{Colors.ENDC}")
        return 1


def _deploy_render(project_dir: str, prod: bool) -> int:
    """Deploy to Render (via git push)."""
    print(f"{Colors.BLUE}🎨 Deploying to Render...{Colors.ENDC}")
    print(f"  {Colors.YELLOW}💡 Render deploys automatically on git push{Colors.ENDC}")
    
    try:
        # Check if render remote exists
        result = subprocess.run(["git", "remote", "-v"], capture_output=True, text=True, cwd=project_dir, timeout=10)
        if "render" not in result.stdout.lower() and "origin" in result.stdout:
            print(f"  {Colors.YELLOW}⏳ Pushing to origin (Render auto-deploys)...{Colors.ENDC}")
            push = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True, cwd=project_dir, timeout=60)
            if push.returncode == 0:
                print(f"\n  {Colors.GREEN}✅ Pushed! Render will auto-deploy.{Colors.ENDC}")
                _save_deploy_record(project_dir, "render", "", prod)
                return 0
            else:
                print(f"\n  {Colors.RED}❌ Push failed: {push.stderr.strip()[:200]}{Colors.ENDC}")
                return 1
        else:
            print(f"  {Colors.YELLOW}💡 Configure Render dashboard at https://dashboard.render.com{Colors.ENDC}")
            return 0
    except Exception as e:
        print(f"  {Colors.RED}❌ Error: {e}{Colors.ENDC}")
        return 1


def _deploy_docker(project_dir: str, prod: bool, name: str) -> int:
    """Build and run Docker container."""
    print(f"{Colors.BLUE}🐳 Building Docker image...{Colors.ENDC}")
    
    if not os.path.exists(os.path.join(project_dir, "Dockerfile")):
        print(f"  {Colors.RED}❌ No Dockerfile found{Colors.ENDC}")
        return 1
    
    tag = f"{name.lower()}:{'latest' if prod else 'preview'}"
    
    try:
        # Build
        print(f"  {Colors.YELLOW}⏳ Building {tag}...{Colors.ENDC}")
        build = subprocess.run(
            ["docker", "build", "-t", tag, "."], 
            capture_output=True, text=True, cwd=project_dir, timeout=300
        )
        if build.returncode != 0:
            print(f"\n  {Colors.RED}❌ Build failed{Colors.ENDC}")
            errors = build.stderr.strip().split("\n")[-5:]
            for line in errors:
                print(f"     {line}")
            return 1
        
        print(f"  {Colors.GREEN}✅ Image built: {tag}{Colors.ENDC}")
        
        # Run
        print(f"  {Colors.YELLOW}⏳ Starting container...{Colors.ENDC}")
        run = subprocess.run(
            ["docker", "run", "-d", "--name", f"{name.lower()}-deploy", "-p", "3000:3000", tag],
            capture_output=True, text=True, timeout=30
        )
        if run.returncode == 0:
            container_id = run.stdout.strip()[:12]
            print(f"\n  {Colors.GREEN}✅ Container running: {container_id}{Colors.ENDC}")
            print(f"  {Colors.BOLD}🔗 http://localhost:3000{Colors.ENDC}")
            _save_deploy_record(project_dir, "docker", f"localhost:3000", prod)
            return 0
        else:
            print(f"\n  {Colors.YELLOW}⚠️  Container may already exist. Try: docker rm -f {name.lower()}-deploy{Colors.ENDC}")
            return 1
    except subprocess.TimeoutExpired:
        print(f"\n  {Colors.RED}❌ Timed out{Colors.ENDC}")
        return 1


def _save_deploy_record(project_dir: str, platform: str, url: str, prod: bool) -> None:
    """Save deployment record for history."""
    try:
        deploy_log = os.path.join(project_dir, ".mw-deploys.json")
        deploys = []
        if os.path.exists(deploy_log):
            with open(deploy_log) as f:
                deploys = json.load(f)
        
        from datetime import datetime
        deploys.append({
            "timestamp": datetime.now().isoformat(),
            "platform": platform,
            "url": url,
            "production": prod,
            "project": os.path.basename(project_dir)
        })
        
        # Keep last 50
        deploys = deploys[-50:]
        
        with open(deploy_log, "w") as f:
            json.dump(deploys, f, indent=2)
    except Exception:
        pass  # Non-critical


def cmd_env(args: List[str] = None) -> int:
    """Manage environment variables across projects.

    Usage:
        mw env                        # Show current .env status
        mw env list                   # List all variables (values hidden)
        mw env list --show            # List all variables (values shown)
        mw env get KEY                # Get a specific variable
        mw env set KEY=VALUE          # Set a variable
        mw env set KEY VALUE          # Set a variable (alt syntax)
        mw env rm KEY                 # Remove a variable
        mw env diff                   # Compare .env vs .env.example
        mw env validate               # Check all required vars are set
        mw env export --format=docker # Export as Docker env format
        mw env init                   # Create .env from .env.example
    """
    args = args or []
    subcommand = args[0] if args else "status"

    # Find .env files
    env_file = Path(".env")
    env_example = Path(".env.example")

    def _parse_env(path: Path) -> dict:
        """Parse a .env file into key-value dict."""
        result = {}
        if not path.exists():
            return result
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                result[key] = value
        return result

    def _write_env(path: Path, data: dict, comments: dict = None):
        """Write key-value dict back to .env preserving comments."""
        lines = []
        if path.exists():
            existing_lines = path.read_text().splitlines()
            written_keys = set()
            for line in existing_lines:
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    lines.append(line)
                    continue
                if "=" in stripped:
                    key = stripped.split("=", 1)[0].strip()
                    if key in data:
                        lines.append(f"{key}={data[key]}")
                        written_keys.add(key)
                    # Skip removed keys
                    elif key not in data:
                        continue
            # Add new keys
            for key, value in data.items():
                if key not in written_keys:
                    lines.append(f"{key}={value}")
        else:
            for key, value in data.items():
                lines.append(f"{key}={value}")
        path.write_text("\n".join(lines) + "\n")

    def _mask(value: str) -> str:
        if len(value) <= 4:
            return "****"
        return value[:2] + "*" * (len(value) - 4) + value[-2:]

    if subcommand == "status":
        print(f"\n{Colors.BOLD}📋 Environment Status{Colors.ENDC}\n")
        env_exists = env_file.exists()
        example_exists = env_example.exists()
        print(f"  .env          {'✅ Found' if env_exists else '❌ Not found'}")
        print(f"  .env.example  {'✅ Found' if example_exists else '⚠️  Not found'}")
        if env_exists:
            data = _parse_env(env_file)
            print(f"  Variables     {Colors.GREEN}{len(data)}{Colors.ENDC}")
            empty = sum(1 for v in data.values() if not v)
            if empty:
                print(f"  Empty values  {Colors.YELLOW}{empty}{Colors.ENDC}")
        if example_exists and env_exists:
            example_data = _parse_env(env_example)
            env_data = _parse_env(env_file)
            missing = set(example_data.keys()) - set(env_data.keys())
            if missing:
                print(f"  Missing vars  {Colors.RED}{len(missing)}{Colors.ENDC}: {', '.join(sorted(missing))}")
            else:
                print(f"  Coverage      {Colors.GREEN}100% ✓{Colors.ENDC}")
        print()
        return 0

    elif subcommand == "list":
        if not env_file.exists():
            print(f"{Colors.RED}❌ No .env file found{Colors.ENDC}")
            return 1
        data = _parse_env(env_file)
        show = "--show" in args
        print(f"\n{Colors.BOLD}📋 Environment Variables ({len(data)}){Colors.ENDC}\n")
        for key in sorted(data.keys()):
            value = data[key] if show else _mask(data[key]) if data[key] else "(empty)"
            print(f"  {Colors.GREEN}{key}{Colors.ENDC}={value}")
        print()
        return 0

    elif subcommand == "get":
        if len(args) < 2:
            print(f"{Colors.RED}Usage: mw env get KEY{Colors.ENDC}")
            return 1
        key = args[1]
        data = _parse_env(env_file)
        if key in data:
            print(data[key])
            return 0
        else:
            print(f"{Colors.RED}❌ Variable '{key}' not found{Colors.ENDC}")
            return 1

    elif subcommand == "set":
        if len(args) < 2:
            print(f"{Colors.RED}Usage: mw env set KEY=VALUE or mw env set KEY VALUE{Colors.ENDC}")
            return 1
        if "=" in args[1]:
            key, _, value = args[1].partition("=")
        elif len(args) >= 3:
            key, value = args[1], args[2]
        else:
            print(f"{Colors.RED}Usage: mw env set KEY=VALUE{Colors.ENDC}")
            return 1
        data = _parse_env(env_file)
        is_new = key not in data
        data[key] = value
        _write_env(env_file, data)
        action = "Added" if is_new else "Updated"
        print(f"{Colors.GREEN}✅ {action} {key}{Colors.ENDC}")
        return 0

    elif subcommand == "rm":
        if len(args) < 2:
            print(f"{Colors.RED}Usage: mw env rm KEY{Colors.ENDC}")
            return 1
        key = args[1]
        data = _parse_env(env_file)
        if key not in data:
            print(f"{Colors.RED}❌ Variable '{key}' not found{Colors.ENDC}")
            return 1
        del data[key]
        _write_env(env_file, data)
        print(f"{Colors.GREEN}✅ Removed {key}{Colors.ENDC}")
        return 0

    elif subcommand == "diff":
        if not env_example.exists():
            print(f"{Colors.RED}❌ No .env.example found{Colors.ENDC}")
            return 1
        example_data = _parse_env(env_example)
        env_data = _parse_env(env_file) if env_file.exists() else {}
        all_keys = sorted(set(list(example_data.keys()) + list(env_data.keys())))
        print(f"\n{Colors.BOLD}🔍 Environment Diff (.env vs .env.example){Colors.ENDC}\n")
        for key in all_keys:
            in_env = key in env_data
            in_example = key in example_data
            has_value = in_env and bool(env_data.get(key))
            if in_env and in_example and has_value:
                print(f"  {Colors.GREEN}✅{Colors.ENDC} {key}")
            elif in_example and not in_env:
                print(f"  {Colors.RED}❌{Colors.ENDC} {key} (missing from .env)")
            elif in_env and not in_example:
                print(f"  {Colors.YELLOW}➕{Colors.ENDC} {key} (extra, not in .env.example)")
            elif in_env and not has_value:
                print(f"  {Colors.YELLOW}⚠️{Colors.ENDC}  {key} (empty value)")
        print()
        return 0

    elif subcommand == "validate":
        if not env_example.exists():
            print(f"{Colors.YELLOW}⚠️  No .env.example to validate against{Colors.ENDC}")
            return 0
        example_data = _parse_env(env_example)
        env_data = _parse_env(env_file) if env_file.exists() else {}
        missing = []
        empty = []
        for key in example_data:
            if key not in env_data:
                missing.append(key)
            elif not env_data[key]:
                empty.append(key)
        if not missing and not empty:
            print(f"{Colors.GREEN}✅ All {len(example_data)} required variables are set{Colors.ENDC}")
            return 0
        if missing:
            print(f"{Colors.RED}❌ Missing variables:{Colors.ENDC}")
            for k in missing:
                print(f"   {k}")
        if empty:
            print(f"{Colors.YELLOW}⚠️  Empty variables:{Colors.ENDC}")
            for k in empty:
                print(f"   {k}")
        return 1 if missing else 0

    elif subcommand == "export":
        if not env_file.exists():
            print(f"{Colors.RED}❌ No .env file found{Colors.ENDC}")
            return 1
        data = _parse_env(env_file)
        fmt = "shell"
        for a in args:
            if a.startswith("--format="):
                fmt = a.split("=", 1)[1]
        if fmt == "docker":
            for key, value in sorted(data.items()):
                print(f"-e {key}={value}")
        elif fmt == "json":
            import json as json_mod
            print(json_mod.dumps(data, indent=2))
        elif fmt == "yaml":
            for key, value in sorted(data.items()):
                print(f"{key}: \"{value}\"")
        else:  # shell
            for key, value in sorted(data.items()):
                print(f"export {key}=\"{value}\"")
        return 0

    elif subcommand == "init":
        if env_file.exists():
            print(f"{Colors.YELLOW}⚠️  .env already exists. Use 'mw env set' to modify.{Colors.ENDC}")
            return 0
        if not env_example.exists():
            print(f"{Colors.RED}❌ No .env.example to copy from{Colors.ENDC}")
            return 1
        import shutil
        shutil.copy2(env_example, env_file)
        data = _parse_env(env_file)
        print(f"{Colors.GREEN}✅ Created .env from .env.example ({len(data)} variables){Colors.ENDC}")
        print(f"   Edit with: {Colors.BOLD}mw env set KEY=VALUE{Colors.ENDC}")
        return 0

    else:
        print(f"{Colors.RED}❌ Unknown env subcommand: {subcommand}{Colors.ENDC}")
        print(f"   Try: mw env list | get | set | rm | diff | validate | export | init")
        return 1


def cmd_monitor(args: List[str] = None) -> int:
    """Monitor project health and uptime.
    
    Usage:
        mw monitor                    # Monitor all registered projects
        mw monitor <project>          # Monitor specific project
        mw monitor --urls             # Check all deployed URLs
    """
    args = args or []
    
    print(f"\n{Colors.BOLD}📊 MyWork Project Monitor{Colors.ENDC}")
    print(f"{'─' * 50}")
    
    # Check deployed URLs from deploy records
    check_urls = "--urls" in args
    project_filter = None
    for a in args:
        if not a.startswith("-"):
            project_filter = a
            break
    
    # Find all projects with deploy records
    import glob
    deploy_files = glob.glob(os.path.expanduser("~/*/. mw-deploys.json")) + \
                   glob.glob(os.path.expanduser("~/*/.mw-deploys.json"))
    
    # Also check common project locations
    for base in [os.path.expanduser("~"), "/home/Memo1981"]:
        for item in os.listdir(base):
            deploy_file = os.path.join(base, item, ".mw-deploys.json")
            if os.path.exists(deploy_file) and deploy_file not in deploy_files:
                deploy_files.append(deploy_file)
    
    if not deploy_files:
        print(f"  {Colors.YELLOW}No deployment records found.{Colors.ENDC}")
        print(f"  {Colors.YELLOW}💡 Deploy a project first: mw deploy <project>{Colors.ENDC}")
        return 0
    
    for deploy_file in deploy_files:
        try:
            with open(deploy_file) as f:
                deploys = json.load(f)
            if not deploys:
                continue
            
            last = deploys[-1]
            project = last.get("project", "unknown")
            
            if project_filter and project_filter.lower() != project.lower():
                continue
            
            print(f"\n  {Colors.BOLD}{project}{Colors.ENDC}")
            print(f"    Platform: {last.get('platform', 'unknown')}")
            print(f"    Last deploy: {last.get('timestamp', 'unknown')[:19]}")
            print(f"    Mode: {'Production' if last.get('production') else 'Preview'}")
            
            url = last.get("url", "")
            if url and check_urls:
                # Quick health check
                try:
                    import urllib.request
                    req = urllib.request.Request(url if url.startswith("http") else f"https://{url}", method="HEAD")
                    resp = urllib.request.urlopen(req, timeout=10)
                    print(f"    Status: {Colors.GREEN}✅ UP ({resp.status}){Colors.ENDC}")
                except Exception as e:
                    print(f"    Status: {Colors.RED}❌ DOWN ({e}){Colors.ENDC}")
            elif url:
                print(f"    URL: {url}")
            
            print(f"    Total deploys: {len(deploys)}")
        except Exception:
            continue
    
    print()
    return 0


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print_help()
        sys.exit(0)

    command = sys.argv[1].lower()
    args = sys.argv[2:]
    
    # Validate command input
    if not validate_input(command, "command", max_length=50):
        sys.exit(1)

    # Command routing
    commands = {
        "dashboard": lambda: cmd_dashboard(args),
        "status": lambda: cmd_status(args),
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
        "af": lambda: cmd_autoforge(args),
        "autoforge": lambda: cmd_autoforge(args),
        "ac": lambda: cmd_autoforge(args),  # Backwards compatibility alias
        "autocoder": lambda: cmd_autoforge(args),  # Backwards compatibility alias
        "n8n": lambda: cmd_n8n(args),
        "brain": lambda: cmd_brain(args),
        "credits": lambda: cmd_credits(args),
        "lint": lambda: cmd_lint(args),
        "setup": lambda: cmd_setup(args),
        "guide": lambda: cmd_guide(args),
        "prompt-enhance": lambda: cmd_prompt_enhance(args),
        "ecosystem": lambda: cmd_ecosystem(args),
        "marketplace": lambda: cmd_marketplace_info(args),
        "links": lambda: cmd_links(args),
        "remember": lambda: cmd_brain(["add"] + args),  # Shortcut
        "init": lambda: cmd_init(args),
        "stats": lambda: cmd_stats(args),
        "clean": lambda: cmd_clean(args),
        "backup": lambda: cmd_backup(args),
        "changelog": lambda: cmd_changelog(args),
        "test": lambda: cmd_test(args),
        "workflow": lambda: cmd_workflow(args),
        "wf": lambda: cmd_workflow(args),
        "analytics": lambda: cmd_analytics_wrapper(args),
        "docs": lambda: cmd_docs(args),
        "ci": lambda: cmd_ci(args),
        "deploy": lambda: cmd_deploy(args),
        "monitor": lambda: cmd_monitor(args),
        "env": lambda: cmd_env(args),
        "plugin": lambda: _cmd_plugin_wrapper(args),
        "config": lambda: cmd_config(args),
        "cfg": lambda: cmd_config(args),
        "ai": lambda: _cmd_ai_wrapper(args),
        "security": lambda: cmd_security(args),
        "sec": lambda: cmd_security(args),
        "git": lambda: cmd_git(args),
        "g": lambda: cmd_git(args),
        "hook": lambda: cmd_hook(args),
        "hooks": lambda: cmd_hook(args),
        "version": lambda: cmd_version(),
        "-v": lambda: cmd_version(),
        "--version": lambda: cmd_version(),
        "help": lambda: print_help() or 0,
        "-h": lambda: print_help() or 0,
        "--help": lambda: print_help() or 0,
    }

    if command in commands:
        sys.exit(commands[command]() or 0)
    else:
        # Try to find similar commands (fuzzy matching)
        def levenshtein_distance(s1, s2):
            """Calculate edit distance between two strings."""
            if len(s1) < len(s2):
                return levenshtein_distance(s2, s1)
            if len(s2) == 0:
                return len(s1)
            previous_row = list(range(len(s2) + 1))
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            return previous_row[-1]
        
        # Find similar commands
        similar_commands = []
        for cmd in commands.keys():
            if cmd.startswith('-'):  # Skip help flags
                continue
            distance = levenshtein_distance(command, cmd)
            if distance <= 2:  # Allow up to 2 character differences
                similar_commands.append((cmd, distance))
        
        # Sort by similarity and take top 3
        similar_commands.sort(key=lambda x: x[1])
        suggestions = [cmd for cmd, _ in similar_commands[:3]]
        
        print(f"{Colors.RED}❌ Unknown command: {command}{Colors.ENDC}")
        
        if suggestions:
            print(f"{Colors.YELLOW}💡 Did you mean:{Colors.ENDC}")
            for suggestion in suggestions:
                print(f"   {Colors.GREEN}mw {suggestion}{Colors.ENDC}")
        else:
            # If no similar commands, suggest most common ones
            common_commands = ["new", "status", "dashboard", "projects", "brain", "af", "setup"]
            print(f"{Colors.YELLOW}💡 Popular commands to try:{Colors.ENDC}")
            for cmd in common_commands[:3]:
                print(f"   {Colors.GREEN}mw {cmd}{Colors.ENDC}")
        
        print(f"\n{Colors.BLUE}📚 For help:{Colors.ENDC}")
        print(f"   {color('mw help', Colors.BOLD)}           # All available commands")
        print(f"   {color('mw setup', Colors.BOLD)}          # First-time setup")
        print(f"   {color('mw guide', Colors.BOLD)}          # Interactive tutorial")
        print(f"   {color('mw ecosystem', Colors.BOLD)}      # View ecosystem")
        sys.exit(1)


if __name__ == "__main__":
    main()
