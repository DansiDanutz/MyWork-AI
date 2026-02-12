#!/usr/bin/env python3
"""MyWork Task Runner — Universal project task discovery and execution.

Usage:
    mw run                     List all discovered tasks
    mw run <task>              Run a named task
    mw run <task> -- <args>    Run task with extra arguments
    mw run add <name> <cmd>    Add a custom mw task
    mw run rm <name>           Remove a custom mw task

Discovers tasks from:
  - mw.tasks.json (custom MyWork tasks)
  - package.json scripts
  - Makefile targets
  - pyproject.toml [tool.taskipy.tasks] or [project.scripts]
  - Cargo.toml (build/run/test/bench)
  - Procfile entries

Tasks are displayed with source labels and can be run from any directory.
"""

import json
import os
import re
import subprocess
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ENDC = "\033[0m"


TASKS_FILE = "mw.tasks.json"


def _find_project_root() -> Path:
    """Walk up to find project root."""
    cwd = Path.cwd()
    markers = ["package.json", "pyproject.toml", "Cargo.toml", "Makefile", "mw.tasks.json", ".git"]
    for p in [cwd] + list(cwd.parents):
        if any((p / m).exists() for m in markers):
            return p
        if p == p.parent:
            break
    return cwd


def _discover_mw_tasks(root: Path) -> Dict[str, Tuple[str, str]]:
    """Discover tasks from mw.tasks.json. Returns {name: (command, source)}."""
    tasks = {}
    tf = root / TASKS_FILE
    if tf.exists():
        try:
            data = json.loads(tf.read_text())
            for name, entry in data.items():
                if isinstance(entry, str):
                    tasks[name] = (entry, "mw")
                elif isinstance(entry, dict):
                    tasks[name] = (entry.get("cmd", entry.get("command", "")), "mw")
        except (json.JSONDecodeError, AttributeError):
            pass
    return tasks


def _discover_npm_scripts(root: Path) -> Dict[str, Tuple[str, str]]:
    """Discover from package.json scripts."""
    tasks = {}
    pj = root / "package.json"
    if pj.exists():
        try:
            data = json.loads(pj.read_text())
            for name, cmd in data.get("scripts", {}).items():
                tasks[f"npm:{name}"] = (f"npm run {name}", "npm")
        except (json.JSONDecodeError, AttributeError):
            pass
    return tasks


def _discover_makefile(root: Path) -> Dict[str, Tuple[str, str]]:
    """Discover from Makefile."""
    tasks = {}
    mf = root / "Makefile"
    if mf.exists():
        content = mf.read_text()
        for match in re.finditer(r'^([a-zA-Z_][\w-]*)\s*:', content, re.MULTILINE):
            target = match.group(1)
            if target not in ("PHONY", "FORCE", "SHELL"):
                tasks[f"make:{target}"] = (f"make {target}", "make")
    return tasks


def _discover_pyproject(root: Path) -> Dict[str, Tuple[str, str]]:
    """Discover from pyproject.toml (taskipy or scripts)."""
    tasks = {}
    pp = root / "pyproject.toml"
    if pp.exists():
        content = pp.read_text()
        # Simple TOML parser for [tool.taskipy.tasks]
        in_taskipy = False
        for line in content.split("\n"):
            if "[tool.taskipy.tasks]" in line:
                in_taskipy = True
                continue
            if in_taskipy:
                if line.startswith("["):
                    break
                m = re.match(r'(\w+)\s*=\s*"(.+)"', line.strip())
                if m:
                    tasks[f"py:{m.group(1)}"] = (m.group(2), "taskipy")

        # [project.scripts]
        in_scripts = False
        for line in content.split("\n"):
            if "[project.scripts]" in line:
                in_scripts = True
                continue
            if in_scripts:
                if line.startswith("["):
                    break
                m = re.match(r'(\w[\w-]*)\s*=\s*"(.+)"', line.strip())
                if m:
                    tasks[f"py:{m.group(1)}"] = (m.group(2), "pyproject")
    return tasks


def _discover_cargo(root: Path) -> Dict[str, Tuple[str, str]]:
    """Discover Cargo tasks."""
    tasks = {}
    if (root / "Cargo.toml").exists():
        for cmd in ["build", "run", "test", "bench", "check", "clippy"]:
            tasks[f"cargo:{cmd}"] = (f"cargo {cmd}", "cargo")
    return tasks


def _discover_procfile(root: Path) -> Dict[str, Tuple[str, str]]:
    """Discover from Procfile."""
    tasks = {}
    pf = root / "Procfile"
    if pf.exists():
        for line in pf.read_text().strip().split("\n"):
            if ":" in line:
                name, cmd = line.split(":", 1)
                tasks[f"proc:{name.strip()}"] = (cmd.strip(), "procfile")
    return tasks


def _discover_all(root: Path) -> Dict[str, Tuple[str, str]]:
    """Discover all tasks, mw tasks take priority."""
    all_tasks = OrderedDict()
    # Priority order: mw > npm > make > pyproject > cargo > procfile
    for discoverer in [_discover_mw_tasks, _discover_npm_scripts, _discover_makefile,
                       _discover_pyproject, _discover_cargo, _discover_procfile]:
        all_tasks.update(discoverer(root))
    return all_tasks


def _list_tasks(root: Path) -> int:
    """List all discovered tasks."""
    tasks = _discover_all(root)
    if not tasks:
        print(f"\n{Colors.YELLOW}No tasks found.{Colors.ENDC}")
        print(f"  Create one: {Colors.GREEN}mw run add dev \"npm run dev\"{Colors.ENDC}")
        print(f"  Or add scripts to package.json, Makefile, etc.")
        return 0

    # Group by source
    sources = OrderedDict()
    for name, (cmd, source) in tasks.items():
        sources.setdefault(source, []).append((name, cmd))

    source_colors = {
        "mw": Colors.GREEN, "npm": Colors.RED, "make": Colors.BLUE,
        "taskipy": Colors.YELLOW, "pyproject": Colors.YELLOW,
        "cargo": Colors.MAGENTA, "procfile": Colors.CYAN,
    }

    print(f"\n{Colors.BOLD}⚡ Available Tasks{Colors.ENDC}  ({len(tasks)} total)")
    print(f"{'─' * 60}")

    for source, items in sources.items():
        color = source_colors.get(source, Colors.DIM)
        print(f"\n  {color}[{source}]{Colors.ENDC}")
        for name, cmd in items:
            # Show short name (strip prefix if it matches source)
            display = name.split(":", 1)[-1] if ":" in name else name
            truncated = cmd[:45] + "…" if len(cmd) > 45 else cmd
            print(f"    {Colors.BOLD}{display:<20}{Colors.ENDC} {Colors.DIM}{truncated}{Colors.ENDC}")

    print(f"\n  Run: {Colors.GREEN}mw run <task>{Colors.ENDC}")
    print()
    return 0


def _run_task(name: str, extra_args: List[str], root: Path) -> int:
    """Run a specific task."""
    tasks = _discover_all(root)

    # Exact match
    if name in tasks:
        cmd, source = tasks[name]
    else:
        # Try without prefix
        matches = [(k, v) for k, v in tasks.items() if k.split(":", 1)[-1] == name or k == name]
        if len(matches) == 1:
            cmd, source = matches[0][1]
            name = matches[0][0]
        elif len(matches) > 1:
            print(f"{Colors.YELLOW}⚠️  Ambiguous task '{name}'. Did you mean:{Colors.ENDC}")
            for k, (c, s) in matches:
                print(f"    {Colors.GREEN}{k}{Colors.ENDC} → {c}")
            return 1
        else:
            print(f"{Colors.RED}❌ Task '{name}' not found.{Colors.ENDC}")
            print(f"   Run {Colors.GREEN}mw run{Colors.ENDC} to see available tasks.")
            return 1

    if extra_args:
        cmd = f"{cmd} {' '.join(extra_args)}"

    source_emoji = {"mw": "⚡", "npm": "📦", "make": "🔨", "cargo": "🦀", "procfile": "🔧"}.get(source, "▶️")
    print(f"{source_emoji} Running {Colors.CYAN}{name}{Colors.ENDC} → {Colors.DIM}{cmd}{Colors.ENDC}\n")

    try:
        result = subprocess.run(cmd, shell=True, cwd=str(root))
        return result.returncode
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Interrupted.{Colors.ENDC}")
        return 130


def _add_task(name: str, cmd: str, root: Path) -> int:
    """Add a custom mw task."""
    tf = root / TASKS_FILE
    data = {}
    if tf.exists():
        try:
            data = json.loads(tf.read_text())
        except json.JSONDecodeError:
            pass

    data[name] = cmd
    tf.write_text(json.dumps(data, indent=2) + "\n")
    print(f"{Colors.GREEN}✅ Added task:{Colors.ENDC} {Colors.BOLD}{name}{Colors.ENDC} → {cmd}")
    return 0


def _rm_task(name: str, root: Path) -> int:
    """Remove a custom mw task."""
    tf = root / TASKS_FILE
    if not tf.exists():
        print(f"{Colors.RED}❌ No mw.tasks.json found{Colors.ENDC}")
        return 1
    data = json.loads(tf.read_text())
    if name not in data:
        print(f"{Colors.RED}❌ Task '{name}' not found{Colors.ENDC}")
        return 1
    del data[name]
    tf.write_text(json.dumps(data, indent=2) + "\n")
    print(f"{Colors.GREEN}✅ Removed task: {name}{Colors.ENDC}")
    return 0


def cmd_run(args: List[str] = None) -> int:
    """Main entry for mw run."""
    args = args or []
    root = _find_project_root()

    if not args or args[0] in ("-h", "--help", "help"):
        return _list_tasks(root)

    if args[0] == "add":
        if len(args) < 3:
            print(f"{Colors.RED}❌ Usage: mw run add <name> <command>{Colors.ENDC}")
            return 1
        return _add_task(args[1], " ".join(args[2:]), root)

    if args[0] == "rm":
        if len(args) < 2:
            print(f"{Colors.RED}❌ Usage: mw run rm <name>{Colors.ENDC}")
            return 1
        return _rm_task(args[1], root)

    # Split on -- for extra args
    task_name = args[0]
    extra = []
    if "--" in args:
        idx = args.index("--")
        extra = args[idx + 1:]

    return _run_task(task_name, extra, root)


if __name__ == "__main__":
    sys.exit(cmd_run(sys.argv[1:]))
