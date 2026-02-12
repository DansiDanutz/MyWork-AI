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
    --toc-width: 220px;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

html { scroll-behavior: smooth; }

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
    opacity: 0;
    transition: opacity .5s;
    min-height: 100vh;
}

body.fade-in { opacity: 1; }

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
    z-index: 1001;
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

.hamburger {
    display: none;
    background: none;
    border: none;
    margin-right: 12px;
    margin-left: -8px;
    font-size: 28px;
    color: var(--accent);
    cursor: pointer;
    z-index: 1500;
}

@media (max-width: 768px) {
    .hamburger { display: block; }
}

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
    z-index: 1100;
    transition: transform 0.2s cubic-bezier(.4,0,.2,1);
}

.sidebar.sidebar-mobile-hidden {
    transform: translateX(-100%);
    box-shadow: none;
}

.sidebar.sidebar-mobile-visible {
    transform: translateX(0);
    box-shadow: 2px 0 14px 0 rgba(0,0,0,0.38);
}

.sidebar-backdrop {
    display: none;
    position: fixed;
    left: 0; top: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.28);
    z-index: 1099;
}

.sidebar-backdrop.visible {
    display: block;
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
    min-height: calc(100vh - var(--header-height) - 80px);
    transition: margin-left .2s cubic-bezier(.4,0,.2,1);
}

@media (max-width: 1000px) {
    .content {
        max-width: 100vw;
        padding: 32px 6vw;
    }
}

@media (max-width: 768px) {
    .sidebar { left: 0; top: var(--header-height); width: 78vw; max-width: 330px; }
    .content { margin-left: 0; padding: 22px 3vw; }
}

/* Table of Contents */
.toc-panel {
    position: fixed;
    right: min(12px, 2vw);
    top: calc(var(--header-height) + 30px);
    width: var(--toc-width);
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px 18px 12px 18px;
    font-size: 15px;
    color: var(--text-dim);
    max-height: 60vh;
    overflow-y: auto;
    z-index: 1010;
    box-shadow: 0 6px 24px 0 rgba(0,0,0,0.10);
    display: none;
}
.toc-panel.visible { display: block; }

.toc-panel ul { list-style: none; margin: 0; padding: 0; }
.toc-panel li { margin-bottom: 6px; }
.toc-panel a { color: var(--accent); text-decoration: none; transition: color .14s; }
.toc-panel a:hover, .toc-panel a.active { color: var(--accent-hover); text-decoration: underline; }
.toc-title { font-size: 13px; color: var(--text-dim); font-weight: 700; margin-bottom: 7px; text-transform: uppercase; letter-spacing: 0.8px; }

@media (max-width: 1200px) { .toc-panel { display: none !important; } }

/* Breadcrumbs */
.breadcrumbs {
    margin-bottom: 20px;
    font-size: 14px;
    color: var(--text-dim);
}
.breadcrumbs a { color: var(--accent); text-decoration: none; margin-right: 4px; }
.breadcrumbs span { margin-right: 4px; }
.breadcrumbs .crumb-sep { margin-right: 6px; color: var(--border); }

/* Footer */
.footer {
    text-align: center;
    color: var(--text-dim);
    border-top: 1px solid var(--border);
    margin-top: 44px;
    padding: 23px 0 10px 0;
    font-size: 15px;
    background: var(--surface);
    min-height: 46px;
}
.footer a { color: var(--accent); margin: 0 10px; }

/* Copy button */
.copy-btn {
    float: right;
    position: relative;
    top: -5px;
    right: 2px;
    padding: 1px 12px;
    font-size: 15px;
    background: var(--surface);
    color: var(--accent);
    border: 1px solid var(--border);
    border-radius: 5px;
    cursor: pointer;
    z-index: 2;
    opacity: 0.7;
    transition: opacity .13s, background .13s;
}
.copy-btn:hover { opacity: 1; background: var(--accent); color: var(--bg); }

/* Hero section & grid (index) */
.hero {
    width: 100%;
    padding: 54px 0 38px 0;
    min-height: 240px;
    text-align: center;
    background: linear-gradient(90deg, #58a6ff 16%, #79c0ff 86%, #bc8cff 100%);
    color: #10152f;
    font-family: inherit;
    margin-bottom: 30px;
}
.hero .hero-title {
    font-size: 2.4em;
    font-weight: 800;
    letter-spacing: -1.0px;
    margin-bottom: 13px;
    color: #10152f;
}
.hero .hero-desc {
    max-width: 480px;
    margin: 0 auto 24px auto;
    font-size: 1.18em;
    color: #293653;
}
.hero .get-started {
    display: inline-block;
    background: #10152f;
    color: #fff;
    border-radius: 24px;
    padding: 15px 42px;
    font-size: 1.03em;
    font-weight: 700;
    text-decoration: none;
    box-shadow: 0 3px 10px 0 rgba(88, 166, 255, 0.12);
    transition: background .15s;
    margin-top: 16px;
}
.hero .get-started:hover { background: #293653; color: #fff; }
.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 26px;
    margin: 28px 0 32px 0;
    width: 100%;
}
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 24px 20px 18px 20px;
    box-shadow: 0 8px 22px 0 rgba(88, 166, 255, 0.09);
    color: var(--text);
    transition: transform .13s, box-shadow .13s;
    font-size: 1.095em;
}
.card strong { color: var(--accent); }
.card:hover { transform: translateY(-6px) scale(1.012); box-shadow: 0 3px 26px 0 rgba(88, 166, 255, 0.21); }

/* Back to top */
.back-to-top {
    position: fixed;
    bottom: 38px;
    right: 36px;
    width: 44px;
    height: 44px;
    background: var(--surface);
    color: var(--accent);
    border: 1.5px solid var(--border);
    border-radius: 26px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    cursor: pointer;
    opacity: 0;
    pointer-events: none;
    transition: opacity .14s, background .13s;
    z-index: 2001;
}
.back-to-top.visible {
    opacity: 0.87;
    pointer-events: auto;
}
.back-to-top:hover { background: var(--accent); color: var(--bg); }

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
    """Minimal markdown → HTML converter with code copy buttons."""
    lines = md.split('\n')
    html = []
    in_code = False
    in_list = False
    code_block_number = 0
    for i, line in enumerate(lines):
        # Code blocks
        if line.strip().startswith('```'):
            if in_code:
                html.append('</code></pre>')
                in_code = False
            else:
                lang = line.strip().replace('```', '')
                code_block_number += 1
                btn_html = f'<button class="copy-btn" onclick="copyCodeBlock(this)" aria-label="Copy code">Copy</button>'
                html.append(f'<pre>{btn_html}<code class="lang-{lang}" id="codeblock-{code_block_number}">')
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


def build_breadcrumbs(page_id: str, sidebar_items: list) -> str:
    mapping = {
        'index': [],
        'quickstart': [('index', 'Home')],
        'commands': [('index', 'Home'),],
        'cli-core': [('index', 'Home'), ('commands', 'Reference')],
        'cli-project': [('index', 'Home'), ('commands', 'Reference')],
        'cli-ai': [('index', 'Home'), ('commands', 'Reference')],
        'cli-git': [('index', 'Home'), ('commands', 'Reference')],
        'cli-devops': [('index', 'Home'), ('commands', 'Reference')],
        'architecture': [('index', 'Home'),],
        'changelog': [('index', 'Home')],
    }
    label_map = {i['id']: i['label'].replace('🏠 ','').replace('⌨️ ','').replace('🚀 ','').replace('🏗️ ','').replace('📝 ','') for i in sidebar_items}
    trail = mapping.get(page_id, [('index', 'Home')])
    crumbs = ['<span><a href="index.html">Home</a></span>']
    for pid, _ in trail:
        if pid == 'index': continue
        crumbs.append('<span class="crumb-sep">›</span>')
        crumbs.append(f'<span><a href="{pid}.html">{label_map.get(pid,pid.title())}</a></span>')
    if page_id != 'index':
        crumbs.append('<span class="crumb-sep">›</span>')
        crumbs.append(f'<span>{label_map.get(page_id, page_id.title())}</span>')
    return '<nav class="breadcrumbs">' + ''.join(crumbs) + '</nav>'

def extract_h2s(content_html: str) -> list:
    pattern = r'<h2 id="([^"]+)">(.+?)</h2>'
    return re.findall(pattern, content_html)

def build_toc_panel(h2s: list) -> str:
    if len(h2s) < 2:
        return ''
    toc = '<div class="toc-panel visible"><div class="toc-title">On this page</div><ul>'
    for aid, title in h2s:
        toc += f'<li><a href="#{aid}">{title}</a></li>'
    toc += '</ul></div>'
    return toc


def build_footer(version: str) -> str:
    return f'''<footer class="footer">
        &copy; {datetime.now().year} MyWork-AI &bull;
        <a href="https://github.com/openclaw-ai/mywork-ai" target="_blank">GitHub</a>
        <span> | v{version} | </span>
        Built with <a href="https://github.com/openclaw-ai/mywork-ai" target="_blank">MyWork-AI</a>
    </footer>'''

def build_page(page_id: str, title: str, content_html: str, sidebar_items: list, version: str) -> str:
    sidebar_html = ""
    current_section = ""
    for item in sidebar_items:
        if item.get('section') != current_section:
            current_section = item['section']
            sidebar_html += f'<div class="section-title">{current_section}</div>\n'
        active = ' class="active"' if item['id'] == page_id else ''
        sidebar_html += f'<a href="{item["id"]}.html"{active}>{item["label"]}</a>\n'
    favicon_svg = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 128 128'><rect width='128' height='128' fill='%230d1117'/><text x='50%' y='56%' text-anchor='middle' fill='%2358a6ff' font-family='monospace' font-size='70' font-weight='bold' dy='.3em'>MW</text></svg>"
    breadcrumbs = build_breadcrumbs(page_id, sidebar_items)
    h2s = extract_h2s(content_html)
    toc_panel = build_toc_panel(h2s)
    footer_html = build_footer(version)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — MyWork-AI Docs</title>
<link rel="icon" type="image/svg+xml" href="{favicon_svg}" />
<style>{SITE_CSS}</style>
</head>
<body>
<div class="header">
    <button class="hamburger" id="hamburger" aria-label="Open menu">&#9776;</button>
    <h1>MyWork-AI <span>Docs</span></h1>
    <span class="version">v{version}</span>
    <input class="search" type="text" placeholder="Search docs..." id="search">
</div>
<div class="sidebar-backdrop" id="sidebar-backdrop"></div>
<nav class="sidebar sidebar-mobile-hidden" id="sidebar">
{sidebar_html}
</nav>
<main class="content">
{breadcrumbs}
{content_html}
</main>
{toc_panel}
{footer_html}
<button class="back-to-top" id="backToTop" title="Back to top">&#8593;</button>
<script>
// Fade-in transition
window.addEventListener('DOMContentLoaded', function () {{ document.body.classList.add('fade-in'); }});

// Mobile sidebar hamburger toggle
const hamburger = document.getElementById('hamburger');
const sidebar = document.getElementById('sidebar');
const backdrop = document.getElementById('sidebar-backdrop');
function openSidebar() {{ sidebar.classList.remove('sidebar-mobile-hidden'); sidebar.classList.add('sidebar-mobile-visible'); backdrop.classList.add('visible'); }}
function closeSidebar() {{ sidebar.classList.add('sidebar-mobile-hidden'); sidebar.classList.remove('sidebar-mobile-visible'); backdrop.classList.remove('visible'); }}
hamburger.addEventListener('click', openSidebar);
backdrop.addEventListener('click', closeSidebar);
window.addEventListener('resize', function() {{ if(window.innerWidth > 768) closeSidebar(); }});

// Keyboard shortcut to focus search
window.addEventListener('keydown', function(e) {{
    if ((e.ctrlKey && e.key==='k') || e.key==='/') {{
        if(document.activeElement !== document.getElementById('search')) {{
            e.preventDefault();
            document.getElementById('search').focus();
        }}
    }}
}});
// Search filter
const searchInput = document.getElementById('search');
searchInput.addEventListener('input', function(e) {{
    const q = e.target.value.toLowerCase();
    document.querySelectorAll('.content h2, .content h3, .content p, .content .cmd-card').forEach(el => {{
        el.style.display = el.textContent.toLowerCase().includes(q) || !q ? '' : 'none';
    }});
}});

// Smooth-scroll anchor offset for fixed header
function scrollIfAnchor() {{
    if(location.hash.length > 1) {{
        var el = document.getElementById(location.hash.slice(1));
        if(el) {{
            var y = el.getBoundingClientRect().top + window.pageYOffset - 64;
            window.scrollTo({{top:y,behavior:'smooth'}});
        }}
    }}
}}
window.addEventListener('hashchange', scrollIfAnchor, false);
window.addEventListener('DOMContentLoaded', scrollIfAnchor);

// Copy code blocks
function copyCodeBlock(btn) {{
    var code = btn.parentElement.querySelector('code');
    if(!code) return;
    var text = code.innerText;
    navigator.clipboard.writeText(text).then(function() {{
        btn.textContent = 'Copied!';
        setTimeout(() => {{ btn.textContent = 'Copy'; }}, 1600);
    }});
}}

// Back to top button
const backToTop = document.getElementById('backToTop');
window.addEventListener('scroll', function() {{
    if(window.scrollY > 170) backToTop.classList.add('visible');
    else backToTop.classList.remove('visible');
}});
backToTop.addEventListener('click', function() {{
    window.scrollTo({{ top:0, behavior:'smooth' }});
}});

// TOC highlight
if(document.querySelector('.toc-panel')) {{
    let tocLinks = document.querySelectorAll('.toc-panel a');
    function tocHighlight() {{
        let lastActive = null;
        tocLinks.forEach(function(link) {{
            var target = document.getElementById(link.hash.substr(1));
            if (target && window.scrollY+66>=target.offsetTop) lastActive = link;
            link.classList.remove('active');
        }});
        if(lastActive) lastActive.classList.add('active');
    }}
    window.addEventListener('scroll', tocHighlight);
    tocHighlight();
}}
</script>
</body>
</html>'''


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
    hero_html = f'''
      <section class="hero">
        <div class="hero-title">AI-Powered Development Framework</div>
        <div class="hero-desc">Build, test, deploy, &amp; orchestrate apps — from idea to production — with pure Python &amp; AI superpowers. <br> Save days per project with seamless automation.</div>
        <a href="quickstart.html" class="get-started">Get Started &rarr;</a>
      </section>
      <div class="grid">
        <div class="card"><strong>Unified CLI</strong> for scaffolding, management, health, &amp; orchestration across all your projects.<br><code>mw new</code>, <code>mw health</code>, <code>mw dashboard</code></div>
        <div class="card"><strong>AI Integration</strong> at every stage: code review, bug fixes, docs, tests &mdash; all accessible via <code>mw ai</code></div>
        <div class="card"><strong>Auto Testing</strong>: run, detect, and generate tests with one command. <code>mw test</code></div>
        <div class="card"><strong>Smart Git</strong>: automatic commit/message, branch, undo &mdash; <code>mw git commit</code></div>
        <div class="card"><strong>Deployment</strong>: <code>mw deploy</code> to Vercel, Railway, Docker, more.</div>
        <div class="card"><strong>Plugin System</strong>: extend with <code>mw plugin</code> for custom logic/tools</div>
        <div class="card"><strong>Knowledge Brain</strong>: AI learns your patterns, stores lessons with <code>mw brain</code></div>
        <div class="card"><strong>Web Dashboard</strong>: <code>mw serve</code> offers full browser UI</div>
      </div>
      <div class="stats-bar">
        <div class="stat"><div class="num">48+</div><div class="label">Commands</div></div>
        <div class="stat"><div class="num">{n_tools}</div><div class="label">Modules</div></div>
        <div class="stat"><div class="num">{n_tests}</div><div class="label">Test Files</div></div>
        <div class="stat"><div class="num">v{version}</div><div class="label">Version</div></div>
      </div>
      <div style="text-align:center; margin-top:28px; color:var(--text-dim);">Install: <code>pip install mywork-ai</code> &nbsp; | &nbsp; <a href="quickstart.html">Quick Start</a></div>
    '''
    (out / "index.html").write_text(build_page("index", "Home", hero_html, sidebar, version))

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
