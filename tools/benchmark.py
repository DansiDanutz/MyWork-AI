#!/usr/bin/env python3
"""mw bench — Performance benchmarking for MyWork-AI CLI and projects.

Measures startup time, command latency, and project build performance.
Outputs a clean report with historical tracking.
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

MYWORK_ROOT = Path(__file__).resolve().parent.parent
BENCH_DIR = MYWORK_ROOT / ".benchmarks"
BENCH_DIR.mkdir(exist_ok=True)

# ANSI colors
G = "\033[92m"
Y = "\033[93m"
R = "\033[91m"
B = "\033[94m"
C = "\033[96m"
BOLD = "\033[1m"
END = "\033[0m"


def _time_cmd(cmd: list[str], cwd: str = None, timeout: int = 30) -> dict:
    """Time a command execution. Returns dict with duration, success, output."""
    start = time.perf_counter()
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
            cwd=cwd or str(MYWORK_ROOT)
        )
        elapsed = time.perf_counter() - start
        return {
            "cmd": " ".join(cmd),
            "duration_ms": round(elapsed * 1000, 1),
            "success": result.returncode == 0,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        elapsed = time.perf_counter() - start
        return {
            "cmd": " ".join(cmd),
            "duration_ms": round(elapsed * 1000, 1),
            "success": False,
            "returncode": -1,
            "error": "timeout",
        }
    except Exception as e:
        elapsed = time.perf_counter() - start
        return {
            "cmd": " ".join(cmd),
            "duration_ms": round(elapsed * 1000, 1),
            "success": False,
            "returncode": -1,
            "error": str(e),
        }


def _rating(ms: float, good: float, ok: float) -> str:
    """Return colored rating based on thresholds."""
    if ms <= good:
        return f"{G}⚡ fast{END}"
    elif ms <= ok:
        return f"{Y}⏱ ok{END}"
    else:
        return f"{R}🐢 slow{END}"


def bench_startup() -> list[dict]:
    """Benchmark CLI startup/help times."""
    print(f"\n{BOLD}🚀 CLI Startup Benchmarks{END}\n")
    benchmarks = []

    tests = [
        (["python3", str(MYWORK_ROOT / "tools" / "mw.py"), "--help"], "mw --help", 500, 2000),
        (["python3", str(MYWORK_ROOT / "tools" / "mw.py"), "status"], "mw status", 1000, 3000),
        (["python3", "-c", "import tools.mw"], "Python import", 500, 1500),
    ]

    for cmd, label, good, ok in tests:
        # Warm up once
        _time_cmd(cmd, timeout=15)
        # Actual measurement (avg of 3)
        times = []
        for _ in range(3):
            r = _time_cmd(cmd, timeout=15)
            times.append(r["duration_ms"])
        avg = round(sum(times) / len(times), 1)
        rating = _rating(avg, good, ok)
        print(f"  {label:25s} {avg:8.1f}ms  {rating}")
        benchmarks.append({"label": label, "avg_ms": avg, "runs": times})

    return benchmarks


def bench_commands() -> list[dict]:
    """Benchmark key mw commands."""
    print(f"\n{BOLD}⚙️  Command Benchmarks{END}\n")
    benchmarks = []
    mw = str(MYWORK_ROOT / "tools" / "mw.py")

    tests = [
        (["python3", mw, "ecosystem"], "mw ecosystem", 1000, 3000),
        (["python3", mw, "links"], "mw links", 500, 1500),
        (["python3", mw, "changelog"], "mw changelog", 2000, 5000),
        (["python3", mw, "ci", "status"], "mw ci status", 3000, 8000),
        (["python3", mw, "scan"], "mw scan", 2000, 5000),
    ]

    for cmd, label, good, ok in tests:
        r = _time_cmd(cmd, timeout=20)
        ms = r["duration_ms"]
        status = f"{G}✓{END}" if r["success"] else f"{R}✗{END}"
        rating = _rating(ms, good, ok)
        print(f"  {status} {label:25s} {ms:8.1f}ms  {rating}")
        benchmarks.append({"label": label, "ms": ms, "success": r["success"]})

    return benchmarks


def bench_python() -> dict:
    """Benchmark Python environment."""
    print(f"\n{BOLD}🐍 Python Environment{END}\n")
    r = _time_cmd(["python3", "-c", "print('ok')"], timeout=5)
    print(f"  Python startup:        {r['duration_ms']:8.1f}ms")

    r2 = _time_cmd(["python3", "-c", "import json, os, sys, subprocess, pathlib; print('ok')"], timeout=5)
    print(f"  Stdlib imports:        {r2['duration_ms']:8.1f}ms")

    return {"startup_ms": r["duration_ms"], "imports_ms": r2["duration_ms"]}


def bench_git() -> dict:
    """Benchmark git operations."""
    print(f"\n{BOLD}📦 Git Performance{END}\n")
    results = {}

    for cmd, label in [
        (["git", "status", "--porcelain"], "git status"),
        (["git", "log", "--oneline", "-20"], "git log -20"),
        (["git", "diff", "--stat", "HEAD~5"], "git diff HEAD~5"),
    ]:
        r = _time_cmd(cmd, timeout=10)
        ms = r["duration_ms"]
        rating = _rating(ms, 200, 1000)
        print(f"  {label:25s} {ms:8.1f}ms  {rating}")
        results[label] = ms

    return results


def save_results(data: dict) -> Path:
    """Save benchmark results to JSON."""
    ts = datetime.now(tz=__import__("datetime").timezone.utc).strftime("%Y%m%d_%H%M%S")
    out = BENCH_DIR / f"bench_{ts}.json"
    data["timestamp"] = datetime.now(tz=__import__("datetime").timezone.utc).isoformat()
    with open(out, "w") as f:
        json.dump(data, f, indent=2)
    return out


def show_history():
    """Show benchmark history trend."""
    files = sorted(BENCH_DIR.glob("bench_*.json"))
    if not files:
        print(f"\n{Y}No benchmark history yet. Run: mw bench{END}")
        return

    print(f"\n{BOLD}📈 Benchmark History (last 10 runs){END}\n")
    print(f"  {'Date':20s} {'mw --help':>12s} {'mw status':>12s} {'mw ecosystem':>14s}")
    print(f"  {'─'*20} {'─'*12} {'─'*12} {'─'*14}")

    for f in files[-10:]:
        try:
            d = json.loads(f.read_text())
            ts = d.get("timestamp", "?")[:16].replace("T", " ")
            startup = next((b["avg_ms"] for b in d.get("startup", []) if b["label"] == "mw --help"), "—")
            status = next((b["avg_ms"] for b in d.get("startup", []) if b["label"] == "mw status"), "—")
            eco = next((b["ms"] for b in d.get("commands", []) if b["label"] == "mw ecosystem"), "—")
            fmt = lambda v: f"{v:>10.1f}ms" if isinstance(v, (int, float)) else f"{v:>12s}"
            print(f"  {ts:20s} {fmt(startup)} {fmt(status)} {fmt(eco)}")
        except Exception:
            pass


def cmd_benchmark(args: list[str] = None) -> int:
    """Main entry point for mw bench."""
    args = args or []

    if args and args[0] in ["--help", "-h"]:
        print(f"""
{BOLD}🏎️  mw bench — Performance Benchmarking{END}

Usage:
    mw bench              Run full benchmark suite
    mw bench quick        Quick startup-only benchmark
    mw bench history      Show historical benchmark trends
    mw bench --help       Show this help

Measures CLI startup, command latency, Python env, and git performance.
Results saved to .benchmarks/ for trend tracking.
""")
        return 0

    if args and args[0] == "history":
        show_history()
        return 0

    print(f"\n{BOLD}{C}{'═'*60}{END}")
    print(f"{BOLD}{C}  🏎️  MyWork-AI Performance Benchmark{END}")
    print(f"{BOLD}{C}{'═'*60}{END}")

    results = {}

    results["startup"] = bench_startup()
    
    if not (args and args[0] == "quick"):
        results["commands"] = bench_commands()
        results["python"] = bench_python()
        results["git"] = bench_git()

    out = save_results(results)

    # Summary
    print(f"\n{BOLD}{'─'*60}{END}")
    total_tests = len(results.get("startup", [])) + len(results.get("commands", []))
    print(f"  {G}✅ {total_tests} benchmarks completed{END}")
    print(f"  📁 Results: {out}")
    print(f"  📈 History: {B}mw bench history{END}\n")

    return 0


if __name__ == "__main__":
    sys.exit(cmd_benchmark(sys.argv[1:]))
