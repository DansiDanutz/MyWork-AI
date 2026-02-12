#!/usr/bin/env python3
"""MyWork-AI Documentation Site Generator.

Generates a static HTML documentation site from:
- README.md
- All mw command help texts
- CHANGELOG.md
- CONTRIBUTING.md

Usage:
    python3 tools/docs_site.py build [--output docs_site]
    python3 tools/docs_site.py serve [--port 8080]
"""

import os
import sys
import json
import http.server
import socketserver
import subprocess
import re
from pathlib import Path
from datetime import datetime

MYWORK_ROOT = Path(__file__).resolve().parent.parent

# ─── HTML Template ───────────────────────────────────────────────────────────

SITE_CSS = """
:root {
    --bg: #0d1117;
    --surface: #161b22;
    --border: #30363d;
    --text: #e6edf3;
    --text-dim: #8b949e;
    --accent: #58a6ff;
    --accent-hover: #79c0ff;
    --green: #3fb950;
    --yellow: #d29922;
    --red: #f85149;
    --purple: #bc8cff;
    --sidebar-width: 280px;
    --header-height: 60px;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
}

/* Header */
.header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: var(--header-height);
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    padding: 0 24px;
    z-index: 100;
}

.header h1 {
    font-size: 20px;
    font-weight: 600;
    color: var(--accent);
}

.header h1 span { color: var(--text-dim); font-weight: 400; }

.header .version {
    margin-left: 12px;
    padding: 2px 8px;
    background: rgba(88,166,255,0.15);
    color: var(--accent);
    border-radius: 12px;
    font-size: 12px;
}

.header .search {
    margin-left: auto;
    padding: 6px 12px;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    color: var(--text);
    font-size: 14px;
    width: 240px;
    outline: none;
}

.header .search:focus { border-color: var(--accent); }

/* Sidebar */
.sidebar {
    position: fixed;
    top: var(--header-height);
    left: 0;
    bottom: 0;
    width: var(--sidebar-width);
    background: var(--surface);
    border-right: 1px solid var(--border);
    overflow-y: auto;
    padding: 16px 0;
}

.sidebar .section-title {
    padding: 8px 20px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-dim);
}

.sidebar a {
    display: block;
    padding: 6px 20px 6px 28px;
    color: var(--text-dim);
    text-decoration: none;
    font-size: 14px;
    transition: all 0.15s;
}

.sidebar a:hover { color: var(--text); background: rgba(255,255,255,0.04); }
.sidebar a.active { color: var(--accent); background: rgba(88,166,255,0.08); border-right: 2px solid var(--accent); }

/* Content */
.content {
    margin-left: var(--sidebar-width);
    margin-top: var(--header-height);
    padding: 40px 48px;
    max-width: 900px;
}

.content h1 { font-size: 32px; margin-bottom: 8px; color: var(--text); }
.content h2 { font-size: 24px; margin: 32px 0 12px; color: var(--text); padding-bottom: 8px; border-bottom: 1px solid var(--border); }
.content h3 { font-size: 18px; margin: 24px 0 8px; color: var(--text); }
.content p { margin-bottom: 16px; color: var(--text-dim); }
.content ul, .content ol { margin: 0 0 16px 24px; color: var(--text-dim); }
.content li { margin-bottom: 4px; }
.content a { color: var(--accent); text-decoration: none; }
.content a:hover { text-decoration: underline; }

.content code {
    background: rgba(110,118,129,0.2);
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 13px;
    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
}

.content pre {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px;
    overflow-x: auto;
    margin-bottom: 16px;
}

.content pre code { background: none; padding: 0; font-size: 13px; color: var(--text); }

/* Command card */
.cmd-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 16px;
}

.cmd-card .cmd-name {
    font-family: monospace;
    font-size: 16px;
    font-weight: 600;
    color: var(--green);
    margin-bottom: 8px;
}

.cmd-card .cmd-desc { color: var(--text-dim); font-size: 14px; }

/* Stats bar */
.stats-bar {
    display: flex;
    gap: 24px;
    margin: 24px 0;
    padding: 16px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
}

.stat { text-align: center; }
.stat .num { font-size: 28px; font-weight: 700; color: var(--accent); }
.stat .label { font-size: 12px; color: var(--text-dim); text-transform: uppercase; }

/* Responsive */
@media (max-width: 768px) {
    .sidebar { display: none; }
    .content { margin-left: 0; padding: 24px 16px; }
}
"""


def get_version():
    """Read version from pyproject.toml or mw.py."""
    toml_path = MYWORK_ROOT / "pyproject.toml"
    if toml_path.exists():
        for line in toml_path.read_text().splitlines():
            if line.strip().startswith("version"):
                m = re.search(r'"([^"]+)"', line)
                if m:
                    return m.group(1)
    return "2.0.0"


def get_commands():
    """Extract command info from mw help output."""
    try:
        r = subprocess.run(
            [sys.executable, str(MYWORK_ROOT / "tools" / "mw.py"), "help"],
            capture_output=True, text=True, timeout=10, cwd=str(MYWORK_ROOT)
        )
        return r.stdout
    except Exception:
        return ""


def markdown_to_html(md: str) -> str:
    """Minimal markdown → HTML converter."""
    lines = md.split('\n')
    html = []
    in_code = False
    in_list = False

    for line in lines:
        # Code blocks
        if line.strip().startswith('```'):
            if in_code:
                html.append('</code></pre>')
                in_code = False
            else:
                lang = line.strip().replace('```', '')
                html.append(f'<pre><code class="lang-{lang}">')
                in_code = True
            continue

        if in_code:
            html.append(line.replace('<', '&lt;').replace('>', '&gt;'))
            continue

        # Close list if non-list line
        if in_list and not line.strip().startswith('- ') and not line.strip().startswith('* ') and line.strip():
            html.append('</ul>')
            in_list = False

        # Headers
        if line.startswith('#### '):
            html.append(f'<h4>{line[5:]}</h4>')
        elif line.startswith('### '):
            html.append(f'<h3>{line[4:]}</h3>')
        elif line.startswith('## '):
            anchor = re.sub(r'[^a-z0-9]+', '-', line[3:].strip().lower()).strip('-')
            html.append(f'<h2 id="{anchor}">{line[3:]}</h2>')
        elif line.startswith('# '):
            html.append(f'<h1>{line[2:]}</h1>')
        # List items
        elif line.strip().startswith('- ') or line.strip().startswith('* '):
            if not in_list:
                html.append('<ul>')
                in_list = True
            content = line.strip()[2:]
            # Inline code
            content = re.sub(r'`([^`]+)`', r'<code>\1</code>', content)
            # Bold
            content = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', content)
            # Links
            content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', content)
            html.append(f'<li>{content}</li>')
        # Empty lines
        elif not line.strip():
            if in_list:
                html.append('</ul>')
                in_list = False
            html.append('')
        # Paragraphs
        else:
            content = line
            content = re.sub(r'`([^`]+)`', r'<code>\1</code>', content)
            content = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', content)
            content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', content)
            html.append(f'<p>{content}</p>')

    if in_list:
        html.append('</ul>')
    if in_code:
        html.append('</code></pre>')

    return '\n'.join(html)


def parse_commands(help_text: str) -> list:
    """Parse commands from help output into structured data."""
    commands = []
    current_section = ""
    for line in help_text.split('\n'):
        if line.strip() and not line.startswith(' ') and line.endswith(':'):
            current_section = line.strip().rstrip(':')
        m = re.match(r'\s{4}(mw \S+.*?)\s{2,}(.+)', line)
        if m:
            commands.append({
                'usage': m.group(1).strip(),
                'desc': m.group(2).strip(),
                'section': current_section
            })
    return commands


def count_tests():
    """Count test files."""
    test_dir = MYWORK_ROOT / "tests"
    if test_dir.exists():
        return len([f for f in test_dir.iterdir() if f.name.startswith("test_") and f.suffix == ".py"])
    return 0


def count_tools():
    """Count tool files."""
    tools_dir = MYWORK_ROOT / "tools"
    if tools_dir.exists():
        return len([f for f in tools_dir.iterdir() if f.suffix == ".py" and not f.name.startswith("_")])
    return 0


def build_page(page_id: str, title: str, content_html: str, sidebar_items: list, version: str) -> str:
    """Build a full HTML page."""
    sidebar_html = ""
    current_section = ""
    for item in sidebar_items:
        if item.get('section') != current_section:
            current_section = item['section']
            sidebar_html += f'<div class="section-title">{current_section}</div>\n'
        active = ' class="active"' if item['id'] == page_id else ''
        sidebar_html += f'<a href="{item["id"]}.html"{active}>{item["label"]}</a>\n'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — MyWork-AI Docs</title>
<style>{SITE_CSS}</style>
</head>
<body>
<div class="header">
    <h1>MyWork-AI <span>Docs</span></h1>
    <span class="version">v{version}</span>
    <input class="search" type="text" placeholder="Search docs..." id="search">
</div>
<nav class="sidebar">
{sidebar_html}
</nav>
<main class="content">
{content_html}
</main>
<script>
document.getElementById('search').addEventListener('input', function(e) {{
    const q = e.target.value.toLowerCase();
    document.querySelectorAll('.content h2, .content h3, .content p, .content .cmd-card').forEach(el => {{
        el.style.display = el.textContent.toLowerCase().includes(q) || !q ? '' : 'none';
    }});
}});
</script>
</body>
</html>"""


def build_site(output_dir: str = "docs_site"):
    """Build the complete documentation site."""
    out = MYWORK_ROOT / output_dir
    out.mkdir(parents=True, exist_ok=True)

    version = get_version()
    help_text = get_commands()
    commands = parse_commands(help_text)
    n_tests = count_tests()
    n_tools = count_tools()

    # Sidebar navigation
    sidebar = [
        {'id': 'index', 'label': '🏠 Home', 'section': 'Getting Started'},
        {'id': 'quickstart', 'label': '🚀 Quick Start', 'section': 'Getting Started'},
        {'id': 'commands', 'label': '⌨️ All Commands', 'section': 'Reference'},
        {'id': 'cli-core', 'label': 'Core Commands', 'section': 'Reference'},
        {'id': 'cli-project', 'label': 'Project Commands', 'section': 'Reference'},
        {'id': 'cli-ai', 'label': 'AI Commands', 'section': 'Reference'},
        {'id': 'cli-git', 'label': 'Git Commands', 'section': 'Reference'},
        {'id': 'cli-devops', 'label': 'DevOps Commands', 'section': 'Reference'},
        {'id': 'architecture', 'label': '🏗️ Architecture', 'section': 'Guides'},
        {'id': 'changelog', 'label': '📝 Changelog', 'section': 'Guides'},
    ]

    # ── Index page ──
    stats_html = f"""
    <h1>MyWork-AI Documentation</h1>
    <p>The AI-Powered Development Framework — build complete apps from idea to deployment.</p>
    <div class="stats-bar">
        <div class="stat"><div class="num">48+</div><div class="label">Commands</div></div>
        <div class="stat"><div class="num">{n_tools}</div><div class="label">Modules</div></div>
        <div class="stat"><div class="num">{n_tests}</div><div class="label">Test Files</div></div>
        <div class="stat"><div class="num">v{version}</div><div class="label">Version</div></div>
    </div>
    <h2>What is MyWork-AI?</h2>
    <p>MyWork-AI (<code>mw</code>) is a unified CLI framework that brings together project scaffolding,
    AI-assisted development, automated testing, linting, deployment, and knowledge management
    into a single tool.</p>
    <h2>Key Features</h2>
    <ul>
    <li><strong>Project Scaffolding</strong> — <code>mw new</code> creates projects from 6+ templates</li>
    <li><strong>AI Assistant</strong> — <code>mw ai</code> for code review, fixes, refactoring, docs</li>
    <li><strong>Smart Git</strong> — <code>mw git commit</code> auto-generates commit messages</li>
    <li><strong>Universal Testing</strong> — <code>mw test</code> auto-detects your test framework</li>
    <li><strong>Deployment</strong> — <code>mw deploy</code> to Vercel, Railway, Render, Docker</li>
    <li><strong>CI/CD Generation</strong> — <code>mw ci</code> generates GitHub Actions / GitLab CI</li>
    <li><strong>Plugin System</strong> — <code>mw plugin</code> for extensibility</li>
    <li><strong>Knowledge Brain</strong> — <code>mw brain</code> stores and retrieves lessons</li>
    <li><strong>Web Dashboard</strong> — <code>mw serve</code> for a browser-based UI</li>
    </ul>
    <h2>Install</h2>
    <pre><code>pip install mywork-ai
mw setup</code></pre>
    """
    (out / "index.html").write_text(build_page("index", "Home", stats_html, sidebar, version))

    # ── Quick Start page ──
    qs_html = """
    <h1>🚀 Quick Start</h1>
    <h2>1. Install</h2>
    <pre><code>pip install mywork-ai
mw setup</code></pre>
    <h2>2. Create a Project</h2>
    <pre><code># Enhance your idea into a detailed spec
mw prompt-enhance "build a SaaS invoice tool"

# Create from template
mw new invoice-app fullstack</code></pre>
    <h2>3. Develop with AI</h2>
    <pre><code># AI code review
mw ai review --staged

# Auto-fix bugs
mw ai fix src/main.py

# Generate tests
mw ai test src/main.py</code></pre>
    <h2>4. Test & Deploy</h2>
    <pre><code># Run tests (auto-detects framework)
mw test

# Deploy to Vercel
mw deploy my-app --platform vercel</code></pre>
    <h2>5. Monitor</h2>
    <pre><code># Check project health
mw health my-app

# Full diagnostics
mw doctor</code></pre>
    """
    (out / "quickstart.html").write_text(build_page("quickstart", "Quick Start", qs_html, sidebar, version))

    # ── Commands overview ──
    cmd_sections = {}
    for cmd in commands:
        s = cmd['section'] or 'Other'
        cmd_sections.setdefault(s, []).append(cmd)

    cmds_html = "<h1>⌨️ All Commands</h1>\n<p>Complete reference for all <code>mw</code> commands.</p>\n"
    for section, cmds in cmd_sections.items():
        cmds_html += f"<h2>{section}</h2>\n"
        for c in cmds:
            cmds_html += f"""<div class="cmd-card">
<div class="cmd-name">{c['usage']}</div>
<div class="cmd-desc">{c['desc']}</div>
</div>\n"""

    (out / "commands.html").write_text(build_page("commands", "All Commands", cmds_html, sidebar, version))

    # ── Category pages ──
    categories = {
        'cli-core': {
            'title': 'Core Commands',
            'cmds': ['status', 'dashboard', 'doctor', 'report', 'fix', 'setup', 'guide', 'version', 'config'],
            'desc': 'Essential commands for framework health and configuration.'
        },
        'cli-project': {
            'title': 'Project Commands',
            'cmds': ['new', 'projects', 'open', 'cd', 'health', 'snapshot', 'scan', 'search'],
            'desc': 'Create, manage, and monitor projects.'
        },
        'cli-ai': {
            'title': 'AI Commands',
            'cmds': ['ai ask', 'ai explain', 'ai fix', 'ai refactor', 'ai test', 'ai commit', 'ai review', 'ai doc', 'ai changelog', 'prompt-enhance'],
            'desc': 'AI-powered development assistance.'
        },
        'cli-git': {
            'title': 'Git Commands',
            'cmds': ['git status', 'git commit', 'git log', 'git branch', 'git diff', 'git push', 'git pull', 'git stash', 'git undo', 'release'],
            'desc': 'Smart git operations with auto-generated messages.'
        },
        'cli-devops': {
            'title': 'DevOps Commands',
            'cmds': ['deploy', 'monitor', 'ci', 'env', 'test', 'lint', 'security', 'audit', 'backup', 'db'],
            'desc': 'Deployment, CI/CD, testing, and infrastructure management.'
        },
    }

    for cat_id, cat in categories.items():
        cat_html = f"<h1>{cat['title']}</h1>\n<p>{cat['desc']}</p>\n"
        for cmd_name in cat['cmds']:
            matching = [c for c in commands if cmd_name in c['usage']]
            if matching:
                for c in matching:
                    cat_html += f"""<div class="cmd-card">
<div class="cmd-name">{c['usage']}</div>
<div class="cmd-desc">{c['desc']}</div>
</div>\n"""
            else:
                cat_html += f"""<div class="cmd-card">
<div class="cmd-name">mw {cmd_name}</div>
<div class="cmd-desc">See <code>mw {cmd_name} --help</code> for details.</div>
</div>\n"""
        (out / f"{cat_id}.html").write_text(build_page(cat_id, cat['title'], cat_html, sidebar, version))

    # ── Architecture page ──
    arch_html = """
    <h1>🏗️ Architecture</h1>
    <h2>Directory Structure</h2>
    <pre><code>MyWork-AI/
├── tools/           # All command implementations (50+ modules)
│   ├── mw.py        # Main CLI entry point & router
│   ├── ai_assistant.py
│   ├── db_manager.py
│   ├── web_dashboard.py
│   └── ...
├── tests/           # Comprehensive test suite
├── gsd/             # Project planning & orchestration
├── wat/             # Workflows, Agents, Tools layer
├── projects/        # Generated projects live here
├── .planning/       # Roadmap, state, phase plans
└── .mw/             # Runtime data (brain, config, snapshots)</code></pre>
    <h2>How It Works</h2>
    <p>The <code>mw</code> CLI is a single entry point that routes commands to specialized tool modules.
    Each module is a standalone Python file in <code>tools/</code> that handles one domain.</p>
    <h3>Command Flow</h3>
    <pre><code>User → mw &lt;command&gt; → tools/mw.py (router) → tools/&lt;module&gt;.py → Output</code></pre>
    <h3>Key Design Principles</h3>
    <ul>
    <li><strong>Zero config</strong> — works out of the box with sensible defaults</li>
    <li><strong>Auto-detection</strong> — detects project type, test framework, deploy target</li>
    <li><strong>Modular</strong> — each command is independent, easy to extend</li>
    <li><strong>AI-native</strong> — AI integrated at every level (review, fix, generate, explain)</li>
    </ul>
    """
    (out / "architecture.html").write_text(build_page("architecture", "Architecture", arch_html, sidebar, version))

    # ── Changelog page ──
    changelog_path = MYWORK_ROOT / "CHANGELOG.md"
    if changelog_path.exists():
        cl_md = changelog_path.read_text()[:20000]  # Limit size
        cl_html = "<h1>📝 Changelog</h1>\n" + markdown_to_html(cl_md)
    else:
        cl_html = "<h1>📝 Changelog</h1>\n<p>No CHANGELOG.md found.</p>"
    (out / "changelog.html").write_text(build_page("changelog", "Changelog", cl_html, sidebar, version))

    # Count pages
    pages = list(out.glob("*.html"))
    print(f"\n\033[92m✅ Documentation site built!\033[0m")
    print(f"   📁 Output: {out}")
    print(f"   📄 Pages: {len(pages)}")
    print(f"   🌐 Open: file://{out}/index.html")
    print(f"   🚀 Serve: mw docs serve --port 8080")
    return 0


def serve_site(port: int = 8080, output_dir: str = "docs_site"):
    """Serve the docs site locally."""
    site_dir = MYWORK_ROOT / output_dir
    if not site_dir.exists() or not (site_dir / "index.html").exists():
        print("📦 Building docs site first...")
        build_site(output_dir)

    os.chdir(str(site_dir))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"\n🌐 Docs server running at http://localhost:{port}")
        print(f"   Press Ctrl+C to stop\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped.")
    return 0


def cmd_docs_site(args=None):
    """Entry point for mw docs site."""
    args = args or []
    if not args or args[0] == "build":
        output = "docs_site"
        for i, a in enumerate(args):
            if a == "--output" and i + 1 < len(args):
                output = args[i + 1]
        return build_site(output)
    elif args[0] == "serve":
        port = 8080
        for i, a in enumerate(args):
            if a == "--port" and i + 1 < len(args):
                port = int(args[i + 1])
        return serve_site(port)
    else:
        print("Usage: mw docs site build [--output dir]")
        print("       mw docs site serve [--port 8080]")
        return 1


if __name__ == "__main__":
    sys.exit(cmd_docs_site(sys.argv[1:]))
