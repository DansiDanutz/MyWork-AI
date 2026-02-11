#!/usr/bin/env python3
"""MyWork Web Dashboard - Browser-based interface for mw CLI.

Usage:
    mw serve [--port PORT] [--host HOST] [--no-open]

Starts a lightweight web server with a dashboard showing:
- Project overview and health
- Brain knowledge stats
- Recent git activity
- Quick command runner
- System status
"""

import http.server
import json
import os
import subprocess
import sys
import threading
import webbrowser
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, urlparse

# Framework root
FRAMEWORK_ROOT = Path(__file__).parent.parent

def get_projects():
    """Get list of projects."""
    projects = []
    projects_dir = FRAMEWORK_ROOT / "projects"
    if projects_dir.exists():
        for p in sorted(projects_dir.iterdir()):
            if p.is_dir() and not p.name.startswith('.'):
                pkg = p / "package.json"
                pyproject = p / "pyproject.toml"
                lang = "node" if pkg.exists() else "python" if pyproject.exists() else "unknown"
                projects.append({
                    "name": p.name,
                    "path": str(p),
                    "language": lang,
                    "has_git": (p / ".git").exists(),
                })
    return projects

def get_brain_stats():
    """Get brain knowledge vault stats."""
    brain_dir = FRAMEWORK_ROOT / "brain"
    if not brain_dir.exists():
        return {"entries": 0, "categories": [], "size_kb": 0}
    entries = list(brain_dir.glob("**/*.md")) + list(brain_dir.glob("**/*.json"))
    total_size = sum(f.stat().st_size for f in entries if f.exists())
    categories = list(set(f.parent.name for f in entries if f.parent != brain_dir))
    return {
        "entries": len(entries),
        "categories": categories[:10],
        "size_kb": round(total_size / 1024, 1),
    }

def get_git_log(limit=10):
    """Get recent git commits."""
    try:
        result = subprocess.run(
            ["git", "log", f"--max-count={limit}", "--pretty=format:%H|%h|%s|%an|%ar"],
            capture_output=True, text=True, cwd=str(FRAMEWORK_ROOT), timeout=5
        )
        commits = []
        for line in result.stdout.strip().split("\n"):
            if "|" in line:
                parts = line.split("|", 4)
                if len(parts) == 5:
                    commits.append({
                        "hash": parts[0], "short": parts[1],
                        "message": parts[2], "author": parts[3], "when": parts[4]
                    })
        return commits
    except Exception:
        return []

def get_test_count():
    """Get total test count."""
    try:
        result = subprocess.run(
            ["python3", "-m", "pytest", "tests/", "--co", "-q"],
            capture_output=True, text=True, cwd=str(FRAMEWORK_ROOT), timeout=15
        )
        for line in result.stdout.strip().split("\n"):
            if "test" in line and "collected" in line:
                import re
                m = re.search(r'(\d+)\s+test', line)
                if m:
                    return int(m.group(1))
    except Exception:
        pass
    return 0

def get_system_status():
    """Gather system status."""
    return {
        "python": sys.version.split()[0],
        "framework_version": "2.0.0",
        "cwd": str(FRAMEWORK_ROOT),
        "timestamp": datetime.now().isoformat(),
        "test_count": get_test_count(),
    }

def get_commands():
    """List available mw commands."""
    return [
        {"name": "status", "desc": "Quick health check", "category": "Info"},
        {"name": "dashboard", "desc": "Interactive dashboard", "category": "Info"},
        {"name": "doctor", "desc": "Full diagnostics", "category": "Info"},
        {"name": "projects", "desc": "List projects", "category": "Projects"},
        {"name": "new", "desc": "Create project", "category": "Projects"},
        {"name": "test", "desc": "Run tests", "category": "Dev"},
        {"name": "lint", "desc": "Code linting", "category": "Dev"},
        {"name": "git", "desc": "Git operations", "category": "Dev"},
        {"name": "deploy", "desc": "Deploy project", "category": "Deploy"},
        {"name": "ci", "desc": "CI/CD setup", "category": "Deploy"},
        {"name": "brain", "desc": "Knowledge vault", "category": "AI"},
        {"name": "ai", "desc": "AI assistant", "category": "AI"},
        {"name": "env", "desc": "Environment vars", "category": "Config"},
        {"name": "config", "desc": "Configuration", "category": "Config"},
        {"name": "plugin", "desc": "Plugin manager", "category": "Extensions"},
        {"name": "security", "desc": "Security scan", "category": "Security"},
        {"name": "audit", "desc": "Quality audit", "category": "Security"},
        {"name": "perf", "desc": "Performance analysis", "category": "Analysis"},
        {"name": "analytics", "desc": "Usage analytics", "category": "Analysis"},
    ]


DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MyWork-AI Dashboard</title>
<style>
  :root {
    --bg: #0d1117; --surface: #161b22; --border: #30363d;
    --text: #e6edf3; --muted: #8b949e; --accent: #58a6ff;
    --green: #3fb950; --yellow: #d29922; --red: #f85149; --purple: #bc8cff;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; }
  .header { background: var(--surface); border-bottom: 1px solid var(--border); padding: 1rem 2rem; display: flex; align-items: center; gap: 1rem; }
  .header h1 { font-size: 1.4rem; }
  .header .badge { background: var(--accent); color: #000; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; }
  .container { max-width: 1200px; margin: 0 auto; padding: 1.5rem; display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 1rem; }
  .card { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 1.2rem; }
  .card h2 { font-size: 1rem; color: var(--muted); margin-bottom: 0.8rem; display: flex; align-items: center; gap: 0.5rem; }
  .stat { font-size: 2rem; font-weight: 700; color: var(--accent); }
  .stat-row { display: flex; gap: 2rem; margin-bottom: 0.5rem; }
  .stat-item { text-align: center; }
  .stat-item .label { font-size: 0.75rem; color: var(--muted); }
  .stat-item .value { font-size: 1.5rem; font-weight: 700; }
  .commit { padding: 0.4rem 0; border-bottom: 1px solid var(--border); font-size: 0.85rem; }
  .commit:last-child { border: none; }
  .commit .hash { color: var(--accent); font-family: monospace; }
  .commit .msg { color: var(--text); }
  .commit .meta { color: var(--muted); font-size: 0.75rem; }
  .project { display: flex; align-items: center; gap: 0.5rem; padding: 0.3rem 0; }
  .project .dot { width: 8px; height: 8px; border-radius: 50%; }
  .project .dot.node { background: var(--green); }
  .project .dot.python { background: var(--yellow); }
  .project .dot.unknown { background: var(--muted); }
  .cmd-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 0.5rem; }
  .cmd-btn { background: var(--bg); border: 1px solid var(--border); border-radius: 6px; padding: 0.5rem; text-align: center; cursor: pointer; transition: all 0.2s; font-size: 0.85rem; color: var(--text); }
  .cmd-btn:hover { border-color: var(--accent); background: rgba(88,166,255,0.1); }
  .cmd-btn .name { font-weight: 600; }
  .cmd-btn .desc { font-size: 0.7rem; color: var(--muted); }
  #output { background: var(--bg); border: 1px solid var(--border); border-radius: 6px; padding: 0.8rem; font-family: monospace; font-size: 0.8rem; max-height: 300px; overflow-y: auto; white-space: pre-wrap; color: var(--green); display: none; margin-top: 0.8rem; }
  .footer { text-align: center; padding: 1rem; color: var(--muted); font-size: 0.75rem; }
  .green { color: var(--green); }
  .yellow { color: var(--yellow); }
  .purple { color: var(--purple); }
  @media (max-width: 768px) { .container { grid-template-columns: 1fr; padding: 0.5rem; } }
</style>
</head>
<body>
<div class="header">
  <span style="font-size:1.5rem">🔧</span>
  <h1>MyWork-AI</h1>
  <span class="badge">v2.0.0</span>
  <span style="margin-left:auto;color:var(--muted);font-size:0.8rem" id="time"></span>
</div>
<div class="container">
  <div class="card">
    <h2>📊 System Status</h2>
    <div class="stat-row">
      <div class="stat-item"><div class="value green" id="tests">-</div><div class="label">Tests</div></div>
      <div class="stat-item"><div class="value purple" id="commands">-</div><div class="label">Commands</div></div>
      <div class="stat-item"><div class="value yellow" id="projects-count">-</div><div class="label">Projects</div></div>
      <div class="stat-item"><div class="value" style="color:var(--accent)" id="brain-entries">-</div><div class="label">Brain Entries</div></div>
    </div>
    <div style="font-size:0.8rem;color:var(--muted);margin-top:0.5rem">Python <span id="py-version">-</span> | <span id="cwd">-</span></div>
  </div>

  <div class="card">
    <h2>📁 Projects</h2>
    <div id="projects-list">Loading...</div>
  </div>

  <div class="card" style="grid-column: span 2">
    <h2>🔄 Recent Commits</h2>
    <div id="commits">Loading...</div>
  </div>

  <div class="card" style="grid-column: span 2">
    <h2>⚡ Quick Commands</h2>
    <div class="cmd-grid" id="cmd-grid">Loading...</div>
    <div id="output"></div>
  </div>
</div>
<div class="footer">MyWork-AI Framework &mdash; Built with ❤️</div>

<script>
async function load() {
  const [status, projects, commits, commands] = await Promise.all([
    fetch('/api/status').then(r=>r.json()),
    fetch('/api/projects').then(r=>r.json()),
    fetch('/api/commits').then(r=>r.json()),
    fetch('/api/commands').then(r=>r.json()),
  ]);
  document.getElementById('tests').textContent = status.test_count || '?';
  document.getElementById('commands').textContent = commands.length;
  document.getElementById('projects-count').textContent = projects.length;
  document.getElementById('brain-entries').textContent = status.brain?.entries || 0;
  document.getElementById('py-version').textContent = status.python;
  document.getElementById('cwd').textContent = status.cwd;

  const pl = document.getElementById('projects-list');
  pl.innerHTML = projects.length ? projects.map(p =>
    `<div class="project"><span class="dot ${p.language}"></span><strong>${p.name}</strong><span style="color:var(--muted);font-size:0.75rem;margin-left:auto">${p.language}</span></div>`
  ).join('') : '<span style="color:var(--muted)">No projects found</span>';

  const cl = document.getElementById('commits');
  cl.innerHTML = commits.length ? commits.map(c =>
    `<div class="commit"><span class="hash">${c.short}</span> <span class="msg">${c.message}</span><br><span class="meta">${c.author} &middot; ${c.when}</span></div>`
  ).join('') : '<span style="color:var(--muted)">No commits</span>';

  const cg = document.getElementById('cmd-grid');
  cg.innerHTML = commands.map(c =>
    `<div class="cmd-btn" onclick="runCmd('${c.name}')"><div class="name">mw ${c.name}</div><div class="desc">${c.desc}</div></div>`
  ).join('');
}

async function runCmd(name) {
  const out = document.getElementById('output');
  out.style.display = 'block';
  out.textContent = `$ mw ${name}\\nRunning...`;
  try {
    const r = await fetch('/api/run?cmd=' + encodeURIComponent(name));
    const data = await r.json();
    out.textContent = `$ mw ${name}\\n${data.output || data.error || 'Done'}`;
  } catch(e) { out.textContent = `Error: ${e.message}`; }
}

function updateTime() {
  document.getElementById('time').textContent = new Date().toLocaleString();
}
setInterval(updateTime, 1000);
updateTime();
load();
</script>
</body>
</html>"""


class DashboardHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for the dashboard."""
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass
    
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == "/" or path == "/dashboard":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.encode())
        
        elif path == "/api/status":
            status = get_system_status()
            status["brain"] = get_brain_stats()
            self._json(status)
        
        elif path == "/api/projects":
            self._json(get_projects())
        
        elif path == "/api/commits":
            self._json(get_git_log(15))
        
        elif path == "/api/commands":
            self._json(get_commands())
        
        elif path == "/api/run":
            params = parse_qs(parsed.query)
            cmd = params.get("cmd", ["status"])[0]
            # Whitelist safe commands
            safe = {"status", "doctor", "report", "projects", "stats", "version",
                    "ecosystem", "links", "changelog", "brain stats", "env list", "config list"}
            if cmd not in safe:
                self._json({"error": f"Command '{cmd}' not allowed via web. Use terminal."})
                return
            try:
                result = subprocess.run(
                    ["python3", str(FRAMEWORK_ROOT / "tools" / "mw.py"), cmd],
                    capture_output=True, text=True, cwd=str(FRAMEWORK_ROOT), timeout=15
                )
                # Strip ANSI codes
                import re
                output = re.sub(r'\x1b\[[0-9;]*m', '', result.stdout + result.stderr)
                self._json({"output": output[:5000]})
            except subprocess.TimeoutExpired:
                self._json({"error": "Command timed out (15s limit)"})
            except Exception as e:
                self._json({"error": str(e)})
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def _json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())


def cmd_serve(args=None):
    """Start the web dashboard server."""
    port = 8420
    host = "0.0.0.0"
    no_open = False
    
    if args:
        i = 0
        while i < len(args):
            if args[i] == "--port" and i + 1 < len(args):
                port = int(args[i + 1]); i += 2
            elif args[i] == "--host" and i + 1 < len(args):
                host = args[i + 1]; i += 2
            elif args[i] == "--no-open":
                no_open = True; i += 1
            else:
                i += 1
    
    server = http.server.HTTPServer((host, port), DashboardHandler)
    url = f"http://localhost:{port}"
    
    print(f"\n  🔧 MyWork-AI Web Dashboard")
    print(f"  {'─' * 35}")
    print(f"  🌐 Running at: {url}")
    print(f"  📡 Host: {host}:{port}")
    print(f"  🛑 Press Ctrl+C to stop\n")
    
    if not no_open:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  👋 Dashboard stopped.")
        server.shutdown()
    
    return 0


if __name__ == "__main__":
    cmd_serve(sys.argv[1:])
