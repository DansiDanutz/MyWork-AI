#!/usr/bin/env python3
"""
mw context — Smart Context Builder for AI Coding Assistants
============================================================
Gathers relevant project context (structure, key files, git history,
dependencies) and formats it into a prompt-ready block for AI tools
like Claude, ChatGPT, Cursor, Aider, etc.

Usage:
    mw context                      # Auto-detect project, build context
    mw context --files src/main.py  # Include specific files
    mw context --depth 3            # Tree depth (default: 3)
    mw context --git                # Include recent git changes
    mw context --deps               # Include dependency info
    mw context --full               # Everything (git + deps + all key files)
    mw context --copy               # Copy to clipboard
    mw context --output ctx.md      # Save to file
    mw context --max-tokens 8000    # Limit output size (default: 12000)
    mw context --focus "auth"       # Focus on files matching pattern
"""
import os
import sys
import subprocess
import json
import argparse
from pathlib import Path
from typing import List, Optional, Dict, Tuple


# Key file patterns to auto-include
KEY_FILES = [
    "README.md", "CLAUDE.md", "AGENTS.md",
    "pyproject.toml", "setup.py", "setup.cfg",
    "package.json", "Cargo.toml", "go.mod",
    "Makefile", "Dockerfile", "docker-compose.yml",
    ".env.example", "requirements.txt",
    "tsconfig.json", "vite.config.ts", "next.config.js",
]

# Directories to skip in tree
SKIP_DIRS = {
    "node_modules", ".git", "__pycache__", ".pytest_cache",
    "dist", "build", ".next", ".vercel", "venv", ".venv",
    "env", ".tox", ".mypy_cache", ".ruff_cache", "target",
    ".eggs", "*.egg-info", "coverage", ".coverage",
}

# File extensions to include when reading
CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".rs", ".go",
    ".java", ".rb", ".php", ".c", ".cpp", ".h", ".hpp",
    ".sh", ".bash", ".zsh", ".sql", ".graphql",
    ".yaml", ".yml", ".toml", ".json", ".md",
}


def run_cmd(cmd: str, cwd: str = None, timeout: int = 10) -> str:
    """Run a shell command and return output."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            cwd=cwd, timeout=timeout
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, Exception):
        return ""


def estimate_tokens(text: str) -> int:
    """Rough token estimate (~4 chars per token)."""
    return len(text) // 4


def build_tree(root: str, max_depth: int = 3, focus: str = None) -> str:
    """Build directory tree string."""
    lines = []
    root_path = Path(root)
    
    def _walk(path: Path, prefix: str, depth: int):
        if depth > max_depth:
            return
        
        try:
            entries = sorted(path.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower()))
        except PermissionError:
            return
        
        # Filter out skip dirs
        entries = [e for e in entries if e.name not in SKIP_DIRS and not e.name.startswith('.')]
        
        if focus:
            # When focusing, only show paths that match or contain matching children
            focus_lower = focus.lower()
            filtered = []
            for e in entries:
                if focus_lower in e.name.lower():
                    filtered.append(e)
                elif e.is_dir():
                    # Check if any children match
                    try:
                        has_match = any(focus_lower in f.name.lower() for f in e.rglob("*"))
                        if has_match:
                            filtered.append(e)
                    except (PermissionError, OSError):
                        pass
            entries = filtered
        
        for i, entry in enumerate(entries):
            is_last = i == len(entries) - 1
            connector = "└── " if is_last else "├── "
            
            try:
                if entry.is_dir():
                    lines.append(f"{prefix}{connector}{entry.name}/")
                    extension = "    " if is_last else "│   "
                    _walk(entry, prefix + extension, depth + 1)
                else:
                    size = entry.stat().st_size
                    size_str = f" ({_human_size(size)})" if size > 10000 else ""
                    lines.append(f"{prefix}{connector}{entry.name}{size_str}")
            except (OSError, FileNotFoundError):
                lines.append(f"{prefix}{connector}{entry.name} [broken link]")
    
    lines.append(f"{root_path.name}/")
    _walk(root_path, "", 1)
    return "\n".join(lines)


def _human_size(size: int) -> str:
    for unit in ["B", "KB", "MB"]:
        if size < 1024:
            return f"{size:.0f}{unit}"
        size /= 1024
    return f"{size:.1f}GB"


def detect_project_type(root: str) -> Dict:
    """Detect project type and key info."""
    info = {"type": "unknown", "language": "unknown", "framework": "unknown"}
    root_path = Path(root)
    
    if (root_path / "pyproject.toml").exists():
        info["type"] = "python"
        info["language"] = "Python"
        try:
            content = (root_path / "pyproject.toml").read_text()
            if "fastapi" in content.lower():
                info["framework"] = "FastAPI"
            elif "django" in content.lower():
                info["framework"] = "Django"
            elif "flask" in content.lower():
                info["framework"] = "Flask"
        except Exception:
            pass
    elif (root_path / "package.json").exists():
        info["type"] = "node"
        info["language"] = "JavaScript/TypeScript"
        try:
            pkg = json.loads((root_path / "package.json").read_text())
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            if "next" in deps:
                info["framework"] = "Next.js"
            elif "react" in deps:
                info["framework"] = "React"
            elif "vue" in deps:
                info["framework"] = "Vue"
            elif "express" in deps:
                info["framework"] = "Express"
        except Exception:
            pass
    elif (root_path / "Cargo.toml").exists():
        info["type"] = "rust"
        info["language"] = "Rust"
    elif (root_path / "go.mod").exists():
        info["type"] = "go"
        info["language"] = "Go"
    
    return info


def get_git_context(root: str, limit: int = 10) -> str:
    """Get recent git history and diff summary."""
    sections = []
    
    # Recent commits
    log = run_cmd(f"git log --oneline -n {limit}", cwd=root)
    if log:
        sections.append(f"### Recent Commits\n```\n{log}\n```")
    
    # Current branch and status
    branch = run_cmd("git branch --show-current", cwd=root)
    status = run_cmd("git status --short", cwd=root)
    if branch:
        sections.append(f"### Branch: `{branch}`")
    if status:
        sections.append(f"### Uncommitted Changes\n```\n{status}\n```")
    
    # Diff stats (last commit)
    diff_stat = run_cmd("git diff --stat HEAD~1 2>/dev/null || echo 'No previous commit'", cwd=root)
    if diff_stat and "No previous" not in diff_stat:
        sections.append(f"### Last Commit Diff Stats\n```\n{diff_stat}\n```")
    
    return "\n\n".join(sections)


def get_deps_context(root: str) -> str:
    """Get dependency information."""
    sections = []
    root_path = Path(root)
    
    req_file = root_path / "requirements.txt"
    if req_file.exists():
        content = req_file.read_text().strip()
        if content:
            sections.append(f"### Python Dependencies (requirements.txt)\n```\n{content}\n```")
    
    pkg_file = root_path / "package.json"
    if pkg_file.exists():
        try:
            pkg = json.loads(pkg_file.read_text())
            deps = pkg.get("dependencies", {})
            dev_deps = pkg.get("devDependencies", {})
            if deps:
                dep_list = "\n".join(f"  {k}: {v}" for k, v in deps.items())
                sections.append(f"### Dependencies\n```\n{dep_list}\n```")
            if dev_deps:
                dev_list = "\n".join(f"  {k}: {v}" for k, v in dev_deps.items())
                sections.append(f"### Dev Dependencies\n```\n{dev_list}\n```")
        except Exception:
            pass
    
    pyproject = root_path / "pyproject.toml"
    if pyproject.exists() and not req_file.exists():
        content = pyproject.read_text()
        # Extract dependencies section
        in_deps = False
        deps_lines = []
        for line in content.split("\n"):
            if "dependencies" in line and "=" in line:
                in_deps = True
                deps_lines.append(line)
            elif in_deps:
                if line.startswith("[") or (line.strip() == "" and deps_lines):
                    break
                deps_lines.append(line)
        if deps_lines:
            sections.append(f"### Python Dependencies (pyproject.toml)\n```toml\n{'chr(10)'.join(deps_lines)}\n```")
    
    return "\n\n".join(sections)


def read_file_content(filepath: str, max_lines: int = 100) -> str:
    """Read file content with line limit."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
        
        if len(lines) > max_lines:
            return "".join(lines[:max_lines]) + f"\n... ({len(lines) - max_lines} more lines)\n"
        return "".join(lines)
    except Exception:
        return ""


def build_context(
    root: str,
    files: List[str] = None,
    depth: int = 3,
    include_git: bool = False,
    include_deps: bool = False,
    focus: str = None,
    max_tokens: int = 12000,
) -> str:
    """Build the full context string."""
    sections = []
    root_path = Path(root).resolve()
    project_name = root_path.name
    
    # Project info
    project_info = detect_project_type(root)
    header = f"# Project Context: {project_name}\n"
    header += f"- **Language:** {project_info['language']}\n"
    if project_info['framework'] != 'unknown':
        header += f"- **Framework:** {project_info['framework']}\n"
    header += f"- **Path:** `{root_path}`\n"
    sections.append(header)
    
    # Directory tree
    tree = build_tree(root, max_depth=depth, focus=focus)
    sections.append(f"## Project Structure\n```\n{tree}\n```")
    
    # Key files (auto-detected)
    key_files_content = []
    for kf in KEY_FILES:
        kf_path = root_path / kf
        if kf_path.exists():
            content = read_file_content(str(kf_path), max_lines=60)
            if content.strip():
                ext = kf_path.suffix.lstrip('.') or 'text'
                key_files_content.append(f"### {kf}\n```{ext}\n{content.rstrip()}\n```")
    
    if key_files_content:
        sections.append("## Key Files\n" + "\n\n".join(key_files_content))
    
    # Explicitly requested files
    if files:
        explicit_content = []
        for f in files:
            f_path = root_path / f if not os.path.isabs(f) else Path(f)
            if f_path.exists() and f_path.is_file():
                content = read_file_content(str(f_path), max_lines=200)
                if content.strip():
                    ext = f_path.suffix.lstrip('.') or 'text'
                    explicit_content.append(f"### {f}\n```{ext}\n{content.rstrip()}\n```")
        if explicit_content:
            sections.append("## Requested Files\n" + "\n\n".join(explicit_content))
    
    # Focus files
    if focus:
        focus_files = []
        focus_lower = focus.lower()
        for p in root_path.rglob("*"):
            if p.is_file() and focus_lower in p.name.lower() and p.suffix in CODE_EXTENSIONS:
                rel = p.relative_to(root_path)
                # Skip big files and skip dirs
                if any(skip in str(rel) for skip in SKIP_DIRS):
                    continue
                if p.stat().st_size < 50000:
                    content = read_file_content(str(p), max_lines=150)
                    if content.strip():
                        ext = p.suffix.lstrip('.') or 'text'
                        focus_files.append(f"### {rel}\n```{ext}\n{content.rstrip()}\n```")
        if focus_files:
            sections.append(f"## Files Matching '{focus}'\n" + "\n\n".join(focus_files[:10]))
    
    # Git context
    if include_git:
        git_ctx = get_git_context(root)
        if git_ctx:
            sections.append(f"## Git History\n{git_ctx}")
    
    # Dependencies
    if include_deps:
        deps_ctx = get_deps_context(root)
        if deps_ctx:
            sections.append(f"## Dependencies\n{deps_ctx}")
    
    # Combine and trim
    full_context = "\n\n---\n\n".join(sections)
    
    # Trim if over token limit
    current_tokens = estimate_tokens(full_context)
    if current_tokens > max_tokens:
        # Truncate from the end, keeping header + tree
        lines = full_context.split("\n")
        truncated = []
        token_count = 0
        for line in lines:
            token_count += estimate_tokens(line + "\n")
            if token_count > max_tokens:
                truncated.append(f"\n... [Truncated at ~{max_tokens} tokens. Use --max-tokens to increase]")
                break
            truncated.append(line)
        full_context = "\n".join(truncated)
    
    return full_context


def copy_to_clipboard(text: str) -> bool:
    """Copy text to clipboard (works on macOS/Linux/WSL)."""
    for cmd in ["pbcopy", "xclip -selection clipboard", "xsel --clipboard --input", "clip.exe"]:
        try:
            proc = subprocess.Popen(
                cmd.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            proc.communicate(input=text.encode())
            if proc.returncode == 0:
                return True
        except FileNotFoundError:
            continue
    return False


def main(args: List[str] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="mw context",
        description="Smart context builder for AI coding assistants"
    )
    parser.add_argument("--files", "-f", nargs="+", help="Specific files to include")
    parser.add_argument("--depth", "-d", type=int, default=3, help="Tree depth (default: 3)")
    parser.add_argument("--git", "-g", action="store_true", help="Include git history")
    parser.add_argument("--deps", action="store_true", help="Include dependency info")
    parser.add_argument("--full", action="store_true", help="Include everything")
    parser.add_argument("--focus", help="Focus on files matching pattern")
    parser.add_argument("--copy", "-c", action="store_true", help="Copy to clipboard")
    parser.add_argument("--output", "-o", help="Save to file")
    parser.add_argument("--max-tokens", type=int, default=12000, help="Max output tokens")
    parser.add_argument("--quiet", "-q", action="store_true", help="No status messages")
    parser.add_argument("path", nargs="?", default=".", help="Project root path")
    
    parsed = parser.parse_args(args)
    
    root = os.path.abspath(parsed.path)
    if not os.path.isdir(root):
        print(f"❌ Not a directory: {root}", file=sys.stderr)
        return 1
    
    if parsed.full:
        parsed.git = True
        parsed.deps = True
    
    if not parsed.quiet:
        print(f"🔍 Building context for: {root}", file=sys.stderr)
    
    context = build_context(
        root=root,
        files=parsed.files,
        depth=parsed.depth,
        include_git=parsed.git,
        include_deps=parsed.deps,
        focus=parsed.focus,
        max_tokens=parsed.max_tokens,
    )
    
    tokens = estimate_tokens(context)
    
    if parsed.output:
        with open(parsed.output, 'w') as f:
            f.write(context)
        if not parsed.quiet:
            print(f"✅ Saved to {parsed.output} (~{tokens} tokens)", file=sys.stderr)
    elif parsed.copy:
        if copy_to_clipboard(context):
            if not parsed.quiet:
                print(f"📋 Copied to clipboard (~{tokens} tokens)", file=sys.stderr)
        else:
            print(context)
            if not parsed.quiet:
                print(f"⚠️  Clipboard not available, printed to stdout (~{tokens} tokens)", file=sys.stderr)
    else:
        print(context)
        if not parsed.quiet:
            print(f"\n📊 ~{tokens} tokens", file=sys.stderr)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
