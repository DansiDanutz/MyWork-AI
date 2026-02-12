#!/usr/bin/env python3
"""
MyWork Pair Programming — mw pair

Live AI pair programming session that watches your file changes in real-time
and provides intelligent suggestions, catches bugs, and helps you code faster.

Features:
- File watcher: detects saves and analyzes diffs
- Smart suggestions: only speaks when it has something useful to say
- Context-aware: understands your project structure
- Multi-model: uses OpenRouter, DeepSeek, or local models
- Session history: remembers context within the pairing session

Usage:
    mw pair                          # Start pairing in current directory
    mw pair --path src/              # Watch specific directory
    mw pair --model deepseek         # Use specific AI provider
    mw pair --quiet                  # Only show critical issues (bugs, security)
    mw pair --review                 # Review all changes since last commit
    mw pair history                  # Show past pairing session summaries
"""

import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ANSI colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

FRAMEWORK_ROOT = Path(__file__).parent.parent
PAIR_DIR = FRAMEWORK_ROOT / ".mw" / "pair_sessions"
PAIR_DIR.mkdir(parents=True, exist_ok=True)

# File extensions to watch
WATCH_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".rs", ".go", ".rb", ".java",
    ".c", ".cpp", ".h", ".hpp", ".cs", ".swift", ".kt", ".scala",
    ".vue", ".svelte", ".html", ".css", ".scss", ".sql", ".sh", ".yaml", ".yml",
    ".toml", ".json", ".md", ".dockerfile", ".tf", ".hcl",
}

# Ignore patterns
IGNORE_PATTERNS = {
    "node_modules", "__pycache__", ".git", ".venv", "venv", "dist", "build",
    ".next", ".nuxt", "target", ".pytest_cache", ".mypy_cache", "coverage",
    ".tox", "egg-info", ".eggs",
}


def get_ai_provider():
    """Get the best available AI provider config."""
    providers = [
        {
            "name": "openrouter",
            "url": "https://openrouter.ai/api/v1/chat/completions",
            "key_env": "OPENROUTER_API_KEY",
            "model": "deepseek/deepseek-chat",
            "headers": {"HTTP-Referer": "https://mywork-ai.dev", "X-Title": "MyWork-AI Pair"},
        },
        {
            "name": "deepseek",
            "url": "https://api.deepseek.com/chat/completions",
            "key_env": "DEEPSEEK_API_KEY",
            "model": "deepseek-chat",
            "headers": {},
        },
        {
            "name": "openai",
            "url": "https://api.openai.com/v1/chat/completions",
            "key_env": "OPENAI_API_KEY",
            "model": "gpt-4o-mini",
            "headers": {},
        },
    ]

    # Check .env file
    env_vars = {}
    env_path = FRAMEWORK_ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env_vars[k.strip()] = v.strip().strip('"').strip("'")

    for p in providers:
        key = os.environ.get(p["key_env"]) or env_vars.get(p["key_env"])
        if key:
            p["key"] = key
            return p

    return None


def call_ai(provider: dict, messages: list, max_tokens: int = 1000) -> Optional[str]:
    """Call AI provider and return response text."""
    import urllib.request
    import urllib.error

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {provider['key']}",
        **provider.get("headers", {}),
    }

    payload = json.dumps({
        "model": provider["model"],
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.3,
    }).encode()

    req = urllib.request.Request(provider["url"], data=payload, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        return None


def get_file_diff(filepath: str) -> Optional[str]:
    """Get the git diff for a specific file."""
    try:
        # First try staged diff, then unstaged
        result = subprocess.run(
            ["git", "diff", "--", filepath],
            capture_output=True, text=True, timeout=5, cwd=os.path.dirname(filepath) or "."
        )
        if result.stdout.strip():
            return result.stdout.strip()

        # Try diff against HEAD
        result = subprocess.run(
            ["git", "diff", "HEAD", "--", filepath],
            capture_output=True, text=True, timeout=5, cwd=os.path.dirname(filepath) or "."
        )
        return result.stdout.strip() if result.stdout.strip() else None
    except Exception:
        return None


def get_file_context(filepath: str) -> str:
    """Get surrounding context about a file."""
    try:
        content = Path(filepath).read_text(errors="replace")
        lines = content.split("\n")
        # Truncate for API limits
        if len(lines) > 200:
            content = "\n".join(lines[:200]) + f"\n... ({len(lines) - 200} more lines)"
        return content[:8000]
    except Exception:
        return ""


def detect_project_type(watch_path: str) -> dict:
    """Detect project type and relevant info."""
    info = {"type": "unknown", "language": "unknown", "framework": "unknown"}
    p = Path(watch_path)

    if (p / "package.json").exists():
        try:
            pkg = json.loads((p / "package.json").read_text())
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            info["language"] = "javascript/typescript"
            if "next" in deps:
                info["framework"] = "Next.js"
            elif "react" in deps:
                info["framework"] = "React"
            elif "vue" in deps:
                info["framework"] = "Vue"
            elif "express" in deps:
                info["framework"] = "Express"
            elif "fastify" in deps:
                info["framework"] = "Fastify"
            elif "@nestjs/core" in deps:
                info["framework"] = "NestJS"
            info["type"] = "node"
        except Exception:
            pass

    if (p / "pyproject.toml").exists() or (p / "setup.py").exists() or (p / "requirements.txt").exists():
        info["language"] = "python"
        info["type"] = "python"
        if (p / "pyproject.toml").exists():
            content = (p / "pyproject.toml").read_text()
            if "fastapi" in content.lower():
                info["framework"] = "FastAPI"
            elif "django" in content.lower():
                info["framework"] = "Django"
            elif "flask" in content.lower():
                info["framework"] = "Flask"

    if (p / "Cargo.toml").exists():
        info["language"] = "rust"
        info["type"] = "rust"
    if (p / "go.mod").exists():
        info["language"] = "go"
        info["type"] = "go"

    return info


def scan_files(watch_path: str) -> Dict[str, float]:
    """Scan directory and return file -> mtime mapping."""
    files = {}
    watch = Path(watch_path)

    for root, dirs, filenames in os.walk(watch):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_PATTERNS]

        for f in filenames:
            fp = Path(root) / f
            if fp.suffix in WATCH_EXTENSIONS:
                try:
                    files[str(fp)] = fp.stat().st_mtime
                except OSError:
                    pass
    return files


def analyze_change(provider: dict, filepath: str, diff: str, project_info: dict,
                   session_context: list, quiet: bool = False) -> Optional[str]:
    """Analyze a file change and return suggestion if warranted."""
    filename = os.path.basename(filepath)
    ext = Path(filepath).suffix

    system_prompt = f"""You are an expert pair programming partner for a {project_info['language']} project using {project_info['framework']}.
You are watching the developer code in real-time. They just saved changes to `{filename}`.

Your job:
1. Review the diff for bugs, security issues, performance problems, or logic errors
2. Suggest improvements ONLY if they are genuinely valuable
3. Be concise — max 3-4 lines for minor things, more for critical issues
4. {"Only flag bugs and security issues." if quiet else "Flag bugs, suggest improvements, and share insights."}

Rules:
- Do NOT comment on style preferences (semicolons, quotes, etc.)
- Do NOT suggest changes that are purely cosmetic
- Do NOT repeat yourself — check the session context
- If the code looks good, respond with exactly: LGTM
- Be specific — mention line numbers when relevant
- Use emoji sparingly: 🐛 for bugs, ⚠️ for warnings, 💡 for suggestions, 🔒 for security"""

    messages = [
        {"role": "system", "content": system_prompt},
    ]

    # Add recent session context (last 3 interactions)
    for ctx in session_context[-3:]:
        messages.append({"role": "user", "content": f"[Previous change to {ctx['file']}]: {ctx['summary']}"})
        if ctx.get("response"):
            messages.append({"role": "assistant", "content": ctx["response"]})

    user_msg = f"File: {filepath}\n\nDiff:\n```\n{diff[:4000]}\n```"
    messages.append({"role": "user", "content": user_msg})

    return call_ai(provider, messages, max_tokens=500)


def review_all_changes(provider: dict, watch_path: str, project_info: dict) -> str:
    """Review all uncommitted changes at once."""
    try:
        result = subprocess.run(
            ["git", "diff", "--stat"],
            capture_output=True, text=True, timeout=10, cwd=watch_path
        )
        stat = result.stdout.strip()

        result = subprocess.run(
            ["git", "diff"],
            capture_output=True, text=True, timeout=10, cwd=watch_path
        )
        full_diff = result.stdout.strip()

        if not full_diff:
            return "No uncommitted changes found."

    except Exception as e:
        return f"Error getting git diff: {e}"

    messages = [
        {"role": "system", "content": f"""You are reviewing all uncommitted changes in a {project_info['language']}/{project_info['framework']} project.
Provide a concise code review covering:
1. 🐛 Bugs or logic errors
2. 🔒 Security concerns
3. ⚡ Performance issues
4. 💡 Improvement suggestions
5. ✅ What looks good

Be specific with file names and line numbers. Format as a clean list."""},
        {"role": "user", "content": f"Files changed:\n{stat}\n\nFull diff:\n```\n{full_diff[:12000]}\n```"},
    ]

    return call_ai(provider, messages, max_tokens=1500) or "AI review unavailable."


def save_session(session_id: str, session_context: list, project_info: dict, watch_path: str):
    """Save pairing session summary."""
    session_file = PAIR_DIR / f"{session_id}.json"
    session_data = {
        "id": session_id,
        "timestamp": datetime.now().isoformat(),
        "project": project_info,
        "watch_path": watch_path,
        "changes_reviewed": len(session_context),
        "interactions": session_context[-20:],  # Keep last 20
    }
    session_file.write_text(json.dumps(session_data, indent=2))


def show_history():
    """Show past pairing session summaries."""
    sessions = sorted(PAIR_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)

    if not sessions:
        print(f"{YELLOW}No pairing sessions found.{RESET}")
        return 0

    print(f"\n{BOLD}🤝 Pair Programming History{RESET}")
    print(f"{'─' * 60}")

    for sf in sessions[:10]:
        try:
            data = json.loads(sf.read_text())
            ts = data.get("timestamp", "unknown")[:16]
            changes = data.get("changes_reviewed", 0)
            proj = data.get("project", {})
            lang = proj.get("language", "?")
            fw = proj.get("framework", "?")
            print(f"  {DIM}{ts}{RESET}  {CYAN}{lang}/{fw}{RESET}  {changes} changes reviewed")
        except Exception:
            pass

    print(f"{'─' * 60}")
    return 0


def cmd_pair(args: List[str] = None) -> int:
    """Main pair programming command."""
    args = args or []

    # Handle subcommands
    if args and args[0] == "history":
        return show_history()

    if args and args[0] in ["--help", "-h", "help"]:
        print(__doc__)
        return 0

    # Parse flags
    watch_path = "."
    quiet = False
    review_mode = False
    model_override = None

    i = 0
    while i < len(args):
        if args[i] == "--path" and i + 1 < len(args):
            watch_path = args[i + 1]
            i += 2
        elif args[i] == "--quiet":
            quiet = True
            i += 1
        elif args[i] == "--review":
            review_mode = True
            i += 1
        elif args[i] == "--model" and i + 1 < len(args):
            model_override = args[i + 1]
            i += 2
        else:
            watch_path = args[i]
            i += 1

    watch_path = os.path.abspath(watch_path)

    if not os.path.isdir(watch_path):
        print(f"{RED}❌ Directory not found: {watch_path}{RESET}")
        return 1

    # Get AI provider
    provider = get_ai_provider()
    if not provider:
        print(f"{RED}❌ No AI provider configured. Set OPENROUTER_API_KEY, DEEPSEEK_API_KEY, or OPENAI_API_KEY{RESET}")
        return 1

    if model_override:
        # Simple model override mapping
        model_map = {
            "deepseek": ("deepseek", "deepseek-chat"),
            "gpt4": ("openai", "gpt-4o"),
            "gpt4o": ("openai", "gpt-4o"),
            "gpt4o-mini": ("openai", "gpt-4o-mini"),
            "claude": ("openrouter", "anthropic/claude-3.5-sonnet"),
        }
        if model_override in model_map:
            _, provider["model"] = model_map[model_override]

    project_info = detect_project_type(watch_path)
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_context: list = []

    # Review mode — one-shot review of all changes
    if review_mode:
        print(f"\n{BOLD}🔍 Reviewing all uncommitted changes...{RESET}")
        result = review_all_changes(provider, watch_path, project_info)
        print(f"\n{result}")
        return 0

    # Live watch mode
    print(f"""
{BOLD}{MAGENTA}🤝 MyWork Pair Programming{RESET}
{'─' * 50}
{DIM}Directory:{RESET}  {watch_path}
{DIM}Project:{RESET}    {project_info['language']} / {project_info['framework']}
{DIM}AI Model:{RESET}   {provider['name']} ({provider['model']})
{DIM}Mode:{RESET}       {'Quiet (bugs only)' if quiet else 'Full (bugs + suggestions)'}
{'─' * 50}
{GREEN}Watching for file changes... (Ctrl+C to stop){RESET}
""")

    # Initial file scan
    known_files = scan_files(watch_path)
    changes_count = 0

    try:
        while True:
            time.sleep(1)  # Poll every second

            current_files = scan_files(watch_path)

            # Find changed files
            for filepath, mtime in current_files.items():
                old_mtime = known_files.get(filepath)

                if old_mtime is not None and mtime > old_mtime:
                    # File was modified
                    diff = get_file_diff(filepath)
                    if not diff:
                        continue

                    rel_path = os.path.relpath(filepath, watch_path)
                    changes_count += 1

                    print(f"\n{BLUE}📝 Change detected:{RESET} {rel_path}")

                    response = analyze_change(
                        provider, filepath, diff, project_info, session_context, quiet
                    )

                    if response and response.strip() != "LGTM":
                        print(f"{CYAN}🤖 Pair:{RESET} {response}")
                    elif response:
                        print(f"{GREEN}✅ LGTM{RESET}")

                    session_context.append({
                        "file": rel_path,
                        "time": datetime.now().isoformat(),
                        "summary": diff[:200],
                        "response": response,
                    })

                    # Save session periodically
                    if changes_count % 5 == 0:
                        save_session(session_id, session_context, project_info, watch_path)

                elif filepath not in known_files:
                    # New file
                    rel_path = os.path.relpath(filepath, watch_path)
                    print(f"{GREEN}📄 New file:{RESET} {rel_path}")

            # Check for deleted files
            for filepath in set(known_files) - set(current_files):
                rel_path = os.path.relpath(filepath, watch_path)
                print(f"{YELLOW}🗑️  Deleted:{RESET} {rel_path}")

            known_files = current_files

    except KeyboardInterrupt:
        print(f"\n\n{BOLD}📊 Session Summary{RESET}")
        print(f"{'─' * 40}")
        print(f"  Changes reviewed: {changes_count}")
        print(f"  Duration: {session_id}")
        save_session(session_id, session_context, project_info, watch_path)
        print(f"  Session saved to: {PAIR_DIR / f'{session_id}.json'}")
        print(f"\n{GREEN}Thanks for pairing! 🤝{RESET}\n")
        return 0


if __name__ == "__main__":
    sys.exit(cmd_pair(sys.argv[1:]))
