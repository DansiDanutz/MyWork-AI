#!/usr/bin/env python3
"""
mw bench — Project Performance Benchmarking
============================================
Measures, tracks, and compares project performance metrics over time.

Usage:
    mw bench                    Run all benchmarks for current project
    mw bench run                Same as above
    mw bench history            Show benchmark history
    mw bench compare [ref]      Compare current vs previous (or git ref)
    mw bench ci                 CI-friendly output (exit 1 if regression)
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# ANSI colors
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"


def _detect_project_type(project_dir: str) -> str:
    """Detect project type from files."""
    p = Path(project_dir)
    if (p / "package.json").exists():
        return "node"
    if (p / "pyproject.toml").exists() or (p / "setup.py").exists():
        return "python"
    if (p / "Cargo.toml").exists():
        return "rust"
    if (p / "go.mod").exists():
        return "go"
    return "unknown"


def _time_command(cmd: List[str], cwd: str, timeout: int = 120) -> Optional[float]:
    """Run a command and return elapsed seconds, or None if failed."""
    try:
        start = time.monotonic()
        result = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout
        )
        elapsed = time.monotonic() - start
        if result.returncode == 0:
            return round(elapsed, 3)
        return None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def _count_files(project_dir: str) -> Dict[str, int]:
    """Count source files by type."""
    counts = {}
    p = Path(project_dir)
    skip = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".next", "target"}
    for f in p.rglob("*"):
        if any(s in f.parts for s in skip):
            continue
        if f.is_file():
            ext = f.suffix.lower()
            if ext in (".py", ".js", ".ts", ".tsx", ".jsx", ".rs", ".go", ".java", ".rb"):
                counts[ext] = counts.get(ext, 0) + 1
    return counts


def _get_dir_size_mb(path: str, skip: set = None) -> float:
    """Get directory size in MB, skipping certain dirs."""
    skip = skip or {".git", "node_modules", "__pycache__", ".venv", "target"}
    total = 0
    for f in Path(path).rglob("*"):
        if any(s in f.parts for s in skip):
            continue
        if f.is_file():
            total += f.stat().st_size
    return round(total / (1024 * 1024), 2)


def _get_dep_count(project_dir: str, ptype: str) -> int:
    """Count dependencies."""
    p = Path(project_dir)
    if ptype == "node":
        pkg = p / "package.json"
        if pkg.exists():
            try:
                data = json.loads(pkg.read_text())
                deps = len(data.get("dependencies", {}))
                dev = len(data.get("devDependencies", {}))
                return deps + dev
            except Exception:
                pass
    elif ptype == "python":
        req = p / "requirements.txt"
        if req.exists():
            return len([l for l in req.read_text().splitlines() if l.strip() and not l.startswith("#")])
    return 0


def _bench_history_path(project_dir: str) -> Path:
    """Get path for benchmark history file."""
    return Path(project_dir) / ".bench_history.json"


def _load_history(project_dir: str) -> List[dict]:
    """Load benchmark history."""
    hp = _bench_history_path(project_dir)
    if hp.exists():
        try:
            return json.loads(hp.read_text())
        except Exception:
            pass
    return []


def _save_history(project_dir: str, history: List[dict]):
    """Save benchmark history."""
    hp = _bench_history_path(project_dir)
    hp.write_text(json.dumps(history, indent=2))


def _get_git_ref(project_dir: str) -> str:
    """Get current git short hash."""
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=project_dir, capture_output=True, text=True
        )
        return r.stdout.strip() if r.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def run_benchmarks(project_dir: str = ".") -> dict:
    """Run all benchmarks and return results."""
    project_dir = os.path.abspath(project_dir)
    ptype = _detect_project_type(project_dir)
    results = {
        "timestamp": datetime.now().isoformat(),
        "git_ref": _get_git_ref(project_dir),
        "project_type": ptype,
        "metrics": {}
    }
    m = results["metrics"]

    # File counts
    m["file_counts"] = _count_files(project_dir)
    m["total_source_files"] = sum(m["file_counts"].values())

    # Project size
    m["project_size_mb"] = _get_dir_size_mb(project_dir)

    # Dependency count
    m["dependency_count"] = _get_dep_count(project_dir, ptype)

    # Lines of code (fast count)
    try:
        skip = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".next", "target"}
        loc = 0
        exts = {".py", ".js", ".ts", ".tsx", ".jsx", ".rs", ".go"}
        for f in Path(project_dir).rglob("*"):
            if any(s in f.parts for s in skip):
                continue
            if f.is_file() and f.suffix.lower() in exts:
                loc += len(f.read_text(errors="ignore").splitlines())
        m["lines_of_code"] = loc
    except Exception:
        m["lines_of_code"] = 0

    # Test speed
    if ptype == "python":
        m["test_time_s"] = _time_command(
            [sys.executable, "-m", "pytest", "-q", "--tb=no", "-x"], project_dir, timeout=60
        )
    elif ptype == "node":
        if (Path(project_dir) / "package.json").exists():
            pkg = json.loads((Path(project_dir) / "package.json").read_text())
            if "test" in pkg.get("scripts", {}):
                m["test_time_s"] = _time_command(["npm", "test", "--", "--passWithNoTests"], project_dir, timeout=60)

    # Build time (node only)
    if ptype == "node":
        pkg_path = Path(project_dir) / "package.json"
        if pkg_path.exists():
            pkg = json.loads(pkg_path.read_text())
            if "build" in pkg.get("scripts", {}):
                m["build_time_s"] = _time_command(["npm", "run", "build"], project_dir, timeout=120)

    # Import/startup time
    if ptype == "python":
        m["import_time_s"] = _time_command(
            [sys.executable, "-c", "import tools.mw"], project_dir, timeout=10
        )

    return results


def _format_delta(current, previous, unit="", lower_is_better=True):
    """Format a delta comparison."""
    if current is None or previous is None:
        return ""
    diff = current - previous
    pct = (diff / previous * 100) if previous != 0 else 0
    if abs(pct) < 1:
        return f" {DIM}(no change){RESET}"
    arrow = "↑" if diff > 0 else "↓"
    color = (RED if lower_is_better else GREEN) if diff > 0 else (GREEN if lower_is_better else RED)
    return f" {color}{arrow} {abs(pct):.1f}%{RESET}"


def cmd_bench(args: List[str] = None) -> int:
    """Main bench command."""
    args = args or []

    if not args or args[0] == "run":
        return _cmd_run(args[1:] if args and args[0] == "run" else args)
    elif args[0] == "history":
        return _cmd_history(args[1:])
    elif args[0] == "compare":
        return _cmd_compare(args[1:])
    elif args[0] == "ci":
        return _cmd_ci(args[1:])
    elif args[0] in ("--help", "-h", "help"):
        print(__doc__)
        return 0
    else:
        return _cmd_run(args)


def _cmd_run(args: List[str] = None) -> int:
    """Run benchmarks and display results."""
    project_dir = args[0] if args else "."
    print(f"\n{BOLD}{CYAN}⚡ Running benchmarks...{RESET}\n")

    results = run_benchmarks(project_dir)
    m = results["metrics"]

    # Save to history
    history = _load_history(project_dir)
    prev = history[-1]["metrics"] if history else {}
    history.append(results)
    # Keep last 50 entries
    if len(history) > 50:
        history = history[-50:]
    _save_history(project_dir, history)

    # Display
    print(f"  {BOLD}Project type:{RESET}  {results['project_type']}")
    print(f"  {BOLD}Git ref:{RESET}       {results['git_ref']}")
    print(f"  {BOLD}Timestamp:{RESET}     {results['timestamp'][:19]}")
    print()

    print(f"  {BOLD}📊 Metrics:{RESET}")
    print(f"    Source files:    {m['total_source_files']}{_format_delta(m['total_source_files'], prev.get('total_source_files'), lower_is_better=False)}")
    print(f"    Lines of code:   {m['lines_of_code']:,}{_format_delta(m['lines_of_code'], prev.get('lines_of_code'), lower_is_better=False)}")
    print(f"    Project size:    {m['project_size_mb']} MB{_format_delta(m['project_size_mb'], prev.get('project_size_mb'))}")
    print(f"    Dependencies:    {m['dependency_count']}{_format_delta(m['dependency_count'], prev.get('dependency_count'))}")

    if m.get("test_time_s") is not None:
        print(f"    Test time:       {m['test_time_s']:.2f}s{_format_delta(m['test_time_s'], prev.get('test_time_s'))}")
    if m.get("build_time_s") is not None:
        print(f"    Build time:      {m['build_time_s']:.2f}s{_format_delta(m['build_time_s'], prev.get('build_time_s'))}")
    if m.get("import_time_s") is not None:
        print(f"    Import time:     {m['import_time_s']:.3f}s{_format_delta(m['import_time_s'], prev.get('import_time_s'))}")

    if m.get("file_counts"):
        print(f"\n  {BOLD}📁 Files by type:{RESET}")
        for ext, count in sorted(m["file_counts"].items(), key=lambda x: -x[1]):
            print(f"    {ext:8s} {count}")

    print(f"\n  {GREEN}✅ Benchmark saved ({len(history)} total entries){RESET}\n")
    return 0


def _cmd_history(args: List[str] = None) -> int:
    """Show benchmark history."""
    project_dir = args[0] if args else "."
    history = _load_history(project_dir)

    if not history:
        print(f"\n  {YELLOW}No benchmark history found. Run: mw bench{RESET}\n")
        return 0

    print(f"\n{BOLD}{CYAN}📈 Benchmark History ({len(history)} entries){RESET}\n")
    print(f"  {'Date':<20s} {'Ref':<10s} {'Files':>6s} {'LOC':>8s} {'Size':>8s} {'Tests':>8s}")
    print(f"  {'─'*20} {'─'*10} {'─'*6} {'─'*8} {'─'*8} {'─'*8}")

    for entry in history[-15:]:
        m = entry["metrics"]
        ts = entry["timestamp"][:16]
        ref = entry.get("git_ref", "?")[:8]
        files = str(m.get("total_source_files", "?"))
        loc = f"{m.get('lines_of_code', 0):,}"
        size = f"{m.get('project_size_mb', 0):.1f}MB"
        test_t = f"{m['test_time_s']:.2f}s" if m.get("test_time_s") else "—"
        print(f"  {ts:<20s} {ref:<10s} {files:>6s} {loc:>8s} {size:>8s} {test_t:>8s}")

    print()
    return 0


def _cmd_compare(args: List[str] = None) -> int:
    """Compare current vs previous benchmark."""
    project_dir = "."
    history = _load_history(project_dir)

    if len(history) < 2:
        print(f"\n  {YELLOW}Need at least 2 benchmark runs to compare. Run: mw bench{RESET}\n")
        return 0

    curr = history[-1]["metrics"]
    prev = history[-2]["metrics"]

    print(f"\n{BOLD}{CYAN}🔍 Benchmark Comparison{RESET}")
    print(f"  {DIM}Previous: {history[-2].get('git_ref', '?')} ({history[-2]['timestamp'][:16]}){RESET}")
    print(f"  {DIM}Current:  {history[-1].get('git_ref', '?')} ({history[-1]['timestamp'][:16]}){RESET}\n")

    metrics = [
        ("Source files", "total_source_files", False),
        ("Lines of code", "lines_of_code", False),
        ("Project size (MB)", "project_size_mb", True),
        ("Dependencies", "dependency_count", True),
        ("Test time (s)", "test_time_s", True),
        ("Build time (s)", "build_time_s", True),
        ("Import time (s)", "import_time_s", True),
    ]

    for label, key, lower_better in metrics:
        c = curr.get(key)
        p = prev.get(key)
        if c is None and p is None:
            continue
        c_str = f"{c:,.2f}" if isinstance(c, float) else str(c or "—")
        p_str = f"{p:,.2f}" if isinstance(p, float) else str(p or "—")
        delta = _format_delta(c, p, lower_is_better=lower_better)
        print(f"  {label:<22s}  {p_str:>10s} → {c_str:>10s}{delta}")

    print()
    return 0


def _cmd_ci(args: List[str] = None) -> int:
    """CI mode — exit 1 if significant regressions detected."""
    project_dir = "."
    results = run_benchmarks(project_dir)
    history = _load_history(project_dir)

    if len(history) < 2:
        history.append(results)
        _save_history(project_dir, history)
        print("BENCH_OK: First run, no comparison available")
        return 0

    prev = history[-1]["metrics"]
    curr = results["metrics"]
    history.append(results)
    _save_history(project_dir, history)

    regressions = []
    # Check test time regression > 20%
    if curr.get("test_time_s") and prev.get("test_time_s"):
        pct = (curr["test_time_s"] - prev["test_time_s"]) / prev["test_time_s"] * 100
        if pct > 20:
            regressions.append(f"Test time regressed {pct:.1f}% ({prev['test_time_s']:.2f}s → {curr['test_time_s']:.2f}s)")

    # Check build time regression > 20%
    if curr.get("build_time_s") and prev.get("build_time_s"):
        pct = (curr["build_time_s"] - prev["build_time_s"]) / prev["build_time_s"] * 100
        if pct > 20:
            regressions.append(f"Build time regressed {pct:.1f}%")

    # Check project size grew > 30%
    if curr.get("project_size_mb") and prev.get("project_size_mb"):
        pct = (curr["project_size_mb"] - prev["project_size_mb"]) / prev["project_size_mb"] * 100
        if pct > 30:
            regressions.append(f"Project size grew {pct:.1f}%")

    if regressions:
        print(f"BENCH_FAIL: {len(regressions)} regression(s) detected:")
        for r in regressions:
            print(f"  ❌ {r}")
        return 1

    print("BENCH_OK: No significant regressions")
    return 0
