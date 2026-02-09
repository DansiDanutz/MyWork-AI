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
    python brain.py analytics              # Comprehensive analytics dashboard
    python brain.py export [markdown|json|csv] # Export to markdown, JSON, or CSV
    python brain.py import <file>           # Import from JSON/markdown/CSV
    python brain.py backup                  # Create timestamped backup
    python brain.py restore <backup>        # Restore from backup

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
from dataclasses import dataclass, asdict, field, fields

# Configuration - Import from shared config with fallback
try:
    from config import get_mywork_root
except ImportError:  # pragma: no cover - fallback for standalone usage

    def get_mywork_root() -> Path:
        if env_root := os.environ.get("MYWORK_ROOT"):
            return Path(env_root)
        script_dir = Path(__file__).resolve().parent
        return script_dir.parent if script_dir.name == "tools" else Path.home() / "MyWork"


def _resolve_brain_paths(root: Optional[Path] = None) -> tuple[Path, Path, Path]:
    resolved_root = (root or get_mywork_root()).resolve()
    brain_file = resolved_root / ".planning" / "BRAIN.md"
    brain_json = resolved_root / ".planning" / "brain_data.json"
    return resolved_root, brain_file, brain_json


# Backwards-compatible defaults (do not rely on these for dynamic roots)
MYWORK_ROOT, BRAIN_FILE, BRAIN_JSON = _resolve_brain_paths()

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
    references: int = 0

    def __post_init__(self):
        if not self.date_added:
            self.date_added = datetime.now().strftime("%Y-%m-%d")
        if not self.date_updated:
            self.date_updated = self.date_added

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "BrainEntry":
        allowed = {field.name for field in fields(cls)}
        filtered = {key: value for key, value in data.items() if key in allowed}
        return cls(**filtered)


class BrainManager:
    """Manages the brain knowledge base."""

    def __init__(self, root: Optional[Path] = None):
        self.root, self.brain_file, self.brain_json = _resolve_brain_paths(root)
        self.entries: Dict[str, BrainEntry] = {}
        self.load()

    def load(self):
        """Load entries from JSON backup if exists."""
        if self.brain_json.exists():
            try:
                with open(self.brain_json) as f:
                    data = json.load(f)
                    for entry_data in data.get("entries", []):
                        entry = BrainEntry.from_dict(entry_data)
                        self.entries[entry.id] = entry
            except (json.JSONDecodeError, TypeError) as e:
                print(f"Warning: Could not load brain data: {e}")

    def save(self):
        """Save entries to JSON backup."""
        self.brain_json.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "entry_count": len(self.entries),
            "entries": [e.to_dict() for e in self.entries.values()],
        }
        with open(self.brain_json, "w") as f:
            json.dump(data, f, indent=2)

    def generate_id(self, entry_type: str) -> str:
        """Generate a unique ID for an entry."""
        type_entries = [e for e in self.entries.values() if e.type == entry_type]
        next_num = len(type_entries) + 1
        return f"{entry_type}-{next_num:03d}"

    def add(
        self,
        entry_type: str,
        content: str,
        context: str = "",
        status: str = "TESTED",
        tags: List[str] = None,
    ) -> BrainEntry:
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
            tags=tags or [],
        )
        self.entries[entry_id] = entry
        self.save()
        self._update_brain_md()
        return entry

    def update(
        self,
        entry_id: str,
        content: str = None,
        context: str = None,
        status: str = None,
        tags: List[str] = None,
    ) -> Optional[BrainEntry]:
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
        if not self.brain_file.exists():
            return

        content = self.brain_file.read_text()

        # For now, we'll append new entries to the changelog
        # A more sophisticated version would rebuild sections

        # Update the "Last updated" line
        content = re.sub(
            r"> Last updated: \d{4}-\d{2}-\d{2}",
            f'> Last updated: {datetime.now().strftime("%Y-%m-%d")}',
            content,
        )

        self.brain_file.write_text(content)


def print_entry(entry: BrainEntry, verbose: bool = False):
    """Print a formatted entry with improved styling."""
    status_icons = {"TESTED": "✅", "EXPERIMENTAL": "🧪", "DEPRECATED": "❌"}
    icon = status_icons.get(entry.status, "❓")
    
    # Color codes
    BOLD = '\033[1m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    
    # Create a nice box for each entry
    content_preview = entry.content[:80] + '...' if len(entry.content) > 80 else entry.content
    
    print(f"\n{CYAN}╭─ {icon} {BOLD}{entry.type.upper()}{RESET}{CYAN} [{entry.id}]{'─' * max(0, 60 - len(entry.id) - len(entry.type))}╮{RESET}")
    
    # Split content into multiple lines if needed
    words = content_preview.split()
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 <= 60:
            current_line.append(word)
            current_length += len(word) + 1
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word)
    
    if current_line:
        lines.append(' '.join(current_line))
    
    for line in lines:
        print(f"{CYAN}│ {RESET}{line:<60}{CYAN} │{RESET}")
    
    # Metadata line
    metadata = f"📅 {entry.date_added.split()[0]} • 🏷️ {entry.status}"
    print(f"{CYAN}├─{YELLOW} {metadata:<58} {CYAN}─┤{RESET}")
    
    if verbose:
        if entry.context:
            context_words = entry.context.split()
            context_lines = []
            current_line = []
            current_length = 0
            
            for word in context_words:
                if current_length + len(word) + 1 <= 58:
                    current_line.append(word)
                    current_length += len(word) + 1
                else:
                    context_lines.append(' '.join(current_line))
                    current_line = [word]
                    current_length = len(word)
            
            if current_line:
                context_lines.append(' '.join(current_line))
            
            print(f"{CYAN}├─ {BLUE}📝 Context:{RESET}{' ' * 47}{CYAN}─┤{RESET}")
            for line in context_lines:
                print(f"{CYAN}│ {RESET}{line:<60}{CYAN} │{RESET}")
        
        if entry.tags:
            tags_str = ', '.join(entry.tags)
            print(f"{CYAN}├─ {GREEN}🏷️  Tags: {tags_str:<51}{CYAN}─┤{RESET}")
    
    print(f"{CYAN}╰{'─' * 62}╯{RESET}")


def cmd_add(args: List[str]):
    """Add a new entry."""
    if len(args) < 2:
        print(
            "Usage: python brain.py add <type> <content> [--context <ctx>] [--status <status>] [--tags <t1,t2>]"
        )
        print(f"Types: {', '.join(ENTRY_TYPES.keys())}")
        return

    entry_type = args[0]
    content = args[1]
    
    # Validate entry type
    if entry_type not in ENTRY_TYPES:
        print(f"❌ Invalid entry type: '{entry_type}'")
        print(f"   Valid types: {', '.join(ENTRY_TYPES.keys())}")
        sys.exit(1)
    
    # Validate content is not empty
    if not content or content.strip() == "":
        print("❌ Content cannot be empty")
        print("   Usage: python brain.py add <type> <content>")
        print("   Example: python brain.py add lesson 'Always test before deploying'")
        sys.exit(1)
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
        print(
            "Usage: python brain.py update <id> [--content <text>] [--context <ctx>] [--status <status>]"
        )
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
    """Search the brain with improved formatting."""
    if not args:
        print("Usage: python brain.py search <query>")
        return

    query = " ".join(args)
    brain = BrainManager()
    results = brain.search(query)

    # Color codes
    BOLD = '\033[1m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    RESET = '\033[0m'

    if not results:
        print(f"\n{RED}❌ No entries found matching '{YELLOW}{query}{RESET}{RED}'{RESET}")
        print(f"{CYAN}💡 Try searching for broader terms or check `brain stats` for available categories.{RESET}")
        return

    # Search results header
    print(f"\n{BOLD}{CYAN}{'═' * 70}{RESET}")
    print(f"{BOLD}{CYAN}🔍 BRAIN SEARCH RESULTS{RESET}")
    print(f"{BOLD}{CYAN}{'═' * 70}{RESET}")
    print(f"{GREEN}Query:{RESET} '{YELLOW}{query}{RESET}' • {GREEN}Found:{RESET} {BOLD}{len(results)}{RESET} entries")
    
    # Group results by type for better organization
    by_type = {}
    for entry in results:
        if entry.type not in by_type:
            by_type[entry.type] = []
        by_type[entry.type].append(entry)
    
    # Show summary by type
    print(f"\n{CYAN}📊 Results by type:{RESET}")
    for entry_type, entries in sorted(by_type.items()):
        print(f"  • {entry_type}: {len(entries)} matches")
    
    print(f"\n{BOLD}{CYAN}{'─' * 70}{RESET}")
    
    # Show top results (limit to 10 for readability)
    shown_results = results[:10]
    for i, entry in enumerate(shown_results, 1):
        print(f"\n{BOLD}{YELLOW}[{i}/{len(results)}]{RESET}")
        print_entry(entry, verbose=True)
    
    # Show pagination info if there are more results
    if len(results) > 10:
        print(f"\n{CYAN}📄 Showing first 10 of {len(results)} results. Use more specific terms to narrow down.{RESET}")
    
    print(f"\n{BOLD}{CYAN}{'═' * 70}{RESET}")
    print(f"{CYAN}💡 Use 'brain review' to see experimental entries or 'brain stats' for overview.{RESET}")


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


def cmd_analytics(args: List[str]):
    """Show comprehensive brain analytics."""
    brain = BrainManager()
    
    # Color codes
    BOLD = '\033[1m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    RED = '\033[91m'
    RESET = '\033[0m'
    
    print(f"\n{BOLD}{CYAN}{'═' * 80}{RESET}")
    print(f"{BOLD}{CYAN}📊 BRAIN ANALYTICS DASHBOARD{RESET}")
    print(f"{BOLD}{CYAN}{'═' * 80}{RESET}")
    
    entries = list(brain.entries.values())
    if not entries:
        print(f"{RED}❌ No entries found in brain{RESET}")
        return
    
    # 1. Knowledge Growth Over Time
    print(f"\n{BOLD}{GREEN}📈 Knowledge Growth Analysis{RESET}")
    print(f"{CYAN}{'─' * 50}{RESET}")
    
    # Group entries by week/month
    from collections import defaultdict
    import calendar
    
    weekly_counts = defaultdict(int)
    monthly_counts = defaultdict(int)
    
    for entry in entries:
        try:
            date_obj = datetime.strptime(entry.date_added, '%Y-%m-%d')
            # Week calculation (ISO week)
            year, week, _ = date_obj.isocalendar()
            week_key = f"{year}-W{week:02d}"
            weekly_counts[week_key] += 1
            
            # Month calculation
            month_key = f"{year}-{date_obj.month:02d}"
            monthly_counts[month_key] += 1
        except ValueError:
            continue
    
    # Show recent weeks
    sorted_weeks = sorted(weekly_counts.items())[-8:]  # Last 8 weeks
    print(f"{BLUE}Recent Weekly Growth:{RESET}")
    for week, count in sorted_weeks:
        bar = '█' * count + '░' * max(0, 10 - count)
        print(f"  {week}: {bar} ({count} entries)")
    
    # Show monthly trend
    sorted_months = sorted(monthly_counts.items())[-6:]  # Last 6 months
    print(f"\n{BLUE}Monthly Trend:{RESET}")
    for month, count in sorted_months:
        try:
            year_str, month_str = month.split('-')
            month_name = calendar.month_abbr[int(month_str)]
            bar = '█' * min(count, 20) + '░' * max(0, 20 - count)
            print(f"  {year_str}-{month_name}: {bar} ({count} entries)")
        except:
            print(f"  {month}: {count} entries")
    
    # 2. Most Referenced/Active Entries
    print(f"\n{BOLD}{GREEN}🔗 Most Referenced Knowledge{RESET}")
    print(f"{CYAN}{'─' * 50}{RESET}")
    
    # Since we don't have actual reference tracking yet, we'll rank by:
    # - Recency (newer = more likely to be referenced)
    # - Type popularity  
    # - Tag count (more tags = more discoverable)
    
    scored_entries = []
    for entry in entries:
        score = 0
        
        # Recency score (0-10)
        try:
            days_old = (datetime.now() - datetime.strptime(entry.date_added, '%Y-%m-%d')).days
            recency_score = max(0, 10 - (days_old / 30))  # Decay over months
            score += recency_score
        except:
            pass
        
        # Tag score (more tags = more discoverable)
        score += len(entry.tags) * 2
        
        # Type bonus (patterns and insights are typically more referenced)
        type_bonus = {'pattern': 5, 'insight': 4, 'lesson': 3, 'tip': 2, 'experiment': 1, 'antipattern': 2}
        score += type_bonus.get(entry.type, 0)
        
        # Status bonus
        status_bonus = {'TESTED': 3, 'EXPERIMENTAL': 1, 'DEPRECATED': -5}
        score += status_bonus.get(entry.status, 0)
        
        scored_entries.append((score, entry))
    
    # Show top 5 most likely to be referenced
    top_entries = sorted(scored_entries, key=lambda x: x[0], reverse=True)[:5]
    for i, (score, entry) in enumerate(top_entries, 1):
        status_icon = {"TESTED": "✅", "EXPERIMENTAL": "🧪", "DEPRECATED": "❌"}.get(entry.status, "❓")
        content_preview = entry.content[:50] + '...' if len(entry.content) > 50 else entry.content
        print(f"  {YELLOW}{i}.{RESET} {status_icon} {BLUE}{entry.id}{RESET} - {content_preview}")
        print(f"      📊 Score: {score:.1f} | 📅 {entry.date_added} | 🏷️ {len(entry.tags)} tags")
    
    # 3. Tag Cloud / Most Common Tags
    print(f"\n{BOLD}{GREEN}🏷️  Tag Cloud Analysis{RESET}")
    print(f"{CYAN}{'─' * 50}{RESET}")
    
    all_tags = []
    for entry in entries:
        all_tags.extend([tag.lower() for tag in entry.tags])
    
    if all_tags:
        from collections import Counter
        tag_counts = Counter(all_tags)
        top_tags = tag_counts.most_common(15)
        
        print(f"{BLUE}Most Popular Tags:{RESET}")
        for i, (tag, count) in enumerate(top_tags):
            # Visual size based on frequency
            if count >= 3:
                size = "████"
            elif count == 2:
                size = "███░"
            else:
                size = "██░░"
            
            print(f"  {size} {YELLOW}{tag}{RESET} ({count})")
    else:
        print(f"{BLUE}No tags found - consider adding tags to entries for better organization{RESET}")
    
    # 4. Knowledge Gaps Analysis
    print(f"\n{BOLD}{GREEN}🕳️  Knowledge Gap Analysis{RESET}")
    print(f"{CYAN}{'─' * 50}{RESET}")
    
    type_counts = defaultdict(int)
    for entry in entries:
        type_counts[entry.type] += 1
    
    print(f"{BLUE}Entry Type Distribution:{RESET}")
    total_entries = len(entries)
    gap_threshold = max(1, total_entries // 10)  # Consider <10% as a gap
    
    gaps_found = []
    for entry_type, display_name in ENTRY_TYPES.items():
        count = type_counts[entry_type]
        percentage = (count / total_entries * 100) if total_entries > 0 else 0
        
        # Visual bar
        bar_length = min(20, count)
        bar = '█' * bar_length + '░' * max(0, 20 - bar_length)
        
        status = ""
        if count == 0:
            status = f" {RED}[EMPTY!]{RESET}"
            gaps_found.append(f"No {entry_type} entries")
        elif count < gap_threshold:
            status = f" {YELLOW}[LOW]{RESET}"
            gaps_found.append(f"Only {count} {entry_type} entries")
        
        print(f"  {bar} {BLUE}{entry_type}{RESET}: {count} ({percentage:.1f}%){status}")
    
    if gaps_found:
        print(f"\n{YELLOW}💡 Suggestions to fill gaps:{RESET}")
        for gap in gaps_found[:3]:  # Show top 3 gaps
            print(f"  • {gap}")
    
    # 5. Staleness Report
    print(f"\n{BOLD}{GREEN}⏰ Staleness Report{RESET}")
    print(f"{CYAN}{'─' * 50}{RESET}")
    
    now = datetime.now()
    stale_entries = []
    recent_entries = []
    
    for entry in entries:
        try:
            last_updated = datetime.strptime(entry.date_updated, '%Y-%m-%d')
            days_old = (now - last_updated).days
            
            if days_old >= 30:
                stale_entries.append((days_old, entry))
            elif days_old <= 7:
                recent_entries.append((days_old, entry))
        except:
            continue
    
    stale_entries.sort(key=lambda x: x[0], reverse=True)  # Oldest first (by days_old)
    recent_entries.sort(key=lambda x: x[0])  # Newest first (by days_old)
    
    if stale_entries:
        print(f"{YELLOW}🕒 Stale Entries (30+ days old):{RESET}")
        for days_old, entry in stale_entries[:5]:  # Show 5 oldest
            content_preview = entry.content[:40] + '...' if len(entry.content) > 40 else entry.content
            months_old = days_old // 30
            print(f"  {RED}•{RESET} {BLUE}{entry.id}{RESET} - {content_preview}")
            print(f"    📅 Last updated {days_old} days ago ({months_old} months)")
    
    if recent_entries:
        print(f"\n{GREEN}🆕 Recently Updated:{RESET}")
        for days_old, entry in recent_entries[:3]:
            content_preview = entry.content[:40] + '...' if len(entry.content) > 40 else entry.content
            time_text = "today" if days_old == 0 else f"{days_old} days ago"
            print(f"  {GREEN}•{RESET} {BLUE}{entry.id}{RESET} - {content_preview} ({time_text})")
    
    # 6. Entry Quality Scores
    print(f"\n{BOLD}{GREEN}⭐ Entry Quality Analysis{RESET}")
    print(f"{CYAN}{'─' * 50}{RESET}")
    
    quality_scores = []
    for entry in entries:
        score = 0
        
        # Content length (good detail)
        if len(entry.content) >= 50:
            score += 2
        elif len(entry.content) >= 20:
            score += 1
        
        # Has context
        if entry.context and len(entry.context) > 10:
            score += 2
        
        # Has tags
        score += min(len(entry.tags), 3)  # Max 3 points for tags
        
        # Status bonus
        if entry.status == 'TESTED':
            score += 2
        elif entry.status == 'EXPERIMENTAL':
            score += 1
        
        # Recent updates (shows maintenance)
        try:
            days_since_update = (now - datetime.strptime(entry.date_updated, '%Y-%m-%d')).days
            if days_since_update <= 30:
                score += 1
        except:
            pass
        
        quality_scores.append((score, entry))
    
    # Show distribution
    quality_ranges = {'High (7+)': 0, 'Medium (4-6)': 0, 'Low (0-3)': 0}
    for score, _ in quality_scores:
        if score >= 7:
            quality_ranges['High (7+)'] += 1
        elif score >= 4:
            quality_ranges['Medium (4-6)'] += 1
        else:
            quality_ranges['Low (0-3)'] += 1
    
    print(f"{BLUE}Quality Distribution:{RESET}")
    for range_name, count in quality_ranges.items():
        percentage = (count / total_entries * 100) if total_entries > 0 else 0
        bar = '█' * min(15, count) + '░' * max(0, 15 - count)
        print(f"  {bar} {range_name}: {count} ({percentage:.1f}%)")
    
    # Show highest quality entries
    top_quality = sorted(quality_scores, key=lambda x: x[0], reverse=True)[:3]
    if top_quality:
        print(f"\n{YELLOW}🏆 Highest Quality Entries:{RESET}")
        for score, entry in top_quality:
            content_preview = entry.content[:40] + '...' if len(entry.content) > 40 else entry.content
            print(f"  ⭐ {BLUE}{entry.id}{RESET} (score: {score}) - {content_preview}")
    
    # Summary and Recommendations
    print(f"\n{BOLD}{GREEN}📋 Summary & Recommendations{RESET}")
    print(f"{CYAN}{'─' * 50}{RESET}")
    
    recommendations = []
    
    if len(stale_entries) > 5:
        recommendations.append("Review and update old entries")
    if len([e for e in entries if not e.tags]) > len(entries) // 2:
        recommendations.append("Add more tags for better discoverability")
    if type_counts.get('pattern', 0) < 3:
        recommendations.append("Document more patterns from your work")
    if len(entries) < 20:
        recommendations.append("Continue growing your knowledge base")
    
    if recommendations:
        print(f"{YELLOW}💡 Action Items:{RESET}")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
    else:
        print(f"{GREEN}✅ Your brain is in excellent shape!{RESET}")
    
    print(f"\n{BOLD}{CYAN}{'═' * 80}{RESET}")
    print(f"{CYAN}📊 Use 'brain search' for semantic queries • 'brain review' for maintenance{RESET}")
    print(f"{BOLD}{CYAN}{'═' * 80}{RESET}")


def cmd_export(args: List[str]):
    """Export brain to markdown, JSON, or CSV."""
    format_type = args[0] if args else "markdown"
    
    if format_type not in ["markdown", "json", "csv"]:
        print("Usage: python brain.py export [markdown|json|csv]")
        return
    
    brain = BrainManager()
    
    if format_type == "json":
        brain.save()
        print(f"✅ JSON exported to: {brain.brain_json}")
        return
    
    mywork_root = get_mywork_root()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if format_type == "csv":
        import csv
        
        export_file = mywork_root / f"BRAIN_EXPORT_{timestamp}.csv"
        
        with open(export_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow(['id', 'type', 'content', 'context', 'status', 'date_added', 
                           'date_updated', 'tags', 'references'])
            
            # Data rows
            for entry in brain.entries.values():
                writer.writerow([
                    entry.id,
                    entry.type,
                    entry.content,
                    entry.context,
                    entry.status,
                    entry.date_added,
                    entry.date_updated,
                    ', '.join(entry.tags),
                    entry.references
                ])
        
        print(f"✅ CSV exported to: {export_file}")
        print(f"📊 Exported {len(brain.entries)} entries")
        return
    
    # Markdown export
    export_file = mywork_root / f"BRAIN_EXPORT_{timestamp}.md"
    
    entries = list(brain.entries.values())
    
    # Group entries by type
    by_type = {}
    for entry in entries:
        if entry.type not in by_type:
            by_type[entry.type] = []
        by_type[entry.type].append(entry)
    
    with open(export_file, 'w') as f:
        f.write("# MyWork-AI Brain Export\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Summary stats
        stats = brain.get_stats()
        f.write("## Summary\n\n")
        f.write(f"- **Total Entries:** {stats['total_entries']}\n")
        f.write(f"- **Types:** {', '.join(stats['by_type'].keys())}\n")
        f.write(f"- **Status Distribution:** ")
        status_summary = [f"{status}: {count}" for status, count in stats['by_status'].items()]
        f.write(", ".join(status_summary) + "\n\n")
        
        # Table of contents
        f.write("## Table of Contents\n\n")
        for entry_type in sorted(by_type.keys()):
            count = len(by_type[entry_type])
            f.write(f"- [{entry_type.title()}](#user-content-{entry_type.lower()}) ({count} entries)\n")
        f.write("\n")
        
        # Export each type
        for entry_type in sorted(by_type.keys()):
            entries_of_type = sorted(by_type[entry_type], key=lambda x: x.date_added, reverse=True)
            
            f.write(f"## {entry_type.title()}\n\n")
            
            for entry in entries_of_type:
                status_emoji = {"TESTED": "✅", "EXPERIMENTAL": "🧪", "DEPRECATED": "❌"}.get(entry.status, "❓")
                
                f.write(f"### {status_emoji} {entry.id}\n\n")
                f.write(f"**Content:** {entry.content}\n\n")
                
                if entry.context:
                    f.write(f"**Context:** {entry.context}\n\n")
                
                metadata = []
                metadata.append(f"**Added:** {entry.date_added}")
                metadata.append(f"**Updated:** {entry.date_updated}")
                metadata.append(f"**Status:** {entry.status}")
                
                if entry.tags:
                    metadata.append(f"**Tags:** {', '.join(entry.tags)}")
                
                f.write(" | ".join(metadata) + "\n\n")
                f.write("---\n\n")
    
    print(f"✅ Markdown exported to: {export_file}")
    print(f"📊 Exported {stats['total_entries']} entries across {len(by_type)} types")


def cmd_import(args: List[str]):
    """Import brain entries from JSON, CSV, or Markdown."""
    if not args:
        print("Usage: python brain.py import <file_path>")
        return
    
    file_path = Path(args[0])
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return
    
    brain = BrainManager()
    
    # Color codes
    BOLD = '\033[1m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    
    print(f"{BLUE}📥 Importing from: {file_path}{RESET}")
    
    imported_count = 0
    skipped_count = 0
    error_count = 0
    
    try:
        if file_path.suffix.lower() == '.json':
            # Import from JSON
            with open(file_path) as f:
                data = json.load(f)
            
            # Handle different JSON formats
            entries_data = data.get('entries', [])
            if not entries_data and isinstance(data, list):
                entries_data = data  # Direct array format
            
            for entry_data in entries_data:
                try:
                    # Check if entry already exists
                    entry_id = entry_data.get('id')
                    if entry_id and entry_id in brain.entries:
                        print(f"{YELLOW}⚠️  Skipping existing entry: {entry_id}{RESET}")
                        skipped_count += 1
                        continue
                    
                    # Create new entry
                    entry = BrainEntry.from_dict(entry_data)
                    
                    # Generate new ID if missing or conflicting
                    if not entry.id or entry.id in brain.entries:
                        entry.id = brain.generate_id(entry.type)
                    
                    brain.entries[entry.id] = entry
                    imported_count += 1
                    print(f"{GREEN}✅ Imported: {entry.id} - {entry.content[:50]}...{RESET}")
                    
                except Exception as e:
                    error_count += 1
                    print(f"{RED}❌ Error importing entry: {e}{RESET}")
        
        elif file_path.suffix.lower() == '.csv':
            # Import from CSV
            import csv
            
            with open(file_path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    try:
                        # Check if entry already exists
                        entry_id = row.get('id')
                        if entry_id and entry_id in brain.entries:
                            print(f"{YELLOW}⚠️  Skipping existing entry: {entry_id}{RESET}")
                            skipped_count += 1
                            continue
                        
                        # Parse tags
                        tags = []
                        if row.get('tags'):
                            tags = [tag.strip() for tag in row['tags'].split(',') if tag.strip()]
                        
                        # Create entry
                        entry = BrainEntry(
                            id=entry_id or brain.generate_id(row.get('type', 'lesson')),
                            type=row.get('type', 'lesson'),
                            content=row.get('content', ''),
                            context=row.get('context', ''),
                            status=row.get('status', 'TESTED'),
                            date_added=row.get('date_added', datetime.now().strftime('%Y-%m-%d')),
                            date_updated=row.get('date_updated', datetime.now().strftime('%Y-%m-%d')),
                            tags=tags,
                            references=int(row.get('references', 0))
                        )
                        
                        brain.entries[entry.id] = entry
                        imported_count += 1
                        print(f"{GREEN}✅ Imported: {entry.id} - {entry.content[:50]}...{RESET}")
                        
                    except Exception as e:
                        error_count += 1
                        print(f"{RED}❌ Error importing row: {e}{RESET}")
        
        elif file_path.suffix.lower() in ['.md', '.markdown']:
            # Import from Markdown (basic parsing)
            with open(file_path) as f:
                content = f.read()
            
            # Parse markdown entries (look for patterns like "### ✅ lesson-001")
            import re
            
            # Pattern to match entry headers
            entry_pattern = r'###\s*([✅🧪❌❓])\s*(\w+-\d+)'
            content_pattern = r'\*\*Content:\*\*\s*([^\n]+)'
            context_pattern = r'\*\*Context:\*\*\s*([^\n]+)'
            status_pattern = r'\*\*Status:\*\*\s*([^\n|]+)'
            tags_pattern = r'\*\*Tags:\*\*\s*([^\n|]+)'
            
            matches = list(re.finditer(entry_pattern, content))
            
            for i, match in enumerate(matches):
                try:
                    status_icon = match.group(1)
                    entry_id = match.group(2)
                    
                    # Extract entry type from ID
                    entry_type = entry_id.split('-')[0]
                    
                    # Get content between this match and next match
                    start_pos = match.end()
                    end_pos = matches[i+1].start() if i+1 < len(matches) else len(content)
                    section_content = content[start_pos:end_pos]
                    
                    # Extract fields
                    content_match = re.search(content_pattern, section_content)
                    context_match = re.search(context_pattern, section_content)
                    status_match = re.search(status_pattern, section_content)
                    tags_match = re.search(tags_pattern, section_content)
                    
                    # Determine status from icon
                    status_map = {"✅": "TESTED", "🧪": "EXPERIMENTAL", "❌": "DEPRECATED", "❓": "TESTED"}
                    status = status_map.get(status_icon, "TESTED")
                    if status_match:
                        status = status_match.group(1).strip()
                    
                    # Check if entry already exists
                    if entry_id in brain.entries:
                        print(f"{YELLOW}⚠️  Skipping existing entry: {entry_id}{RESET}")
                        skipped_count += 1
                        continue
                    
                    # Parse tags
                    tags = []
                    if tags_match:
                        tags = [tag.strip() for tag in tags_match.group(1).split(',') if tag.strip()]
                    
                    # Create entry
                    entry = BrainEntry(
                        id=entry_id,
                        type=entry_type,
                        content=content_match.group(1).strip() if content_match else "",
                        context=context_match.group(1).strip() if context_match else "",
                        status=status,
                        tags=tags
                    )
                    
                    brain.entries[entry.id] = entry
                    imported_count += 1
                    print(f"{GREEN}✅ Imported: {entry.id} - {entry.content[:50]}...{RESET}")
                    
                except Exception as e:
                    error_count += 1
                    print(f"{RED}❌ Error parsing entry: {e}{RESET}")
        
        else:
            print(f"{RED}❌ Unsupported file format: {file_path.suffix}{RESET}")
            return
        
        # Save changes
        if imported_count > 0:
            brain.save()
            brain._update_brain_md()
        
        # Summary
        print(f"\n{BOLD}📊 Import Summary:{RESET}")
        print(f"  {GREEN}✅ Imported: {imported_count}{RESET}")
        print(f"  {YELLOW}⚠️  Skipped: {skipped_count}{RESET}")
        print(f"  {RED}❌ Errors: {error_count}{RESET}")
        
        if imported_count > 0:
            print(f"\n{GREEN}🧠 Brain updated successfully!{RESET}")
    
    except Exception as e:
        print(f"{RED}❌ Import failed: {e}{RESET}")


def cmd_backup(args: List[str]):
    """Create a timestamped backup of the brain."""
    brain = BrainManager()
    
    # Create backup directory
    mywork_root = get_mywork_root()
    backup_dir = mywork_root / "backups" / "brain"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = backup_dir / f"brain_backup_{timestamp}.json"
    
    # Create backup with metadata
    backup_data = {
        "backup_info": {
            "created_at": datetime.now().isoformat(),
            "source": str(brain.brain_json),
            "entry_count": len(brain.entries),
            "brain_version": "1.0"
        },
        "brain_data": {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "entry_count": len(brain.entries),
            "entries": [e.to_dict() for e in brain.entries.values()]
        }
    }
    
    with open(backup_file, 'w') as f:
        json.dump(backup_data, f, indent=2)
    
    print(f"✅ Brain backup created: {backup_file}")
    print(f"📊 Backed up {len(brain.entries)} entries")
    
    # Also backup the original brain_data.json if it exists
    if brain.brain_json.exists():
        backup_original = backup_dir / f"brain_data_{timestamp}.json"
        import shutil
        shutil.copy2(brain.brain_json, backup_original)
        print(f"📁 Original data file backed up: {backup_original}")


def cmd_restore(args: List[str]):
    """Restore brain from a backup file."""
    if not args:
        # List available backups
        mywork_root = get_mywork_root()
        backup_dir = mywork_root / "backups" / "brain"
        
        if not backup_dir.exists():
            print("❌ No backups directory found")
            return
        
        backup_files = list(backup_dir.glob("brain_backup_*.json"))
        if not backup_files:
            print("❌ No backup files found")
            return
        
        print("📁 Available backups:")
        backup_files.sort(reverse=True)  # Latest first
        
        for i, backup_file in enumerate(backup_files[:10], 1):  # Show last 10
            try:
                with open(backup_file) as f:
                    backup_data = json.load(f)
                
                backup_info = backup_data.get("backup_info", {})
                created_at = backup_info.get("created_at", "Unknown")
                entry_count = backup_info.get("entry_count", 0)
                
                # Parse datetime for display
                try:
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    time_str = created_at
                
                print(f"  {i:2}. {backup_file.name}")
                print(f"      📅 {time_str} • 📊 {entry_count} entries")
                
            except Exception as e:
                print(f"  ❌ {backup_file.name} (corrupted: {e})")
        
        print(f"\nUsage: python brain.py restore <backup_filename>")
        return
    
    backup_filename = args[0]
    
    # Find backup file
    mywork_root = get_mywork_root()
    backup_dir = mywork_root / "backups" / "brain"
    backup_file = backup_dir / backup_filename
    
    if not backup_file.exists():
        # Try with full pattern
        pattern_file = backup_dir / f"brain_backup_{backup_filename}.json"
        if pattern_file.exists():
            backup_file = pattern_file
        else:
            print(f"❌ Backup file not found: {backup_filename}")
            return
    
    # Confirm restore
    print(f"⚠️  This will replace your current brain with the backup:")
    print(f"   📁 {backup_file}")
    
    response = input("\nProceed with restore? [y/N]: ").strip().lower()
    if response != 'y':
        print("Restore cancelled")
        return
    
    try:
        # Load backup
        with open(backup_file) as f:
            backup_data = json.load(f)
        
        brain_data = backup_data.get("brain_data", backup_data)  # Handle old format
        
        # Create current backup before restore
        brain = BrainManager()
        current_backup_file = backup_dir / f"brain_backup_before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        current_backup = {
            "backup_info": {
                "created_at": datetime.now().isoformat(),
                "source": "pre_restore_backup",
                "entry_count": len(brain.entries),
                "brain_version": "1.0"
            },
            "brain_data": {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "entry_count": len(brain.entries),
                "entries": [e.to_dict() for e in brain.entries.values()]
            }
        }
        
        with open(current_backup_file, 'w') as f:
            json.dump(current_backup, f, indent=2)
        
        print(f"💾 Current brain backed up to: {current_backup_file}")
        
        # Restore from backup
        with open(brain.brain_json, 'w') as f:
            json.dump(brain_data, f, indent=2)
        
        # Reload brain
        brain.load()
        
        print(f"✅ Brain restored successfully!")
        print(f"📊 Restored {len(brain.entries)} entries")
        
        # Update BRAIN.md
        brain._update_brain_md()
        
    except Exception as e:
        print(f"❌ Restore failed: {e}")


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
        "analytics": cmd_analytics,
        "export": cmd_export,
        "import": cmd_import,
        "backup": cmd_backup,
        "restore": cmd_restore,
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
