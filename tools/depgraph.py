#!/usr/bin/env python3
"""MyWork Dependency Graph — mw depgraph

Analyzes Python imports across a project and generates a dependency graph.
Outputs ASCII art, DOT format, or JSON for visualization.

Usage:
    mw depgraph [path]              Show dependency graph for current/given project
    mw depgraph --format dot        Output in Graphviz DOT format
    mw depgraph --format json       Output as JSON
    mw depgraph --external          Include external (pip) dependencies
    mw depgraph --depth N           Limit graph depth (default: unlimited)
    mw depgraph --module NAME       Show deps for a specific module only
    mw depgraph --cycles            Detect and highlight circular imports
    mw depgraph --stats             Show import statistics
"""

import ast
import json
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# ANSI colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"


def extract_imports(filepath: Path) -> Tuple[Set[str], Set[str]]:
    """Extract import statements from a Python file.
    
    Returns:
        (local_imports, external_imports)
    """
    local_imports = set()
    external_imports = set()
    
    try:
        source = filepath.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, UnicodeDecodeError):
        return local_imports, external_imports
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name.split(".")[0]
                external_imports.add(name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                name = node.module.split(".")[0]
                if node.level > 0:
                    local_imports.add(name)
                else:
                    external_imports.add(name)
    
    return local_imports, external_imports


def scan_project(project_path: Path, include_external: bool = False) -> Dict:
    """Scan a project directory and build dependency map."""
    project_path = project_path.resolve()
    
    # Find all Python files
    py_files = sorted(project_path.rglob("*.py"))
    
    # Filter out common non-source dirs
    skip_dirs = {".git", "__pycache__", "node_modules", ".venv", "venv", "env",
                 ".tox", ".mypy_cache", ".pytest_cache", "dist", "build", ".eggs"}
    
    py_files = [
        f for f in py_files
        if not any(s in f.parts for s in skip_dirs)
    ]
    
    # Build module name mapping
    modules = {}
    for f in py_files:
        try:
            rel = f.relative_to(project_path)
        except ValueError:
            continue
        
        # Convert path to module name
        parts = list(rel.parts)
        if parts[-1] == "__init__.py":
            parts = parts[:-1]
        else:
            parts[-1] = parts[-1].replace(".py", "")
        
        if parts:
            module_name = ".".join(parts)
            modules[module_name] = f
    
    # Get the set of local top-level package names
    local_packages = set()
    for m in modules:
        local_packages.add(m.split(".")[0])
    
    # Build dependency graph
    graph = {}  # module -> {local_deps, external_deps, loc}
    
    for module_name, filepath in modules.items():
        local_imports, external_imports = extract_imports(filepath)
        
        # Classify: if top-level matches a local package, it's local
        local_deps = set()
        ext_deps = set()
        
        for imp in external_imports:
            if imp in local_packages:
                local_deps.add(imp)
            else:
                ext_deps.add(imp)
        
        local_deps.update(local_imports)
        
        # Count lines of code
        try:
            loc = sum(1 for line in filepath.read_text(errors="ignore").splitlines() 
                      if line.strip() and not line.strip().startswith("#"))
        except Exception:
            loc = 0
        
        entry = {"local_deps": sorted(local_deps), "loc": loc}
        if include_external:
            entry["external_deps"] = sorted(ext_deps)
        
        graph[module_name] = entry
    
    return graph


def detect_cycles(graph: Dict) -> List[List[str]]:
    """Detect circular import cycles using DFS."""
    cycles = []
    visited = set()
    rec_stack = set()
    path = []
    
    def dfs(node):
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        
        deps = graph.get(node, {}).get("local_deps", [])
        for dep in deps:
            # Find modules that start with this dep
            matching = [m for m in graph if m == dep or m.startswith(dep + ".")]
            for neighbor in matching:
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    # Found a cycle
                    idx = path.index(neighbor)
                    cycle = path[idx:] + [neighbor]
                    cycles.append(cycle)
        
        path.pop()
        rec_stack.discard(node)
    
    for node in graph:
        if node not in visited:
            dfs(node)
    
    return cycles


def format_ascii(graph: Dict, module_filter: Optional[str] = None, max_depth: Optional[int] = None) -> str:
    """Format dependency graph as ASCII tree."""
    lines = []
    lines.append(f"{BOLD}{CYAN}📊 Dependency Graph{RESET}")
    lines.append(f"{DIM}{'─' * 60}{RESET}")
    
    # Sort modules by dependency count (most deps first)
    sorted_modules = sorted(graph.items(), key=lambda x: len(x[1].get("local_deps", [])), reverse=True)
    
    if module_filter:
        sorted_modules = [(m, d) for m, d in sorted_modules if module_filter in m]
    
    for module_name, data in sorted_modules:
        local_deps = data.get("local_deps", [])
        ext_deps = data.get("external_deps", [])
        loc = data.get("loc", 0)
        
        # Color based on complexity
        if loc > 500:
            color = RED
        elif loc > 200:
            color = YELLOW
        else:
            color = GREEN
        
        dep_count = len(local_deps) + len(ext_deps)
        lines.append(f"\n{BOLD}{color}📦 {module_name}{RESET} {DIM}({loc} LOC, {dep_count} deps){RESET}")
        
        if local_deps:
            for i, dep in enumerate(local_deps):
                prefix = "└── " if i == len(local_deps) - 1 and not ext_deps else "├── "
                lines.append(f"  {BLUE}{prefix}{dep}{RESET}")
        
        if ext_deps:
            for i, dep in enumerate(ext_deps):
                prefix = "└── " if i == len(ext_deps) - 1 else "├── "
                lines.append(f"  {DIM}{prefix}{dep} (external){RESET}")
    
    # Summary
    total_modules = len(graph)
    total_deps = sum(len(d.get("local_deps", [])) for d in graph.values())
    total_loc = sum(d.get("loc", 0) for d in graph.values())
    
    lines.append(f"\n{DIM}{'─' * 60}{RESET}")
    lines.append(f"{BOLD}Summary:{RESET} {total_modules} modules, {total_deps} internal deps, {total_loc:,} LOC")
    
    return "\n".join(lines)


def format_dot(graph: Dict, project_name: str = "project") -> str:
    """Format as Graphviz DOT."""
    lines = [f'digraph "{project_name}" {{']
    lines.append('  rankdir=LR;')
    lines.append('  node [shape=box, style=filled, fillcolor="#e8f4fd"];')
    lines.append('  edge [color="#666666"];')
    lines.append('')
    
    for module_name, data in graph.items():
        loc = data.get("loc", 0)
        # Size node by LOC
        width = max(1.0, min(3.0, loc / 200))
        safe_name = module_name.replace(".", "_")
        
        if loc > 500:
            color = "#ffcccc"
        elif loc > 200:
            color = "#fff3cd"
        else:
            color = "#d4edda"
        
        lines.append(f'  {safe_name} [label="{module_name}\\n{loc} LOC", '
                      f'fillcolor="{color}", width={width:.1f}];')
    
    lines.append('')
    
    for module_name, data in graph.items():
        safe_name = module_name.replace(".", "_")
        for dep in data.get("local_deps", []):
            safe_dep = dep.replace(".", "_")
            if safe_dep + "_" in "".join(f"{m.replace('.', '_')}" for m in graph):
                # Find best match
                matches = [m for m in graph if m.startswith(dep)]
                for match in matches[:1]:
                    lines.append(f'  {safe_name} -> {match.replace(".", "_")};')
            else:
                lines.append(f'  {safe_name} -> {safe_dep};')
    
    lines.append('}')
    return "\n".join(lines)


def format_json(graph: Dict) -> str:
    """Format as JSON."""
    return json.dumps(graph, indent=2, sort_keys=True)


def show_stats(graph: Dict) -> str:
    """Show import statistics."""
    lines = []
    lines.append(f"{BOLD}{CYAN}📈 Import Statistics{RESET}")
    lines.append(f"{DIM}{'─' * 60}{RESET}")
    
    total_modules = len(graph)
    total_loc = sum(d.get("loc", 0) for d in graph.values())
    all_local_deps = sum(len(d.get("local_deps", [])) for d in graph.values())
    all_ext_deps = sum(len(d.get("external_deps", [])) for d in graph.values())
    
    # Most imported (most depended upon)
    import_count = defaultdict(int)
    for data in graph.values():
        for dep in data.get("local_deps", []):
            import_count[dep] += 1
    
    # Most dependent (imports the most)
    most_deps = sorted(graph.items(), key=lambda x: len(x[1].get("local_deps", [])), reverse=True)
    
    # Largest files
    largest = sorted(graph.items(), key=lambda x: x[1].get("loc", 0), reverse=True)
    
    lines.append(f"\n{BOLD}Overview:{RESET}")
    lines.append(f"  Modules: {total_modules}")
    lines.append(f"  Total LOC: {total_loc:,}")
    lines.append(f"  Internal deps: {all_local_deps}")
    lines.append(f"  External deps: {all_ext_deps}")
    lines.append(f"  Avg deps/module: {all_local_deps / max(total_modules, 1):.1f}")
    
    lines.append(f"\n{BOLD}🔥 Most Imported (highest coupling):{RESET}")
    for dep, count in sorted(import_count.items(), key=lambda x: -x[1])[:10]:
        bar = "█" * count
        lines.append(f"  {dep:30s} {count:3d} {GREEN}{bar}{RESET}")
    
    lines.append(f"\n{BOLD}🕸️ Most Dependencies (highest complexity):{RESET}")
    for module_name, data in most_deps[:10]:
        count = len(data.get("local_deps", []))
        bar = "█" * count
        lines.append(f"  {module_name:30s} {count:3d} {YELLOW}{bar}{RESET}")
    
    lines.append(f"\n{BOLD}📏 Largest Modules (LOC):{RESET}")
    for module_name, data in largest[:10]:
        loc = data.get("loc", 0)
        bar = "█" * (loc // 50)
        color = RED if loc > 500 else YELLOW if loc > 200 else GREEN
        lines.append(f"  {module_name:30s} {loc:5d} {color}{bar}{RESET}")
    
    return "\n".join(lines)


def main(args: List[str] = None):
    """Main entry point."""
    if args is None:
        args = sys.argv[1:]
    
    # Parse args
    fmt = "ascii"
    include_external = False
    max_depth = None
    module_filter = None
    show_cycles = False
    show_statistics = False
    project_path = Path.cwd()
    
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("--format", "-f") and i + 1 < len(args):
            fmt = args[i + 1]
            i += 2
        elif arg in ("--external", "-e"):
            include_external = True
            i += 1
        elif arg in ("--depth", "-d") and i + 1 < len(args):
            max_depth = int(args[i + 1])
            i += 2
        elif arg in ("--module", "-m") and i + 1 < len(args):
            module_filter = args[i + 1]
            i += 2
        elif arg in ("--cycles", "-c"):
            show_cycles = True
            i += 1
        elif arg in ("--stats", "-s"):
            show_statistics = True
            i += 1
        elif arg in ("--help", "-h"):
            print(__doc__)
            return
        elif not arg.startswith("-"):
            project_path = Path(arg)
            i += 1
        else:
            print(f"{RED}Unknown option: {arg}{RESET}")
            print(__doc__)
            return
    
    if not project_path.exists():
        print(f"{RED}Error: Path '{project_path}' does not exist{RESET}")
        sys.exit(1)
    
    # Scan
    graph = scan_project(project_path, include_external=include_external)
    
    if not graph:
        print(f"{YELLOW}No Python modules found in {project_path}{RESET}")
        return
    
    # Output
    if show_cycles:
        cycles = detect_cycles(graph)
        if cycles:
            print(f"{RED}{BOLD}⚠️  Circular Import Cycles Detected!{RESET}")
            for cycle in cycles:
                print(f"  {RED}→ {' → '.join(cycle)}{RESET}")
        else:
            print(f"{GREEN}✅ No circular imports detected{RESET}")
        print()
    
    if show_statistics:
        print(show_stats(graph))
        return
    
    if fmt == "dot":
        print(format_dot(graph, project_path.name))
    elif fmt == "json":
        print(format_json(graph))
    else:
        print(format_ascii(graph, module_filter=module_filter, max_depth=max_depth))


if __name__ == "__main__":
    main()
