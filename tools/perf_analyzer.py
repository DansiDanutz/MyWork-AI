#!/usr/bin/env python3
"""
mw perf — Project Performance Analyzer
=======================================
Analyzes project health metrics: dependency bloat, startup time,
file structure, code complexity, and provides optimization tips.
"""

import os
import sys
import json
import time
import subprocess
import re
from pathlib import Path
from collections import Counter, defaultdict

# Colors
class C:
    B = "\033[1m"
    G = "\033[92m"
    Y = "\033[93m"
    R = "\033[91m"
    CYAN = "\033[96m"
    E = "\033[0m"
    DIM = "\033[2m"

def find_project_root(start="."):
    """Find project root by looking for common markers."""
    p = Path(start).resolve()
    markers = ["package.json", "pyproject.toml", "setup.py", "Cargo.toml", "go.mod", "Makefile"]
    while p != p.parent:
        if any((p / m).exists() for m in markers):
            return p
        p = p.parent
    return Path(start).resolve()

def detect_stack(root: Path) -> dict:
    """Detect project stack and language."""
    stack = {"lang": "unknown", "framework": None, "pkg_manager": None}
    if (root / "package.json").exists():
        stack["lang"] = "node"
        stack["pkg_manager"] = "npm"
        if (root / "yarn.lock").exists():
            stack["pkg_manager"] = "yarn"
        elif (root / "pnpm-lock.yaml").exists():
            stack["pkg_manager"] = "pnpm"
        try:
            pkg = json.loads((root / "package.json").read_text())
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            if "next" in deps: stack["framework"] = "Next.js"
            elif "react" in deps: stack["framework"] = "React"
            elif "vue" in deps: stack["framework"] = "Vue"
            elif "svelte" in deps: stack["framework"] = "Svelte"
            elif "express" in deps: stack["framework"] = "Express"
        except: pass
    elif (root / "pyproject.toml").exists() or (root / "setup.py").exists():
        stack["lang"] = "python"
        stack["pkg_manager"] = "pip"
    elif (root / "Cargo.toml").exists():
        stack["lang"] = "rust"
        stack["pkg_manager"] = "cargo"
    elif (root / "go.mod").exists():
        stack["lang"] = "go"
        stack["pkg_manager"] = "go mod"
    return stack

def analyze_dependencies(root: Path, stack: dict) -> dict:
    """Analyze dependency count and potential bloat."""
    result = {"total": 0, "prod": 0, "dev": 0, "unused_candidates": [], "heavy": []}
    
    if stack["lang"] == "node" and (root / "package.json").exists():
        try:
            pkg = json.loads((root / "package.json").read_text())
            prod = pkg.get("dependencies", {})
            dev = pkg.get("devDependencies", {})
            result["prod"] = len(prod)
            result["dev"] = len(dev)
            result["total"] = len(prod) + len(dev)
            
            # Known heavy packages
            heavy_pkgs = {"moment": "dayjs", "lodash": "lodash-es or native", "webpack": "esbuild/vite",
                         "babel": "swc", "node-sass": "sass", "request": "undici/fetch",
                         "uuid": "crypto.randomUUID()", "axios": "fetch"}
            for dep in prod:
                base = dep.split("/")[-1] if "/" in dep else dep
                if base in heavy_pkgs:
                    result["heavy"].append({"name": dep, "alternative": heavy_pkgs[base]})
            
            # Check node_modules size
            nm = root / "node_modules"
            if nm.exists():
                try:
                    out = subprocess.run(["du", "-sh", str(nm)], capture_output=True, text=True, timeout=10)
                    result["node_modules_size"] = out.stdout.split()[0] if out.returncode == 0 else "?"
                except: pass
        except: pass
    
    elif stack["lang"] == "python":
        req_files = list(root.glob("requirements*.txt"))
        if req_files:
            all_deps = set()
            for rf in req_files:
                for line in rf.read_text().splitlines():
                    line = line.strip()
                    if line and not line.startswith("#") and not line.startswith("-"):
                        name = re.split(r'[>=<!\[]', line)[0].strip()
                        if name:
                            all_deps.add(name)
            result["total"] = len(all_deps)
            result["prod"] = len(all_deps)
    
    return result

def analyze_file_structure(root: Path) -> dict:
    """Analyze file counts, sizes, and structure."""
    stats = {"total_files": 0, "total_size": 0, "by_ext": Counter(), "largest_files": [],
             "empty_files": 0, "deep_nesting": 0}
    
    skip_dirs = {".git", "node_modules", "__pycache__", ".next", "dist", "build", 
                 ".pytest_cache", "venv", ".venv", "target", ".tox"}
    
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        rel = os.path.relpath(dirpath, root)
        depth = rel.count(os.sep) + 1 if rel != "." else 0
        
        for f in filenames:
            fp = Path(dirpath) / f
            try:
                size = fp.stat().st_size
            except:
                continue
            
            stats["total_files"] += 1
            stats["total_size"] += size
            ext = fp.suffix.lower() or "(no ext)"
            stats["by_ext"][ext] += 1
            
            if size == 0:
                stats["empty_files"] += 1
            if depth > 6:
                stats["deep_nesting"] += 1
            
            stats["largest_files"].append((str(fp.relative_to(root)), size))
    
    stats["largest_files"].sort(key=lambda x: -x[1])
    stats["largest_files"] = stats["largest_files"][:10]
    return stats

def analyze_code_quality(root: Path, stack: dict) -> dict:
    """Quick code quality metrics."""
    result = {"total_lines": 0, "code_lines": 0, "comment_lines": 0, "todo_count": 0,
              "fixme_count": 0, "long_files": [], "duplicate_candidates": []}
    
    code_exts = {".py", ".js", ".jsx", ".ts", ".tsx", ".rs", ".go", ".java", ".rb"}
    skip_dirs = {".git", "node_modules", "__pycache__", ".next", "dist", "build", "venv", ".venv", "target"}
    
    file_hashes = defaultdict(list)
    
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for f in filenames:
            fp = Path(dirpath) / f
            if fp.suffix.lower() not in code_exts:
                continue
            try:
                content = fp.read_text(errors='ignore')
                lines = content.splitlines()
                line_count = len(lines)
                result["total_lines"] += line_count
                
                for line in lines:
                    stripped = line.strip()
                    if not stripped:
                        continue
                    if stripped.startswith("#") or stripped.startswith("//") or stripped.startswith("*"):
                        result["comment_lines"] += 1
                    else:
                        result["code_lines"] += 1
                    if "TODO" in line.upper():
                        result["todo_count"] += 1
                    if "FIXME" in line.upper():
                        result["fixme_count"] += 1
                
                if line_count > 500:
                    result["long_files"].append((str(fp.relative_to(root)), line_count))
                
                # Simple duplicate detection via size+linecount hash
                key = (fp.suffix, line_count, len(content))
                file_hashes[key].append(str(fp.relative_to(root)))
            except: pass
    
    for key, files in file_hashes.items():
        if len(files) > 1 and key[1] > 20:
            result["duplicate_candidates"].append(files)
    
    result["long_files"].sort(key=lambda x: -x[1])
    result["long_files"] = result["long_files"][:10]
    return result

def measure_startup(root: Path, stack: dict) -> dict:
    """Measure project startup/import time."""
    result = {"time_ms": None, "method": None}
    
    if stack["lang"] == "python":
        # Try importing main module
        main_candidates = list(root.glob("*//__init__.py")) + list(root.glob("*.py"))
        if main_candidates:
            start = time.time()
            try:
                subprocess.run([sys.executable, "-c", f"import importlib; importlib.import_module('tools.mw')"],
                             capture_output=True, timeout=10, cwd=str(root))
            except: pass
            result["time_ms"] = round((time.time() - start) * 1000)
            result["method"] = "python import"
    
    elif stack["lang"] == "node":
        start = time.time()
        try:
            subprocess.run(["node", "-e", "require('./package.json')"], 
                         capture_output=True, timeout=10, cwd=str(root))
        except: pass
        result["time_ms"] = round((time.time() - start) * 1000)
        result["method"] = "node require"
    
    return result

def generate_tips(stack, deps, files, quality) -> list:
    """Generate actionable optimization tips."""
    tips = []
    
    if deps.get("total", 0) > 50:
        tips.append(("🔴", f"High dependency count ({deps['total']}). Audit with: mw audit"))
    if deps.get("heavy"):
        for h in deps["heavy"][:3]:
            tips.append(("🟡", f"Consider replacing '{h['name']}' with {h['alternative']}"))
    if deps.get("node_modules_size", "").replace("G","").replace("M",""):
        size_str = deps.get("node_modules_size", "")
        if "G" in size_str:
            tips.append(("🔴", f"node_modules is {size_str}! Consider pnpm or dependency cleanup"))
    
    if files.get("empty_files", 0) > 5:
        tips.append(("🟡", f"{files['empty_files']} empty files found. Clean up?"))
    if files.get("deep_nesting", 0) > 10:
        tips.append(("🟡", f"{files['deep_nesting']} deeply nested files (>6 levels). Flatten structure?"))
    
    if quality.get("todo_count", 0) > 20:
        tips.append(("🟡", f"{quality['todo_count']} TODOs in codebase. Time to address them?"))
    if quality.get("fixme_count", 0) > 5:
        tips.append(("🔴", f"{quality['fixme_count']} FIXMEs need attention"))
    if quality.get("long_files"):
        tips.append(("🟡", f"{len(quality['long_files'])} files over 500 lines. Consider splitting"))
    if quality.get("duplicate_candidates"):
        tips.append(("🟡", f"{len(quality['duplicate_candidates'])} potential duplicate file groups"))
    
    comment_ratio = quality.get("comment_lines", 0) / max(quality.get("code_lines", 1), 1)
    if comment_ratio < 0.05 and quality.get("code_lines", 0) > 1000:
        tips.append(("🟡", "Low comment ratio (<5%). Consider adding documentation"))
    
    if not tips:
        tips.append(("✅", "Project looks healthy! No major issues detected."))
    
    return tips

def format_size(size_bytes: int) -> str:
    """Format bytes to human readable."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f}TB"

def run(args=None):
    """Main entry point."""
    project_dir = "."
    if args and len(args) > 0 and args[0] not in ("--help", "-h"):
        project_dir = args[0]
    
    if args and args[0] in ("--help", "-h"):
        print(f"""
{C.B}mw perf — Project Performance Analyzer{C.E}
{'=' * 45}
Usage:
    mw perf              Analyze current directory
    mw perf <path>       Analyze specific project
    mw perf --help       Show this help

Analyzes:
    • Stack detection (language, framework, package manager)
    • Dependency bloat and heavy package detection
    • File structure (counts, sizes, nesting depth)
    • Code quality (lines, comments, TODOs, long files)
    • Startup/import time measurement
    • Actionable optimization tips
""")
        return 0
    
    root = find_project_root(project_dir)
    
    print(f"\n{C.B}⚡ MyWork Performance Analyzer{C.E}")
    print("=" * 55)
    print(f"{C.DIM}Scanning: {root}{C.E}\n")
    
    # 1. Stack detection
    stack = detect_stack(root)
    lang_icons = {"node": "🟢", "python": "🐍", "rust": "🦀", "go": "🐹", "unknown": "❓"}
    print(f"{C.B}📦 Stack{C.E}")
    print(f"   Language:  {lang_icons.get(stack['lang'], '❓')} {stack['lang'].title()}")
    if stack["framework"]:
        print(f"   Framework: {stack['framework']}")
    if stack["pkg_manager"]:
        print(f"   Packages:  {stack['pkg_manager']}")
    print()
    
    # 2. Dependencies
    deps = analyze_dependencies(root, stack)
    print(f"{C.B}📋 Dependencies{C.E}")
    print(f"   Total: {deps['total']}  (prod: {deps['prod']}, dev: {deps['dev']})")
    if deps.get("node_modules_size"):
        print(f"   node_modules: {deps['node_modules_size']}")
    if deps.get("heavy"):
        print(f"   ⚠️  Heavy packages:")
        for h in deps["heavy"][:5]:
            print(f"      • {h['name']} → try {h['alternative']}")
    print()
    
    # 3. File structure
    files = analyze_file_structure(root)
    print(f"{C.B}📁 File Structure{C.E}")
    print(f"   Files: {files['total_files']:,}  |  Size: {format_size(files['total_size'])}")
    if files["empty_files"]:
        print(f"   Empty: {files['empty_files']}")
    top_exts = files["by_ext"].most_common(5)
    if top_exts:
        ext_str = ", ".join(f"{ext}({n})" for ext, n in top_exts)
        print(f"   Top types: {ext_str}")
    if files["largest_files"]:
        print(f"   Largest:")
        for name, size in files["largest_files"][:5]:
            print(f"      {format_size(size):>8s}  {name}")
    print()
    
    # 4. Code quality
    quality = analyze_code_quality(root, stack)
    print(f"{C.B}📊 Code Metrics{C.E}")
    print(f"   Lines: {quality['total_lines']:,} total ({quality['code_lines']:,} code, {quality['comment_lines']:,} comments)")
    if quality["todo_count"] or quality["fixme_count"]:
        print(f"   Markers: {quality['todo_count']} TODOs, {quality['fixme_count']} FIXMEs")
    if quality["long_files"]:
        print(f"   Long files (>500 lines):")
        for name, lines in quality["long_files"][:5]:
            print(f"      {lines:>5d} lines  {name}")
    print()
    
    # 5. Startup time
    startup = measure_startup(root, stack)
    if startup["time_ms"]:
        color = C.G if startup["time_ms"] < 500 else (C.Y if startup["time_ms"] < 2000 else C.R)
        print(f"{C.B}⏱️  Startup{C.E}")
        print(f"   {color}{startup['time_ms']}ms{C.E} ({startup['method']})")
        print()
    
    # 6. Tips
    tips = generate_tips(stack, deps, files, quality)
    print(f"{C.B}💡 Optimization Tips{C.E}")
    for icon, tip in tips:
        print(f"   {icon} {tip}")
    
    # Score
    score = 100
    if deps.get("total", 0) > 80: score -= 15
    elif deps.get("total", 0) > 50: score -= 8
    if deps.get("heavy"): score -= len(deps["heavy"]) * 3
    if files.get("empty_files", 0) > 10: score -= 5
    if quality.get("todo_count", 0) > 30: score -= 10
    if quality.get("fixme_count", 0) > 10: score -= 10
    if quality.get("long_files"): score -= min(len(quality["long_files"]) * 2, 10)
    score = max(0, min(100, score))
    
    score_color = C.G if score >= 80 else (C.Y if score >= 60 else C.R)
    grade = "A+" if score >= 95 else "A" if score >= 90 else "A-" if score >= 85 else \
            "B+" if score >= 80 else "B" if score >= 75 else "B-" if score >= 70 else \
            "C+" if score >= 65 else "C" if score >= 60 else "D" if score >= 50 else "F"
    
    print(f"\n{'=' * 55}")
    print(f"{C.B}Performance Score: {score_color}{score}/100 ({grade}){C.E}")
    print(f"{'=' * 55}\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(run(sys.argv[1:]))
