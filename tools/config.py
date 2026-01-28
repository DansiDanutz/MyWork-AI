#!/usr/bin/env python3
"""
MyWork Framework Configuration
==============================
Shared configuration module for all MyWork tools.
Handles dynamic path detection and environment variables.
"""

import os
from pathlib import Path
from typing import Optional


def get_mywork_root() -> Path:
    """
    Detect MyWork root directory.

    Priority:
    1. MYWORK_ROOT environment variable
    2. Parent of this script's directory (tools/ -> MyWork/)
    3. Default to ~/MyWork

    Returns:
        Path: The MyWork root directory
    """
    # Check environment variable first
    if env_root := os.environ.get("MYWORK_ROOT"):
        return Path(env_root).resolve()

    # Try to detect from script location
    script_dir = Path(__file__).resolve().parent
    if script_dir.name == "tools":
        potential_root = script_dir.parent
        # Verify it's actually MyWork root by checking for key files
        if (potential_root / "CLAUDE.md").exists() or (potential_root / ".planning").exists():
            return potential_root

    # Default fallback
    default_path = Path.home() / "MyWork"
    if default_path.exists():
        return default_path

    # Last resort: return the potential root even if not verified
    return script_dir.parent if script_dir.name == "tools" else Path.home() / "MyWork"


def get_autocoder_root() -> Path:
    """
    Get Autocoder installation directory.

    Priority:
    1. AUTOCODER_ROOT environment variable
    2. MYWORK_ROOT/../GamesAI/autocoder
    3. ~/GamesAI/autocoder

    Returns:
        Path: The Autocoder root directory
    """
    if env_root := os.environ.get("AUTOCODER_ROOT"):
        return Path(env_root).resolve()

    # Try relative to MyWork
    mywork = get_mywork_root()
    potential = mywork.parent / "GamesAI" / "autocoder"
    if potential.exists():
        return potential

    # Default fallback
    return Path.home() / "GamesAI" / "autocoder"


# === Core Paths ===
MYWORK_ROOT = get_mywork_root()
TOOLS_DIR = MYWORK_ROOT / "tools"
PROJECTS_DIR = MYWORK_ROOT / "projects"
WORKFLOWS_DIR = MYWORK_ROOT / "workflows"
PLANNING_DIR = MYWORK_ROOT / ".planning"
TMP_DIR = MYWORK_ROOT / ".tmp"

# === Data Files ===
MODULE_REGISTRY_JSON = PLANNING_DIR / "module_registry.json"
MODULE_REGISTRY_MD = PLANNING_DIR / "MODULE_REGISTRY.md"
PROJECT_REGISTRY_JSON = PLANNING_DIR / "project_registry.json"
PROJECT_REGISTRY_MD = PLANNING_DIR / "PROJECT_REGISTRY.md"
BRAIN_DATA_JSON = PLANNING_DIR / "brain_data.json"
BRAIN_MD = PLANNING_DIR / "BRAIN.md"

# === External Tools ===
AUTOCODER_ROOT = get_autocoder_root()
AUTOCODER_SERVER = os.environ.get("AUTOCODER_SERVER", "http://127.0.0.1:8888")

# === Environment ===
ENV_FILE = MYWORK_ROOT / ".env"


def ensure_directories():
    """Ensure all required directories exist."""
    for dir_path in [PROJECTS_DIR, PLANNING_DIR, TMP_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)


def get_project_path(project_name: str) -> Path:
    """Get path to a specific project."""
    return PROJECTS_DIR / project_name


def list_projects() -> list[Path]:
    """List all projects in the projects directory."""
    if not PROJECTS_DIR.exists():
        return []
    return [p for p in PROJECTS_DIR.iterdir() if p.is_dir() and not p.name.startswith((".", "_"))]


# === Color Codes for Terminal ===
class Colors:
    """ANSI color codes for terminal output."""

    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def color(text: str, color_code: str) -> str:
    """Apply color to text for terminal output."""
    return f"{color_code}{text}{Colors.ENDC}"


def print_success(msg: str):
    """Print success message in green."""
    print(f"{Colors.GREEN}✅ {msg}{Colors.ENDC}")


def print_error(msg: str):
    """Print error message in red."""
    print(f"{Colors.RED}❌ {msg}{Colors.ENDC}")


def print_warning(msg: str):
    """Print warning message in yellow."""
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.ENDC}")


def print_info(msg: str):
    """Print info message in blue."""
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.ENDC}")


def print_header(msg: str):
    """Print header message in bold."""
    print(f"\n{Colors.BOLD}{msg}{Colors.ENDC}")


if __name__ == "__main__":
    # Print configuration for debugging
    print(f"MYWORK_ROOT: {MYWORK_ROOT}")
    print(f"TOOLS_DIR: {TOOLS_DIR}")
    print(f"PROJECTS_DIR: {PROJECTS_DIR}")
    print(f"AUTOCODER_ROOT: {AUTOCODER_ROOT}")
    print(f"AUTOCODER_SERVER: {AUTOCODER_SERVER}")
    print(f"\nProjects: {[p.name for p in list_projects()]}")
