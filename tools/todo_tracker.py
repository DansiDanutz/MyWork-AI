#!/usr/bin/env python3
"""MyWork TODO Tracker — Find and categorize technical debt.

Usage:
    mw todo              Show all TODOs/FIXMEs grouped by priority
    mw todo --stats      Show summary statistics only
    mw todo --file X     Filter to specific file
    mw todo --type fixme Filter by type (todo/fixme/hack/xxx)
    mw todo --json       Output as JSON
"""

import os
import re
import sys
import json
from pathlib import Path
from collections import defaultdict

# Patterns to scan
MARKERS = {
    "FIXME": {"priority": "high", "icon": "🔴", "desc": "Known bugs to fix"},
    "HACK": {"priority": "high", "icon": "🟠", "desc": "Dirty workarounds"},
    "XXX": {"priority": "medium", "icon": "🟡", "desc": "Needs attention"},
    "TODO": {"priority": "low", "icon": "🔵", "desc": "Future improvements"},
    "NOTE": {"priority": "info", "icon": "📝", "desc": "Developer notes"},
}

PATTERN = re.compile(
    r"#\s*(TODO|FIXME|HACK|XXX|NOTE)\b[:\s]*(.*)", re.IGNORECASE
)

SKIP_DIRS = {
    "__pycache__", ".git", "node_modules", ".venv", "venv",
    ".mypy_cache", ".pytest_cache", "dist", "build", "egg-info",
}

EXTENSIONS = {".py", ".js", ".ts", ".tsx", ".jsx", ".sh", ".yaml", ".yml", ".toml", ".md"}


def scan_file(filepath: Path):
    """Scan a single file for TODO markers."""
    items = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for lineno, line in enumerate(f, 1):
                m = PATTERN.search(line)
                if m:
                    marker = m.group(1).upper()
                    text = m.group(2).strip()
                    items.append({
                        "file": str(filepath),
                        "line": lineno,
                        "marker": marker,
                        "text": text,
                        "priority": MARKERS.get(marker, {}).get("priority", "low"),
                    })
    except (PermissionError, OSError):
        pass
    return items


def scan_project(root: str, file_filter=None, type_filter=None):
    """Scan entire project for TODO markers."""
    root = Path(root)
    all_items = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            fpath = Path(dirpath) / fname
            if fpath.suffix not in EXTENSIONS:
                continue
            rel = str(fpath.relative_to(root))
            if file_filter and file_filter not in rel:
                continue
            items = scan_file(fpath)
            for item in items:
                item["file"] = rel
                if type_filter and item["marker"].lower() != type_filter.lower():
                    continue
                all_items.append(item)
    return all_items


def print_grouped(items):
    """Print items grouped by priority."""
    priority_order = ["high", "medium", "low", "info"]
    by_priority = defaultdict(list)
    for item in items:
        by_priority[item["priority"]].append(item)

    print(f"\n\033[1m📋 MyWork TODO Tracker\033[0m")
    print("=" * 60)
    print(f"   Found \033[1m{len(items)}\033[0m markers across project\n")

    for pri in priority_order:
        group = by_priority.get(pri, [])
        if not group:
            continue
        # Find matching marker info
        icons = [v["icon"] for k, v in MARKERS.items() if v["priority"] == pri]
        icon = icons[0] if icons else "•"
        labels = [k for k, v in MARKERS.items() if v["priority"] == pri]
        label = "/".join(labels)

        print(f"{icon} \033[1m{label}\033[0m ({len(group)} items) — Priority: {pri.upper()}")
        print("-" * 50)

        # Group by file
        by_file = defaultdict(list)
        for item in group:
            by_file[item["file"]].append(item)

        for filepath, file_items in sorted(by_file.items()):
            print(f"   \033[96m{filepath}\033[0m")
            for item in file_items:
                text = item["text"][:70] + ("..." if len(item["text"]) > 70 else "")
                print(f"      L{item['line']:>4}: {text}")
        print()


def print_stats(items):
    """Print summary statistics."""
    print(f"\n\033[1m📊 TODO Statistics\033[0m")
    print("=" * 40)

    by_marker = defaultdict(int)
    by_file = defaultdict(int)
    for item in items:
        by_marker[item["marker"]] += 1
        by_file[item["file"]] += 1

    print("\nBy Type:")
    for marker in ["FIXME", "HACK", "XXX", "TODO", "NOTE"]:
        count = by_marker.get(marker, 0)
        if count:
            info = MARKERS[marker]
            bar = "█" * min(count, 30)
            print(f"   {info['icon']} {marker:>5}: {count:>3} {bar}")

    print(f"\nTop Files (most markers):")
    for filepath, count in sorted(by_file.items(), key=lambda x: -x[1])[:10]:
        print(f"   {count:>3} — {filepath}")

    print(f"\n   Total: {len(items)} markers in {len(by_file)} files")


def main():
    args = sys.argv[1:]
    project_root = os.environ.get("MW_ROOT", os.getcwd())

    file_filter = None
    type_filter = None
    as_json = "--json" in args
    stats_only = "--stats" in args

    if "--file" in args:
        idx = args.index("--file")
        file_filter = args[idx + 1] if idx + 1 < len(args) else None

    if "--type" in args:
        idx = args.index("--type")
        type_filter = args[idx + 1] if idx + 1 < len(args) else None

    items = scan_project(project_root, file_filter, type_filter)

    if as_json:
        print(json.dumps(items, indent=2))
    elif stats_only:
        print_stats(items)
    else:
        print_grouped(items)
        print_stats(items)


if __name__ == "__main__":
    main()
