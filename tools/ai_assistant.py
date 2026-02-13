"""
MyWork AI Assistant — mw ai

Inline AI assistance for developers: ask questions, explain code,
fix errors, refactor, and generate tests.

Uses OpenRouter API for multi-model support.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

# ANSI colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


# Multi-provider configuration
PROVIDERS = {
    "openrouter": {
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "env_key": "OPENROUTER_API_KEY",
        "config_key": "openrouter_api_key",
        "default_model": "deepseek/deepseek-chat",
        "extra_headers": {"HTTP-Referer": "https://mywork-ai.dev", "X-Title": "MyWork-AI CLI"},
    },
    "deepseek": {
        "url": "https://api.deepseek.com/chat/completions",
        "env_key": "DEEPSEEK_API_KEY",
        "config_key": "deepseek_api_key",
        "default_model": "deepseek-chat",
        "extra_headers": {},
    },
    "openai": {
        "url": "https://api.openai.com/v1/chat/completions",
        "env_key": "OPENAI_API_KEY",
        "config_key": "openai_api_key",
        "default_model": "gpt-4o-mini",
        "extra_headers": {},
    },
    "gemini": {
        "url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        "env_key": "GEMINI_API_KEY",
        "config_key": "gemini_api_key",
        "default_model": "gemini-2.0-flash",
        "extra_headers": {},
    },
}

# Model shortcuts for --model flag
MODEL_SHORTCUTS = {
    "deepseek": ("openrouter", "deepseek/deepseek-chat"),
    "ds-reasoner": ("deepseek", "deepseek-reasoner"),
    "gpt4": ("openai", "gpt-4o-mini"),
    "gpt4o": ("openai", "gpt-4o"),
    "claude": ("openrouter", "anthropic/claude-3.5-sonnet"),
    "gemini": ("gemini", "gemini-2.0-flash"),
    "gemini-pro": ("gemini", "gemini-2.5-pro"),
    "kimi": ("openrouter", "moonshotai/kimi-k2"),
    "llama": ("openrouter", "meta-llama/llama-3.3-70b-instruct"),
}


def _load_env():
    """Load .env from framework root."""
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _get_provider_key(provider_name: str) -> Optional[str]:
    """Get API key for a specific provider."""
    _load_env()
    prov = PROVIDERS.get(provider_name, {})
    # Check env
    key = os.environ.get(prov.get("env_key", ""), "")
    if key:
        return key
    # Check config
    config_path = Path.home() / ".mywork" / "config.json"
    if config_path.exists():
        try:
            cfg = json.loads(config_path.read_text())
            return cfg.get(prov.get("config_key", ""))
        except Exception:
            pass
    return None


def _detect_provider() -> tuple:
    """Auto-detect first available provider. Returns (name, api_key)."""
    _load_env()
    for name in ["openrouter", "deepseek", "gemini", "openai"]:
        key = _get_provider_key(name)
        if key:
            return name, key
    return None, None


def _call_llm(prompt: str, system: str = "", model: str = "deepseek/deepseek-chat",
              provider_name: str = None) -> str:
    """Call LLM via configurable provider (OpenRouter, DeepSeek, OpenAI, Gemini)."""
    import urllib.request
    import urllib.error

    # Resolve provider
    if provider_name and provider_name in PROVIDERS:
        api_key = _get_provider_key(provider_name)
    else:
        provider_name, api_key = _detect_provider()

    if not api_key:
        return (f"{RED}Error: No API key found. Set one of: "
                f"OPENROUTER_API_KEY, DEEPSEEK_API_KEY, GEMINI_API_KEY, OPENAI_API_KEY\n"
                f"Or run: mw config set <provider>_api_key <key>{RESET}")

    prov = PROVIDERS[provider_name]
    if model == "deepseek/deepseek-chat" and provider_name != "openrouter":
        model = prov["default_model"]

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = json.dumps({
        "model": model,
        "messages": messages,
        "max_tokens": 4096,
        "temperature": 0.3,
    }).encode()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    headers.update(prov.get("extra_headers", {}))

    req = urllib.request.Request(prov["url"], data=payload, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
            return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        return f"{RED}API Error ({e.code}) [{provider_name}]: {body[:200]}{RESET}"
    except Exception as e:
        return f"{RED}Error [{provider_name}]: {e}{RESET}"


def _read_file(path: str) -> Optional[str]:
    """Read file contents safely."""
    p = Path(path)
    if not p.exists():
        print(f"{RED}File not found: {path}{RESET}")
        return None
    if p.stat().st_size > 100_000:
        print(f"{YELLOW}Warning: Large file ({p.stat().st_size} bytes), reading first 100KB{RESET}")
        return p.read_text(errors="replace")[:100_000]
    return p.read_text(errors="replace")


def _get_git_diff() -> str:
    """Get current git diff."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True, text=True, timeout=10
        )
        diff = result.stdout.strip()
        if not diff:
            result = subprocess.run(
                ["git", "diff"],
                capture_output=True, text=True, timeout=10
            )
            diff = result.stdout.strip()
        return diff if diff else "(no changes)"
    except Exception:
        return "(git not available)"


def cmd_ai_ask(args: List[str]) -> int:
    """Ask the AI a coding question.

    Usage: mw ai ask "How do I handle async errors in Python?"
    """
    if not args:
        print(f"{RED}Usage: mw ai ask \"your question\"{RESET}")
        return 1

    question = " ".join(args)
    print(f"{CYAN}🤖 Thinking...{RESET}")

    system = (
        "You are a senior developer assistant for the MyWork-AI framework. "
        "Give concise, practical answers with code examples when relevant. "
        "Use markdown formatting."
    )
    answer = _call_llm(question, system)
    print(f"\n{answer}\n")
    return 0


def cmd_ai_explain(args: List[str]) -> int:
    """Explain code from a file.

    Usage: mw ai explain <file> [--lines 10-50]
    """
    if not args:
        print(f"{RED}Usage: mw ai explain <file> [--lines START-END]{RESET}")
        return 1

    file_path = args[0]
    lines_range = None

    # Parse --lines flag
    for i, arg in enumerate(args[1:], 1):
        if arg == "--lines" and i + 1 < len(args):
            lines_range = args[i + 1]

    content = _read_file(file_path)
    if content is None:
        return 1

    if lines_range:
        try:
            start, end = map(int, lines_range.split("-"))
            all_lines = content.splitlines()
            content = "\n".join(all_lines[start - 1:end])
            file_path = f"{file_path} (lines {start}-{end})"
        except ValueError:
            print(f"{YELLOW}Invalid line range, showing full file{RESET}")

    print(f"{CYAN}🤖 Analyzing {file_path}...{RESET}")

    prompt = f"Explain this code clearly and concisely. Highlight:\n- Purpose\n- Key logic\n- Any potential issues\n\n```\n{content}\n```"
    system = "You are a code explainer. Be concise but thorough. Use bullet points."
    answer = _call_llm(prompt, system)
    print(f"\n{answer}\n")
    return 0


def cmd_ai_fix(args: List[str]) -> int:
    """Fix errors in a file or from an error message.

    Usage:
        mw ai fix <file>                    # Analyze file for bugs
        mw ai fix <file> --error "message"  # Fix specific error
        mw ai fix --diff                    # Review git diff for issues
    """
    if not args:
        print(f"{RED}Usage: mw ai fix <file> [--error \"message\"]{RESET}")
        return 1

    if args[0] == "--diff":
        diff = _get_git_diff()
        print(f"{CYAN}🤖 Reviewing diff for issues...{RESET}")
        prompt = f"Review this git diff for bugs, issues, or improvements:\n\n```diff\n{diff}\n```"
        system = "You are a code reviewer. Find bugs, security issues, and suggest fixes with code."
        answer = _call_llm(prompt, system)
        print(f"\n{answer}\n")
        return 0

    file_path = args[0]
    error_msg = None

    for i, arg in enumerate(args[1:], 1):
        if arg == "--error" and i + 1 < len(args):
            error_msg = " ".join(args[i + 1:])
            break

    content = _read_file(file_path)
    if content is None:
        return 1

    print(f"{CYAN}🤖 Analyzing {file_path} for issues...{RESET}")

    if error_msg:
        prompt = f"Fix this error in the code below.\n\nError: {error_msg}\n\nCode:\n```\n{content}\n```\n\nProvide the fixed code and explain what was wrong."
    else:
        prompt = f"Analyze this code for bugs, security issues, and improvements:\n\n```\n{content}\n```\n\nList issues found and provide fixed code."

    system = "You are a bug-fixing assistant. Identify issues and provide corrected code with explanations."
    answer = _call_llm(prompt, system)
    print(f"\n{answer}\n")
    return 0


def cmd_ai_refactor(args: List[str]) -> int:
    """Suggest refactoring for a file.

    Usage: mw ai refactor <file> [--focus "performance|readability|security"]
    """
    if not args:
        print(f"{RED}Usage: mw ai refactor <file> [--focus \"area\"]{RESET}")
        return 1

    file_path = args[0]
    focus = "general best practices"

    for i, arg in enumerate(args[1:], 1):
        if arg == "--focus" and i + 1 < len(args):
            focus = args[i + 1]

    content = _read_file(file_path)
    if content is None:
        return 1

    print(f"{CYAN}🤖 Refactoring suggestions for {file_path} (focus: {focus})...{RESET}")

    prompt = f"Refactor this code with focus on: {focus}\n\nCode:\n```\n{content}\n```\n\nProvide refactored code and explain each change."
    system = "You are a refactoring expert. Suggest clean, idiomatic improvements."
    answer = _call_llm(prompt, system)
    print(f"\n{answer}\n")
    return 0


def cmd_ai_test(args: List[str]) -> int:
    """Generate tests for a file.

    Usage: mw ai test <file> [--framework pytest|unittest]
    """
    if not args:
        print(f"{RED}Usage: mw ai test <file> [--framework pytest]{RESET}")
        return 1

    file_path = args[0]
    framework = "pytest"

    for i, arg in enumerate(args[1:], 1):
        if arg == "--framework" and i + 1 < len(args):
            framework = args[i + 1]

    content = _read_file(file_path)
    if content is None:
        return 1

    print(f"{CYAN}🤖 Generating {framework} tests for {file_path}...{RESET}")

    prompt = f"Generate comprehensive {framework} tests for this code:\n\n```\n{content}\n```\n\nInclude:\n- Happy path tests\n- Edge cases\n- Error handling tests\n- Mock external dependencies"
    system = f"You are a test engineer. Generate thorough {framework} tests. Output ONLY the test code."
    answer = _call_llm(prompt, system)
    print(f"\n{answer}\n")
    return 0


def cmd_ai_commit(args: List[str]) -> int:
    """Generate a commit message from staged changes.

    Usage: mw ai commit [--push]
    """
    diff = _get_git_diff()
    if diff == "(no changes)":
        print(f"{YELLOW}No changes to commit.{RESET}")
        return 1

    print(f"{CYAN}🤖 Generating commit message...{RESET}")

    prompt = f"Generate a conventional commit message for this diff. Format: type(scope): description\n\nDiff:\n```diff\n{diff[:8000]}\n```\n\nReturn ONLY the commit message, nothing else."
    system = "You generate concise git commit messages following conventional commits format."
    msg = _call_llm(prompt, system).strip().strip("`").strip()

    print(f"\n{GREEN}Suggested commit message:{RESET}")
    print(f"  {BOLD}{msg}{RESET}\n")

    if "--push" not in args:
        print(f"{DIM}Use --push to auto-commit, or copy the message above.{RESET}")
    else:
        try:
            subprocess.run(["git", "add", "-A"], check=True, timeout=10)
            subprocess.run(["git", "commit", "-m", msg], check=True, timeout=10)
            subprocess.run(["git", "push"], check=True, timeout=30)
            print(f"{GREEN}✅ Committed and pushed!{RESET}")
        except subprocess.CalledProcessError as e:
            print(f"{RED}Git error: {e}{RESET}")
            return 1

    return 0


def cmd_ai_review(args: List[str]) -> int:
    """Review code changes with AI — like a senior dev code review.

    Usage: mw ai review [--staged] [--branch main] [--severity]
    """
    staged_only = "--staged" in args
    show_severity = "--severity" in args
    branch = None
    for i, arg in enumerate(args):
        if arg == "--branch" and i + 1 < len(args):
            branch = args[i + 1]

    # Get diff
    if branch:
        diff = subprocess.run(
            ["git", "diff", branch], capture_output=True, text=True
        ).stdout
    elif staged_only:
        diff = subprocess.run(
            ["git", "diff", "--cached"], capture_output=True, text=True
        ).stdout
    else:
        diff = _get_git_diff()

    if not diff or not diff.strip():
        print(f"{GREEN}✓ No changes to review.{RESET}")
        return 0

    # Truncate very large diffs
    if len(diff) > 8000:
        diff = diff[:8000] + "\n\n... (truncated, showing first 8000 chars)"

    print(f"{CYAN}🔍 Reviewing code changes...{RESET}\n")

    system = """You are a senior code reviewer. Review the git diff and provide:

1. **Summary** — What changed in 1-2 sentences
2. **Issues** — Bugs, security problems, logic errors (with file:line references)
3. **Suggestions** — Improvements for readability, performance, best practices
4. **Rating** — Overall quality: 🟢 Good / 🟡 Needs Work / 🔴 Critical Issues

Be specific, reference file names and line numbers. Be constructive, not harsh."""

    prompt = f"Review this git diff:\n\n```diff\n{diff}\n```"
    answer = _call_llm(prompt, system)
    print(f"{answer}\n")
    return 0


def cmd_ai_doc(args: List[str]) -> int:
    """Auto-generate documentation for a file or project.

    Usage: mw ai doc <file> [--style google|numpy|sphinx] [--readme]
    """
    if not args:
        print(f"{RED}Usage: mw ai doc <file> [--style google|numpy] [--readme]{RESET}")
        return 1

    file_path = args[0]
    style = "google"
    gen_readme = "--readme" in args

    for i, arg in enumerate(args):
        if arg == "--style" and i + 1 < len(args):
            style = args[i + 1]

    if gen_readme:
        # Generate README for current project
        print(f"{CYAN}📄 Generating README...{RESET}\n")

        # Gather project info
        files_info = []
        for ext in ("*.py", "*.js", "*.ts", "*.go", "*.rs"):
            for f in Path(".").rglob(ext):
                if ".git" not in str(f) and "node_modules" not in str(f):
                    files_info.append(str(f))
                if len(files_info) >= 30:
                    break

        pkg_json = Path("package.json")
        pyproject = Path("pyproject.toml")
        setup_py = Path("setup.py")
        project_info = ""
        if pkg_json.exists():
            project_info = pkg_json.read_text()[:1000]
        elif pyproject.exists():
            project_info = pyproject.read_text()[:1000]
        elif setup_py.exists():
            project_info = setup_py.read_text()[:1000]

        prompt = f"""Generate a professional README.md for this project.

Project config:
{project_info}

Files in project:
{chr(10).join(files_info[:20])}

Include: badges, features, installation, usage, API reference outline, contributing, license sections."""

        system = "You are a technical writer. Generate clean, professional README files in markdown."
        answer = _call_llm(prompt, system)
        print(f"{answer}\n")
        return 0

    content = _read_file(file_path)
    if content is None:
        return 1

    print(f"{CYAN}📄 Generating docs for {file_path} ({style} style)...{RESET}\n")

    prompt = f"""Generate comprehensive documentation for this code using {style} docstring style.

For each function/class:
- Purpose description
- Parameters with types
- Return values
- Example usage
- Any exceptions raised

Code:
```
{content}
```

Output the fully documented version of the code."""

    system = f"You are a documentation expert. Generate {style}-style docstrings and inline comments."
    answer = _call_llm(prompt, system)
    print(f"{answer}\n")
    return 0


def cmd_ai_changelog(args: List[str]) -> int:
    """Generate a changelog from recent git commits.

    Usage: mw ai changelog [--since "1 week ago"] [--format keep-a-changelog]
    """
    since = "1 week ago"
    for i, arg in enumerate(args):
        if arg == "--since" and i + 1 < len(args):
            since = args[i + 1]

    log = subprocess.run(
        ["git", "log", f"--since={since}", "--oneline", "--no-merges"],
        capture_output=True, text=True,
    ).stdout

    if not log.strip():
        print(f"{YELLOW}No commits found since {since}.{RESET}")
        return 0

    print(f"{CYAN}📋 Generating changelog from recent commits...{RESET}\n")

    prompt = f"""Generate a clean changelog from these git commits:

{log}

Format as Keep a Changelog (https://keepachangelog.com) with sections:
### Added, ### Changed, ### Fixed, ### Removed

Group related commits, write user-friendly descriptions (not raw commit messages)."""

    system = "You are a release manager. Generate clean, user-friendly changelogs."
    answer = _call_llm(prompt, system)
    print(f"{answer}\n")
    return 0


def cmd_ai_generate(args: List[str]) -> int:
    """Generate a complete file from a natural language description.

    Usage:
        mw ai generate <filename> "description of what to build"
        mw ai generate api.py "FastAPI CRUD for users with JWT auth"
        mw ai generate components/Modal.tsx "React modal with close on ESC and backdrop click"
        mw ai generate --dry-run schema.sql "PostgreSQL schema for e-commerce"
    """
    if not args or args[0] in ("-h", "--help"):
        print(f"""
{BOLD}{CYAN}🛠️  mw ai generate — Generate Files from Description{RESET}

{BOLD}Usage:{RESET}
    mw ai generate <filename> "description"
    mw ai generate --dry-run <filename> "description"

{BOLD}Examples:{RESET}
    mw ai generate api.py "FastAPI REST API for blog posts with CRUD"
    mw ai generate src/utils/cache.ts "LRU cache with TTL support"
    mw ai generate Dockerfile "Multi-stage build for Python FastAPI app"
    mw ai generate schema.prisma "E-commerce data model with users, products, orders"
    mw ai generate --dry-run config.yaml "Kubernetes deployment for 3 replicas"

{BOLD}Options:{RESET}
    --dry-run     Print generated code without writing to file
    --model X     Use specific model (deepseek, claude, gpt4, gemini)

{BOLD}Supported:{RESET} Any file type — Python, TypeScript, SQL, YAML, Docker, Terraform, etc.
""")
        return 0

    dry_run = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]

    # Parse --model
    provider_name = None
    model = None
    filtered = []
    i = 0
    while i < len(args):
        if args[i] == "--model" and i + 1 < len(args):
            model_shortcut = args[i + 1]
            model_map = {
                "deepseek": ("openrouter", "deepseek/deepseek-chat"),
                "claude": ("openrouter", "anthropic/claude-sonnet-4-20250514"),
                "gpt4": ("openrouter", "openai/gpt-4.1"),
                "gemini": ("openrouter", "google/gemini-2.5-flash"),
                "gemini-pro": ("openrouter", "google/gemini-2.5-pro"),
                "kimi": ("openrouter", "moonshotai/kimi-k2"),
                "llama": ("openrouter", "meta-llama/llama-4-maverick"),
            }
            if model_shortcut in model_map:
                provider_name, model = model_map[model_shortcut]
            else:
                provider_name = "openrouter"
                model = model_shortcut
            i += 2
        else:
            filtered.append(args[i])
            i += 1
    args = filtered

    if len(args) < 2:
        print(f"{RED}❌ Usage: mw ai generate <filename> \"description\"{RESET}")
        print(f"   Example: mw ai generate api.py \"FastAPI CRUD for users\"")
        return 1

    filename = args[0]
    description = " ".join(args[1:])
    ext = Path(filename).suffix.lstrip(".")

    # Detect language from extension
    lang_map = {
        "py": "Python", "js": "JavaScript", "ts": "TypeScript", "tsx": "TypeScript React",
        "jsx": "JavaScript React", "rs": "Rust", "go": "Go", "rb": "Ruby",
        "java": "Java", "kt": "Kotlin", "swift": "Swift", "cs": "C#",
        "sql": "SQL", "prisma": "Prisma", "yaml": "YAML", "yml": "YAML",
        "toml": "TOML", "json": "JSON", "md": "Markdown", "sh": "Bash",
        "dockerfile": "Dockerfile", "tf": "Terraform", "hcl": "HCL",
        "html": "HTML", "css": "CSS", "scss": "SCSS", "vue": "Vue",
        "svelte": "Svelte",
    }
    # Handle Dockerfile specially
    base = Path(filename).name.lower()
    if base in ("dockerfile", "docker-compose.yml", "docker-compose.yaml"):
        lang = "Docker"
    else:
        lang = lang_map.get(ext, ext.upper() if ext else "text")

    # Build context from existing project files
    context_files = []
    cwd = Path.cwd()
    # Check for project config files to understand the stack
    for cfg in ["package.json", "pyproject.toml", "Cargo.toml", "go.mod", "requirements.txt"]:
        cfg_path = cwd / cfg
        if cfg_path.exists():
            try:
                content = cfg_path.read_text()[:500]
                context_files.append(f"--- {cfg} ---\n{content}")
            except Exception:
                pass

    context = ""
    if context_files:
        context = "\n\nProject context (existing config files):\n" + "\n".join(context_files)

    system = f"""You are an expert {lang} developer. Generate a complete, production-ready file.
Rules:
- Output ONLY the file content, no markdown fences, no explanations
- Include proper imports, types, error handling, and documentation
- Follow best practices and conventions for {lang}
- Add helpful inline comments for complex logic
- Make it production-ready, not a toy example"""

    prompt = f"""Generate a complete {lang} file: {filename}

Description: {description}{context}

Output the complete file content only. No markdown, no explanations."""

    print(f"\n{BOLD}🛠️  Generating: {CYAN}{filename}{RESET}")
    print(f"   {DIM}Language: {lang} | Description: {description[:60]}{'...' if len(description) > 60 else ''}{RESET}\n")

    call_kwargs = {"prompt": prompt, "system": system}
    if model:
        call_kwargs["model"] = model
    if provider_name:
        call_kwargs["provider_name"] = provider_name
    result = _call_llm(**call_kwargs)

    if not result or result.startswith(RED):
        print(result or f"{RED}❌ No response from AI{RESET}")
        return 1

    # Strip markdown fences if AI included them anyway
    lines = result.strip().split("\n")
    if lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    content = "\n".join(lines) + "\n"

    if dry_run:
        print(f"{BOLD}📋 Generated ({len(content)} chars, {len(lines)} lines):{RESET}\n")
        print(content)
        return 0

    # Create parent directories if needed
    filepath = Path(filename)
    if filepath.parent != Path("."):
        filepath.parent.mkdir(parents=True, exist_ok=True)

    filepath.write_text(content)
    print(f"   {GREEN}✅ Written to {filename} ({len(content)} chars, {len(lines)} lines){RESET}")

    # Make shell scripts executable
    if ext in ("sh", "bash") or base.startswith("Makefile"):
        os.chmod(filename, 0o755)
        print(f"   {DIM}Made executable (chmod +x){RESET}")

    return 0


def _cmd_ai_optimize(args: List[str]) -> int:
    """Delegate to ai_optimize module."""
    from tools.ai_optimize import cmd_optimize
    return cmd_optimize(args)


def _cmd_ai_refactor_static(args: List[str]) -> int:
    """Delegate to ai_refactor module (AST-based, no API key needed)."""
    from tools.ai_refactor import main as refactor_main
    return refactor_main(args)


def cmd_ai(args: List[str] = None) -> int:
    """AI Assistant — inline AI help for developers.

    Usage:
        mw ai ask "question"                    Ask a coding question
        mw ai explain <file> [--lines 10-50]    Explain code
        mw ai fix <file> [--error "msg"]         Fix bugs in code
        mw ai fix --diff                         Review git diff
        mw ai refactor <file> [--focus area]     Refactor suggestions
        mw ai test <file> [--framework pytest]   Generate tests
        mw ai commit [--push]                    Generate commit message
        mw ai review [--staged] [--branch main]  Code review of changes
        mw ai doc <file> [--readme]              Generate documentation
        mw ai changelog [--since "1 week ago"]   Generate changelog
    """
    args = args or []

    if not args or args[0] in ("-h", "--help", "help"):
        print(f"""
{BOLD}{CYAN}🤖 MyWork AI Assistant{RESET}

{BOLD}Commands:{RESET}
    mw ai ask "question"                    {DIM}Ask a coding question{RESET}
    mw ai generate <file> "description"     {DIM}Generate a complete file from description{RESET}
    mw ai explain <file> [--lines 10-50]    {DIM}Explain code{RESET}
    mw ai fix <file> [--error "msg"]         {DIM}Fix bugs in code{RESET}
    mw ai fix --diff                         {DIM}Review git diff for issues{RESET}
    mw ai refactor <file> [--focus area]     {DIM}Suggest refactoring{RESET}
    mw ai test <file> [--framework pytest]   {DIM}Generate tests{RESET}
    mw ai commit [--push]                    {DIM}Generate commit message{RESET}
    mw ai review [--staged] [--branch main]  {DIM}AI code review of changes{RESET}
    mw ai doc <file> [--readme]              {DIM}Generate documentation{RESET}
    mw ai changelog [--since "1 week ago"]   {DIM}Generate changelog from commits{RESET}
    mw ai optimize <file|dir>                {DIM}Find performance optimizations{RESET}

{BOLD}Interactive:{RESET}
    mw ai chat                               {DIM}Start interactive chat session{RESET}
    mw ai chat --model gemini                {DIM}Chat with specific model{RESET}
    mw ai providers                          {DIM}Show configured AI providers{RESET}
    mw ai models                             {DIM}Show model shortcuts{RESET}

{BOLD}Providers:{RESET} OpenRouter, DeepSeek, OpenAI, Google Gemini (auto-detected)
{BOLD}Models:{RESET} deepseek (default), claude, gpt4, gemini, gemini-pro, kimi, llama
""")
        return 0

    subcmd = args[0]
    sub_args = args[1:]

    subcmds = {
        "ask": cmd_ai_ask,
        "generate": cmd_ai_generate,
        "gen": cmd_ai_generate,
        "explain": cmd_ai_explain,
        "fix": cmd_ai_fix,
        "refactor": cmd_ai_refactor,
        "test": cmd_ai_test,
        "commit": cmd_ai_commit,
        "chat": cmd_ai_chat,
        "providers": cmd_ai_providers,
        "models": cmd_ai_models,
        "review": cmd_ai_review,
        "doc": cmd_ai_doc,
        "changelog": cmd_ai_changelog,
        "optimize": _cmd_ai_optimize,
        "perf": _cmd_ai_optimize,
        "refactor-static": _cmd_ai_refactor_static,
        "lint-deep": _cmd_ai_refactor_static,
    }

    if subcmd in subcmds:
        return subcmds[subcmd](sub_args)
    else:
        # Treat unknown subcommand as a question (convenience shortcut)
        return cmd_ai_ask([subcmd] + sub_args)


def cmd_ai_chat(args: List[str]) -> int:
    """Interactive AI chat with project context."""
    # Parse --model flag
    provider_name = None
    model = None
    i = 0
    while i < len(args):
        if args[i] == "--model" and i + 1 < len(args):
            shortcut = args[i + 1]
            if shortcut in MODEL_SHORTCUTS:
                provider_name, model = MODEL_SHORTCUTS[shortcut]
            else:
                model = shortcut
            i += 2
        else:
            i += 1

    if not provider_name:
        provider_name, _ = _detect_provider()
    if not model and provider_name:
        model = PROVIDERS[provider_name]["default_model"]

    print(f"\n{BOLD}{CYAN}🤖 MyWork AI Chat{RESET}")
    print(f"{DIM}Provider: {provider_name or 'auto'} | Model: {model or 'auto'}{RESET}")
    print(f"{DIM}Type 'quit' or Ctrl+C to exit. Type '/context <file>' to add context.{RESET}\n")

    context_files = []
    history = []

    while True:
        try:
            user_input = input(f"{GREEN}You>{RESET} ").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{DIM}Goodbye!{RESET}")
            return 0

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print(f"{DIM}Goodbye!{RESET}")
            return 0

        # Commands
        if user_input.startswith("/context "):
            path = user_input[9:].strip()
            if Path(path).exists():
                context_files.append(path)
                print(f"{GREEN}✓ Added {path} to context{RESET}")
            else:
                print(f"{RED}File not found: {path}{RESET}")
            continue
        if user_input == "/clear":
            history.clear()
            context_files.clear()
            print(f"{GREEN}✓ Context and history cleared{RESET}")
            continue

        # Build prompt with context
        prompt_parts = []
        if context_files:
            for cf in context_files:
                try:
                    content = Path(cf).read_text()[:3000]
                    prompt_parts.append(f"[File: {cf}]\n{content}")
                except Exception:
                    pass
        if history:
            prompt_parts.append("Previous conversation:\n" + "\n".join(
                f"{'User' if i % 2 == 0 else 'AI'}: {msg}" for i, msg in enumerate(history[-6:])
            ))
        prompt_parts.append(user_input)
        full_prompt = "\n\n".join(prompt_parts)

        print(f"{CYAN}AI>{RESET} ", end="", flush=True)
        result = _call_llm(
            full_prompt,
            system="You are a helpful developer assistant. Be concise and practical.",
            model=model or "deepseek/deepseek-chat",
            provider_name=provider_name,
        )
        print(result)
        print()

        history.append(user_input)
        history.append(result[:500])

    return 0


def cmd_ai_providers(args: List[str]) -> int:
    """Show available AI providers and their status."""
    _load_env()
    print(f"\n{BOLD}{CYAN}🤖 AI Providers{RESET}\n")
    for name, prov in PROVIDERS.items():
        key = _get_provider_key(name)
        status = f"{GREEN}✓ configured{RESET}" if key else f"{RED}✗ no key{RESET}"
        print(f"  {BOLD}{name:12}{RESET}  {status}  (model: {prov['default_model']})")
        print(f"  {DIM}  env: {prov['env_key']}{RESET}")
    print(f"\n{DIM}Set keys: mw config set <provider>_api_key <key> or export ENV_VAR=<key>{RESET}\n")
    return 0


def cmd_ai_models(args: List[str]) -> int:
    """Show model shortcuts for --model flag."""
    print(f"\n{BOLD}{CYAN}🤖 Model Shortcuts{RESET}\n")
    for shortcut, (prov, model) in sorted(MODEL_SHORTCUTS.items()):
        print(f"  {BOLD}{shortcut:14}{RESET}  → {prov}/{model}")
    print(f"\n{DIM}Usage: mw ai chat --model gemini{RESET}")
    print(f"{DIM}       mw ai ask --model claude \"your question\"{RESET}\n")
    return 0
