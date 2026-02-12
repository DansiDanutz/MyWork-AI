#!/usr/bin/env python3
"""MyWork API Server — REST interface for the mw framework.

Usage:
    mw api [--port PORT] [--host HOST]

Exposes all framework functionality via REST endpoints:
    GET  /health              — Server + framework health
    GET  /status              — Framework status (mw status)
    GET  /projects            — List all projects
    GET  /projects/{name}     — Project details
    POST /projects            — Create new project (mw new)
    GET  /brain/search?q=     — Search knowledge vault
    POST /brain               — Add knowledge entry
    GET  /brain/stats         — Brain statistics
    GET  /git/log             — Recent commits
    POST /commands/run        — Run any mw command
    GET  /doctor              — Full diagnostics
    GET  /ecosystem           — Live app URLs
    GET  /plugins             — List plugins
    GET  /env                 — List env vars (masked)
    POST /check               — Run quality gate
    GET  /metrics             — Framework metrics (tests, commands, uptime)
"""

import http.server
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import parse_qs, urlparse

# Try to import FastAPI; fall back to built-in HTTP server
try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    import uvicorn
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

FRAMEWORK_ROOT = Path(__file__).parent.parent
START_TIME = time.time()

# Allowed mw subcommands (whitelist for security)
ALLOWED_COMMANDS = {
    "status", "doctor", "report", "dashboard", "ecosystem",
    "links", "search", "projects", "brain", "lint", "check",
    "env", "monitor", "ci", "plugin", "test", "fix",
}


def run_mw(args: list[str], timeout: int = 30) -> dict:
    """Run an mw subcommand and capture output."""
    cmd = [sys.executable, str(FRAMEWORK_ROOT / "tools" / "mw.py")] + args
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True,
            timeout=timeout, cwd=str(FRAMEWORK_ROOT),
            env={**os.environ, "NO_COLOR": "1", "TERM": "dumb"}
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "stdout": "", "stderr": "Command timed out", "returncode": -1}
    except Exception as e:
        return {"success": False, "stdout": "", "stderr": str(e), "returncode": -1}


def get_projects_list() -> list[dict]:
    """List all projects with metadata."""
    projects = []
    projects_dir = FRAMEWORK_ROOT / "projects"
    if not projects_dir.exists():
        return projects
    for p in sorted(projects_dir.iterdir()):
        if p.is_dir() and not p.name.startswith('.'):
            info = {"name": p.name, "path": str(p)}
            pkg = p / "package.json"
            pyproject = p / "pyproject.toml"
            if pkg.exists():
                try:
                    data = json.loads(pkg.read_text())
                    info["language"] = "node"
                    info["version"] = data.get("version", "unknown")
                    info["description"] = data.get("description", "")
                except Exception:
                    info["language"] = "node"
            elif pyproject.exists():
                info["language"] = "python"
            else:
                info["language"] = "unknown"
            info["has_git"] = (p / ".git").exists()
            info["has_tests"] = any(
                (p / d).exists() for d in ["tests", "test", "__tests__", "spec"]
            )
            projects.append(info)
    return projects


def get_brain_stats() -> dict:
    """Get brain knowledge vault statistics."""
    brain_dir = FRAMEWORK_ROOT / "brain"
    if not brain_dir.exists():
        return {"entries": 0, "categories": [], "size_kb": 0}
    entries = list(brain_dir.glob("**/*.md")) + list(brain_dir.glob("**/*.json"))
    total_size = sum(f.stat().st_size for f in entries if f.exists())
    categories = sorted(set(f.parent.name for f in entries if f.parent != brain_dir))
    return {
        "entries": len(entries),
        "categories": categories[:20],
        "size_kb": round(total_size / 1024, 1),
    }


def search_brain(query: str, limit: int = 10) -> list[dict]:
    """Search brain entries."""
    brain_dir = FRAMEWORK_ROOT / "brain"
    if not brain_dir.exists():
        return []
    results = []
    query_lower = query.lower()
    for f in brain_dir.glob("**/*.md"):
        try:
            content = f.read_text()
            if query_lower in content.lower():
                # Extract first 200 chars as snippet
                idx = content.lower().index(query_lower)
                start = max(0, idx - 50)
                snippet = content[start:start + 200].strip()
                results.append({
                    "file": str(f.relative_to(brain_dir)),
                    "category": f.parent.name if f.parent != brain_dir else "root",
                    "snippet": snippet,
                    "size_kb": round(f.stat().st_size / 1024, 1),
                })
                if len(results) >= limit:
                    break
        except Exception:
            continue
    return results


def get_git_log(limit: int = 20) -> list[dict]:
    """Get recent git commits."""
    try:
        result = subprocess.run(
            ["git", "log", f"--max-count={limit}",
             "--pretty=format:%H|%h|%s|%an|%ar|%aI"],
            capture_output=True, text=True,
            cwd=str(FRAMEWORK_ROOT), timeout=5
        )
        commits = []
        for line in result.stdout.strip().split("\n"):
            if "|" in line:
                parts = line.split("|", 5)
                if len(parts) >= 5:
                    commits.append({
                        "hash": parts[0], "short": parts[1],
                        "message": parts[2], "author": parts[3],
                        "when": parts[4],
                        "date": parts[5] if len(parts) > 5 else "",
                    })
        return commits
    except Exception:
        return []


def get_metrics() -> dict:
    """Gather framework metrics."""
    # Count tests
    test_count = 0
    for pattern in ["test_*.py", "*_test.py"]:
        for f in (FRAMEWORK_ROOT / "tools").glob(f"**/{pattern}"):
            try:
                content = f.read_text()
                test_count += content.count("def test_")
            except Exception:
                pass

    # Count mw commands
    mw_path = FRAMEWORK_ROOT / "tools" / "mw.py"
    cmd_count = 0
    if mw_path.exists():
        try:
            for line in mw_path.read_text().split("\n"):
                if line.strip().startswith('"') and ":" in line and "—" in line:
                    cmd_count += 1
        except Exception:
            pass

    # Count tools
    tools_count = len(list((FRAMEWORK_ROOT / "tools").glob("*.py")))

    return {
        "test_count": test_count,
        "command_count": cmd_count,
        "tools_count": tools_count,
        "uptime_seconds": round(time.time() - START_TIME),
        "framework_version": "2.1.0",
        "python_version": sys.version.split()[0],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ─── FastAPI App ────────────────────────────────────────────

def create_app() -> "FastAPI":
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="MyWork-AI API",
        description="REST interface for the MyWork development framework",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        status_result = run_mw(["status"], timeout=10)
        return {
            "status": "healthy" if status_result["success"] else "degraded",
            "uptime_seconds": round(time.time() - START_TIME),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "framework": "mywork-ai",
            "version": "2.1.0",
        }

    @app.get("/status")
    async def status():
        """Full framework status."""
        result = run_mw(["status"])
        return {"output": result["stdout"], "success": result["success"]}

    @app.get("/projects")
    async def list_projects():
        """List all projects."""
        return {"projects": get_projects_list()}

    @app.get("/projects/{name}")
    async def get_project(name: str):
        """Get project details."""
        projects = get_projects_list()
        for p in projects:
            if p["name"] == name:
                return p
        raise HTTPException(status_code=404, detail=f"Project '{name}' not found")

    @app.post("/projects")
    async def create_project(name: str, template: str = "basic"):
        """Create a new project."""
        result = run_mw(["new", name, template])
        if result["success"]:
            return {"message": f"Project '{name}' created", "output": result["stdout"]}
        raise HTTPException(status_code=400, detail=result["stderr"] or result["stdout"])

    @app.get("/brain/search")
    async def brain_search(q: str = Query(..., min_length=1), limit: int = 10):
        """Search the knowledge vault."""
        return {"query": q, "results": search_brain(q, limit)}

    @app.post("/brain")
    async def brain_add(title: str, content: str, category: str = "general"):
        """Add a knowledge entry."""
        result = run_mw(["brain", "add", "--title", title, "--category", category, "--content", content])
        return {"success": result["success"], "output": result["stdout"]}

    @app.get("/brain/stats")
    async def brain_stats():
        """Brain statistics."""
        return get_brain_stats()

    @app.get("/git/log")
    async def git_log(limit: int = 20):
        """Recent git commits."""
        return {"commits": get_git_log(limit)}

    @app.post("/commands/run")
    async def run_command(command: str, args: list[str] = []):
        """Run an mw command (whitelisted)."""
        if command not in ALLOWED_COMMANDS:
            raise HTTPException(
                status_code=403,
                detail=f"Command '{command}' not allowed. Allowed: {sorted(ALLOWED_COMMANDS)}"
            )
        result = run_mw([command] + args, timeout=60)
        return result

    @app.get("/doctor")
    async def doctor():
        """Full system diagnostics."""
        result = run_mw(["doctor"], timeout=30)
        return {"output": result["stdout"], "success": result["success"]}

    @app.get("/ecosystem")
    async def ecosystem():
        """Live app URLs and ecosystem overview."""
        result = run_mw(["ecosystem"])
        return {"output": result["stdout"], "success": result["success"]}

    @app.get("/plugins")
    async def plugins():
        """List installed plugins."""
        result = run_mw(["plugin", "list"])
        return {"output": result["stdout"], "success": result["success"]}

    @app.get("/env")
    async def env_list():
        """List environment variables (masked)."""
        result = run_mw(["env", "list"])
        return {"output": result["stdout"], "success": result["success"]}

    @app.post("/check")
    async def quality_check(quick: bool = False):
        """Run quality gate checks."""
        args = ["check"]
        if quick:
            args.append("--quick")
        result = run_mw(args, timeout=120)
        return result

    @app.get("/metrics")
    async def metrics():
        """Framework metrics."""
        return get_metrics()

    return app


# ─── Fallback: Built-in HTTP Server ────────────────────────

class SimpleAPIHandler(http.server.BaseHTTPRequestHandler):
    """Minimal HTTP handler when FastAPI is not available."""

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        params = parse_qs(parsed.query)

        routes = {
            "/health": lambda: {
                "status": "healthy",
                "uptime_seconds": round(time.time() - START_TIME),
                "note": "Install fastapi+uvicorn for full API: pip install fastapi uvicorn",
            },
            "/status": lambda: run_mw(["status"]),
            "/projects": lambda: {"projects": get_projects_list()},
            "/brain/stats": lambda: get_brain_stats(),
            "/git/log": lambda: {"commits": get_git_log()},
            "/metrics": lambda: get_metrics(),
            "/doctor": lambda: run_mw(["doctor"]),
        }

        if path in routes:
            data = routes[path]()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(data, indent=2).encode())
        elif path == "/brain/search" and "q" in params:
            results = search_brain(params["q"][0])
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"results": results}, indent=2).encode())
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            endpoints = list(routes.keys()) + ["/brain/search?q="]
            self.wfile.write(json.dumps({
                "error": "Not found",
                "available_endpoints": endpoints,
            }).encode())

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


def serve(host: str = "0.0.0.0", port: int = 8420):
    """Start the API server."""
    if HAS_FASTAPI:
        app = create_app()
        print(f"\n🚀 MyWork API Server starting...")
        print(f"   URL:  http://{host}:{port}")
        print(f"   Docs: http://{host}:{port}/docs")
        print(f"   Mode: FastAPI + Uvicorn\n")
        uvicorn.run(app, host=host, port=port, log_level="info")
    else:
        print(f"\n🚀 MyWork API Server (lite) starting...")
        print(f"   URL:  http://{host}:{port}")
        print(f"   Note: Install fastapi+uvicorn for full API")
        print(f"   Mode: Built-in HTTP server\n")
        server = http.server.HTTPServer((host, port), SimpleAPIHandler)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n⏹ Server stopped.")
            server.server_close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="MyWork API Server")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8420)
    args = parser.parse_args()
    serve(args.host, args.port)
