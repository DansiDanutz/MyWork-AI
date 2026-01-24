#!/usr/bin/env python3
"""
Autocoder Service Manager
=========================
Manages the Autocoder server as a macOS LaunchAgent service.

The service runs automatically on login and restarts if it crashes.

Usage:
    python tools/autocoder_service.py install   # Install and start service
    python tools/autocoder_service.py start     # Start service
    python tools/autocoder_service.py stop      # Stop service
    python tools/autocoder_service.py restart   # Restart service
    python tools/autocoder_service.py status    # Check service status
    python tools/autocoder_service.py logs      # View logs
    python tools/autocoder_service.py uninstall # Remove service
"""

import os
import sys
import subprocess
import argparse
import time
import plistlib
from pathlib import Path

# Configuration - Import from shared config with fallback
try:
    from config import MYWORK_ROOT, TMP_DIR, AUTOCODER_ROOT as AUTOCODER_PATH
    LOG_PATH = TMP_DIR / "autocoder.log"
    ERROR_LOG_PATH = TMP_DIR / "autocoder.error.log"
except ImportError:
    def _get_mywork_root():
        if env_root := os.environ.get("MYWORK_ROOT"):
            return Path(env_root)
        script_dir = Path(__file__).resolve().parent
        return script_dir.parent if script_dir.name == "tools" else Path.home() / "MyWork"
    MYWORK_ROOT = _get_mywork_root()
    LOG_PATH = MYWORK_ROOT / ".tmp" / "autocoder.log"
    ERROR_LOG_PATH = MYWORK_ROOT / ".tmp" / "autocoder.error.log"
    AUTOCODER_PATH = Path(os.environ.get("AUTOCODER_ROOT", Path.home() / "GamesAI" / "autocoder"))

SERVICE_NAME = "com.mywork.autocoder"
PLIST_PATH = Path.home() / "Library/LaunchAgents" / f"{SERVICE_NAME}.plist"
SERVER_URL = "http://127.0.0.1:8888"

def get_autocoder_python() -> str:
    """Prefer Autocoder venv python when available."""
    candidates = [
        AUTOCODER_PATH / "venv" / "bin" / "python",
        AUTOCODER_PATH / ".venv" / "bin" / "python",
        AUTOCODER_PATH / "venv" / "Scripts" / "python.exe",
        AUTOCODER_PATH / ".venv" / "Scripts" / "python.exe",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return sys.executable

def generate_plist() -> dict:
    """Generate LaunchAgent plist content."""
    python_bin = get_autocoder_python()
    start_script = AUTOCODER_PATH / "start_ui.py"
    return {
        "Label": SERVICE_NAME,
        "ProgramArguments": [python_bin, str(start_script)],
        "WorkingDirectory": str(AUTOCODER_PATH),
        "RunAtLoad": True,
        "KeepAlive": True,
        "StandardOutPath": str(LOG_PATH),
        "StandardErrorPath": str(ERROR_LOG_PATH),
        "EnvironmentVariables": {
            "MYWORK_ROOT": str(MYWORK_ROOT),
            "AUTOCODER_ROOT": str(AUTOCODER_PATH),
        },
    }

def setup():
    """Create or update the LaunchAgent plist."""
    if sys.platform != "darwin":
        print("ERROR: Autocoder service uses macOS LaunchAgents.")
        print("Run Autocoder manually on this platform.")
        return False

    if not AUTOCODER_PATH.exists():
        print(f"ERROR: Autocoder not found at {AUTOCODER_PATH}")
        return False

    start_script = AUTOCODER_PATH / "start_ui.py"
    if not start_script.exists():
        print(f"ERROR: Autocoder start script missing at {start_script}")
        return False

    PLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
    plist_data = generate_plist()
    with open(PLIST_PATH, "wb") as f:
        plistlib.dump(plist_data, f)

    print(f"Created plist: {PLIST_PATH}")
    print(f"Uses python: {plist_data['ProgramArguments'][0]}")
    return True


def run_cmd(cmd: list, check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def is_loaded() -> bool:
    """Check if the service is loaded."""
    result = run_cmd(["launchctl", "list"], check=False)
    return SERVICE_NAME in result.stdout


def is_running() -> bool:
    """Check if the server is actually responding."""
    try:
        import httpx
        response = httpx.get(f"{SERVER_URL}/health", timeout=5.0)
        return response.status_code == 200
    except:
        return False


def get_pid() -> int | None:
    """Get the PID of the running service."""
    result = run_cmd(["launchctl", "list", SERVICE_NAME], check=False)
    if result.returncode == 0:
        lines = result.stdout.strip().split('\n')
        for line in lines:
            parts = line.split('\t')
            if len(parts) >= 1 and parts[0].isdigit():
                return int(parts[0])
    return None


def install():
    """Install and load the service."""
    if not PLIST_PATH.exists():
        print("Plist file missing; generating now...")
        if not setup():
            return False

    # Ensure log directory exists
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Load the service
    if is_loaded():
        print("Service already loaded. Restarting...")
        run_cmd(["launchctl", "unload", str(PLIST_PATH)], check=False)

    result = run_cmd(["launchctl", "load", str(PLIST_PATH)], check=False)
    if result.returncode != 0:
        print(f"ERROR loading service: {result.stderr}")
        return False

    print("Service installed and started.")
    print("Waiting for server to start", end="")

    for _ in range(30):
        time.sleep(1)
        print(".", end="", flush=True)
        if is_running():
            print(f"\n\nAutocoder server is RUNNING at {SERVER_URL}")
            return True

    print("\n\nWARNING: Server may not have started. Check logs with:")
    print(f"  python tools/autocoder_service.py logs")
    return False


def start():
    """Start the service."""
    if not PLIST_PATH.exists():
        print("Service not installed. Installing first...")
        return install()

    if is_loaded():
        print("Service is already loaded.")
        if is_running():
            print(f"Server is RUNNING at {SERVER_URL}")
        else:
            print("Server not responding. Restarting...")
            return restart()
        return True

    result = run_cmd(["launchctl", "load", str(PLIST_PATH)], check=False)
    if result.returncode != 0:
        print(f"ERROR: {result.stderr}")
        return False

    print("Service started.")
    return True


def stop():
    """Stop the service."""
    if not is_loaded():
        print("Service is not running.")
        return True

    result = run_cmd(["launchctl", "unload", str(PLIST_PATH)], check=False)
    if result.returncode != 0:
        print(f"ERROR: {result.stderr}")
        return False

    print("Service stopped.")
    return True


def restart():
    """Restart the service."""
    stop()
    time.sleep(2)
    return start()


def status():
    """Show service status."""
    loaded = is_loaded()
    running = is_running()
    pid = get_pid() if loaded else None

    print("=" * 50)
    print("Autocoder Service Status")
    print("=" * 50)
    print(f"Service Name:   {SERVICE_NAME}")
    print(f"Plist Path:     {PLIST_PATH}")
    print(f"Server URL:     {SERVER_URL}")
    print("-" * 50)
    print(f"Service Loaded: {'Yes' if loaded else 'No'}")
    print(f"Server Running: {'Yes' if running else 'No'}")
    if pid:
        print(f"Process ID:     {pid}")
    print("-" * 50)

    if loaded and running:
        print("STATUS: HEALTHY")
    elif loaded and not running:
        print("STATUS: LOADED BUT NOT RESPONDING")
        print("Try: python tools/autocoder_service.py restart")
    else:
        print("STATUS: NOT RUNNING")
        print("Try: python tools/autocoder_service.py install")


def logs(follow: bool = False, lines: int = 50):
    """View service logs."""
    if not LOG_PATH.exists() and not ERROR_LOG_PATH.exists():
        print("No logs found yet. Service may not have started.")
        return

    if follow:
        print(f"Following logs (Ctrl+C to exit)...")
        try:
            subprocess.run(["tail", "-f", str(LOG_PATH), str(ERROR_LOG_PATH)])
        except KeyboardInterrupt:
            print("\nStopped following logs.")
    else:
        print(f"=== Last {lines} lines of output log ===")
        if LOG_PATH.exists():
            subprocess.run(["tail", f"-{lines}", str(LOG_PATH)])

        print(f"\n=== Last {lines} lines of error log ===")
        if ERROR_LOG_PATH.exists():
            subprocess.run(["tail", f"-{lines}", str(ERROR_LOG_PATH)])


def uninstall():
    """Uninstall the service."""
    if is_loaded():
        stop()

    if PLIST_PATH.exists():
        PLIST_PATH.unlink()
        print(f"Removed plist file: {PLIST_PATH}")

    print("Service uninstalled.")


def main():
    parser = argparse.ArgumentParser(
        description="Autocoder Service Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  setup     Create or update the LaunchAgent plist
  install   Install and start the service (runs on login)
  start     Start the service
  stop      Stop the service
  restart   Restart the service
  status    Show service status
  logs      View service logs
  uninstall Remove the service

Examples:
  python tools/autocoder_service.py setup     # Generate plist
  python tools/autocoder_service.py install   # First time setup
  python tools/autocoder_service.py status    # Check if running
  python tools/autocoder_service.py logs -f   # Follow logs live
"""
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("setup", help="Create or update plist")
    subparsers.add_parser("install", help="Install and start service")
    subparsers.add_parser("start", help="Start service")
    subparsers.add_parser("stop", help="Stop service")
    subparsers.add_parser("restart", help="Restart service")
    subparsers.add_parser("status", help="Show status")
    subparsers.add_parser("uninstall", help="Remove service")

    logs_parser = subparsers.add_parser("logs", help="View logs")
    logs_parser.add_argument("-f", "--follow", action="store_true", help="Follow logs")
    logs_parser.add_argument("-n", "--lines", type=int, default=50, help="Number of lines")

    args = parser.parse_args()

    if args.command == "install":
        install()
    elif args.command == "setup":
        setup()
    elif args.command == "start":
        start()
    elif args.command == "stop":
        stop()
    elif args.command == "restart":
        restart()
    elif args.command == "status":
        status()
    elif args.command == "uninstall":
        uninstall()
    elif args.command == "logs":
        logs(follow=args.follow, lines=args.lines)


if __name__ == "__main__":
    main()
