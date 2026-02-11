#!/usr/bin/env python3
"""MyWork AI Documentation Generator.

Scans a project directory and auto-generates comprehensive documentation:
- README.md with project overview, install, usage
- API.md for HTTP endpoints (FastAPI/Flask/Express detection)
- MODULES.md for Python module documentation
- ARCHITECTURE.md for project structure overview
"""

import os
import sys
import ast
import json
import re
from pathlib import Path
from datetime import datetime


class Colors:
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    DIM = "\033[2m"


def scan_python_module(filepath: Path) -> dict:
    """Extract docstrings, classes, functions from a Python file."""
    try:
        source = filepath.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source)
    except (SyntaxError, UnicodeDecodeError):
        return None

    module_doc = ast.get_docstring(tree) or ""
    classes = []
    functions = []
    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods = []
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not item.name.startswith("_") or item.name == "__init__":
                        args = [a.arg for a in item.args.args if a.arg != "self"]
                        methods.append({
                            "name": item.name,
                            "args": args,
                            "doc": ast.get_docstring(item) or "",
                            "async": isinstance(item, ast.AsyncFunctionDef),
                        })
            classes.append({
                "name": node.name,
                "doc": ast.get_docstring(node) or "",
                "methods": methods,
                "bases": [getattr(b, "id", getattr(b, "attr", "?")) for b in node.bases],
            })
        elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            if node.col_offset == 0 and not node.name.startswith("_"):
                args = [a.arg for a in node.args.args if a.arg != "self"]
                functions.append({
                    "name": node.name,
                    "args": args,
                    "doc": ast.get_docstring(node) or "",
                    "async": isinstance(node, ast.AsyncFunctionDef),
                })
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)

    return {
        "path": str(filepath),
        "module_doc": module_doc,
        "classes": classes,
        "functions": functions,
        "imports": imports,
        "lines": len(source.splitlines()),
    }


def detect_framework(project_path: Path) -> dict:
    """Detect project framework and tech stack."""
    info = {"language": "unknown", "framework": None, "features": []}

    # Check for Python
    if list(project_path.glob("*.py")) or (project_path / "requirements.txt").exists():
        info["language"] = "python"
        reqs = ""
        for f in ["requirements.txt", "pyproject.toml", "setup.py"]:
            p = project_path / f
            if p.exists():
                reqs = p.read_text(errors="ignore")
                break
        if "fastapi" in reqs.lower():
            info["framework"] = "FastAPI"
        elif "flask" in reqs.lower():
            info["framework"] = "Flask"
        elif "django" in reqs.lower():
            info["framework"] = "Django"
        if "pytest" in reqs.lower():
            info["features"].append("pytest")
        if "sqlalchemy" in reqs.lower() or "supabase" in reqs.lower():
            info["features"].append("database")

    # Check for Node.js
    pkg = project_path / "package.json"
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text())
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            info["language"] = "typescript" if (project_path / "tsconfig.json").exists() else "javascript"
            if "next" in deps:
                info["framework"] = "Next.js"
            elif "express" in deps:
                info["framework"] = "Express"
            elif "react" in deps:
                info["framework"] = "React"
            if "tailwindcss" in deps:
                info["features"].append("Tailwind CSS")
            if "prisma" in deps or "@supabase/supabase-js" in deps:
                info["features"].append("database")
        except json.JSONDecodeError:
            pass

    return info


def scan_api_routes(project_path: Path) -> list:
    """Detect API routes from FastAPI/Flask/Express files."""
    routes = []
    patterns = [
        # FastAPI
        (r'@\w+\.(get|post|put|delete|patch)\(\s*["\']([^"\']+)["\']', "python"),
        # Flask
        (r'@\w+\.route\(\s*["\']([^"\']+)["\'].*methods=\[([^\]]+)\]', "python"),
        # Express
        (r'\w+\.(get|post|put|delete|patch)\(\s*["\']([^"\']+)["\']', "javascript"),
    ]

    for py_file in list(project_path.rglob("*.py")) + list(project_path.rglob("*.ts")) + list(project_path.rglob("*.js")):
        if any(skip in str(py_file) for skip in ["node_modules", "__pycache__", ".git", "venv", ".venv"]):
            continue
        try:
            content = py_file.read_text(errors="ignore")
        except Exception:
            continue
        for pattern, lang in patterns:
            for match in re.finditer(pattern, content):
                groups = match.groups()
                if len(groups) == 2:
                    method = groups[0].upper()
                    path = groups[1]
                    routes.append({"method": method, "path": path, "file": str(py_file.relative_to(project_path))})

    return routes


def generate_tree(project_path: Path, max_depth=3, prefix="") -> str:
    """Generate a directory tree string."""
    skip = {".git", "node_modules", "__pycache__", ".pytest_cache", "venv", ".venv",
            ".mypy_cache", ".tox", "dist", "build", "*.egg-info", ".tmp"}
    lines = []
    items = sorted(project_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
    dirs = [i for i in items if i.is_dir() and i.name not in skip and not i.name.endswith(".egg-info")]
    files = [i for i in items if i.is_file()]

    entries = dirs + files
    for i, entry in enumerate(entries):
        is_last = i == len(entries) - 1
        connector = "└── " if is_last else "├── "
        if entry.is_dir():
            lines.append(f"{prefix}{connector}{entry.name}/")
            if max_depth > 1:
                extension = "    " if is_last else "│   "
                lines.append(generate_tree(entry, max_depth - 1, prefix + extension))
        else:
            lines.append(f"{prefix}{connector}{entry.name}")

    return "\n".join(line for line in lines if line.strip())


def generate_readme(project_path: Path, info: dict, modules: list, routes: list) -> str:
    """Generate README.md content."""
    name = project_path.name
    tree = generate_tree(project_path, max_depth=2)

    # Count stats
    py_files = list(project_path.rglob("*.py"))
    ts_files = list(project_path.rglob("*.ts"))
    js_files = list(project_path.rglob("*.js"))
    total_files = len([f for f in py_files + ts_files + js_files
                       if "node_modules" not in str(f) and "__pycache__" not in str(f)])
    total_lines = 0
    for f in py_files:
        if "__pycache__" not in str(f):
            try:
                total_lines += len(f.read_text(errors="ignore").splitlines())
            except Exception:
                pass

    doc = f"""# {name}

> Auto-generated documentation by MyWork AI Doc Generator
> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Overview

| Metric | Value |
|--------|-------|
| Language | {info['language'].title()} |
| Framework | {info['framework'] or 'N/A'} |
| Source Files | {total_files} |
| Lines of Code | {total_lines:,} |
| Features | {', '.join(info['features']) or 'N/A'} |

## Project Structure

```
{name}/
{tree}
```
"""

    # Installation section
    if info["language"] == "python":
        req_file = project_path / "requirements.txt"
        doc += """
## Installation

```bash
pip install -r requirements.txt
```
"""
        if (project_path / "pyproject.toml").exists():
            doc += f"""
Or install as package:
```bash
pip install .
```
"""
    elif info["language"] in ("javascript", "typescript"):
        doc += """
## Installation

```bash
npm install
```
"""

    # API Routes
    if routes:
        doc += "\n## API Endpoints\n\n"
        doc += "| Method | Path | File |\n"
        doc += "|--------|------|------|\n"
        for r in routes[:50]:
            doc += f"| `{r['method']}` | `{r['path']}` | `{r['file']}` |\n"

    # Module summary
    if modules:
        doc += "\n## Modules\n\n"
        for mod in modules[:30]:
            rel = Path(mod["path"]).relative_to(project_path)
            desc = mod["module_doc"].split("\n")[0] if mod["module_doc"] else f"{len(mod['classes'])} classes, {len(mod['functions'])} functions"
            doc += f"- **`{rel}`** — {desc} ({mod['lines']} lines)\n"

    doc += f"""
---

*Documentation generated by [MyWork AI](https://github.com/DansiDanutz/MyWork-AI) `mw docs`*
"""
    return doc


def generate_api_doc(routes: list) -> str:
    """Generate API.md from detected routes."""
    if not routes:
        return ""
    doc = "# API Reference\n\n"
    doc += "> Auto-generated by MyWork AI Doc Generator\n\n"
    by_prefix = {}
    for r in routes:
        parts = r["path"].strip("/").split("/")
        prefix = parts[0] if parts else "root"
        by_prefix.setdefault(prefix, []).append(r)

    for prefix, group in sorted(by_prefix.items()):
        doc += f"## /{prefix}\n\n"
        for r in group:
            doc += f"### `{r['method']}` {r['path']}\n\n"
            doc += f"**File:** `{r['file']}`\n\n"
        doc += "---\n\n"
    return doc


def generate_modules_doc(modules: list, project_path: Path) -> str:
    """Generate MODULES.md with detailed module documentation."""
    doc = "# Module Reference\n\n"
    doc += "> Auto-generated by MyWork AI Doc Generator\n\n"
    doc += f"**Total modules:** {len(modules)}\n\n"

    for mod in sorted(modules, key=lambda m: m["path"]):
        rel = Path(mod["path"]).relative_to(project_path)
        doc += f"## `{rel}`\n\n"
        if mod["module_doc"]:
            doc += f"{mod['module_doc']}\n\n"
        doc += f"*{mod['lines']} lines*\n\n"

        for cls in mod["classes"]:
            bases = f"({', '.join(cls['bases'])})" if cls["bases"] else ""
            doc += f"### class `{cls['name']}`{bases}\n\n"
            if cls["doc"]:
                doc += f"{cls['doc']}\n\n"
            if cls["methods"]:
                doc += "| Method | Args | Description |\n"
                doc += "|--------|------|-------------|\n"
                for m in cls["methods"]:
                    args_str = ", ".join(m["args"][:5])
                    desc = m["doc"].split("\n")[0][:80] if m["doc"] else ""
                    prefix = "async " if m["async"] else ""
                    doc += f"| `{prefix}{m['name']}` | `{args_str}` | {desc} |\n"
                doc += "\n"

        if mod["functions"]:
            doc += "### Functions\n\n"
            doc += "| Function | Args | Description |\n"
            doc += "|----------|------|-------------|\n"
            for fn in mod["functions"]:
                args_str = ", ".join(fn["args"][:5])
                desc = fn["doc"].split("\n")[0][:80] if fn["doc"] else ""
                prefix = "async " if fn["async"] else ""
                doc += f"| `{prefix}{fn['name']}` | `{args_str}` | {desc} |\n"
            doc += "\n"

        doc += "---\n\n"
    return doc


def run_docs(args: list):
    """Main entry point for docs command."""
    if not args or args[0] in ("--help", "-h"):
        print(f"""
{Colors.BOLD}📚 MyWork AI Documentation Generator{Colors.ENDC}

{Colors.CYAN}Usage:{Colors.ENDC}
  mw docs generate <path>   Generate docs for a project
  mw docs preview <path>    Preview what would be generated
  mw docs stats <path>      Show documentation coverage stats

{Colors.CYAN}Options:{Colors.ENDC}
  --output-dir <dir>   Output directory (default: <project>/docs/generated/)
  --format md          Output format (default: markdown)

{Colors.CYAN}Examples:{Colors.ENDC}
  mw docs generate ./my-project
  mw docs stats ./my-project
  mw docs generate . --output-dir ./docs
""")
        return 0

    subcmd = args[0]
    if len(args) < 2:
        project_path = Path.cwd()
    else:
        project_path = Path(args[1]).resolve()

    if not project_path.exists():
        print(f"{Colors.RED}✗ Project path not found: {project_path}{Colors.ENDC}")
        return 1

    # Parse --output-dir
    output_dir = project_path / "docs" / "generated"
    if "--output-dir" in args:
        idx = args.index("--output-dir")
        if idx + 1 < len(args):
            output_dir = Path(args[idx + 1]).resolve()

    print(f"\n{Colors.BOLD}📚 MyWork AI Doc Generator{Colors.ENDC}")
    print(f"{Colors.DIM}Scanning: {project_path}{Colors.ENDC}\n")

    # Detect framework
    info = detect_framework(project_path)
    print(f"  {Colors.GREEN}✓{Colors.ENDC} Detected: {info['language'].title()}" +
          (f" / {info['framework']}" if info['framework'] else ""))

    # Scan Python modules
    modules = []
    for py_file in sorted(project_path.rglob("*.py")):
        if any(skip in str(py_file) for skip in ["node_modules", "__pycache__", ".git", "venv", ".venv", ".egg-info", ".tmp"]):
            continue
        result = scan_python_module(py_file)
        if result and (result["classes"] or result["functions"] or result["module_doc"]):
            modules.append(result)
    print(f"  {Colors.GREEN}✓{Colors.ENDC} Scanned {len(modules)} documented modules")

    # Scan API routes
    routes = scan_api_routes(project_path)
    if routes:
        print(f"  {Colors.GREEN}✓{Colors.ENDC} Found {len(routes)} API routes")

    if subcmd == "stats":
        # Show coverage
        total_py = len(list(project_path.rglob("*.py")))
        documented = len([m for m in modules if m["module_doc"]])
        classes_total = sum(len(m["classes"]) for m in modules)
        classes_documented = sum(1 for m in modules for c in m["classes"] if c["doc"])
        funcs_total = sum(len(m["functions"]) for m in modules)
        funcs_documented = sum(1 for m in modules for f in m["functions"] if f["doc"])

        print(f"\n{Colors.BOLD}📊 Documentation Coverage{Colors.ENDC}\n")
        print(f"  Modules with docstrings:  {documented}/{len(modules)} ({(documented/max(len(modules),1)*100):.0f}%)")
        print(f"  Classes with docstrings:  {classes_documented}/{classes_total} ({(classes_documented/max(classes_total,1)*100):.0f}%)")
        print(f"  Functions with docstrings: {funcs_documented}/{funcs_total} ({(funcs_documented/max(funcs_total,1)*100):.0f}%)")
        print(f"  API routes found:         {len(routes)}")
        return 0

    if subcmd == "preview":
        print(f"\n{Colors.BOLD}📋 Would generate:{Colors.ENDC}")
        print(f"  • README.md (project overview)")
        if routes:
            print(f"  • API.md ({len(routes)} endpoints)")
        if modules:
            print(f"  • MODULES.md ({len(modules)} modules)")
        print(f"  • ARCHITECTURE.md (project structure)")
        print(f"\n  Output: {output_dir}/")
        return 0

    if subcmd == "generate":
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate README
        readme = generate_readme(project_path, info, modules, routes)
        (output_dir / "README.md").write_text(readme)
        print(f"  {Colors.GREEN}✓{Colors.ENDC} Generated README.md")

        # Generate API docs
        if routes:
            api_doc = generate_api_doc(routes)
            (output_dir / "API.md").write_text(api_doc)
            print(f"  {Colors.GREEN}✓{Colors.ENDC} Generated API.md ({len(routes)} routes)")

        # Generate module docs
        if modules:
            mod_doc = generate_modules_doc(modules, project_path)
            (output_dir / "MODULES.md").write_text(mod_doc)
            print(f"  {Colors.GREEN}✓{Colors.ENDC} Generated MODULES.md ({len(modules)} modules)")

        # Generate architecture
        tree = generate_tree(project_path, max_depth=3)
        arch = f"# Architecture\n\n> Auto-generated by MyWork AI\n\n```\n{project_path.name}/\n{tree}\n```\n"
        (output_dir / "ARCHITECTURE.md").write_text(arch)
        print(f"  {Colors.GREEN}✓{Colors.ENDC} Generated ARCHITECTURE.md")

        total = 2 + (1 if routes else 0) + (1 if modules else 0)
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ Generated {total} docs in {output_dir}/{Colors.ENDC}\n")
        return 0

    print(f"{Colors.RED}Unknown subcommand: {subcmd}{Colors.ENDC}")
    return 1


if __name__ == "__main__":
    sys.exit(run_docs(sys.argv[1:]) or 0)
