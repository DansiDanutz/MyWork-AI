#!/usr/bin/env python3
"""
AutoForge API Integration Tool
==============================
Provides programmatic control over AutoForge with both automatic and manual modes.

AutoForge Server: http://127.0.0.1:8888
WebSocket: ws://127.0.0.1:8888/ws/projects/{project_name}

Reference: https://github.com/AutoForgeAI/autoforge

Usage:
    # Check if AutoForge server is running
    python tools/autoforge_api.py status

    # Start a project (automatic mode)
    python tools/autoforge_api.py start my-project --concurrency 3

    # Stop a running project
    python tools/autoforge_api.py stop my-project

    # Get project progress
    python tools/autoforge_api.py progress my-project

    # Open AutoForge UI (manual mode)
    python tools/autoforge_api.py ui

    # Start server if not running
    python tools/autoforge_api.py server
"""

import os
import sys
import json
import time
import httpx
import asyncio
import argparse
import subprocess
import webbrowser
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / ".env")

# Configuration - Import from shared config with fallback
try:
    from config import AUTOFORGE_ROOT as AUTOFORGE_PATH, PROJECTS_DIR as MYWORK_PROJECTS
except ImportError:

    def _get_mywork_root():
        if env_root := os.environ.get("MYWORK_ROOT"):
            return Path(env_root)
        script_dir = Path(__file__).resolve().parent
        return script_dir.parent if script_dir.name == "tools" else Path.home() / "MyWork"

    AUTOFORGE_PATH = Path(os.getenv("AUTOFORGE_ROOT", Path.home() / "GamesAI" / "autoforge"))
    MYWORK_PROJECTS = _get_mywork_root() / "projects"
AUTOFORGE_API = "http://127.0.0.1:8888"
WEBHOOK_URL = os.getenv("PROGRESS_N8N_WEBHOOK_URL", "")

# Default settings
DEFAULT_MODEL = "claude-opus-4-5-20251101"
AVAILABLE_MODELS = [
    "claude-opus-4-5-20251101",
    "claude-sonnet-4-5-20250929",
    "glm-4-plus",
    "glm-4-long",
    "codex",
]

# Provider endpoints for non-Anthropic models
MODEL_PROVIDERS = {
    "glm-4-plus": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "env_key": "ZAI_API_KEY",
    },
    "glm-4-long": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "env_key": "ZAI_API_KEY",
    },
    "codex": {
        "type": "cli",
        "command": "codex",
    },
}


def get_autoforge_python() -> str:
    """Prefer AutoForge venv python when available."""
    candidates = [
        AUTOFORGE_PATH / "venv" / "bin" / "python",
        AUTOFORGE_PATH / ".venv" / "bin" / "python",
        AUTOFORGE_PATH / "venv" / "Scripts" / "python.exe",
        AUTOFORGE_PATH / ".venv" / "Scripts" / "python.exe",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return sys.executable


class AutoForgeAPI:
    """Client for AutoForge REST API."""

    def __init__(self, base_url: str = AUTOFORGE_API):
        self.base_url = base_url
        self.client = httpx.Client(timeout=30.0)

    def is_server_running(self) -> bool:
        """Check if AutoForge server is running."""
        try:
            response = self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except httpx.ConnectError:
            return False

    def get_agent_status(self, project_name: str) -> Dict[str, Any]:
        """Get current agent status for a project."""
        try:
            response = self.client.get(f"{self.base_url}/api/projects/{project_name}/agent/status")
            return response.json()
        except httpx.ConnectError:
            return {"error": "Server not running", "status": "unknown"}
        except Exception as e:
            return {"error": str(e), "status": "unknown"}

    def start_agent(
        self,
        project_name: str,
        model: str = DEFAULT_MODEL,
        concurrency: int = 1,
        yolo_mode: bool = False,
        testing_ratio: int = 1,
    ) -> Dict[str, Any]:
        """Start the AutoForge agent for a project."""
        try:
            response = self.client.post(
                f"{self.base_url}/api/projects/{project_name}/agent/start",
                json={
                    "model": model,
                    "max_concurrency": concurrency,
                    "yolo_mode": yolo_mode,
                    "testing_agent_ratio": testing_ratio,
                },
            )
            return response.json()
        except httpx.ConnectError:
            return {"error": "Server not running. Start with: python tools/autoforge_api.py server"}
        except Exception as e:
            return {"error": str(e)}

    def stop_agent(self, project_name: str) -> Dict[str, Any]:
        """Stop the running agent."""
        try:
            response = self.client.post(f"{self.base_url}/api/projects/{project_name}/agent/stop")
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def pause_agent(self, project_name: str) -> Dict[str, Any]:
        """Pause the running agent."""
        try:
            response = self.client.post(f"{self.base_url}/api/projects/{project_name}/agent/pause")
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def resume_agent(self, project_name: str) -> Dict[str, Any]:
        """Resume a paused agent."""
        try:
            response = self.client.post(f"{self.base_url}/api/projects/{project_name}/agent/resume")
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def get_features(self, project_name: str) -> Dict[str, Any]:
        """Get feature progress for a project."""
        try:
            response = self.client.get(f"{self.base_url}/api/projects/{project_name}/features")
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def list_projects(self) -> Dict[str, Any]:
        """List all registered projects."""
        try:
            response = self.client.get(f"{self.base_url}/api/projects")
            return response.json()
        except Exception as e:
            return {"error": str(e)}


def start_server():
    """Start the AutoForge server."""
    api = AutoForgeAPI()
    if api.is_server_running():
        print("AutoForge server is already running at http://127.0.0.1:8888")
        return True

    print("Starting AutoForge server...")
    start_script = AUTOFORGE_PATH / "start_ui.py"

    if not start_script.exists():
        print(f"ERROR: AutoForge not found at {AUTOFORGE_PATH}")
        return False

    # Start server in background
    python_bin = get_autoforge_python()
    
    # Security: Validate paths and use list args to prevent injection
    if not os.path.isfile(python_bin):
        print(f"ERROR: Invalid python executable: {python_bin}")
        return False
    
    subprocess.Popen(
        [python_bin, str(start_script)],  # Using list args prevents shell injection
        cwd=str(AUTOFORGE_PATH),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Wait for server to start
    print("Waiting for server to start", end="")
    for _ in range(30):
        time.sleep(1)
        print(".", end="", flush=True)
        if api.is_server_running():
            print("\nServer started successfully!")
            print(f"UI available at: http://127.0.0.1:8888")
            return True

    print("\nFailed to start server within 30 seconds")
    return False


def open_ui():
    """Open the AutoForge UI in browser."""
    api = AutoForgeAPI()
    if not api.is_server_running():
        print("Server not running. Starting...")
        if not start_server():
            return

    webbrowser.open("http://127.0.0.1:8888")
    print("Opened AutoForge UI in browser")


def get_progress(project_name: str) -> Dict[str, Any]:
    """Get detailed progress for a project."""
    api = AutoForgeAPI()

    if not api.is_server_running():
        # Try reading directly from database
        project_path = MYWORK_PROJECTS / project_name
        db_path = project_path / "features.db"

        if db_path.exists():
            import sqlite3

            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN passes = 1 THEN 1 ELSE 0 END) as passing,
                    SUM(CASE WHEN in_progress = 1 THEN 1 ELSE 0 END) as in_progress
                FROM features
            """)
            row = cursor.fetchone()
            conn.close()

            return {
                "total": row[0],
                "passing": row[1] or 0,
                "in_progress": row[2] or 0,
                "pending": row[0] - (row[1] or 0) - (row[2] or 0),
                "source": "database",
            }
        return {"error": "Server not running and no database found"}

    # Get from API
    features = api.get_features(project_name)
    status = api.get_agent_status(project_name)

    if "error" in features:
        return features

    # Calculate progress
    total = len(features) if isinstance(features, list) else 0
    passing = sum(1 for f in features if f.get("passes")) if isinstance(features, list) else 0
    in_progress = (
        sum(1 for f in features if f.get("in_progress")) if isinstance(features, list) else 0
    )

    return {
        "total": total,
        "passing": passing,
        "in_progress": in_progress,
        "pending": total - passing - in_progress,
        "agent_status": status.get("status", "unknown"),
        "source": "api",
    }


def notify_webhook(event: str, data: Dict[str, Any]):
    """Send notification to n8n webhook if configured."""
    if not WEBHOOK_URL:
        return

    try:
        httpx.post(
            WEBHOOK_URL,
            json={
                "event": event,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                **data,
            },
        )
    except Exception as e:
        print(f"Webhook notification failed: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="AutoForge API Integration Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check server status
  python tools/autoforge_api.py status

  # Start project with automatic mode
  python tools/autoforge_api.py start my-project --concurrency 3

  # Open manual UI
  python tools/autoforge_api.py ui

  # Get project progress
  python tools/autoforge_api.py progress my-project
""",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Status command
    subparsers.add_parser("status", help="Check if AutoForge server is running")

    # Server command
    subparsers.add_parser("server", help="Start AutoForge server")

    # UI command
    subparsers.add_parser("ui", help="Open AutoForge UI in browser (manual mode)")

    # Start command
    start_parser = subparsers.add_parser("start", help="Start agent for a project (automatic mode)")
    start_parser.add_argument("project", help="Project name")
    start_parser.add_argument(
        "--model", default=DEFAULT_MODEL, choices=AVAILABLE_MODELS, help="Model to use"
    )
    start_parser.add_argument(
        "--concurrency", type=int, default=1, help="Number of parallel agents"
    )
    start_parser.add_argument("--yolo", action="store_true", help="Skip testing for speed")
    start_parser.add_argument(
        "--testing-ratio", type=int, default=1, help="Testing agents per coding agent"
    )

    # Stop command
    stop_parser = subparsers.add_parser("stop", help="Stop agent for a project")
    stop_parser.add_argument("project", help="Project name")

    # Pause command
    pause_parser = subparsers.add_parser("pause", help="Pause agent for a project")
    pause_parser.add_argument("project", help="Project name")

    # Resume command
    resume_parser = subparsers.add_parser("resume", help="Resume paused agent")
    resume_parser.add_argument("project", help="Project name")

    # Progress command
    progress_parser = subparsers.add_parser("progress", help="Get project progress")
    progress_parser.add_argument("project", help="Project name")

    # List command
    subparsers.add_parser("list", help="List all registered projects")

    args = parser.parse_args()
    api = AutoForgeAPI()

    if args.command == "status":
        if api.is_server_running():
            print("AutoForge server is RUNNING at http://127.0.0.1:8888")
        else:
            print("AutoForge server is NOT RUNNING")
            print("Start with: python tools/autoforge_api.py server")

    elif args.command == "server":
        start_server()

    elif args.command == "ui":
        open_ui()

    elif args.command == "start":
        if not api.is_server_running():
            print("Server not running. Starting...")
            if not start_server():
                sys.exit(1)

        print(f"Starting agent for project: {args.project}")
        print(f"  Model: {args.model}")
        print(f"  Concurrency: {args.concurrency}")
        print(f"  YOLO mode: {args.yolo}")

        result = api.start_agent(
            args.project,
            model=args.model,
            concurrency=args.concurrency,
            yolo_mode=args.yolo,
            testing_ratio=args.testing_ratio,
        )
        print(json.dumps(result, indent=2))

        notify_webhook(
            "agent_started",
            {"project": args.project, "model": args.model, "concurrency": args.concurrency},
        )

    elif args.command == "stop":
        result = api.stop_agent(args.project)
        print(json.dumps(result, indent=2))
        notify_webhook("agent_stopped", {"project": args.project})

    elif args.command == "pause":
        result = api.pause_agent(args.project)
        print(json.dumps(result, indent=2))

    elif args.command == "resume":
        result = api.resume_agent(args.project)
        print(json.dumps(result, indent=2))

    elif args.command == "progress":
        result = get_progress(args.project)
        print(json.dumps(result, indent=2))

        if "total" in result:
            pct = (result["passing"] / result["total"] * 100) if result["total"] > 0 else 0
            print(f"\nProgress: {result['passing']}/{result['total']} features ({pct:.1f}%)")

    elif args.command == "list":
        result = api.list_projects()
        print(json.dumps(result, indent=2))


# Backwards compatibility alias
AutoForgeClient = AutoForgeAPI

if __name__ == "__main__":
    main()
