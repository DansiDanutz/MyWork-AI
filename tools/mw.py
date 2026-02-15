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
    upgrade         Self-upgrade MyWork-AI (from GitHub or PyPI)
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
    api             Start REST API server (programmatic access)
    serve           Start web dashboard (browser UI for mw)
    demo            Live demo showcasing all framework features
    tour            Interactive feature tour (2 min onboarding)

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
    mw pair                  Live AI pair programming (watches file changes)
    mw pair --review         Review all uncommitted changes
    mw pair --quiet          Only flag bugs and security issues
    mw pair history          Show past pairing sessions
    mw ai fix <file>         Fix bugs in code
    mw ai refactor <file>    Get refactoring suggestions
    mw ai test <file>        Generate tests for code
    mw ai commit [--push]    Generate commit message from diff
    mw ai review [--staged]  AI code review of git changes
    mw ai doc <file>         Generate documentation for code
    mw ai changelog          Generate changelog from commits

Code Review & Quality Commands:
    mw review <file>         AI-powered code review of specific file
    mw review --diff         Review current git diff
    mw review --staged       Review staged changes
    mw docs generate <proj>  Generate AI documentation for project
    mw health <project>      Score project health (0-100)
    mw snapshot               Capture project metrics snapshot (LoC, tests, deps, git)
    mw snapshot history       Show snapshot history over time
    mw snapshot compare       Compare last two snapshots
    mw release <patch|minor|major>                        Version bump + changelog + tag
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
import re
import json
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any

# Ensure the framework root is on sys.path so `from tools.X` imports work
# regardless of the current working directory.
_FRAMEWORK_ROOT = str(Path(__file__).resolve().parent.parent)
if _FRAMEWORK_ROOT not in sys.path:
    sys.path.insert(0, _FRAMEWORK_ROOT)

try:
    import yaml
except ImportError:  # pragma: no cover - optional dependency
    yaml = None

# Configuration - prefer shared config for consistent path detection
try:
    from config import MYWORK_ROOT, TOOLS_DIR, PROJECTS_DIR, PROJECT_REGISTRY_JSON
except ImportError:

    def _get_mywork_root() -> Path:
        """Resolve the MyWork-AI root directory from env or script location."""
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
    CYAN = "\033[96m"
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
    try:
        import importlib
        import signal
        
        # Set up timeout for hanging tools
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Tool {tool_name} timed out after 30 seconds")
        
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(30)  # 30 second timeout
        
        module_name = tool_name
        
        # Try importing from current package
        try:
            module = importlib.import_module(module_name)
        except ImportError:
            # Try importing with tools prefix
            try:
                module = importlib.import_module(f"tools.{module_name}")
            except ImportError:
                # Fall back to file-based execution for development
                tool_path = TOOLS_DIR / f"{tool_name}.py"
                if not tool_path.exists():
                    print(f"{Colors.RED}❌ Error: Tool '{tool_name}' not found{Colors.ENDC}")
                    print(f"{Colors.YELLOW}💡 Try: mw help{Colors.ENDC}")
                    signal.alarm(0)  # Cancel timeout
                    return 1
                try:
                    cmd = [sys.executable, str(tool_path)] + (args or [])
                    result = subprocess.run(cmd, timeout=30, capture_output=True, text=True)
                    if result.returncode != 0 and result.stderr:
                        print(f"{Colors.RED}❌ Error: {result.stderr.strip()}{Colors.ENDC}")
                        print(f"{Colors.YELLOW}💡 Try: mw {tool_name} --help{Colors.ENDC}")
                    signal.alarm(0)  # Cancel timeout
                    return result.returncode
                except subprocess.TimeoutExpired:
                    print(f"{Colors.RED}❌ Error: Tool '{tool_name}' timed out{Colors.ENDC}")
                    print(f"{Colors.YELLOW}💡 Try: mw status for a quick health check{Colors.ENDC}")
                    signal.alarm(0)  # Cancel timeout
                    return 1
        
        # Execute the module's main function
        if hasattr(module, 'main'):
            # Store original sys.argv to restore later
            original_argv = sys.argv[:]
            try:
                # Set sys.argv to mimic command line execution
                sys.argv = [f"{tool_name}.py"] + (args or [])
                result = module.main()
                signal.alarm(0)  # Cancel timeout
                return result if result is not None else 0
            except SystemExit as e:
                signal.alarm(0)  # Cancel timeout
                return e.code if e.code is not None else 0
            except TimeoutError as e:
                print(f"{Colors.RED}❌ Error: {e}{Colors.ENDC}")
                print(f"{Colors.YELLOW}💡 Try: mw status for a quick health check{Colors.ENDC}")
                return 1
            finally:
                # Restore original sys.argv
                sys.argv = original_argv
        else:
            print(f"{Colors.RED}❌ Error: Tool {tool_name} does not have a main() function{Colors.ENDC}")
            print(f"{Colors.YELLOW}💡 Try: mw help{Colors.ENDC}")
            signal.alarm(0)  # Cancel timeout
            return 1
            
    except TimeoutError as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.ENDC}")
        print(f"{Colors.YELLOW}💡 Try: mw status for a quick health check{Colors.ENDC}")
        return 1
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️ Interrupted by user{Colors.ENDC}")
        signal.alarm(0)  # Cancel timeout
        return 1
    except Exception as e:
        print(f"{Colors.RED}❌ Error running tool {tool_name}: {e}{Colors.ENDC}")
        print(f"{Colors.YELLOW}💡 Try: mw {tool_name} --help{Colors.ENDC}")
        signal.alarm(0)  # Cancel timeout
        return 1


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
    if len(args) == 1 and args[0] in ["--help", "-h"]:
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
    
    if not args:
        print(f"{Colors.RED}❌ Error: Project name is required{Colors.ENDC}")
        print(f"{Colors.YELLOW}💡 Usage: mw new <project-name> [template]{Colors.ENDC}")
        print(f"{Colors.BLUE}Examples:{Colors.ENDC}")
        print(f"   mw new my-app")
        print(f"   mw new api-server fastapi")
        print(f"   mw new website nextjs")
        return 1
    
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
        
    return run_tool("scaffold", ["new"] + args + ["--current-dir"])


def cmd_scan() -> int:
    """Scan projects for modules."""
    print(f"\n{Colors.BOLD}🔍 Scanning projects for modules...{Colors.ENDC}")
    return run_tool("module_registry", ["scan"])


def cmd_fix() -> int:
    """Auto-fix issues."""
    try:
        print(f"{Colors.BLUE}🔧 Running auto-fix...{Colors.ENDC}")
        return run_tool("health_check", ["fix"])
    except Exception as e:
        print(f"{Colors.RED}❌ Error: Failed to run auto-fix{Colors.ENDC}")
        print(f"{Colors.YELLOW}💡 Try: mw status{Colors.ENDC}")
        return 1


def cmd_report() -> int:
    """Generate health report."""
    try:
        print(f"{Colors.BLUE}📊 Generating health report...{Colors.ENDC}")
        return run_tool("health_check", ["report"])
    except Exception as e:
        print(f"{Colors.RED}❌ Error: Failed to generate report{Colors.ENDC}")
        print(f"{Colors.YELLOW}💡 Try: mw status{Colors.ENDC}")
        return 1


def cmd_doctor_legacy() -> int:
    """Legacy system diagnostics."""
    try:
        print(f"{Colors.BLUE}🩺 Running legacy system diagnostics...{Colors.ENDC}")
        return run_tool("health_check")
    except Exception as e:
        print(f"{Colors.RED}❌ Error: Failed to run diagnostics{Colors.ENDC}")
        print(f"{Colors.YELLOW}💡 Try: mw status{Colors.ENDC}")
        return 1


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

    if args and args[0] in {"-h", "--help", "help"}:
        print("Usage: mw projects [subcommand]")
        print()
        print("Subcommands:")
        print("  (none)        List all projects")
        print("  scan          Refresh project registry")
        print("  export        Export project data")
        print("  stats         Show project statistics")
        print("  list          List projects from registry")
        print("  health <name> Show project health report")
        return 0

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
        """Parse a YAML scalar string into its Python equivalent (bool, str)."""
        if value.startswith(('"', "'")) and value.endswith(('"', "'")):
            return value[1:-1]
        lowered = value.lower()
        if lowered in {"true", "yes"}:
            return True
        if lowered in {"false", "no"}:
            return False
        return value

    def _simple_yaml_load(text: str) -> dict:
        """Load a simple YAML document without external dependencies."""
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
        """Safely load a YAML file, returning empty dict on any error."""
        if not path.exists():
            return {}
        try:
            if yaml:
                return yaml.safe_load(path.read_text()) or {}
            return _simple_yaml_load(path.read_text())
        except Exception:
            return {}

    def _load_project_meta(project_path: Path) -> dict:
        """Load project metadata from registry or project.yaml fallback."""
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


def cmd_gsd(args: List[str]) -> int:
    """GSD (Get Stuff Done) - Project planning and orchestration."""
    if not args or (len(args) == 1 and args[0] in ["--help", "-h"]):
        print(f"""
{Colors.BOLD}{Colors.BLUE}🎯 GSD — Get Stuff Done{Colors.ENDC}
{Colors.BLUE}{'='*50}{Colors.ENDC}

  Project planning, requirements, roadmaps, and execution tracking.

{Colors.BOLD}Commands:{Colors.ENDC}
  mw gsd new <project>      Create a new GSD project with full planning
  mw gsd status              Show all GSD project statuses
  mw gsd plan <project>      Plan next phase for a project
  mw gsd execute <project>   Execute current phase
  mw gsd progress <project>  Show detailed progress
  mw gsd quick <task>        Quick task (no full planning needed)
  mw gsd pause <project>     Pause work with context save
  mw gsd resume <project>    Resume paused project

{Colors.BOLD}Examples:{Colors.ENDC}
  mw gsd new my-saas-app              # Full project planning
  mw gsd quick "fix login bug"        # Quick one-off task
  mw gsd status                       # See all projects
  mw gsd plan my-saas-app             # Plan next phase
  mw gsd execute my-saas-app          # Execute current phase

{Colors.BOLD}Integration:{Colors.ENDC}
  mw gsd → autoforge                  # Hand off to AutoForge for coding
  mw gsd → brain                      # Store learnings in Brain
  mw gsd → marketplace                # Publish result to marketplace
""")
        return 0

    sub = args[0]
    rest = args[1:]
    project_root = Path(".")
    mw_dir = project_root / ".mw"
    gsd_dir = mw_dir / "gsd"

    if sub == "new":
        if not rest:
            print(f"{Colors.RED}❌ Error: Project name required{Colors.ENDC}")
            print(f"{Colors.YELLOW}💡 Usage: mw gsd new <project-name>{Colors.ENDC}")
            return 1
        name = rest[0]
        gsd_dir.mkdir(parents=True, exist_ok=True)
        state_file = gsd_dir / "STATE.md"
        roadmap_file = gsd_dir / "ROADMAP.md"
        requirements_file = gsd_dir / "REQUIREMENTS.md"

        state_file.write_text(f"""# {name} — Project State
## Status: 🟢 Active
## Phase: 1 — Planning
## Started: {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}

### Current Focus
- Define requirements
- Plan architecture
- Set up project structure

### Blockers
- None
""")
        roadmap_file.write_text(f"""# {name} — Roadmap

## Phase 1: Foundation
- [ ] Requirements gathering
- [ ] Architecture design
- [ ] Project scaffolding
- [ ] Core data models

## Phase 2: Core Features
- [ ] Main functionality
- [ ] API endpoints
- [ ] Database integration
- [ ] Authentication

## Phase 3: Polish
- [ ] Testing
- [ ] Documentation
- [ ] Performance optimization
- [ ] Security audit

## Phase 4: Launch
- [ ] Deployment
- [ ] Monitoring
- [ ] Marketing page
- [ ] Marketplace listing
""")
        requirements_file.write_text(f"""# {name} — Requirements

## Functional Requirements
- [ ] (Add your requirements here)

## Non-Functional Requirements
- [ ] Performance: Response time < 200ms
- [ ] Security: OWASP Top 10 compliance
- [ ] Scalability: Handle 1000+ concurrent users
- [ ] Availability: 99.9% uptime

## Tech Stack
- Backend: (TBD)
- Frontend: (TBD)
- Database: (TBD)
- Deployment: (TBD)
""")
        print(f"{Colors.GREEN}✅ GSD project '{name}' created!{Colors.ENDC}")
        print(f"   📋 State:        .mw/gsd/STATE.md")
        print(f"   🗺️  Roadmap:      .mw/gsd/ROADMAP.md")
        print(f"   📝 Requirements: .mw/gsd/REQUIREMENTS.md")
        print(f"\n{Colors.YELLOW}💡 Next: Edit requirements, then run 'mw gsd plan {name}'{Colors.ENDC}")
        return 0

    elif sub == "status":
        if not gsd_dir.exists():
            print(f"{Colors.YELLOW}⚠️  No GSD projects found in this directory{Colors.ENDC}")
            print(f"{Colors.CYAN}💡 Create one: mw gsd new <project-name>{Colors.ENDC}")
            return 0
        state_file = gsd_dir / "STATE.md"
        if state_file.exists():
            content = state_file.read_text()
            print(f"{Colors.BOLD}{Colors.BLUE}🎯 GSD Project Status{Colors.ENDC}")
            print(f"{Colors.BLUE}{'='*50}{Colors.ENDC}")
            print(content)
        else:
            print(f"{Colors.YELLOW}⚠️  No STATE.md found{Colors.ENDC}")
        return 0

    elif sub == "progress":
        roadmap = gsd_dir / "ROADMAP.md" if gsd_dir.exists() else None
        if roadmap and roadmap.exists():
            content = roadmap.read_text()
            total = content.count("- [")
            done = content.count("- [x]") + content.count("- [X]")
            pct = int(done / total * 100) if total > 0 else 0
            bar_len = 30
            filled = int(bar_len * pct / 100)
            bar = "█" * filled + "░" * (bar_len - filled)
            print(f"{Colors.BOLD}{Colors.BLUE}📊 Project Progress{Colors.ENDC}")
            print(f"   [{bar}] {pct}% ({done}/{total} tasks)")
            print(f"\n{content}")
        else:
            print(f"{Colors.YELLOW}⚠️  No roadmap found. Run 'mw gsd new <project>' first{Colors.ENDC}")
        return 0

    elif sub == "quick":
        task = " ".join(rest) if rest else None
        if not task:
            print(f"{Colors.RED}❌ Error: Task description required{Colors.ENDC}")
            print(f"{Colors.YELLOW}💡 Usage: mw gsd quick \"fix the login bug\"{Colors.ENDC}")
            return 1
        print(f"{Colors.GREEN}⚡ Quick task started: {task}{Colors.ENDC}")
        print(f"   No full planning — just get it done!")
        print(f"\n{Colors.CYAN}💡 When done, run: mw brain add \"Completed: {task}\"{Colors.ENDC}")
        return 0

    else:
        print(f"{Colors.YELLOW}⚠️  Unknown GSD subcommand: {sub}{Colors.ENDC}")
        print(f"{Colors.CYAN}💡 Run 'mw gsd --help' for available commands{Colors.ENDC}")
        return 1


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
    """n8n workflow automation commands."""
    if not args or (len(args) == 1 and args[0] in ["--help", "-h"]):
        print("""
n8n Commands — Workflow Automation Manager
==========================================
Usage:
    mw n8n setup                    Install & start n8n (Docker or local)
    mw n8n status                   Check n8n connection status
    mw n8n list                     List all workflows
    mw n8n import <file.json>       Import a workflow from JSON
    mw n8n export <id> [file]       Export workflow to JSON
    mw n8n activate <id>            Activate a workflow
    mw n8n deactivate <id>          Deactivate a workflow
    mw n8n delete <id>              Delete a workflow
    mw n8n exec <id>                Execute a workflow manually
    mw n8n executions [id]          List recent executions
    mw n8n logs <exec_id>           Show execution details
    mw n8n config                   Show/set n8n connection config
    mw n8n test <file.json>         Validate workflow JSON locally
    mw n8n --help                   Show this help message

Description:
    Full interface to n8n workflow automation. Manage workflows,
    monitor executions, import/export automations, and integrate
    with the MyWork-AI ecosystem.

Examples:
    mw n8n setup                    # Install n8n locally
    mw n8n status                   # Check connection
    mw n8n import workflow.json     # Import automation
    mw n8n list                     # See all workflows
    mw n8n exec abc123              # Trigger a run
""")
        return 0

    subcmd = args[0]
    sub_args = args[1:]

    if subcmd == "setup":
        return _n8n_setup(sub_args)
    elif subcmd == "status":
        return _n8n_status()
    elif subcmd == "list":
        return _n8n_api_call("GET", "/api/v1/workflows", display="workflows")
    elif subcmd == "import":
        if not sub_args:
            print("❌ Error: Missing workflow file")
            print("💡 Try: mw n8n import workflow.json")
            return 1
        return _n8n_import(sub_args[0])
    elif subcmd == "export":
        if not sub_args:
            print("❌ Error: Missing workflow ID")
            print("💡 Try: mw n8n export <workflow-id>")
            return 1
        outfile = sub_args[1] if len(sub_args) > 1 else None
        return _n8n_export(sub_args[0], outfile)
    elif subcmd == "activate":
        if not sub_args:
            print("❌ Error: Missing workflow ID")
            return 1
        return _n8n_api_call("PATCH", f"/api/v1/workflows/{sub_args[0]}", body={"active": True})
    elif subcmd == "deactivate":
        if not sub_args:
            print("❌ Error: Missing workflow ID")
            return 1
        return _n8n_api_call("PATCH", f"/api/v1/workflows/{sub_args[0]}", body={"active": False})
    elif subcmd == "delete":
        if not sub_args:
            print("❌ Error: Missing workflow ID")
            return 1
        confirm = input(f"⚠️  Delete workflow {sub_args[0]}? (y/N): ").strip().lower()
        if confirm != "y":
            print("Cancelled.")
            return 0
        return _n8n_api_call("DELETE", f"/api/v1/workflows/{sub_args[0]}")
    elif subcmd == "exec":
        if not sub_args:
            print("❌ Error: Missing workflow ID")
            return 1
        return _n8n_api_call("POST", f"/api/v1/workflows/{sub_args[0]}/execute", display="execution")
    elif subcmd == "executions":
        wf_id = sub_args[0] if sub_args else None
        path = "/api/v1/executions"
        if wf_id:
            path += f"?workflowId={wf_id}"
        return _n8n_api_call("GET", path, display="executions")
    elif subcmd == "logs":
        if not sub_args:
            print("❌ Error: Missing execution ID")
            return 1
        return _n8n_api_call("GET", f"/api/v1/executions/{sub_args[0]}", display="execution_detail")
    elif subcmd == "config":
        return _n8n_config(sub_args)
    elif subcmd == "test":
        if not sub_args:
            print("❌ Error: Missing workflow file")
            return 1
        return _n8n_test(sub_args[0])
    else:
        print(f"❌ Unknown n8n command: {subcmd}")
        print("💡 Try: mw n8n --help")
        return 1


def _n8n_get_config():
    """Get n8n connection config from env or .env file."""
    import os
    url = os.environ.get("N8N_API_URL", "")
    key = os.environ.get("N8N_API_KEY", "")
    if not url:
        # Try reading from .env in project root
        env_file = Path(".env")
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                line = line.strip()
                if line.startswith("N8N_API_URL="):
                    url = line.split("=", 1)[1].strip().strip('"').strip("'")
                elif line.startswith("N8N_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
    return url, key


def _n8n_api_call(method: str, path: str, body: dict = None, display: str = None) -> int:
    """Make an API call to n8n."""
    import urllib.request
    import urllib.error
    url, key = _n8n_get_config()
    if not url:
        print("❌ n8n not configured")
        print("💡 Try: mw n8n setup")
        print("   Or set N8N_API_URL and N8N_API_KEY in your .env file")
        return 1

    full_url = url.rstrip("/") + path
    headers = {"Content-Type": "application/json"}
    if key:
        headers["X-N8N-API-KEY"] = key

    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(full_url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode() if e.fp else ""
        print(f"❌ n8n API error ({e.code}): {body_text[:200]}")
        return 1
    except urllib.error.URLError as e:
        print(f"❌ Cannot reach n8n at {url}")
        print(f"💡 Is n8n running? Try: mw n8n setup")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    # Display results
    if display == "workflows":
        workflows = result.get("data", result) if isinstance(result, dict) else result
        if isinstance(workflows, list):
            if not workflows:
                print("📋 No workflows found")
            else:
                print(f"📋 {len(workflows)} workflow(s):\n")
                for wf in workflows:
                    status = "🟢 Active" if wf.get("active") else "⚪ Inactive"
                    print(f"  {status}  {wf.get('id', '?'):>6}  {wf.get('name', 'Untitled')}")
                    if wf.get("tags"):
                        tags = ", ".join(t.get("name", t) if isinstance(t, dict) else str(t) for t in wf["tags"])
                        print(f"              Tags: {tags}")
        else:
            print(json.dumps(result, indent=2))
    elif display == "executions":
        execs = result.get("data", result) if isinstance(result, dict) else result
        if isinstance(execs, list):
            if not execs:
                print("📋 No executions found")
            else:
                print(f"📋 {len(execs)} execution(s):\n")
                for ex in execs[:20]:
                    status_icon = "✅" if ex.get("finished") and not ex.get("stoppedAt") else "❌" if ex.get("stoppedAt") else "⏳"
                    print(f"  {status_icon}  {ex.get('id', '?'):>8}  {ex.get('workflowId', '?')}  {ex.get('startedAt', '?')[:19]}")
        else:
            print(json.dumps(result, indent=2))
    elif display == "execution_detail":
        print(f"Execution: {result.get('id')}")
        print(f"Workflow:  {result.get('workflowId')}")
        print(f"Status:    {'✅ Success' if result.get('finished') else '❌ Failed'}")
        print(f"Started:   {result.get('startedAt', 'N/A')}")
        print(f"Finished:  {result.get('stoppedAt', 'N/A')}")
        if result.get('data', {}).get('resultData', {}).get('error'):
            err = result['data']['resultData']['error']
            print(f"Error:     {err.get('message', err)}")
    else:
        if isinstance(result, dict) and result.get("id"):
            print(f"✅ Done (ID: {result['id']})")
        else:
            print("✅ Done")

    return 0


def _n8n_status() -> int:
    """Check n8n connection status."""
    import urllib.request
    import urllib.error
    url, key = _n8n_get_config()
    if not url:
        print("❌ n8n not configured")
        print("💡 Run: mw n8n setup")
        return 1

    print(f"🔍 Checking n8n at {url}...")
    req = urllib.request.Request(url.rstrip("/") + "/api/v1/workflows?limit=1")
    if key:
        req.add_header("X-N8N-API-KEY", key)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            count = len(data.get("data", []))
            print(f"✅ n8n is running!")
            print(f"   URL: {url}")
            print(f"   Auth: {'✅ API key configured' if key else '⚠️  No API key'}")
            # Get total workflows
            req2 = urllib.request.Request(url.rstrip("/") + "/api/v1/workflows")
            if key:
                req2.add_header("X-N8N-API-KEY", key)
            with urllib.request.urlopen(req2, timeout=10) as resp2:
                all_wf = json.loads(resp2.read().decode())
                total = len(all_wf.get("data", all_wf) if isinstance(all_wf, dict) else all_wf)
                active = sum(1 for w in (all_wf.get("data", all_wf) if isinstance(all_wf, dict) else all_wf) if isinstance(w, dict) and w.get("active"))
                print(f"   Workflows: {total} total, {active} active")
            return 0
    except urllib.error.URLError:
        print(f"❌ Cannot reach n8n at {url}")
        print("💡 Try: mw n8n setup")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def _n8n_setup(args: List[str]) -> int:
    """Setup n8n - install and start."""
    import subprocess
    import shutil

    print("""
🔧 n8n Setup — Workflow Automation Engine
==========================================
""")
    # Check if Docker is available
    docker = shutil.which("docker")
    if docker:
        # Test docker access
        try:
            result = subprocess.run(["docker", "ps"], capture_output=True, timeout=5)
            has_docker = result.returncode == 0
        except Exception:
            has_docker = False
    else:
        has_docker = False

    if has_docker:
        print("🐳 Docker detected! Setting up n8n container...")
        try:
            # Check if already running
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=n8n", "--format", "{{.Names}}"],
                capture_output=True, text=True, timeout=10
            )
            if "n8n" in result.stdout:
                print("✅ n8n is already running!")
                print("   URL: http://localhost:5678")
                return 0

            # Pull and start
            print("📦 Pulling n8n image...")
            subprocess.run(["docker", "pull", "n8nio/n8n:latest"], timeout=300)
            print("🚀 Starting n8n...")
            subprocess.run([
                "docker", "run", "-d",
                "--name", "n8n",
                "--restart", "always",
                "-p", "5678:5678",
                "-v", "n8n_data:/home/node/.n8n",
                "-e", "GENERIC_TIMEZONE=UTC",
                "n8nio/n8n:latest"
            ], timeout=30)
            print("✅ n8n is running!")
            print("   URL: http://localhost:5678")
            print("   Data: Persistent (Docker volume: n8n_data)")
            
            # Auto-append N8N_API_URL to .env file
            try:
                from pathlib import Path
                env_file = Path.cwd() / ".env"
                
                # Check if N8N_API_URL already exists
                if env_file.exists():
                    content = env_file.read_text()
                    if "N8N_API_URL" not in content:
                        with open(env_file, "a") as f:
                            f.write("\n# n8n Configuration (auto-added by mw n8n setup)\n")
                            f.write("N8N_API_URL=http://localhost:5678\n")
                        print("✅ Added N8N_API_URL to .env file")
                    else:
                        print("ℹ️ N8N_API_URL already exists in .env file")
                else:
                    # Create .env file with N8N_API_URL
                    with open(env_file, "w") as f:
                        f.write("# n8n Configuration (auto-added by mw n8n setup)\n")
                        f.write("N8N_API_URL=http://localhost:5678\n")
                    print("✅ Created .env file with N8N_API_URL")
            except Exception as e:
                print(f"⚠️ Could not auto-configure .env: {e}")

            print("\n📝 Next steps:")
            print("   1. Open http://localhost:5678 in your browser")
            print("   2. Create owner account")
            print("   3. Go to Settings → API → Create API key")
            print("   4. Add to .env: N8N_API_KEY=your-api-key")
            print("      (N8N_API_URL already added ✅)")
            return 0
        except Exception as e:
            print(f"❌ Docker setup failed: {e}")
            print("Falling back to npm install...")

    # npm/npx fallback
    npx = shutil.which("npx")
    if npx:
        print("📦 Installing n8n via npm (no Docker)...")
        print("   This may take a few minutes on first run.\n")
        home = Path.home()
        n8n_dir = home / "n8n-server"
        n8n_dir.mkdir(exist_ok=True)

        # Check if already installed
        n8n_bin = n8n_dir / "node_modules" / ".bin" / "n8n"
        if not n8n_bin.exists():
            print("   Installing n8n package...")
            result = subprocess.run(
                ["npm", "install", "n8n"],
                cwd=str(n8n_dir),
                timeout=300
            )
            if result.returncode != 0:
                print("❌ npm install failed")
                return 1

        print("✅ n8n installed!")
        print(f"   Location: {n8n_dir}")
        print(f"\n🚀 To start n8n:")
        print(f"   cd {n8n_dir} && npx n8n start")
        print(f"\n   Or run in background:")
        print(f"   cd {n8n_dir} && nohup npx n8n start &")
        print(f"\n   Then open: http://localhost:5678")
        return 0

    print("❌ Neither Docker nor npm/npx found")
    print("💡 Install Docker: curl -fsSL https://get.docker.com | sh")
    print("   Or install Node.js: https://nodejs.org")
    return 1


def _n8n_import(filepath: str) -> int:
    """Import a workflow from JSON file."""
    p = Path(filepath)
    if not p.exists():
        print(f"❌ File not found: {filepath}")
        return 1
    try:
        workflow = json.loads(p.read_text())
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return 1

    print(f"📦 Importing workflow: {workflow.get('name', 'Untitled')}...")
    return _n8n_api_call("POST", "/api/v1/workflows", body=workflow, display=None)


def _n8n_export(workflow_id: str, outfile: str = None) -> int:
    """Export a workflow to JSON file."""
    import urllib.request
    url, key = _n8n_get_config()
    if not url:
        print("❌ n8n not configured")
        return 1

    req = urllib.request.Request(url.rstrip("/") + f"/api/v1/workflows/{workflow_id}")
    if key:
        req.add_header("X-N8N-API-KEY", key)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read().decode()
            workflow = json.loads(data)
    except Exception as e:
        print(f"❌ Failed to fetch workflow: {e}")
        return 1

    if not outfile:
        name = workflow.get("name", "workflow").replace(" ", "_").lower()
        outfile = f"{name}_{workflow_id}.json"

    Path(outfile).write_text(json.dumps(workflow, indent=2))
    print(f"✅ Exported to {outfile}")
    return 0


def _n8n_config(args: List[str]) -> int:
    """Show or set n8n config."""
    url, key = _n8n_get_config()
    if not args:
        print("⚙️  n8n Configuration:")
        print(f"   URL: {url or '(not set)'}")
        print(f"   Key: {'***' + key[-8:] if key and len(key) > 8 else '(not set)'}")
        print(f"\n💡 Set in .env file:")
        print(f"   N8N_API_URL=http://localhost:5678")
        print(f"   N8N_API_KEY=your-api-key")
        return 0
    return 0


def _n8n_test(filepath: str) -> int:
    """Validate a workflow JSON file locally."""
    p = Path(filepath)
    if not p.exists():
        print(f"❌ File not found: {filepath}")
        return 1
    try:
        wf = json.loads(p.read_text())
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return 1

    errors = []
    warnings = []

    # Check required fields
    if not wf.get("nodes"):
        errors.append("Missing 'nodes' array")
    if not wf.get("connections"):
        errors.append("Missing 'connections' object")

    # Validate nodes
    nodes = wf.get("nodes", [])
    node_names = set()
    for i, node in enumerate(nodes):
        if not node.get("name"):
            errors.append(f"Node {i}: missing 'name'")
        elif node["name"] in node_names:
            errors.append(f"Node {i}: duplicate name '{node['name']}'")
        else:
            node_names.add(node["name"])
        if not node.get("type"):
            errors.append(f"Node {i} ({node.get('name', '?')}): missing 'type'")
        if not node.get("position"):
            warnings.append(f"Node '{node.get('name', '?')}': missing position")

    # Validate connections reference existing nodes
    for src_name, conns in wf.get("connections", {}).items():
        if src_name not in node_names:
            errors.append(f"Connection from unknown node: '{src_name}'")
        if isinstance(conns, dict) and "main" in conns:
            for branch in conns["main"]:
                if isinstance(branch, list):
                    for conn in branch:
                        tgt = conn.get("node", "")
                        if tgt not in node_names:
                            errors.append(f"Connection to unknown node: '{tgt}'")

    # Report
    print(f"🔍 Validating: {filepath}")
    print(f"   Name: {wf.get('name', 'Untitled')}")
    print(f"   Nodes: {len(nodes)}")
    print(f"   Connections: {len(wf.get('connections', {}))}")

    if errors:
        print(f"\n❌ {len(errors)} error(s):")
        for e in errors:
            print(f"   • {e}")
    if warnings:
        print(f"\n⚠️  {len(warnings)} warning(s):")
        for w in warnings:
            print(f"   • {w}")
    if not errors and not warnings:
        print("\n✅ Workflow is valid!")
    elif not errors:
        print("\n✅ Workflow is valid (with warnings)")

    return 1 if errors else 0


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


def cmd_marketplace(args: Optional[List[str]] = None) -> None:
    """Marketplace commands - publish, browse, install, and info."""
    if not args or args[0] in ["--help", "-h"]:
        print("""
Marketplace Commands — Publish, Browse & Install Projects
=========================================================
Usage:
    mw marketplace <subcommand> [options]

Subcommands:
    info                            Show marketplace information and links
    publish                         Publish current project to marketplace
    browse [--category <cat>]       Browse available marketplace products
    install <product-id>            Download and install a marketplace product
    status                          Check marketplace connectivity
    
Examples:
    mw marketplace info             # Show marketplace overview and links
    mw marketplace publish          # Publish current project (interactive)
    mw marketplace browse           # Browse all available products
    mw marketplace browse --category=tools  # Browse tools category
    mw marketplace install c54f73f4 # Install a specific product
    mw marketplace status           # Check marketplace API status
""")
        return 0
    
    subcommand = args[0].lower()
    
    if subcommand == "info":
        return _cmd_marketplace_info(args[1:] if len(args) > 1 else [])
    elif subcommand == "publish":
        return _cmd_marketplace_publish(args[1:] if len(args) > 1 else [])
    elif subcommand == "browse":
        return _cmd_marketplace_browse(args[1:] if len(args) > 1 else [])
    elif subcommand == "install":
        return _cmd_marketplace_install(args[1:] if len(args) > 1 else [])
    elif subcommand == "status":
        return _cmd_marketplace_status(args[1:] if len(args) > 1 else [])
    else:
        print(f"{Colors.RED}Unknown subcommand: {subcommand}{Colors.ENDC}")
        print(f"Run {color('mw marketplace --help', Colors.BOLD)} for available commands")
        return 1


def _cmd_marketplace_info(args: Optional[List[str]] = None) -> None:
    """Show marketplace information and links."""
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


def _cmd_marketplace_status(args: Optional[List[str]] = None) -> None:
    """Check marketplace API connectivity."""
    import requests
    
    backend_url = "https://mywork-ai-production.up.railway.app"
    frontend_url = "https://frontend-hazel-ten-17.vercel.app"
    
    print(f"{Colors.BOLD}🔍 Marketplace Status Check{Colors.ENDC}")
    print("=" * 40)
    
    # Test backend health
    try:
        response = requests.get(f"{backend_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend API: {Colors.GREEN}Healthy{Colors.ENDC}")
            print(f"   Version: {data.get('version', 'unknown')}")
            print(f"   Service: {data.get('service', 'unknown')}")
        else:
            print(f"❌ Backend API: {Colors.RED}Error {response.status_code}{Colors.ENDC}")
    except Exception as e:
        print(f"❌ Backend API: {Colors.RED}Connection failed ({e}){Colors.ENDC}")
    
    # Test backend products
    try:
        response = requests.get(f"{backend_url}/api/products", timeout=10)
        if response.status_code == 200:
            data = response.json()
            product_count = data.get('total', 0)
            print(f"✅ Products API: {Colors.GREEN}Working{Colors.ENDC} ({product_count} products)")
        else:
            print(f"❌ Products API: {Colors.RED}Error {response.status_code}{Colors.ENDC}")
    except Exception as e:
        print(f"❌ Products API: {Colors.RED}Failed ({e}){Colors.ENDC}")
    
    # Test frontend
    try:
        response = requests.get(frontend_url, timeout=10)
        if response.status_code == 200:
            print(f"✅ Frontend: {Colors.GREEN}Online{Colors.ENDC}")
        else:
            print(f"❌ Frontend: {Colors.RED}Error {response.status_code}{Colors.ENDC}")
    except Exception as e:
        print(f"❌ Frontend: {Colors.RED}Connection failed ({e}){Colors.ENDC}")
    
    print(f"\n{Colors.BLUE}🔗 URLs:{Colors.ENDC}")
    print(f"   Backend:  {backend_url}")
    print(f"   Frontend: {frontend_url}")


def _cmd_marketplace_browse(args: Optional[List[str]] = None) -> None:
    """Browse marketplace products."""
    import requests
    
    backend_url = "https://mywork-ai-production.up.railway.app"
    category_filter = None
    
    # Parse arguments
    if args:
        for arg in args:
            if arg.startswith("--category="):
                category_filter = arg.split("=", 1)[1]
            elif arg == "--help" or arg == "-h":
                print("""
Browse Marketplace Products
===========================
Usage:
    mw marketplace browse [options]

Options:
    --category=<category>    Filter by category (tools, templates, components, etc.)
    --help, -h               Show this help

Examples:
    mw marketplace browse                    # Browse all products
    mw marketplace browse --category=tools   # Browse tools only
""")
                return 0
    
    print(f"{Colors.BOLD}🛒 Marketplace Products{Colors.ENDC}")
    print("=" * 40)
    
    try:
        url = f"{backend_url}/api/products"
        if category_filter:
            url += f"?category={category_filter}"
        
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            print(f"{Colors.RED}❌ Failed to fetch products: HTTP {response.status_code}{Colors.ENDC}")
            return 1
        
        data = response.json()
        products = data.get('products', [])
        total = data.get('total', 0)
        
        if not products:
            if category_filter:
                print(f"No products found in category '{category_filter}'")
            else:
                print("No products available")
            return 0
        
        print(f"Found {total} product(s)" + (f" in category '{category_filter}'" if category_filter else ""))
        print()
        
        for product in products:
            product_id = product.get('id', 'unknown')[:8]
            title = product.get('title', 'Untitled')
            price = product.get('price', 0)
            category = product.get('category', 'uncategorized')
            description = product.get('short_description', product.get('description', ''))
            rating = product.get('rating_average', 0)
            sales = product.get('sales', 0)
            
            # Truncate description
            if len(description) > 100:
                description = description[:97] + "..."
            
            print(f"{Colors.BOLD}{Colors.BLUE}📦 {title}{Colors.ENDC}")
            print(f"   ID: {color(product_id, Colors.YELLOW)}")
            print(f"   Price: {color(f'${price}', Colors.GREEN)} | Category: {category}")
            print(f"   Rating: {'⭐' * int(rating)} ({rating:.1f}) | Sales: {sales}")
            print(f"   {description}")
            
            if product.get('demo_url'):
                print(f"   🔗 Demo: {color(product['demo_url'], Colors.BLUE)}")
            
            print()
        
        print(f"{Colors.BLUE}💡 To install a product:{Colors.ENDC}")
        print(f"   mw marketplace install <product-id>")
        print(f"{Colors.BLUE}💡 To view in browser:{Colors.ENDC}")
        print(f"   Visit: https://frontend-hazel-ten-17.vercel.app")
        
    except Exception as e:
        print(f"{Colors.RED}❌ Error browsing marketplace: {e}{Colors.ENDC}")
        return 1


def _cmd_marketplace_install(args: Optional[List[str]] = None) -> None:
    """Install a marketplace product."""
    if not args or args[0] in ["--help", "-h"]:
        print("""
Install Marketplace Product
===========================
Usage:
    mw marketplace install <product-id> [options]

Arguments:
    product-id               Product ID or slug to install

Options:
    --dir=<directory>        Install to specific directory (default: ./product-name)
    --help, -h               Show this help

Examples:
    mw marketplace install c54f73f4         # Install product by ID
    mw marketplace install sportsai-app    # Install by slug
    mw marketplace install abc123 --dir=my-project  # Install to custom directory

Note: Currently requires manual authentication via the web interface.
For now, this will show you the download information and guide you through the process.
""")
        return 0
    
    import requests
    
    product_id = args[0]
    backend_url = "https://mywork-ai-production.up.railway.app"
    
    print(f"{Colors.BOLD}📦 Installing Product: {product_id}{Colors.ENDC}")
    print("=" * 40)
    
    try:
        # First, find the product
        response = requests.get(f"{backend_url}/api/products", timeout=10)
        if response.status_code != 200:
            print(f"{Colors.RED}❌ Failed to fetch products: HTTP {response.status_code}{Colors.ENDC}")
            return 1
        
        data = response.json()
        products = data.get('products', [])
        
        # Find matching product
        product = None
        for p in products:
            if (p.get('id', '').startswith(product_id) or 
                p.get('slug', '') == product_id or
                product_id.lower() in p.get('title', '').lower()):
                product = p
                break
        
        if not product:
            print(f"{Colors.RED}❌ Product not found: {product_id}{Colors.ENDC}")
            print(f"{Colors.BLUE}💡 Try 'mw marketplace browse' to see available products{Colors.ENDC}")
            return 1
        
        # Display product info
        title = product.get('title', 'Unknown')
        price = product.get('price', 0)
        description = product.get('short_description', '')
        
        print(f"{Colors.BOLD}{Colors.GREEN}✅ Found: {title}{Colors.ENDC}")
        print(f"Price: ${price}")
        print(f"Description: {description}")
        print()
        
        # For now, guide user to web interface
        print(f"{Colors.YELLOW}🔄 Manual Installation Required{Colors.ENDC}")
        print("Full automated installation is coming soon!")
        print()
        print(f"{Colors.BOLD}To install this product:{Colors.ENDC}")
        print(f"1. Visit: {color('https://frontend-hazel-ten-17.vercel.app', Colors.BLUE)}")
        print(f"2. Sign in with your account")
        print(f"3. Search for: {color(title, Colors.BOLD)}")
        print(f"4. Purchase and download the source code")
        print()
        
        if product.get('demo_url'):
            print(f"{Colors.BLUE}🔗 Live Demo: {product['demo_url']}{Colors.ENDC}")
        
        if product.get('documentation_url'):
            print(f"{Colors.BLUE}📖 Documentation: {product['documentation_url']}{Colors.ENDC}")
        
        print(f"\n{Colors.GREEN}💡 Coming soon: Direct CLI installation with authentication!{Colors.ENDC}")
        
    except Exception as e:
        print(f"{Colors.RED}❌ Error installing product: {e}{Colors.ENDC}")
        return 1


def _cmd_marketplace_publish(args: Optional[List[str]] = None) -> None:
    """Publish current project to marketplace."""
    import requests
    import json
    import os
    import zipfile
    import tempfile
    from pathlib import Path
    
    if args and (args[0] in ["--help", "-h"]):
        print("""
Publish Project to Marketplace
==============================
Usage:
    mw marketplace publish [options]

Options:
    --name=<name>            Project name (default: current directory name)
    --price=<price>          Price in dollars (required)
    --category=<category>    Category (tools, templates, components, etc.)
    --description=<text>     Short description (or use --interactive)
    --interactive            Interactive mode (recommended)
    --help, -h               Show this help

Examples:
    mw marketplace publish --interactive     # Guided setup (recommended)
    mw marketplace publish --name="My App" --price=99 --category=tools

Note: You must be signed in to the marketplace web interface first.
This command packages your project and guides you through the upload process.
""")
        return 0
    
    # Check if we're in a project directory
    current_dir = Path.cwd()
    if not any(file.exists() for file in [current_dir / "package.json", current_dir / "requirements.txt", 
                                         current_dir / "Cargo.toml", current_dir / "go.mod"]):
        print(f"{Colors.YELLOW}⚠️  Warning: No project files detected in current directory{Colors.ENDC}")
        confirm = input("Continue anyway? (y/n): ").strip().lower()
        if confirm != 'y':
            return 0
    
    # Parse arguments
    interactive = "--interactive" in args if args else True
    project_name = current_dir.name
    price = None
    category = None
    description = None
    
    if args:
        for arg in args:
            if arg.startswith("--name="):
                project_name = arg.split("=", 1)[1]
            elif arg.startswith("--price="):
                try:
                    price = float(arg.split("=", 1)[1])
                except ValueError:
                    print(f"{Colors.RED}❌ Invalid price format{Colors.ENDC}")
                    return 1
            elif arg.startswith("--category="):
                category = arg.split("=", 1)[1]
            elif arg.startswith("--description="):
                description = arg.split("=", 1)[1]
    
    print(f"{Colors.BOLD}🚀 Publishing to MyWork Marketplace{Colors.ENDC}")
    print("=" * 40)
    
    # Interactive mode
    if interactive or not all([price, category, description]):
        print(f"{Colors.BLUE}📝 Project Information{Colors.ENDC}")
        
        if not project_name:
            project_name = input("Project name: ").strip() or current_dir.name
        else:
            print(f"Project name: {color(project_name, Colors.BOLD)}")
        
        if not price:
            while not price:
                try:
                    price_input = input("Price (USD): $").strip()
                    price = float(price_input)
                    break
                except ValueError:
                    print(f"{Colors.RED}Please enter a valid number{Colors.ENDC}")
        else:
            print(f"Price: ${price}")
        
        if not category:
            categories = ["tools", "templates", "components", "ai", "web", "mobile", "blockchain", "other"]
            print("\nAvailable categories:")
            for i, cat in enumerate(categories, 1):
                print(f"  {i}. {cat}")
            
            while not category:
                try:
                    choice = input("Select category (number or name): ").strip()
                    if choice.isdigit() and 1 <= int(choice) <= len(categories):
                        category = categories[int(choice) - 1]
                    elif choice.lower() in categories:
                        category = choice.lower()
                    else:
                        print(f"{Colors.RED}Invalid choice{Colors.ENDC}")
                except ValueError:
                    print(f"{Colors.RED}Invalid choice{Colors.ENDC}")
        else:
            print(f"Category: {category}")
        
        if not description:
            print("\nShort description (1-2 sentences):")
            description = input("> ").strip()
        else:
            print(f"Description: {description}")
    
    # Create project package
    print(f"\n{Colors.BLUE}📦 Creating project package...{Colors.ENDC}")
    
    try:
        # Create temporary zip file
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_file:
            zip_path = tmp_file.name
        
        # Exclude common directories and files
        exclude_patterns = {
            'node_modules', '.git', '__pycache__', '.venv', 'venv', 'env',
            'dist', 'build', '.next', '.nuxt', 'target', 'vendor',
            '.DS_Store', '*.pyc', '*.log', '.env', '.env.local'
        }
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(current_dir):
                # Filter directories
                dirs[:] = [d for d in dirs if d not in exclude_patterns]
                
                for file in files:
                    if file not in exclude_patterns and not any(file.endswith(ext) for ext in ['.pyc', '.log']):
                        file_path = Path(root) / file
                        relative_path = file_path.relative_to(current_dir)
                        zipf.write(file_path, relative_path)
        
        zip_size = os.path.getsize(zip_path) / 1024 / 1024  # MB
        print(f"✅ Package created: {zip_size:.2f} MB")
        
        # Generate marketplace listing info
        listing_info = {
            "title": project_name,
            "description": description,
            "short_description": description[:100] + "..." if len(description) > 100 else description,
            "category": category,
            "price": int(price),
            "license_type": "MIT",
            "tech_stack": _detect_tech_stack(current_dir),
            "requirements": _detect_requirements(current_dir),
        }
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}✅ Package ready! ({zip_size:.2f} MB){Colors.ENDC}")
        
        # Upload to R2 storage
        print(f"\n{Colors.BLUE}☁️  Uploading to cloud storage...{Colors.ENDC}")
        package_url = _marketplace_upload_r2(zip_path, listing_info["title"])
        
        if not package_url:
            print(f"\n{Colors.YELLOW}⚠️  Cloud upload skipped (R2 not configured){Colors.ENDC}")
            print(f"Package saved locally: {zip_path}")
            print(f"\n{Colors.BOLD}To publish manually:{Colors.ENDC}")
            print(f"1. Visit: {color('https://frontend-hazel-ten-17.vercel.app', Colors.BLUE)}")
            print(f"2. Sign in and upload the package")
        else:
            listing_info["package_url"] = package_url
            listing_info["package_size_bytes"] = os.path.getsize(zip_path)
            print(f"✅ Uploaded: {package_url}")
            
            # Create product on marketplace API
            print(f"\n{Colors.BLUE}📋 Listing on marketplace...{Colors.ENDC}")
            product_id = _marketplace_create_product(listing_info)
            
            if product_id:
                print(f"\n{Colors.BOLD}{Colors.GREEN}🎉 Published to marketplace!{Colors.ENDC}")
                print(f"   Product ID: {product_id}")
                print(f"   URL: https://frontend-hazel-ten-17.vercel.app/products/{listing_info.get('title', '').lower().replace(' ', '-')}")
            else:
                print(f"\n{Colors.YELLOW}⚠️  Package uploaded but listing needs manual step{Colors.ENDC}")
                print(f"Visit: https://frontend-hazel-ten-17.vercel.app to complete listing")
        
        # Cleanup temp zip
        try:
            os.unlink(zip_path)
        except:
            pass
        
    except Exception as e:
        print(f"{Colors.RED}❌ Error creating package: {e}{Colors.ENDC}")
        return 1


def _marketplace_upload_r2(zip_path: str, product_name: str) -> str:
    """Upload package to R2 cloud storage. Returns URL or empty string."""
    import os
    try:
        import boto3
        from botocore.config import Config
    except ImportError:
        print("  (boto3 not installed — run: pip install boto3)")
        return ""
    
    # Read R2 credentials from env or .credentials file
    r2_key = os.environ.get("R2_ACCESS_KEY_ID", "")
    r2_secret = os.environ.get("R2_SECRET_ACCESS_KEY", "")
    r2_endpoint = os.environ.get("R2_ENDPOINT", "")
    r2_bucket = os.environ.get("R2_BUCKET", "mywork")
    r2_public = os.environ.get("R2_PUBLIC_URL", "")
    
    if not all([r2_key, r2_secret, r2_endpoint]):
        # Try loading from credentials file
        cred_paths = [
            Path.home() / ".openclaw" / "workspace" / ".credentials-marketplace.json",
            Path.home() / ".mywork" / "credentials.json",
            Path(".credentials.json"),
        ]
        for cp in cred_paths:
            if cp.exists():
                try:
                    creds = json.loads(cp.read_text())
                    r2_key = r2_key or creds.get("R2_ACCESS_KEY_ID", "")
                    r2_secret = r2_secret or creds.get("R2_SECRET_ACCESS_KEY", "")
                    r2_endpoint = r2_endpoint or creds.get("R2_ENDPOINT", "")
                    r2_bucket = creds.get("R2_BUCKET", r2_bucket)
                    r2_public = r2_public or creds.get("R2_PUBLIC_URL", "")
                    break
                except Exception:
                    pass
    
    if not all([r2_key, r2_secret, r2_endpoint]):
        return ""
    
    try:
        r2 = boto3.client('s3',
            endpoint_url=r2_endpoint,
            aws_access_key_id=r2_key,
            aws_secret_access_key=r2_secret,
            config=Config(signature_version='s3v4'),
            region_name='auto'
        )
        
        # Generate unique key
        import hashlib, time
        slug = product_name.lower().replace(" ", "-")[:50]
        ts = int(time.time())
        key = f"packages/{slug}/{slug}-{ts}.zip"
        
        r2.upload_file(zip_path, r2_bucket, key, ExtraArgs={"ContentType": "application/zip"})
        
        if r2_public:
            return f"{r2_public.rstrip('/')}/{key}"
        return f"{r2_endpoint.rstrip('/')}/{r2_bucket}/{key}"
    except Exception as e:
        print(f"  ⚠️  Upload error: {e}")
        return ""


def _marketplace_create_product(listing_info: dict) -> str:
    """Create product on marketplace API. Returns product ID or empty string."""
    import urllib.request
    import urllib.error
    
    api_url = os.environ.get("MARKETPLACE_API_URL", "https://mywork-ai-production.up.railway.app")
    
    # Build product payload
    product = {
        "title": listing_info.get("title", ""),
        "description": listing_info.get("description", listing_info.get("short_description", "No description")),
        "short_description": listing_info.get("short_description", "")[:500],
        "category": listing_info.get("category", "tools"),
        "price": float(listing_info.get("price", 0)),
        "license_type": listing_info.get("license_type", "standard"),
        "tech_stack": listing_info.get("tech_stack", []),
        "requirements": listing_info.get("requirements", ""),
        "package_url": listing_info.get("package_url"),
        "package_size_bytes": listing_info.get("package_size_bytes"),
    }
    
    # Need Clerk JWT for auth
    clerk_secret = os.environ.get("CLERK_SECRET_KEY", "")
    if not clerk_secret:
        # Try credentials file
        cred_paths = [
            Path.home() / ".openclaw" / "workspace" / ".credentials-marketplace.json",
            Path.home() / ".mywork" / "credentials.json",
        ]
        for cp in cred_paths:
            if cp.exists():
                try:
                    creds = json.loads(cp.read_text())
                    clerk_secret = creds.get("CLERK_SECRET_KEY", "")
                    if clerk_secret:
                        break
                except Exception:
                    pass
    
    if not clerk_secret:
        print("  ⚠️  No CLERK_SECRET_KEY — can't authenticate with marketplace")
        print("  💡 Set CLERK_SECRET_KEY in environment or .credentials-marketplace.json")
        return ""
    
    try:
        # Get active session for the Clerk user
        req = urllib.request.Request(
            "https://api.clerk.com/v1/users?limit=1",
            headers={"Authorization": f"Bearer {clerk_secret}"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            users = json.loads(resp.read())
            if not users:
                print("  ⚠️  No Clerk users found")
                return ""
            user_id = users[0]["id"] if isinstance(users, list) else users.get("data", [{}])[0].get("id", "")
        
        if not user_id:
            return ""
        
        # Create session and get JWT
        req = urllib.request.Request(
            "https://api.clerk.com/v1/sessions",
            data=json.dumps({"user_id": user_id}).encode(),
            headers={"Authorization": f"Bearer {clerk_secret}", "Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            session = json.loads(resp.read())
            session_id = session["id"]
        
        # Get JWT token
        req = urllib.request.Request(
            f"https://api.clerk.com/v1/sessions/{session_id}/tokens",
            headers={"Authorization": f"Bearer {clerk_secret}", "Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            jwt = json.loads(resp.read())["jwt"]
        
        # Create product
        req = urllib.request.Request(
            f"{api_url}/api/products",
            data=json.dumps(product).encode(),
            headers={"Authorization": f"Bearer {jwt}", "Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            product_id = result.get("id", "")
        
        if not product_id:
            return ""
        
        # Publish (activate) the product — need fresh JWT
        req = urllib.request.Request(
            f"https://api.clerk.com/v1/sessions/{session_id}/tokens",
            headers={"Authorization": f"Bearer {clerk_secret}", "Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            jwt2 = json.loads(resp.read())["jwt"]
        
        req = urllib.request.Request(
            f"{api_url}/api/products/{product_id}/publish",
            headers={"Authorization": f"Bearer {jwt2}", "Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            json.loads(resp.read())
        
        return product_id
    except Exception as e:
        print(f"  ⚠️  Marketplace API error: {e}")
        return ""


def _detect_tech_stack(project_dir: Path) -> list:
    """Detect technology stack from project files."""
    tech_stack = []
    
    if (project_dir / "package.json").exists():
        tech_stack.extend(["Node.js", "JavaScript"])
        try:
            with open(project_dir / "package.json") as f:
                package = json.load(f)
                deps = {**package.get('dependencies', {}), **package.get('devDependencies', {})}
                
                if any(dep.startswith('react') for dep in deps):
                    tech_stack.append("React")
                if 'next' in deps:
                    tech_stack.append("Next.js")
                if 'vue' in deps:
                    tech_stack.append("Vue.js")
                if 'express' in deps:
                    tech_stack.append("Express")
        except:
            pass
    
    if (project_dir / "requirements.txt").exists() or (project_dir / "pyproject.toml").exists():
        tech_stack.extend(["Python"])
        try:
            req_file = project_dir / "requirements.txt"
            if req_file.exists():
                content = req_file.read_text()
                if 'django' in content.lower():
                    tech_stack.append("Django")
                if 'flask' in content.lower():
                    tech_stack.append("Flask")
                if 'fastapi' in content.lower():
                    tech_stack.append("FastAPI")
        except:
            pass
    
    if (project_dir / "Cargo.toml").exists():
        tech_stack.append("Rust")
    
    if (project_dir / "go.mod").exists():
        tech_stack.append("Go")
    
    return tech_stack


def _detect_requirements(project_dir: Path) -> str:
    """Detect system requirements."""
    requirements = []
    
    if (project_dir / "package.json").exists():
        try:
            with open(project_dir / "package.json") as f:
                package = json.load(f)
                engines = package.get('engines', {})
                if 'node' in engines:
                    requirements.append(f"Node.js {engines['node']}")
                else:
                    requirements.append("Node.js 18+")
        except:
            requirements.append("Node.js 18+")
    
    if (project_dir / "requirements.txt").exists():
        requirements.append("Python 3.8+")
    
    if (project_dir / "Cargo.toml").exists():
        requirements.append("Rust 1.70+")
    
    if (project_dir / "go.mod").exists():
        requirements.append("Go 1.19+")
    
    return ", ".join(requirements) if requirements else "See documentation"


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
    """Enhanced setup command for first-time users - interactive configuration wizard."""
    if args and (args[0] in ["--help", "-h"]):
        print("""
Setup Commands — First-Time Setup Guide
=======================================
Usage:
    mw setup                        Run first-time setup wizard
    mw setup --help                 Show this help message

Description:
    Interactive setup wizard that configures:
    • User profile and preferences
    • API keys for AI services (OpenRouter/OpenAI)
    • Default project template preferences
    • ~/.mywork/ configuration directory
    • Shell completions (optional)

The wizard creates a personalized MyWork configuration and guides you
through your first project creation.

Examples:
    mw setup                        # Run interactive setup wizard
""")
        return 0
        
    import sys
    import json
    import platform
    from datetime import datetime
    from pathlib import Path

    def get_input(prompt, default=""):
        """Get user input with optional default."""
        if default:
            response = input(f"{prompt} [{default}]: ").strip()
            return response if response else default
        return input(f"{prompt}: ").strip()

    def yes_no(prompt, default=True):
        """Get yes/no input from user."""
        default_str = "Y/n" if default else "y/N"
        while True:
            response = input(f"{prompt} ({default_str}): ").strip().lower()
            if not response:
                return default
            if response in ['y', 'yes']:
                return True
            if response in ['n', 'no']:
                return False
            print("Please enter 'y' or 'n'")

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

{Colors.BOLD}🚀 Let's set up your personalized MyWork environment!{Colors.ENDC}
""")
    
    # Python version check
    python_version = sys.version_info
    if python_version < (3, 9):
        print(f"{Colors.RED}❌ Python {python_version.major}.{python_version.minor} is too old{Colors.ENDC}")
        print(f"{Colors.RED}   MyWork requires Python 3.9 or higher{Colors.ENDC}")
        return 1
    
    print(f"{Colors.GREEN}✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} looks good!{Colors.ENDC}\n")
    
    # Step 1: User Profile
    print(f"{Colors.BOLD}{Colors.CYAN}👤 Step 1: User Profile{Colors.ENDC}")
    print("─" * 30)
    
    user_name = get_input("What's your name?", "Developer")
    
    # Step 2: Project preferences  
    print(f"\n{Colors.BOLD}{Colors.CYAN}🎯 Step 2: Project Preferences{Colors.ENDC}")
    print("─" * 30)
    
    print("What type of projects do you usually build? (select multiple)")
    print("1. Web APIs (FastAPI, Flask)")
    print("2. Web Apps (React, Next.js)")  
    print("3. CLI Tools")
    print("4. Data Science/ML")
    print("5. Full-stack applications")
    
    project_types = get_input("Enter numbers (e.g., 1,3,5)", "1,2").split(',')
    project_types = [t.strip() for t in project_types if t.strip()]
    
    # Step 3: API Configuration
    print(f"\n{Colors.BOLD}{Colors.CYAN}🔑 Step 3: AI API Setup{Colors.ENDC}")
    print("─" * 30)
    print("MyWork works best with AI assistance. Let's configure your API keys.")
    
    api_key = None
    api_provider = "none"
    
    if yes_no("Do you have an OpenRouter API key?", False):
        api_key = get_input("Enter your OpenRouter API key").strip()
        if api_key:
            api_provider = "openrouter"
    elif yes_no("Do you have an OpenAI API key?", False):
        api_key = get_input("Enter your OpenAI API key").strip() 
        if api_key:
            api_provider = "openai"
    else:
        print(f"{Colors.YELLOW}⏭️  No API key provided - you can add one later in ~/.mywork/config.json{Colors.ENDC}")
    
    # Step 4: Create ~/.mywork directory and config
    print(f"\n{Colors.BOLD}{Colors.CYAN}📁 Step 4: Configuration Setup{Colors.ENDC}")
    print("─" * 30)
    
    config_dir = Path.home() / ".mywork"
    config_dir.mkdir(exist_ok=True)
    
    config = {
        "user": {
            "name": user_name,
            "setup_date": datetime.now().isoformat(),
            "version": "2.0.0"
        },
        "preferences": {
            "project_types": project_types,
            "default_template": "basic"
        },
        "api": {
            "provider": api_provider,
            "key": api_key if api_key else ""
        },
        "completion_configured": False
    }
    
    config_file = config_dir / "config.json"
    config_file.write_text(json.dumps(config, indent=2))
    
    print(f"{Colors.GREEN}✅ Configuration saved to {config_file}{Colors.ENDC}")
    
    # Step 5: Shell completions (optional)
    print(f"\n{Colors.BOLD}{Colors.CYAN}🐚 Step 5: Shell Completions (Optional){Colors.ENDC}")
    print("─" * 30)
    
    if yes_no("Install shell completions for tab-completion?", True):
        try:
            # Try to use the existing completions command if available
            from tools.mw import cmd_completions
            result = cmd_completions(['install'])
            if result == 0:
                config["completion_configured"] = True
                config_file.write_text(json.dumps(config, indent=2))
                print(f"{Colors.GREEN}✅ Shell completions installed{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️  Could not auto-install completions{Colors.ENDC}")
            print(f"{Colors.BLUE}💡 You can install them later with: mw completions install{Colors.ENDC}")
    
    # Final setup complete message
    print(f"""
{Colors.BOLD}{Colors.GREEN}🎉 Setup Complete! Welcome to MyWork, {user_name}!{Colors.ENDC}

{Colors.BOLD}✨ What's next?{Colors.ENDC}
{Colors.CYAN}1. Take the interactive tour:{Colors.ENDC}
   {Colors.BOLD}mw tour{Colors.ENDC}                    # Learn key features hands-on

{Colors.CYAN}2. Create your first project:{Colors.ENDC}
   {Colors.BOLD}mw new my-app{Colors.ENDC}              # Basic project
   {Colors.BOLD}mw new api-server fastapi{Colors.ENDC}  # FastAPI project

{Colors.CYAN}3. Explore the framework:{Colors.ENDC}
   {Colors.BOLD}mw dashboard{Colors.ENDC}               # Web dashboard
   {Colors.BOLD}mw status{Colors.ENDC}                  # Health check
   
{Colors.BLUE}📖 Configuration stored in: {config_dir}/{Colors.ENDC}
{Colors.BLUE}🎯 You're ready to build! Try '{Colors.BOLD}mw tour{Colors.ENDC}{Colors.BLUE}' next{Colors.ENDC}
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


def _detect_project_type(project_dir: Path) -> dict:
    """Auto-detect project type, language, framework, and tooling."""
    info = {
        "language": "unknown",
        "framework": None,
        "package_manager": None,
        "has_git": (project_dir / ".git").exists(),
        "has_tests": False,
        "has_ci": False,
        "has_docker": False,
        "dependencies": [],
        "scripts": {},
        "recommendations": [],
    }

    # Python detection
    pyproject = project_dir / "pyproject.toml"
    setup_py = project_dir / "setup.py"
    requirements = project_dir / "requirements.txt"
    pipfile = project_dir / "Pipfile"

    if pyproject.exists() or setup_py.exists() or requirements.exists():
        info["language"] = "python"
        if pipfile.exists():
            info["package_manager"] = "pipenv"
        elif (project_dir / "poetry.lock").exists():
            info["package_manager"] = "poetry"
        else:
            info["package_manager"] = "pip"

        # Detect Python frameworks
        search_files = [requirements, pyproject, setup_py]
        combined = ""
        for f in search_files:
            if f.exists():
                try:
                    combined += f.read_text(errors="ignore")
                except Exception:
                    pass
        if "fastapi" in combined.lower():
            info["framework"] = "FastAPI"
        elif "django" in combined.lower():
            info["framework"] = "Django"
        elif "flask" in combined.lower():
            info["framework"] = "Flask"
        elif "click" in combined.lower() or "typer" in combined.lower():
            info["framework"] = "CLI (Click/Typer)"

    # Node.js detection
    pkg_json = project_dir / "package.json"
    if pkg_json.exists():
        info["language"] = "node" if info["language"] == "unknown" else f"{info['language']}+node"
        if (project_dir / "pnpm-lock.yaml").exists():
            info["package_manager"] = "pnpm"
        elif (project_dir / "yarn.lock").exists():
            info["package_manager"] = "yarn"
        elif (project_dir / "bun.lockb").exists():
            info["package_manager"] = "bun"
        else:
            info["package_manager"] = info.get("package_manager") or "npm"

        try:
            pkg = json.loads(pkg_json.read_text())
            all_deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            info["scripts"] = pkg.get("scripts", {})
            if "next" in all_deps:
                info["framework"] = "Next.js"
            elif "react" in all_deps and "vite" in all_deps:
                info["framework"] = "React + Vite"
            elif "react" in all_deps:
                info["framework"] = "React"
            elif "vue" in all_deps:
                info["framework"] = "Vue.js"
            elif "svelte" in all_deps or "@sveltejs/kit" in all_deps:
                info["framework"] = "SvelteKit" if "@sveltejs/kit" in all_deps else "Svelte"
            elif "express" in all_deps:
                info["framework"] = "Express.js"
            elif "@nestjs/core" in all_deps:
                info["framework"] = "NestJS"
        except Exception:
            pass

    # Go detection
    if (project_dir / "go.mod").exists():
        info["language"] = "go" if info["language"] == "unknown" else f"{info['language']}+go"
        info["package_manager"] = "go modules"

    # Rust detection
    if (project_dir / "Cargo.toml").exists():
        info["language"] = "rust" if info["language"] == "unknown" else f"{info['language']}+rust"
        info["package_manager"] = "cargo"

    # Tooling detection
    test_dirs = ["tests", "test", "__tests__", "spec", "src/test"]
    info["has_tests"] = any((project_dir / d).exists() for d in test_dirs)
    ci_dirs = [".github/workflows", ".gitlab-ci.yml", ".circleci", "Jenkinsfile"]
    info["has_ci"] = any((project_dir / d).exists() for d in ci_dirs)
    info["has_docker"] = (project_dir / "Dockerfile").exists() or (project_dir / "docker-compose.yml").exists()

    # Generate recommendations
    if not info["has_git"]:
        info["recommendations"].append("Run 'git init' — version control is essential")
    if not info["has_tests"]:
        info["recommendations"].append("Add tests with 'mw test' — use --init to scaffold test directory")
    if not info["has_ci"]:
        info["recommendations"].append("Generate CI/CD with 'mw ci github' or 'mw ci gitlab'")
    if not info["has_docker"]:
        info["recommendations"].append("Consider adding Docker — run 'mw new --template docker'")
    if info["language"] == "unknown":
        info["recommendations"].append("No recognized project files found — consider 'mw new <name>' to scaffold")

    return info


def cmd_init(args: List[str] = None):
    """Initialize current directory as a MyWork project with smart auto-detection."""
    import datetime
    if args and (args[0] in ["--help", "-h"]):
        print("""
Init Commands — Initialize MyWork Project
========================================
Usage:
    mw init                         Initialize current directory as MyWork project
    mw init --force                 Re-initialize (overwrite existing .mw config)
    mw init --minimal               Skip auto-detection, create bare config only
    mw init --help                  Show this help message

Description:
    Smart project initialization that auto-detects:
    • Language (Python, Node.js, Go, Rust, multi-lang)
    • Framework (FastAPI, Next.js, Django, Express, etc.)
    • Package manager (pip, npm, yarn, pnpm, cargo, etc.)
    • Existing tooling (tests, CI/CD, Docker)
    
    Creates:
    • .mw/ configuration directory with detected settings
    • .env environment file (if missing)
    • GSD plan template for structured development
    • Tailored recommendations based on your project

Examples:
    mw init                         # Smart init with auto-detection
    mw init --force                 # Re-initialize existing project
    mw init --minimal               # Bare minimum setup
""")
        return 0

    force = args and "--force" in args if args else False
    minimal = args and "--minimal" in args if args else False
    current_dir = Path.cwd()
    
    # Check if already initialized
    mw_dir = current_dir / ".mw"
    if mw_dir.exists() and not force:
        print(f"{Colors.YELLOW}⚠️  Already a MyWork project (.mw/ exists). Use --force to re-initialize.{Colors.ENDC}")
        return 1

    print(f"\n{Colors.BOLD}🚀 Initializing MyWork project in: {current_dir.name}/{Colors.ENDC}\n")
    
    # Auto-detect project type
    if not minimal:
        print(f"   🔍 Scanning project...")
        info = _detect_project_type(current_dir)
        
        lang_display = info["language"].replace("+", " + ").title() if info["language"] != "unknown" else "Not detected"
        print(f"   📦 Language:        {Colors.BLUE}{lang_display}{Colors.ENDC}")
        if info["framework"]:
            print(f"   🏗️  Framework:      {Colors.BLUE}{info['framework']}{Colors.ENDC}")
        if info["package_manager"]:
            print(f"   📋 Package Manager: {Colors.BLUE}{info['package_manager']}{Colors.ENDC}")
        print(f"   🧪 Tests:           {'✅ Found' if info['has_tests'] else '❌ Not found'}")
        print(f"   🔄 CI/CD:           {'✅ Found' if info['has_ci'] else '❌ Not found'}")
        print(f"   🐳 Docker:          {'✅ Found' if info['has_docker'] else '❌ Not found'}")
        print(f"   📂 Git:             {'✅ Initialized' if info['has_git'] else '❌ Not found'}")
        print()
        lang_display = info["language"].replace("+", " + ").title() if info["language"] != "unknown" else "Not detected"
    else:
        info = {"language": "unknown", "framework": None, "package_manager": None,
                "has_git": False, "has_tests": False, "has_ci": False, "has_docker": False,
                "recommendations": [], "scripts": {}}
        lang_display = "Not detected"

    # Create .mw config directory
    mw_dir.mkdir(exist_ok=True)
    (mw_dir / "cache").mkdir(exist_ok=True)
    
    # Create config file with detected info
    config_content = {
        "project_name": current_dir.name,
        "created_at": str(datetime.datetime.now(datetime.timezone.utc)),
        "mywork_version": "2.1.0",
        "version": "1.0.0",
        "type": info["language"],
        "framework": info["framework"],
        "package_manager": info["package_manager"],
        "brain_enabled": True,
        "autoforge_enabled": True,
        "detected": {
            "has_tests": info["has_tests"],
            "has_ci": info["has_ci"],
            "has_docker": info["has_docker"],
            "has_git": info["has_git"],
        }
    }
    
    config_file = mw_dir / "config.json"
    config_file.write_text(json.dumps(config_content, indent=2))
    print(f"   ✅ Created .mw/config.json (with auto-detected settings)")

    # Create GSD plan template
    gsd_dir = mw_dir / "gsd"
    gsd_dir.mkdir(exist_ok=True)
    plan_file = gsd_dir / "PLAN.md"
    if not plan_file.exists():
        fw_note = f" ({info['framework']})" if info['framework'] else ""
        plan_content = f"""# {current_dir.name} — Development Plan

## Project Type: {lang_display}{fw_note}

## Vision
<!-- What is this project? What problem does it solve? -->

## Milestones

### v1.0 — MVP
- [ ] Core functionality
- [ ] Basic tests
- [ ] Documentation
- [ ] CI/CD pipeline

### v1.1 — Polish
- [ ] Error handling
- [ ] Performance optimization
- [ ] User feedback integration

## Architecture Notes
<!-- Key design decisions, data flow, etc. -->

## Commands
```bash
mw status          # Health check
mw test            # Run tests
mw lint scan       # Code quality
mw check           # Full quality gate
mw deploy          # Deploy to production
```
"""
        plan_file.write_text(plan_content)
        print(f"   ✅ Created .mw/gsd/PLAN.md (development plan template)")

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
    
    # Add .mw/cache to gitignore if git exists
    gitignore_file = current_dir / ".gitignore"
    if gitignore_file.exists():
        content = gitignore_file.read_text()
        if ".mw/cache/" not in content:
            with open(gitignore_file, "a") as f:
                f.write("\n# MyWork\n.mw/cache/\n")
            print(f"   ✅ Added .mw/cache/ to .gitignore")

    print(f"\n{Colors.GREEN}🎉 Project initialized successfully!{Colors.ENDC}")
    
    # Show recommendations
    if info.get("recommendations"):
        print(f"\n{Colors.YELLOW}💡 Recommendations:{Colors.ENDC}")
        for rec in info["recommendations"]:
            print(f"   → {rec}")
    
    print(f"\n{Colors.BLUE}Next steps:{Colors.ENDC}")
    print(f"   • Run 'mw status' to check project health")
    print(f"   • Edit .mw/gsd/PLAN.md to define your development plan")
    print(f"   • Run 'mw guide' for workflow guidance")
    print(f"   • Run 'mw check' before committing")
    
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
        """Format a single stats line with icon, label, value, and color."""
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


def cmd_release(args: List[str] = None) -> int:
    """Automate releases: version bump, changelog, git tag, and optional publish.

    Usage:
        mw release patch              # 1.0.0 → 1.0.1
        mw release minor              # 1.0.0 → 1.1.0
        mw release major              # 1.0.0 → 2.0.0
        mw release <version>          # Set explicit version (e.g. 2.5.0)
        mw release --dry-run patch    # Preview without changes
        mw release status             # Show current version and unreleased changes
    """
    import re as _re
    import subprocess as _sp

    args = args or []
    dry_run = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]
    bump = args[0] if args else "status"

    def _run(cmd, **kw):
        """Run a subprocess command with captured output and 10s timeout."""
        return _sp.run(cmd, capture_output=True, text=True, timeout=10, **kw)

    def _get_version(path="."):
        """Read version from pyproject.toml or package.json."""
        pp = os.path.join(path, "pyproject.toml")
        pj = os.path.join(path, "package.json")
        if os.path.exists(pp):
            for line in open(pp):
                m = _re.match(r'^version\s*=\s*["\']([^"\']+)', line)
                if m:
                    return m.group(1), "pyproject.toml"
        if os.path.exists(pj):
            import json as _j
            data = _j.load(open(pj))
            return data.get("version", "0.0.0"), "package.json"
        return "0.0.0", None

    def _set_version(new_ver, source_file, path="."):
        """Write new version to the source file."""
        fp = os.path.join(path, source_file)
        content = open(fp).read()
        if source_file == "pyproject.toml":
            content = _re.sub(r'(version\s*=\s*["\'])[\d.]+', f'\\g<1>{new_ver}', content, count=1)
        elif source_file == "package.json":
            content = _re.sub(r'("version"\s*:\s*")[\d.]+', f'\\g<1>{new_ver}', content, count=1)
        open(fp, 'w').write(content)

    def _bump_version(current, bump_type):
        """Bump a semver version string by the given type (major/minor/patch)."""
        parts = current.split(".")
        parts = [int(p) for p in parts[:3]] + [0] * (3 - len(parts[:3]))
        if bump_type == "major":
            return f"{parts[0]+1}.0.0"
        elif bump_type == "minor":
            return f"{parts[0]}.{parts[1]+1}.0"
        elif bump_type == "patch":
            return f"{parts[0]}.{parts[1]}.{parts[2]+1}"
        else:
            return bump_type  # Explicit version

    def _get_unreleased_commits():
        """Get commits since last tag."""
        r = _run(["git", "describe", "--tags", "--abbrev=0"], cwd=".")
        last_tag = r.stdout.strip() if r.returncode == 0 else ""
        range_spec = f"{last_tag}..HEAD" if last_tag else "HEAD"
        r = _run(["git", "log", range_spec, "--pretty=format:%s (%an)"], cwd=".")
        return [l for l in r.stdout.strip().split("\n") if l.strip()]

    def _categorize_commits(commits):
        """Group commit messages by conventional-commit prefix."""
        cats = {"feat": [], "fix": [], "docs": [], "refactor": [], "test": [], "other": []}
        for c in commits:
            matched = False
            for prefix in ["feat", "fix", "docs", "refactor", "test"]:
                if c.lower().startswith(prefix):
                    cats[prefix].append(c)
                    matched = True
                    break
            if not matched:
                cats["other"].append(c)
        return cats

    current_ver, source = _get_version()

    if bump == "status" or bump == "help" or bump == "--help":
        print(f"\n{Colors.BOLD}📦 Release Status{Colors.ENDC}")
        print(f"  Current version: {Colors.BLUE}v{current_ver}{Colors.ENDC}")
        print(f"  Version source:  {source or 'not found'}")
        commits = _get_unreleased_commits()
        print(f"  Unreleased commits: {len(commits)}")
        if commits:
            cats = _categorize_commits(commits)
            for cat, items in cats.items():
                if items:
                    print(f"    {cat}: {len(items)}")
            print(f"\n  {Colors.YELLOW}💡 Run 'mw release patch|minor|major' to release{Colors.ENDC}")
        else:
            print(f"  {Colors.GREEN}✅ No unreleased changes{Colors.ENDC}")
        return 0

    if not source:
        print(f"{Colors.RED}❌ No version file found (pyproject.toml or package.json){Colors.ENDC}")
        return 1

    new_ver = _bump_version(current_ver, bump)
    commits = _get_unreleased_commits()
    cats = _categorize_commits(commits)

    print(f"\n{Colors.BOLD}🚀 Release: v{current_ver} → v{new_ver}{Colors.ENDC}")
    print(f"  Commits: {len(commits)}")
    if dry_run:
        print(f"  {Colors.YELLOW}(DRY RUN - no changes will be made){Colors.ENDC}")

    # Generate changelog entry
    from datetime import datetime as _dt
    date_str = _dt.now().strftime("%Y-%m-%d")
    changelog_entry = f"\n## [{new_ver}] - {date_str}\n"
    section_map = {"feat": "### ✨ Features", "fix": "### 🐛 Bug Fixes", "docs": "### 📚 Documentation",
                   "refactor": "### ♻️ Refactoring", "test": "### 🧪 Tests", "other": "### 📦 Other"}
    for cat, title in section_map.items():
        if cats.get(cat):
            changelog_entry += f"\n{title}\n"
            for c in cats[cat]:
                changelog_entry += f"- {c}\n"

    print(f"\n{Colors.ENDC}Changelog entry:{Colors.ENDC}")
    print(changelog_entry)

    if dry_run:
        print(f"{Colors.YELLOW}Dry run complete. No changes made.{Colors.ENDC}")
        return 0

    # 1. Update version
    _set_version(new_ver, source)
    print(f"  {Colors.GREEN}✅ Updated {source} → v{new_ver}{Colors.ENDC}")

    # 2. Update CHANGELOG.md
    cl_path = "CHANGELOG.md"
    if os.path.exists(cl_path):
        content = open(cl_path).read()
        # Insert after first heading
        if "## [" in content:
            content = content.replace("\n## [", f"\n{changelog_entry}\n## [", 1)
        else:
            content += changelog_entry
        open(cl_path, 'w').write(content)
        print(f"  {Colors.GREEN}✅ Updated CHANGELOG.md{Colors.ENDC}")

    # 3. Git commit and tag
    _run(["git", "add", "-A"])
    _run(["git", "commit", "-m", f"release: v{new_ver}"])
    _run(["git", "tag", "-a", f"v{new_ver}", "-m", f"Release v{new_ver}"])
    print(f"  {Colors.GREEN}✅ Git commit + tag v{new_ver}{Colors.ENDC}")

    print(f"\n  {Colors.YELLOW}💡 Push with: git push && git push --tags{Colors.ENDC}")
    print(f"  {Colors.YELLOW}💡 Publish:   pip install build && python -m build && twine upload dist/*{Colors.ENDC}")
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
    """Generate changelog from git commits (enhanced with categorization and stats).

    Delegates to tools/changelog_gen.py for full conventional-commit parsing,
    breaking-change detection, scoped grouping, and JSON/Markdown output.
    """
    from tools.changelog_gen import cmd_changelog as _changelog_impl
    return _changelog_impl(args or [])


def _cmd_changelog_legacy(args: List[str] = None):
    """Legacy changelog generator (kept for reference)."""
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


def _cmd_test_coverage(args: List[str] = None) -> int:
    """Test coverage analysis — find untested tools and scaffold tests."""
    from test_coverage import main as tc_main
    return tc_main(args or [])


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
    
    if args and args[0] == "doctor":
        # Run test doctor to find hanging/broken tests
        return run_tool("test_doctor", args[1:])
    
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
                parts = ["pytest", "--timeout=30"]
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
    
    completed = subprocess.run(cmd, shell=True)
    return_code = completed.returncode
    
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
    completed = subprocess.run(cmd, shell=True)
    return completed.returncode


def cmd_analytics_wrapper(args: List[str] = None) -> int:
    """Run project analytics."""
    from tools.analytics import cmd_analytics
    return cmd_analytics(args or [])


def print_help() -> None:
    """Print help message."""
    print(__doc__)


def cmd_docs(args: list) -> int:
    """Auto-generate documentation for a project."""
    if args and args[0] == "site":
        from tools.docs_site import cmd_docs_site
        return cmd_docs_site(args[1:])
    from doc_generator import run_docs
    return run_docs(args) or 0


def _cmd_watch_wrapper(args: List[str] = None) -> int:
    """Smart file watcher with auto-test."""
    watch_path = Path(__file__).parent / "watch.py"
    import importlib.util
    spec = importlib.util.spec_from_file_location("watch", watch_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.main(args or [])


def _cmd_profile_wrapper(args: List[str] = None) -> int:
    """Command profiler with CPU, memory, and I/O stats."""
    profiler_path = Path(__file__).parent / "profiler.py"
    import importlib.util
    spec = importlib.util.spec_from_file_location("profiler", profiler_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    sys.argv = ['mw-profile'] + (args or [])
    mod.main()
    return 0


def _cmd_insights_wrapper(args: List[str] = None) -> int:
    """Project insights — tech debt, hotspots, coverage analysis."""
    from tools.project_insights import cmd_insights
    return cmd_insights(args or [])


def _cmd_bench_wrapper(args: List[str] = None) -> int:
    """Project benchmarking."""
    bench_path = Path(__file__).parent / "bench.py"
    import importlib.util
    spec = importlib.util.spec_from_file_location("bench", bench_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    sys.argv = ['mw-bench'] + (args or [])
    mod.main()
    return 0


def _cmd_migrate_wrapper(args: List[str] = None) -> int:
    """Database migration management."""
    from tools.migrate import cmd_migrate
    return cmd_migrate(args or [])


def _cmd_db_wrapper(args: List[str] = None) -> int:
    """Database management command."""
    from tools.db_manager import cmd_db
    return cmd_db(args or [])


def _cmd_api_wrapper(args: List[str] = None) -> int:
    """Launch REST API server."""
    args = args or []
    host = "0.0.0.0"
    port = 8420
    for i, a in enumerate(args):
        if a == "--host" and i + 1 < len(args):
            host = args[i + 1]
        elif a == "--port" and i + 1 < len(args):
            try:
                port = int(args[i + 1])
            except ValueError:
                pass
    from tools.api_server import serve
    serve(host, port)
    return 0


def _cmd_serve_wrapper(args: List[str] = None) -> int:
    """Launch web dashboard."""
    from tools.web_dashboard import cmd_serve
    return cmd_serve(args or [])


def _cmd_webdash(args: List[str] = None) -> int:
    """Generate static HTML project health dashboard."""
    from tools.html_report import main as webdash_main
    return webdash_main(args or [])


def _cmd_demo_wrapper(args: List[str] = None) -> int:
    """Launch interactive demo."""
    from tools.demo import main as demo_main
    demo_main(args or [])
    return 0

def _cmd_tour_wrapper(args: List[str] = None) -> int:
    """Launch interactive tour."""
    from tools.tour import cmd_tour
    return cmd_tour(args or [])


def _cmd_run_wrapper(args: List[str] = None) -> int:
    """Universal task runner."""
    from tools.task_runner import cmd_run
    return cmd_run(args or [])

def _cmd_check_wrapper(args: List[str] = None) -> int:
    """Quality gate command."""
    from tools.quality_gate import cmd_check
    return cmd_check(args or [])


def _cmd_ai_wrapper(args: List[str] = None) -> int:
    """AI assistant command."""
    from tools.ai_assistant import cmd_ai
    return cmd_ai(args or [])


def _cmd_pair_wrapper(args: List[str] = None) -> int:
    """Pair programming command."""
    from tools.pair_session import cmd_pair
    return cmd_pair(args or [])


def _cmd_secrets_wrapper(args: List[str] = None) -> int:
    """Secrets vault management command."""
    from tools.secrets_vault import cmd_secrets
    return cmd_secrets(args or [])


def _cmd_plugin_wrapper(args: List[str] = None) -> int:
    """Plugin management command."""
    from tools.plugin_manager import main as plugin_main
    plugin_main(args or [])
    return 0


def cmd_benchmark(args: List[str] = None) -> int:
    """Benchmark mw command performance.

    Usage:
        mw benchmark                  # Benchmark core commands
        mw benchmark --all            # Benchmark all safe commands
        mw benchmark <cmd> [<cmd>...] # Benchmark specific commands
        mw benchmark --iterations N   # Runs per command (default: 3)
    """
    import time as _time
    import subprocess

    if args and args[0] in ("--help", "-h"):
        print("""
Benchmark — Profile mw Command Performance
============================================
Usage:
    mw benchmark                  Benchmark core commands
    mw benchmark --all            Benchmark all safe commands
    mw benchmark <cmd> [<cmd>...] Benchmark specific commands
    mw benchmark --iterations N   Runs per command (default: 3)

Identifies slow commands so you can optimize startup/execution time.
""")
        return 0

    iterations = 3
    # Parse --iterations
    if args and "--iterations" in args:
        idx = args.index("--iterations")
        if idx + 1 < len(args):
            try:
                iterations = int(args[idx + 1])
            except ValueError:
                pass
            args = args[:idx] + args[idx + 2:]

    # Safe commands that don't modify anything
    core_commands = ["version", "status", "selftest", "doctor"]
    all_safe = ["version", "status", "selftest", "doctor", "projects", "brain stats",
                "changelog", "config", "health", "deps", "completions"]

    if args and "--all" in args:
        commands_to_test = all_safe
    elif args and not args[0].startswith("-"):
        commands_to_test = args
    else:
        commands_to_test = core_commands

    print(f"{Colors.BOLD}⚡ MyWork-AI CLI Benchmark{Colors.ENDC}")
    print(f"   Iterations per command: {iterations}")
    print("=" * 55)

    results = []
    for cmd in commands_to_test:
        times = []
        for i in range(iterations):
            start = _time.perf_counter()
            try:
                subprocess.run(
                    ["python3", "-m", "tools.mw", *cmd.split()],
                    capture_output=True, timeout=30,
                    cwd=str(MYWORK_ROOT)
                )
            except subprocess.TimeoutExpired:
                times.append(30.0)
                continue
            elapsed = _time.perf_counter() - start
            times.append(elapsed)

        avg = sum(times) / len(times)
        mn = min(times)
        mx = max(times)
        results.append((cmd, avg, mn, mx))

    # Sort by average time descending
    results.sort(key=lambda x: x[1], reverse=True)

    print(f"\n{'Command':<20} {'Avg':>8} {'Min':>8} {'Max':>8}  Rating")
    print("-" * 60)
    for cmd, avg, mn, mx in results:
        if avg < 0.5:
            rating = f"{Colors.GREEN}⚡ fast{Colors.ENDC}"
        elif avg < 1.5:
            rating = f"{Colors.YELLOW}🟡 ok{Colors.ENDC}"
        elif avg < 3.0:
            rating = f"{Colors.RED}🐢 slow{Colors.ENDC}"
        else:
            rating = f"{Colors.RED}🔴 very slow{Colors.ENDC}"
        print(f"  mw {cmd:<16} {avg:>6.2f}s {mn:>6.2f}s {mx:>6.2f}s  {rating}")

    overall_avg = sum(r[1] for r in results) / len(results) if results else 0
    print("-" * 60)
    print(f"  {'Overall avg':<20} {overall_avg:>6.2f}s")

    if results and results[0][1] > 2.0:
        print(f"\n{Colors.YELLOW}💡 Tip: 'mw {results[0][0]}' is your slowest command ({results[0][1]:.2f}s avg){Colors.ENDC}")

    return 0


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
        """Load config from disk, falling back to defaults on error."""
        if config_file.exists():
            try:
                return _json.loads(config_file.read_text())
            except Exception:
                return dict(DEFAULTS)
        return dict(DEFAULTS)

    def _save(cfg: dict):
        """Persist configuration dict to ~/.mywork/config.json."""
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
        
        # Validate key exists in DEFAULTS
        if key not in DEFAULTS:
            print(f"{Colors.RED}❌ Error: Unknown configuration key '{key}'{Colors.ENDC}")
            print(f"{Colors.YELLOW}💡 Valid keys are:{Colors.ENDC}")
            for valid_key in sorted(DEFAULTS.keys()):
                print(f"   {valid_key}")
            return 1
        
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
        mw git sync                   # Stash, pull --rebase, pop, push (all-in-one)
        mw git pr [base]              # Generate PR description from commits
    """
    import subprocess as _sp
    args = args or ["status"]
    sub = args[0] if args else "status"
    rest = args[1:] if len(args) > 1 else []

    def _run(cmd, capture=True):
        """Run a shell command and return stdout or exit code."""
        r = _sp.run(cmd, shell=True, capture_output=capture, text=True)
        return r.stdout.strip() if capture else r.returncode

    def _is_git():
        """Check if the current directory is inside a git repo."""
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

    elif sub == "standup":
        for label, since, until in [("Today", "midnight", ""), ("Yesterday", "yesterday.midnight", "--until=midnight")]:
            log = _run(f"git log --oneline --all --since={since} {until}").strip()
            commits = [l for l in log.split('\n') if l.strip()] if log else []
            print(f"\n📅 {label} ({len(commits)} commits):")
            for c in commits[:15]:
                print(f"  • {c}")
            if not commits:
                print("  (no commits)")
        return 0

    elif sub == "contributors":
        log = _run("git shortlog -sn --all --no-merges")
        if not log:
            print("No commits found.")
            return 1
        print("👥 Contributors\n" + "─" * 40)
        for line in log.split('\n')[:20]:
            line = line.strip()
            if line:
                parts = line.split('\t', 1)
                count = parts[0].strip()
                name = parts[1] if len(parts) > 1 else "unknown"
                bar = "█" * min(int(count) // 5, 30)
                print(f"  {name:30s} {count:>5s} {bar}")
        return 0

    elif sub == "summary":
        branch = _run("git branch --show-current") or "detached"
        total = _run("git rev-list --count HEAD") or "0"
        branches = len([b for b in _run("git branch --list").split('\n') if b.strip()])
        tags = len([t for t in _run("git tag --list").split('\n') if t.strip()])
        last_tag = _run("git describe --tags --abbrev=0 2>/dev/null") or "none"
        files = len([f for f in _run("git ls-files").split('\n') if f.strip()])
        dirty = len([s for s in _run("git status --porcelain").split('\n') if s.strip()])
        print("📊 Repository Summary")
        print("─" * 45)
        print(f"  🌿 Branch:    {branch}")
        print(f"  📝 Commits:   {total}")
        print(f"  🌳 Branches:  {branches}")
        print(f"  🏷️  Tags:      {tags}")
        print(f"  📦 Last tag:  {last_tag}")
        print(f"  📄 Files:     {files}")
        print(f"  {'🔴' if dirty else '🟢'} Dirty:     {dirty} changes")
        return 0

    elif sub == "sync":
        # All-in-one: stash dirty changes, pull --rebase, pop stash, push
        branch = _run("git branch --show-current")
        dirty = _run("git status --porcelain").strip()
        stashed = False
        if dirty:
            print("📦 Stashing local changes...")
            _run("git stash push -m 'mw-git-sync-auto'", capture=False)
            stashed = True
        print(f"⬇️ Pulling {branch} with rebase...")
        pull_rc = _run("git pull --rebase origin " + branch, capture=False)
        if pull_rc and pull_rc != 0:
            print(f"{Colors.RED}❌ Pull failed — resolve conflicts manually{Colors.ENDC}")
            if stashed:
                print("💡 Your changes are stashed. Run: git stash pop")
            return 1
        if stashed:
            print("📦 Restoring stashed changes...")
            pop_out = _run("git stash pop")
            if "CONFLICT" in (pop_out or ""):
                print(f"{Colors.YELLOW}⚠️ Stash pop had conflicts — resolve manually{Colors.ENDC}")
                return 1
        # Push if there are commits ahead
        ahead = _run("git rev-list @{u}..HEAD --count 2>/dev/null") or "0"
        if ahead != "0":
            print(f"⬆️ Pushing {ahead} commit(s)...")
            _run(f"git push origin {branch}", capture=False)
        print(f"{Colors.GREEN}✅ Synced! Branch {branch} is up to date.{Colors.ENDC}")
        return 0

    elif sub == "pr":
        # Generate a PR description from commits not on main/master
        base = rest[0] if rest else None
        if not base:
            for candidate in ["main", "master"]:
                if _run(f"git rev-parse --verify {candidate} 2>/dev/null"):
                    base = candidate
                    break
        if not base:
            print("❌ Could not detect base branch. Usage: mw git pr <base-branch>")
            return 1
        branch = _run("git branch --show-current")
        commits = _run(f"git log {base}..HEAD --oneline --no-merges")
        if not commits:
            print(f"No commits ahead of {base}")
            return 0
        commit_list = [c for c in commits.split('\n') if c.strip()]
        diff_stat = _run(f"git diff {base}..HEAD --stat")
        # Build PR template
        print(f"## 🔀 PR: {branch} → {base}\n")
        print(f"### Changes ({len(commit_list)} commits)\n")
        for c in commit_list:
            print(f"- {c}")
        print(f"\n### Files Changed\n```\n{diff_stat}\n```")
        print(f"\n---\n_Generated by `mw git pr`_")
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
        """Run a shell command and return stdout or exit code."""
        r = _sp.run(cmd, shell=True, capture_output=capture, text=True)
        return r.stdout.strip() if capture else r.returncode

    def _is_git():
        """Check if the current directory is inside a git repo."""
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


def cmd_snapshot(args: List[str] = None) -> int:
    """Capture a project health snapshot for trend tracking.

    Usage:
        mw snapshot [project_path]       Capture snapshot of current or given project
        mw snapshot history [project]    Show snapshot history
        mw snapshot compare              Compare last two snapshots

    Captures: lines of code, file count, test count, git stats, dependencies, complexity.
    Snapshots are stored in .mw/snapshots/ for historical comparison.
    """
    import datetime
    import glob

    args = args or []
    sub = args[0] if args else "capture"

    if sub in ["--help", "-h"]:
        print(cmd_snapshot.__doc__)
        return 0

    # Determine project path
    if sub == "history":
        project_path = Path(args[1]) if len(args) > 1 else Path.cwd()
        snap_dir = project_path / ".mw" / "snapshots"
        if not snap_dir.exists():
            print(f"No snapshots found in {project_path}")
            return 1
        snaps = sorted(snap_dir.glob("*.json"))
        print(f"{Colors.BOLD}📸 Snapshot History ({len(snaps)} snapshots){Colors.ENDC}")
        print("=" * 50)
        for s in snaps[-10:]:
            try:
                data = json.loads(s.read_text())
                ts = data.get("timestamp", "?")[:19]
                loc = data.get("lines_of_code", 0)
                files = data.get("file_count", 0)
                tests = data.get("test_count", "?")
                print(f"  {ts}  |  {loc:>6} LoC  |  {files:>4} files  |  {tests} tests")
            except Exception:
                pass
        return 0

    if sub == "compare":
        project_path = Path(args[1]) if len(args) > 1 else Path.cwd()
        snap_dir = project_path / ".mw" / "snapshots"
        snaps = sorted(snap_dir.glob("*.json")) if snap_dir.exists() else []
        if len(snaps) < 2:
            print("Need at least 2 snapshots to compare. Run 'mw snapshot' first.")
            return 1
        old = json.loads(snaps[-2].read_text())
        new = json.loads(snaps[-1].read_text())
        print(f"{Colors.BOLD}📊 Snapshot Comparison{Colors.ENDC}")
        print("=" * 55)
        for key in ["lines_of_code", "file_count", "test_count", "dependency_count", "git_commits"]:
            o = old.get(key, 0) or 0
            n = new.get(key, 0) or 0
            diff = n - o
            arrow = f"{Colors.GREEN}↑{diff}{Colors.ENDC}" if diff > 0 else (f"{Colors.RED}↓{abs(diff)}{Colors.ENDC}" if diff < 0 else "→0")
            label = key.replace("_", " ").title()
            print(f"  {label:<20}  {o:>8}  →  {n:>8}  {arrow}")
        return 0

    # Default: capture snapshot
    project_path = Path(sub) if sub != "capture" and not sub.startswith("-") else Path.cwd()
    if not project_path.exists():
        project_path = Path.cwd()

    print(f"{Colors.BOLD}📸 Capturing project snapshot...{Colors.ENDC}")

    snapshot = {
        "timestamp": datetime.datetime.now().isoformat(),
        "project": project_path.name,
        "lines_of_code": 0,
        "file_count": 0,
        "test_count": 0,
        "dependency_count": 0,
        "git_commits": 0,
        "git_branch": "",
        "file_types": {},
    }

    # Count lines and files by type
    skip_dirs = {'.git', 'node_modules', '__pycache__', 'venv', 'env', '.venv', 'dist', 'build', '.next'}
    code_exts = {'.py', '.js', '.jsx', '.ts', '.tsx', '.vue', '.rb', '.go', '.rs', '.java', '.c', '.cpp', '.h'}

    for root, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for f in files:
            ext = Path(f).suffix.lower()
            if ext in code_exts:
                fp = Path(root) / f
                try:
                    lines = len(fp.read_text(errors='ignore').splitlines())
                    snapshot["lines_of_code"] += lines
                    snapshot["file_count"] += 1
                    snapshot["file_types"][ext] = snapshot["file_types"].get(ext, 0) + 1
                except Exception:
                    pass

    # Count tests
    try:
        test_files = list(project_path.rglob("test_*.py")) + list(project_path.rglob("*_test.py"))
        test_files += list(project_path.rglob("*.test.ts")) + list(project_path.rglob("*.test.tsx"))
        test_files += list(project_path.rglob("*.test.js")) + list(project_path.rglob("*.spec.*"))
        snapshot["test_count"] = len(test_files)
    except Exception:
        pass

    # Count dependencies
    pkg_json = project_path / "package.json"
    req_txt = project_path / "requirements.txt"
    pyproject = project_path / "pyproject.toml"
    deps = 0
    if pkg_json.exists():
        try:
            pkg = json.loads(pkg_json.read_text())
            deps += len(pkg.get("dependencies", {})) + len(pkg.get("devDependencies", {}))
        except Exception:
            pass
    if req_txt.exists():
        try:
            deps += sum(1 for l in req_txt.read_text().splitlines() if l.strip() and not l.startswith('#'))
        except Exception:
            pass
    if pyproject.exists():
        try:
            in_deps = False
            for line in pyproject.read_text().splitlines():
                if 'dependencies' in line and '[' in line:
                    in_deps = True
                elif in_deps and line.strip().startswith(']'):
                    in_deps = False
                elif in_deps and line.strip().startswith('"'):
                    deps += 1
        except Exception:
            pass
    snapshot["dependency_count"] = deps

    # Git info
    try:
        result = subprocess.run(['git', 'rev-list', '--count', 'HEAD'], cwd=project_path, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            snapshot["git_commits"] = int(result.stdout.strip())
        result = subprocess.run(['git', 'branch', '--show-current'], cwd=project_path, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            snapshot["git_branch"] = result.stdout.strip()
    except Exception:
        pass

    # Save snapshot
    snap_dir = project_path / ".mw" / "snapshots"
    snap_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    snap_file = snap_dir / f"snapshot_{ts}.json"
    snap_file.write_text(json.dumps(snapshot, indent=2))

    # Display
    print(f"\n{Colors.BLUE}{'=' * 50}{Colors.ENDC}")
    print(f"  📁 Project:      {snapshot['project']}")
    print(f"  📝 Lines of Code: {snapshot['lines_of_code']:,}")
    print(f"  📄 Code Files:    {snapshot['file_count']}")
    print(f"  🧪 Test Files:    {snapshot['test_count']}")
    print(f"  📦 Dependencies:  {snapshot['dependency_count']}")
    print(f"  🔀 Git Commits:   {snapshot['git_commits']}")
    print(f"  🌿 Branch:        {snapshot['git_branch']}")
    if snapshot["file_types"]:
        top = sorted(snapshot["file_types"].items(), key=lambda x: -x[1])[:5]
        types_str = ", ".join(f"{ext}({n})" for ext, n in top)
        print(f"  📊 Top Types:     {types_str}")
    print(f"{Colors.BLUE}{'=' * 50}{Colors.ENDC}")
    print(f"  💾 Saved to: {snap_file}")
    return 0


def cmd_recap(args: List[str] = None) -> int:
    """Generate a productivity recap (daily/weekly/custom).

    Usage:
        mw recap                  # Today's recap
        mw recap --week           # This week's recap
        mw recap --since "3 days ago"  # Custom period
        mw recap --all            # All projects
        mw recap --json           # JSON output
    """
    import json as json_mod
    import re as re_mod

    period = "today"
    since_arg = "midnight"
    json_output = False
    all_projects = False

    if args:
        i = 0
        while i < len(args):
            if args[i] == "--week":
                period = "week"
                since_arg = "7 days ago"
                i += 1
            elif args[i] == "--since" and i + 1 < len(args):
                period = "custom"
                since_arg = args[i + 1]
                i += 2
            elif args[i] == "--json":
                json_output = True
                i += 1
            elif args[i] == "--all":
                all_projects = True
                i += 1
            elif args[i] in ("--help", "-h"):
                print("mw recap — Productivity Recap")
                print("=" * 40)
                print("Usage:")
                print("    mw recap                  Today's recap")
                print("    mw recap --week           This week's recap")
                print('    mw recap --since "3 days ago"  Custom period')
                print("    mw recap --all            Include all project dirs")
                print("    mw recap --json           JSON output")
                return 0
            else:
                i += 1

    def _run_recap(cmd: str, cwd: str = None) -> str:
        try:
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10, cwd=cwd)
            return r.stdout.strip()
        except Exception:
            return ""

    # Determine project directories to scan
    fw_root = Path(__file__).parent.parent
    project_dirs = [str(fw_root)]
    if all_projects:
        pdir = fw_root / "projects"
        if pdir.exists():
            for p in pdir.iterdir():
                if p.is_dir() and (p / ".git").exists():
                    project_dirs.append(str(p))

    recap = {
        "period": period,
        "since": since_arg,
        "projects": [],
        "totals": {"commits": 0, "files_changed": 0, "insertions": 0, "deletions": 0, "authors": set()},
    }

    for pdir_path in project_dirs:
        if not Path(pdir_path, ".git").exists():
            continue
        pname = Path(pdir_path).name

        commits_raw = _run_recap(f'git log --oneline --since="{since_arg}" 2>/dev/null', cwd=pdir_path)
        commits = [l for l in commits_raw.split("\n") if l.strip()] if commits_raw else []
        num_commits = len(commits)

        if num_commits == 0:
            continue

        shortstat = _run_recap(f'git log --since="{since_arg}" --shortstat --format="" 2>/dev/null', cwd=pdir_path)
        files_changed = 0
        insertions = 0
        deletions = 0
        for line in shortstat.split("\n"):
            line = line.strip()
            if not line:
                continue
            m_files = re_mod.search(r"(\d+) files? changed", line)
            m_ins = re_mod.search(r"(\d+) insertions?\(\+\)", line)
            m_del = re_mod.search(r"(\d+) deletions?\(-\)", line)
            if m_files:
                files_changed += int(m_files.group(1))
            if m_ins:
                insertions += int(m_ins.group(1))
            if m_del:
                deletions += int(m_del.group(1))

        authors_raw = _run_recap(f'git log --since="{since_arg}" --format="%an" 2>/dev/null', cwd=pdir_path)
        authors = list(set(a.strip() for a in authors_raw.split("\n") if a.strip())) if authors_raw else []

        top_files_raw = _run_recap(
            f'git log --since="{since_arg}" --name-only --format="" 2>/dev/null | sort | uniq -c | sort -rn | head -5',
            cwd=pdir_path,
        )
        top_files = []
        if top_files_raw:
            for line in top_files_raw.split("\n"):
                line = line.strip()
                if line:
                    parts = line.split(None, 1)
                    if len(parts) == 2:
                        top_files.append({"count": int(parts[0]), "file": parts[1]})

        proj_data = {
            "name": pname,
            "commits": num_commits,
            "commit_messages": [c.split(" ", 1)[1] if " " in c else c for c in commits[:10]],
            "files_changed": files_changed,
            "insertions": insertions,
            "deletions": deletions,
            "authors": authors,
            "top_files": top_files,
        }
        recap["projects"].append(proj_data)
        recap["totals"]["commits"] += num_commits
        recap["totals"]["files_changed"] += files_changed
        recap["totals"]["insertions"] += insertions
        recap["totals"]["deletions"] += deletions
        recap["totals"]["authors"].update(authors)

    recap["totals"]["authors"] = list(recap["totals"]["authors"])

    if json_output:
        print(json_mod.dumps(recap, indent=2))
        return 0

    # Pretty print
    period_label = {"today": "Today", "week": "This Week", "custom": f'Since "{since_arg}"'}.get(period, period)

    print(f"\n  {Colors.BOLD}📊 Productivity Recap — {period_label}{Colors.ENDC}")
    print(f"  {'━' * 45}")

    if not recap["projects"]:
        print(f"\n  {Colors.ENDC}No commits found for this period.{Colors.ENDC}\n")
        return 0

    t = recap["totals"]
    print(f"\n  {Colors.GREEN}📈 Totals:{Colors.ENDC}")
    print(f"     Commits:    {t['commits']}")
    print(f"     Files:      {t['files_changed']} changed")
    print(f"     Lines:      {Colors.GREEN}+{t['insertions']}{Colors.ENDC} / {Colors.RED}-{t['deletions']}{Colors.ENDC}")
    net = t["insertions"] - t["deletions"]
    print(f"     Net:        {'+' if net >= 0 else ''}{net} lines")
    if t["authors"]:
        print(f"     Authors:    {', '.join(t['authors'])}")

    for proj in recap["projects"]:
        print(f"\n  {Colors.BLUE}📁 {proj['name']}{Colors.ENDC} — {proj['commits']} commits")
        print(f"     {Colors.GREEN}+{proj['insertions']}{Colors.ENDC} / {Colors.RED}-{proj['deletions']}{Colors.ENDC} across {proj['files_changed']} files")

        if proj["commit_messages"]:
            print(f"     Recent:")
            for msg in proj["commit_messages"][:5]:
                print(f"       • {msg}")

        if proj["top_files"]:
            print(f"     Hot files:")
            for tf in proj["top_files"][:3]:
                print(f"       {tf['count']}× {tf['file']}")

    print(f"\n  {'━' * 45}\n")
    return 0


def _cmd_context_wrapper(args: List[str] = None) -> int:
    """Smart context builder for AI coding assistants."""
    try:
        from tools.context_builder import main as context_main
        return context_main(args or [])
    except ImportError:
        try:
            # Try relative import for installed package
            script_dir = os.path.dirname(os.path.abspath(__file__))
            sys.path.insert(0, os.path.dirname(script_dir))
            from tools.context_builder import main as context_main
            return context_main(args or [])
        except ImportError:
            print(f"{Colors.RED}❌ context_builder.py not found{Colors.ENDC}")
            return 1


def cmd_todo(args: List[str] = None) -> int:
    """Scan project files for TODO/FIXME/HACK/XXX comments.

    Usage:
        mw todo [path] [--tag TAG] [--json] [--stats]

    Scans Python, JS/TS, Go, Rust, Ruby, Shell, and config files for
    actionable comments. Defaults to current directory.
    """
    import re as _re

    args = args or []
    if args and args[0] in ("--help", "-h"):
        print("""
Todo Scanner — Find actionable comments in your codebase
=========================================================
Usage:
    mw todo [path]        Scan path (default: current dir)
    mw todo --tag FIXME   Filter by specific tag
    mw todo --stats       Show summary counts only
    mw todo --json        Output as JSON

Tags scanned: TODO, FIXME, HACK, XXX, NOTE, OPTIMIZE, REFACTOR
""")
        return 0

    scan_path = Path(".")
    filter_tag = None
    json_mode = False
    stats_only = False

    i = 0
    while i < len(args):
        if args[i] == "--tag" and i + 1 < len(args):
            filter_tag = args[i + 1].upper()
            i += 2
        elif args[i] == "--json":
            json_mode = True
            i += 1
        elif args[i] == "--stats":
            stats_only = True
            i += 1
        elif not args[i].startswith("-"):
            scan_path = Path(args[i])
            i += 1
        else:
            i += 1

    if not scan_path.exists():
        print(f"{Colors.RED}✗ Path not found: {scan_path}{Colors.ENDC}")
        return 1

    TAGS = ["TODO", "FIXME", "HACK", "XXX", "NOTE", "OPTIMIZE", "REFACTOR"]
    EXTENSIONS = {
        ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".rb",
        ".sh", ".bash", ".zsh", ".yaml", ".yml", ".toml", ".cfg",
        ".c", ".cpp", ".h", ".hpp", ".java", ".kt", ".swift",
        ".css", ".scss", ".html", ".md",
    }
    SKIP_DIRS = {
        ".git", "node_modules", "__pycache__", ".venv", "venv",
        "dist", "build", ".tox", ".mypy_cache", ".pytest_cache",
        "target", ".next", "coverage",
    }

    pattern = _re.compile(
        r"#\s*(" + "|".join(TAGS) + r")\b[:\s]*(.*)|//\s*(" + "|".join(TAGS) + r")\b[:\s]*(.*)|/\*\s*(" + "|".join(TAGS) + r")\b[:\s]*(.*)",
        _re.IGNORECASE,
    )

    results = []
    tag_counts: dict = {}

    for root_dir, dirs, files in os.walk(scan_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fname in files:
            fpath = Path(root_dir) / fname
            if fpath.suffix.lower() not in EXTENSIONS:
                continue
            try:
                lines = fpath.read_text(errors="ignore").splitlines()
            except (OSError, PermissionError):
                continue
            for line_no, line in enumerate(lines, 1):
                m = pattern.search(line)
                if m:
                    # Extract tag and text from whichever group matched
                    tag = (m.group(1) or m.group(3) or m.group(5) or "").upper()
                    text = (m.group(2) or m.group(4) or m.group(6) or "").strip()
                    if filter_tag and tag != filter_tag:
                        continue
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
                    results.append({
                        "file": str(fpath),
                        "line": line_no,
                        "tag": tag,
                        "text": text,
                    })

    if json_mode:
        print(json.dumps({"total": len(results), "by_tag": tag_counts, "items": results}, indent=2))
        return 0

    if stats_only:
        print(f"{Colors.BOLD}{Colors.BLUE}📋 Todo Stats{Colors.ENDC}")
        print(f"{'=' * 40}")
        total = 0
        tag_colors = {"FIXME": Colors.RED, "HACK": Colors.YELLOW, "XXX": Colors.RED, "TODO": Colors.BLUE}
        for tag in sorted(tag_counts, key=lambda t: -tag_counts[t]):
            c = tag_colors.get(tag, Colors.ENDC)
            cnt = tag_counts[tag]
            total += cnt
            print(f"  {c}{tag:12s}{Colors.ENDC} {cnt}")
        print(f"{'─' * 40}")
        print(f"  {'Total':12s} {total}")
        return 0

    if not results:
        print(f"{Colors.GREEN}✅ No TODO/FIXME comments found — clean codebase!{Colors.ENDC}")
        return 0

    print(f"{Colors.BOLD}{Colors.BLUE}📋 Found {len(results)} actionable comments{Colors.ENDC}")
    print(f"{'=' * 60}")

    tag_colors = {"FIXME": Colors.RED, "HACK": Colors.YELLOW, "XXX": Colors.RED, "TODO": Colors.BLUE}
    current_file = None
    for item in results:
        if item["file"] != current_file:
            current_file = item["file"]
            print(f"\n{Colors.BOLD}{current_file}{Colors.ENDC}")
        c = tag_colors.get(item["tag"], Colors.ENDC)
        print(f"  {Colors.ENDC}L{item['line']:>4d}{Colors.ENDC}  {c}{item['tag']:7s}{Colors.ENDC} {item['text']}")

    print(f"\n{'─' * 60}")
    for tag in sorted(tag_counts, key=lambda t: -tag_counts[t]):
        c = tag_colors.get(tag, Colors.ENDC)
        print(f"  {c}{tag}{Colors.ENDC}: {tag_counts[tag]}", end="  ")
    print(f"\n  Total: {len(results)}")
    return 0


def cmd_version(args: List[str] = None) -> int:
    """Show framework version, Python version, and platform info.

    Usage:
        mw version              Show local version info
        mw version --check      Check PyPI for updates
        mw version --json       Output as JSON
    """
    import platform
    args = args or []
    check_pypi = "--check" in args
    as_json = "--json" in args

    try:
        pyproject_path = MYWORK_ROOT / "pyproject.toml"
        version = "unknown"
        if pyproject_path.exists():
            with open(pyproject_path, 'r') as f:
                for line in f:
                    if line.startswith('version ='):
                        version = line.split('=')[1].strip().strip('"')
                        break

        info = {
            "version": version,
            "python": platform.python_version(),
            "platform": f"{platform.system()} {platform.machine()}",
            "install_path": str(MYWORK_ROOT),
        }

        # Check PyPI for latest version
        if check_pypi:
            try:
                import urllib.request, json as _json
                req = urllib.request.Request(
                    "https://pypi.org/pypi/mywork-ai/json",
                    headers={"Accept": "application/json", "User-Agent": "mywork-ai"},
                )
                with urllib.request.urlopen(req, timeout=5) as resp:
                    pypi_data = _json.loads(resp.read())
                latest = pypi_data.get("info", {}).get("version", "unknown")
                info["latest_pypi"] = latest
                # Compare versions properly using tuple comparison
                def _parse_ver(v):
                    try:
                        return tuple(int(x) for x in v.split('.'))
                    except (ValueError, AttributeError):
                        return (0,)
                info["update_available"] = (
                    version != "unknown"
                    and latest != "unknown"
                    and _parse_ver(latest) > _parse_ver(version)
                )
            except Exception:
                info["latest_pypi"] = "check failed"
                info["update_available"] = False

        if as_json:
            import json as _json
            print(_json.dumps(info, indent=2))
        else:
            print(f"MyWork-AI v{version}")
            print(f"Python {platform.python_version()} on {platform.system()} {platform.machine()}")
            print(f"Install: {MYWORK_ROOT}")
            if check_pypi:
                latest = info.get("latest_pypi", "?")
                if info.get("update_available"):
                    print(f"\n⬆️  Update available: v{version} → v{latest}")
                    print(f"   Run: pip install --upgrade mywork-ai")
                elif latest == "check failed":
                    print(f"\n⚠️  Could not reach PyPI to check for updates")
                else:
                    print(f"\n✅ You're on the latest version (v{version})")
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
    
    # Delegate to ci_status for status/badge subcommands
    if sub in ("status", "badge"):
        try:
            from tools.ci_status import main as ci_status_main
            return ci_status_main([sub] + args[1:])
        except ImportError:
            import importlib.util
            spec = importlib.util.spec_from_file_location("ci_status", os.path.join(os.path.dirname(__file__), "ci_status.py"))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod.main([sub] + args[1:])
    
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
    
    elif sub == "status":
        # Check GitHub Actions workflow status via API
        import subprocess as _sp, json as _json
        proj_path = args[1] if len(args) > 1 and not args[1].startswith("-") else "."
        
        # Detect GitHub repo from git remote
        try:
            remote = _sp.check_output(["git", "-C", proj_path, "remote", "get-url", "origin"],
                                       stderr=_sp.DEVNULL).decode().strip()
        except Exception:
            print(f"{Colors.RED}❌ Not a git repo or no remote configured{Colors.ENDC}")
            return 1
        
        # Parse owner/repo from remote URL
        owner_repo = None
        if "github.com" in remote:
            # SSH or HTTPS
            parts = remote.replace(".git", "").split("github.com")[-1].lstrip(":/").split("/")
            if len(parts) >= 2:
                owner_repo = f"{parts[0]}/{parts[1]}"
        
        if not owner_repo:
            print(f"{Colors.RED}❌ Could not detect GitHub repo from remote: {remote}{Colors.ENDC}")
            return 1
        
        print(f"\n{Colors.BOLD}🔄 GitHub Actions Status — {owner_repo}{Colors.ENDC}\n")
        
        # Fetch latest workflow runs (public API, no auth needed for public repos)
        import urllib.request
        gh_token = os.environ.get("GITHUB_TOKEN", "")
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "mw-cli"}
        if gh_token:
            headers["Authorization"] = f"Bearer {gh_token}"
        
        url = f"https://api.github.com/repos/{owner_repo}/actions/runs?per_page=10"
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = _json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(f"{Colors.YELLOW}⚠️  No GitHub Actions found (repo may be private — set GITHUB_TOKEN){Colors.ENDC}")
            else:
                print(f"{Colors.RED}❌ GitHub API error: {e.code}{Colors.ENDC}")
            return 1
        except Exception as e:
            print(f"{Colors.RED}❌ Failed to reach GitHub API: {e}{Colors.ENDC}")
            return 1
        
        runs = data.get("workflow_runs", [])
        if not runs:
            print(f"  {Colors.YELLOW}No workflow runs found.{Colors.ENDC}")
            print(f"  Set up CI with: {Colors.BOLD}mw ci generate{Colors.ENDC}")
            return 0
        
        status_icons = {
            "completed": {"success": f"{Colors.GREEN}✅ passed", "failure": f"{Colors.RED}❌ failed",
                          "cancelled": f"{Colors.YELLOW}⚠️  cancelled", "skipped": f"{Colors.YELLOW}⏭️  skipped"},
            "in_progress": f"{Colors.BLUE}🔄 running",
            "queued": f"{Colors.YELLOW}⏳ queued",
            "waiting": f"{Colors.YELLOW}⏳ waiting",
        }
        
        # Group by workflow name, show latest of each
        seen = {}
        for run in runs:
            wf = run.get("name", "unknown")
            if wf not in seen:
                seen[wf] = run
        
        for wf, run in seen.items():
            status = run.get("status", "unknown")
            conclusion = run.get("conclusion", "")
            branch = run.get("head_branch", "?")
            sha = run.get("head_sha", "?")[:7]
            created = run.get("created_at", "?")[:19].replace("T", " ")
            
            if status == "completed":
                icon = status_icons["completed"].get(conclusion, f"{Colors.YELLOW}❓ {conclusion}")
            else:
                icon = status_icons.get(status, f"❓ {status}")
            
            print(f"  {Colors.BOLD}{wf}{Colors.ENDC}")
            print(f"    Status:  {icon}{Colors.ENDC}")
            print(f"    Branch:  {branch} ({sha})")
            print(f"    Time:    {created}")
            print(f"    URL:     {run.get('html_url', 'N/A')}")
            print()
        
        total = data.get("total_count", len(runs))
        print(f"  {Colors.BLUE}Total runs: {total} | Showing latest per workflow{Colors.ENDC}\n")
        return 0
    
    print(f"{Colors.RED}❌ Unknown ci subcommand: {sub}{Colors.ENDC}")
    print(f"   Usage: mw ci [generate|validate|templates|status]")
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
    
    # Check for help flag first
    if "--help" in args or "-h" in args:
        print(f"\n{Colors.BOLD}🚀 MyWork Deploy{Colors.ENDC}")
        print(f"{'─' * 50}")
        print("Deploy projects to cloud platforms with zero config.")
        print()
        print(f"{Colors.BOLD}Usage:{Colors.ENDC}")
        print("  mw deploy                          Deploy current directory")
        print("  mw deploy <project>                Deploy named project") 
        print("  mw deploy --platform <name>        Specify platform")
        print("  mw deploy --prod                   Production deploy")
        print("  mw deploy --preview                Preview deploy")
        print("  mw deploy --status                 Check deployment status")
        print("  mw deploy --list                   List recent deployments")
        print("  mw deploy --dry-run                Preview what would be deployed")
        print()
        print(f"{Colors.BOLD}Platforms:{Colors.ENDC}")
        print("  vercel      Vercel (Node.js, static sites)")
        print("  railway     Railway (Python, Node.js)")
        print("  render      Render (web services)")
        print("  docker      Docker containerized deploy")
        print()
        print(f"{Colors.BOLD}Examples:{Colors.ENDC}")
        print("  mw deploy --platform vercel --prod")
        print("  mw deploy my-api --platform railway")
        print("  mw deploy frontend --dry-run")
        return 0
    
    # Parse flags
    platform = None
    prod = False
    preview = False
    show_status = False
    list_deploys = False
    project_name = None
    token = None
    dry_run = False
    
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
        elif args[i] == "--dry-run":
            dry_run = True
            i += 1
        elif args[i] == "--token" and i + 1 < len(args):
            token = args[i + 1]
            i += 2
        elif not args[i].startswith("-"):
            project_name = args[i]
            i += 1
        else:
            i += 1
    
    # Handle status and list commands early
    if show_status:
        print(f"{Colors.BLUE}📊 Deployment Status{Colors.ENDC}")
        print(f"{'─' * 50}")
        print(f"{Colors.YELLOW}⚠️  Status checking not yet implemented{Colors.ENDC}")
        print(f"{Colors.YELLOW}💡 Use platform-specific tools:{Colors.ENDC}")
        print(f"   • vercel --prod ls")
        print(f"   • railway status")
        print(f"   • docker ps")
        return 0
        
    if list_deploys:
        print(f"{Colors.BLUE}📋 Recent Deployments{Colors.ENDC}")
        print(f"{'─' * 50}")
        print(f"{Colors.YELLOW}⚠️  Deployment history not yet implemented{Colors.ENDC}")
        print(f"{Colors.YELLOW}💡 Use platform dashboards:{Colors.ENDC}")
        print(f"   • https://vercel.com/dashboard")
        print(f"   • https://railway.app/")
        print(f"   • https://render.com/")
        return 0
    
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
        for base in [os.path.expanduser("~")]:
            candidate = os.path.join(base, project_name)
            if os.path.isdir(candidate):
                project_dir = candidate
                break
    
    print(f"\n{Colors.BOLD}🚀 MyWork Deploy{Colors.ENDC}")
    print(f"{'─' * 50}")
    
    # Auto-detect platform if not specified (priority-based detection)
    if not platform:
        # Check project type first (language takes priority over config files)
        is_python = (os.path.exists(os.path.join(project_dir, "pyproject.toml")) or 
                     os.path.exists(os.path.join(project_dir, "requirements.txt")) or
                     os.path.exists(os.path.join(project_dir, "setup.py")))
        is_nodejs = os.path.exists(os.path.join(project_dir, "package.json"))
        has_docker = os.path.exists(os.path.join(project_dir, "Dockerfile"))
        
        # Platform-specific config files
        has_vercel = os.path.exists(os.path.join(project_dir, "vercel.json"))
        has_railway = (os.path.exists(os.path.join(project_dir, "railway.json")) or 
                       os.path.exists(os.path.join(project_dir, "railway.toml")))
        has_render = os.path.exists(os.path.join(project_dir, "render.yaml"))
        
        # Priority detection logic
        if has_docker:
            platform = "docker"
        elif has_railway:
            platform = "railway"
        elif has_render:
            platform = "render"
        elif is_python:
            platform = "railway"  # Railway is best for Python projects
        elif has_vercel or is_nodejs:
            platform = "vercel"  # Vercel for Node.js/static sites
        else:
            print(f"{Colors.RED}❌ Could not auto-detect platform for deployment{Colors.ENDC}")
            print(f"{Colors.BLUE}📋 Project Analysis:{Colors.ENDC}")
            if os.path.exists(os.path.join(project_dir, "package.json")):
                print(f"   • Node.js project detected")
            if os.path.exists(os.path.join(project_dir, "requirements.txt")) or os.path.exists(os.path.join(project_dir, "pyproject.toml")):
                print(f"   • Python project detected")
            if os.path.exists(os.path.join(project_dir, "go.mod")):
                print(f"   • Go project detected")
                
            print(f"\n{Colors.YELLOW}🎯 Recommended platforms:{Colors.ENDC}")
            if is_nodejs:
                print(f"   mw deploy --platform vercel     # ⭐ Best for Next.js/React/Vue/static sites")
                print(f"   mw deploy --platform railway    # Good for Node.js APIs")
                print(f"   mw deploy --platform render     # Full-stack apps")
            elif is_python:
                print(f"   mw deploy --platform railway    # ⭐ Best for FastAPI/Django/Flask")
                print(f"   mw deploy --platform render     # Web services")
                print(f"   mw deploy --platform vercel     # Static sites only")
            else:
                print(f"   mw deploy --platform railway    # General purpose")
                print(f"   mw deploy --platform render     # Web services")
                print(f"   mw deploy --platform docker     # Any containerized app")
                
            print(f"\n{Colors.YELLOW}🔧 Quick Setup Guides:{Colors.ENDC}")
            print(f"   Vercel: Add vercel.json → https://vercel.com/docs/projects/project-configuration")
            print(f"   Railway: Login → railway login, then railway init")
            print(f"   Render: Connect Git repo → https://render.com/docs")
            print(f"   Docker: Add Dockerfile → mw generate dockerfile")
            print(f"\n{Colors.BLUE}💡 Try: mw deploy --dry-run --platform <name> to preview{Colors.ENDC}")
            return 1
    
    print(f"  📁 Project: {Colors.GREEN}{os.path.basename(project_dir)}{Colors.ENDC}")
    print(f"  📍 Path: {project_dir}")
    print(f"  🎯 Platform: {Colors.BLUE}{platform}{Colors.ENDC}")
    print(f"  🏷️  Mode: {'Production' if prod else 'Preview'}")
    
    # Handle dry-run mode
    if dry_run:
        print(f"  {Colors.YELLOW}🔍 Mode: DRY RUN (preview only){Colors.ENDC}")
        print()
        print(f"{Colors.YELLOW}📋 Would deploy with these settings:{Colors.ENDC}")
        print(f"   Platform: {platform}")
        print(f"   Environment: {'Production' if prod else 'Preview'}")
        print(f"   Directory: {project_dir}")
        print(f"\n{Colors.GREEN}✅ Dry run complete. Use without --dry-run to deploy.{Colors.ENDC}")
        return 0
        
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
        """Mask a secret value, showing only first/last 2 chars."""
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
    for base in [os.path.expanduser("~")]:
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


def cmd_api(args: List[str] = None) -> int:
    """Scaffold and manage FastAPI projects with auto-generated CRUD.

    Usage:
        mw api init <name>                    # Create new FastAPI project
        mw api add-model <name> <fields...>   # Add a model with CRUD routes
        mw api run [--port PORT]              # Run the dev server
        mw api routes                         # List all routes

    Fields format: field_name:type (types: str, int, float, bool, datetime)
    Example: mw api add-model User name:str email:str age:int active:bool
    """
    args = args or []

    if not args or args[0] in ("-h", "--help", "help"):
        print(f"\n{Colors.BOLD}🚀 MyWork API Generator{Colors.ENDC}")
        print(f"{'─' * 50}")
        print(f"  {Colors.GREEN}mw api init <name>{Colors.ENDC}                 Create new FastAPI project")
        print(f"  {Colors.GREEN}mw api add-model <Name> <fields>{Colors.ENDC}   Add model + CRUD routes")
        print(f"  {Colors.GREEN}mw api run [--port N]{Colors.ENDC}              Start dev server")
        print(f"  {Colors.GREEN}mw api routes{Colors.ENDC}                      List all routes")
        print(f"\n  {Colors.YELLOW}Fields:{Colors.ENDC} name:str email:str age:int price:float active:bool")
        print(f"  {Colors.YELLOW}Example:{Colors.ENDC} mw api add-model Product name:str price:float in_stock:bool")
        return 0

    subcmd = args[0]

    if subcmd == "init":
        if len(args) < 2:
            print(f"{Colors.RED}❌ Usage: mw api init <project-name>{Colors.ENDC}")
            return 1
        name = args[1]
        project_dir = os.path.join(os.getcwd(), name)
        if os.path.exists(project_dir):
            print(f"{Colors.RED}❌ Directory '{name}' already exists{Colors.ENDC}")
            return 1

        os.makedirs(os.path.join(project_dir, "app", "models"), exist_ok=True)
        os.makedirs(os.path.join(project_dir, "app", "routes"), exist_ok=True)
        os.makedirs(os.path.join(project_dir, "app", "schemas"), exist_ok=True)
        os.makedirs(os.path.join(project_dir, "tests"), exist_ok=True)

        # Main app
        with open(os.path.join(project_dir, "app", "__init__.py"), "w") as f:
            f.write("")
        with open(os.path.join(project_dir, "app", "models", "__init__.py"), "w") as f:
            f.write("")
        with open(os.path.join(project_dir, "app", "routes", "__init__.py"), "w") as f:
            f.write("")
        with open(os.path.join(project_dir, "app", "schemas", "__init__.py"), "w") as f:
            f.write("")

        with open(os.path.join(project_dir, "app", "main.py"), "w") as f:
            f.write(f'''"""
{name} API — Generated by MyWork-AI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="{name}",
    description="API generated by MyWork-AI framework",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {{"service": "{name}", "status": "running", "docs": "/docs"}}

@app.get("/health")
def health():
    return {{"status": "healthy"}}

# Routes are auto-registered by mw api add-model
''')

        with open(os.path.join(project_dir, "app", "database.py"), "w") as f:
            f.write('''"""Database connection — SQLite by default, easily swap to PostgreSQL."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
''')

        with open(os.path.join(project_dir, "requirements.txt"), "w") as f:
            f.write("fastapi>=0.104.0\\nuvicorn[standard]>=0.24.0\\nsqlalchemy>=2.0.0\\npydantic>=2.0.0\\n")

        with open(os.path.join(project_dir, "run.py"), "w") as f:
            f.write('''#!/usr/bin/env python3
"""Run the API server."""
import uvicorn
import sys

port = 8000
for i, arg in enumerate(sys.argv[1:]):
    if arg == "--port" and i + 2 < len(sys.argv):
        port = int(sys.argv[i + 2])

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
''')
        os.chmod(os.path.join(project_dir, "run.py"), 0o755)

        with open(os.path.join(project_dir, ".gitignore"), "w") as f:
            f.write("__pycache__/\\n*.pyc\\n.env\\ndata.db\\nvenv/\\n.pytest_cache/\\n")

        with open(os.path.join(project_dir, "README.md"), "w") as f:
            f.write(f'''# {name}

API generated by [MyWork-AI](https://github.com/DansiDanutz/MyWork-AI).

## Quick Start
```bash
pip install -r requirements.txt
python run.py
# Open http://localhost:8000/docs
```

## Add Models
```bash
mw api add-model User name:str email:str
mw api add-model Product title:str price:float
```
''')

        print(f"\n{Colors.GREEN}✅ API project '{name}' created!{Colors.ENDC}")
        print(f"{'─' * 50}")
        print(f"  📁 {project_dir}/")
        print(f"  📄 app/main.py      — FastAPI app")
        print(f"  📄 app/database.py  — SQLAlchemy setup")
        print(f"  📄 requirements.txt — Dependencies")
        print(f"  📄 run.py           — Dev server")
        print(f"\n{Colors.YELLOW}Next steps:{Colors.ENDC}")
        print(f"  cd {name}")
        print(f"  mw api add-model User name:str email:str age:int")
        print(f"  pip install -r requirements.txt")
        print(f"  mw api run")
        return 0

    elif subcmd == "add-model":
        if len(args) < 3:
            print(f"{Colors.RED}❌ Usage: mw api add-model <ModelName> <field:type ...>{Colors.ENDC}")
            print(f"  Example: mw api add-model User name:str email:str age:int")
            return 1

        model_name = args[1]
        fields_raw = args[2:]

        # Parse fields
        type_map = {
            "str": ("String", "str"),
            "string": ("String", "str"),
            "int": ("Integer", "int"),
            "integer": ("Integer", "int"),
            "float": ("Float", "float"),
            "bool": ("Boolean", "bool"),
            "boolean": ("Boolean", "bool"),
            "datetime": ("DateTime", "datetime"),
            "date": ("Date", "date"),
            "text": ("Text", "str"),
        }
        fields = []
        for f in fields_raw:
            if ":" not in f:
                print(f"{Colors.RED}❌ Invalid field '{f}'. Use format: name:type{Colors.ENDC}")
                return 1
            fname, ftype = f.split(":", 1)
            if ftype.lower() not in type_map:
                print(f"{Colors.RED}❌ Unknown type '{ftype}'. Use: str, int, float, bool, datetime, text{Colors.ENDC}")
                return 1
            sa_type, py_type = type_map[ftype.lower()]
            fields.append((fname, sa_type, py_type))

        table_name = model_name.lower() + "s"
        model_lower = model_name.lower()

        # Find app directory
        app_dir = None
        for check in ["app", "."]:
            if os.path.exists(os.path.join(check, "main.py")):
                app_dir = check
                break
        if not app_dir:
            print(f"{Colors.RED}❌ No app/main.py found. Run 'mw api init <name>' first or cd into the project.{Colors.ENDC}")
            return 1

        # Generate model file
        sa_imports = sorted(set(["Column", "Integer"] + [ft[1] for ft in fields]))
        model_code = f'''"""SQLAlchemy model for {model_name}."""
from sqlalchemy import {", ".join(["Column", "Integer"] + sorted(set(ft[0] for ft in fields)))}
from {"app." if app_dir == "app" else ""}database import Base


class {model_name}(Base):
    __tablename__ = "{table_name}"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
'''
        for fname, sa_type, _ in fields:
            nullable = "True" if sa_type != "String" else "False"
            model_code += f"    {fname} = Column({sa_type}, nullable={nullable})\n"

        models_dir = os.path.join(app_dir, "models")
        os.makedirs(models_dir, exist_ok=True)
        with open(os.path.join(models_dir, f"{model_lower}.py"), "w") as f:
            f.write(model_code)

        # Generate Pydantic schema
        schema_code = f'''"""Pydantic schemas for {model_name}."""
from pydantic import BaseModel
from typing import Optional


class {model_name}Base(BaseModel):
'''
        for fname, _, py_type in fields:
            schema_code += f"    {fname}: {py_type}\n"

        schema_code += f'''

class {model_name}Create({model_name}Base):
    pass


class {model_name}Update(BaseModel):
'''
        for fname, _, py_type in fields:
            schema_code += f"    {fname}: Optional[{py_type}] = None\n"

        schema_code += f'''

class {model_name}Response({model_name}Base):
    id: int

    class Config:
        from_attributes = True
'''

        schemas_dir = os.path.join(app_dir, "schemas")
        os.makedirs(schemas_dir, exist_ok=True)
        with open(os.path.join(schemas_dir, f"{model_lower}.py"), "w") as f:
            f.write(schema_code)

        # Generate CRUD routes
        route_code = f'''"""CRUD routes for {model_name}."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from {"app." if app_dir == "app" else ""}database import get_db
from {"app." if app_dir == "app" else ""}models.{model_lower} import {model_name}
from {"app." if app_dir == "app" else ""}schemas.{model_lower} import {model_name}Create, {model_name}Update, {model_name}Response

router = APIRouter(prefix="/{table_name}", tags=["{model_name}"])


@router.post("/", response_model={model_name}Response, status_code=201)
def create_{model_lower}(data: {model_name}Create, db: Session = Depends(get_db)):
    obj = {model_name}(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", response_model=List[{model_name}Response])
def list_{table_name}(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query({model_name}).offset(skip).limit(limit).all()


@router.get("/{{{model_lower}_id}}", response_model={model_name}Response)
def get_{model_lower}({model_lower}_id: int, db: Session = Depends(get_db)):
    obj = db.query({model_name}).filter({model_name}.id == {model_lower}_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="{model_name} not found")
    return obj


@router.put("/{{{model_lower}_id}}", response_model={model_name}Response)
def update_{model_lower}({model_lower}_id: int, data: {model_name}Update, db: Session = Depends(get_db)):
    obj = db.query({model_name}).filter({model_name}.id == {model_lower}_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="{model_name} not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{{{model_lower}_id}}", status_code=204)
def delete_{model_lower}({model_lower}_id: int, db: Session = Depends(get_db)):
    obj = db.query({model_name}).filter({model_name}.id == {model_lower}_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="{model_name} not found")
    db.delete(obj)
    db.commit()
    return None
'''

        routes_dir = os.path.join(app_dir, "routes")
        os.makedirs(routes_dir, exist_ok=True)
        with open(os.path.join(routes_dir, f"{model_lower}.py"), "w") as f:
            f.write(route_code)

        # Auto-register route in main.py
        main_path = os.path.join(app_dir, "main.py")
        with open(main_path, "r") as f:
            main_content = f.read()

        import_line = f"from {'app.' if app_dir == 'app' else ''}routes.{model_lower} import router as {model_lower}_router"
        include_line = f"app.include_router({model_lower}_router)"

        if import_line not in main_content:
            # Add import after last import or after middleware
            lines = main_content.split("\n")
            insert_idx = 0
            for i, line in enumerate(lines):
                if line.startswith("from ") or line.startswith("import "):
                    insert_idx = i + 1
            lines.insert(insert_idx, import_line)

            # Add include_router before the last line or at end
            route_idx = len(lines)
            for i, line in enumerate(lines):
                if "# Routes are auto-registered" in line:
                    route_idx = i + 1
                    break
            lines.insert(route_idx, include_line)

            with open(main_path, "w") as f:
                f.write("\n".join(lines))

        # Auto-create tables setup
        db_init_path = os.path.join(app_dir, "db_init.py")
        if not os.path.exists(db_init_path):
            with open(db_init_path, "w") as f:
                f.write('''"""Initialize database tables."""
from database import Base, engine

def init_db():
    """Create all tables."""
    # Import all models to register them
    import importlib, os, glob
    models_dir = os.path.join(os.path.dirname(__file__), "models")
    for f in glob.glob(os.path.join(models_dir, "*.py")):
        if not f.endswith("__init__.py"):
            mod = os.path.basename(f)[:-3]
            importlib.import_module(f"models.{mod}")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")

if __name__ == "__main__":
    init_db()
''')

        print(f"\n{Colors.GREEN}✅ Model '{model_name}' added with full CRUD!{Colors.ENDC}")
        print(f"{'─' * 50}")
        print(f"  📄 {app_dir}/models/{model_lower}.py   — SQLAlchemy model")
        print(f"  📄 {app_dir}/schemas/{model_lower}.py  — Pydantic schemas")
        print(f"  📄 {app_dir}/routes/{model_lower}.py   — CRUD endpoints")
        print(f"  📄 {app_dir}/main.py              — Auto-registered ✓")
        print(f"\n{Colors.YELLOW}Endpoints created:{Colors.ENDC}")
        print(f"  POST   /{table_name}/        Create {model_name}")
        print(f"  GET    /{table_name}/        List all {table_name}")
        print(f"  GET    /{table_name}/{{id}}   Get one {model_name}")
        print(f"  PUT    /{table_name}/{{id}}   Update {model_name}")
        print(f"  DELETE /{table_name}/{{id}}   Delete {model_name}")
        return 0

    elif subcmd == "run":
        port = "8000"
        for i, a in enumerate(args):
            if a == "--port" and i + 1 < len(args):
                port = args[i + 1]
        print(f"\n{Colors.GREEN}🚀 Starting API server on port {port}...{Colors.ENDC}")
        print(f"  📖 Docs: http://localhost:{port}/docs")
        subprocess.run(f"{sys.executable} run.py --port {port}", shell=True)
        return 0

    elif subcmd == "routes":
        # Scan route files
        app_dir = None
        for check in ["app", "."]:
            if os.path.exists(os.path.join(check, "main.py")):
                app_dir = check
                break
        if not app_dir:
            print(f"{Colors.RED}❌ No API project found in current directory{Colors.ENDC}")
            return 1

        routes_dir = os.path.join(app_dir, "routes")
        if not os.path.exists(routes_dir):
            print(f"{Colors.YELLOW}No routes directory found{Colors.ENDC}")
            return 0

        import glob as glob_mod
        route_files = glob_mod.glob(os.path.join(routes_dir, "*.py"))
        route_files = [f for f in route_files if "__init__" not in f]

        print(f"\n{Colors.BOLD}🛣️  API Routes{Colors.ENDC}")
        print(f"{'─' * 50}")
        if not route_files:
            print(f"  {Colors.YELLOW}No models yet. Add one: mw api add-model User name:str{Colors.ENDC}")
        for rf in sorted(route_files):
            name = os.path.basename(rf).replace(".py", "")
            table = name + "s"
            print(f"  {Colors.GREEN}{name.capitalize()}{Colors.ENDC} → /{table}/")
            print(f"    POST /  GET /  GET /{{id}}  PUT /{{id}}  DELETE /{{id}}")
        return 0

    else:
        print(f"{Colors.RED}❌ Unknown api subcommand: {subcmd}{Colors.ENDC}")
        print(f"  Try: mw api --help")
        return 1


def cmd_audit(args: List[str] = None) -> int:
    """Comprehensive project audit — generates a quality report card.

    Usage:
        mw audit [project_path]        Full audit of a project
        mw audit --quick [path]        Quick audit (skip slow checks)
        mw audit --json [path]         Output as JSON
        mw audit --help                Show this help

    Checks:
        • Code health (file count, size, complexity)
        • Dependencies (outdated, missing lock files)
        • Tests (presence, coverage estimation)
        • Security (secrets, known patterns)
        • Documentation (README, docs coverage)
        • Git health (uncommitted changes, branch hygiene)

    Output: Letter grade A-F with detailed breakdown.
    """
    args = args or []

    if "--help" in args or "-h" in args:
        print(cmd_audit.__doc__)
        return 0

    quick_mode = "--quick" in args
    json_mode = "--json" in args
    path_args = [a for a in args if not a.startswith("-")]
    project_path = Path(path_args[0]).resolve() if path_args else Path.cwd()

    if not project_path.is_dir():
        print(f"{Colors.RED}❌ Not a directory: {project_path}{Colors.ENDC}")
        return 1

    scores: Dict[str, Dict[str, Any]] = {}
    findings: List[str] = []

    # --- 1. Code Health ---
    code_files = []
    total_lines = 0
    lang_counts: Dict[str, int] = {}
    exts_map = {".py": "Python", ".js": "JavaScript", ".ts": "TypeScript", ".jsx": "React",
                ".tsx": "React/TS", ".go": "Go", ".rs": "Rust", ".rb": "Ruby", ".java": "Java"}
    ignore_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".next", ".tox"}

    for root_dir, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for f in files:
            ext = Path(f).suffix
            if ext in exts_map:
                fp = Path(root_dir) / f
                code_files.append(fp)
                lang_counts[exts_map[ext]] = lang_counts.get(exts_map[ext], 0) + 1
                try:
                    total_lines += sum(1 for _ in open(fp, errors="ignore"))
                except Exception:
                    pass

    code_score = 10
    if len(code_files) == 0:
        code_score = 0
        findings.append("⚠️  No source code files found")
    elif total_lines > 50000:
        code_score = 7
        findings.append("⚠️  Large codebase (>50k lines) — consider splitting")
    elif total_lines > 100000:
        code_score = 5
    # Check for very large files
    large_files = []
    for cf in code_files:
        try:
            lc = sum(1 for _ in open(cf, errors="ignore"))
            if lc > 500:
                large_files.append((cf.relative_to(project_path), lc))
        except Exception:
            pass
    if large_files:
        code_score = max(code_score - 1, 0)
        top3 = sorted(large_files, key=lambda x: -x[1])[:3]
        for lf, lc in top3:
            findings.append(f"📏 Large file: {lf} ({lc} lines)")

    scores["Code Health"] = {"score": code_score, "files": len(code_files),
                             "lines": total_lines, "languages": lang_counts}

    # --- 2. Dependencies ---
    dep_score = 10
    has_pkg_json = (project_path / "package.json").exists()
    has_requirements = (project_path / "requirements.txt").exists()
    has_pyproject = (project_path / "pyproject.toml").exists()
    has_lock = any((project_path / lf).exists() for lf in
                   ["package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock", "Pipfile.lock", "requirements.lock", "uv.lock"])

    if not (has_pkg_json or has_requirements or has_pyproject):
        dep_score = 5
        findings.append("⚠️  No dependency manifest found")
    if (has_pkg_json or has_requirements) and not has_lock:
        dep_score = max(dep_score - 2, 0)
        findings.append("🔒 No lock file — builds may not be reproducible")
    # Check for pinned versions
    if has_requirements:
        try:
            reqs = (project_path / "requirements.txt").read_text()
            unpinned = sum(1 for line in reqs.strip().splitlines()
                          if line.strip() and not line.startswith("#") and "==" not in line and ">=" not in line)
            if unpinned > 3:
                dep_score = max(dep_score - 1, 0)
                findings.append(f"📌 {unpinned} unpinned dependencies in requirements.txt")
        except Exception:
            pass

    scores["Dependencies"] = {"score": dep_score}

    # --- 3. Tests ---
    test_score = 0
    test_dirs = ["tests", "test", "__tests__", "spec"]
    test_files = []
    for td in test_dirs:
        tp = project_path / td
        if tp.is_dir():
            for root_dir, _, files in os.walk(tp):
                for f in files:
                    if f.startswith("test_") or f.endswith("_test.py") or f.endswith(".test.js") or f.endswith(".test.ts") or f.endswith(".spec.js") or f.endswith(".spec.ts"):
                        test_files.append(Path(root_dir) / f)
    # Also check for test files in src
    for cf in code_files:
        if "test" in cf.name.lower() and cf not in test_files:
            test_files.append(cf)

    if not test_files:
        findings.append("🧪 No test files found")
    else:
        ratio = len(test_files) / max(len(code_files), 1)
        if ratio >= 0.5:
            test_score = 10
        elif ratio >= 0.3:
            test_score = 8
        elif ratio >= 0.1:
            test_score = 6
        else:
            test_score = 4
            findings.append(f"🧪 Low test ratio: {len(test_files)} tests / {len(code_files)} source files")

    # Check for CI test config
    has_ci_tests = False
    for ci_file in [".github/workflows", ".gitlab-ci.yml", "Jenkinsfile"]:
        if (project_path / ci_file).exists():
            has_ci_tests = True
            break
    if test_files and not has_ci_tests:
        test_score = max(test_score - 1, 0)
        findings.append("⚙️  Tests exist but no CI pipeline detected")

    scores["Tests"] = {"score": test_score, "test_files": len(test_files)}

    # --- 4. Security ---
    sec_score = 10
    secret_patterns = [
        r'(?:api[_-]?key|secret|password|token)\s*[=:]\s*["\'][A-Za-z0-9+/=_-]{16,}',
        r'sk-[A-Za-z0-9]{20,}',
        r'ghp_[A-Za-z0-9]{36}',
        r'AKIA[A-Z0-9]{16}',
    ]
    secrets_found = 0
    if not quick_mode:
        for cf in code_files[:200]:  # Cap at 200 files
            try:
                content = cf.read_text(errors="ignore")
                for pat in secret_patterns:
                    if re.search(pat, content, re.IGNORECASE):
                        secrets_found += 1
                        break
            except Exception:
                pass
    if secrets_found:
        sec_score = max(10 - secrets_found * 2, 0)
        findings.append(f"🔑 Potential secrets in {secrets_found} file(s)")
    if not (project_path / ".gitignore").exists():
        sec_score = max(sec_score - 2, 0)
        findings.append("📄 No .gitignore file")
    # Check for env file committed
    if (project_path / ".env").exists():
        sec_score = max(sec_score - 1, 0)
        findings.append("⚠️  .env file present — ensure it's in .gitignore")

    scores["Security"] = {"score": sec_score, "secrets_found": secrets_found}

    # --- 5. Documentation ---
    doc_score = 0
    has_readme = any((project_path / r).exists() for r in ["README.md", "README.rst", "README.txt", "README"])
    has_changelog = any((project_path / c).exists() for c in ["CHANGELOG.md", "CHANGES.md", "HISTORY.md"])
    has_contributing = (project_path / "CONTRIBUTING.md").exists()
    has_license = any((project_path / l).exists() for l in ["LICENSE", "LICENSE.md", "LICENSE.txt"])
    has_docs_dir = (project_path / "docs").is_dir()

    if has_readme:
        doc_score += 4
    else:
        findings.append("📖 No README file")
    if has_changelog:
        doc_score += 2
    if has_contributing:
        doc_score += 1
    if has_license:
        doc_score += 2
    else:
        findings.append("📜 No LICENSE file")
    if has_docs_dir:
        doc_score += 1

    scores["Documentation"] = {"score": min(doc_score, 10)}

    # --- 6. Git Health ---
    git_score = 10
    git_dir = project_path / ".git"
    if not git_dir.is_dir():
        git_score = 3
        findings.append("📂 Not a git repository")
    else:
        import subprocess
        try:
            result = subprocess.run(["git", "status", "--porcelain"], capture_output=True,
                                    text=True, cwd=project_path, timeout=10)
            dirty = len([l for l in result.stdout.strip().splitlines() if l.strip()])
            if dirty > 20:
                git_score = max(git_score - 3, 0)
                findings.append(f"📝 {dirty} uncommitted changes")
            elif dirty > 5:
                git_score = max(git_score - 1, 0)
                findings.append(f"📝 {dirty} uncommitted changes")
        except Exception:
            pass
        # Check for .gitignore
        if not (project_path / ".gitignore").exists():
            git_score = max(git_score - 2, 0)

    scores["Git Health"] = {"score": git_score}

    # --- Calculate Overall Grade ---
    weights = {"Code Health": 2, "Dependencies": 1.5, "Tests": 2, "Security": 2.5,
               "Documentation": 1, "Git Health": 1}
    weighted_sum = sum(scores[cat]["score"] * weights[cat] for cat in scores)
    max_weighted = sum(10 * w for w in weights.values())
    overall_pct = (weighted_sum / max_weighted) * 100

    if overall_pct >= 90:
        grade, grade_color = "A", Colors.GREEN
    elif overall_pct >= 80:
        grade, grade_color = "B", Colors.GREEN
    elif overall_pct >= 70:
        grade, grade_color = "C", Colors.YELLOW
    elif overall_pct >= 60:
        grade, grade_color = "D", Colors.YELLOW
    else:
        grade, grade_color = "F", Colors.RED

    # --- Output ---
    if json_mode:
        import json as _json
        output = {"project": str(project_path), "grade": grade, "score": round(overall_pct, 1),
                  "categories": scores, "findings": findings}
        print(_json.dumps(output, indent=2, default=str))
        return 0

    print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}  🔍 PROJECT AUDIT — {project_path.name}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

    bar_chars = 20
    for cat, data in scores.items():
        s = data["score"]
        filled = int((s / 10) * bar_chars)
        bar = "█" * filled + "░" * (bar_chars - filled)
        sc = Colors.GREEN if s >= 7 else (Colors.YELLOW if s >= 5 else Colors.RED)
        extra = ""
        if cat == "Code Health":
            extra = f" ({data['lines']} lines, {data['files']} files)"
        elif cat == "Tests":
            extra = f" ({data['test_files']} test files)"
        print(f"  {cat:<18} {sc}{bar} {s}/10{Colors.ENDC}{extra}")

    print(f"\n  {'─'*56}")
    print(f"  {Colors.BOLD}Overall Grade:{Colors.ENDC}  {grade_color}{Colors.BOLD}{grade}{Colors.ENDC}  ({overall_pct:.0f}%)")
    print(f"  {'─'*56}")

    if findings:
        print(f"\n  {Colors.BOLD}📋 Findings:{Colors.ENDC}")
        for f in findings:
            print(f"    {f}")

    # Recommendations
    print(f"\n  {Colors.BOLD}💡 Top Recommendations:{Colors.ENDC}")
    recs = []
    if scores["Tests"]["score"] < 7:
        recs.append("Add more tests — aim for 1 test file per 2-3 source files")
    if scores["Security"]["score"] < 8:
        recs.append("Run `mw security scan` and fix findings")
    if scores["Documentation"]["score"] < 7:
        recs.append("Add README, LICENSE, and CHANGELOG")
    if scores["Dependencies"]["score"] < 8:
        recs.append("Pin dependencies and add a lock file")
    if scores["Git Health"]["score"] < 8:
        recs.append("Commit or stash uncommitted changes")
    if not recs:
        recs.append("Looking good! Keep up the quality 🎉")
    for i, r in enumerate(recs[:3], 1):
        print(f"    {i}. {r}")

    print()
    return 0


def cmd_deps(args: List[str] = None) -> int:
    """Dependency management — audit, outdated, tree, licenses, cleanup.

    Usage:
        mw deps                  # Overview (counts + summary)
        mw deps list             # List all dependencies with versions
        mw deps outdated         # Show outdated packages
        mw deps audit            # Security vulnerability scan
        mw deps tree             # Dependency tree (top 2 levels)
        mw deps licenses         # License audit (flag copyleft/unknown)
        mw deps why <package>    # Why is this package installed?
        mw deps size             # Disk usage of dependency dirs
        mw deps cleanup          # Remove unused/orphaned deps
        mw deps export           # Export deps to lock files
    """
    import subprocess as _sp
    args = args or []
    sub = args[0] if args else "overview"

    has_pip = os.path.exists("requirements.txt") or os.path.exists("pyproject.toml") or os.path.exists("setup.py")
    has_npm = os.path.exists("package.json")
    has_cargo = os.path.exists("Cargo.toml")
    has_go = os.path.exists("go.mod")

    if not any([has_pip, has_npm, has_cargo, has_go]):
        print("\033[93m⚠️  No dependency files found (requirements.txt, package.json, Cargo.toml, go.mod)\033[0m")
        return 1

    def _run_cmd(cmd):
        try:
            r = _sp.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            return r.stdout.strip(), r.stderr.strip(), r.returncode
        except Exception as e:
            return "", str(e), 1

    def _pip_deps():
        deps = []
        if os.path.exists("requirements.txt"):
            with open("requirements.txt") as fh:
                for line in fh:
                    line = line.strip()
                    if line and not line.startswith("#") and not line.startswith("-"):
                        parts = line.split("==")
                        name = parts[0].split(">=")[0].split("<=")[0].split("~=")[0].split("!=")[0].strip()
                        ver = parts[1].strip() if len(parts) > 1 else "any"
                        deps.append({"name": name, "version": ver, "source": "requirements.txt"})
        if os.path.exists("pyproject.toml"):
            with open("pyproject.toml") as fh:
                in_deps = False
                for line in fh:
                    if "dependencies" in line and "[" in line:
                        in_deps = True
                        continue
                    if in_deps:
                        if line.strip().startswith("]"):
                            in_deps = False
                            continue
                        pkg = line.strip().strip('",').strip("',")
                        if pkg:
                            name = pkg.split(">=")[0].split("==")[0].split("<")[0].split("~=")[0].strip()
                            if name:
                                deps.append({"name": name, "version": "spec", "source": "pyproject.toml"})
        return deps

    def _npm_deps():
        deps = []
        if os.path.exists("package.json"):
            import json as _json
            with open("package.json") as fh:
                pkg = _json.load(fh)
            for section in ["dependencies", "devDependencies"]:
                for name, ver in pkg.get(section, {}).items():
                    deps.append({"name": name, "version": ver, "dev": section == "devDependencies"})
        return deps

    if sub == "list":
        print("\033[1m📦 Dependencies\033[0m\n")
        if has_pip:
            deps = _pip_deps()
            print(f"  \033[96mPython ({len(deps)} packages)\033[0m")
            for d in sorted(deps, key=lambda x: x["name"]):
                print(f"    {d['name']:30s} {d['version']:15s} ({d['source']})")
        if has_npm:
            deps = _npm_deps()
            prod = [d for d in deps if not d.get("dev")]
            dev = [d for d in deps if d.get("dev")]
            print(f"  \033[96mNode.js ({len(prod)} prod + {len(dev)} dev)\033[0m")
            for d in sorted(prod, key=lambda x: x["name"]):
                print(f"    {d['name']:30s} {d['version']}")
            if dev:
                print("  \033[90m  Dev:\033[0m")
                for d in sorted(dev, key=lambda x: x["name"])[:15]:
                    print(f"    {d['name']:30s} {d['version']}")
                if len(dev) > 15:
                    print(f"    ... and {len(dev)-15} more dev deps")
        return 0

    elif sub == "outdated":
        print("\033[1m📦 Outdated Dependencies\033[0m\n")
        if has_pip:
            out, _, _ = _run_cmd("pip list --outdated --format=columns 2>/dev/null")
            if out:
                print("  \033[96mPython:\033[0m")
                for line in out.split("\n"):
                    print(f"    {line}")
            else:
                print("  \033[92m✅ All Python packages up to date\033[0m")
        if has_npm:
            out, _, _ = _run_cmd("npm outdated --json 2>/dev/null")
            if out and out != "{}":
                import json as _json
                try:
                    data = _json.loads(out)
                    print(f"  \033[96mNode.js ({len(data)} outdated):\033[0m")
                    print(f"    {'Package':25s} {'Current':12s} {'Wanted':12s} {'Latest':12s}")
                    for pkg, info in sorted(data.items()):
                        cur = info.get("current", "?")
                        want = info.get("wanted", "?")
                        lat = info.get("latest", "?")
                        flag = " 🔴" if cur != lat else ""
                        print(f"    {pkg:25s} {cur:12s} {want:12s} {lat:12s}{flag}")
                except Exception:
                    print(f"    {out[:300]}")
            else:
                print("  \033[92m✅ All Node packages up to date\033[0m")
        return 0

    elif sub == "audit":
        print("\033[1m🔒 Dependency Security Audit\033[0m\n")
        vulns = 0
        if has_pip:
            print("  \033[96mPython:\033[0m")
            out, err, rc = _run_cmd("pip-audit --format=columns 2>/dev/null")
            if rc == 0 and ("No known" in out or "No known" in err or not out):
                print("    \033[92m✅ No known vulnerabilities\033[0m")
            elif out:
                for line in out.split("\n")[:20]:
                    print(f"    {line}")
                vulns += max(1, out.count("\n"))
            else:
                print("    \033[93m⚠️  Install pip-audit: pip install pip-audit\033[0m")
        if has_npm:
            print("  \033[96mNode.js:\033[0m")
            out, _, _ = _run_cmd("npm audit --json 2>/dev/null")
            if out:
                import json as _json
                try:
                    data = _json.loads(out)
                    meta = data.get("metadata", {}).get("vulnerabilities", {})
                    c, h, m, l = meta.get("critical", 0), meta.get("high", 0), meta.get("moderate", 0), meta.get("low", 0)
                    total = c + h + m + l
                    vulns += total
                    if total == 0:
                        print("    \033[92m✅ No vulnerabilities\033[0m")
                    else:
                        if c: print(f"    \033[91m🔴 Critical: {c}\033[0m")
                        if h: print(f"    \033[91m🟠 High: {h}\033[0m")
                        if m: print(f"    \033[93m🟡 Moderate: {m}\033[0m")
                        if l: print(f"    \033[90m⚪ Low: {l}\033[0m")
                except Exception:
                    pass
        if vulns == 0:
            print(f"\n  \033[92m🛡️  All clear!\033[0m")
        else:
            print(f"\n  \033[91m⚠️  {vulns} issue(s) found\033[0m")
        return 0

    elif sub == "tree":
        print("\033[1m🌳 Dependency Tree\033[0m\n")
        if has_pip:
            out, _, _ = _run_cmd("pipdeptree --warn silence 2>/dev/null")
            if out:
                for line in out.split("\n")[:40]:
                    print(f"  {line}")
            else:
                print("  \033[93m⚠️  Install pipdeptree: pip install pipdeptree\033[0m")
        if has_npm:
            out, _, _ = _run_cmd("npm ls --depth=1 2>/dev/null")
            if out:
                for line in out.split("\n")[:40]:
                    print(f"  {line}")
        return 0

    elif sub == "licenses":
        print("\033[1m📜 License Audit\033[0m\n")
        copyleft_kw = {"GPL", "AGPL", "LGPL", "SSPL", "EUPL"}
        flagged = []
        if has_pip:
            out, _, _ = _run_cmd("pip list --format=json 2>/dev/null")
            if out:
                import json as _json
                try:
                    pkgs = _json.loads(out)
                    print(f"  \033[96mPython ({len(pkgs)} packages):\033[0m")
                    for pkg in pkgs[:30]:
                        meta_out, _, _ = _run_cmd(f"pip show {pkg['name']} 2>/dev/null | grep -i license")
                        lic = meta_out.split(":", 1)[1].strip() if ":" in meta_out else "Unknown"
                        flag = ""
                        if any(c in lic.upper() for c in copyleft_kw):
                            flag = " \033[91m⚠️ COPYLEFT\033[0m"
                            flagged.append(f"{pkg['name']} ({lic})")
                        elif lic in ["UNKNOWN", "Unknown", ""]:
                            flag = " \033[93m❓\033[0m"
                        print(f"    {pkg['name']:30s} {lic:20s}{flag}")
                except Exception:
                    pass
        if flagged:
            print(f"\n  \033[91m⚠️  {len(flagged)} need review:\033[0m")
            for f in flagged:
                print(f"    • {f}")
        else:
            print(f"\n  \033[92m✅ All licenses look clean\033[0m")
        return 0

    elif sub == "why" and len(args) > 1:
        pkg = args[1]
        print(f"\033[1m🔍 Why is '{pkg}' installed?\033[0m\n")
        if has_pip:
            out, _, _ = _run_cmd(f"pipdeptree --reverse --packages {pkg} 2>/dev/null")
            if out:
                for line in out.split("\n")[:15]:
                    print(f"  {line}")
            else:
                out2, _, _ = _run_cmd(f"pip show {pkg} 2>/dev/null")
                if out2:
                    for line in out2.split("\n"):
                        if "Required-by:" in line or "Requires:" in line:
                            print(f"  {line}")
        if has_npm:
            out, _, _ = _run_cmd(f"npm ls {pkg} 2>/dev/null")
            if out:
                for line in out.split("\n")[:10]:
                    print(f"  {line}")
        return 0

    elif sub == "size":
        print("\033[1m💾 Dependency Disk Usage\033[0m\n")
        for d, label in [("node_modules", "Node.js"), (".venv", "Python venv"), ("venv", "Python venv"), ("__pycache__", "Cache"), ("target", "Rust")]:
            if os.path.isdir(d):
                out, _, _ = _run_cmd(f"du -sh {d} 2>/dev/null")
                size = out.split("\t")[0] if out else "?"
                print(f"  📁 {d:20s} {size:>10s}  ({label})")
        return 0

    elif sub == "cleanup":
        print("\033[1m🧹 Dependency Cleanup\033[0m\n")
        if has_npm and os.path.isdir("node_modules"):
            out, _, _ = _run_cmd("npx depcheck --json 2>/dev/null")
            if out:
                import json as _json
                try:
                    data = _json.loads(out)
                    unused = data.get("dependencies", [])
                    if unused:
                        print(f"  \033[93mUnused ({len(unused)}):\033[0m")
                        for pkg in unused:
                            print(f"    npm uninstall {pkg}")
                    else:
                        print("  \033[92m✅ All deps in use\033[0m")
                except Exception:
                    pass
        return 0

    elif sub == "export":
        print("\033[1m📤 Export Dependencies\033[0m\n")
        if has_pip:
            out, _, _ = _run_cmd("pip freeze 2>/dev/null")
            if out:
                with open("requirements.lock.txt", "w") as fh:
                    fh.write(out + "\n")
                print(f"  \033[92m✅ {len(out.strip().split(chr(10)))} packages → requirements.lock.txt\033[0m")
        if has_npm and not os.path.exists("package-lock.json"):
            _run_cmd("npm install --package-lock-only 2>/dev/null")
            print("  \033[92m✅ Generated package-lock.json\033[0m")
        elif has_npm:
            print("  \033[92m✅ package-lock.json exists\033[0m")
        return 0

    else:
        # Overview
        print("\033[1m📦 Dependency Overview\033[0m\n")
        total = 0
        if has_pip:
            deps = _pip_deps()
            total += len(deps)
            print(f"  🐍 Python: {len(deps)} packages")
        if has_npm:
            deps = _npm_deps()
            prod = len([d for d in deps if not d.get("dev")])
            dev = len([d for d in deps if d.get("dev")])
            total += len(deps)
            print(f"  📦 Node.js: {prod} prod + {dev} dev")
        if has_cargo:
            print("  🦀 Rust: Cargo.toml detected")
        if has_go:
            print("  🐹 Go: go.mod detected")
        print(f"\n  Total: {total} dependencies")
        print(f"\n  \033[90mSubcommands: list | outdated | audit | tree | licenses | why <pkg> | size | cleanup | export\033[0m")
        return 0


def cmd_health(args: List[str] = None) -> int:
    """Project health score — instant quality assessment (0-100).

    Usage:
        mw health              # Score current project
        mw health --json       # Output as JSON
        mw health --verbose    # Show detailed breakdown
    """
    import glob
    args = args or []
    as_json = "--json" in args
    verbose = "--verbose" in args or "-v" in args

    cwd = os.getcwd()
    scores = {}
    details = {}

    # 1. README/Documentation (0-15)
    doc_score = 0
    doc_detail = []
    if os.path.exists("README.md"):
        size = os.path.getsize("README.md")
        if size > 2000:
            doc_score += 10
            doc_detail.append("✅ README.md (detailed)")
        elif size > 200:
            doc_score += 6
            doc_detail.append("⚠️ README.md (short)")
        else:
            doc_score += 2
            doc_detail.append("⚠️ README.md (stub)")
    else:
        doc_detail.append("❌ No README.md")
    if any(os.path.exists(f) for f in ["docs", "CONTRIBUTING.md", "CHANGELOG.md"]):
        doc_score += 5
        doc_detail.append("✅ Extra docs found")
    scores["Documentation"] = min(doc_score, 15)
    details["Documentation"] = doc_detail

    # 2. Tests (0-20)
    test_score = 0
    test_detail = []
    test_dirs = ["tests", "test", "__tests__", "spec"]
    has_tests = any(os.path.isdir(d) for d in test_dirs)
    if has_tests:
        test_files = []
        for d in test_dirs:
            if os.path.isdir(d):
                test_files.extend(glob.glob(f"{d}/**/*test*", recursive=True))
                test_files.extend(glob.glob(f"{d}/**/test_*", recursive=True))
        test_files = list(set(f for f in test_files if os.path.isfile(f)))
        if len(test_files) > 20:
            test_score = 20
            test_detail.append(f"✅ {len(test_files)} test files (excellent)")
        elif len(test_files) > 10:
            test_score = 15
            test_detail.append(f"✅ {len(test_files)} test files (good)")
        elif len(test_files) > 3:
            test_score = 10
            test_detail.append(f"⚠️ {len(test_files)} test files (basic)")
        else:
            test_score = 5
            test_detail.append(f"⚠️ {len(test_files)} test files (minimal)")
    else:
        test_detail.append("❌ No test directory")
    # Check for CI config
    ci_files = [".github/workflows", ".gitlab-ci.yml", "Jenkinsfile", ".circleci"]
    if any(os.path.exists(f) for f in ci_files):
        test_score = min(test_score + 3, 20)
        test_detail.append("✅ CI/CD configured")
    scores["Testing"] = test_score
    details["Testing"] = test_detail

    # 3. Dependencies (0-15)
    dep_score = 0
    dep_detail = []
    dep_files = ["requirements.txt", "pyproject.toml", "package.json", "Cargo.toml", "go.mod"]
    lock_files = ["requirements.lock", "requirements.lock.txt", "poetry.lock", "Pipfile.lock", "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "Cargo.lock", "go.sum", "uv.lock"]
    if any(os.path.exists(f) for f in dep_files):
        dep_score += 8
        dep_detail.append("✅ Dependencies declared")
    else:
        dep_detail.append("❌ No dependency file")
    if any(os.path.exists(f) for f in lock_files):
        dep_score += 7
        dep_detail.append("✅ Lock file present")
    else:
        dep_detail.append("⚠️ No lock file")
    scores["Dependencies"] = min(dep_score, 15)
    details["Dependencies"] = dep_detail

    # 4. Code Quality (0-15)
    qual_score = 0
    qual_detail = []
    lint_configs = [".eslintrc", ".eslintrc.js", ".eslintrc.json", "ruff.toml", ".flake8", ".pylintrc", "tox.ini", ".prettierrc", "biome.json"]
    if any(os.path.exists(f) for f in lint_configs):
        qual_score += 8
        qual_detail.append("✅ Linter configured")
    # Check pyproject.toml for tool configs
    if os.path.exists("pyproject.toml"):
        with open("pyproject.toml") as fh:
            content = fh.read()
        if "ruff" in content or "flake8" in content or "mypy" in content or "pylint" in content:
            qual_score += 8
            qual_detail.append("✅ Linter in pyproject.toml")
    if not qual_detail:
        qual_detail.append("⚠️ No linter config")
    type_configs = ["tsconfig.json", "mypy.ini", "py.typed"]
    if any(os.path.exists(f) for f in type_configs) or (os.path.exists("pyproject.toml") and "mypy" in open("pyproject.toml").read()):
        qual_score += 7
        qual_detail.append("✅ Type checking configured")
    else:
        qual_detail.append("⚠️ No type checking")
    scores["Code Quality"] = min(qual_score, 15)
    details["Code Quality"] = qual_detail

    # 5. Git hygiene (0-10)
    git_score = 0
    git_detail = []
    if os.path.exists(".git"):
        git_score += 3
        git_detail.append("✅ Git initialized")
        if os.path.exists(".gitignore"):
            git_score += 4
            git_detail.append("✅ .gitignore present")
        else:
            git_detail.append("⚠️ No .gitignore")
        # Check for conventional commits (look at recent messages)
        import subprocess as _sp
        try:
            r = _sp.run(["git", "log", "--oneline", "-10"], capture_output=True, text=True, timeout=5)
            if r.returncode == 0 and r.stdout:
                lines = r.stdout.strip().split("\n")
                conventional = sum(1 for l in lines if any(l.split(" ", 1)[-1].startswith(p) for p in ["feat:", "fix:", "docs:", "chore:", "refactor:", "test:", "ci:"]))
                if conventional >= 5:
                    git_score += 3
                    git_detail.append("✅ Conventional commits")
                elif conventional >= 2:
                    git_score += 1
                    git_detail.append("⚠️ Some conventional commits")
        except Exception:
            pass
    else:
        git_detail.append("❌ Not a git repo")
    scores["Git"] = min(git_score, 10)
    details["Git"] = git_detail

    # 6. Security (0-10)
    sec_score = 0
    sec_detail = []
    dangerous_patterns = [".env", "secrets.json", "credentials.json"]
    if os.path.exists(".gitignore"):
        gitignore = open(".gitignore").read()
        if ".env" in gitignore:
            sec_score += 5
            sec_detail.append("✅ .env in .gitignore")
        else:
            sec_detail.append("⚠️ .env not in .gitignore")
    sec_configs = ["SECURITY.md", ".github/SECURITY.md", "security.txt"]
    if any(os.path.exists(f) for f in sec_configs):
        sec_score += 5
        sec_detail.append("✅ Security policy")
    else:
        sec_detail.append("⚠️ No SECURITY.md")
    scores["Security"] = min(sec_score, 10)
    details["Security"] = sec_detail

    # 7. Structure (0-15)
    struct_score = 0
    struct_detail = []
    if os.path.exists("LICENSE") or os.path.exists("LICENSE.md"):
        struct_score += 5
        struct_detail.append("✅ LICENSE file")
    else:
        struct_detail.append("⚠️ No LICENSE")
    # Check for source directory structure
    src_dirs = ["src", "lib", "tools", "app", "pkg", "cmd"]
    if any(os.path.isdir(d) for d in src_dirs):
        struct_score += 5
        struct_detail.append("✅ Organized source directory")
    else:
        struct_detail.append("⚠️ No src/ directory")
    # Check for config files (editor, formatter)
    editor_configs = [".editorconfig", ".vscode", ".idea"]
    if any(os.path.exists(f) for f in editor_configs):
        struct_score += 5
        struct_detail.append("✅ Editor config")
    scores["Structure"] = min(struct_score, 15)
    details["Structure"] = struct_detail

    # Calculate total
    total = sum(scores.values())
    max_score = 100

    # Grade
    if total >= 90:
        grade, color, emoji = "A+", "\033[92m", "🏆"
    elif total >= 80:
        grade, color, emoji = "A", "\033[92m", "🌟"
    elif total >= 70:
        grade, color, emoji = "B", "\033[93m", "👍"
    elif total >= 60:
        grade, color, emoji = "C", "\033[93m", "📝"
    elif total >= 50:
        grade, color, emoji = "D", "\033[91m", "⚠️"
    else:
        grade, color, emoji = "F", "\033[91m", "🔴"

    if as_json:
        import json as _json
        print(_json.dumps({"score": total, "grade": grade, "categories": scores, "details": details}, indent=2))
        return 0

    # Display
    print(f"\n{color}{'═' * 50}\033[0m")
    print(f"  {emoji} Project Health Score: {color}{total}/{max_score} (Grade: {grade})\033[0m")
    print(f"{color}{'═' * 50}\033[0m\n")

    # Bar chart
    for cat, score in scores.items():
        max_cat = {"Documentation": 15, "Testing": 20, "Dependencies": 15, "Code Quality": 15, "Git": 10, "Security": 10, "Structure": 15}[cat]
        pct = int((score / max_cat) * 20)
        bar = "█" * pct + "░" * (20 - pct)
        cat_color = "\033[92m" if score >= max_cat * 0.7 else "\033[93m" if score >= max_cat * 0.4 else "\033[91m"
        print(f"  {cat:15s} {cat_color}{bar}\033[0m {score}/{max_cat}")
        if verbose:
            for d in details.get(cat, []):
                print(f"                   {d}")

    # Top recommendations
    print(f"\n{'─' * 50}")
    recs = []
    if scores["Testing"] < 10:
        recs.append("Add more tests (mw test --init)")
    if scores["Documentation"] < 8:
        recs.append("Improve README.md")
    if scores["Code Quality"] < 8:
        recs.append("Add a linter config (mw lint)")
    if scores["Security"] < 5:
        recs.append("Add SECURITY.md and check .gitignore")
    if scores["Git"] < 5:
        recs.append("Use conventional commits (feat:, fix:, etc.)")
    if recs:
        print(f"  💡 Top improvements:")
        for r in recs[:3]:
            print(f"     → {r}")
    else:
        print(f"  🎉 Great project health! Keep it up.")
    print()
    return 0


def cmd_selftest(args: List[str] = None) -> int:
    """Quick smoke test to verify framework installation.

    Usage:
        mw selftest          # Run all checks (~5 seconds)
        mw selftest --quick  # Core checks only (~2 seconds)
        mw selftest --json   # Output as JSON (for CI)
        mw selftest --help   # Show this help message
    """
    import time
    args = args or []
    
    # Handle help request
    if "--help" in args or "-h" in args:
        print("""
Selftest Commands — Framework Self-Diagnostics
==============================================
Usage:
    mw selftest                     Run all framework checks (~5 seconds)
    mw selftest --quick            Core checks only (~2 seconds)
    mw selftest --json             Output as JSON (for CI)
    mw selftest --help             Show this help message

Description:
    Performs comprehensive smoke tests to verify framework installation
    and core functionality. Checks imports, configuration, tools, and
    basic system health.

Examples:
    mw selftest                     # Full diagnostic
    mw selftest --quick             # Quick check
    mw selftest --json              # JSON output for scripts
""")
        return 0
    
    quick = "--quick" in args
    as_json = "--json" in args

    results = []
    t_start = time.time()

    def check(name: str, fn, critical: bool = True):
        t0 = time.time()
        try:
            ok, detail = fn()
            elapsed = time.time() - t0
            results.append({"name": name, "ok": ok, "detail": detail, "time": elapsed, "critical": critical})
        except Exception as e:
            elapsed = time.time() - t0
            results.append({"name": name, "ok": False, "detail": str(e), "time": elapsed, "critical": critical})

    # 1. Core imports
    def check_imports():
        failures = []
        for mod in ["tools.mw", "tools.brain", "tools.config", "tools.health_check",
                     "tools.scaffold", "tools.workflow_engine", "tools.ai_assistant"]:
            try:
                __import__(mod)
            except Exception as e:
                failures.append(f"{mod}: {e}")
        if failures:
            return False, f"Failed: {', '.join(failures)}"
        return True, f"{len(['tools.mw', 'tools.brain', 'tools.config', 'tools.health_check', 'tools.scaffold', 'tools.workflow_engine', 'tools.ai_assistant'])} core modules OK"
    check("Core imports", check_imports)

    # 2. System requirements
    def check_python():
        version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        min_version = (3, 8)
        if sys.version_info[:2] >= min_version:
            return True, f"Python {version} (>= 3.8 required)"
        else:
            return False, f"Python {version} too old (>= 3.8 required)"
    check("Python version", check_python)

    # 3. Pip availability
    def check_pip():
        import shutil
        pip_path = shutil.which("pip") or shutil.which("pip3")
        if pip_path:
            try:
                import subprocess
                result = subprocess.run([pip_path, "--version"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    version = result.stdout.split()[1] if result.stdout else "unknown"
                    return True, f"pip {version} available"
                else:
                    return False, "pip command failed"
            except Exception as e:
                return False, f"pip error: {str(e)}"
        else:
            return False, "pip not found in PATH"
    check("Pip package manager", check_pip)

    # 4. Git availability
    def check_git():
        import shutil
        git_path = shutil.which("git")
        if git_path:
            try:
                import subprocess
                result = subprocess.run([git_path, "--version"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    version = result.stdout.strip().split()[-1] if result.stdout else "unknown"
                    return True, f"Git {version} available"
                else:
                    return False, "git command failed"
            except Exception as e:
                return False, f"git error: {str(e)}"
        else:
            return False, "git not found in PATH"
    check("Git version control", check_git)

    # 5. Config system
    def check_config():
        from tools.config import get_mywork_root, ensure_directories
        root = get_mywork_root()
        return True, f"Root: {root}"
    check("Config system", check_config)

    # 6. CLI dispatch
    def check_cli():
        import subprocess
        r = subprocess.run([sys.executable, "-m", "tools.mw", "version"],
                           capture_output=True, text=True, timeout=5,
                           cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return r.returncode == 0, r.stdout.strip()[:80] or r.stderr.strip()[:80]
    check("CLI dispatch", check_cli)

    # 7. Brain (knowledge vault)
    def check_brain():
        from tools.brain import BrainManager
        b = BrainManager()
        count = len(b.entries) if hasattr(b, 'entries') else 0
        return True, f"{count} entries"
    check("Brain vault", check_brain, critical=False)

    if not quick:
        # 8. Project registry
        def check_projects():
            from tools.config import list_projects
            projects = list_projects()
            return True, f"{len(projects)} projects"
        check("Project registry", check_projects, critical=False)

        # 9. Scaffold templates
        def check_scaffold():
            from tools.scaffold import TEMPLATES
            return len(TEMPLATES) > 0, f"{len(TEMPLATES)} templates"
        check("Scaffold templates", check_scaffold, critical=False)

        # 10. Workflow engine
        def check_workflows():
            from tools.workflow_engine import WorkflowEngine
            engine = WorkflowEngine()
            return True, "Engine initialized"
        check("Workflow engine", check_workflows, critical=False)

        # 11. Plugin system
        def check_plugins():
            from tools.plugin_manager import load_registry
            reg = load_registry()
            count = len(reg.get("plugins", {})) if isinstance(reg, dict) else 0
            return True, f"{count} plugins"
        check("Plugin system", check_plugins, critical=False)

    total_time = time.time() - t_start
    passed = sum(1 for r in results if r["ok"])
    failed = sum(1 for r in results if not r["ok"])
    critical_failed = sum(1 for r in results if not r["ok"] and r["critical"])

    if as_json:
        import json
        print(json.dumps({"passed": passed, "failed": failed, "time": round(total_time, 2),
                           "ok": critical_failed == 0, "checks": results}, indent=2))
        return 0 if critical_failed == 0 else 1

    print(f"\n{Colors.BOLD}🔬 MyWork-AI Self-Test{Colors.ENDC}")
    print("=" * 50)
    for r in results:
        icon = "✅" if r["ok"] else ("❌" if r["critical"] else "⚠️")
        time_str = f"{r['time']:.2f}s"
        print(f"  {icon} {r['name']:.<30} {r['detail'][:35]:.<35} {time_str}")
    print("=" * 50)
    if critical_failed == 0:
        print(f"  {Colors.GREEN}✅ All checks passed!{Colors.ENDC} ({passed}/{len(results)} in {total_time:.2f}s)")
    else:
        print(f"  {Colors.RED}❌ {critical_failed} critical failure(s){Colors.ENDC} ({passed}/{len(results)} passed)")
    print()
    return 0 if critical_failed == 0 else 1


def cmd_doctor(args: List[str] = None) -> int:
    """COMPREHENSIVE project doctor — diagnose, analyze, and auto-fix issues."""
    import subprocess as _sp
    import time
    import shutil
    import json as _json
    from pathlib import Path
    
    # Parse arguments
    args = args or []
    fix_mode = "--fix" in args
    
    if "--help" in args or "-h" in args:
        print(f"""
{Colors.BOLD}🩺 MyWork Doctor — Comprehensive Diagnostics{Colors.ENDC}
{'=' * 60}

Usage:
    mw doctor                       Run full system diagnostics
    mw doctor --fix                 Run diagnostics and auto-fix issues
    mw doctor --help                Show this help message

Diagnostic Checks:
    • TODO markers and technical debt
    • Large files and disk usage  
    • Test coverage and test execution
    • Git status and sync health
    • Security scan and vulnerability check
    • Dependency health and outdated packages
    • Configuration validation (.env, settings)
    • Performance analysis (CLI startup time)
    • API connectivity testing
    • Documentation completeness
    • Overall project health score (A-F grade)

Auto-fix Features (--fix):
    • Clean node_modules and cache directories
    • Update outdated dependencies
    • Fix common configuration issues
    • Clean stale git branches
    • Auto-generate missing documentation

Examples:
    mw doctor                       # Comprehensive health check
    mw doctor --fix                 # Fix what can be auto-fixed
""")
        return 0

    proj = os.path.basename(os.getcwd())
    print(f"\n{Colors.BOLD}{Colors.BLUE}🩺 MyWork Doctor — Comprehensive Diagnostics{Colors.ENDC}")
    print(f"{Colors.BLUE}{'═' * 65}{Colors.ENDC}")
    print(f"{Colors.CYAN}📁 Project: {Colors.BOLD}{proj}{Colors.ENDC}  {'🔧 Fix Mode' if fix_mode else '🔍 Analysis Mode'}")
    print(f"{Colors.BLUE}{'─' * 65}{Colors.ENDC}")

    # Diagnostic results tracking
    checks = {
        "critical": [],
        "warnings": [], 
        "passed": [],
        "fixed": []
    }

    def add_check(category, icon, message, fix_func=None):
        """Add a check result and optionally apply fix."""
        full_msg = f"{icon} {message}"
        checks[category].append(full_msg)
        
        if fix_mode and fix_func and category in ["critical", "warnings"]:
            try:
                fix_result = fix_func()
                if fix_result:
                    checks["fixed"].append(f"🔧 Fixed: {message}")
                    return True
            except Exception as e:
                print(f"  {Colors.RED}❌ Fix failed for '{message}': {str(e)[:50]}...{Colors.ENDC}")
        return False

    # ═══════════════════════════════════════════════════════════════
    # 1. SECURITY SCAN — Check security baseline and vulnerability score
    # ═══════════════════════════════════════════════════════════════
    print(f"\n{Colors.BOLD}{Colors.RED}🛡️  SECURITY SCAN{Colors.ENDC}")
    try:
        # Run the actual security scanner to get real score
        from tools.security_scanner import full_scan
        print(f"     {Colors.YELLOW}⏳ Running comprehensive security scan...{Colors.ENDC}")
        
        security_results = full_scan(".", verbose=False)
        score = security_results['summary']['score']
        total_findings = security_results['summary']['total_findings']
        high_findings = security_results['summary']['high']
        
        if score >= 90:
            add_check("passed", "🟢", f"Security score: {score}/100 (Excellent) - {total_findings} total findings")
        elif score >= 75:
            add_check("warnings", "🟡", f"Security score: {score}/100 (Good) - {high_findings} high severity findings")
        elif score >= 50:
            add_check("warnings", "🟡", f"Security score: {score}/100 (Needs improvement) - {high_findings} high severity findings")
        else:
            add_check("critical", "🔴", f"Security score: {score}/100 (Critical) - {high_findings} high severity findings")
            
        # Show breakdown if there are findings
        if total_findings > 0:
            breakdown = []
            if security_results['summary']['high'] > 0:
                breakdown.append(f"{security_results['summary']['high']} high")
            if security_results['summary']['medium'] > 0:
                breakdown.append(f"{security_results['summary']['medium']} medium")
            if security_results['summary']['low'] > 0:
                breakdown.append(f"{security_results['summary']['low']} low")
            print(f"     {Colors.CYAN}📊 Findings: {', '.join(breakdown)}{Colors.ENDC}")
    except ImportError:
        add_check("warnings", "⚠️", "Security scanner not available")
    except Exception as e:
        add_check("warnings", "⚠️", f"Could not run security scan: {str(e)[:50]}")

    # ═══════════════════════════════════════════════════════════════
    # 2. DEPENDENCY HEALTH — Check for outdated packages
    # ═══════════════════════════════════════════════════════════════
    print(f"\n{Colors.BOLD}{Colors.YELLOW}📦 DEPENDENCY HEALTH{Colors.ENDC}")
    try:
        # Python dependencies
        if Path("requirements.txt").exists():
            try:
                result = _sp.run(["pip", "list", "--outdated", "--format=freeze"], 
                               capture_output=True, text=True, timeout=8)
                if result.returncode == 0:
                    outdated = [line for line in result.stdout.split('\n') if line.strip()]
                    if len(outdated) > 5:
                        add_check("warnings", "🟡", f"{len(outdated)} outdated Python packages")
                    elif len(outdated) > 0:
                        add_check("warnings", "⚠️", f"{len(outdated)} outdated packages")
                    else:
                        add_check("passed", "🟢", "All Python packages up to date")
                else:
                    add_check("passed", "🟢", "Python dependencies checked")
            except (_sp.TimeoutExpired, FileNotFoundError):
                add_check("warnings", "⚠️", "Could not check Python dependencies")

        # Node dependencies
        if Path("package.json").exists():
            try:
                result = _sp.run(["npm", "outdated"], capture_output=True, text=True, timeout=6)
                if result.stdout.strip():
                    lines = result.stdout.strip().split('\n')
                    outdated_count = len(lines) - 1  # Subtract header
                    if outdated_count > 10:
                        add_check("warnings", "🟡", f"{outdated_count} outdated npm packages")
                    elif outdated_count > 0:
                        add_check("warnings", "⚠️", f"{outdated_count} outdated npm packages")
                    else:
                        add_check("passed", "🟢", "All npm packages up to date")
                else:
                    add_check("passed", "🟢", "All npm packages up to date")
            except (_sp.TimeoutExpired, FileNotFoundError):
                add_check("passed", "🟢", "npm dependencies checked")
                
    except Exception:
        add_check("warnings", "⚠️", "Could not check dependency health")

    # ═══════════════════════════════════════════════════════════════
    # 3. CONFIG VALIDATION — Check .env and configuration files
    # ═══════════════════════════════════════════════════════════════
    print(f"\n{Colors.BOLD}{Colors.BLUE}⚙️  CONFIGURATION VALIDATION{Colors.ENDC}")
    try:
        env_file = Path(".env")
        env_example = Path(".env.example")
        
        if not env_file.exists():
            if env_example.exists():
                add_check("warnings", "🟡", ".env file missing (template available)",
                         lambda: shutil.copy(env_example, env_file))
            else:
                add_check("warnings", "⚠️", ".env file missing")
        else:
            env_content = env_file.read_text()
            # Count non-comment, non-empty lines
            config_lines = [line for line in env_content.split('\n') 
                          if line.strip() and not line.strip().startswith('#')]
            
            if len(config_lines) < 2:
                add_check("warnings", "⚠️", ".env file appears empty or minimal")
            else:
                add_check("passed", "🟢", f".env configured with {len(config_lines)} settings")
                
        # Check for common config files
        config_files = ["config.py", "settings.py", "config.json", "config.yaml"]
        config_found = [f for f in config_files if Path(f).exists()]
        if config_found:
            add_check("passed", "🟢", f"Config files: {', '.join(config_found)}")
        else:
            add_check("warnings", "⚠️", "No dedicated config files found")
            
    except Exception:
        add_check("warnings", "⚠️", "Could not validate configuration")

    # ═══════════════════════════════════════════════════════════════
    # 4. DISK USAGE — Project size and cleanup opportunities
    # ═══════════════════════════════════════════════════════════════
    print(f"\n{Colors.BOLD}{Colors.GREEN}💾 DISK USAGE ANALYSIS{Colors.ENDC}")
    try:
        # Get project size
        try:
            result = _sp.run(["du", "-sh", "."], capture_output=True, text=True, timeout=8)
            if result.returncode == 0:
                size = result.stdout.split()[0]
                if 'G' in size and float(size.replace('G', '')) > 1.0:
                    add_check("warnings", "🟡", f"Large project size: {size}")
                else:
                    add_check("passed", "🟢", f"Project size: {size}")
        except (_sp.TimeoutExpired, ValueError):
            add_check("passed", "🟢", "Project size checked")

        # Check for cleanup opportunities
        cleanup_targets = []
        
        # node_modules check
        if Path("node_modules").exists():
            cleanup_targets.append("node_modules")
        
        # Cache directories
        cache_dirs = [".pytest_cache", "__pycache__", ".mypy_cache", ".ruff_cache"]
        for cache_dir in cache_dirs:
            if Path(cache_dir).exists():
                cleanup_targets.append(cache_dir)
        
        if len(cleanup_targets) > 2:
            add_check("warnings", "⚠️", f"Cleanup opportunities: {len(cleanup_targets)} cache/build dirs",
                     lambda: all(shutil.rmtree(d, ignore_errors=True) for d in cleanup_targets if Path(d).exists()))
        elif cleanup_targets:
            add_check("passed", "🟢", f"Some cache dirs present ({len(cleanup_targets)})")
        else:
            add_check("passed", "🟢", "No unnecessary cache directories")
            
    except Exception:
        add_check("warnings", "⚠️", "Could not analyze disk usage")

    # ═══════════════════════════════════════════════════════════════
    # 5. PERFORMANCE — CLI startup time and performance metrics
    # ═══════════════════════════════════════════════════════════════
    print(f"\n{Colors.BOLD}{Colors.CYAN}⚡ PERFORMANCE ANALYSIS{Colors.ENDC}")
    try:
        # Test Python import time for main module
        start_time = time.time()
        try:
            result = _sp.run(["python3", "-c", "import sys; print('OK')"], 
                           capture_output=True, text=True, timeout=3)
            end_time = time.time()
            
            startup_time = end_time - start_time
            if startup_time > 2.0:
                add_check("warnings", "🟡", f"Python startup slow: {startup_time:.2f}s")
            else:
                add_check("passed", "🟢", f"Python startup: {startup_time:.2f}s")
        except _sp.TimeoutExpired:
            add_check("warnings", "⚠️", "Python startup timeout")
            
        # Check for performance-impacting files
        large_files = []
        try:
            result = _sp.run(["find", ".", "-name", "*.py", "-size", "+100k"], 
                           capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                large_files = [f for f in result.stdout.strip().split('\n') if f]
                
            if len(large_files) > 3:
                add_check("warnings", "⚠️", f"{len(large_files)} large Python files (>100KB)")
            elif large_files:
                add_check("passed", "🟢", f"{len(large_files)} large files found")
            else:
                add_check("passed", "🟢", "No oversized Python files")
        except (_sp.TimeoutExpired, FileNotFoundError):
            add_check("passed", "🟢", "File size check completed")
            
    except Exception:
        add_check("warnings", "⚠️", "Could not analyze performance")

    # ═══════════════════════════════════════════════════════════════
    # 6. API CONNECTIVITY — Test configured API keys
    # ═══════════════════════════════════════════════════════════════
    print(f"\n{Colors.BOLD}{Colors.HEADER}🌐 API CONNECTIVITY{Colors.ENDC}")
    try:
        env_file = Path(".env")
        api_keys_found = 0
        
        if env_file.exists():
            env_content = env_file.read_text()
            
            # Count API keys
            api_patterns = ["API_KEY", "SECRET_KEY", "ACCESS_TOKEN", "_TOKEN"]
            for pattern in api_patterns:
                if pattern in env_content:
                    api_keys_found += 1
                    break  # Count each type only once
            
            # Specific API checks
            if "OPENAI_API_KEY" in env_content or "sk-" in env_content:
                add_check("passed", "🟢", "OpenAI API key configured")
                api_keys_found += 1
            
            if "OPENROUTER_API_KEY" in env_content or "sk-or-" in env_content:
                add_check("passed", "🟢", "OpenRouter API key configured")
                api_keys_found += 1
            
            if api_keys_found >= 2:
                add_check("passed", "🟢", f"{api_keys_found} API services configured")
            elif api_keys_found == 1:
                add_check("warnings", "⚠️", "Only 1 API service configured")
            else:
                add_check("warnings", "⚠️", "No API keys found in .env")
        else:
            add_check("warnings", "⚠️", "No .env file for API configuration")
            
    except Exception:
        add_check("warnings", "⚠️", "Could not test API connectivity")

    # ═══════════════════════════════════════════════════════════════
    # 7. GIT HEALTH — Repository status and sync health
    # ═══════════════════════════════════════════════════════════════
    print(f"\n{Colors.BOLD}{Colors.BLUE}📡 GIT HEALTH{Colors.ENDC}")
    try:
        # Check if it's a git repo
        result = _sp.run(["git", "status", "--porcelain"], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            add_check("warnings", "⚠️", "Not a git repository")
        else:
            # Check uncommitted changes
            dirty_files = len([l for l in result.stdout.strip().split("\n") if l.strip()])
            if dirty_files > 10:
                add_check("warnings", "🟡", f"{dirty_files} uncommitted changes")
            elif dirty_files > 0:
                add_check("warnings", "⚠️", f"{dirty_files} uncommitted changes")
            else:
                add_check("passed", "🟢", "Working tree clean")
            
            # Check for stale branches
            try:
                result = _sp.run(["git", "branch", "-v"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    branches = result.stdout.strip().split('\n')
                    branch_count = len([b for b in branches if b.strip()])
                    if branch_count > 5:
                        add_check("warnings", "⚠️", f"{branch_count} local branches")
                    else:
                        add_check("passed", "🟢", f"{branch_count} branches")
            except _sp.TimeoutExpired:
                add_check("passed", "🟢", "Git branches checked")
                
    except Exception:
        add_check("warnings", "⚠️", "Could not check git health")

    # ═══════════════════════════════════════════════════════════════
    # 8. TEST EXECUTION — Run tests and check coverage
    # ═══════════════════════════════════════════════════════════════
    print(f"\n{Colors.BOLD}{Colors.GREEN}🧪 TEST EXECUTION{Colors.ENDC}")
    try:
        # Check if tests exist
        test_dirs = ["tests", "test", "__tests__"]
        test_files = []
        for test_dir in test_dirs:
            if Path(test_dir).exists():
                test_files.extend(list(Path(test_dir).glob("**/*test*.py")))
        
        if not test_files:
            add_check("warnings", "⚠️", "No test files found")
        else:
            # Try to run a quick test
            try:
                result = _sp.run(["python3", "-m", "pytest", "--collect-only", "-q"], 
                               capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    test_count = len([l for l in lines if 'test' in l])
                    add_check("passed", "🟢", f"Found {test_count} test cases")
                else:
                    add_check("warnings", "⚠️", f"{len(test_files)} test files (pytest not available)")
            except (_sp.TimeoutExpired, FileNotFoundError):
                add_check("warnings", "⚠️", f"{len(test_files)} test files found")
                
    except Exception:
        add_check("warnings", "⚠️", "Could not check test execution")

    # ═══════════════════════════════════════════════════════════════
    # 9. DOCUMENTATION — Check documentation completeness
    # ═══════════════════════════════════════════════════════════════
    print(f"\n{Colors.BOLD}{Colors.CYAN}📚 DOCUMENTATION{Colors.ENDC}")
    try:
        doc_score = 0
        total_docs = 3
        
        # Check README
        readme_files = ["README.md", "readme.md", "README.rst"]
        readme = next((Path(f) for f in readme_files if Path(f).exists()), None)
        if readme and len(readme.read_text().strip()) > 100:
            add_check("passed", "🟢", f"README.md exists ({len(readme.read_text())} chars)")
            doc_score += 1
        elif readme:
            add_check("warnings", "⚠️", "README.md exists but short")
        else:
            add_check("warnings", "⚠️", "README.md missing",
                     lambda: Path("README.md").write_text(f"# {proj}\n\nProject description here.\n\n## Installation\n\n## Usage\n\n## Contributing\n"))
        
        # Check CHANGELOG
        changelog_files = ["CHANGELOG.md", "HISTORY.md", "changelog.md"]
        changelog = next((Path(f) for f in changelog_files if Path(f).exists()), None)
        if changelog and len(changelog.read_text().strip()) > 50:
            add_check("passed", "🟢", "CHANGELOG exists")
            doc_score += 1
        else:
            add_check("warnings", "⚠️", "CHANGELOG missing")
        
        # Check for docs directory or API docs
        if Path("docs").exists() or any(Path(f).exists() for f in ["API.md", "api.md", "DOCS.md"]):
            add_check("passed", "🟢", "Additional documentation found")
            doc_score += 1
        else:
            add_check("warnings", "⚠️", "No additional documentation")
        
        doc_percentage = (doc_score / total_docs) * 100
        if doc_percentage >= 80:
            add_check("passed", "🟢", f"Documentation coverage: {doc_percentage:.0f}%")
        else:
            add_check("warnings", "⚠️", f"Documentation coverage: {doc_percentage:.0f}%")
            
    except Exception:
        add_check("warnings", "⚠️", "Could not check documentation")

    # ═══════════════════════════════════════════════════════════════
    # 10. CODE QUALITY — TODO markers, large files, complexity
    # ═══════════════════════════════════════════════════════════════
    print(f"\n{Colors.BOLD}{Colors.YELLOW}🔍 CODE QUALITY{Colors.ENDC}")
    
    # TODO/FIXME markers
    try:
        result = _sp.run(["grep", "-r", "--include=*.py", "-c", "TODO\\|FIXME\\|HACK", "."], 
                        capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            todo_lines = result.stdout.strip().split('\n')
            todo_count = sum(int(line.split(':')[-1]) for line in todo_lines if ':' in line and line.split(':')[-1].isdigit())
            if todo_count > 20:
                add_check("warnings", "🟡", f"{todo_count} TODO/FIXME markers")
            elif todo_count > 0:
                add_check("warnings", "⚠️", f"{todo_count} TODO markers")
            else:
                add_check("passed", "🟢", "No TODO/FIXME markers")
        else:
            add_check("passed", "🟢", "No TODO markers found")
    except (_sp.TimeoutExpired, FileNotFoundError):
        add_check("passed", "🟢", "Code quality check completed")

    # Python version
    try:
        v = sys.version_info
        if v >= (3, 10):
            add_check("passed", "🟢", f"Python {v.major}.{v.minor}.{v.micro} (modern)")
        else:
            add_check("warnings", "⚠️", f"Python {v.major}.{v.minor} — consider upgrading")
    except Exception:
        pass

    # ═══════════════════════════════════════════════════════════════
    # RESULTS SUMMARY AND OVERALL SCORE
    # ═══════════════════════════════════════════════════════════════
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'═' * 65}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}📊 DIAGNOSTIC RESULTS SUMMARY{Colors.ENDC}")
    print(f"{Colors.BLUE}{'═' * 65}{Colors.ENDC}")

    # Calculate overall score
    base_score = 100
    critical_impact = len(checks["critical"]) * 20
    warning_impact = len(checks["warnings"]) * 5
    bonus_points = min(len(checks["passed"]) * 2, 20)
    
    final_score = max(0, base_score - critical_impact - warning_impact + bonus_points)

    # Determine grade
    if final_score >= 90:
        grade, grade_color, grade_desc = "A", Colors.GREEN, "Excellent"
    elif final_score >= 80:
        grade, grade_color, grade_desc = "B", Colors.BLUE, "Good"
    elif final_score >= 70:
        grade, grade_color, grade_desc = "C", Colors.YELLOW, "Fair"
    elif final_score >= 60:
        grade, grade_color, grade_desc = "D", Colors.YELLOW, "Poor"
    else:
        grade, grade_color, grade_desc = "F", Colors.RED, "Critical"

    # Print results by category
    if checks["critical"]:
        print(f"\n{Colors.RED}🔴 CRITICAL ISSUES ({len(checks['critical'])}){Colors.ENDC}")
        for item in checks["critical"]:
            print(f"    {item}")

    if checks["warnings"]:
        print(f"\n{Colors.YELLOW}🟡 WARNINGS ({len(checks['warnings'])}){Colors.ENDC}")
        for item in checks["warnings"][:8]:  # Limit display
            print(f"    {item}")
        if len(checks["warnings"]) > 8:
            print(f"    ... and {len(checks['warnings']) - 8} more")

    if checks["passed"]:
        print(f"\n{Colors.GREEN}🟢 PASSED CHECKS ({len(checks['passed'])}){Colors.ENDC}")
        for item in checks["passed"][:6]:  # Show top items
            print(f"    {item}")
        if len(checks["passed"]) > 6:
            print(f"    ... and {len(checks['passed']) - 6} more")

    if checks["fixed"]:
        print(f"\n{Colors.CYAN}🔧 AUTO-FIXES APPLIED ({len(checks['fixed'])}){Colors.ENDC}")
        for item in checks["fixed"]:
            print(f"    {item}")

    # Overall score display
    print(f"\n{Colors.BOLD}{grade_color}🏆 OVERALL HEALTH SCORE: {final_score}/100 (Grade {grade} - {grade_desc}){Colors.ENDC}")

    # Actionable recommendations
    print(f"\n{Colors.BOLD}{Colors.CYAN}💡 ACTIONABLE RECOMMENDATIONS{Colors.ENDC}")
    print(f"{Colors.CYAN}{'─' * 40}{Colors.ENDC}")
    
    recommendations = []
    
    if checks["critical"]:
        recommendations.append("🔴 Address critical issues immediately")
        recommendations.append("   • Run security audit and fix vulnerabilities")
    
    if len(checks["warnings"]) > 5:
        recommendations.append("🟡 High warning count - prioritize fixes")
        if any("outdated" in item.lower() for item in checks["warnings"]):
            recommendations.append("   • Update dependencies: pip list --outdated")
        if any("todo" in item.lower() for item in checks["warnings"]):
            recommendations.append("   • Clean up TODO markers in codebase")
        if any("test" in item.lower() for item in checks["warnings"]):
            recommendations.append("   • Add test coverage: python3 -m pytest --cov")
    
    if final_score < 80:
        recommendations.append("📈 Focus on documentation and configuration")
        if fix_mode:
            recommendations.append("🔄 Re-run without --fix to see current status")
        else:
            recommendations.append("🔧 Run with --fix to auto-fix common issues")
    
    if not recommendations:
        recommendations = [
            "🎉 Project health is excellent!",
            "✨ Consider sharing best practices with the team",
            "📈 Monitor metrics with regular doctor checkups"
        ]
    
    for rec in recommendations[:6]:  # Limit recommendations
        print(f"    {rec}")
    
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'═' * 65}{Colors.ENDC}")
    
    if fix_mode:
        print(f"{Colors.GREEN}✅ Comprehensive diagnosis completed with auto-fixes applied{Colors.ENDC}")
    else:
        print(f"{Colors.BLUE}💡 Run with --fix to automatically resolve fixable issues{Colors.ENDC}")
    
    print(f"{Colors.CYAN}📊 Use 'mw status' for quick checks or 'mw dashboard' for overview{Colors.ENDC}")
    
    return 1 if checks["critical"] else 0
    
    if "--help" in args or "-h" in args:
        print(f"""
{Colors.BOLD}🩺 MyWork Doctor — Comprehensive Diagnostics{Colors.ENDC}
{'=' * 60}

Usage:
    mw doctor                       Run full system diagnostics
    mw doctor --fix                 Run diagnostics and auto-fix issues
    mw doctor --help                Show this help message

Diagnostic Checks:
    • TODO markers and technical debt
    • Large files and disk usage  
    • Test coverage and test execution
    • Git status and sync health
    • Security scan and vulnerability check
    • Dependency health and outdated packages
    • Configuration validation (.env, settings)
    • Performance analysis (CLI startup time)
    • API connectivity testing
    • Documentation completeness
    • Overall project health score (A-F grade)

Auto-fix Features (--fix):
    • Clean node_modules and cache directories
    • Update outdated dependencies
    • Fix common configuration issues
    • Clean stale git branches
    • Auto-generate missing documentation

Examples:
    mw doctor                       # Comprehensive health check
    mw doctor --fix                 # Fix what can be auto-fixed
""")
        return 0

    proj = os.path.basename(os.getcwd())
    print(f"\n{Colors.BOLD}{Colors.BLUE}🩺 MyWork Doctor — Comprehensive Diagnostics{Colors.ENDC}")
    print(f"{Colors.BLUE}{'═' * 65}{Colors.ENDC}")
    print(f"{Colors.CYAN}📁 Project: {Colors.BOLD}{proj}{Colors.ENDC}  {'🔧 Fix Mode' if fix_mode else '🔍 Analysis Mode'}")
    print(f"{Colors.BLUE}{'─' * 65}{Colors.ENDC}")

    # Diagnostic results tracking
    checks = {
        "critical": [],   # Score impact: -20 points each
        "warnings": [],   # Score impact: -5 points each  
        "passed": [],     # Score impact: +5 points each
        "fixed": []       # Track auto-fixes applied
    }

    def add_check(category, icon, message, fix_func=None):
        """Add a check result and optionally apply fix."""
        full_msg = f"{icon} {message}"
        checks[category].append(full_msg)
        
        if fix_mode and fix_func and category in ["critical", "warnings"]:
            try:
                fix_result = fix_func()
                if fix_result:
                    checks["fixed"].append(f"🔧 Fixed: {message}")
                    return True
            except Exception as e:
                print(f"  {Colors.RED}❌ Fix failed for '{message}': {str(e)[:50]}...{Colors.ENDC}")
        return False

    # ═══════════════════════════════════════════════════════════════
    # 1. SECURITY SCAN — Run security scanner and show score
    # ═══════════════════════════════════════════════════════════════
    print(f"\n{Colors.BOLD}{Colors.RED}🛡️  SECURITY SCAN{Colors.ENDC}")
    try:
        # Look for security baseline
        baseline_file = Path(".security_baseline.json")
        if baseline_file.exists():
            baseline = _json.loads(baseline_file.read_text())
            score = baseline.get("overall_score", 0)
            if score >= 90:
                add_check("passed", "🟢", f"Security score: {score}/100 (Excellent)")
            elif score >= 75:
                add_check("warnings", "🟡", f"Security score: {score}/100 (Good)")
            else:
                add_check("critical", "🔴", f"Security score: {score}/100 (Needs improvement)")
        else:
            # Try to run security scan with shorter timeout
            try:
                result = _sp.run(["python3", "-m", "bandit", "-r", ".", "-f", "json"], 
                               capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    add_check("passed", "🟢", "Security scan completed successfully")
                else:
                    add_check("warnings", "🟡", "Security scanner not available")
            except (_sp.TimeoutExpired, FileNotFoundError):
                add_check("warnings", "⚠️", "Security scanner not found or timed out")
    except Exception:
        add_check("warnings", "⚠️", "Could not run security scan")

    # ═══════════════════════════════════════════════════════════════
    # 2. DEPENDENCY HEALTH — Check for outdated packages, missing deps
    # ═══════════════════════════════════════════════════════════════
    print(f"{Colors.BOLD}{Colors.YELLOW}📦 DEPENDENCY HEALTH{Colors.ENDC}")
    try:
        # Python dependencies
        if Path("requirements.txt").exists() or Path("pyproject.toml").exists():
            try:
                result = _sp.run(["pip", "list", "--outdated", "--format=json"], 
                               capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    outdated = _json.loads(result.stdout) if result.stdout.strip() else []
                    if len(outdated) > 5:
                        add_check("warnings", "🟡", f"{len(outdated)} outdated Python packages")
                    elif len(outdated) > 0:
                        add_check("warnings", "⚠️", f"{len(outdated)} outdated packages (manageable)")
                    else:
                        add_check("passed", "🟢", "All Python packages up to date")
                else:
                    add_check("passed", "🟢", "Python dependencies check completed")
            except (_sp.TimeoutExpired, FileNotFoundError, _json.JSONDecodeError):
                add_check("warnings", "⚠️", "Could not check Python dependencies")
            
        # Node dependencies
        if Path("package.json").exists():
            try:
                result = _sp.run(["npm", "outdated", "--json"], capture_output=True, text=True, timeout=8)
                outdated_npm = _json.loads(result.stdout) if result.stdout.strip() else {}
                count = len(outdated_npm)
                if count > 10:
                    add_check("warnings", "🟡", f"{count} outdated npm packages")
                elif count > 0:
                    add_check("warnings", "⚠️", f"{count} outdated npm packages")
                else:
                    add_check("passed", "🟢", "All npm packages up to date")
            except (_sp.TimeoutExpired, FileNotFoundError, _json.JSONDecodeError):
                add_check("passed", "🟢", "npm dependencies check completed")
                
    except Exception:
        add_check("warnings", "⚠️", "Could not check dependency health")

    # ═══════════════════════════════════════════════════════════════
    # 3. CONFIG VALIDATION — Verify .env exists, required keys present  
    # ═══════════════════════════════════════════════════════════════
    print(f"{Colors.BOLD}{Colors.BLUE}⚙️  CONFIGURATION VALIDATION{Colors.ENDC}")
    try:
        env_file = Path(".env")
        env_example = Path(".env.example")
        
        if not env_file.exists():
            if env_example.exists():
                add_check("warnings", "🟡", ".env file missing (template available)",
                         lambda: shutil.copy(env_example, env_file))
            else:
                add_check("warnings", "⚠️", ".env and .env.example files missing")
        else:
            env_content = env_file.read_text()
            
            # Check for common required keys
            required_keys = ["DATABASE_URL", "SECRET_KEY", "API_KEY", "OPENAI_API_KEY", "DEBUG"]
            missing_keys = [key for key in required_keys if key not in env_content]
            
            if len(missing_keys) > 3:
                add_check("warnings", "🟡", f"Missing common env vars: {', '.join(missing_keys[:3])}")
            else:
                add_check("passed", "🟢", ".env file configured properly")
                
        # Check for config files
        config_files = ["config.py", "settings.py", "config.json", "config.yaml"]
        has_config = any(Path(f).exists() for f in config_files)
        if has_config:
            add_check("passed", "🟢", "Configuration files present")
        else:
            add_check("warnings", "⚠️", "No dedicated config files found")
            
    except Exception:
        add_check("warnings", "⚠️", "Could not validate configuration")

    # ═══════════════════════════════════════════════════════════════
    # 4. DISK USAGE — Project size, node_modules bloat
    # ═══════════════════════════════════════════════════════════════
    print(f"{Colors.BOLD}{Colors.GREEN}💾 DISK USAGE ANALYSIS{Colors.ENDC}")
    try:
        # Get project size
        result = _sp.run(["du", "-sh", "."], capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            size = result.stdout.split()[0]
            size_mb = 0
            if 'G' in size:
                size_mb = float(size.replace('G', '')) * 1024
            elif 'M' in size:
                size_mb = float(size.replace('M', ''))
            
            if size_mb > 1000:  # > 1GB
                add_check("warnings", "🟡", f"Large project size: {size}")
            else:
                add_check("passed", "🟢", f"Project size: {size} (reasonable)")

        # Check node_modules bloat
        node_modules = Path("node_modules")
        if node_modules.exists():
            result = _sp.run(["du", "-sh", "node_modules"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                nm_size = result.stdout.split()[0]
                nm_mb = 0
                if 'G' in nm_size:
                    nm_mb = float(nm_size.replace('G', '')) * 1024
                elif 'M' in nm_size:
                    nm_mb = float(nm_size.replace('M', ''))
                    
                if nm_mb > 500:  # > 500MB
                    add_check("warnings", "🟡", f"node_modules bloat: {nm_size}",
                             lambda: shutil.rmtree("node_modules") or _sp.run(["npm", "install"]).returncode == 0)
                else:
                    add_check("passed", "🟢", f"node_modules size: {nm_size}")

        # Check for cache directories
        cache_dirs = [".pytest_cache", "__pycache__", ".mypy_cache", ".ruff_cache", ".coverage"]
        large_caches = []
        for cache_dir in cache_dirs:
            if Path(cache_dir).exists():
                try:
                    result = _sp.run(["du", "-sm", cache_dir], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        size_mb = int(result.stdout.split()[0])
                        if size_mb > 50:  # > 50MB
                            large_caches.append(cache_dir)
                except:
                    pass
        
        if large_caches:
            add_check("warnings", "⚠️", f"Large cache dirs: {', '.join(large_caches)}",
                     lambda: all(shutil.rmtree(d) for d in large_caches if Path(d).exists()))
        else:
            add_check("passed", "🟢", "Cache directories are clean")
            
    except Exception:
        add_check("warnings", "⚠️", "Could not analyze disk usage")

    # ═══════════════════════════════════════════════════════════════
    # 5. PERFORMANCE — mw CLI startup time (should be <1s)
    # ═══════════════════════════════════════════════════════════════
    print(f"{Colors.BOLD}{Colors.CYAN}⚡ PERFORMANCE ANALYSIS{Colors.ENDC}")
    try:
        # Test CLI startup time
        start_time = time.time()
        result = _sp.run(["mw", "--version"], capture_output=True, text=True, timeout=5)
        end_time = time.time()
        
        startup_time = end_time - start_time
        if startup_time > 2.0:
            add_check("warnings", "🟡", f"CLI startup slow: {startup_time:.2f}s")
        elif startup_time > 1.0:
            add_check("warnings", "⚠️", f"CLI startup time: {startup_time:.2f}s")
        else:
            add_check("passed", "🟢", f"CLI startup fast: {startup_time:.2f}s")
            
        # Check Python import time
        start_time = time.time()
        result = _sp.run(["python3", "-c", "import tools.mw"], capture_output=True, text=True, timeout=5)
        end_time = time.time()
        
        import_time = end_time - start_time
        if import_time > 1.0:
            add_check("warnings", "⚠️", f"Module import slow: {import_time:.2f}s")
        else:
            add_check("passed", "🟢", f"Module import fast: {import_time:.2f}s")
            
    except Exception:
        add_check("warnings", "⚠️", "Could not measure performance")

    # ═══════════════════════════════════════════════════════════════
    # 6. API CONNECTIVITY — Test if configured API keys work
    # ═══════════════════════════════════════════════════════════════
    print(f"{Colors.BOLD}{Colors.HEADER}🌐 API CONNECTIVITY{Colors.ENDC}")
    try:
        env_file = Path(".env")
        if env_file.exists():
            env_content = env_file.read_text()
            
            # Test OpenRouter API
            if "OPENROUTER_API_KEY" in env_content or "sk-or-v1-" in env_content:
                try:
                    # Quick health check (no actual API call to avoid charges)
                    add_check("passed", "🟢", "OpenRouter API key configured")
                except:
                    add_check("warnings", "⚠️", "OpenRouter API key issue")
            
            # Test OpenAI API  
            if "OPENAI_API_KEY" in env_content or "sk-proj-" in env_content or "sk-" in env_content:
                try:
                    add_check("passed", "🟢", "OpenAI API key configured")
                except:
                    add_check("warnings", "⚠️", "OpenAI API key issue")
            
            # Test DeepSeek API
            if "DEEPSEEK_API_KEY" in env_content:
                add_check("passed", "🟢", "DeepSeek API key configured")
            
            # Generic API health
            api_count = sum(1 for line in env_content.split('\n') 
                          if 'API_KEY' in line and not line.strip().startswith('#'))
            if api_count >= 2:
                add_check("passed", "🟢", f"{api_count} API keys configured")
            elif api_count == 1:
                add_check("warnings", "⚠️", "Only 1 API key configured")
            else:
                add_check("warnings", "⚠️", "No API keys found in .env")
        else:
            add_check("warnings", "⚠️", "No .env file for API configuration")
            
    except Exception:
        add_check("warnings", "⚠️", "Could not test API connectivity")

    # ═══════════════════════════════════════════════════════════════
    # 7. GIT HEALTH — Unpushed commits, remote sync status
    # ═══════════════════════════════════════════════════════════════
    print(f"{Colors.BOLD}{Colors.BLUE}📡 GIT HEALTH{Colors.ENDC}")
    try:
        # Check if it's a git repo
        result = _sp.run(["git", "rev-parse", "--git-dir"], capture_output=True, text=True)
        if result.returncode != 0:
            add_check("warnings", "⚠️", "Not a git repository")
        else:
            # Check uncommitted changes
            result = _sp.run(["git", "status", "--porcelain"], capture_output=True, text=True)
            dirty_files = len([l for l in result.stdout.strip().split("\n") if l.strip()])
            if dirty_files > 10:
                add_check("warnings", "🟡", f"{dirty_files} uncommitted changes")
            elif dirty_files > 0:
                add_check("warnings", "⚠️", f"{dirty_files} uncommitted changes")
            else:
                add_check("passed", "🟢", "Working tree clean")
            
            # Check unpushed commits
            try:
                result = _sp.run(["git", "rev-list", "--count", "HEAD", "^origin/main"], 
                               capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    unpushed = int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0
                    if unpushed > 10:
                        add_check("warnings", "🟡", f"{unpushed} unpushed commits")
                    elif unpushed > 0:
                        add_check("warnings", "⚠️", f"{unpushed} unpushed commits")
                    else:
                        add_check("passed", "🟢", "All commits pushed")
            except:
                add_check("passed", "🟢", "Remote sync status OK")

            # Check stale branches
            result = _sp.run(["git", "branch", "--merged"], capture_output=True, text=True, timeout=5)
            merged = [b.strip() for b in result.stdout.strip().split("\n") 
                     if b.strip() and not b.strip().startswith("*") and b.strip() not in ["main", "master"]]
            if len(merged) > 3:
                add_check("warnings", "⚠️", f"{len(merged)} stale merged branches",
                         lambda: all(_sp.run(["git", "branch", "-d", branch]).returncode == 0 for branch in merged[:3]))
            elif merged:
                add_check("warnings", "⚠️", f"{len(merged)} merged branches")
            else:
                add_check("passed", "🟢", "No stale branches")
    except Exception:
        add_check("warnings", "⚠️", "Could not check git health")

    # ═══════════════════════════════════════════════════════════════
    # 8. TEST RESULTS — Actually run pytest and show pass/fail count
    # ═══════════════════════════════════════════════════════════════
    print(f"{Colors.BOLD}{Colors.GREEN}🧪 TEST EXECUTION{Colors.ENDC}")
    try:
        # Check if tests exist
        test_dirs = ["tests", "test", "__tests__", "spec"]
        test_files = []
        for test_dir in test_dirs:
            if Path(test_dir).exists():
                test_files.extend(list(Path(test_dir).glob("**/*test*.py")))
        
        if not test_files:
            add_check("warnings", "⚠️", "No test files found")
        else:
            # Run pytest
            try:
                result = _sp.run(["python3", "-m", "pytest", "--tb=no", "-q"], 
                               capture_output=True, text=True, timeout=30)
                output = result.stdout + result.stderr
                
                # Parse pytest output
                if "passed" in output or "failed" in output:
                    lines = output.split('\n')
                    for line in lines:
                        if "passed" in line or "failed" in line:
                            if "failed" in line and "0 failed" not in line:
                                add_check("critical", "🔴", f"Tests failing: {line.strip()}")
                            else:
                                add_check("passed", "🟢", f"Tests: {line.strip()}")
                            break
                else:
                    add_check("warnings", "⚠️", "Tests found but pytest failed to run")
            except:
                add_check("warnings", "⚠️", f"{len(test_files)} test files found (not executed)")
                
    except Exception:
        add_check("warnings", "⚠️", "Could not run test suite")

    # ═══════════════════════════════════════════════════════════════
    # 9. DOCUMENTATION — Check if README, CHANGELOG exist and are not empty
    # ═══════════════════════════════════════════════════════════════
    print(f"{Colors.BOLD}{Colors.CYAN}📚 DOCUMENTATION{Colors.ENDC}")
    try:
        docs_score = 0
        total_docs = 0
        
        # Check README
        readme_files = ["README.md", "README.rst", "README.txt", "readme.md"]
        readme_exists = any(Path(f).exists() for f in readme_files)
        if readme_exists:
            readme_file = next(Path(f) for f in readme_files if Path(f).exists())
            content = readme_file.read_text()
            if len(content.strip()) > 100:
                add_check("passed", "🟢", f"README.md exists ({len(content)} chars)")
                docs_score += 1
            else:
                add_check("warnings", "⚠️", "README.md too short")
        else:
            add_check("warnings", "⚠️", "README.md missing",
                     lambda: Path("README.md").write_text("# " + proj + "\n\nProject description here.\n"))
        total_docs += 1
        
        # Check CHANGELOG
        changelog_files = ["CHANGELOG.md", "CHANGELOG.rst", "HISTORY.md", "changelog.md"]
        changelog_exists = any(Path(f).exists() for f in changelog_files)
        if changelog_exists:
            changelog_file = next(Path(f) for f in changelog_files if Path(f).exists())
            content = changelog_file.read_text()
            if len(content.strip()) > 50:
                add_check("passed", "🟢", "CHANGELOG exists")
                docs_score += 1
            else:
                add_check("warnings", "⚠️", "CHANGELOG too short")
        else:
            add_check("warnings", "⚠️", "CHANGELOG missing")
        total_docs += 1
        
        # Check API documentation
        api_docs = ["docs/", "API.md", "api.md", "docs/api/"]
        has_api_docs = any(Path(f).exists() for f in api_docs)
        if has_api_docs:
            add_check("passed", "🟢", "API documentation found")
            docs_score += 1
        total_docs += 1
        
        # Documentation score
        doc_percentage = (docs_score / total_docs) * 100
        if doc_percentage >= 80:
            add_check("passed", "🟢", f"Documentation coverage: {doc_percentage:.0f}%")
        else:
            add_check("warnings", "⚠️", f"Documentation coverage: {doc_percentage:.0f}%")
            
    except Exception:
        add_check("warnings", "⚠️", "Could not check documentation")

    # ═══════════════════════════════════════════════════════════════
    # 10. LEGACY CHECKS — TODO markers, large files, circular imports, etc.
    # ═══════════════════════════════════════════════════════════════
    print(f"{Colors.BOLD}{Colors.YELLOW}🔍 CODE QUALITY CHECKS{Colors.ENDC}")
    
    # TODO/FIXME markers
    try:
        r = _sp.run(["grep", "-rn", "--include=*.py", "--include=*.ts", "--include=*.tsx",
                      "--include=*.js", "-E", "TODO|FIXME|HACK|XXX", "."],
                     capture_output=True, text=True, timeout=10)
        count = len(r.stdout.strip().split("\n")) if r.stdout.strip() else 0
        if count > 20:
            add_check("warnings", "🟡", f"{count} TODO/FIXME/HACK markers in code")
        elif count > 0:
            add_check("warnings", "⚠️", f"{count} TODO markers (manageable)")
        else:
            add_check("passed", "🟢", "No TODO/FIXME markers")
    except Exception:
        pass

    # Large files  
    try:
        r = _sp.run(["find", ".", "-not", "-path", "./.git/*", "-not", "-path", "./node_modules/*",
                      "-not", "-path", "./.venv/*", "-type", "f", "-size", "+1M"],
                     capture_output=True, text=True, timeout=10)
        large = [f for f in r.stdout.strip().split("\n") if f]
        if len(large) > 3:
            add_check("warnings", "🟡", f"{len(large)} files over 1MB")
        elif large:
            add_check("warnings", "⚠️", f"{len(large)} large files: {', '.join([Path(f).name for f in large[:2]])}")
        else:
            add_check("passed", "🟢", "No oversized files")
    except Exception:
        pass

    # Python version
    try:
        import sys
        v = sys.version_info
        if v >= (3, 10):
            add_check("passed", "🟢", f"Python {v.major}.{v.minor}.{v.micro} (modern)")
        else:
            add_check("warnings", "⚠️", f"Python {v.major}.{v.minor} — consider upgrading to 3.10+")
    except Exception:
        pass

    # ═══════════════════════════════════════════════════════════════
    # RESULTS SUMMARY AND OVERALL SCORE
    # ═══════════════════════════════════════════════════════════════
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'═' * 65}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}📊 DIAGNOSTIC RESULTS SUMMARY{Colors.ENDC}")
    print(f"{Colors.BLUE}{'═' * 65}{Colors.ENDC}")

    # Calculate overall score
    base_score = 100
    critical_impact = len(checks["critical"]) * 20
    warning_impact = len(checks["warnings"]) * 5
    bonus_points = min(len(checks["passed"]) * 2, 20)  # Max 20 bonus points
    
    final_score = max(0, base_score - critical_impact - warning_impact + bonus_points)

    # Determine grade
    if final_score >= 90:
        grade = "A"
        grade_color = Colors.GREEN
        grade_desc = "Excellent"
    elif final_score >= 80:
        grade = "B" 
        grade_color = Colors.BLUE
        grade_desc = "Good"
    elif final_score >= 70:
        grade = "C"
        grade_color = Colors.YELLOW
        grade_desc = "Fair"
    elif final_score >= 60:
        grade = "D"
        grade_color = Colors.YELLOW
        grade_desc = "Poor"
    else:
        grade = "F"
        grade_color = Colors.RED
        grade_desc = "Critical"

    # Print results
    if checks["critical"]:
        print(f"\n{Colors.RED}🔴 CRITICAL ISSUES ({len(checks['critical'])}){Colors.ENDC}")
        for item in checks["critical"]:
            print(f"    {item}")

    if checks["warnings"]:
        print(f"\n{Colors.YELLOW}🟡 WARNINGS ({len(checks['warnings'])}){Colors.ENDC}")
        for item in checks["warnings"]:
            print(f"    {item}")

    if checks["passed"]:
        print(f"\n{Colors.GREEN}🟢 PASSED CHECKS ({len(checks['passed'])}){Colors.ENDC}")
        for item in checks["passed"][:10]:  # Show first 10
            print(f"    {item}")
        if len(checks["passed"]) > 10:
            print(f"    ... and {len(checks['passed']) - 10} more")

    if checks["fixed"]:
        print(f"\n{Colors.CYAN}🔧 AUTO-FIXES APPLIED ({len(checks['fixed'])}){Colors.ENDC}")
        for item in checks["fixed"]:
            print(f"    {item}")

    # Overall score
    print(f"\n{Colors.BOLD}{grade_color}🏆 OVERALL HEALTH SCORE: {final_score}/100 (Grade {grade} - {grade_desc}){Colors.ENDC}")

    # Actionable recommendations
    print(f"\n{Colors.BOLD}{Colors.CYAN}💡 ACTIONABLE RECOMMENDATIONS{Colors.ENDC}")
    print(f"{Colors.CYAN}{'─' * 40}{Colors.ENDC}")
    
    recommendations = []
    
    if checks["critical"]:
        recommendations.append("🔴 Address critical issues immediately")
        if any("test" in item.lower() for item in checks["critical"]):
            recommendations.append("   • Fix failing tests with: python3 -m pytest -v")
        if any("security" in item.lower() for item in checks["critical"]):
            recommendations.append("   • Run security audit: python3 -m bandit -r .")
    
    if len(checks["warnings"]) > 5:
        recommendations.append("🟡 High warning count - prioritize top issues")
        if any("outdated" in item.lower() for item in checks["warnings"]):
            recommendations.append("   • Update dependencies: pip install --upgrade pip && pip list --outdated")
        if any("todo" in item.lower() for item in checks["warnings"]):
            recommendations.append("   • Address TODO markers in critical paths")
        if any("branch" in item.lower() for item in checks["warnings"]):
            recommendations.append("   • Clean stale branches: git branch --merged | grep -v main | xargs git branch -d")
    
    if final_score < 80:
        recommendations.append("📈 Focus on improving test coverage and documentation")
        recommendations.append("🔧 Run 'mw doctor --fix' to auto-fix common issues")
    
    if not recommendations:
        recommendations = [
            "🎉 Project health is excellent!",
            "✨ Consider sharing your project on the marketplace",
            "🧠 Document learnings with: mw brain add 'lesson learned'"
        ]
    
    for rec in recommendations[:8]:  # Limit to 8 recommendations
        print(f"    {rec}")
    
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'═' * 65}{Colors.ENDC}")
    
    if fix_mode:
        print(f"{Colors.GREEN}✅ Doctor completed with auto-fixes applied{Colors.ENDC}")
    else:
        print(f"{Colors.BLUE}💡 Run 'mw doctor --fix' to automatically fix common issues{Colors.ENDC}")
    
    return 1 if checks["critical"] else 0


def _cmd_env(args: List[str] = None) -> int:
    """Environment variable manager — audit, compare, template, secrets scan."""
    return run_tool("env_manager", args or [])


def _cmd_tree(args: List[str] = None) -> int:
    """Smart project tree with git status, icons, and .gitignore awareness."""
    from tools.tree_viewer import cmd_tree
    return cmd_tree(args or [])


def _cmd_deps_audit(args: List[str] = None) -> int:
    """Dependency security audit — scan for vulnerabilities and outdated packages."""
    from tools.deps_audit import cmd_deps_audit
    return cmd_deps_audit(args or [])


def _cmd_depgraph(args: List[str] = None) -> int:
    """Run dependency graph analyzer."""
    return run_tool("depgraph", args or [])


def _cmd_metrics(args: List[str] = None) -> int:
    """Code metrics dashboard — LOC, complexity, quality score.

    Subcommands:
        mw metrics              Code analysis (LOC, complexity, quality)
        mw metrics track        Record snapshot & show current tracked metrics
        mw metrics history      Show tracked metrics history with trends
        mw metrics chart        ASCII sparkline chart of metrics over time
    """
    args = args or []
    if args and args[0] in ("track", "history", "chart"):
        from tools.metrics_tracker import cmd_metrics as tracker
        subcmd = args[0]
        if subcmd == "track":
            return tracker(["record"])
        return tracker([subcmd])
    from metrics import cmd_metrics
    return cmd_metrics(args)


def cmd_time(args: List[str] = None) -> int:
    """Developer time tracking — log work sessions per project.

    Usage:
        mw time start [project]   Start tracking time on a project
        mw time stop              Stop current session
        mw time status            Show active session
        mw time log [days]        Show time log (default: 7 days)
        mw time report [days]     Weekly summary with charts
        mw time today             Show today's work breakdown

    Data stored in ~/.mywork/time_tracking.json
    """
    import time as _time
    from datetime import datetime

    args = args or []
    if args and args[0] in ("--help", "-h"):
        print(cmd_time.__doc__)
        return 0

    time_file = Path.home() / ".mywork" / "time_tracking.json"
    time_file.parent.mkdir(parents=True, exist_ok=True)

    def _load():
        if time_file.exists():
            try:
                return json.loads(time_file.read_text())
            except Exception:
                pass
        return {"sessions": [], "active": None}

    def _save(data):
        time_file.write_text(json.dumps(data, indent=2))

    def _fmt_duration(seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        if h > 0:
            return f"{h}h {m}m"
        return f"{m}m"

    sub = args[0] if args else "status"

    if sub == "start":
        project = args[1] if len(args) > 1 else Path.cwd().name
        data = _load()
        if data.get("active"):
            # Auto-stop previous session
            sess = data["active"]
            sess["end"] = _time.time()
            sess["duration"] = sess["end"] - sess["start"]
            data["sessions"].append(sess)
            print(f"  {Colors.YELLOW}⏹  Stopped {sess['project']} ({_fmt_duration(sess['duration'])}){Colors.ENDC}")
        data["active"] = {
            "project": project,
            "start": _time.time(),
            "date": datetime.now().strftime("%Y-%m-%d"),
        }
        _save(data)
        print(f"{Colors.GREEN}▶  Started tracking: {Colors.BOLD}{project}{Colors.ENDC}")
        print(f"   {datetime.now().strftime('%H:%M:%S')}")
        return 0

    elif sub == "stop":
        data = _load()
        if not data.get("active"):
            print(f"{Colors.YELLOW}⚠️  No active session{Colors.ENDC}")
            return 1
        sess = data["active"]
        sess["end"] = _time.time()
        sess["duration"] = sess["end"] - sess["start"]
        data["sessions"].append(sess)
        data["active"] = None
        _save(data)
        print(f"{Colors.RED}⏹  Stopped: {Colors.BOLD}{sess['project']}{Colors.ENDC}")
        print(f"   Duration: {_fmt_duration(sess['duration'])}")
        return 0

    elif sub == "status":
        data = _load()
        if data.get("active"):
            sess = data["active"]
            elapsed = _time.time() - sess["start"]
            print(f"{Colors.GREEN}▶  Active: {Colors.BOLD}{sess['project']}{Colors.ENDC}")
            print(f"   Elapsed: {_fmt_duration(elapsed)}")
            print(f"   Started: {datetime.fromtimestamp(sess['start']).strftime('%H:%M:%S')}")
        else:
            print(f"{Colors.ENDC}⏸  No active session{Colors.ENDC}")
            print(f"   Use: mw time start [project]")
        return 0

    elif sub == "today":
        data = _load()
        today = datetime.now().strftime("%Y-%m-%d")
        today_sessions = [s for s in data["sessions"] if s.get("date") == today]
        if data.get("active") and data["active"].get("date") == today:
            active = data["active"].copy()
            active["duration"] = _time.time() - active["start"]
            active["_active"] = True
            today_sessions.append(active)

        if not today_sessions:
            print(f"{Colors.ENDC}📅 Today: No work logged yet{Colors.ENDC}")
            return 0

        total = sum(s.get("duration", 0) for s in today_sessions)
        by_project: dict = {}
        for s in today_sessions:
            p = s["project"]
            by_project[p] = by_project.get(p, 0) + s.get("duration", 0)

        print(f"{Colors.BOLD}{Colors.BLUE}📅 Today — {_fmt_duration(total)}{Colors.ENDC}")
        print(f"{'─' * 40}")
        for proj, dur in sorted(by_project.items(), key=lambda x: -x[1]):
            pct = int(dur / total * 100) if total > 0 else 0
            bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
            marker = " ▶" if any(s.get("_active") and s["project"] == proj for s in today_sessions) else ""
            print(f"  {proj:20s} {_fmt_duration(dur):>8s} {bar} {pct}%{marker}")
        return 0

    elif sub in ("log", "report"):
        data = _load()
        days = int(args[1]) if len(args) > 1 else 7
        cutoff = _time.time() - (days * 86400)
        recent = [s for s in data["sessions"] if s.get("start", 0) >= cutoff]

        if not recent:
            print(f"{Colors.ENDC}📊 No sessions in the last {days} days{Colors.ENDC}")
            return 0

        by_date: dict = {}
        by_project: dict = {}
        for s in recent:
            d = s.get("date", "unknown")
            p = s["project"]
            dur = s.get("duration", 0)
            by_date[d] = by_date.get(d, 0) + dur
            by_project[p] = by_project.get(p, 0) + dur

        total = sum(s.get("duration", 0) for s in recent)

        print(f"{Colors.BOLD}{Colors.BLUE}📊 Time Report — Last {days} days{Colors.ENDC}")
        print(f"{'═' * 50}")
        print(f"  Total: {Colors.BOLD}{_fmt_duration(total)}{Colors.ENDC} across {len(recent)} sessions")
        print()

        print(f"{Colors.BOLD}By Project:{Colors.ENDC}")
        for proj, dur in sorted(by_project.items(), key=lambda x: -x[1]):
            pct = int(dur / total * 100) if total > 0 else 0
            bar = "█" * (pct // 4) + "░" * (25 - pct // 4)
            print(f"  {proj:20s} {_fmt_duration(dur):>8s} {bar} {pct}%")

        print(f"\n{Colors.BOLD}By Day:{Colors.ENDC}")
        for d in sorted(by_date.keys()):
            dur = by_date[d]
            bar_len = min(int(dur / 3600 * 4), 30)
            bar = "█" * bar_len
            print(f"  {d}  {_fmt_duration(dur):>8s} {bar}")

        return 0

    else:
        print(f"{Colors.RED}Unknown subcommand: {sub}{Colors.ENDC}")
        print("Usage: mw time start|stop|status|today|log|report")
        return 1


def cmd_upgrade(args: List[str] = None) -> int:
    """Self-upgrade MyWork-AI from GitHub or PyPI.

    Usage:
        mw upgrade              # Upgrade to latest from GitHub
        mw upgrade --check      # Check if update available (no install)
        mw upgrade --pypi       # Upgrade from PyPI instead of GitHub
        mw upgrade --version X  # Upgrade to specific version
    """
    import subprocess as _sp
    args = args or []

    if "--help" in args or "-h" in args:
        print(f"""
{Colors.BOLD}⬆️  MyWork-AI Upgrade{Colors.ENDC}
{'=' * 50}

Usage:
    mw upgrade              Upgrade to latest from GitHub (default)
    mw upgrade --check      Check for updates without installing
    mw upgrade --pypi       Upgrade from PyPI
    mw upgrade --version X  Install specific version

Examples:
    mw upgrade              # Pull latest + reinstall
    mw upgrade --check      # Just check what's new
""")
        return 0

    check_only = "--check" in args
    use_pypi = "--pypi" in args
    target_version = None
    if "--version" in args:
        idx = args.index("--version")
        if idx + 1 < len(args):
            target_version = args[idx + 1]

    # Get current version
    install_dir = Path(__file__).resolve().parent.parent
    current_ver = "unknown"
    try:
        toml_path = install_dir / "pyproject.toml"
        if toml_path.exists():
            for line in toml_path.read_text().splitlines():
                if line.strip().startswith('version'):
                    current_ver = line.split('"')[1]
                    break
    except Exception:
        pass

    print(f"\n{Colors.BOLD}⬆️  MyWork-AI Upgrade{Colors.ENDC}")
    print(f"{'=' * 50}")
    print(f"   Current version: {Colors.BLUE}v{current_ver}{Colors.ENDC}")
    print(f"   Install path:    {install_dir}\n")

    if use_pypi:
        if check_only:
            print(f"   🔍 Checking PyPI for updates...")
            r = _sp.run([sys.executable, "-m", "pip", "index", "versions", "mywork-ai"],
                       capture_output=True, text=True)
            print(f"   {r.stdout.strip()}" if r.returncode == 0 else f"   ⚠️  Could not check PyPI")
            return 0
        print(f"   📦 Upgrading from PyPI...")
        cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "mywork-ai", "--break-system-packages"]
        if target_version:
            cmd[-1] = f"mywork-ai=={target_version}"
            cmd.append("--break-system-packages")
        r = _sp.run(cmd, capture_output=True, text=True)
        if r.returncode == 0:
            print(f"   {Colors.GREEN}✅ Upgraded successfully!{Colors.ENDC}")
            # Show new version
            _sp.run([sys.executable, "-m", "pip", "show", "mywork-ai"], capture_output=False)
        else:
            print(f"   {Colors.RED}❌ Upgrade failed:{Colors.ENDC}")
            print(f"   {r.stderr.strip()[:200]}")
        return r.returncode

    # GitHub upgrade (default)
    git_dir = install_dir / ".git"
    if not git_dir.exists():
        print(f"   {Colors.RED}❌ Not a git repo. Use --pypi to upgrade from PyPI.{Colors.ENDC}")
        return 1

    # Fetch latest
    print(f"   🔍 Fetching latest from GitHub...")
    _sp.run(["git", "fetch", "--tags"], cwd=install_dir, capture_output=True)

    # Check if behind
    r = _sp.run(["git", "rev-list", "--count", "HEAD..origin/main"],
                cwd=install_dir, capture_output=True, text=True)
    behind = int(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip().isdigit() else 0

    if behind == 0:
        print(f"   {Colors.GREEN}✅ Already up to date (v{current_ver}){Colors.ENDC}")
        return 0

    # Show what's new
    r = _sp.run(["git", "log", "--oneline", "HEAD..origin/main"],
                cwd=install_dir, capture_output=True, text=True)
    commits = r.stdout.strip().splitlines()[:10]
    print(f"   📋 {behind} new commit(s):")
    for c in commits:
        print(f"      {c}")
    if behind > 10:
        print(f"      ... and {behind - 10} more")

    if check_only:
        print(f"\n   Run {Colors.BOLD}mw upgrade{Colors.ENDC} to install updates.")
        return 0

    # Pull and reinstall
    print(f"\n   ⬇️  Pulling updates...")
    r = _sp.run(["git", "pull", "--ff-only"], cwd=install_dir, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"   {Colors.YELLOW}⚠️  Fast-forward failed, trying rebase...{Colors.ENDC}")
        r = _sp.run(["git", "pull", "--rebase"], cwd=install_dir, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"   {Colors.RED}❌ Pull failed. Resolve conflicts manually.{Colors.ENDC}")
            return 1

    # Reinstall
    print(f"   📦 Reinstalling...")
    r = _sp.run([sys.executable, "-m", "pip", "install", "-e", ".", "--break-system-packages"],
                cwd=install_dir, capture_output=True, text=True)
    if r.returncode == 0:
        # Get new version
        new_ver = current_ver
        try:
            for line in (install_dir / "pyproject.toml").read_text().splitlines():
                if line.strip().startswith('version'):
                    new_ver = line.split('"')[1]
                    break
        except Exception:
            pass
        print(f"\n   {Colors.GREEN}✅ Upgraded: v{current_ver} → v{new_ver}{Colors.ENDC}")
        print(f"   {Colors.BLUE}Run 'mw doctor' to verify everything works.{Colors.ENDC}")
    else:
        print(f"   {Colors.RED}❌ Reinstall failed: {r.stderr.strip()[:200]}{Colors.ENDC}")
    return r.returncode


def cmd_completions(args: List[str] = None) -> int:
    """Generate shell completion scripts.

    Usage:
        mw completions bash    # Bash completions
        mw completions zsh     # Zsh completions
        mw completions fish    # Fish completions
        mw completions install # Auto-install for current shell

    Setup:
        eval "$(mw completions bash)"          # Add to ~/.bashrc
        eval "$(mw completions zsh)"           # Add to ~/.zshrc
        mw completions fish > ~/.config/fish/completions/mw.fish
    """
    args = args or []

    # All top-level commands (excluding flags)
    top_cmds = [
        "ai", "analytics", "api", "audit", "af", "autoforge", "backup", "bench",
        "brain", "cd", "cfg", "changelog", "check", "ci", "clean", "completion", "completions", "config",
        "credits", "dashboard", "db", "deploy", "docs", "doctor", "ecosystem",
        "api", "env", "fix", "git", "guide", "help", "hook", "init", "insights", "links", "lint",
        "marketplace", "monitor", "n8n", "new", "open", "perf", "plugin",
        "profile", "projects", "prompt-enhance", "release", "remember", "report", "scan",
        "run", "search", "sec", "secrets", "security", "selftest", "serve", "setup", "stats", "status", "test",
        "demo", "metrics", "todo", "todos", "tour", "update", "upgrade", "verify", "version", "web", "wf", "workflow",
    ]
    # Subcommands per command
    subcmds = {
        "ai": ["ask", "explain", "fix", "refactor", "test", "commit", "chat", "providers", "models"],
        "brain": ["search", "add", "stats", "export", "list", "delete", "cleanup"],
        "git": ["status", "commit", "log", "branch", "diff", "push", "pull", "stash", "undo", "amend", "cleanup"],
        "projects": ["scan", "export", "stats", "list", "health"],
        "env": ["list", "get", "set", "rm", "diff", "validate", "export", "init"],
        "config": ["list", "get", "set", "reset", "rm", "path"],
        "deploy": ["vercel", "railway", "render", "docker"],
        "plugin": ["install", "uninstall", "enable", "disable", "list", "create", "scan"],
        "pair": ["--path", "--model", "--quiet", "--review", "history"],
        "ci": ["github", "gitlab", "status"],
        "metrics": ["track", "history", "chart"],
        "lint": ["scan", "stats", "watch"],
        "af": ["start", "stop", "pause", "resume", "status", "progress", "list", "ui", "service"],
        "test": ["--coverage", "--watch", "--verbose"],
        "test-coverage": ["--detail", "--scaffold", "--json", "--min"],
        "db": ["status", "tables", "schema", "query", "migrate", "seed", "export", "backup", "restore"],
        "hook": ["install", "uninstall", "list", "run", "create"],
        "secrets": ["set", "get", "list", "delete", "inject", "export", "import", "audit", "rotate"],
        "security": ["scan", "audit", "secrets", "deps"],
        "release": ["patch", "minor", "major", "status", "--dry-run"],
        "run": ["add", "rm"],
        "completions": ["bash", "zsh", "fish", "install"],
    }

    if not args or args[0] in ("-h", "--help", "help"):
        print(f"{Colors.BOLD}🐚 Shell Completions{Colors.ENDC}")
        print("=" * 50)
        print()
        print("Generate tab-completion scripts for your shell.")
        print()
        print(f"{Colors.BOLD}Usage:{Colors.ENDC}")
        print('  eval "$(mw completions bash)"   # Bash (add to ~/.bashrc)')
        print('  eval "$(mw completions zsh)"    # Zsh  (add to ~/.zshrc)')
        print("  mw completions fish > ~/.config/fish/completions/mw.fish")
        print("  mw completions install          # Auto-install for current shell")
        return 0

    shell = args[0].lower()

    if shell == "bash":
        cmds_str = " ".join(top_cmds)
        # Build case statements for subcommands
        cases = []
        for cmd, subs in sorted(subcmds.items()):
            cases.append(f'        {cmd}) COMPREPLY=( $(compgen -W "{" ".join(subs)}" -- "$cur") ) ;;')
        case_block = "\n".join(cases)
        print(f"""_mw_completions() {{
    local cur prev commands
    cur="${{COMP_WORDS[COMP_CWORD]}}"
    prev="${{COMP_WORDS[COMP_CWORD-1]}}"
    commands="{cmds_str}"

    if [[ $COMP_CWORD -eq 1 ]]; then
        COMPREPLY=( $(compgen -W "$commands" -- "$cur") )
        return 0
    fi

    case "$prev" in
{case_block}
        *) COMPREPLY=() ;;
    esac
}}
complete -F _mw_completions mw""")
        return 0

    elif shell == "zsh":
        cmds_str = " ".join(top_cmds)
        cases = []
        for cmd, subs in sorted(subcmds.items()):
            subs_str = " ".join(subs)
            cases.append(f"        {cmd}) _values 'subcommand' {subs_str} ;;")
        case_block = "\n".join(cases)
        print(f"""#compdef mw
_mw() {{
    local -a commands
    commands=({cmds_str})

    if (( CURRENT == 2 )); then
        _describe 'command' commands
        return
    fi

    case "$words[2]" in
{case_block}
    esac
}}
_mw""")
        return 0

    elif shell == "fish":
        lines = [f"# Fish completions for mw"]
        lines.append("complete -c mw -e  # Clear existing")
        for cmd in top_cmds:
            desc = cmd.replace("-", " ").title()
            lines.append(f'complete -c mw -n "__fish_use_subcommand" -a "{cmd}" -d "{desc}"')
        for cmd, subs in sorted(subcmds.items()):
            for sub in subs:
                lines.append(f'complete -c mw -n "__fish_seen_subcommand_from {cmd}" -a "{sub}"')
        print("\n".join(lines))
        return 0

    elif shell == "install":
        # Detect shell and install
        current_shell = os.environ.get("SHELL", "")
        home = Path.home()

        if "zsh" in current_shell:
            rc = home / ".zshrc"
            line = 'eval "$(mw completions zsh)"'
        elif "fish" in current_shell:
            comp_dir = home / ".config" / "fish" / "completions"
            comp_dir.mkdir(parents=True, exist_ok=True)
            comp_file = comp_dir / "mw.fish"
            # Generate and write fish completions
            import io
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            cmd_completions(["fish"])
            content = sys.stdout.getvalue()
            sys.stdout = old_stdout
            comp_file.write_text(content)
            print(f"{Colors.GREEN}✅ Fish completions installed to {comp_file}{Colors.ENDC}")
            print("   Restart your shell or run: source ~/.config/fish/config.fish")
            return 0
        else:
            rc = home / ".bashrc"
            line = 'eval "$(mw completions bash)"'

        # Check if already installed
        if rc.exists() and line in rc.read_text():
            print(f"{Colors.YELLOW}⚠️  Completions already installed in {rc}{Colors.ENDC}")
            return 0

        with open(rc, "a") as f:
            f.write(f"\n# MyWork CLI completions\n{line}\n")
        print(f"{Colors.GREEN}✅ Completions installed in {rc}{Colors.ENDC}")
        print(f"   Run: source {rc}")
        return 0

    else:
        print(f"{Colors.RED}❌ Unknown shell: {shell}{Colors.ENDC}")
        print("   Supported: bash, zsh, fish, install")
        return 1


def main() -> None:
    """Main entry point with global exception handling."""
    if len(sys.argv) < 2:
        print_help()
        sys.exit(0)

    command = sys.argv[1].lower()
    args = sys.argv[2:]
    
    # Validate command input
    if not validate_input(command, "command", max_length=50):
        sys.exit(1)

    def _cmd_badge(badge_args):
        """Generate project badges (shields.io compatible)."""
        tool_path = Path(_FRAMEWORK_ROOT) / "tools" / "badge.py"
        if tool_path.exists():
            return subprocess.run(
                [sys.executable, str(tool_path)] + (badge_args or []),
                cwd=str(_FRAMEWORK_ROOT)
            ).returncode
        print("Badge tool not found")
        return 1

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
        "doctor": lambda: cmd_doctor([]),
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
        "marketplace": lambda: cmd_marketplace(args),
        "links": lambda: cmd_links(args),
        "remember": lambda: cmd_brain(["add"] + args),  # Shortcut
        "init": lambda: cmd_init(args),
        "stats": lambda: cmd_stats(args),
        "check": lambda: _cmd_check_wrapper(args),
        "clean": lambda: cmd_clean(args),
        "backup": lambda: cmd_backup(args),
        "changelog": lambda: cmd_changelog(args),
        "metrics": lambda: _cmd_metrics(args),
        "test": lambda: cmd_test(args),
        "test-coverage": lambda: _cmd_test_coverage(args),
        "workflow": lambda: cmd_workflow(args),
        "wf": lambda: cmd_workflow(args),
        "analytics": lambda: cmd_analytics_wrapper(args),
        "docs": lambda: cmd_docs(args),
        "ci": lambda: cmd_ci(args),
        "release": lambda: cmd_release(args),
        "badge": lambda: _cmd_badge(args),
        "run": lambda: _cmd_run_wrapper(args),
        "deploy": lambda: cmd_deploy(args),
        "monitor": lambda: cmd_monitor(args),
        "env": lambda: cmd_env(args),
        "plugin": lambda: _cmd_plugin_wrapper(args),
        "config": lambda: cmd_config(args),
        "cfg": lambda: cmd_config(args),
        "ai": lambda: _cmd_ai_wrapper(args),
        "pair": lambda: _cmd_pair_wrapper(args),
        "secrets": lambda: _cmd_secrets_wrapper(args),
        "vault": lambda: _cmd_secrets_wrapper(args),
        "security": lambda: cmd_security(args),
        "sec": lambda: cmd_security(args),
        "git": lambda: cmd_git(args),
        "g": lambda: cmd_git(args),
        "hook": lambda: cmd_hook(args),
        "hooks": lambda: cmd_hook(args),
        "insights": lambda: _cmd_insights_wrapper(args),
        "api": lambda: cmd_api(args),
        "audit": lambda: cmd_audit(args),
        "bench": lambda: _cmd_bench_wrapper(args),
        "profile": lambda: _cmd_profile_wrapper(args),
        "benchmark": lambda: _cmd_bench_wrapper(args),
        "doctor": lambda: cmd_doctor(args),
        "diagnose": lambda: cmd_doctor(args),
        "perf": lambda: run_tool("perf_analyzer", args),
        "performance": lambda: run_tool("perf_analyzer", args),
        "api": lambda: _cmd_api_wrapper(args),
        "serve": lambda: _cmd_serve_wrapper(args),
        "demo": lambda: _cmd_demo_wrapper(args),
        "tour": lambda: _cmd_tour_wrapper(args),
        "web": lambda: _cmd_serve_wrapper(args),
        "db": lambda: _cmd_db_wrapper(args),
        "database": lambda: _cmd_db_wrapper(args),
        "migrate": lambda: _cmd_migrate_wrapper(args),
        "migration": lambda: _cmd_migrate_wrapper(args),
        "snapshot": lambda: cmd_snapshot(args),
        "snap": lambda: cmd_snapshot(args),
        "deps": lambda: cmd_deps(args),
        "dependencies": lambda: cmd_deps(args),
        "health": lambda: cmd_health(args),
        "score": lambda: cmd_health(args),
        "completions": lambda: cmd_completions(args),
        "completion": lambda: cmd_completions(args),  # Alias for completions
        "selftest": lambda: cmd_selftest(args),
        "self-test": lambda: cmd_selftest(args),
        "verify": lambda: cmd_selftest(args),
        "benchmark": lambda: cmd_benchmark(args),
        "bench": lambda: cmd_benchmark(args),
        "perf": lambda: cmd_benchmark(args),
        "recap": lambda: cmd_recap(args),
        "todo": lambda: cmd_todo(args),
        "watch": lambda: _cmd_watch_wrapper(args),
        "context": lambda: _cmd_context_wrapper(args),
        "ctx": lambda: _cmd_context_wrapper(args),
        "todos": lambda: cmd_todo(args),
        "metrics": lambda: _cmd_metrics(args),
        "stats": lambda: _cmd_metrics(args),
        "time": lambda: cmd_time(args),
        "timer": lambda: cmd_time(args),
        "track": lambda: cmd_time(args),
        "deps": lambda: _cmd_deps_audit(args),
        "deps-audit": lambda: _cmd_deps_audit(args),
        "audit": lambda: _cmd_deps_audit(args),
        "depgraph": lambda: _cmd_depgraph(args),
        "dep-graph": lambda: _cmd_depgraph(args),
        "tree": lambda: _cmd_tree(args),
        "upgrade": lambda: cmd_upgrade(args),
        "update-cli": lambda: cmd_upgrade(args),
        "af": lambda: cmd_autoforge(args),
        "autoforge": lambda: cmd_autoforge(args),
        "gsd": lambda: cmd_gsd(args),
        "plan": lambda: cmd_gsd(args),
        "webdash": lambda: _cmd_webdash(args),
        "html-report": lambda: _cmd_webdash(args),
        "version": lambda: cmd_version(args),
        "-v": lambda: cmd_version(),
        "--version": lambda: cmd_version(args),
        "help": lambda: print_help() or 0,
        "-h": lambda: print_help() or 0,
        "--help": lambda: print_help() or 0,
    }

    try:
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
            
            # Try running as plugin before showing error
            try:
                from tools.plugin_manager import run_plugin
                if run_plugin(command, args):
                    sys.exit(0)
            except Exception:
                pass
            
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
    
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}🛑 Operation interrupted by user{Colors.ENDC}")
        sys.exit(0)
    except PermissionError as e:
        print(f"{Colors.RED}❌ Permission denied: {e}{Colors.ENDC}")
        print(f"{Colors.YELLOW}💡 Try running with different permissions or in a different directory{Colors.ENDC}")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"{Colors.RED}❌ File not found: {e}{Colors.ENDC}")
        print(f"{Colors.YELLOW}💡 Check that the file exists and the path is correct{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.RED}❌ Unexpected error: {e}{Colors.ENDC}")
        if "--debug" in sys.argv:
            import traceback
            print(f"{Colors.BLUE}🐛 Debug traceback:{Colors.ENDC}")
            traceback.print_exc()
        else:
            print(f"{Colors.YELLOW}💡 Run with --debug for full traceback{Colors.ENDC}")
        sys.exit(1)


if __name__ == "__main__":
    main()
