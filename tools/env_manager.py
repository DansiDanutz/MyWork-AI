#!/usr/bin/env python3
"""
Environment Manager (mw env)
============================
Manage .env files across projects — audit, compare, sync, and validate.

Usage:
    python3 env_manager.py check [--project <path>]   # Audit .env vs code usage
    python3 env_manager.py compare <env1> <env2>       # Diff two .env files
    python3 env_manager.py template [--project <path>] # Generate .env.example
    python3 env_manager.py list [--project <path>]     # List all env vars used
    python3 env_manager.py secrets [--project <path>]  # Detect leaked secrets
"""

import os
import re
import sys
import json
from pathlib import Path
from collections import defaultdict

# ANSI colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

def _find_root() -> Path:
    """Find MyWork-AI root."""
    p = Path(__file__).resolve().parent.parent
    if (p / "tools" / "mw.py").exists():
        return p
    return Path.cwd()

SECRET_PATTERNS = [
    (r'(?:sk|pk|api|token|key|secret|password|auth)[_-]?[a-zA-Z0-9]{20,}', "API key/token"),
    (r'eyJ[a-zA-Z0-9_-]{20,}\.eyJ[a-zA-Z0-9_-]{20,}', "JWT token"),
    (r'ghp_[a-zA-Z0-9]{36}', "GitHub PAT"),
    (r'sk-[a-zA-Z0-9]{32,}', "OpenAI/Stripe key"),
    (r'AIza[a-zA-Z0-9_-]{35}', "Google API key"),
    (r'xox[bpsa]-[a-zA-Z0-9-]+', "Slack token"),
]

ENV_VAR_PATTERNS = [
    r'os\.environ\.get\(["\'](\w+)',
    r'os\.environ\[["\'](\w+)',
    r'os\.getenv\(["\'](\w+)',
    r'process\.env\.(\w+)',
    r'\$\{(\w+)\}',
    r'env\(["\'](\w+)',
    r'getenv\(["\'](\w+)',
]

SKIP_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', '.next', 'dist', 'build'}
CODE_EXTS = {'.py', '.js', '.ts', '.jsx', '.tsx', '.sh', '.yml', '.yaml', '.toml', '.cfg', '.env'}


def parse_env_file(path: Path) -> dict:
    """Parse a .env file into key=value dict."""
    env = {}
    if not path.exists():
        return env
    for line in path.read_text(errors='ignore').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' in line:
            key, _, val = line.partition('=')
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            env[key] = val
    return env


def find_env_usage(project_path: Path) -> dict:
    """Scan code for env var references. Returns {var: [files]}."""
    usage = defaultdict(list)
    for root, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fname in files:
            fp = Path(root) / fname
            if fp.suffix not in CODE_EXTS:
                continue
            try:
                content = fp.read_text(errors='ignore')
            except Exception:
                continue
            for pattern in ENV_VAR_PATTERNS:
                for match in re.finditer(pattern, content):
                    var = match.group(1)
                    rel = str(fp.relative_to(project_path))
                    if rel not in usage[var]:
                        usage[var].append(rel)
    return dict(usage)


def find_env_files(project_path: Path) -> list:
    """Find all .env* files in project."""
    envs = []
    for f in project_path.iterdir():
        if f.name.startswith('.env') and f.is_file():
            envs.append(f)
    return sorted(envs)


def cmd_check(project_path: Path):
    """Audit: find missing, unused, and undocumented env vars."""
    print(f"\n{BOLD}🔍 Environment Audit: {project_path.name}{RESET}\n")

    env_files = find_env_files(project_path)
    defined = {}
    for ef in env_files:
        defined.update(parse_env_file(ef))

    usage = find_env_usage(project_path)

    # Missing: used in code but not in .env
    missing = {k: v for k, v in usage.items() if k not in defined and not k.startswith('_')}
    # Unused: in .env but not referenced in code
    unused = {k: v for k, v in defined.items() if k not in usage}
    # OK: both defined and used
    ok = {k for k in defined if k in usage}

    if env_files:
        print(f"  {GREEN}📄 Env files found:{RESET}")
        for ef in env_files:
            count = len(parse_env_file(ef))
            print(f"     {ef.name} ({count} vars)")
    else:
        print(f"  {YELLOW}⚠ No .env files found{RESET}")

    print(f"\n  {GREEN}✅ Matched:{RESET} {len(ok)} vars defined & used")

    if missing:
        # Filter out common false positives
        skip = {'PATH', 'HOME', 'USER', 'SHELL', 'TERM', 'PWD', 'LANG', 'LC_ALL',
                'NODE_ENV', 'PYTHONPATH', 'VIRTUAL_ENV', 'CI', 'DEBUG'}
        missing = {k: v for k, v in missing.items() if k not in skip}

    if missing:
        print(f"  {RED}❌ Missing from .env:{RESET} {len(missing)} vars used in code but not defined")
        for var, files in sorted(missing.items())[:10]:
            print(f"     {RED}{var}{RESET} → {DIM}{', '.join(files[:2])}{RESET}")
        if len(missing) > 10:
            print(f"     {DIM}... and {len(missing)-10} more{RESET}")

    if unused:
        print(f"  {YELLOW}⚠ Unused:{RESET} {len(unused)} vars defined but not referenced in code")
        for var in sorted(unused)[:10]:
            print(f"     {YELLOW}{var}{RESET}")

    print()
    total = len(ok) + len(missing) + len(unused)
    if total > 0:
        score = int((len(ok) / max(total, 1)) * 100)
        bar = "█" * (score // 5) + "░" * (20 - score // 5)
        color = GREEN if score >= 80 else YELLOW if score >= 50 else RED
        print(f"  {BOLD}Env Health: {color}{bar} {score}%{RESET}")
    print()


def cmd_compare(file1: Path, file2: Path):
    """Compare two .env files."""
    print(f"\n{BOLD}🔄 Comparing: {file1.name} vs {file2.name}{RESET}\n")

    env1 = parse_env_file(file1)
    env2 = parse_env_file(file2)

    only1 = set(env1) - set(env2)
    only2 = set(env2) - set(env1)
    both = set(env1) & set(env2)
    diff_vals = {k for k in both if env1[k] != env2[k]}

    if only1:
        print(f"  {RED}Only in {file1.name}:{RESET}")
        for k in sorted(only1):
            print(f"    - {k}")
    if only2:
        print(f"  {GREEN}Only in {file2.name}:{RESET}")
        for k in sorted(only2):
            print(f"    + {k}")
    if diff_vals:
        print(f"  {YELLOW}Different values:{RESET}")
        for k in sorted(diff_vals):
            print(f"    ~ {k}: {DIM}{env1[k][:20]}...{RESET} → {DIM}{env2[k][:20]}...{RESET}")
    if not only1 and not only2 and not diff_vals:
        print(f"  {GREEN}✅ Files are identical!{RESET}")
    print()


def cmd_template(project_path: Path):
    """Generate .env.example from code usage and existing .env."""
    print(f"\n{BOLD}📋 Generating .env.example for: {project_path.name}{RESET}\n")

    usage = find_env_usage(project_path)
    env_files = find_env_files(project_path)
    existing = {}
    for ef in env_files:
        existing.update(parse_env_file(ef))

    skip = {'PATH', 'HOME', 'USER', 'SHELL', 'TERM', 'PWD', 'LANG', 'LC_ALL',
            'VIRTUAL_ENV', 'PYTHONPATH', '_'}

    lines = ["# Environment Variables", f"# Generated for {project_path.name}", ""]
    all_vars = sorted(set(list(usage.keys()) + list(existing.keys())) - skip)

    for var in all_vars:
        files = usage.get(var, [])
        if files:
            lines.append(f"# Used in: {', '.join(files[:3])}")
        if var in existing and not any(p[0] in existing[var] for p in SECRET_PATTERNS if re.search(p[0], existing[var])):
            lines.append(f"{var}={existing[var]}")
        else:
            lines.append(f"{var}=")
        lines.append("")

    out = project_path / ".env.example"
    out.write_text("\n".join(lines))
    print(f"  {GREEN}✅ Written to {out}{RESET}")
    print(f"  {DIM}{len(all_vars)} variables documented{RESET}\n")


def cmd_secrets(project_path: Path):
    """Scan for leaked secrets in code (not .env files)."""
    print(f"\n{BOLD}🔐 Secret Scan: {project_path.name}{RESET}\n")

    findings = []
    for root, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fname in files:
            fp = Path(root) / fname
            if fp.suffix in {'.pyc', '.so', '.o', '.bin', '.png', '.jpg', '.ico'}:
                continue
            if fp.name.startswith('.env'):
                continue  # .env files are expected to have secrets
            try:
                content = fp.read_text(errors='ignore')
            except Exception:
                continue
            for pattern, desc in SECRET_PATTERNS:
                for match in re.finditer(pattern, content):
                    rel = str(fp.relative_to(project_path))
                    line_num = content[:match.start()].count('\n') + 1
                    snippet = match.group()[:30] + "..."
                    findings.append((rel, line_num, desc, snippet))

    if findings:
        print(f"  {RED}⚠ Found {len(findings)} potential secrets in code:{RESET}\n")
        for fpath, line, desc, snippet in findings[:20]:
            print(f"  {RED}●{RESET} {fpath}:{line} — {desc}")
            print(f"    {DIM}{snippet}{RESET}")
        if len(findings) > 20:
            print(f"\n  {DIM}... and {len(findings)-20} more{RESET}")
    else:
        print(f"  {GREEN}✅ No secrets found in source code!{RESET}")
    print()


def cmd_list(project_path: Path):
    """List all env vars used in project."""
    print(f"\n{BOLD}📋 Environment Variables: {project_path.name}{RESET}\n")
    usage = find_env_usage(project_path)
    if not usage:
        print(f"  {DIM}No env vars found in code{RESET}\n")
        return
    for var in sorted(usage):
        files = usage[var]
        print(f"  {CYAN}{var}{RESET} → {DIM}{', '.join(files[:3])}{RESET}")
    print(f"\n  {DIM}Total: {len(usage)} unique variables{RESET}\n")


def main():
    args = sys.argv[1:]
    if not args or args[0] in ('--help', '-h', 'help'):
        print(__doc__)
        return

    cmd = args[0]

    # Parse --project flag
    project_path = Path.cwd()
    if '--project' in args:
        idx = args.index('--project')
        if idx + 1 < len(args):
            project_path = Path(args[idx + 1]).resolve()

    if cmd == 'check':
        cmd_check(project_path)
    elif cmd == 'compare':
        if len(args) < 3:
            print(f"{RED}Usage: mw env compare <file1> <file2>{RESET}")
            sys.exit(1)
        cmd_compare(Path(args[1]), Path(args[2]))
    elif cmd == 'template':
        cmd_template(project_path)
    elif cmd == 'secrets':
        cmd_secrets(project_path)
    elif cmd == 'list':
        cmd_list(project_path)
    else:
        print(f"{RED}Unknown command: {cmd}{RESET}")
        print(__doc__)
        sys.exit(1)


if __name__ == '__main__':
    main()
