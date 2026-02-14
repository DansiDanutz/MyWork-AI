"""mw profile — Command profiler with CPU, memory, and I/O stats.

Usage:
    mw profile <command>           Profile a shell command
    mw profile --py <script>       Profile a Python script with cProfile
    mw profile --flame <command>   Generate flame graph data (requires py-spy)
"""

import os
import sys
import time
import json
import resource
import subprocess
import tempfile
from pathlib import Path

PROFILE_DIR = os.path.join(os.path.dirname(__file__), "..", ".mw", "profiles")


def ensure_dir():
    os.makedirs(PROFILE_DIR, exist_ok=True)


def profile_command(cmd, verbose=False):
    """Profile a shell command, returning resource usage stats."""
    start = time.monotonic()
    start_cpu = time.process_time()

    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=300
        )
        exit_code = result.returncode
        stdout = result.stdout
        stderr = result.stderr
    except subprocess.TimeoutExpired:
        return {"error": "Command timed out after 300s"}

    elapsed = time.monotonic() - start
    cpu_time = time.process_time() - start_cpu

    # Get resource usage of child
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)

    stats = {
        "command": cmd,
        "exit_code": exit_code,
        "wall_time_s": round(elapsed, 3),
        "user_cpu_s": round(usage.ru_utime, 3),
        "sys_cpu_s": round(usage.ru_stime, 3),
        "max_rss_mb": round(usage.ru_maxrss / 1024, 2),
        "voluntary_ctx_switches": usage.ru_nvcsw,
        "involuntary_ctx_switches": usage.ru_nivcsw,
        "page_faults": usage.ru_majflt,
        "block_input": usage.ru_inblock,
        "block_output": usage.ru_oublock,
        "stdout_lines": len(stdout.splitlines()),
        "stderr_lines": len(stderr.splitlines()),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }

    if verbose:
        stats["stdout"] = stdout[:2000]
        stats["stderr"] = stderr[:2000]

    return stats


def profile_python(script_path):
    """Profile a Python script using cProfile."""
    import cProfile
    import pstats
    import io

    if not os.path.exists(script_path):
        return {"error": f"File not found: {script_path}"}

    prof = cProfile.Profile()
    start = time.monotonic()

    try:
        prof.run(open(script_path).read())
    except Exception as e:
        return {"error": str(e)}

    elapsed = time.monotonic() - start

    stream = io.StringIO()
    ps = pstats.Stats(prof, stream=stream)
    ps.sort_stats("cumulative")
    ps.print_stats(20)

    return {
        "script": script_path,
        "wall_time_s": round(elapsed, 3),
        "total_calls": ps.total_calls,
        "top_functions": stream.getvalue(),
    }


def format_stats(stats):
    """Format stats as a readable table."""
    if "error" in stats:
        return f"❌ Error: {stats['error']}"

    if "top_functions" in stats:
        # Python profile
        lines = [
            f"🐍 Python Profile: {stats['script']}",
            f"   Wall time: {stats['wall_time_s']}s",
            f"   Total calls: {stats['total_calls']:,}",
            "",
            stats["top_functions"][:2000],
        ]
        return "\n".join(lines)

    # Command profile
    status = "✅" if stats["exit_code"] == 0 else "❌"
    lines = [
        f"{status} Profile: {stats['command']}",
        "",
        f"  ⏱  Wall time:    {stats['wall_time_s']}s",
        f"  🖥  User CPU:     {stats['user_cpu_s']}s",
        f"  ⚙️  System CPU:   {stats['sys_cpu_s']}s",
        f"  📊 Max RSS:      {stats['max_rss_mb']} MB",
        f"  🔄 Ctx switches: {stats['voluntary_ctx_switches']} vol / {stats['involuntary_ctx_switches']} invol",
        f"  📄 Output:       {stats['stdout_lines']} stdout / {stats['stderr_lines']} stderr lines",
    ]

    if stats["block_input"] or stats["block_output"]:
        lines.append(f"  💾 I/O blocks:   {stats['block_input']} in / {stats['block_output']} out")

    return "\n".join(lines)


def save_profile(stats):
    """Save profile results to history."""
    ensure_dir()
    ts = time.strftime("%Y%m%d_%H%M%S")
    name = stats.get("command", stats.get("script", "unknown"))
    safe_name = "".join(c if c.isalnum() else "_" for c in name[:30])
    path = os.path.join(PROFILE_DIR, f"{ts}_{safe_name}.json")
    with open(path, "w") as f:
        json.dump(stats, f, indent=2)
    return path


def show_history(limit=10):
    """Show recent profile history."""
    ensure_dir()
    files = sorted(Path(PROFILE_DIR).glob("*.json"), reverse=True)[:limit]
    if not files:
        print("No profile history. Run: mw profile <command>")
        return

    print(f"📊 Last {len(files)} profiles:\n")
    for f in files:
        data = json.loads(f.read_text())
        cmd = data.get("command", data.get("script", "?"))
        wt = data.get("wall_time_s", "?")
        rss = data.get("max_rss_mb", "?")
        ts = data.get("timestamp", f.stem[:15])
        status = "✅" if data.get("exit_code", 0) == 0 else "❌"
        print(f"  {status} {ts}  {wt}s  {rss}MB  {cmd[:50]}")


def show_help():
    print(__doc__)


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help", "help"):
        show_help()
        return

    if args[0] == "history":
        show_history(int(args[1]) if len(args) > 1 else 10)
        return

    verbose = "--verbose" in args or "-v" in args
    args = [a for a in args if a not in ("--verbose", "-v")]

    if args[0] == "--py":
        if len(args) < 2:
            print("Usage: mw profile --py <script.py>")
            return
        stats = profile_python(args[1])
    else:
        cmd = " ".join(args)
        stats = profile_command(cmd, verbose=verbose)

    print(format_stats(stats))
    path = save_profile(stats)
    print(f"\n💾 Saved to {path}")


if __name__ == "__main__":
    main()
