#!/usr/bin/env python3
"""
mw tree — Smart project tree visualizer.

Shows project structure with:
- Git status indicators (M/A/D/?)
- File sizes (human-readable)
- .gitignore awareness
- Depth limiting
- File type filtering

Usage:
    mw tree                     # Current directory, depth 3
    mw tree --depth 5           # Deeper view
    mw tree --all               # Include hidden & gitignored files
    mw tree --dirs              # Directories only
    mw tree --filter .py        # Only show .py files
    mw tree --size              # Show file sizes
    mw tree /path/to/project    # Specific path
    mw tree --json              # JSON output
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# ANSI colors
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"

# File type icons
ICONS = {
    ".py": "🐍", ".js": "📜", ".ts": "📘", ".jsx": "⚛️", ".tsx": "⚛️",
    ".json": "📋", ".yaml": "📋", ".yml": "📋", ".toml": "📋",
    ".md": "📝", ".txt": "📄", ".rst": "📄",
    ".html": "🌐", ".css": "🎨", ".scss": "🎨",
    ".sh": "🔧", ".bash": "🔧",
    ".go": "🔵", ".rs": "🦀", ".rb": "💎", ".java": "☕",
    ".sql": "🗃️", ".db": "🗃️",
    ".png": "🖼️", ".jpg": "🖼️", ".svg": "🖼️", ".gif": "🖼️",
    ".lock": "🔒", ".env": "🔐",
    ".test.py": "🧪", ".spec.js": "🧪", ".test.js": "🧪",
    ".dockerfile": "🐳",
}

# Always skip these directories
ALWAYS_SKIP = {
    "__pycache__", ".git", "node_modules", ".tox", ".mypy_cache",
    ".pytest_cache", ".ruff_cache", "dist", "build", "*.egg-info",
    ".eggs", ".venv", "venv", "env", ".env",
}


def human_size(size: int) -> str:
    """Convert bytes to human-readable size."""
    for unit in ["B", "K", "M", "G"]:
        if size < 1024:
            if unit == "B":
                return f"{size}{unit}"
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}T"


def get_git_status(root: Path) -> Dict[str, str]:
    """Get git status for all files."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", "-uall"],
            capture_output=True, text=True, cwd=root, timeout=5,
        )
        if result.returncode != 0:
            return {}
        status = {}
        for line in result.stdout.strip().split("\n"):
            if len(line) >= 4:
                st = line[:2].strip()
                path = line[3:]
                status[path] = st
        return status
    except Exception:
        return {}


def get_gitignore_patterns(root: Path) -> Set[str]:
    """Get list of gitignored files."""
    try:
        result = subprocess.run(
            ["git", "ls-files", "--others", "--ignored", "--exclude-standard", "--directory"],
            capture_output=True, text=True, cwd=root, timeout=5,
        )
        if result.returncode != 0:
            return set()
        return {p.rstrip("/") for p in result.stdout.strip().split("\n") if p}
    except Exception:
        return set()


def get_icon(name: str, is_dir: bool) -> str:
    """Get icon for file/directory."""
    if is_dir:
        return "📁"
    lower = name.lower()
    if lower == "dockerfile":
        return "🐳"
    if lower in ("makefile", "justfile"):
        return "🔧"
    if lower in ("readme.md", "readme"):
        return "📖"
    if lower == "license":
        return "⚖️"
    # Check compound extensions first
    for ext, icon in ICONS.items():
        if lower.endswith(ext):
            return icon
    return "📄"


def git_status_color(status: str) -> str:
    """Color code for git status."""
    if status in ("M", "MM", "AM"):
        return YELLOW
    if status in ("A", "??"):
        return GREEN
    if status == "D":
        return RED
    return ""


def build_tree(
    root: Path,
    max_depth: int = 3,
    show_all: bool = False,
    dirs_only: bool = False,
    filter_ext: Optional[str] = None,
    show_size: bool = False,
    as_json: bool = False,
) -> Tuple[List[str], dict]:
    """Build tree output lines and stats."""
    git_status = get_git_status(root)
    gitignored = get_gitignore_patterns(root) if not show_all else set()
    
    lines = []
    stats = {"dirs": 0, "files": 0, "total_size": 0}
    
    def _should_skip(name: str, rel: str) -> bool:
        if not show_all and name.startswith("."):
            return True
        if name in ALWAYS_SKIP:
            return True
        for pattern in ALWAYS_SKIP:
            if "*" in pattern and name.endswith(pattern.replace("*", "")):
                return True
        if not show_all and rel in gitignored:
            return True
        return False
    
    def _walk(path: Path, prefix: str, depth: int, rel_prefix: str):
        if depth > max_depth:
            return
        
        try:
            entries = sorted(path.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower()))
        except PermissionError:
            return
        
        # Filter
        visible = []
        for entry in entries:
            rel = os.path.join(rel_prefix, entry.name) if rel_prefix else entry.name
            if _should_skip(entry.name, rel):
                continue
            if dirs_only and not entry.is_dir():
                continue
            if filter_ext and not entry.is_dir() and not entry.name.endswith(filter_ext):
                continue
            visible.append((entry, rel))
        
        for i, (entry, rel) in enumerate(visible):
            is_last = i == len(visible) - 1
            connector = "└── " if is_last else "├── "
            child_prefix = prefix + ("    " if is_last else "│   ")
            
            is_dir = entry.is_dir()
            icon = get_icon(entry.name, is_dir)
            name = entry.name
            
            # Git status
            gs = git_status.get(rel, "")
            gs_color = git_status_color(gs)
            gs_label = f" {gs_color}[{gs}]{RESET}" if gs else ""
            
            # Size
            size_label = ""
            if show_size and not is_dir:
                try:
                    sz = entry.stat().st_size
                    stats["total_size"] += sz
                    size_label = f" {DIM}({human_size(sz)}){RESET}"
                except OSError:
                    pass
            
            if is_dir:
                stats["dirs"] += 1
                lines.append(f"{prefix}{connector}{icon} {BOLD}{BLUE}{name}/{RESET}{gs_label}")
                _walk(entry, child_prefix, depth + 1, rel)
            else:
                stats["files"] += 1
                lines.append(f"{prefix}{connector}{icon} {name}{gs_label}{size_label}")
    
    _walk(root, "", 1, "")
    return lines, stats


def cmd_tree(args: List[str] = None) -> int:
    """Execute mw tree command."""
    args = args or []
    
    if "--help" in args or "-h" in args:
        print(__doc__)
        return 0
    
    # Parse args
    max_depth = 3
    show_all = False
    dirs_only = False
    filter_ext = None
    show_size = False
    as_json = False
    target = "."
    
    i = 0
    while i < len(args):
        a = args[i]
        if a in ("--depth", "-d") and i + 1 < len(args):
            max_depth = int(args[i + 1])
            i += 2
        elif a == "--all":
            show_all = True
            i += 1
        elif a == "--dirs":
            dirs_only = True
            i += 1
        elif a in ("--filter", "-f") and i + 1 < len(args):
            filter_ext = args[i + 1]
            if not filter_ext.startswith("."):
                filter_ext = "." + filter_ext
            i += 2
        elif a == "--size":
            show_size = True
            i += 1
        elif a == "--json":
            as_json = True
            i += 1
        elif not a.startswith("-"):
            target = a
            i += 1
        else:
            i += 1
    
    root = Path(target).resolve()
    if not root.is_dir():
        print(f"❌ Not a directory: {root}")
        return 1
    
    lines, stats = build_tree(root, max_depth, show_all, dirs_only, filter_ext, show_size, as_json)
    
    if as_json:
        print(json.dumps({
            "root": str(root),
            "dirs": stats["dirs"],
            "files": stats["files"],
            "total_size": stats["total_size"],
        }))
        return 0
    
    # Header
    print(f"\n{BOLD}📂 {root.name}/{RESET}")
    for line in lines:
        print(line)
    
    # Summary
    size_info = f", {human_size(stats['total_size'])}" if show_size else ""
    print(f"\n{DIM}{stats['dirs']} directories, {stats['files']} files{size_info}{RESET}")
    
    return 0


if __name__ == "__main__":
    sys.exit(cmd_tree(sys.argv[1:]))
