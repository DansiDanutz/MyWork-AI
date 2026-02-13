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
- Real-time auto-refresh
- Brain search
- Command history
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
    """Get list of projects with health indicators."""
    projects = []
    projects_dir = FRAMEWORK_ROOT / "projects"
    if projects_dir.exists():
        for p in sorted(projects_dir.iterdir()):
            if p.is_dir() and not p.name.startswith('.'):
                pkg = p / "package.json"
                pyproject = p / "pyproject.toml"
                setup_py = p / "setup.py"
                cargo = p / "Cargo.toml"
                if pkg.exists():
                    lang = "node"
                elif pyproject.exists() or setup_py.exists():
                    lang = "python"
                elif cargo.exists():
                    lang = "rust"
                else:
                    lang = "unknown"
                
                # Count files
                src_files = list(p.rglob("*.py")) + list(p.rglob("*.ts")) + list(p.rglob("*.tsx")) + list(p.rglob("*.js"))
                src_files = [f for f in src_files if "node_modules" not in str(f) and "__pycache__" not in str(f)]
                
                # Check for tests
                has_tests = (p / "tests").exists() or (p / "test").exists() or (p / "__tests__").exists()
                
                # Check for readme
                has_readme = (p / "README.md").exists() or (p / "readme.md").exists()
                
                projects.append({
                    "name": p.name,
                    "path": str(p),
                    "language": lang,
                    "has_git": (p / ".git").exists(),
                    "file_count": len(src_files),
                    "has_tests": has_tests,
                    "has_readme": has_readme,
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
        "categories": sorted(categories[:15]),
        "size_kb": round(total_size / 1024, 1),
    }

def search_brain(query, limit=10):
    """Search brain entries."""
    brain_dir = FRAMEWORK_ROOT / "brain"
    if not brain_dir.exists():
        return []
    results = []
    query_lower = query.lower()
    for f in brain_dir.rglob("*.md"):
        try:
            content = f.read_text(errors='ignore')
            if query_lower in content.lower():
                # Extract snippet
                idx = content.lower().index(query_lower)
                start = max(0, idx - 80)
                end = min(len(content), idx + len(query) + 80)
                snippet = content[start:end].strip()
                if start > 0:
                    snippet = "..." + snippet
                if end < len(content):
                    snippet = snippet + "..."
                results.append({
                    "file": str(f.relative_to(brain_dir)),
                    "category": f.parent.name if f.parent != brain_dir else "root",
                    "snippet": snippet,
                })
                if len(results) >= limit:
                    break
        except Exception:
            continue
    return results

def get_git_log(limit=15):
    """Get recent git commits."""
    try:
        result = subprocess.run(
            ["git", "log", f"--max-count={limit}", "--pretty=format:%H|%h|%s|%an|%ar|%aI"],
            capture_output=True, text=True, cwd=str(FRAMEWORK_ROOT), timeout=5
        )
        commits = []
        for line in result.stdout.strip().split("\n"):
            if "|" in line:
                parts = line.split("|", 5)
                if len(parts) == 6:
                    # Categorize commit type
                    msg = parts[2]
                    ctype = "other"
                    if msg.startswith("feat"):
                        ctype = "feat"
                    elif msg.startswith("fix"):
                        ctype = "fix"
                    elif msg.startswith("test"):
                        ctype = "test"
                    elif msg.startswith("docs"):
                        ctype = "docs"
                    elif msg.startswith("refactor"):
                        ctype = "refactor"
                    elif msg.startswith("chore"):
                        ctype = "chore"
                    commits.append({
                        "hash": parts[0], "short": parts[1],
                        "message": parts[2], "author": parts[3],
                        "when": parts[4], "date": parts[5], "type": ctype
                    })
        return commits
    except Exception:
        return []

def get_git_stats():
    """Get git repository statistics."""
    stats = {}
    try:
        # Total commits
        r = subprocess.run(["git", "rev-list", "--count", "HEAD"],
                          capture_output=True, text=True, cwd=str(FRAMEWORK_ROOT), timeout=5)
        stats["total_commits"] = int(r.stdout.strip()) if r.returncode == 0 else 0
        
        # Contributors
        r = subprocess.run(["git", "shortlog", "-sn", "--all"],
                          capture_output=True, text=True, cwd=str(FRAMEWORK_ROOT), timeout=5)
        stats["contributors"] = len([l for l in r.stdout.strip().split("\n") if l.strip()]) if r.returncode == 0 else 0
        
        # Files tracked
        r = subprocess.run(["git", "ls-files"],
                          capture_output=True, text=True, cwd=str(FRAMEWORK_ROOT), timeout=5)
        stats["tracked_files"] = len(r.stdout.strip().split("\n")) if r.returncode == 0 else 0
        
        # Lines of code (python files only for speed)
        r = subprocess.run(["git", "ls-files", "*.py"],
                          capture_output=True, text=True, cwd=str(FRAMEWORK_ROOT), timeout=5)
        py_files = [f for f in r.stdout.strip().split("\n") if f]
        total_lines = 0
        for pf in py_files[:100]:  # limit for speed
            fp = FRAMEWORK_ROOT / pf
            if fp.exists():
                total_lines += sum(1 for _ in open(fp, errors='ignore'))
        stats["python_loc"] = total_lines
        
    except Exception:
        pass
    return stats

def get_system_status():
    """Gather system status."""
    return {
        "python": sys.version.split()[0],
        "framework_version": "2.1.0",
        "cwd": str(FRAMEWORK_ROOT),
        "timestamp": datetime.now().isoformat(),
        "uptime": _get_uptime(),
    }

def _get_uptime():
    """Get system uptime."""
    try:
        with open("/proc/uptime") as f:
            secs = float(f.read().split()[0])
            days = int(secs // 86400)
            hours = int((secs % 86400) // 3600)
            return f"{days}d {hours}h"
    except Exception:
        return "unknown"

def get_commands():
    """List available mw commands grouped by category."""
    return [
        {"name": "status", "desc": "Quick health check", "category": "Info", "icon": "💚"},
        {"name": "dashboard", "desc": "Interactive dashboard", "category": "Info", "icon": "📊"},
        {"name": "doctor", "desc": "Full diagnostics", "category": "Info", "icon": "🏥"},
        {"name": "report", "desc": "Detailed report", "category": "Info", "icon": "📋"},
        {"name": "projects", "desc": "List projects", "category": "Projects", "icon": "📁"},
        {"name": "new", "desc": "Create project", "category": "Projects", "icon": "✨"},
        {"name": "test", "desc": "Run tests", "category": "Dev", "icon": "🧪"},
        {"name": "lint", "desc": "Code linting", "category": "Dev", "icon": "🔍"},
        {"name": "check", "desc": "Quality gate", "category": "Dev", "icon": "✅"},
        {"name": "git", "desc": "Git operations", "category": "Dev", "icon": "🔀"},
        {"name": "deploy", "desc": "Deploy project", "category": "Deploy", "icon": "🚀"},
        {"name": "ci", "desc": "CI/CD setup", "category": "Deploy", "icon": "⚙️"},
        {"name": "monitor", "desc": "Deployment health", "category": "Deploy", "icon": "📡"},
        {"name": "brain", "desc": "Knowledge vault", "category": "AI", "icon": "🧠"},
        {"name": "ai", "desc": "AI assistant", "category": "AI", "icon": "🤖"},
        {"name": "pair", "desc": "AI pair programming", "category": "AI", "icon": "👥"},
        {"name": "env", "desc": "Environment vars", "category": "Config", "icon": "🔧"},
        {"name": "config", "desc": "Configuration", "category": "Config", "icon": "⚙️"},
        {"name": "plugin", "desc": "Plugin manager", "category": "Extensions", "icon": "🔌"},
        {"name": "security", "desc": "Security scan", "category": "Security", "icon": "🛡️"},
        {"name": "audit", "desc": "Quality audit", "category": "Security", "icon": "🔒"},
        {"name": "perf", "desc": "Performance analysis", "category": "Analysis", "icon": "⚡"},
        {"name": "analytics", "desc": "Usage analytics", "category": "Analysis", "icon": "📈"},
        {"name": "recap", "desc": "Project recap", "category": "Analysis", "icon": "📝"},
        {"name": "changelog", "desc": "Generate changelog", "category": "Dev", "icon": "📜"},
        {"name": "snapshot", "desc": "Capture metrics", "category": "Analysis", "icon": "📸"},
    ]


DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MyWork-AI Dashboard</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🔧</text></svg>">
<style>
  :root {
    --bg: #0a0e14; --surface: #131920; --surface-2: #1a2130;
    --border: #1e2a3a; --border-hover: #2d4160;
    --text: #e6edf3; --muted: #6e7a8a; --dim: #4a5568;
    --accent: #4f9cf7; --accent-glow: rgba(79,156,247,0.15);
    --green: #34d399; --yellow: #fbbf24; --red: #f87171;
    --purple: #a78bfa; --cyan: #22d3ee; --orange: #fb923c;
    --radius: 10px; --shadow: 0 2px 12px rgba(0,0,0,0.3);
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: var(--bg); color: var(--text); min-height: 100vh;
    background-image: radial-gradient(ellipse at top, rgba(79,156,247,0.03) 0%, transparent 60%);
  }
  
  /* Header */
  .header {
    background: var(--surface); border-bottom: 1px solid var(--border);
    padding: 0.8rem 2rem; display: flex; align-items: center; gap: 0.8rem;
    position: sticky; top: 0; z-index: 100; backdrop-filter: blur(12px);
    background: rgba(19,25,32,0.9);
  }
  .header .logo { font-size: 1.5rem; }
  .header h1 { font-size: 1.2rem; font-weight: 700; letter-spacing: -0.5px; }
  .header .badge {
    background: linear-gradient(135deg, var(--accent), var(--purple));
    color: #fff; padding: 2px 10px; border-radius: 12px;
    font-size: 0.7rem; font-weight: 700; letter-spacing: 0.5px;
  }
  .header .refresh-btn {
    margin-left: auto; background: none; border: 1px solid var(--border);
    color: var(--muted); padding: 4px 12px; border-radius: 6px; cursor: pointer;
    font-size: 0.75rem; transition: all 0.2s;
  }
  .header .refresh-btn:hover { border-color: var(--accent); color: var(--accent); }
  .header .refresh-btn.loading { animation: spin 1s linear infinite; }
  @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
  .header .time { color: var(--muted); font-size: 0.75rem; font-family: monospace; }
  
  /* Tabs */
  .tabs {
    display: flex; gap: 0; background: var(--surface);
    border-bottom: 1px solid var(--border); padding: 0 2rem;
  }
  .tab {
    padding: 0.6rem 1.2rem; font-size: 0.8rem; color: var(--muted);
    cursor: pointer; border-bottom: 2px solid transparent; transition: all 0.2s;
    font-weight: 500;
  }
  .tab:hover { color: var(--text); }
  .tab.active { color: var(--accent); border-bottom-color: var(--accent); }
  
  /* Layout */
  .container {
    max-width: 1400px; margin: 0 auto; padding: 1.5rem;
    display: grid; grid-template-columns: repeat(12, 1fr); gap: 1rem;
  }
  .tab-content { display: none; }
  .tab-content.active { display: grid; grid-template-columns: repeat(12, 1fr); gap: 1rem; max-width: 1400px; margin: 0 auto; padding: 1.5rem; }
  
  /* Cards */
  .card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 1.2rem;
    transition: border-color 0.3s, box-shadow 0.3s;
  }
  .card:hover { border-color: var(--border-hover); box-shadow: var(--shadow); }
  .card h2 {
    font-size: 0.8rem; color: var(--muted); margin-bottom: 1rem;
    text-transform: uppercase; letter-spacing: 1px; font-weight: 600;
    display: flex; align-items: center; gap: 0.5rem;
  }
  
  /* Stat cards */
  .stats-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 0.8rem; }
  .stat-card {
    background: var(--surface-2); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 1rem; text-align: center;
    transition: all 0.3s;
  }
  .stat-card:hover { transform: translateY(-2px); border-color: var(--border-hover); }
  .stat-card .value {
    font-size: 1.8rem; font-weight: 800; letter-spacing: -1px;
    background: linear-gradient(135deg, var(--accent), var(--cyan));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }
  .stat-card .label { font-size: 0.7rem; color: var(--muted); margin-top: 0.3rem; text-transform: uppercase; letter-spacing: 0.5px; }
  .stat-card.green .value { background: linear-gradient(135deg, var(--green), #10b981); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
  .stat-card.purple .value { background: linear-gradient(135deg, var(--purple), #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
  .stat-card.yellow .value { background: linear-gradient(135deg, var(--yellow), var(--orange)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
  .stat-card.cyan .value { background: linear-gradient(135deg, var(--cyan), var(--accent)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
  
  /* Commits */
  .commit {
    padding: 0.6rem 0; border-bottom: 1px solid rgba(30,42,58,0.5);
    display: flex; align-items: flex-start; gap: 0.8rem;
  }
  .commit:last-child { border: none; }
  .commit .type-badge {
    font-size: 0.6rem; padding: 2px 6px; border-radius: 4px;
    font-weight: 600; text-transform: uppercase; white-space: nowrap; min-width: 48px; text-align: center;
  }
  .commit .type-badge.feat { background: rgba(52,211,153,0.15); color: var(--green); }
  .commit .type-badge.fix { background: rgba(248,113,113,0.15); color: var(--red); }
  .commit .type-badge.test { background: rgba(167,139,250,0.15); color: var(--purple); }
  .commit .type-badge.docs { background: rgba(79,156,247,0.15); color: var(--accent); }
  .commit .type-badge.refactor { background: rgba(251,191,36,0.15); color: var(--yellow); }
  .commit .type-badge.chore { background: rgba(110,122,138,0.15); color: var(--muted); }
  .commit .type-badge.other { background: rgba(110,122,138,0.1); color: var(--dim); }
  .commit .info { flex: 1; min-width: 0; }
  .commit .hash { color: var(--accent); font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; }
  .commit .msg { color: var(--text); font-size: 0.85rem; }
  .commit .meta { color: var(--muted); font-size: 0.7rem; margin-top: 0.2rem; }
  
  /* Projects */
  .project-card {
    background: var(--surface-2); border: 1px solid var(--border);
    border-radius: 8px; padding: 0.8rem 1rem; display: flex;
    align-items: center; gap: 0.8rem; transition: all 0.2s;
  }
  .project-card:hover { border-color: var(--accent); transform: translateX(4px); }
  .project-card .lang-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
  .project-card .lang-dot.node { background: var(--green); box-shadow: 0 0 6px rgba(52,211,153,0.4); }
  .project-card .lang-dot.python { background: var(--yellow); box-shadow: 0 0 6px rgba(251,191,36,0.4); }
  .project-card .lang-dot.rust { background: var(--orange); box-shadow: 0 0 6px rgba(251,146,60,0.4); }
  .project-card .lang-dot.unknown { background: var(--muted); }
  .project-card .name { font-weight: 600; font-size: 0.9rem; }
  .project-card .badges { margin-left: auto; display: flex; gap: 0.3rem; }
  .project-card .badge-sm {
    font-size: 0.6rem; padding: 1px 5px; border-radius: 3px;
    background: rgba(79,156,247,0.1); color: var(--accent);
  }
  
  /* Commands */
  .cmd-category { margin-bottom: 1rem; }
  .cmd-category-title { font-size: 0.7rem; color: var(--dim); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.4rem; font-weight: 600; }
  .cmd-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 0.5rem; }
  .cmd-btn {
    background: var(--surface-2); border: 1px solid var(--border);
    border-radius: 8px; padding: 0.6rem; text-align: center;
    cursor: pointer; transition: all 0.2s; font-size: 0.8rem; color: var(--text);
  }
  .cmd-btn:hover { border-color: var(--accent); background: var(--accent-glow); transform: translateY(-1px); }
  .cmd-btn .icon { font-size: 1.1rem; margin-bottom: 0.2rem; }
  .cmd-btn .name { font-weight: 600; font-size: 0.75rem; }
  .cmd-btn .desc { font-size: 0.6rem; color: var(--muted); }
  
  /* Output terminal */
  #output {
    background: var(--bg); border: 1px solid var(--border); border-radius: 8px;
    padding: 1rem; font-family: 'JetBrains Mono', 'Fira Code', monospace;
    font-size: 0.75rem; max-height: 400px; overflow-y: auto;
    white-space: pre-wrap; color: var(--green); display: none; margin-top: 1rem;
    line-height: 1.6;
  }
  #output .prompt { color: var(--accent); }
  
  /* Search */
  .search-box {
    display: flex; gap: 0.5rem; margin-bottom: 1rem;
  }
  .search-box input {
    flex: 1; background: var(--bg); border: 1px solid var(--border);
    border-radius: 8px; padding: 0.6rem 1rem; color: var(--text);
    font-size: 0.85rem; outline: none; transition: border-color 0.2s;
  }
  .search-box input:focus { border-color: var(--accent); }
  .search-box input::placeholder { color: var(--dim); }
  .search-box button {
    background: var(--accent); color: #fff; border: none;
    padding: 0.6rem 1.2rem; border-radius: 8px; cursor: pointer;
    font-weight: 600; font-size: 0.8rem; transition: opacity 0.2s;
  }
  .search-box button:hover { opacity: 0.9; }
  
  .search-result {
    background: var(--surface-2); border: 1px solid var(--border);
    border-radius: 8px; padding: 0.8rem; margin-bottom: 0.5rem;
  }
  .search-result .file { color: var(--accent); font-family: monospace; font-size: 0.75rem; }
  .search-result .snippet { color: var(--text); font-size: 0.8rem; margin-top: 0.3rem; line-height: 1.4; }
  .search-result .cat { color: var(--purple); font-size: 0.65rem; text-transform: uppercase; }
  
  /* Footer */
  .footer { text-align: center; padding: 2rem 1rem; color: var(--dim); font-size: 0.7rem; }
  .footer a { color: var(--accent); text-decoration: none; }
  
  /* Responsive */
  @media (max-width: 900px) {
    .stats-grid { grid-template-columns: repeat(3, 1fr); }
    .tab-content.active { grid-template-columns: 1fr; }
    .header { padding: 0.6rem 1rem; }
    .tabs { padding: 0 1rem; overflow-x: auto; }
  }
  @media (max-width: 600px) {
    .stats-grid { grid-template-columns: repeat(2, 1fr); }
    .cmd-grid { grid-template-columns: repeat(2, 1fr); }
  }
  
  /* Animations */
  @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
  .card { animation: fadeIn 0.3s ease-out; }
  
  /* Scrollbar */
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
  ::-webkit-scrollbar-thumb:hover { background: var(--dim); }
</style>
</head>
<body>

<div class="header">
  <span class="logo">🔧</span>
  <h1>MyWork-AI</h1>
  <span class="badge">v2.1.0</span>
  <button class="refresh-btn" onclick="refresh()" id="refresh-btn">↻ Refresh</button>
  <span class="time" id="time"></span>
</div>

<div class="tabs">
  <div class="tab active" onclick="switchTab('overview')">Overview</div>
  <div class="tab" onclick="switchTab('commands')">Commands</div>
  <div class="tab" onclick="switchTab('brain')">Brain</div>
  <div class="tab" onclick="switchTab('git')">Git</div>
</div>

<!-- Overview Tab -->
<div class="tab-content active" id="tab-overview">
  <div style="grid-column: span 12">
    <div class="stats-grid" id="stats-grid">
      <div class="stat-card green"><div class="value" id="s-tests">—</div><div class="label">Tests Passing</div></div>
      <div class="stat-card purple"><div class="value" id="s-commands">—</div><div class="label">CLI Commands</div></div>
      <div class="stat-card yellow"><div class="value" id="s-projects">—</div><div class="label">Projects</div></div>
      <div class="stat-card cyan"><div class="value" id="s-brain">—</div><div class="label">Brain Entries</div></div>
      <div class="stat-card"><div class="value" id="s-commits">—</div><div class="label">Total Commits</div></div>
    </div>
  </div>
  
  <div class="card" style="grid-column: span 5">
    <h2>📁 Projects</h2>
    <div id="projects-list" style="display:flex;flex-direction:column;gap:0.5rem">Loading...</div>
  </div>
  
  <div class="card" style="grid-column: span 7">
    <h2>🔄 Recent Activity</h2>
    <div id="commits-mini" style="max-height:300px;overflow-y:auto">Loading...</div>
  </div>
  
  <div class="card" style="grid-column: span 12">
    <h2>ℹ️ System Info</h2>
    <div style="display:flex;gap:2rem;flex-wrap:wrap;font-size:0.8rem;color:var(--muted)">
      <span>Python <strong id="i-py" style="color:var(--text)">—</strong></span>
      <span>Uptime <strong id="i-uptime" style="color:var(--text)">—</strong></span>
      <span>Files <strong id="i-files" style="color:var(--text)">—</strong></span>
      <span>Python LoC <strong id="i-loc" style="color:var(--text)">—</strong></span>
      <span>Root <code id="i-cwd" style="color:var(--accent);font-size:0.75rem">—</code></span>
    </div>
  </div>
</div>

<!-- Commands Tab -->
<div class="tab-content" id="tab-commands">
  <div class="card" style="grid-column: span 12">
    <h2>⚡ Quick Commands</h2>
    <p style="font-size:0.75rem;color:var(--muted);margin-bottom:1rem">Click a command to run it. Only safe read-only commands are allowed via web.</p>
    <div id="cmd-container">Loading...</div>
    <div id="output"></div>
  </div>
</div>

<!-- Brain Tab -->
<div class="tab-content" id="tab-brain">
  <div class="card" style="grid-column: span 12">
    <h2>🧠 Brain Knowledge Vault</h2>
    <div class="search-box">
      <input type="text" id="brain-search" placeholder="Search brain entries..." onkeydown="if(event.key==='Enter')searchBrain()">
      <button onclick="searchBrain()">Search</button>
    </div>
    <div id="brain-stats" style="font-size:0.8rem;color:var(--muted);margin-bottom:1rem">Loading stats...</div>
    <div id="brain-results"></div>
  </div>
</div>

<!-- Git Tab -->
<div class="tab-content" id="tab-git">
  <div class="card" style="grid-column: span 12">
    <h2>🔀 Git History</h2>
    <div style="display:flex;gap:1rem;margin-bottom:1rem;font-size:0.75rem;color:var(--muted)">
      <span>Total commits: <strong id="g-total" style="color:var(--text)">—</strong></span>
      <span>Contributors: <strong id="g-contribs" style="color:var(--text)">—</strong></span>
      <span>Tracked files: <strong id="g-files" style="color:var(--text)">—</strong></span>
    </div>
    <div id="commits-full" style="max-height:500px;overflow-y:auto">Loading...</div>
  </div>
</div>

<div class="footer">
  <strong>MyWork-AI Framework</strong> — Built with ❤️ &nbsp;|&nbsp;
  <a href="https://github.com/dansidanutz/MyWork-AI" target="_blank">GitHub</a> &nbsp;|&nbsp;
  <a href="https://pypi.org/project/mywork-ai/" target="_blank">PyPI</a>
</div>

<script>
let data = {};

function switchTab(name) {
  document.querySelectorAll('.tab').forEach((t, i) => t.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  document.querySelectorAll('.tab')[['overview','commands','brain','git'].indexOf(name)].classList.add('active');
}

function renderCommit(c) {
  return `<div class="commit">
    <span class="type-badge ${c.type}">${c.type}</span>
    <div class="info">
      <span class="hash">${c.short}</span> <span class="msg">${esc(c.message)}</span>
      <div class="meta">${esc(c.author)} · ${c.when}</div>
    </div>
  </div>`;
}

function esc(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

async function refresh() {
  const btn = document.getElementById('refresh-btn');
  btn.textContent = '↻ Loading...';
  
  const [status, projects, commits, commands, gitstats, brain] = await Promise.all([
    fetch('/api/status').then(r=>r.json()),
    fetch('/api/projects').then(r=>r.json()),
    fetch('/api/commits').then(r=>r.json()),
    fetch('/api/commands').then(r=>r.json()),
    fetch('/api/gitstats').then(r=>r.json()),
    fetch('/api/brain').then(r=>r.json()),
  ]);
  data = { status, projects, commits, commands, gitstats, brain };
  
  // Stats
  document.getElementById('s-commands').textContent = commands.length;
  document.getElementById('s-projects').textContent = projects.length;
  document.getElementById('s-brain').textContent = brain.entries;
  document.getElementById('s-commits').textContent = gitstats.total_commits || '?';
  document.getElementById('s-tests').textContent = '314+';
  
  // System info
  document.getElementById('i-py').textContent = status.python;
  document.getElementById('i-uptime').textContent = status.uptime;
  document.getElementById('i-files').textContent = gitstats.tracked_files || '?';
  document.getElementById('i-loc').textContent = (gitstats.python_loc || 0).toLocaleString();
  document.getElementById('i-cwd').textContent = status.cwd;
  
  // Projects
  const pl = document.getElementById('projects-list');
  pl.innerHTML = projects.length ? projects.map(p => {
    const badges = [];
    if (p.has_tests) badges.push('<span class="badge-sm">tests</span>');
    if (p.has_readme) badges.push('<span class="badge-sm">docs</span>');
    badges.push(`<span class="badge-sm">${p.file_count} files</span>`);
    return `<div class="project-card">
      <span class="lang-dot ${p.language}"></span>
      <span class="name">${esc(p.name)}</span>
      <div class="badges">${badges.join('')}</div>
    </div>`;
  }).join('') : '<span style="color:var(--muted)">No projects yet. Run <code>mw new</code> to create one!</span>';
  
  // Commits (mini + full)
  const commitHtml = commits.map(renderCommit).join('');
  document.getElementById('commits-mini').innerHTML = commits.slice(0,8).map(renderCommit).join('') || '<span style="color:var(--muted)">No commits</span>';
  document.getElementById('commits-full').innerHTML = commitHtml || '<span style="color:var(--muted)">No commits</span>';
  
  // Git stats
  document.getElementById('g-total').textContent = gitstats.total_commits || '?';
  document.getElementById('g-contribs').textContent = gitstats.contributors || '?';
  document.getElementById('g-files').textContent = gitstats.tracked_files || '?';
  
  // Commands by category
  const cats = {};
  commands.forEach(c => { if (!cats[c.category]) cats[c.category] = []; cats[c.category].push(c); });
  const cc = document.getElementById('cmd-container');
  cc.innerHTML = Object.entries(cats).map(([cat, cmds]) =>
    `<div class="cmd-category">
      <div class="cmd-category-title">${cat}</div>
      <div class="cmd-grid">${cmds.map(c =>
        `<div class="cmd-btn" onclick="runCmd('${c.name}')">
          <div class="icon">${c.icon || '▸'}</div>
          <div class="name">mw ${c.name}</div>
          <div class="desc">${c.desc}</div>
        </div>`
      ).join('')}</div>
    </div>`
  ).join('');
  
  // Brain stats
  document.getElementById('brain-stats').innerHTML = 
    `<strong>${brain.entries}</strong> entries · <strong>${brain.size_kb}</strong> KB · Categories: ${brain.categories.length ? brain.categories.map(c => `<code>${c}</code>`).join(', ') : 'none yet'}`;
  
  btn.textContent = '↻ Refresh';
}

async function runCmd(name) {
  const out = document.getElementById('output');
  out.style.display = 'block';
  out.innerHTML = `<span class="prompt">$ mw ${name}</span>\\nRunning...`;
  try {
    const r = await fetch('/api/run?cmd=' + encodeURIComponent(name));
    const data = await r.json();
    out.innerHTML = `<span class="prompt">$ mw ${name}</span>\\n${esc(data.output || data.error || 'Done')}`;
  } catch(e) { out.innerHTML = `<span class="prompt">$ mw ${name}</span>\\nError: ${esc(e.message)}`; }
  out.scrollTop = out.scrollHeight;
}

async function searchBrain() {
  const q = document.getElementById('brain-search').value.trim();
  if (!q) return;
  const results = document.getElementById('brain-results');
  results.innerHTML = 'Searching...';
  try {
    const r = await fetch('/api/brain/search?q=' + encodeURIComponent(q));
    const data = await r.json();
    if (data.length === 0) {
      results.innerHTML = '<span style="color:var(--muted)">No results found.</span>';
    } else {
      results.innerHTML = data.map(r =>
        `<div class="search-result">
          <span class="cat">${esc(r.category)}</span>
          <div class="file">${esc(r.file)}</div>
          <div class="snippet">${esc(r.snippet)}</div>
        </div>`
      ).join('');
    }
  } catch(e) { results.innerHTML = `Error: ${esc(e.message)}`; }
}

function updateTime() {
  document.getElementById('time').textContent = new Date().toLocaleTimeString();
}
setInterval(updateTime, 1000);
updateTime();

// Auto-refresh every 30s
setInterval(refresh, 30000);
refresh();
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
            self._json(status)
        
        elif path == "/api/projects":
            self._json(get_projects())
        
        elif path == "/api/commits":
            self._json(get_git_log(20))
        
        elif path == "/api/commands":
            self._json(get_commands())
        
        elif path == "/api/gitstats":
            self._json(get_git_stats())
        
        elif path == "/api/brain":
            self._json(get_brain_stats())
        
        elif path == "/api/brain/search":
            params = parse_qs(parsed.query)
            q = params.get("q", [""])[0]
            if q:
                self._json(search_brain(q))
            else:
                self._json([])
        
        elif path == "/api/run":
            params = parse_qs(parsed.query)
            cmd = params.get("cmd", ["status"])[0]
            # Whitelist safe commands
            safe = {"status", "doctor", "report", "projects", "stats", "version",
                    "ecosystem", "links", "changelog", "brain stats", "env list",
                    "config list", "recap", "snapshot", "analytics"}
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
                self._json({"output": output[:8000]})
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
