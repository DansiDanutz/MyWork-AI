#!/usr/bin/env python3
"""
Auto-Update System for MyWork Framework
========================================
Safely updates GSD, Autocoder, n8n-skills, and n8n-mcp without breaking the system.

Usage:
    python auto_update.py check          # Check for available updates
    python auto_update.py update [component]  # Update specific or all components
    python auto_update.py status         # Show current versions
    python auto_update.py rollback [component]  # Rollback to previous version

Components: gsd, autocoder, n8n-skills, n8n-mcp, all
"""

import os
import sys
import json
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

# Configuration
MYWORK_ROOT = Path("/Users/dansidanutz/Desktop/MyWork")
BACKUP_DIR = MYWORK_ROOT / ".backups"
UPDATE_LOG = MYWORK_ROOT / ".tmp" / "update.log"
VERSION_CACHE = MYWORK_ROOT / ".tmp" / "versions.json"

# Component paths
COMPONENTS = {
    "gsd": {
        "path": Path.home() / ".claude" / "commands" / "gsd",
        "type": "git",
        "remote": "origin",
        "branch": "main",
        "version_file": "version.json",
        "pre_update": None,
        "post_update": None,
    },
    "autocoder": {
        "path": Path("/Users/dansidanutz/Desktop/GamesAI/autocoder"),
        "type": "git",
        "remote": "origin",
        "branch": "master",
        "version_file": None,  # Uses git commit hash
        "pre_update": "check_autocoder_running",
        "post_update": "rebuild_autocoder_ui",
    },
    "n8n-skills": {
        "path": Path.home() / ".claude" / "skills" / "n8n-skills",
        "type": "git",
        "remote": "origin",
        "branch": "main",
        "version_file": None,
        "pre_update": None,
        "post_update": None,
    },
    "n8n-mcp": {
        "path": None,  # npx handles this
        "type": "npx",
        "package": "n8n-mcp",
        "pre_update": None,
        "post_update": None,
    },
}


class Logger:
    """Simple logger for update operations."""

    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().isoformat()
        entry = f"[{timestamp}] [{level}] {message}"
        print(entry)
        with open(self.log_file, "a") as f:
            f.write(entry + "\n")

    def info(self, message: str):
        self.log(message, "INFO")

    def error(self, message: str):
        self.log(message, "ERROR")

    def success(self, message: str):
        self.log(message, "SUCCESS")

    def warning(self, message: str):
        self.log(message, "WARNING")


logger = Logger(UPDATE_LOG)


def run_command(cmd: list, cwd: Optional[Path] = None, capture: bool = True) -> Tuple[bool, str]:
    """Run a shell command and return success status and output."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=capture,
            text=True,
            timeout=300  # 5 minute timeout
        )
        output = result.stdout + result.stderr if capture else ""
        return result.returncode == 0, output.strip()
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)


def get_git_info(path: Path) -> Dict[str, str]:
    """Get current git information for a repository."""
    if not path.exists() or not (path / ".git").exists():
        return {"error": "Not a git repository"}

    info = {}

    # Current commit
    success, output = run_command(["git", "rev-parse", "HEAD"], cwd=path)
    info["current_commit"] = output[:8] if success else "unknown"

    # Current branch
    success, output = run_command(["git", "branch", "--show-current"], cwd=path)
    info["branch"] = output if success else "unknown"

    # Last commit message
    success, output = run_command(["git", "log", "-1", "--pretty=%s"], cwd=path)
    info["last_message"] = output[:50] if success else "unknown"

    # Last commit date
    success, output = run_command(["git", "log", "-1", "--pretty=%cr"], cwd=path)
    info["last_date"] = output if success else "unknown"

    # Check for updates
    run_command(["git", "fetch", "--quiet"], cwd=path)
    success, output = run_command(["git", "rev-parse", "HEAD"], cwd=path)
    local = output if success else ""

    success, output = run_command(["git", "rev-parse", "@{u}"], cwd=path)
    remote = output if success else ""

    info["has_updates"] = local != remote if local and remote else False

    if info["has_updates"]:
        success, output = run_command(
            ["git", "log", "--oneline", "HEAD..@{u}"],
            cwd=path
        )
        info["pending_commits"] = len(output.split("\n")) if success and output else 0
    else:
        info["pending_commits"] = 0

    return info


def get_npx_info(package: str) -> Dict[str, str]:
    """Get npm package version info."""
    info = {}

    # Check installed version
    success, output = run_command(["npm", "list", "-g", package, "--json"])
    if success:
        try:
            data = json.loads(output)
            deps = data.get("dependencies", {})
            if package in deps:
                info["installed_version"] = deps[package].get("version", "unknown")
            else:
                info["installed_version"] = "not installed globally"
        except json.JSONDecodeError:
            info["installed_version"] = "unknown"
    else:
        info["installed_version"] = "npx (on-demand)"

    # Check latest version
    success, output = run_command(["npm", "view", package, "version"])
    info["latest_version"] = output if success else "unknown"

    info["has_updates"] = info.get("installed_version") != info.get("latest_version")

    return info


def check_autocoder_running() -> Tuple[bool, str]:
    """Check if Autocoder server is running before update."""
    import socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 8888))
    sock.close()

    if result == 0:
        return False, "Autocoder server is running. Please stop it before updating (python tools/autocoder_api.py stop)"
    return True, "Autocoder server is not running, safe to update"


def rebuild_autocoder_ui() -> Tuple[bool, str]:
    """Rebuild Autocoder UI after update."""
    ui_path = COMPONENTS["autocoder"]["path"] / "ui"
    if not ui_path.exists():
        return True, "No UI directory found, skipping rebuild"

    logger.info("Rebuilding Autocoder UI...")

    # Install dependencies
    success, output = run_command(["npm", "ci"], cwd=ui_path)
    if not success:
        return False, f"Failed to install npm dependencies: {output}"

    # Build
    success, output = run_command(["npm", "run", "build"], cwd=ui_path)
    if not success:
        return False, f"Failed to build UI: {output}"

    return True, "UI rebuilt successfully"


def backup_component(component: str) -> Optional[Path]:
    """Create a backup of a component before updating."""
    config = COMPONENTS.get(component)
    if not config or config["type"] != "git":
        return None

    path = config["path"]
    if not path.exists():
        return None

    # Create backup directory
    backup_path = BACKUP_DIR / component / datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path.parent.mkdir(parents=True, exist_ok=True)

    # Get current commit for backup name
    success, commit = run_command(["git", "rev-parse", "--short", "HEAD"], cwd=path)

    # Create backup marker file (we don't copy the whole repo, just store the commit)
    backup_file = backup_path.with_suffix(".json")
    backup_data = {
        "component": component,
        "commit": commit if success else "unknown",
        "timestamp": datetime.now().isoformat(),
        "path": str(path),
    }

    with open(backup_file, "w") as f:
        json.dump(backup_data, f, indent=2)

    logger.info(f"Created backup marker: {backup_file}")
    return backup_file


def update_git_component(component: str, dry_run: bool = False) -> Tuple[bool, str]:
    """Update a git-based component."""
    config = COMPONENTS.get(component)
    if not config:
        return False, f"Unknown component: {component}"

    path = config["path"]
    if not path.exists():
        return False, f"Component path does not exist: {path}"

    # Pre-update check
    if config.get("pre_update"):
        pre_check = globals().get(config["pre_update"])
        if pre_check:
            success, message = pre_check()
            if not success:
                return False, f"Pre-update check failed: {message}"
            logger.info(f"Pre-update check passed: {message}")

    # Check for local changes
    success, output = run_command(["git", "status", "--porcelain"], cwd=path)
    if success and output:
        return False, f"Local changes detected in {path}. Please commit or stash them first."

    if dry_run:
        return True, f"[DRY RUN] Would update {component} from {config['remote']}/{config['branch']}"

    # Create backup
    backup_component(component)

    # Fetch updates
    logger.info(f"Fetching updates for {component}...")
    success, output = run_command(["git", "fetch", config["remote"]], cwd=path)
    if not success:
        return False, f"Failed to fetch: {output}"

    # Get current and remote commits
    success, local = run_command(["git", "rev-parse", "HEAD"], cwd=path)
    success, remote = run_command(["git", "rev-parse", f"{config['remote']}/{config['branch']}"], cwd=path)

    if local == remote:
        return True, f"{component} is already up to date"

    # Pull updates
    logger.info(f"Pulling updates for {component}...")
    success, output = run_command(
        ["git", "pull", config["remote"], config["branch"]],
        cwd=path
    )
    if not success:
        return False, f"Failed to pull: {output}"

    # Post-update actions
    if config.get("post_update"):
        post_action = globals().get(config["post_update"])
        if post_action:
            success, message = post_action()
            if not success:
                logger.warning(f"Post-update action warning: {message}")
            else:
                logger.info(f"Post-update action: {message}")

    # Get new commit info
    success, new_commit = run_command(["git", "rev-parse", "--short", "HEAD"], cwd=path)

    return True, f"Updated {component}: {local[:8]} → {new_commit}"


def update_npx_component(component: str, dry_run: bool = False) -> Tuple[bool, str]:
    """Update an npx-based component (clears cache to get latest)."""
    config = COMPONENTS.get(component)
    if not config or config["type"] != "npx":
        return False, f"Invalid npx component: {component}"

    package = config["package"]

    if dry_run:
        return True, f"[DRY RUN] Would clear npx cache for {package}"

    # Clear npx cache for this package
    cache_dir = Path.home() / ".npm" / "_npx"
    if cache_dir.exists():
        for item in cache_dir.iterdir():
            if package in str(item):
                shutil.rmtree(item, ignore_errors=True)
                logger.info(f"Cleared cache: {item}")

    return True, f"Cleared npx cache for {package}. Next invocation will use latest version."


def get_status() -> Dict[str, Any]:
    """Get status of all components."""
    status = {}

    for name, config in COMPONENTS.items():
        if config["type"] == "git" and config["path"]:
            status[name] = get_git_info(config["path"])
        elif config["type"] == "npx":
            status[name] = get_npx_info(config["package"])

    return status


def check_updates() -> Dict[str, bool]:
    """Check which components have updates available."""
    updates = {}
    status = get_status()

    for name, info in status.items():
        updates[name] = info.get("has_updates", False)

    return updates


def rollback_component(component: str) -> Tuple[bool, str]:
    """Rollback a component to the previous version."""
    config = COMPONENTS.get(component)
    if not config or config["type"] != "git":
        return False, f"Cannot rollback {component} (not a git component)"

    # Find latest backup
    backup_dir = BACKUP_DIR / component
    if not backup_dir.exists():
        return False, f"No backups found for {component}"

    backups = sorted(backup_dir.glob("*.json"), reverse=True)
    if not backups:
        return False, f"No backup markers found for {component}"

    # Read latest backup
    with open(backups[0]) as f:
        backup_data = json.load(f)

    path = config["path"]
    commit = backup_data.get("commit")

    if not commit or commit == "unknown":
        return False, f"Invalid backup commit for {component}"

    # Rollback to previous commit
    logger.info(f"Rolling back {component} to {commit}...")
    success, output = run_command(["git", "checkout", commit], cwd=path)

    if not success:
        return False, f"Failed to rollback: {output}"

    return True, f"Rolled back {component} to commit {commit}"


def print_status():
    """Print formatted status of all components."""
    print("\n" + "=" * 60)
    print("MyWork Framework - Component Status")
    print("=" * 60)

    status = get_status()

    for name, info in status.items():
        print(f"\n📦 {name.upper()}")
        print("-" * 40)

        if "error" in info:
            print(f"   ❌ {info['error']}")
            continue

        if "current_commit" in info:
            print(f"   Commit:  {info['current_commit']}")
            print(f"   Branch:  {info.get('branch', 'unknown')}")
            print(f"   Updated: {info.get('last_date', 'unknown')}")
            print(f"   Message: {info.get('last_message', 'unknown')}")

            if info.get("has_updates"):
                print(f"   🔄 {info.get('pending_commits', '?')} updates available!")
            else:
                print(f"   ✅ Up to date")

        elif "installed_version" in info:
            print(f"   Installed: {info.get('installed_version', 'unknown')}")
            print(f"   Latest:    {info.get('latest_version', 'unknown')}")

            if info.get("has_updates"):
                print(f"   🔄 Update available!")
            else:
                print(f"   ✅ Up to date")

    print("\n" + "=" * 60)


def update_component(component: str, dry_run: bool = False) -> Tuple[bool, str]:
    """Update a single component."""
    config = COMPONENTS.get(component)
    if not config:
        return False, f"Unknown component: {component}"

    if config["type"] == "git":
        return update_git_component(component, dry_run)
    elif config["type"] == "npx":
        return update_npx_component(component, dry_run)
    else:
        return False, f"Unknown component type: {config['type']}"


def update_all(dry_run: bool = False) -> Dict[str, Tuple[bool, str]]:
    """Update all components."""
    results = {}

    for component in COMPONENTS:
        logger.info(f"\nUpdating {component}...")
        results[component] = update_component(component, dry_run)
        success, message = results[component]
        if success:
            logger.success(message)
        else:
            logger.error(message)

    return results


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "check":
        updates = check_updates()
        print("\n📋 Update Check Results:")
        for name, has_updates in updates.items():
            status = "🔄 Update available" if has_updates else "✅ Up to date"
            print(f"   {name}: {status}")

        if any(updates.values()):
            print("\nRun 'python auto_update.py update' to update all components")

    elif command == "status":
        print_status()

    elif command == "update":
        component = sys.argv[2] if len(sys.argv) > 2 else "all"
        dry_run = "--dry-run" in sys.argv

        if component == "all":
            results = update_all(dry_run)
            print("\n📋 Update Summary:")
            for name, (success, message) in results.items():
                status = "✅" if success else "❌"
                print(f"   {status} {name}: {message}")
        else:
            if component not in COMPONENTS:
                print(f"Unknown component: {component}")
                print(f"Available: {', '.join(COMPONENTS.keys())}, all")
                sys.exit(1)

            success, message = update_component(component, dry_run)
            print(f"{'✅' if success else '❌'} {message}")

    elif command == "rollback":
        if len(sys.argv) < 3:
            print("Usage: python auto_update.py rollback <component>")
            sys.exit(1)

        component = sys.argv[2]
        success, message = rollback_component(component)
        print(f"{'✅' if success else '❌'} {message}")

    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
