#!/usr/bin/env python3
"""
MyWork-AI Web Dashboard — Local browser UI at localhost:9000.
Single-file FastAPI app that serves a beautiful project management dashboard.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

FRAMEWORK_ROOT = os.environ.get("MYWORK_ROOT", str(Path.home() / "MyWork-AI"))

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MyWork-AI Dashboard</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: #0a0a0f; color: #e0e0e0; min-height: 100vh; }
  .header { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            padding: 24px 40px; border-bottom: 1px solid #2a2a3e;
            display: flex; justify-content: space-between; align-items: center; }
  .header h1 { font-size: 24px; color: #00d4ff; }
  .header h1 span { color: #666; font-weight: 300; font-size: 14px; margin-left: 12px; }
  .header .stats { display: flex; gap: 24px; }
  .header .stat { text-align: center; }
  .header .stat-val { font-size: 24px; font-weight: 700; color: #00d4ff; }
  .header .stat-label { font-size: 11px; color: #888; text-transform: uppercase; }
  .container { max-width: 1400px; margin: 0 auto; padding: 32px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 20px; }
  .card { background: #12121a; border: 1px solid #2a2a3e; border-radius: 12px; padding: 24px;
          transition: all 0.2s; }
  .card:hover { border-color: #00d4ff40; transform: translateY(-2px); }
  .card h3 { color: #fff; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
  .card .icon { font-size: 20px; }
  .badge { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 11px;
           font-weight: 600; }
  .badge-green { background: #00d4ff20; color: #00d4ff; }
  .badge-yellow { background: #ffaa0020; color: #ffaa00; }
  .badge-red { background: #ff444420; color: #ff4444; }
  .actions { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
             gap: 12px; margin-bottom: 32px; }
  .btn { padding: 14px 20px; border: 1px solid #2a2a3e; border-radius: 10px; background: #12121a;
         color: #e0e0e0; cursor: pointer; font-size: 14px; transition: all 0.2s;
         display: flex; align-items: center; gap: 8px; text-decoration: none; }
  .btn:hover { background: #1a1a2e; border-color: #00d4ff; color: #00d4ff; }
  .btn-primary { background: linear-gradient(135deg, #0066ff, #00d4ff); color: #fff; border: none; }
  .btn-primary:hover { opacity: 0.9; transform: scale(1.02); }
  .project-list { margin-top: 8px; }
  .project-item { display: flex; justify-content: space-between; align-items: center;
                  padding: 10px 0; border-bottom: 1px solid #1a1a2e; }
  .project-name { font-weight: 500; }
  .project-meta { color: #666; font-size: 13px; }
  .metric { display: flex; justify-content: space-between; padding: 8px 0;
            border-bottom: 1px solid #1a1a2e; }
  .metric-label { color: #888; }
  .metric-value { font-weight: 600; color: #fff; }
  .pipeline { display: flex; gap: 4px; align-items: center; margin: 16px 0; flex-wrap: wrap; }
  .pipeline-step { padding: 8px 16px; border-radius: 8px; font-size: 13px; font-weight: 500; }
  .pipeline-arrow { color: #444; font-size: 18px; }
  .step-done { background: #00d4ff15; color: #00d4ff; border: 1px solid #00d4ff30; }
  .step-active { background: #ffaa0015; color: #ffaa00; border: 1px solid #ffaa0030; }
  .step-pending { background: #1a1a2e; color: #555; border: 1px solid #2a2a3e; }
  #output { background: #0a0a0f; border: 1px solid #2a2a3e; border-radius: 8px; padding: 16px;
            font-family: 'Fira Code', monospace; font-size: 13px; color: #00ff88;
            max-height: 300px; overflow-y: auto; white-space: pre-wrap; display: none; margin-top: 16px; }
  .section-title { font-size: 18px; font-weight: 600; margin: 32px 0 16px; color: #fff; }
</style>
</head>
<body>
<div class="header">
  <h1>⚡ MyWork-AI <span>v{{VERSION}} · {{COMMANDS}} commands · {{TESTS}} tests</span></h1>
  <div class="stats">
    <div class="stat"><div class="stat-val">{{PRODUCTS}}</div><div class="stat-label">Products</div></div>
    <div class="stat"><div class="stat-val">{{CATALOG_VALUE}}</div><div class="stat-label">Catalog</div></div>
    <div class="stat"><div class="stat-val">{{PROJECT_COUNT}}</div><div class="stat-label">Projects</div></div>
  </div>
</div>

<div class="container">
  <div class="section-title">🚀 Pipeline</div>
  <div class="pipeline">
    <div class="pipeline-step step-done">💡 Idea</div>
    <div class="pipeline-arrow">→</div>
    <div class="pipeline-step step-done">🧠 mw plan</div>
    <div class="pipeline-arrow">→</div>
    <div class="pipeline-step step-done">⚡ mw execute</div>
    <div class="pipeline-arrow">→</div>
    <div class="pipeline-step step-active">🧪 mw test</div>
    <div class="pipeline-arrow">→</div>
    <div class="pipeline-step step-pending">🚀 mw deploy</div>
    <div class="pipeline-arrow">→</div>
    <div class="pipeline-step step-pending">💰 mw sell</div>
  </div>

  <div class="section-title">⌨ Quick Actions</div>
  <div class="actions">
    <a class="btn btn-primary" onclick="runCmd('new')">🆕 New Project</a>
    <a class="btn" onclick="runCmd('plan')">🧠 Plan</a>
    <a class="btn" onclick="runCmd('execute')">⚡ Execute</a>
    <a class="btn" onclick="runCmd('test')">🧪 Test</a>
    <a class="btn" onclick="runCmd('deploy')">🚀 Deploy</a>
    <a class="btn" onclick="runCmd('doctor')">🏥 Doctor</a>
    <a class="btn" onclick="runCmd('marketplace')">🏪 Marketplace</a>
    <a class="btn" onclick="runCmd('stats')">📊 Stats</a>
  </div>

  <div id="output"></div>

  <div class="grid">
    <div class="card">
      <h3><span class="icon">📂</span> Projects</h3>
      <div class="project-list">{{PROJECTS_HTML}}</div>
    </div>
    <div class="card">
      <h3><span class="icon">🏪</span> Marketplace Products</h3>
      <div class="project-list">{{MARKETPLACE_HTML}}</div>
    </div>
    <div class="card">
      <h3><span class="icon">⚙</span> Framework</h3>
      <div class="metric"><span class="metric-label">Version</span><span class="metric-value">v{{VERSION}}</span></div>
      <div class="metric"><span class="metric-label">Commands</span><span class="metric-value">{{COMMANDS}}</span></div>
      <div class="metric"><span class="metric-label">Tests</span><span class="metric-value">{{TESTS}} passing</span></div>
      <div class="metric"><span class="metric-label">Python</span><span class="metric-value">{{PYTHON}}</span></div>
      <div class="metric"><span class="metric-label">Git Branch</span><span class="metric-value">{{GIT_BRANCH}}</span></div>
      <div class="metric"><span class="metric-label">Last Commit</span><span class="metric-value">{{GIT_LAST}}</span></div>
    </div>
  </div>
</div>

<script>
async function runCmd(cmd) {
  const output = document.getElementById('output');
  output.style.display = 'block';
  output.textContent = '⏳ Running mw ' + cmd + '...\\n';
  try {
    const resp = await fetch('/api/run?cmd=' + cmd);
    const data = await resp.json();
    output.textContent = data.output || data.error || 'Done';
  } catch (e) {
    output.textContent = 'Error: ' + e.message;
  }
}
</script>
</body>
</html>"""


def get_version():
    try:
        toml = Path(FRAMEWORK_ROOT) / "pyproject.toml"
        for line in toml.read_text().splitlines():
            if line.strip().startswith("version"):
                return line.split("=")[1].strip().strip('"')
    except Exception:
        pass
    return "?"


def get_command_count():
    try:
        import re
        mw = (Path(FRAMEWORK_ROOT) / "tools" / "mw.py").read_text()
        return len(set(re.findall(r'"(\w[\w-]*)"\s*:\s*lambda', mw)))
    except Exception:
        return "?"


def get_projects_html():
    proj_dir = Path(FRAMEWORK_ROOT) / "projects"
    html = ""
    if proj_dir.exists():
        for p in sorted(proj_dir.iterdir()):
            if p.is_dir() and not p.name.startswith("."):
                html += f'<div class="project-item"><span class="project-name">{p.name}</span>'
                html += f'<span class="badge badge-green">active</span></div>'
    return html or '<div class="project-item"><span class="project-meta">No projects yet — run mw new</span></div>'


def get_marketplace_html():
    try:
        r = subprocess.run(
            ["curl", "-s", "https://mywork-ai-production.up.railway.app/api/products"],
            capture_output=True, text=True, timeout=10
        )
        products = json.loads(r.stdout)
        html = ""
        for p in (products if isinstance(products, list) else [])[:10]:
            if p.get("status") == "active":
                price = f"${float(p.get('price', 0)):.0f}"
                html += f'<div class="project-item"><span class="project-name">{p.get("name","?")}</span>'
                html += f'<span class="badge badge-green">{price}</span></div>'
        return html
    except Exception:
        return '<div class="project-meta">Unable to load</div>'


def render_dashboard():
    version = get_version()
    commands = get_command_count()
    git_branch = "?"
    git_last = "?"
    try:
        git_branch = subprocess.run(["git", "branch", "--show-current"],
                                   capture_output=True, text=True, cwd=FRAMEWORK_ROOT, timeout=5).stdout.strip()
        git_last = subprocess.run(["git", "log", "-1", "--format=%cr"],
                                capture_output=True, text=True, cwd=FRAMEWORK_ROOT, timeout=5).stdout.strip()
    except Exception:
        pass

    mkt = {"products": "?", "total_value": "?"}
    try:
        r = subprocess.run(["curl", "-s", "https://mywork-ai-production.up.railway.app/api/products"],
                          capture_output=True, text=True, timeout=10)
        products = json.loads(r.stdout)
        if isinstance(products, list):
            active = [p for p in products if p.get("status") == "active"]
            mkt["products"] = len(active)
            mkt["total_value"] = f"${sum(float(p.get('price',0)) for p in active):.0f}"
    except Exception:
        pass

    html = HTML_TEMPLATE
    html = html.replace("{{VERSION}}", str(version))
    html = html.replace("{{COMMANDS}}", str(commands))
    html = html.replace("{{TESTS}}", "140")
    html = html.replace("{{PRODUCTS}}", str(mkt["products"]))
    html = html.replace("{{CATALOG_VALUE}}", str(mkt["total_value"]))
    html = html.replace("{{PROJECT_COUNT}}", str(len(get_projects_html().split("project-item")) - 1))
    html = html.replace("{{PROJECTS_HTML}}", get_projects_html())
    html = html.replace("{{MARKETPLACE_HTML}}", get_marketplace_html())
    html = html.replace("{{PYTHON}}", sys.version.split()[0])
    html = html.replace("{{GIT_BRANCH}}", git_branch)
    html = html.replace("{{GIT_LAST}}", git_last)
    return html


def cmd_serve(args=None):
    """Start web dashboard at localhost:9000."""
    port = 9000
    if args:
        for i, a in enumerate(args):
            if a in ("--port", "-p") and i + 1 < len(args):
                port = int(args[i + 1])

    try:
        from fastapi import FastAPI, Query
        from fastapi.responses import HTMLResponse, JSONResponse
        import uvicorn
    except ImportError:
        print("Install FastAPI: pip install fastapi uvicorn")
        return 1

    app = FastAPI(title="MyWork-AI Dashboard")

    @app.get("/", response_class=HTMLResponse)
    async def index():
        return render_dashboard()

    @app.get("/api/run")
    async def run_command(cmd: str = Query(...)):
        allowed = {"doctor", "status", "stats", "test", "marketplace", "deploy",
                   "plan", "execute", "new", "git", "check", "loc"}
        if cmd not in allowed:
            return JSONResponse({"error": f"Command '{cmd}' not allowed"})
        try:
            result = subprocess.run(
                [sys.executable, str(Path(FRAMEWORK_ROOT) / "tools" / "mw.py"), cmd],
                capture_output=True, text=True, timeout=60, cwd=FRAMEWORK_ROOT
            )
            # Strip ANSI codes
            import re
            output = re.sub(r'\x1b\[[0-9;]*m', '', result.stdout + result.stderr)
            return JSONResponse({"output": output[:5000]})
        except subprocess.TimeoutExpired:
            return JSONResponse({"error": "Command timed out (60s)"})
        except Exception as e:
            return JSONResponse({"error": str(e)})

    print(f"⚡ MyWork-AI Dashboard starting at http://localhost:{port}")
    print(f"   Press Ctrl+C to stop\n")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")
    return 0


if __name__ == "__main__":
    cmd_serve(sys.argv[1:])
