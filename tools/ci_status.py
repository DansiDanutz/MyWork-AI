#!/usr/bin/env python3
"""MyWork CI Status — check GitHub Actions workflow status.

Usage:
    mw ci status                  Show latest workflow runs
    mw ci status --repo <owner/repo>  Check specific repo
    mw ci status --branch <name>  Filter by branch
    mw ci logs <run_id>           Show logs for a run
    mw ci badge                   Generate status badge markdown
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone


def run_git(args):
    try:
        r = subprocess.run(["git"] + args, capture_output=True, text=True, timeout=10)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def get_repo_info():
    """Detect GitHub repo from git remote."""
    remote = run_git(["remote", "get-url", "origin"])
    if not remote:
        return None
    # Parse github.com/owner/repo
    m = re.search(r"github\.com[:/]([^/]+)/([^/.]+)", remote)
    if m:
        return f"{m.group(1)}/{m.group(2)}"
    return None


def gh_api(endpoint, token=None):
    """Call GitHub API."""
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    cmd = ["curl", "-s", "-H", f"Accept: {headers['Accept']}"]
    if token:
        cmd += ["-H", f"Authorization: {headers['Authorization']}"]
    cmd.append(f"https://api.github.com{endpoint}")
    
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return json.loads(r.stdout) if r.stdout else {}
    except Exception:
        return {}


STATUS_ICONS = {
    "completed": {"success": "✅", "failure": "❌", "cancelled": "⏹️", "skipped": "⏭️"},
    "in_progress": "🔄",
    "queued": "⏳",
    "waiting": "⏳",
}


def format_run(run):
    """Format a workflow run for display."""
    status = run.get("status", "unknown")
    conclusion = run.get("conclusion", "")
    
    if status == "completed":
        icon = STATUS_ICONS["completed"].get(conclusion, "❓")
    else:
        icon = STATUS_ICONS.get(status, "❓")
    
    name = run.get("name", "Unknown")
    branch = run.get("head_branch", "?")
    sha = run.get("head_sha", "")[:7]
    updated = run.get("updated_at", "")
    run_id = run.get("id", "")
    
    # Format time
    time_str = ""
    if updated:
        try:
            dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
            delta = datetime.now(timezone.utc) - dt
            if delta.days > 0:
                time_str = f"{delta.days}d ago"
            elif delta.seconds > 3600:
                time_str = f"{delta.seconds // 3600}h ago"
            else:
                time_str = f"{delta.seconds // 60}m ago"
        except Exception:
            time_str = updated[:10]
    
    return f"  {icon} {name:<30} {branch:<15} {sha}  {time_str}  #{run_id}"


def cmd_status(args):
    """Show CI status."""
    repo = None
    branch = None
    
    i = 0
    while i < len(args):
        if args[i] == "--repo" and i + 1 < len(args):
            repo = args[i + 1]; i += 2
        elif args[i] == "--branch" and i + 1 < len(args):
            branch = args[i + 1]; i += 2
        else:
            i += 1
    
    if not repo:
        repo = get_repo_info()
    if not repo:
        print("❌ Could not detect GitHub repo. Use --repo owner/name")
        return 1
    
    token = os.environ.get("GITHUB_TOKEN", "")
    
    endpoint = f"/repos/{repo}/actions/runs?per_page=10"
    if branch:
        endpoint += f"&branch={branch}"
    
    data = gh_api(endpoint, token)
    runs = data.get("workflow_runs", [])
    
    if not runs:
        print(f"📭 No workflow runs found for {repo}")
        if not token:
            print("   💡 Set GITHUB_TOKEN for private repo access")
        return 0
    
    print(f"\n\033[1m🔧 CI Status — {repo}\033[0m")
    print("=" * 80)
    print(f"  {'Status':<3} {'Workflow':<30} {'Branch':<15} {'SHA'}     {'When'}      {'Run ID'}")
    print("-" * 80)
    
    for run in runs:
        print(format_run(run))
    
    # Summary
    latest = runs[0]
    status = latest.get("status")
    conclusion = latest.get("conclusion", "")
    
    print("-" * 80)
    if status == "completed" and conclusion == "success":
        print("  🟢 Latest: PASSING")
    elif status == "completed" and conclusion == "failure":
        print("  🔴 Latest: FAILING")
    elif status == "in_progress":
        print("  🟡 Latest: IN PROGRESS")
    else:
        print(f"  ⚪ Latest: {status} / {conclusion}")
    
    print()
    return 0


def cmd_badge(args):
    """Generate badge markdown."""
    repo = None
    i = 0
    while i < len(args):
        if args[i] == "--repo" and i + 1 < len(args):
            repo = args[i + 1]; i += 2
        else:
            i += 1
    
    if not repo:
        repo = get_repo_info()
    if not repo:
        print("❌ Could not detect repo")
        return 1
    
    print(f"[![CI](https://github.com/{repo}/actions/workflows/ci.yml/badge.svg)](https://github.com/{repo}/actions)")
    return 0


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    
    if not args or args[0] in ("--help", "-h"):
        print(__doc__)
        return 0
    
    cmd = args[0]
    rest = args[1:]
    
    if cmd == "status":
        return cmd_status(rest)
    elif cmd == "badge":
        return cmd_badge(rest)
    else:
        print(f"Unknown ci command: {cmd}")
        print("Use: mw ci status | mw ci badge")
        return 1


if __name__ == "__main__":
    sys.exit(main())
