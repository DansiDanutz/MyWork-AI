#!/usr/bin/env python3
"""
Brain Learner - Automatic Knowledge Discovery
==============================================
Discovers learnings from work patterns and automatically updates the brain.

This script should be run:
- After completing GSD phases
- After fixing errors
- During weekly maintenance
- After any significant work session

Usage:
    python brain_learner.py discover           # Discover new learnings from recent work
    python brain_learner.py analyze-errors     # Learn from error patterns
    python brain_learner.py analyze-modules    # Learn from module registry patterns
    python brain_learner.py promote            # Promote validated EXPERIMENTAL entries
    python brain_learner.py cleanup-smart      # Intelligent cleanup based on usage
    python brain_learner.py daily              # Run daily learning routine
    python brain_learner.py weekly             # Run weekly deep analysis

The brain learns from:
- GSD phase completions (SUMMARY.md, VERIFICATION.md)
- Git commit patterns
- Error logs and their resolutions
- Module registry patterns
- Health check history
- Successful workflows
"""

import os
import sys
import json
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

# Configuration
MYWORK_ROOT = Path("/Users/dansidanutz/Desktop/MyWork")
PROJECTS_DIR = MYWORK_ROOT / "projects"
BRAIN_JSON = MYWORK_ROOT / ".planning" / "brain_data.json"
BRAIN_MD = MYWORK_ROOT / ".planning" / "BRAIN.md"
LEARNING_LOG = MYWORK_ROOT / ".tmp" / "learning_log.json"
ERROR_LOG = MYWORK_ROOT / ".tmp" / "error_patterns.json"

# Import brain manager
sys.path.insert(0, str(MYWORK_ROOT / "tools"))
try:
    from brain import BrainManager, BrainEntry
except ImportError:
    print("Error: Could not import brain module")
    sys.exit(1)


class LearningEngine:
    """Discovers and extracts learnings from work patterns."""

    def __init__(self):
        self.brain = BrainManager()
        self.discoveries: List[Dict[str, Any]] = []
        self.load_learning_log()

    def load_learning_log(self):
        """Load previous learning sessions."""
        if LEARNING_LOG.exists():
            try:
                with open(LEARNING_LOG) as f:
                    self.learning_history = json.load(f)
            except json.JSONDecodeError:
                self.learning_history = {"sessions": [], "discovered": []}
        else:
            self.learning_history = {"sessions": [], "discovered": []}

    def save_learning_log(self):
        """Save learning session."""
        LEARNING_LOG.parent.mkdir(parents=True, exist_ok=True)
        self.learning_history["sessions"].append({
            "timestamp": datetime.now().isoformat(),
            "discoveries": len(self.discoveries)
        })
        with open(LEARNING_LOG, "w") as f:
            json.dump(self.learning_history, f, indent=2)

    def already_learned(self, content: str) -> bool:
        """Check if we already have this learning."""
        content_lower = content.lower()
        for entry in self.brain.entries.values():
            if content_lower in entry.content.lower() or entry.content.lower() in content_lower:
                return True
        # Check discovery history
        for discovered in self.learning_history.get("discovered", []):
            if content_lower in discovered.lower():
                return True
        return False

    def add_discovery(self, entry_type: str, content: str, context: str = "",
                      confidence: str = "EXPERIMENTAL", source: str = "auto"):
        """Add a discovery if not already known."""
        if self.already_learned(content):
            return False

        self.discoveries.append({
            "type": entry_type,
            "content": content,
            "context": context,
            "confidence": confidence,
            "source": source,
            "timestamp": datetime.now().isoformat()
        })

        # Track in history
        self.learning_history.setdefault("discovered", []).append(content)

        return True

    def discover_from_gsd_phases(self) -> int:
        """Discover learnings from completed GSD phases."""
        count = 0

        for project in PROJECTS_DIR.iterdir():
            if not project.is_dir() or project.name.startswith((".", "_")):
                continue

            phases_dir = project / ".planning" / "phases"
            if not phases_dir.exists():
                continue

            for phase_dir in phases_dir.iterdir():
                if not phase_dir.is_dir():
                    continue

                # Check SUMMARY.md for learnings
                summary = phase_dir / "SUMMARY.md"
                if summary.exists():
                    count += self._extract_from_summary(summary, project.name)

                # Check VERIFICATION.md for issues/solutions
                verification = phase_dir / "VERIFICATION.md"
                if verification.exists():
                    count += self._extract_from_verification(verification, project.name)

        return count

    def _extract_from_summary(self, summary_path: Path, project: str) -> int:
        """Extract learnings from phase summary."""
        count = 0
        content = summary_path.read_text()

        # Look for "Lessons Learned" or "What Worked" sections
        lessons_match = re.search(
            r'(?:lessons?\s*learned|what\s*worked|key\s*insights?)[\s:]*\n((?:[-*]\s*.+\n?)+)',
            content,
            re.IGNORECASE
        )

        if lessons_match:
            for line in lessons_match.group(1).split('\n'):
                line = line.strip().lstrip('-*').strip()
                if line and len(line) > 20:
                    if self.add_discovery(
                        "lesson",
                        line,
                        f"From {project} phase summary",
                        "EXPERIMENTAL",
                        f"gsd:{project}"
                    ):
                        count += 1

        # Look for "Issues" or "Blockers" sections
        issues_match = re.search(
            r'(?:issues?|blockers?|problems?)[\s:]*\n((?:[-*]\s*.+\n?)+)',
            content,
            re.IGNORECASE
        )

        if issues_match:
            for line in issues_match.group(1).split('\n'):
                line = line.strip().lstrip('-*').strip()
                if line and len(line) > 20:
                    # Convert issue to anti-pattern
                    if self.add_discovery(
                        "antipattern",
                        f"Avoid: {line}",
                        f"Issue encountered in {project}",
                        "EXPERIMENTAL",
                        f"gsd:{project}"
                    ):
                        count += 1

        return count

    def _extract_from_verification(self, verification_path: Path, project: str) -> int:
        """Extract learnings from verification results."""
        count = 0
        content = verification_path.read_text()

        # Look for failed tests and their fixes
        failures_match = re.search(
            r'(?:failed|issues?|bugs?)[\s:]*\n((?:[-*]\s*.+\n?)+)',
            content,
            re.IGNORECASE
        )

        if failures_match:
            for line in failures_match.group(1).split('\n'):
                line = line.strip().lstrip('-*').strip()
                if line and len(line) > 20:
                    if self.add_discovery(
                        "antipattern",
                        f"Check for: {line}",
                        f"Verification issue in {project}",
                        "EXPERIMENTAL",
                        f"gsd:{project}"
                    ):
                        count += 1

        return count

    def discover_from_git_commits(self, days: int = 7) -> int:
        """Discover patterns from recent git commits."""
        count = 0

        for project in PROJECTS_DIR.iterdir():
            if not project.is_dir() or project.name.startswith((".", "_")):
                continue

            git_dir = project / ".git"
            if not git_dir.exists():
                continue

            try:
                # Get recent commits
                result = subprocess.run(
                    ["git", "log", f"--since={days} days ago", "--pretty=format:%s"],
                    cwd=project,
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode != 0:
                    continue

                commits = result.stdout.strip().split('\n')

                # Analyze commit patterns
                fix_count = sum(1 for c in commits if 'fix' in c.lower())
                refactor_count = sum(1 for c in commits if 'refactor' in c.lower())
                feature_count = sum(1 for c in commits if any(
                    w in c.lower() for w in ['feat', 'add', 'implement']
                ))

                # If lots of fixes, might indicate pattern to learn
                if fix_count > 3:
                    # Look for common fix patterns
                    fix_commits = [c for c in commits if 'fix' in c.lower()]
                    for commit in fix_commits[:3]:
                        # Extract what was fixed
                        if self.add_discovery(
                            "lesson",
                            f"Common fix pattern: {commit}",
                            f"Recurring fix in {project.name}",
                            "EXPERIMENTAL",
                            f"git:{project.name}"
                        ):
                            count += 1

            except Exception:
                continue

        return count

    def discover_from_module_patterns(self) -> int:
        """Discover patterns from module registry."""
        count = 0
        registry_file = MYWORK_ROOT / ".planning" / "module_registry.json"

        if not registry_file.exists():
            return 0

        try:
            with open(registry_file) as f:
                registry = json.load(f)

            modules = registry.get("modules", [])

            # Analyze naming patterns
            name_patterns = defaultdict(int)
            for mod in modules:
                name = mod.get("name", "")
                # Extract common prefixes
                if name.startswith(("get", "set", "create", "update", "delete")):
                    pattern = name[:6] + "..."
                    name_patterns[pattern] += 1
                elif name.startswith("use"):
                    name_patterns["use... (hook)"] += 1
                elif name.endswith(("Service", "Manager", "Handler")):
                    name_patterns["*Service/*Manager pattern"] += 1

            # Learn from dominant patterns
            for pattern, count_val in sorted(name_patterns.items(), key=lambda x: -x[1])[:3]:
                if count_val > 5:
                    if self.add_discovery(
                        "pattern",
                        f"Common naming: {pattern} (found {count_val} times)",
                        "From module registry analysis",
                        "TESTED",  # Based on evidence
                        "registry"
                    ):
                        count += 1

            # Analyze module types distribution
            type_counts = defaultdict(int)
            for mod in modules:
                type_counts[mod.get("type", "unknown")] += 1

            # Most common types are proven patterns
            for mod_type, type_count in sorted(type_counts.items(), key=lambda x: -x[1])[:3]:
                if type_count > 10:
                    if self.add_discovery(
                        "insight",
                        f"Project pattern: Heavy use of {mod_type} modules ({type_count} found)",
                        "From module registry analysis",
                        "TESTED",
                        "registry"
                    ):
                        count += 1

        except Exception as e:
            print(f"Warning: Could not analyze registry: {e}")

        return count

    def discover_from_error_patterns(self) -> int:
        """Discover patterns from error logs."""
        count = 0

        # Check various log files
        log_files = [
            MYWORK_ROOT / ".tmp" / "autocoder.error.log",
            MYWORK_ROOT / ".tmp" / "update.log",
        ]

        error_patterns = defaultdict(list)

        for log_file in log_files:
            if not log_file.exists():
                continue

            try:
                content = log_file.read_text()

                # Common error patterns
                patterns = [
                    (r'ModuleNotFoundError: No module named [\'"](\w+)[\'"]', "Missing Python module: {}"),
                    (r'ImportError: cannot import name [\'"](\w+)[\'"]', "Import issue: {}"),
                    (r'FileNotFoundError:.*[\'"]([^"\']+)[\'"]', "Missing file: {}"),
                    (r'PermissionError:.*[\'"]([^"\']+)[\'"]', "Permission issue: {}"),
                    (r'ConnectionRefusedError', "Connection refused - check if service is running"),
                    (r'timeout', "Timeout - increase timeout or check network"),
                ]

                for pattern, template in patterns:
                    for match in re.finditer(pattern, content, re.IGNORECASE):
                        if match.groups():
                            error_msg = template.format(match.group(1))
                        else:
                            error_msg = template
                        error_patterns[error_msg].append(log_file.name)

            except Exception:
                continue

        # Learn from recurring errors
        for error, occurrences in error_patterns.items():
            if len(occurrences) >= 2:  # Recurring error
                if self.add_discovery(
                    "antipattern",
                    f"Watch for: {error}",
                    f"Occurred {len(occurrences)} times in logs",
                    "EXPERIMENTAL",
                    "error_logs"
                ):
                    count += 1

        return count

    def promote_validated_entries(self) -> int:
        """Promote EXPERIMENTAL entries that have been validated."""
        count = 0

        for entry in list(self.brain.entries.values()):
            if entry.status != "EXPERIMENTAL":
                continue

            # Check if entry has been around for a while without issues
            try:
                added_date = datetime.strptime(entry.date_added, "%Y-%m-%d")
                age_days = (datetime.now() - added_date).days

                # If experimental for more than 14 days without deprecation, promote
                if age_days > 14:
                    self.brain.update(entry.id, status="TESTED")
                    count += 1
                    print(f"   ✅ Promoted {entry.id}: {entry.content[:40]}...")

            except ValueError:
                continue

        if count > 0:
            self.brain.save()
            self._update_brain_md()

        return count

    def smart_cleanup(self) -> int:
        """Intelligent cleanup based on relevance."""
        count = 0

        for entry in list(self.brain.entries.values()):
            # Check for obsolete entries
            obsolete_indicators = [
                "deprecated",
                "no longer",
                "outdated",
                "replaced by",
                "use instead",
            ]

            content_lower = entry.content.lower()
            if any(ind in content_lower for ind in obsolete_indicators):
                if entry.status != "DEPRECATED":
                    self.brain.update(entry.id, status="DEPRECATED")
                    count += 1
                    print(f"   🗑️ Deprecated {entry.id}: {entry.content[:40]}...")

        if count > 0:
            self.brain.save()
            self._update_brain_md()

        return count

    def commit_discoveries(self) -> int:
        """Commit all discoveries to the brain."""
        count = 0

        for discovery in self.discoveries:
            try:
                entry = self.brain.add(
                    entry_type=discovery["type"],
                    content=discovery["content"],
                    context=discovery["context"],
                    status=discovery["confidence"],
                    tags=[discovery["source"]]
                )
                count += 1
                print(f"   🧠 Learned [{entry.type}]: {entry.content[:50]}...")
            except Exception as e:
                print(f"   ⚠️ Could not add: {discovery['content'][:30]}... ({e})")

        self.discoveries = []
        self._update_brain_md()
        self.save_learning_log()

        return count

    def _update_brain_md(self):
        """Regenerate BRAIN.md from current data."""
        if not BRAIN_MD.exists():
            return

        content = BRAIN_MD.read_text()

        # Update the "Last updated" line
        content = re.sub(
            r'> Last updated: \d{4}-\d{2}-\d{2}',
            f'> Last updated: {datetime.now().strftime("%Y-%m-%d")}',
            content
        )

        # Update statistics in the changelog section if present
        stats = self.brain.get_stats()
        changelog_entry = f"| {datetime.now().strftime('%Y-%m-%d')} | Auto-learning: {stats['total_entries']} entries | Learning |"

        # Add to changelog if not already today
        if datetime.now().strftime('%Y-%m-%d') not in content.split("## Changelog")[-1]:
            content = content.replace(
                "## Changelog\n\n| Date | Change | Category |",
                f"## Changelog\n\n| Date | Change | Category |\n{changelog_entry}"
            )

        BRAIN_MD.write_text(content)


def run_daily_learning():
    """Daily learning routine."""
    print("\n🧠 Daily Brain Learning")
    print("=" * 50)

    engine = LearningEngine()
    total = 0

    print("\n📊 Discovering from recent work...")
    count = engine.discover_from_git_commits(days=1)
    print(f"   Found {count} patterns from git commits")
    total += count

    count = engine.discover_from_error_patterns()
    print(f"   Found {count} patterns from error logs")
    total += count

    print("\n📝 Committing discoveries...")
    committed = engine.commit_discoveries()
    print(f"   Committed {committed} new learnings")

    print("\n✨ Promoting validated entries...")
    promoted = engine.promote_validated_entries()
    print(f"   Promoted {promoted} entries to TESTED")

    print("\n" + "=" * 50)
    print(f"Daily learning complete: {total} discoveries, {committed} committed, {promoted} promoted")


def run_weekly_learning():
    """Weekly deep analysis."""
    print("\n🧠 Weekly Deep Brain Analysis")
    print("=" * 50)

    engine = LearningEngine()
    total = 0

    print("\n📊 Analyzing GSD phases...")
    count = engine.discover_from_gsd_phases()
    print(f"   Found {count} learnings from phase summaries")
    total += count

    print("\n📊 Analyzing git history (7 days)...")
    count = engine.discover_from_git_commits(days=7)
    print(f"   Found {count} patterns from git commits")
    total += count

    print("\n📊 Analyzing module registry...")
    count = engine.discover_from_module_patterns()
    print(f"   Found {count} patterns from modules")
    total += count

    print("\n📊 Analyzing error patterns...")
    count = engine.discover_from_error_patterns()
    print(f"   Found {count} patterns from errors")
    total += count

    print("\n📝 Committing discoveries...")
    committed = engine.commit_discoveries()
    print(f"   Committed {committed} new learnings")

    print("\n✨ Promoting validated entries...")
    promoted = engine.promote_validated_entries()
    print(f"   Promoted {promoted} entries to TESTED")

    print("\n🗑️ Smart cleanup...")
    cleaned = engine.smart_cleanup()
    print(f"   Deprecated {cleaned} obsolete entries")

    print("\n" + "=" * 50)
    stats = engine.brain.get_stats()
    print(f"Weekly analysis complete!")
    print(f"   Total brain entries: {stats['total_entries']}")
    print(f"   New discoveries: {total}")
    print(f"   Committed: {committed}")
    print(f"   Promoted: {promoted}")
    print(f"   Deprecated: {cleaned}")


def run_discover():
    """Quick discovery run."""
    print("\n🔍 Discovering new learnings...")

    engine = LearningEngine()
    total = 0

    count = engine.discover_from_gsd_phases()
    total += count

    count = engine.discover_from_git_commits(days=3)
    total += count

    count = engine.discover_from_module_patterns()
    total += count

    count = engine.discover_from_error_patterns()
    total += count

    print(f"\nFound {total} potential learnings")

    if total > 0:
        committed = engine.commit_discoveries()
        print(f"Committed {committed} to brain")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    command = sys.argv[1].lower()

    commands = {
        "discover": run_discover,
        "analyze-errors": lambda: LearningEngine().discover_from_error_patterns(),
        "analyze-modules": lambda: LearningEngine().discover_from_module_patterns(),
        "promote": lambda: LearningEngine().promote_validated_entries(),
        "cleanup-smart": lambda: LearningEngine().smart_cleanup(),
        "daily": run_daily_learning,
        "weekly": run_weekly_learning,
    }

    if command in commands:
        commands[command]()
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
