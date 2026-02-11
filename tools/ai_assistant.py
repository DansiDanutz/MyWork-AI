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


def _get_api_key() -> Optional[str]:
    """Get OpenRouter API key from env or config."""
    key = os.environ.get("OPENROUTER_API_KEY")
    if key:
        return key
    # Try config file
    config_path = Path.home() / ".mywork" / "config.json"
    if config_path.exists():
        try:
            cfg = json.loads(config_path.read_text())
            return cfg.get("openrouter_api_key")
        except Exception:
            pass
    return None


def _call_llm(prompt: str, system: str = "", model: str = "deepseek/deepseek-chat") -> str:
    """Call LLM via OpenRouter API."""
    import urllib.request
    import urllib.error

    api_key = _get_api_key()
    if not api_key:
        return f"{RED}Error: No API key found. Set OPENROUTER_API_KEY or run: mw config set openrouter_api_key <key>{RESET}"

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

    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://mywork-ai.dev",
            "X-Title": "MyWork-AI CLI",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
            return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        return f"{RED}API Error ({e.code}): {body[:200]}{RESET}"
    except Exception as e:
        return f"{RED}Error: {e}{RESET}"


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
    """
    args = args or []

    if not args:
        print(f"""
{BOLD}{CYAN}🤖 MyWork AI Assistant{RESET}

{BOLD}Commands:{RESET}
    mw ai ask "question"                    {DIM}Ask a coding question{RESET}
    mw ai explain <file> [--lines 10-50]    {DIM}Explain code{RESET}
    mw ai fix <file> [--error "msg"]         {DIM}Fix bugs in code{RESET}
    mw ai fix --diff                         {DIM}Review git diff for issues{RESET}
    mw ai refactor <file> [--focus area]     {DIM}Suggest refactoring{RESET}
    mw ai test <file> [--framework pytest]   {DIM}Generate tests{RESET}
    mw ai commit [--push]                    {DIM}Generate commit message{RESET}

{BOLD}Configuration:{RESET}
    mw config set openrouter_api_key <key>   {DIM}Set API key{RESET}
    export OPENROUTER_API_KEY=<key>          {DIM}Or use env var{RESET}

{BOLD}Models:{RESET} Uses DeepSeek Chat by default (fast & cheap).
    Set MYWORK_AI_MODEL env var to override (e.g. anthropic/claude-3.5-sonnet)
""")
        return 0

    subcmd = args[0]
    sub_args = args[1:]

    subcmds = {
        "ask": cmd_ai_ask,
        "explain": cmd_ai_explain,
        "fix": cmd_ai_fix,
        "refactor": cmd_ai_refactor,
        "test": cmd_ai_test,
        "commit": cmd_ai_commit,
    }

    if subcmd in subcmds:
        return subcmds[subcmd](sub_args)
    else:
        print(f"{RED}Unknown subcommand: {subcmd}{RESET}")
        print(f"Run {CYAN}mw ai{RESET} for help.")
        return 1
