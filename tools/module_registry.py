#!/usr/bin/env python3
"""
Auto-Learning Module Registry for MyWork Framework
===================================================
Scans all projects for reusable components, patterns, and modules.
Enables cross-project search to reduce rebuild time.

Usage:
    python module_registry.py scan           # Scan all projects and update registry
    python module_registry.py search <query> # Search for modules/patterns
    python module_registry.py list [type]    # List all registered modules
    python module_registry.py show <id>      # Show module details
    python module_registry.py stats          # Show registry statistics
    python module_registry.py export         # Export registry to markdown

Module Types:
    - api_endpoint: REST/GraphQL endpoints
    - component: UI components (React, Vue, etc.)
    - service: Backend services/classes
    - utility: Helper functions
    - schema: Database models/schemas
    - workflow: n8n workflows
    - hook: React hooks, Git hooks
    - middleware: Express/FastAPI middleware
    - config: Configuration patterns
    - integration: External API integrations
"""

import os
import sys
import json
import re
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from collections import defaultdict

# Configuration - Import from shared config with fallback
try:
    from config import get_mywork_root
except ImportError:  # pragma: no cover - fallback for standalone usage

    def get_mywork_root() -> Path:
        if env_root := os.environ.get("MYWORK_ROOT"):
            return Path(env_root)
        script_dir = Path(__file__).resolve().parent
        return script_dir.parent if script_dir.name == "tools" else Path.home() / "MyWork"


def _resolve_registry_paths(root: Optional[Path] = None) -> tuple[Path, Path, Path, Path]:
    resolved_root = (root or get_mywork_root()).resolve()
    projects_dir = resolved_root / "projects"
    registry_file = resolved_root / ".planning" / "module_registry.json"
    registry_md = resolved_root / ".planning" / "MODULE_REGISTRY.md"
    return resolved_root, projects_dir, registry_file, registry_md


# Backwards-compatible defaults (do not rely on these for dynamic roots)
MYWORK_ROOT, PROJECTS_DIR, REGISTRY_FILE, REGISTRY_MD = _resolve_registry_paths()

# File patterns to scan
SCAN_PATTERNS = {
    "python": ["*.py"],
    "typescript": ["*.ts", "*.tsx"],
    "javascript": ["*.js", "*.jsx"],
    "json": ["*.json"],
    "yaml": ["*.yml", "*.yaml"],
}

# Directories to skip
SKIP_DIRS = {
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    ".git",
    "dist",
    "build",
    ".next",
    ".nuxt",
    "coverage",
    ".pytest_cache",
}

# Module detection patterns
MODULE_PATTERNS = {
    "api_endpoint": {
        "python": [
            r'@app\.(get|post|put|delete|patch)\s*\(["\']([^"\']+)',
            r'@router\.(get|post|put|delete|patch)\s*\(["\']([^"\']+)',
        ],
        "typescript": [
            r'(GET|POST|PUT|DELETE|PATCH)\s+["\']([^"\']+)',
            r'app\.(get|post|put|delete|patch)\s*\(["\']([^"\']+)',
        ],
    },
    "component": {
        "typescript": [
            r"(?:export\s+(?:default\s+)?)?function\s+([A-Z][a-zA-Z0-9]+)\s*\(",
            r"const\s+([A-Z][a-zA-Z0-9]+)\s*[=:]\s*(?:\([^)]*\)\s*=>|React\.FC)",
        ],
        "javascript": [
            r"(?:export\s+(?:default\s+)?)?function\s+([A-Z][a-zA-Z0-9]+)\s*\(",
        ],
    },
    "service": {
        "python": [
            r"class\s+(\w+Service)\s*[:\(]",
            r"class\s+(\w+Manager)\s*[:\(]",
            r"class\s+(\w+Handler)\s*[:\(]",
        ],
        "typescript": [
            r"class\s+(\w+Service)\s*[{\(]",
            r"class\s+(\w+Manager)\s*[{\(]",
        ],
    },
    "utility": {
        "python": [
            r"def\s+((?:get|set|create|update|delete|parse|format|validate|convert|calculate|generate|transform|extract|normalize|sanitize)[_a-zA-Z0-9]*)\s*\(",
        ],
        "typescript": [
            r"(?:export\s+)?(?:const|function)\s+((?:get|set|create|update|delete|parse|format|validate|convert|calculate|generate|transform|extract|normalize|sanitize)[A-Za-z0-9]*)\s*[=\(]",
        ],
    },
    "schema": {
        "python": [
            r"class\s+(\w+)\s*\(.*(?:Base|Model|Schema|Table)",
            r"class\s+(\w+)\s*\(.*SQLModel",
        ],
        "typescript": [
            r"(?:interface|type)\s+(\w+(?:Schema|Model|Type|Interface))\s*[{=]",
            r"const\s+(\w+Schema)\s*=\s*z\.",
        ],
    },
    "hook": {
        "typescript": [
            r"(?:export\s+)?(?:const|function)\s+(use[A-Z][a-zA-Z0-9]*)\s*[=\(]",
        ],
    },
    "middleware": {
        "python": [
            r'@app\.middleware\s*\(["\']([^"\']+)',
            r"class\s+(\w+Middleware)",
        ],
        "typescript": [
            r"(?:export\s+)?(?:const|function)\s+(\w+Middleware)\s*[=\(]",
        ],
    },
    "integration": {
        "python": [
            r"class\s+(\w+(?:Client|API|Integration|Connector))\s*[:\(]",
        ],
        "typescript": [
            r"class\s+(\w+(?:Client|API|Integration|Connector))\s*[{\(]",
        ],
    },
}


@dataclass
class Module:
    """Represents a discovered module."""

    id: str
    name: str
    type: str
    project: str
    file_path: str
    line_number: int
    language: str
    description: str
    tags: List[str]
    dependencies: List[str]
    exports: List[str]
    last_modified: str
    hash: str

    def to_dict(self) -> Dict:
        return asdict(self)


class ModuleRegistry:
    """Registry for all discovered modules across projects."""

    def __init__(self, root: Optional[Path] = None):
        self.root, self.projects_dir, self.registry_file, self.registry_md = (
            _resolve_registry_paths(root)
        )
        self.modules: Dict[str, Module] = {}
        self.index: Dict[str, Set[str]] = defaultdict(set)  # tag -> module_ids
        self.type_index: Dict[str, Set[str]] = defaultdict(set)  # type -> module_ids
        self.project_index: Dict[str, Set[str]] = defaultdict(set)  # project -> module_ids
        self.load()

    def load(self):
        """Load registry from file."""
        if self.registry_file.exists():
            try:
                with open(self.registry_file) as f:
                    data = json.load(f)
                    for mod_data in data.get("modules", []):
                        mod = Module(**mod_data)
                        self.modules[mod.id] = mod
                        self._index_module(mod)
            except (json.JSONDecodeError, TypeError) as e:
                print(f"Warning: Could not load registry: {e}")

    def save(self):
        """Save registry to file."""
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "module_count": len(self.modules),
            "modules": [m.to_dict() for m in self.modules.values()],
        }
        with open(self.registry_file, "w") as f:
            json.dump(data, f, indent=2)

    def _index_module(self, module: Module):
        """Add module to indexes."""
        for tag in module.tags:
            self.index[tag.lower()].add(module.id)
        self.type_index[module.type].add(module.id)
        self.project_index[module.project].add(module.id)

    def _generate_id(self, project: str, file_path: str, name: str) -> str:
        """Generate a unique module ID."""
        content = f"{project}:{file_path}:{name}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def add_module(self, module: Module):
        """Add or update a module in the registry."""
        self.modules[module.id] = module
        self._index_module(module)

    def search(self, query: str, type_filter: Optional[str] = None, 
              include_brain: bool = True, include_files: bool = True,
              max_results: int = 50) -> Dict[str, List[Any]]:
        """Enhanced search across modules, brain entries, and project files."""
        query_lower = query.lower()
        results = {
            "modules": [],
            "brain_entries": [],
            "project_files": [],
            "total_found": 0
        }

        # Search modules (existing functionality)
        module_results = []
        for module in self.modules.values():
            if type_filter and module.type != type_filter:
                continue

            score = 0

            # Name match (highest priority)
            if query_lower in module.name.lower():
                score += 10

            # Tag match
            for tag in module.tags:
                if query_lower in tag.lower():
                    score += 5

            # Description match
            if query_lower in module.description.lower():
                score += 2

            # File path match
            if query_lower in module.file_path.lower():
                score += 1

            if score > 0:
                module_results.append((score, module))

        # Sort by score descending
        module_results.sort(key=lambda x: x[0], reverse=True)
        results["modules"] = [m for _, m in module_results[:max_results//2]]

        # Search brain entries if enabled
        if include_brain:
            brain_results = self._search_brain_entries(query_lower, max_results//4)
            results["brain_entries"] = brain_results

        # Search project files if enabled
        if include_files:
            file_results = self._search_project_files(query_lower, max_results//4)
            results["project_files"] = file_results

        results["total_found"] = len(results["modules"]) + len(results["brain_entries"]) + len(results["project_files"])
        return results
    
    def _search_brain_entries(self, query_lower: str, max_results: int) -> List[Dict[str, Any]]:
        """Search brain entries for matching content."""
        brain_results = []
        
        try:
            # Try to import brain functionality
            brain_data_file = get_mywork_root() / "tools" / "brain_data.json"
            if brain_data_file.exists():
                import json
                brain_data = json.loads(brain_data_file.read_text())
                entries = brain_data.get("entries", [])
                
                for entry in entries:
                    score = 0
                    
                    # Search in content
                    content = entry.get("content", "").lower()
                    if query_lower in content:
                        score += 8
                    
                    # Search in tags
                    tags = entry.get("tags", [])
                    for tag in tags:
                        if query_lower in tag.lower():
                            score += 5
                    
                    # Search in type
                    entry_type = entry.get("type", "").lower()
                    if query_lower in entry_type:
                        score += 3
                    
                    # Search in context
                    context = entry.get("context", "").lower()
                    if query_lower in context:
                        score += 2
                    
                    if score > 0:
                        brain_results.append({
                            "score": score,
                            "id": entry.get("id", ""),
                            "type": entry.get("type", ""),
                            "content": entry.get("content", "")[:200] + "..." if len(entry.get("content", "")) > 200 else entry.get("content", ""),
                            "tags": entry.get("tags", []),
                            "created": entry.get("created", ""),
                            "status": entry.get("status", "")
                        })
                
                # Sort and limit results
                brain_results.sort(key=lambda x: x["score"], reverse=True)
                brain_results = brain_results[:max_results]
                
        except Exception:
            # Silently fail if brain search is not available
            pass
        
        return brain_results
    
    def _search_project_files(self, query_lower: str, max_results: int) -> List[Dict[str, Any]]:
        """Search project files for matching content."""
        file_results = []
        
        try:
            projects_dir = get_mywork_root() / "projects"
            if not projects_dir.exists():
                return file_results
            
            searchable_extensions = {'.py', '.js', '.jsx', '.ts', '.tsx', '.vue', '.md', '.txt', '.json', '.yaml', '.yml'}
            files_checked = 0
            max_files_to_check = 1000  # Limit to prevent performance issues
            
            for project_dir in projects_dir.iterdir():
                if not project_dir.is_dir() or project_dir.name.startswith('.'):
                    continue
                
                for file_path in project_dir.rglob("*"):
                    if files_checked >= max_files_to_check:
                        break
                    
                    if (not file_path.is_file() or 
                        file_path.suffix.lower() not in searchable_extensions or
                        any(exclude in str(file_path) for exclude in ['.git', 'node_modules', '__pycache__', '.pytest_cache', 'venv', '.env'])):
                        continue
                    
                    try:
                        content = file_path.read_text(encoding='utf-8', errors='ignore')
                        content_lower = content.lower()
                        
                        if query_lower in content_lower:
                            score = 0
                            
                            # Filename match
                            if query_lower in file_path.name.lower():
                                score += 10
                            
                            # Path match
                            if query_lower in str(file_path.relative_to(projects_dir)).lower():
                                score += 5
                            
                            # Content match - count occurrences
                            occurrences = content_lower.count(query_lower)
                            score += min(occurrences, 20)  # Cap at 20 to prevent skewing
                            
                            # Find matching lines for preview
                            matching_lines = []
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if query_lower in line.lower():
                                    matching_lines.append({
                                        "line_number": i + 1,
                                        "content": line.strip()[:200]  # Limit line length
                                    })
                                    if len(matching_lines) >= 3:  # Max 3 matching lines
                                        break
                            
                            file_results.append({
                                "score": score,
                                "file_path": str(file_path.relative_to(projects_dir)),
                                "project": project_dir.name,
                                "file_type": file_path.suffix,
                                "matching_lines": matching_lines,
                                "total_matches": occurrences
                            })
                        
                        files_checked += 1
                    
                    except Exception:
                        continue
                
                if files_checked >= max_files_to_check:
                    break
            
            # Sort and limit results
            file_results.sort(key=lambda x: x["score"], reverse=True)
            file_results = file_results[:max_results]
            
        except Exception:
            # Silently fail if file search is not available
            pass
        
        return file_results

    def get_by_type(self, module_type: str) -> List[Module]:
        """Get all modules of a specific type."""
        ids = self.type_index.get(module_type, set())
        return [self.modules[id] for id in ids if id in self.modules]

    def get_by_project(self, project: str) -> List[Module]:
        """Get all modules in a project."""
        ids = self.project_index.get(project, set())
        return [self.modules[id] for id in ids if id in self.modules]

    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        stats = {
            "total_modules": len(self.modules),
            "by_type": {},
            "by_project": {},
            "by_language": defaultdict(int),
            "top_tags": defaultdict(int),
        }

        for module in self.modules.values():
            stats["by_type"][module.type] = stats["by_type"].get(module.type, 0) + 1
            stats["by_project"][module.project] = stats["by_project"].get(module.project, 0) + 1
            stats["by_language"][module.language] += 1
            for tag in module.tags:
                stats["top_tags"][tag] += 1

        # Sort tags by frequency
        stats["top_tags"] = dict(
            sorted(stats["top_tags"].items(), key=lambda x: x[1], reverse=True)[:20]
        )

        return stats


class ProjectScanner:
    """Scans projects for modules and patterns."""

    def __init__(self, registry: ModuleRegistry):
        self.registry = registry
        self.projects_dir = registry.projects_dir

    def scan_all_projects(self) -> int:
        """Scan all projects in the projects directory."""
        if not self.projects_dir.exists():
            print(f"Projects directory not found: {self.projects_dir}")
            return 0

        total = 0
        for project_dir in self.projects_dir.iterdir():
            if project_dir.is_symlink():
                continue
            if project_dir.is_dir() and not project_dir.name.startswith((".", "_")):
                count = self.scan_project(project_dir)
                total += count
                print(f"  📦 {project_dir.name}: {count} modules found")

        self.registry.save()
        return total

    def scan_project(self, project_path: Path) -> int:
        """Scan a single project for modules."""
        project_name = project_path.name
        count = 0

        for lang, patterns in SCAN_PATTERNS.items():
            for pattern in patterns:
                for file_path in project_path.rglob(pattern):
                    if any(parent.is_symlink() for parent in file_path.parents):
                        continue
                    # Skip excluded directories
                    if any(skip in file_path.parts for skip in SKIP_DIRS):
                        continue

                    try:
                        modules = self.scan_file(file_path, project_name, lang)
                        count += len(modules)
                    except Exception:
                        # Skip files that can't be read
                        pass

        return count

    def scan_file(self, file_path: Path, project: str, language: str) -> List[Module]:
        """Scan a single file for modules."""
        modules = []

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return modules

        lines = content.split("\n")
        relative_path = str(file_path.relative_to(self.projects_dir / project))

        # Get file modification time
        mtime = datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()

        for module_type, lang_patterns in MODULE_PATTERNS.items():
            if language not in lang_patterns:
                continue

            for pattern in lang_patterns[language]:
                for match in re.finditer(pattern, content):
                    # Find line number
                    pos = match.start()
                    line_num = content[:pos].count("\n") + 1

                    # Extract name
                    groups = match.groups()
                    name = groups[-1] if groups else match.group(0)

                    if not name or len(name) < 2:
                        continue

                    # Generate module ID
                    mod_id = self.registry._generate_id(project, relative_path, name)

                    # Extract context (surrounding lines for description)
                    start_line = max(0, line_num - 2)
                    end_line = min(len(lines), line_num + 3)
                    context = "\n".join(lines[start_line:end_line])

                    # Extract description from docstring/comment
                    description = self._extract_description(content, pos, language)

                    # Generate tags
                    tags = self._generate_tags(name, module_type, relative_path)

                    # Extract dependencies (imports)
                    deps = self._extract_dependencies(content, language)

                    # Extract exports
                    exports = self._extract_exports(content, name, language)

                    # Create module
                    module = Module(
                        id=mod_id,
                        name=name,
                        type=module_type,
                        project=project,
                        file_path=relative_path,
                        line_number=line_num,
                        language=language,
                        description=description[:200] if description else "",
                        tags=tags,
                        dependencies=deps[:10],  # Limit to first 10
                        exports=exports[:10],
                        last_modified=mtime,
                        hash=hashlib.md5(context.encode()).hexdigest()[:8],
                    )

                    self.registry.add_module(module)
                    modules.append(module)

        return modules

    def _extract_description(self, content: str, pos: int, language: str) -> str:
        """Extract description from docstring or comment."""
        # Look for docstring or comment before the match
        before = content[max(0, pos - 500) : pos]

        if language == "python":
            # Look for docstring
            match = re.search(r'"""([^"]+)"""', before)
            if match:
                return match.group(1).strip()
            match = re.search(r"'''([^']+)'''", before)
            if match:
                return match.group(1).strip()
            # Look for comment
            match = re.search(r"#\s*(.+)$", before, re.MULTILINE)
            if match:
                return match.group(1).strip()

        elif language in ("typescript", "javascript"):
            # Look for JSDoc
            match = re.search(r"/\*\*\s*\n?\s*\*?\s*([^\n*]+)", before)
            if match:
                return match.group(1).strip()
            # Look for single line comment
            match = re.search(r"//\s*(.+)$", before, re.MULTILINE)
            if match:
                return match.group(1).strip()

        return ""

    def _generate_tags(self, name: str, module_type: str, file_path: str) -> List[str]:
        """Generate tags from module name and context."""
        tags = [module_type]

        # Split camelCase/PascalCase
        words = re.findall(r"[A-Z][a-z]+|[a-z]+", name)
        tags.extend([w.lower() for w in words if len(w) > 2])

        # Add path-based tags
        parts = Path(file_path).parts
        for part in parts:
            if part not in ("src", "lib", "app", "index"):
                tags.append(part.lower())

        return list(set(tags))[:10]  # Dedupe and limit

    def _extract_dependencies(self, content: str, language: str) -> List[str]:
        """Extract import statements."""
        deps = []

        if language == "python":
            for match in re.finditer(r"(?:from|import)\s+([\w.]+)", content):
                deps.append(match.group(1))

        elif language in ("typescript", "javascript"):
            for match in re.finditer(r'(?:import|require)\s*\(?["\']([^"\']+)["\']', content):
                deps.append(match.group(1))

        return list(set(deps))

    def _extract_exports(self, content: str, name: str, language: str) -> List[str]:
        """Extract what the module exports."""
        exports = [name]

        if language == "python":
            for match in re.finditer(rf"{name}\.\w+", content):
                exports.append(match.group(0))

        elif language in ("typescript", "javascript"):
            for match in re.finditer(
                r"export\s+(?:const|function|class|type|interface)\s+(\w+)", content
            ):
                exports.append(match.group(1))

        return list(set(exports))


def print_search_results(modules, query: str):
    """Print formatted search results.
    
    Args:
        modules: Either a list of Module objects or a dict from enhanced search
                 with keys: modules, brain_entries, project_files, total_found
        query: The search query string
    """
    # Handle dict results from enhanced search
    if isinstance(modules, dict):
        total = modules.get("total_found", 0)
        mod_list = modules.get("modules", [])
        brain_entries = modules.get("brain_entries", [])
        project_files = modules.get("project_files", [])
        
        if total == 0 and not mod_list and not brain_entries and not project_files:
            print(f"\n❌ No results found matching '{query}'")
            return
        
        print(f"\n🔍 Search Results for '{query}' ({total} found)")
        print("=" * 60)
        
        if mod_list:
            print(f"\n📦 Modules ({len(mod_list)}):")
            for i, mod in enumerate(mod_list[:20], 1):
                print(f"\n  {i}. {mod.name}")
                print(f"     Type: {mod.type} | Project: {mod.project}")
                print(f"     File: {mod.file_path}:{mod.line_number}")
                if mod.description:
                    print(f"     Desc: {mod.description[:80]}...")
                print(f"     Tags: {', '.join(mod.tags[:5])}")
        
        if brain_entries:
            print(f"\n🧠 Brain Entries ({len(brain_entries)}):")
            for i, entry in enumerate(brain_entries[:10], 1):
                title = entry.get("title", entry.get("name", "Untitled"))
                print(f"  {i}. {title}")
        
        if project_files:
            print(f"\n📁 Project Files ({len(project_files)}):")
            for i, f in enumerate(project_files[:10], 1):
                name = f.get("name", f.get("path", "Unknown"))
                print(f"  {i}. {name}")
        
        return

    # Handle list of Module objects (legacy)
    if not modules:
        print(f"\n❌ No modules found matching '{query}'")
        return

    print(f"\n🔍 Search Results for '{query}' ({len(modules)} found)")
    print("=" * 60)

    for i, mod in enumerate(modules[:20], 1):
        print(f"\n{i}. {mod.name}")
        print(f"   Type: {mod.type} | Project: {mod.project}")
        print(f"   File: {mod.file_path}:{mod.line_number}")
        if mod.description:
            print(f"   Desc: {mod.description[:80]}...")
        print(f"   Tags: {', '.join(mod.tags[:5])}")

    if len(modules) > 20:
        print(f"\n... and {len(modules) - 20} more results")


def print_stats(stats: Dict[str, Any]):
    """Print registry statistics."""
    print("\n📊 Module Registry Statistics")
    print("=" * 60)
    print(f"\nTotal Modules: {stats['total_modules']}")

    print("\n📦 By Type:")
    for type_name, count in sorted(stats["by_type"].items(), key=lambda x: x[1], reverse=True):
        print(f"   {type_name}: {count}")

    print("\n📁 By Project:")
    for project, count in sorted(stats["by_project"].items(), key=lambda x: x[1], reverse=True):
        print(f"   {project}: {count}")

    print("\n🏷️ Top Tags:")
    for tag, count in list(stats["top_tags"].items())[:10]:
        print(f"   {tag}: {count}")


def export_to_markdown(registry: ModuleRegistry):
    """Export registry to markdown file."""
    stats = registry.get_stats()

    content = f"""# MyWork Module Registry

> Auto-generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> Total Modules: {stats['total_modules']}

## Overview

This registry contains all reusable modules discovered across MyWork projects.
Use it to find existing implementations before building new ones.

## Quick Search Commands

```bash
# Search for modules
python tools/module_registry.py search "auth"
python tools/module_registry.py search "api endpoint"

# List by type
python tools/module_registry.py list api_endpoint
python tools/module_registry.py list component
```

## Statistics

### By Type
| Type | Count |
|------|-------|
"""

    for type_name, count in sorted(stats["by_type"].items(), key=lambda x: x[1], reverse=True):
        content += f"| {type_name} | {count} |\n"

    content += "\n### By Project\n| Project | Modules |\n|---------|--------|\n"

    for project, count in sorted(stats["by_project"].items(), key=lambda x: x[1], reverse=True):
        content += f"| {project} | {count} |\n"

    content += "\n## Modules by Type\n\n"

    for mod_type in sorted(stats["by_type"].keys()):
        modules = registry.get_by_type(mod_type)
        if not modules:
            continue

        content += f"### {mod_type.replace('_', ' ').title()}\n\n"

        for mod in sorted(modules, key=lambda x: x.project):
            content += f"- **{mod.name}** ({mod.project})\n"
            content += f"  - File: `{mod.file_path}:{mod.line_number}`\n"
            if mod.description:
                content += f"  - {mod.description[:100]}\n"
            content += f"  - Tags: {', '.join(mod.tags[:5])}\n"
            content += "\n"

    with open(registry.registry_md, "w") as f:
        f.write(content)

    print(f"✅ Exported to {registry.registry_md}")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1].lower()
    registry = ModuleRegistry()

    if command == "scan":
        print("\n🔍 Scanning projects for modules...")
        scanner = ProjectScanner(registry)
        count = scanner.scan_all_projects()
        print(f"\n✅ Scan complete! {count} modules indexed.")
        print(f"   Registry saved to: {registry.registry_file}")

    elif command == "search":
        if len(sys.argv) < 3:
            print("Usage: python module_registry.py search <query> [type]")
            sys.exit(1)

        query = sys.argv[2]
        type_filter = sys.argv[3] if len(sys.argv) > 3 else None
        results = registry.search(query, type_filter)
        print_search_results(results, query)

    elif command == "list":
        type_filter = sys.argv[2] if len(sys.argv) > 2 else None

        if type_filter:
            modules = registry.get_by_type(type_filter)
            print(f"\n📋 Modules of type '{type_filter}' ({len(modules)} found)")
        else:
            modules = list(registry.modules.values())
            print(f"\n📋 All Modules ({len(modules)} total)")

        print("=" * 60)

        for mod in sorted(modules, key=lambda x: (x.project, x.name))[:50]:
            print(f"  [{mod.type}] {mod.name} ({mod.project}/{mod.file_path})")

        if len(modules) > 50:
            print(f"\n... and {len(modules) - 50} more")

    elif command == "show":
        if len(sys.argv) < 3:
            print("Usage: python module_registry.py show <module_id>")
            sys.exit(1)

        mod_id = sys.argv[2]
        module = registry.modules.get(mod_id)

        if not module:
            # Try to find by name
            matches = [m for m in registry.modules.values() if mod_id.lower() in m.name.lower()]
            if matches:
                module = matches[0]

        if module:
            print(f"\n📦 Module: {module.name}")
            print("=" * 60)
            print(f"   ID:          {module.id}")
            print(f"   Type:        {module.type}")
            print(f"   Project:     {module.project}")
            print(f"   File:        {module.file_path}:{module.line_number}")
            print(f"   Language:    {module.language}")
            print(f"   Description: {module.description}")
            print(f"   Tags:        {', '.join(module.tags)}")
            print(f"   Dependencies: {', '.join(module.dependencies[:5])}")
            print(f"   Last Modified: {module.last_modified}")
            print(f"\n   Open in editor:")
            full_path = registry.projects_dir / module.project / module.file_path
            print(f"   code -g {full_path}:{module.line_number}")
        else:
            print(f"❌ Module not found: {mod_id}")

    elif command == "stats":
        stats = registry.get_stats()
        print_stats(stats)

    elif command == "export":
        export_to_markdown(registry)

    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
