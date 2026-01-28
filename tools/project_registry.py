#!/usr/bin/env python3
"""
Project Registry Tool
=====================
Indexes project metadata (project.yaml) for MyWork.

Usage:
    python tools/project_registry.py scan
    python tools/project_registry.py list
    python tools/project_registry.py show <project-name>
    python tools/project_registry.py stats
    python tools/project_registry.py export
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError:  # pragma: no cover - optional dependency
    yaml = None

from config import (
    PROJECTS_DIR,
    PLANNING_DIR,
    PROJECT_REGISTRY_JSON,
    PROJECT_REGISTRY_MD,
    Colors,
    print_error,
    print_header,
    print_info,
    print_success,
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_scalar(value: str) -> Any:
    if value.startswith(('"', "'")) and value.endswith(('"', "'")):
        return value[1:-1]
    lowered = value.lower()
    if lowered in {"true", "yes"}:
        return True
    if lowered in {"false", "no"}:
        return False
    return value


def _simple_yaml_load(text: str) -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        if ":" not in stripped:
            i += 1
            continue
        key, raw_value = stripped.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        if raw_value:
            data[key] = _parse_scalar(raw_value)
            i += 1
            continue
        # Look ahead for list or mapping
        j = i + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        if j < len(lines) and lines[j].lstrip().startswith("- "):
            items: List[Any] = []
            while j < len(lines) and lines[j].lstrip().startswith("- "):
                items.append(_parse_scalar(lines[j].lstrip()[2:].strip()))
                j += 1
            data[key] = items
            i = j
            continue
        if j < len(lines) and lines[j].startswith("  "):
            mapping: Dict[str, Any] = {}
            while j < len(lines) and lines[j].startswith("  "):
                inner = lines[j].strip()
                if not inner or inner.startswith("#"):
                    j += 1
                    continue
                if ":" in inner:
                    inner_key, inner_value = inner.split(":", 1)
                    mapping[inner_key.strip()] = _parse_scalar(inner_value.strip())
                j += 1
            data[key] = mapping
            i = j
            continue
        data[key] = {}
        i += 1
    return data


def _safe_load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        if yaml:
            data = yaml.safe_load(path.read_text())
        else:
            data = _simple_yaml_load(path.read_text())
        return data or {}
    except Exception as exc:
        print_error(f"Failed to read {path}: {exc}")
        return {}


def _normalize_bool(value: Any) -> Optional[bool]:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "yes", "1"}:
            return True
        if lowered in {"false", "no", "0"}:
            return False
    return None


def _build_project_entry(project_path: Path) -> Dict[str, Any]:
    metadata_path = project_path / "project.yaml"
    metadata = _safe_load_yaml(metadata_path)

    has_gsd = (project_path / ".planning" / "STATE.md").exists()
    has_start = (project_path / "start.sh").exists() or (project_path / "start.bat").exists()

    def _list(value: Any) -> List[str]:
        if isinstance(value, list):
            return [str(item) for item in value]
        if value is None:
            return []
        return [str(value)]

    marketplace = _normalize_bool(metadata.get("marketplace"))
    brain_contribution = _normalize_bool(metadata.get("brain_contribution"))

    return {
        "name": str(metadata.get("name") or project_path.name),
        "path": str(project_path),
        "type": str(metadata.get("type") or "unknown"),
        "owner": str(metadata.get("owner") or ""),
        "status": str(metadata.get("status") or "unknown"),
        "marketplace": marketplace if marketplace is not None else False,
        "brain_contribution": brain_contribution if brain_contribution is not None else False,
        "stack": _list(metadata.get("stack")),
        "tags": _list(metadata.get("tags")),
        "description": str(metadata.get("description") or ""),
        "deployment": metadata.get("deployment") or {},
        "has_gsd": has_gsd,
        "has_start": has_start,
        "metadata_path": str(metadata_path) if metadata_path.exists() else None,
        "missing_metadata": not metadata_path.exists(),
    }


def scan_projects() -> Dict[str, Any]:
    if not PROJECTS_DIR.exists():
        print_error("Projects directory not found")
        return {"scanned_at": _now_iso(), "projects": {}}

    projects = [
        p for p in PROJECTS_DIR.iterdir() if p.is_dir() and not p.name.startswith((".", "_"))
    ]

    registry: Dict[str, Any] = {"scanned_at": _now_iso(), "projects": {}}
    for project in sorted(projects):
        entry = _build_project_entry(project)
        registry["projects"][project.name] = entry

    PLANNING_DIR.mkdir(parents=True, exist_ok=True)
    PROJECT_REGISTRY_JSON.write_text(json.dumps(registry, indent=2, sort_keys=True))
    print_success(f"Project registry updated: {PROJECT_REGISTRY_JSON}")
    return registry


def load_registry() -> Dict[str, Any]:
    if PROJECT_REGISTRY_JSON.exists():
        try:
            return json.loads(PROJECT_REGISTRY_JSON.read_text())
        except Exception as exc:
            print_error(f"Failed to read registry: {exc}")
    return scan_projects()


def format_flags(entry: Dict[str, Any]) -> str:
    flags = []
    if entry.get("marketplace"):
        flags.append("🛒")
    if entry.get("brain_contribution"):
        flags.append("🧠")
    if entry.get("missing_metadata"):
        flags.append("⚠️")
    return "".join(flags)


def cmd_list() -> int:
    registry = load_registry()
    projects = registry.get("projects", {})

    print_header("📁 MyWork Project Registry")
    print("=" * 50)

    if not projects:
        print("No projects found.")
        return 0

    for name in sorted(projects.keys()):
        entry = projects[name]
        type_label = entry.get("type", "unknown")
        status = entry.get("status", "unknown")
        flags = format_flags(entry)
        print(f"   {name} ({type_label}, {status}) {flags}")

    print(f"\n   Total: {len(projects)} projects")
    return 0


def cmd_show(args: List[str]) -> int:
    if not args:
        print("Usage: python tools/project_registry.py show <project-name>")
        return 1

    registry = load_registry()
    project = registry.get("projects", {}).get(args[0])
    if not project:
        print_error(f"Project not found: {args[0]}")
        return 1

    print(json.dumps(project, indent=2))
    return 0


def cmd_stats() -> int:
    registry = load_registry()
    projects = registry.get("projects", {}).values()

    total = 0
    by_type: Dict[str, int] = {}
    by_status: Dict[str, int] = {}
    marketplace = 0

    for entry in projects:
        total += 1
        by_type[entry.get("type", "unknown")] = by_type.get(entry.get("type", "unknown"), 0) + 1
        by_status[entry.get("status", "unknown")] = (
            by_status.get(entry.get("status", "unknown"), 0) + 1
        )
        if entry.get("marketplace"):
            marketplace += 1

    print_header("📊 Project Registry Stats")
    print(f"Total projects: {total}")
    print(f"Marketplace-ready: {marketplace}")
    print("By type:")
    for key in sorted(by_type):
        print(f"  - {key}: {by_type[key]}")
    print("By status:")
    for key in sorted(by_status):
        print(f"  - {key}: {by_status[key]}")
    return 0


def cmd_export() -> int:
    registry = load_registry()
    projects = registry.get("projects", {})

    lines = ["# Project Registry", "", f"Last updated: {registry.get('scanned_at', 'unknown')}", ""]
    lines.append("| Project | Type | Status | Marketplace | Brain | Description | Deployment |")
    lines.append("|---|---|---|---|---|---|---|")

    for name in sorted(projects.keys()):
        entry = projects[name]
        marketplace = "yes" if entry.get("marketplace") else "no"
        brain = "yes" if entry.get("brain_contribution") else "no"
        description = entry.get("description", "").replace("|", "/")
        deployment = entry.get("deployment") or {}
        deploy_url = ""
        if isinstance(deployment, dict):
            deploy_url = (
                deployment.get("url")
                or deployment.get("frontend_url")
                or deployment.get("backend_url")
                or ""
            )
        lines.append(
            f"| {name} | {entry.get('type', '')} | {entry.get('status', '')} | {marketplace} | {brain} | {description} | {deploy_url} |"
        )

    PROJECT_REGISTRY_MD.write_text("\n".join(lines) + "\n")
    print_success(f"Exported registry: {PROJECT_REGISTRY_MD}")
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == "scan":
        scan_projects()
        return 0
    if cmd == "list":
        return cmd_list()
    if cmd == "show":
        return cmd_show(args)
    if cmd == "stats":
        return cmd_stats()
    if cmd == "export":
        return cmd_export()

    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
