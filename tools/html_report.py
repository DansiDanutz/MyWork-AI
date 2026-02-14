#!/usr/bin/env python3
"""mw webdash — Generate a static HTML project health dashboard."""

import json, os, subprocess, sys, webbrowser
from datetime import datetime
from collections import Counter


def run(cmd, cwd=None):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10, cwd=cwd)
        return r.stdout.strip()
    except Exception:
        return ""


def get_git_stats(d):
    s = {}
    s["total_commits"] = int(run("git rev-list --count HEAD", cwd=d) or "0")
    s["branch"] = run("git branch --show-current", cwd=d)
    log = run("git log --oneline -20 --format='%h|%s|%ci|%an'", cwd=d)
    commits = []
    for line in log.split("\n"):
        if "|" in line:
            p = line.split("|", 3)
            if len(p) >= 3:
                commits.append({"hash": p[0], "message": p[1], "date": p[2][:10], "author": p[3] if len(p) > 3 else ""})
    s["recent_commits"] = commits
    daily = run("git log --since='30 days ago' --format='%cd' --date=short | sort | uniq -c | sort -k2", cwd=d)
    s["daily_commits"] = []
    for line in daily.split("\n"):
        line = line.strip()
        if line:
            p = line.split()
            if len(p) == 2:
                s["daily_commits"].append({"date": p[1], "count": int(p[0])})
    return s


def get_code_metrics(d):
    m = {"total_lines": 0, "total_files": 0, "by_ext": {}}
    exclude = {".git", "node_modules", "__pycache__", "dist", "build", ".mw", "venv", ".venv"}
    exts = {".py", ".js", ".ts", ".tsx", ".jsx", ".css", ".html", ".json", ".yaml", ".yml", ".md", ".sh"}
    for root, dirs, files in os.walk(d):
        dirs[:] = [x for x in dirs if x not in exclude]
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in exts:
                fp = os.path.join(root, f)
                try:
                    with open(fp, "r", errors="ignore") as fh:
                        lines = sum(1 for _ in fh)
                    m["total_lines"] += lines
                    m["total_files"] += 1
                    m["by_ext"].setdefault(ext, {"files": 0, "lines": 0})
                    m["by_ext"][ext]["files"] += 1
                    m["by_ext"][ext]["lines"] += lines
                except Exception:
                    pass
    return m


def get_todos(d):
    tags = ["TODO", "FIXME", "HACK", "XXX"]
    todos = []
    exclude = {".git", "node_modules", "__pycache__", "dist", "build", ".mw", "venv"}
    exts = {".py", ".js", ".ts", ".tsx", ".jsx", ".css", ".html", ".sh"}
    for root, dirs, files in os.walk(d):
        dirs[:] = [x for x in dirs if x not in exclude]
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext not in exts:
                continue
            fp = os.path.join(root, f)
            try:
                with open(fp, "r", errors="ignore") as fh:
                    for i, line in enumerate(fh, 1):
                        for tag in tags:
                            if tag in line:
                                todos.append({"file": os.path.relpath(fp, d), "line": i, "tag": tag, "text": line.strip()[:120]})
                                break
            except Exception:
                pass
    return todos[:50]


def generate_html(name, git, code, todos):
    lang_data = sorted(code["by_ext"].items(), key=lambda x: -x[1]["lines"])[:8]
    lang_labels = json.dumps([e for e, _ in lang_data])
    lang_values = json.dumps([d["lines"] for _, d in lang_data])
    lang_colors = json.dumps(["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899", "#06b6d4", "#84cc16"])
    commit_dates = json.dumps([c["date"] for c in git.get("daily_commits", [])])
    commit_counts = json.dumps([c["count"] for c in git.get("daily_commits", [])])

    tc = {"TODO": "#3b82f6", "FIXME": "#ef4444", "HACK": "#f59e0b", "XXX": "#dc2626"}
    todo_rows = "".join(
        f'<tr><td><span class="tag" style="background:{tc.get(t["tag"],"#6b7280")}">{t["tag"]}</span></td>'
        f'<td class="mono">{t["file"]}:{t["line"]}</td><td class="text-sm">{t["text"][:80]}</td></tr>'
        for t in todos[:25]
    )
    commit_rows = "".join(
        f'<tr><td class="mono hash">{c["hash"]}</td><td>{c["message"][:60]}</td>'
        f'<td class="text-sm text-muted">{c["date"]}</td></tr>'
        for c in git.get("recent_commits", [])[:10]
    )
    now = datetime.now().strftime("%Y-%m-%d %H:%M UTC")

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{name} — Health Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>
:root{{--bg:#0f172a;--surface:#1e293b;--border:#334155;--text:#e2e8f0;--muted:#94a3b8;--accent:#3b82f6;--green:#10b981;--yellow:#f59e0b;--red:#ef4444}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:var(--bg);color:var(--text);padding:2rem}}
.container{{max-width:1200px;margin:0 auto}}
h1{{font-size:2rem;margin-bottom:.5rem}}.subtitle{{color:var(--muted);margin-bottom:2rem}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:1rem;margin-bottom:2rem}}
.card{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:1.5rem}}
.card h3{{font-size:.875rem;color:var(--muted);text-transform:uppercase;letter-spacing:.05em;margin-bottom:.5rem}}
.card .value{{font-size:2rem;font-weight:700}}
.card .value.green{{color:var(--green)}}.card .value.blue{{color:var(--accent)}}.card .value.yellow{{color:var(--yellow)}}
.chart-card{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:1.5rem;margin-bottom:1.5rem}}
.chart-card h2{{font-size:1.125rem;margin-bottom:1rem}}
.two-col{{display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;margin-bottom:1.5rem}}
@media(max-width:768px){{.two-col{{grid-template-columns:1fr}}}}
table{{width:100%;border-collapse:collapse}}
th,td{{padding:.5rem .75rem;text-align:left;border-bottom:1px solid var(--border)}}
th{{color:var(--muted);font-size:.75rem;text-transform:uppercase}}
.mono{{font-family:'SF Mono','Fira Code',monospace;font-size:.8rem}}
.hash{{color:var(--accent)}}
.tag{{display:inline-block;padding:2px 8px;border-radius:4px;color:white;font-size:.7rem;font-weight:600}}
.text-sm{{font-size:.85rem}}.text-muted{{color:var(--muted)}}
.footer{{text-align:center;color:var(--muted);font-size:.8rem;margin-top:3rem;padding-top:1rem;border-top:1px solid var(--border)}}
</style></head><body>
<div class="container">
<h1>📊 {name}</h1><p class="subtitle">Project Health Dashboard — Generated {now}</p>
<div class="grid">
<div class="card"><h3>Lines of Code</h3><div class="value blue">{code['total_lines']:,}</div></div>
<div class="card"><h3>Code Files</h3><div class="value">{code['total_files']:,}</div></div>
<div class="card"><h3>Total Commits</h3><div class="value green">{git['total_commits']:,}</div></div>
<div class="card"><h3>TODO/FIXME Items</h3><div class="value yellow">{len(todos)}</div></div>
</div>
<div class="two-col">
<div class="chart-card"><h2>📈 Commit Activity (30 days)</h2><canvas id="commitChart" height="200"></canvas></div>
<div class="chart-card"><h2>🔤 Languages by Lines</h2><canvas id="langChart" height="200"></canvas></div>
</div>
<div class="chart-card"><h2>📝 Recent Commits</h2>
<table><thead><tr><th>Hash</th><th>Message</th><th>Date</th></tr></thead><tbody>{commit_rows}</tbody></table></div>
<div class="chart-card"><h2>⚠️ TODOs & Tech Debt ({len(todos)} items)</h2>
<table><thead><tr><th>Tag</th><th>Location</th><th>Context</th></tr></thead><tbody>{todo_rows}</tbody></table></div>
<div class="footer">Generated by <strong>mw webdash</strong> — MyWork-AI Framework</div>
</div>
<script>
new Chart(document.getElementById('commitChart'),{{type:'bar',data:{{labels:{commit_dates},datasets:[{{label:'Commits',data:{commit_counts},backgroundColor:'#3b82f680',borderColor:'#3b82f6',borderWidth:1}}]}},options:{{responsive:true,plugins:{{legend:{{display:false}}}},scales:{{y:{{beginAtZero:true,ticks:{{color:'#94a3b8'}},grid:{{color:'#334155'}}}},x:{{ticks:{{color:'#94a3b8',maxRotation:45}},grid:{{display:false}}}}}}}}}});
new Chart(document.getElementById('langChart'),{{type:'doughnut',data:{{labels:{lang_labels},datasets:[{{data:{lang_values},backgroundColor:{lang_colors},borderWidth:0}}]}},options:{{responsive:true,plugins:{{legend:{{position:'right',labels:{{color:'#e2e8f0',padding:12}}}}}}}}}});
</script></body></html>"""


def main(args=None):
    args = args or []
    d = os.getcwd()
    name = os.path.basename(d)
    if "--help" in args or "-h" in args:
        print("mw webdash — Generate a static HTML project health dashboard.\n\nUsage:\n    mw webdash              Generate dashboard\n    mw webdash --no-open    Generate without opening browser\n    mw webdash --output X   Custom output path")
        return 0
    no_open = "--no-open" in args
    output = None
    if "--output" in args:
        idx = args.index("--output")
        if idx + 1 < len(args):
            output = args[idx + 1]
    print("🌐 Generating project dashboard...")
    git = get_git_stats(d)
    code = get_code_metrics(d)
    todos = get_todos(d)
    out = output or os.path.join(d, ".mw", "dashboard.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    html = generate_html(name, git, code, todos)
    with open(out, "w") as f:
        f.write(html)
    print(f"\n✅ Dashboard: {out}")
    print(f"   📊 {code['total_lines']:,} lines | {git['total_commits']} commits | {len(todos)} TODOs")
    if not no_open:
        try:
            webbrowser.open(f"file://{os.path.abspath(out)}")
        except Exception:
            print("   💡 Open in browser manually")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
