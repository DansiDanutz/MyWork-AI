#!/usr/bin/env python3
"""
Metrics Tracker — Track project health metrics over time.

Usage:
    mw metrics              Show current metrics snapshot
    mw metrics history      Show metrics history with trends
    mw metrics record       Record current metrics to history
    mw metrics chart        ASCII chart of key metrics over time
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

MYWORK_ROOT = Path(__file__).parent.parent
METRICS_FILE = MYWORK_ROOT / ".metrics" / "history.json"


def _run(cmd, cwd=None):
    """Run a command and return stdout."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd or MYWORK_ROOT, timeout=10)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def collect_metrics() -> dict:
    """Collect current project metrics."""
    metrics = {"timestamp": datetime.utcnow().isoformat() + "Z"}

    # Lines of code (Python only, excluding __pycache__ and .git)
    loc_output = _run(["find", ".", "-name", "*.py", "-not", "-path", "./.git/*",
                        "-not", "-path", "./__pycache__/*", "-not", "-path", "./.venv/*",
                        "-exec", "cat", "{}", "+"])
    metrics["python_loc"] = len(loc_output.splitlines()) if loc_output else 0

    # Number of Python files
    py_files = _run(["find", ".", "-name", "*.py", "-not", "-path", "./.git/*",
                      "-not", "-path", "./__pycache__/*", "-not", "-path", "./.venv/*"])
    metrics["python_files"] = len(py_files.splitlines()) if py_files else 0

    # Test count
    test_output = _run(["python3", "-m", "pytest", "--collect-only", "-q"], cwd=MYWORK_ROOT)
    for line in test_output.splitlines():
        if "test" in line and "selected" in line:
            try:
                metrics["test_count"] = int(line.split()[0])
            except (ValueError, IndexError):
                pass
    metrics.setdefault("test_count", 0)

    # Git stats
    commit_count = _run(["git", "rev-list", "--count", "HEAD"])
    metrics["total_commits"] = int(commit_count) if commit_count.isdigit() else 0

    # Commits in last 7 days
    recent = _run(["git", "rev-list", "--count", "--since=7 days ago", "HEAD"])
    metrics["commits_7d"] = int(recent) if recent.isdigit() else 0

    # Number of mw commands (rough count from mw.py)
    mw_py = MYWORK_ROOT / "tools" / "mw.py"
    if mw_py.exists():
        content = mw_py.read_text()
        metrics["mw_commands"] = content.count("def cmd_")

    # Requirements count
    req_file = MYWORK_ROOT / "requirements.txt"
    if req_file.exists():
        lines = [l.strip() for l in req_file.read_text().splitlines() if l.strip() and not l.startswith("#")]
        metrics["dependencies"] = len(lines)

    return metrics


def load_history() -> list:
    """Load metrics history."""
    if METRICS_FILE.exists():
        try:
            return json.loads(METRICS_FILE.read_text())
        except Exception:
            return []
    return []


def save_history(history: list):
    """Save metrics history."""
    METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
    METRICS_FILE.write_text(json.dumps(history, indent=2))


def record_metrics():
    """Record current metrics to history."""
    history = load_history()
    current = collect_metrics()
    history.append(current)
    # Keep last 365 entries
    history = history[-365:]
    save_history(history)
    return current


def format_trend(current, previous, key):
    """Format a trend indicator."""
    if key not in previous:
        return ""
    diff = current.get(key, 0) - previous.get(key, 0)
    if diff > 0:
        return f" \033[92m▲+{diff}\033[0m"
    elif diff < 0:
        return f" \033[91m▼{diff}\033[0m"
    return " →"


def show_current(metrics=None):
    """Display current metrics."""
    m = metrics or collect_metrics()
    history = load_history()
    prev = history[-1] if history else {}

    print("\033[1m\033[94m╔══════════════════════════════════════╗\033[0m")
    print("\033[1m\033[94m║     📊 MyWork-AI Project Metrics     ║\033[0m")
    print("\033[1m\033[94m╚══════════════════════════════════════╝\033[0m")
    print()

    items = [
        ("Python LoC", "python_loc", ""),
        ("Python Files", "python_files", ""),
        ("Test Count", "test_count", ""),
        ("Total Commits", "total_commits", ""),
        ("Commits (7d)", "commits_7d", ""),
        ("CLI Commands", "mw_commands", ""),
        ("Dependencies", "dependencies", ""),
    ]

    for label, key, suffix in items:
        val = m.get(key, "N/A")
        trend = format_trend(m, prev, key) if prev else ""
        print(f"  \033[1m{label:.<25}\033[0m {val:>8}{suffix}{trend}")

    print(f"\n  \033[90mRecorded: {m.get('timestamp', 'now')}\033[0m")
    if history:
        print(f"  \033[90mHistory entries: {len(history)}\033[0m")


def show_history():
    """Show metrics history with trends."""
    history = load_history()
    if not history:
        print("No metrics history yet. Run 'mw metrics record' first.")
        return

    print("\033[1m📈 Metrics History (last 10 entries)\033[0m\n")
    print(f"  {'Date':<22} {'LoC':>7} {'Tests':>6} {'Commits':>8} {'7d':>5}")
    print(f"  {'─'*22} {'─'*7} {'─'*6} {'─'*8} {'─'*5}")

    for entry in history[-10:]:
        ts = entry.get("timestamp", "?")[:16].replace("T", " ")
        loc = entry.get("python_loc", "?")
        tests = entry.get("test_count", "?")
        commits = entry.get("total_commits", "?")
        c7d = entry.get("commits_7d", "?")
        print(f"  {ts:<22} {loc:>7} {tests:>6} {commits:>8} {c7d:>5}")


def show_chart():
    """ASCII sparkline chart of key metrics."""
    history = load_history()
    if len(history) < 2:
        print("Need at least 2 data points. Run 'mw metrics record' a few times.")
        return

    def sparkline(values):
        if not values:
            return ""
        mn, mx = min(values), max(values)
        rng = mx - mn if mx != mn else 1
        chars = "▁▂▃▄▅▆▇█"
        return "".join(chars[min(int((v - mn) / rng * 7), 7)] for v in values)

    print("\033[1m📊 Metrics Trends\033[0m\n")
    for label, key in [("LoC", "python_loc"), ("Tests", "test_count"), ("Commits", "total_commits")]:
        values = [e.get(key, 0) for e in history[-30:]]
        first, last = values[0], values[-1]
        spark = sparkline(values)
        diff = last - first
        sign = "+" if diff >= 0 else ""
        print(f"  {label:<10} {spark}  {last} ({sign}{diff})")


def cmd_metrics(args=None):
    """Entry point for mw metrics command."""
    args = args or []

    if args and args[0] in ("--help", "-h"):
        print(__doc__)
        return 0

    subcmd = args[0] if args else "show"

    if subcmd == "record":
        m = record_metrics()
        print(f"\033[92m✅ Metrics recorded at {m['timestamp']}\033[0m")
        show_current(m)
        return 0
    elif subcmd == "history":
        show_history()
        return 0
    elif subcmd == "chart":
        show_chart()
        return 0
    else:
        show_current()
        return 0
