#!/usr/bin/env python3
"""
MyWork Analytics Engine
=======================
Project analytics, code insights, and health trends.

Commands:
    mw analytics              Full project analytics report
    mw analytics summary      Quick summary
    mw analytics deps         Dependency health check
    mw analytics complexity   Code complexity analysis
    mw analytics trends       Git activity trends
    mw analytics security     Security posture overview
"""

import os
import re
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple


def color(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"

def green(t): return color(t, "32")
def red(t): return color(t, "31")
def yellow(t): return color(t, "33")
def blue(t): return color(t, "34")
def cyan(t): return color(t, "36")
def bold(t): return color(t, "1")
def dim(t): return color(t, "2")


def run_cmd(cmd: str, cwd: str = ".") -> str:
    """Run shell command and return output."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            cwd=cwd, timeout=30
        )
        return result.stdout.strip()
    except Exception:
        return ""


def get_project_root() -> Path:
    """Find project root (has .git or pyproject.toml or package.json)."""
    cwd = Path.cwd()
    for marker in [".git", "pyproject.toml", "package.json", "setup.py"]:
        if (cwd / marker).exists():
            return cwd
    # Walk up
    for parent in cwd.parents:
        for marker in [".git", "pyproject.toml", "package.json", "setup.py"]:
            if (parent / marker).exists():
                return parent
    return cwd


def analyze_languages(root: Path) -> Dict[str, int]:
    """Count lines by language."""
    extensions = {
        ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
        ".tsx": "TypeScript/React", ".jsx": "JavaScript/React",
        ".html": "HTML", ".css": "CSS", ".scss": "SCSS",
        ".json": "JSON", ".yaml": "YAML", ".yml": "YAML",
        ".md": "Markdown", ".sh": "Shell", ".sql": "SQL",
        ".rs": "Rust", ".go": "Go", ".java": "Java",
    }
    counts = Counter()
    skip_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".next", ".tmp"}
    
    for path in root.rglob("*"):
        if any(s in path.parts for s in skip_dirs):
            continue
        if path.is_file() and path.suffix in extensions:
            try:
                lines = len(path.read_text(errors="ignore").splitlines())
                counts[extensions[path.suffix]] += lines
            except Exception:
                pass
    return dict(counts.most_common(10))


def analyze_git_trends(root: Path) -> Dict:
    """Analyze git commit patterns."""
    # Commits per day (last 30 days)
    log = run_cmd(
        'git log --since="30 days ago" --format="%ai" 2>/dev/null',
        cwd=str(root)
    )
    if not log:
        return {"available": False}
    
    dates = []
    for line in log.splitlines():
        if line.strip():
            date_str = line.split()[0]
            dates.append(date_str)
    
    daily = Counter(dates)
    total_commits = len(dates)
    
    # Top contributors
    authors = run_cmd(
        'git log --since="30 days ago" --format="%an" 2>/dev/null',
        cwd=str(root)
    )
    author_counts = Counter(authors.splitlines()) if authors else {}
    
    # Files changed most
    files_changed = run_cmd(
        'git log --since="30 days ago" --name-only --format="" 2>/dev/null',
        cwd=str(root)
    )
    file_counts = Counter(f for f in files_changed.splitlines() if f.strip())
    
    # Streak
    today = datetime.now().date()
    streak = 0
    for i in range(30):
        d = (today - timedelta(days=i)).isoformat()
        if d in daily:
            streak += 1
        else:
            break
    
    return {
        "available": True,
        "total_commits_30d": total_commits,
        "avg_per_day": round(total_commits / 30, 1),
        "active_days": len(daily),
        "current_streak": streak,
        "top_contributors": dict(author_counts.most_common(5)),
        "hottest_files": dict(file_counts.most_common(10)),
        "busiest_day": daily.most_common(1)[0] if daily else None,
    }


def analyze_deps(root: Path) -> Dict:
    """Check dependency health."""
    result = {"python": None, "node": None}
    
    # Python deps
    req_file = root / "requirements.txt"
    if not req_file.exists():
        for sub in ["tools/requirements.txt", "tools/requirements.txt"]:
            if (root / sub).exists():
                req_file = root / sub
                break
    
    if req_file.exists():
        deps = []
        for line in req_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                name = re.split(r'[><=!~]', line)[0].strip()
                if name:
                    deps.append({"name": name, "spec": line})
        result["python"] = {"count": len(deps), "deps": deps[:20]}
    
    # Node deps
    pkg_json = root / "package.json"
    if pkg_json.exists():
        try:
            pkg = json.loads(pkg_json.read_text())
            deps = pkg.get("dependencies", {})
            dev_deps = pkg.get("devDependencies", {})
            result["node"] = {
                "deps": len(deps),
                "devDeps": len(dev_deps),
                "total": len(deps) + len(dev_deps),
            }
        except Exception:
            pass
    
    return result


def analyze_complexity(root: Path) -> Dict:
    """Simple code complexity analysis."""
    skip_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".next"}
    
    total_files = 0
    total_lines = 0
    large_files = []  # >300 lines
    long_functions = []
    todo_count = 0
    
    for path in root.rglob("*.py"):
        if any(s in path.parts for s in skip_dirs):
            continue
        try:
            content = path.read_text(errors="ignore")
            lines = content.splitlines()
            total_files += 1
            total_lines += len(lines)
            
            if len(lines) > 300:
                large_files.append((str(path.relative_to(root)), len(lines)))
            
            # Count TODOs
            for line in lines:
                if "TODO" in line or "FIXME" in line or "HACK" in line:
                    todo_count += 1
            
            # Find long functions
            func_start = None
            func_name = None
            for i, line in enumerate(lines):
                if line.strip().startswith("def ") or line.strip().startswith("async def "):
                    if func_start is not None and (i - func_start) > 50:
                        long_functions.append((func_name, i - func_start, str(path.relative_to(root))))
                    func_name = line.strip().split("(")[0].replace("def ", "").replace("async ", "")
                    func_start = i
            if func_start is not None and func_name and (len(lines) - func_start) > 50:
                long_functions.append((func_name, len(lines) - func_start, str(path.relative_to(root))))
        except Exception:
            pass
    
    # Also scan JS/TS
    for ext in ["*.js", "*.ts", "*.tsx", "*.jsx"]:
        for path in root.rglob(ext):
            if any(s in path.parts for s in skip_dirs):
                continue
            try:
                lines = path.read_text(errors="ignore").splitlines()
                total_files += 1
                total_lines += len(lines)
                if len(lines) > 300:
                    large_files.append((str(path.relative_to(root)), len(lines)))
                for line in lines:
                    if "TODO" in line or "FIXME" in line:
                        todo_count += 1
            except Exception:
                pass
    
    large_files.sort(key=lambda x: x[1], reverse=True)
    long_functions.sort(key=lambda x: x[1], reverse=True)
    
    return {
        "total_files": total_files,
        "total_lines": total_lines,
        "avg_lines_per_file": round(total_lines / max(total_files, 1), 1),
        "large_files": large_files[:10],
        "long_functions": long_functions[:10],
        "todo_fixme_count": todo_count,
    }


def analyze_security(root: Path) -> Dict:
    """Basic security posture check."""
    issues = []
    
    skip_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist"}
    
    # Check for hardcoded secrets patterns
    secret_patterns = [
        (r'(?:password|passwd|pwd)\s*=\s*["\'][^"\']+["\']', "Hardcoded password"),
        (r'(?:api_key|apikey|api_secret)\s*=\s*["\'][^"\']+["\']', "Hardcoded API key"),
        (r'(?:secret_key|SECRET_KEY)\s*=\s*["\'][^"\']{8,}["\']', "Hardcoded secret"),
    ]
    
    secret_files = 0
    for path in root.rglob("*.py"):
        if any(s in path.parts for s in skip_dirs):
            continue
        try:
            content = path.read_text(errors="ignore")
            for pattern, desc in secret_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    secret_files += 1
                    issues.append(f"{desc} in {path.relative_to(root)}")
                    break
        except Exception:
            pass
    
    # Check .env in git
    gitignore = root / ".gitignore"
    env_ignored = False
    if gitignore.exists():
        env_ignored = ".env" in gitignore.read_text()
    
    if not env_ignored:
        issues.append(".env not in .gitignore")
    
    # Check for .env file
    has_env = (root / ".env").exists()
    has_env_example = (root / ".env.example").exists()
    
    return {
        "issues": issues[:20],
        "env_ignored": env_ignored,
        "has_env": has_env,
        "has_env_example": has_env_example,
        "secret_files_flagged": secret_files,
        "score": max(0, 100 - len(issues) * 10),
    }


def print_bar(label: str, value: int, max_val: int, width: int = 30):
    """Print a horizontal bar."""
    if max_val == 0:
        filled = 0
    else:
        filled = int((value / max_val) * width)
    bar = "█" * filled + "░" * (width - filled)
    print(f"  {label:20s} {bar} {value:,}")


def print_section(title: str):
    print(f"\n{bold(cyan(f'━━━ {title} ━━━'))}")


def cmd_analytics(args: List[str] = None) -> int:
    """Run project analytics."""
    root = get_project_root()
    subcmd = args[0] if args else "full"
    
    print(bold(f"\n🔬 MyWork Analytics — {root.name}"))
    print(dim(f"   {root}\n"))
    
    if subcmd in ("full", "summary"):
        print_section("📊 Language Breakdown")
        langs = analyze_languages(root)
        if langs:
            max_lines = max(langs.values())
            for lang, lines in langs.items():
                print_bar(lang, lines, max_lines)
            print(f"\n  {dim('Total:')} {sum(langs.values()):,} lines")
        else:
            print("  No source files found.")
    
    if subcmd in ("full", "trends"):
        print_section("📈 Git Activity (30 days)")
        trends = analyze_git_trends(root)
        if trends.get("available"):
            print(f"  Commits:        {bold(str(trends['total_commits_30d']))}")
            print(f"  Avg/day:        {trends['avg_per_day']}")
            print(f"  Active days:    {trends['active_days']}/30")
            print(f"  Current streak: {green(str(trends['current_streak']))} days")
            if trends.get("busiest_day"):
                print(f"  Busiest day:    {trends['busiest_day'][0]} ({trends['busiest_day'][1]} commits)")
            if trends.get("top_contributors"):
                print(f"\n  {bold('Contributors:')}")
                for name, count in trends["top_contributors"].items():
                    print(f"    {name}: {count} commits")
            if trends.get("hottest_files"):
                print(f"\n  {bold('Most Changed Files:')}")
                for f, count in list(trends["hottest_files"].items())[:5]:
                    print(f"    {dim(str(count)+'x')} {f}")
        else:
            print("  No git history available.")
    
    if subcmd in ("full", "complexity"):
        print_section("🧩 Code Complexity")
        cx = analyze_complexity(root)
        print(f"  Files:          {cx['total_files']}")
        print(f"  Total lines:    {cx['total_lines']:,}")
        print(f"  Avg lines/file: {cx['avg_lines_per_file']}")
        print(f"  TODOs/FIXMEs:   {yellow(str(cx['todo_fixme_count']))}")
        if cx["large_files"]:
            print(f"\n  {bold('Large Files (>300 lines):')}")
            for f, lines in cx["large_files"][:5]:
                print(f"    {red(str(lines))} lines — {f}")
        if cx["long_functions"]:
            print(f"\n  {bold('Long Functions (>50 lines):')}")
            for name, lines, f in cx["long_functions"][:5]:
                print(f"    {yellow(str(lines))} lines — {name}() in {f}")
    
    if subcmd in ("full", "deps"):
        print_section("📦 Dependencies")
        deps = analyze_deps(root)
        if deps["python"]:
            print(f"  Python: {deps['python']['count']} packages")
        if deps["node"]:
            n = deps["node"]
            print(f"  Node:   {n['deps']} deps + {n['devDeps']} devDeps = {n['total']} total")
        if not deps["python"] and not deps["node"]:
            print("  No dependency files found.")
    
    if subcmd in ("full", "security"):
        print_section("🔒 Security Posture")
        sec = analyze_security(root)
        score_color = green if sec["score"] >= 80 else (yellow if sec["score"] >= 50 else red)
        print(f"  Score: {score_color(str(sec['score']) + '/100')}")
        print(f"  .env ignored:   {'✅' if sec['env_ignored'] else '❌'}")
        print(f"  .env exists:    {'✅' if sec['has_env'] else '—'}")
        print(f"  .env.example:   {'✅' if sec['has_env_example'] else '❌'}")
        if sec["issues"]:
            print(f"\n  {bold('Issues:')}")
            for issue in sec["issues"][:5]:
                print(f"    ⚠️  {issue}")
    
    # Overall health score
    if subcmd == "full":
        print_section("🏆 Overall Health")
        cx = analyze_complexity(root)
        sec = analyze_security(root)
        trends = analyze_git_trends(root)
        
        scores = []
        # Activity score
        if trends.get("available"):
            activity = min(100, trends["total_commits_30d"] * 3)
            scores.append(("Activity", activity))
        # Security score
        scores.append(("Security", sec["score"]))
        # Maintainability (inverse of large files ratio)
        if cx["total_files"] > 0:
            large_ratio = len(cx["large_files"]) / cx["total_files"]
            maint = max(0, int(100 - large_ratio * 200))
            scores.append(("Maintainability", maint))
        # Documentation (check for README, docs/)
        doc_score = 0
        if (root / "README.md").exists(): doc_score += 40
        if (root / "docs").is_dir(): doc_score += 30
        if (root / "CHANGELOG.md").exists(): doc_score += 15
        if (root / "CONTRIBUTING.md").exists(): doc_score += 15
        scores.append(("Documentation", doc_score))
        
        overall = int(sum(s for _, s in scores) / max(len(scores), 1))
        
        for name, score in scores:
            c = green if score >= 80 else (yellow if score >= 50 else red)
            bar_len = score // 5
            bar = "█" * bar_len + "░" * (20 - bar_len)
            print(f"  {name:18s} {bar} {c(str(score))}")
        
        overall_color = green if overall >= 80 else (yellow if overall >= 50 else red)
        print(f"\n  {bold('Overall:')} {overall_color(str(overall) + '/100')} {'🌟' if overall >= 90 else '👍' if overall >= 70 else '⚠️'}")
    
    print()
    return 0


if __name__ == "__main__":
    import sys
    cmd_analytics(sys.argv[1:])
