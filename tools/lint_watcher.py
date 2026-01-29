#!/usr/bin/env python3
"""
Lint Scheduler Manager - Control the scheduled linting runner
Part of the MyWork Framework

Usage:
    python tools/lint_watcher.py start    # Start scheduler in background
    python tools/lint_watcher.py stop     # Stop running scheduler
    python tools/lint_watcher.py status   # Check if running
    python tools/lint_watcher.py restart  # Restart scheduler
    python tools/lint_watcher.py logs     # Show recent logs
"""

import os
import sys
import time
import signal
import subprocess
from pathlib import Path

PID_FILE = Path(__file__).parent.parent / ".tmp" / "lint_scheduler.pid"
LOG_FILE = Path(__file__).parent.parent / ".tmp" / "lint_scheduler.log"
DEFAULT_INTERVAL = int(os.getenv("AUTO_LINT_INTERVAL_SECONDS", "14400"))


def get_pid():
    """Get the PID of the running agent"""
    if PID_FILE.exists():
        with open(PID_FILE, "r") as f:
            return int(f.read().strip())
    return None


def is_running(pid):
    """Check if a process is running"""
    if pid is None:
        return False
    try:
        os.kill(pid, 0)  # Signal 0 doesn't kill, just checks
        return True
    except OSError:
        return False


def start():
    """Start the lint scheduler in the background"""
    pid = get_pid()
    if pid and is_running(pid):
        print(f"✅ Lint scheduler is already running (PID: {pid})")
        return

    # Ensure .tmp directory exists
    PID_FILE.parent.mkdir(exist_ok=True)

    # Start the agent
    scheduler_script = Path(__file__).parent / "auto_lint_scheduler.py"
    project_root = Path(__file__).parent.parent

    print("🚀 Starting lint scheduler...")

    # Open log file
    log_handle = open(LOG_FILE, "a")

    process = subprocess.Popen(
        [
            "python3",
            str(scheduler_script),
            "--daemon",
            "--interval",
            str(DEFAULT_INTERVAL),
        ],
        cwd=str(project_root),
        stdout=log_handle,
        stderr=subprocess.STDOUT,
        start_new_session=True,  # Detach from parent
    )

    # Save PID
    with open(PID_FILE, "w") as f:
        f.write(str(process.pid))

    print(f"✅ Lint scheduler started (PID: {process.pid})")
    print(f"   Log file: {LOG_FILE}")
    print(f"   Monitor with: python tools/lint_watcher.py status")


def stop():
    """Stop the lint scheduler"""
    pid = get_pid()
    if not pid:
        print("⚠️  Lint scheduler is not running")
        return

    if not is_running(pid):
        print(f"⚠️  Process {pid} not found (stale PID file)")
        PID_FILE.unlink()
        return

    print(f"🛑 Stopping lint scheduler (PID: {pid})...")
    try:
        os.kill(pid, signal.SIGTERM)
        # Wait for process to terminate
        for _ in range(10):
            time.sleep(0.5)
            if not is_running(pid):
                break
        else:
            # Force kill if it won't stop
            os.kill(pid, signal.SIGKILL)
            time.sleep(0.5)

        PID_FILE.unlink(missing_ok=True)
        print("✅ Lint scheduler stopped")
    except Exception as e:
        print(f"❌ Error stopping lint scheduler: {e}")


def status():
    """Check the status of the lint scheduler"""
    pid = get_pid()
    if pid and is_running(pid):
        print(f"✅ Lint scheduler is RUNNING (PID: {pid})")

        # Check recent activity
        if LOG_FILE.exists():
            print(f"\n📝 Recent log entries:")
            result = subprocess.run(
                ["tail", "-10", str(LOG_FILE)],
                capture_output=True,
                text=True,
            )
            if result.stdout.strip():
                print(result.stdout)
            else:
                print("   (no recent activity)")
        return True
    else:
        print("⚠️  Lint scheduler is NOT running")
        if pid:
            print(f"   (stale PID file: {pid}, cleaning up)")
            PID_FILE.unlink(missing_ok=True)
        return False


def restart():
    """Restart the lint scheduler"""
    stop()
    time.sleep(1)
    start()


def logs():
    """Show the logs"""
    if not LOG_FILE.exists():
        print("📝 No log file found")
        return

    print(f"📝 Log file: {LOG_FILE}")
    print("=" * 60)
    subprocess.run(["tail", "-50", str(LOG_FILE)])


def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        print("Lint Scheduler Manager - MyWork Framework")
        print("\nUsage:")
        print("  python tools/lint_watcher.py start    # Start scheduler in background")
        print("  python tools/lint_watcher.py stop     # Stop running scheduler")
        print("  python tools/lint_watcher.py status   # Check if running")
        print("  python tools/lint_watcher.py restart  # Restart scheduler")
        print("  python tools/lint_watcher.py logs     # Show recent logs")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "start":
        start()
    elif command == "stop":
        stop()
    elif command == "status":
        status()
    elif command == "restart":
        restart()
    elif command == "logs":
        logs()
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
