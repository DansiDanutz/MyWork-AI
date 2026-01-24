#!/usr/bin/env python3
"""
Brain Manager for Master Orchestrator
======================================
Manages the persistent knowledge vault (BRAIN.md).

Usage:
    python brain.py add <type> <content>    # Add new knowledge
    python brain.py update <id> <content>   # Update existing entry
    python brain.py deprecate <id>          # Mark as deprecated
    python brain.py search <query>          # Search the brain
    python brain.py review                  # Show entries needing attention
    python brain.py cleanup                 # Remove deprecated entries
    python brain.py stats                   # Show brain statistics
    python brain.py export                  # Export to JSON for backup

Types:
    lesson      - Something learned from experience
    pattern     - A proven approach that works
    antipattern - Something to avoid
    tip         - Quick tool/usage tip
    insight     - Integration or architecture insight
    experiment  - Something to try

Examples:
    python brain.py add lesson "Always validate before deploy" --context "Broke prod once"
    python brain.py add pattern "Error Handling" --steps "1. Log\\n2. Notify\\n3. Recover"
    python brain.py search "api"
    python brain.py deprecate lesson-003
"""

import os
import sys
import re
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field

# Configuration - Import from shared config
try:
    from config import MYWORK_ROOT, BRAIN_DATA_JSON as BRAIN_JSON, BRAIN_MD as BRAIN_FILE
except ImportError:
    def _get_mywork_root():
        if env_root := os.environ.get("MYWORK_ROOT"):
            return Path(env_root)
        script_dir = Path(__file__).resolve().parent
        return script_dir.parent if script_dir.name == "tools" else Path.home() / "MyWork"
    MYWORK_ROOT = _get_mywork_root()
    BRAIN_FILE = MYWORK_ROOT / ".planning" / "BRAIN.md"
    BRAIN_JSON = MYWORK_ROOT / ".planning" / "brain_data.json"

# Entry types and their sections in BRAIN.md
ENTRY_TYPES = {
    "lesson": "Lessons Learned",
    "pattern": "Patterns That Work",
    "antipattern": "Anti-Patterns to Avoid",
    "tip": "Tool Wisdom",
    "insight": "Integration Insights",
    "experiment": "Pending Experiments",
}


@dataclass
class BrainEntry:
    """Represents a single piece of knowledge."""
    id: str
    type: str
    content: str
    context: str = ""
    status: str = "TESTED"  # TESTED, EXPERIMENTAL, DEPRECATED
    date_added: str = ""
    date_updated: str = ""
    tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.date_added:
            self.date_added = datetime.now().strftime("%Y-%m-%d")
        if not self.date_updated:
            self.date_updated = self.date_added

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "BrainEntry":
        return cls(**data)


class BrainManager:
    """Manages the brain knowledge base."""

    def __init__(self):
        self.entries: Dict[str, BrainEntry] = {}
        self.load()

    def load(self):
        """Load entries from JSON backup if exists."""
        if BRAIN_JSON.exists():
            try:
                with open(BRAIN_JSON) as f:
                    data = json.load(f)
                    for entry_data in data.get("entries", []):
                        entry = BrainEntry.from_dict(entry_data)
                        self.entries[entry.id] = entry
            except (json.JSONDecodeError, TypeError) as e:
                print(f"Warning: Could not load brain data: {e}")

    def save(self):
        """Save entries to JSON backup."""
        BRAIN_JSON.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "entry_count": len(self.entries),
            "entries": [e.to_dict() for e in self.entries.values()]
        }
        with open(BRAIN_JSON, "w") as f:
            json.dump(data, f, indent=2)

    def generate_id(self, entry_type: str) -> str:
        """Generate a unique ID for an entry."""
        type_entries = [e for e in self.entries.values() if e.type == entry_type]
        next_num = len(type_entries) + 1
        return f"{entry_type}-{next_num:03d}"

    def add(self, entry_type: str, content: str, context: str = "",
            status: str = "TESTED", tags: List[str] = None) -> BrainEntry:
        """Add a new entry to the brain."""
        if entry_type not in ENTRY_TYPES:
            raise ValueError(f"Unknown type: {entry_type}. Valid: {', '.join(ENTRY_TYPES.keys())}")

        entry_id = self.generate_id(entry_type)
        entry = BrainEntry(
            id=entry_id,
            type=entry_type,
            content=content,
            context=context,
            status=status,
            tags=tags or []
        )
        self.entries[entry_id] = entry
        self.save()
        self._update_brain_md()
        return entry

    def update(self, entry_id: str, content: str = None, context: str = None,
               status: str = None, tags: List[str] = None) -> Optional[BrainEntry]:
        """Update an existing entry."""
        if entry_id not in self.entries:
            return None

        entry = self.entries[entry_id]
        if content:
            entry.content = content
        if context:
            entry.context = context
        if status:
            entry.status = status
        if tags is not None:
            entry.tags = tags

        entry.date_updated = datetime.now().strftime("%Y-%m-%d")
        self.save()
        self._update_brain_md()
        return entry

    def deprecate(self, entry_id: str) -> Optional[BrainEntry]:
        """Mark an entry as deprecated."""
        return self.update(entry_id, status="DEPRECATED")

    def delete(self, entry_id: str) -> bool:
        """Delete an entry permanently."""
        if entry_id in self.entries:
            del self.entries[entry_id]
            self.save()
            self._update_brain_md()
            return True
        return False

    def search(self, query: str) -> List[BrainEntry]:
        """Search entries by content, context, or tags."""
        query_lower = query.lower()
        results = []

        for entry in self.entries.values():
            score = 0

            if query_lower in entry.content.lower():
                score += 10
            if query_lower in entry.context.lower():
                score += 5
            for tag in entry.tags:
                if query_lower in tag.lower():
                    score += 3

            if score > 0:
                results.append((score, entry))

        results.sort(key=lambda x: x[0], reverse=True)
        return [e for _, e in results]

    def get_by_type(self, entry_type: str) -> List[BrainEntry]:
        """Get all entries of a specific type."""
        return [e for e in self.entries.values() if e.type == entry_type]

    def get_deprecated(self) -> List[BrainEntry]:
        """Get all deprecated entries."""
        return [e for e in self.entries.values() if e.status == "DEPRECATED"]

    def get_experimental(self) -> List[BrainEntry]:
        """Get all experimental entries."""
        return [e for e in self.entries.values() if e.status == "EXPERIMENTAL"]

    def cleanup(self) -> int:
        """Remove all deprecated entries."""
        deprecated = self.get_deprecated()
        for entry in deprecated:
            del self.entries[entry.id]
        self.save()
        self._update_brain_md()
        return len(deprecated)

    def get_stats(self) -> Dict[str, Any]:
        """Get brain statistics."""
        stats = {
            "total_entries": len(self.entries),
            "by_type": {},
            "by_status": {},
            "oldest": None,
            "newest": None,
        }

        for entry in self.entries.values():
            stats["by_type"][entry.type] = stats["by_type"].get(entry.type, 0) + 1
            stats["by_status"][entry.status] = stats["by_status"].get(entry.status, 0) + 1

        if self.entries:
            sorted_by_date = sorted(self.entries.values(), key=lambda e: e.date_added)
            stats["oldest"] = sorted_by_date[0].date_added
            stats["newest"] = sorted_by_date[-1].date_added

        return stats

    def _update_brain_md(self):
        """Regenerate BRAIN.md from entries."""
        # Read the current BRAIN.md to preserve manual sections
        if not BRAIN_FILE.exists():
            return

        content = BRAIN_FILE.read_text()

        # For now, we'll append new entries to the changelog
        # A more sophisticated version would rebuild sections

        # Update the "Last updated" line
        content = re.sub(
            r'> Last updated: \d{4}-\d{2}-\d{2}',
            f'> Last updated: {datetime.now().strftime("%Y-%m-%d")}',
            content
        )

        BRAIN_FILE.write_text(content)


def print_entry(entry: BrainEntry, verbose: bool = False):
    """Print a formatted entry."""
    status_icons = {"TESTED": "✅", "EXPERIMENTAL": "🧪", "DEPRECATED": "❌"}
    icon = status_icons.get(entry.status, "❓")

    print(f"\n{icon} [{entry.id}] {entry.content[:60]}{'...' if len(entry.content) > 60 else ''}")
    print(f"   Type: {entry.type} | Status: {entry.status}")
    print(f"   Added: {entry.date_added} | Updated: {entry.date_updated}")

    if verbose:
        if entry.context:
            print(f"   Context: {entry.context}")
        if entry.tags:
            print(f"   Tags: {', '.join(entry.tags)}")


def cmd_add(args: List[str]):
    """Add a new entry."""
    if len(args) < 2:
        print("Usage: python brain.py add <type> <content> [--context <ctx>] [--status <status>] [--tags <t1,t2>]")
        print(f"Types: {', '.join(ENTRY_TYPES.keys())}")
        return

    entry_type = args[0]
    content = args[1]
    context = ""
    status = "TESTED"
    tags = []

    # Parse optional arguments
    i = 2
    while i < len(args):
        if args[i] == "--context" and i + 1 < len(args):
            context = args[i + 1]
            i += 2
        elif args[i] == "--status" and i + 1 < len(args):
            status = args[i + 1].upper()
            i += 2
        elif args[i] == "--tags" and i + 1 < len(args):
            tags = [t.strip() for t in args[i + 1].split(",")]
            i += 2
        else:
            i += 1

    brain = BrainManager()
    try:
        entry = brain.add(entry_type, content, context, status, tags)
        print(f"✅ Added entry: {entry.id}")
        print_entry(entry, verbose=True)
    except ValueError as e:
        print(f"❌ Error: {e}")


def cmd_update(args: List[str]):
    """Update an existing entry."""
    if len(args) < 2:
        print("Usage: python brain.py update <id> [--content <text>] [--context <ctx>] [--status <status>]")
        return

    entry_id = args[0]
    content = None
    context = None
    status = None

    # Parse optional arguments
    i = 1
    while i < len(args):
        if args[i] == "--content" and i + 1 < len(args):
            content = args[i + 1]
            i += 2
        elif args[i] == "--context" and i + 1 < len(args):
            context = args[i + 1]
            i += 2
        elif args[i] == "--status" and i + 1 < len(args):
            status = args[i + 1].upper()
            i += 2
        else:
            # Treat as content if no flag
            content = args[i]
            i += 1

    brain = BrainManager()
    entry = brain.update(entry_id, content, context, status)

    if entry:
        print(f"✅ Updated entry: {entry.id}")
        print_entry(entry, verbose=True)
    else:
        print(f"❌ Entry not found: {entry_id}")


def cmd_deprecate(args: List[str]):
    """Mark an entry as deprecated."""
    if not args:
        print("Usage: python brain.py deprecate <id>")
        return

    brain = BrainManager()
    entry = brain.deprecate(args[0])

    if entry:
        print(f"✅ Deprecated: {entry.id}")
    else:
        print(f"❌ Entry not found: {args[0]}")


def cmd_search(args: List[str]):
    """Search the brain."""
    if not args:
        print("Usage: python brain.py search <query>")
        return

    query = " ".join(args)
    brain = BrainManager()
    results = brain.search(query)

    if not results:
        print(f"❌ No entries found matching '{query}'")
        return

    print(f"\n🔍 Found {len(results)} entries matching '{query}':")
    for entry in results[:10]:
        print_entry(entry)


def cmd_review(args: List[str]):
    """Show entries needing attention."""
    brain = BrainManager()

    experimental = brain.get_experimental()
    deprecated = brain.get_deprecated()

    print("\n📋 Brain Review")
    print("=" * 50)

    if experimental:
        print(f"\n🧪 Experimental Entries ({len(experimental)}):")
        print("   These need validation or promotion to TESTED")
        for entry in experimental:
            print_entry(entry)

    if deprecated:
        print(f"\n❌ Deprecated Entries ({len(deprecated)}):")
        print("   Run 'python brain.py cleanup' to remove these")
        for entry in deprecated:
            print_entry(entry)

    if not experimental and not deprecated:
        print("\n✅ All entries are in good standing!")


def cmd_cleanup(args: List[str]):
    """Remove deprecated entries."""
    brain = BrainManager()
    deprecated = brain.get_deprecated()

    if not deprecated:
        print("✅ No deprecated entries to clean up")
        return

    print(f"Found {len(deprecated)} deprecated entries:")
    for entry in deprecated:
        print(f"   - {entry.id}: {entry.content[:50]}...")

    response = input("\nRemove these entries? [y/N]: ").strip().lower()
    if response == "y":
        count = brain.cleanup()
        print(f"✅ Removed {count} deprecated entries")
    else:
        print("Cancelled")


def cmd_stats(args: List[str]):
    """Show brain statistics."""
    brain = BrainManager()
    stats = brain.get_stats()

    print("\n🧠 Brain Statistics")
    print("=" * 50)
    print(f"\nTotal Entries: {stats['total_entries']}")

    print("\nBy Type:")
    for type_name, count in sorted(stats["by_type"].items()):
        print(f"   {type_name}: {count}")

    print("\nBy Status:")
    for status, count in sorted(stats["by_status"].items()):
        icon = {"TESTED": "✅", "EXPERIMENTAL": "🧪", "DEPRECATED": "❌"}.get(status, "❓")
        print(f"   {icon} {status}: {count}")

    if stats["oldest"]:
        print(f"\nOldest entry: {stats['oldest']}")
        print(f"Newest entry: {stats['newest']}")


def cmd_export(args: List[str]):
    """Export brain to JSON."""
    brain = BrainManager()
    brain.save()
    print(f"✅ Exported to: {BRAIN_JSON}")


def cmd_list(args: List[str]):
    """List all entries or by type."""
    brain = BrainManager()

    if args and args[0] in ENTRY_TYPES:
        entries = brain.get_by_type(args[0])
        print(f"\n📋 {ENTRY_TYPES[args[0]]} ({len(entries)} entries)")
    else:
        entries = list(brain.entries.values())
        print(f"\n📋 All Entries ({len(entries)} total)")

    print("=" * 50)

    for entry in sorted(entries, key=lambda e: e.date_added, reverse=True):
        print_entry(entry)


def cmd_remember(args: List[str]):
    """Quick add - for use from conversation context."""
    if not args:
        print("Usage: python brain.py remember <what you learned>")
        return

    content = " ".join(args)
    brain = BrainManager()
    entry = brain.add("lesson", content, status="EXPERIMENTAL")
    print(f"🧠 Remembered: {entry.id}")
    print("   Status: EXPERIMENTAL (validate and update to TESTED when confirmed)")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    command = sys.argv[1].lower()
    args = sys.argv[2:]

    commands = {
        "add": cmd_add,
        "update": cmd_update,
        "deprecate": cmd_deprecate,
        "delete": lambda a: print("Use 'deprecate' then 'cleanup' for safety"),
        "search": cmd_search,
        "review": cmd_review,
        "cleanup": cmd_cleanup,
        "stats": cmd_stats,
        "export": cmd_export,
        "list": cmd_list,
        "remember": cmd_remember,
        "help": lambda a: print(__doc__),
    }

    if command in commands:
        commands[command](args)
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
