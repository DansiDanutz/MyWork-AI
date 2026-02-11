#!/usr/bin/env python3
"""
Brain Quality Scoring & Deduplication Engine
=============================================
Phase 9 — Brain Intelligence

Scores brain entries by quality and detects/removes duplicates.

Features:
- Quality scoring (0-100) based on content richness, metadata, recency
- Duplicate detection via content similarity (fuzzy + exact)
- Batch dedupe with merge support
- Provenance tracking (who added, when, usage count)
- CLI interface for quality reports

Usage:
    python brain_quality.py score              # Score all entries
    python brain_quality.py dedupe             # Find & remove duplicates
    python brain_quality.py report             # Full quality report
    python brain_quality.py prune --below 20   # Remove low-quality entries
"""

import os
import sys
import json
import math
import hashlib
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import defaultdict
from difflib import SequenceMatcher

# Import brain infrastructure
try:
    from brain import BrainManager, BrainEntry, ENTRY_TYPES
    from config import get_mywork_root
except ImportError:
    sys.path.append(str(Path(__file__).parent))
    from brain import BrainManager, BrainEntry, ENTRY_TYPES
    from config import get_mywork_root


class QualityScorer:
    """Scores brain entries on a 0-100 scale."""

    # Weight factors for scoring
    WEIGHTS = {
        "content_length": 15,      # Longer, detailed entries score higher
        "has_context": 10,         # Context adds value
        "has_tags": 10,            # Tags improve discoverability
        "tag_count": 5,            # More tags = better categorized
        "has_status": 5,           # Status tracking = maintained
        "status_quality": 10,      # TESTED > DRAFT
        "recency": 15,             # Recent entries more relevant
        "uniqueness": 20,          # Low similarity to others = unique value
        "completeness": 10,        # All fields filled
    }

    STATUS_SCORES = {
        "TESTED": 1.0,
        "VERIFIED": 0.9,
        "REVIEWED": 0.8,
        "ACTIVE": 0.7,
        "DRAFT": 0.4,
        "DEPRECATED": 0.1,
        "ARCHIVED": 0.2,
    }

    def __init__(self, brain: BrainManager):
        self.brain = brain
        self._similarity_cache: Dict[str, float] = {}

    def score_entry(self, entry: BrainEntry, all_entries: Optional[List[BrainEntry]] = None) -> Dict[str, Any]:
        """Score a single entry. Returns breakdown + total."""
        scores = {}

        # Content length (0-15): 0 for <20 chars, max at 500+ chars
        clen = len(entry.content)
        scores["content_length"] = min(clen / 500, 1.0) * self.WEIGHTS["content_length"]

        # Has context (0 or 10)
        scores["has_context"] = self.WEIGHTS["has_context"] if entry.context else 0

        # Has tags (0 or 10)
        has_tags = bool(entry.tags and len(entry.tags) > 0)
        scores["has_tags"] = self.WEIGHTS["has_tags"] if has_tags else 0

        # Tag count (0-5): bonus for 3+ tags
        tag_count = len(entry.tags) if entry.tags else 0
        scores["tag_count"] = min(tag_count / 3, 1.0) * self.WEIGHTS["tag_count"]

        # Has status (0 or 5)
        scores["has_status"] = self.WEIGHTS["has_status"] if entry.status else 0

        # Status quality (0-10)
        status_val = self.STATUS_SCORES.get(entry.status, 0.5) if entry.status else 0
        scores["status_quality"] = status_val * self.WEIGHTS["status_quality"]

        # Recency (0-15): full score if <7 days, decays over 90 days
        try:
            created = datetime.fromisoformat(entry.created) if isinstance(entry.created, str) else entry.created
            age_days = (datetime.now() - created).days
            recency = max(0, 1.0 - (age_days / 90))
            scores["recency"] = recency * self.WEIGHTS["recency"]
        except (ValueError, TypeError, AttributeError):
            scores["recency"] = self.WEIGHTS["recency"] * 0.5

        # Uniqueness (0-20): how different from other entries
        if all_entries:
            max_sim = self._max_similarity(entry, all_entries)
            scores["uniqueness"] = (1.0 - max_sim) * self.WEIGHTS["uniqueness"]
        else:
            scores["uniqueness"] = self.WEIGHTS["uniqueness"] * 0.7

        # Completeness (0-10): percentage of fields filled
        fields = [entry.content, entry.context, entry.tags, entry.status, entry.entry_type]
        filled = sum(1 for f in fields if f)
        scores["completeness"] = (filled / len(fields)) * self.WEIGHTS["completeness"]

        total = sum(scores.values())
        return {
            "entry_id": entry.id,
            "total": round(total, 1),
            "grade": self._grade(total),
            "breakdown": {k: round(v, 1) for k, v in scores.items()},
        }

    def _grade(self, score: float) -> str:
        if score >= 80: return "A"
        if score >= 65: return "B"
        if score >= 50: return "C"
        if score >= 35: return "D"
        return "F"

    def _max_similarity(self, entry: BrainEntry, all_entries: List[BrainEntry]) -> float:
        """Find highest similarity to any other entry."""
        max_sim = 0.0
        for other in all_entries:
            if other.id == entry.id:
                continue
            cache_key = f"{min(entry.id, other.id)}:{max(entry.id, other.id)}"
            if cache_key not in self._similarity_cache:
                sim = SequenceMatcher(None, entry.content.lower(), other.content.lower()).ratio()
                self._similarity_cache[cache_key] = sim
            max_sim = max(max_sim, self._similarity_cache[cache_key])
        return max_sim

    def score_all(self) -> List[Dict[str, Any]]:
        """Score all brain entries."""
        entries = list(self.brain.entries.values())
        results = []
        for entry in entries:
            result = self.score_entry(entry, entries)
            result["title"] = entry.content[:60]
            results.append(result)
        results.sort(key=lambda x: x["total"], reverse=True)
        return results


class DuplicateDetector:
    """Detects duplicate and near-duplicate brain entries."""

    SIMILARITY_THRESHOLD = 0.75  # 75%+ similarity = probable duplicate

    def __init__(self, brain: BrainManager):
        self.brain = brain

    def find_duplicates(self, threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        """Find all duplicate pairs above threshold."""
        thresh = threshold or self.SIMILARITY_THRESHOLD
        entries = list(self.brain.entries.values())
        duplicates = []
        seen = set()

        for i, a in enumerate(entries):
            for j, b in enumerate(entries):
                if j <= i:
                    continue
                pair_key = f"{a.id}:{b.id}"
                if pair_key in seen:
                    continue

                # Quick check: exact content match
                if a.content.strip().lower() == b.content.strip().lower():
                    duplicates.append({
                        "entry_a": a.id,
                        "entry_b": b.id,
                        "content_a": a.content[:80],
                        "content_b": b.content[:80],
                        "similarity": 1.0,
                        "type": "exact",
                    })
                    seen.add(pair_key)
                    continue

                # Fuzzy match
                sim = SequenceMatcher(None, a.content.lower(), b.content.lower()).ratio()
                if sim >= thresh:
                    duplicates.append({
                        "entry_a": a.id,
                        "entry_b": b.id,
                        "content_a": a.content[:80],
                        "content_b": b.content[:80],
                        "similarity": round(sim, 3),
                        "type": "fuzzy",
                    })
                    seen.add(pair_key)

        duplicates.sort(key=lambda x: x["similarity"], reverse=True)
        return duplicates

    def dedupe(self, threshold: Optional[float] = None, dry_run: bool = True) -> Dict[str, Any]:
        """Remove duplicates, keeping the higher-quality entry."""
        dupes = self.find_duplicates(threshold)
        scorer = QualityScorer(self.brain)
        entries = list(self.brain.entries.values())
        removed = []
        kept = []

        for dupe in dupes:
            entry_a = self.brain.entries.get(dupe["entry_a"])
            entry_b = self.brain.entries.get(dupe["entry_b"])
            if not entry_a or not entry_b:
                continue

            score_a = scorer.score_entry(entry_a, entries)["total"]
            score_b = scorer.score_entry(entry_b, entries)["total"]

            # Keep the higher-scored entry
            if score_a >= score_b:
                keep, remove = entry_a, entry_b
            else:
                keep, remove = entry_b, entry_a

            if not dry_run:
                if remove.id in self.brain.entries:
                    del self.brain.entries[remove.id]
                    removed.append(remove.id)
                    kept.append(keep.id)
            else:
                removed.append(remove.id)
                kept.append(keep.id)

        if not dry_run and removed:
            self.brain.save()

        return {
            "duplicates_found": len(dupes),
            "removed": removed,
            "kept": kept,
            "dry_run": dry_run,
        }


class ProvenanceTracker:
    """Track entry provenance — who added, usage count, last accessed."""

    PROVENANCE_FILE = "brain_provenance.json"

    def __init__(self, brain: BrainManager):
        self.brain = brain
        root = get_mywork_root()
        self.prov_path = Path(root) / ".brain" / self.PROVENANCE_FILE
        self.data = self._load()

    def _load(self) -> Dict[str, Dict]:
        if self.prov_path.exists():
            try:
                return json.loads(self.prov_path.read_text())
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def save(self):
        self.prov_path.parent.mkdir(parents=True, exist_ok=True)
        self.prov_path.write_text(json.dumps(self.data, indent=2, default=str))

    def record_access(self, entry_id: str, accessor: str = "system"):
        """Record that an entry was accessed."""
        if entry_id not in self.data:
            self.data[entry_id] = {
                "created_by": "unknown",
                "access_count": 0,
                "last_accessed": None,
                "accessors": [],
            }
        self.data[entry_id]["access_count"] += 1
        self.data[entry_id]["last_accessed"] = datetime.now().isoformat()
        if accessor not in self.data[entry_id]["accessors"]:
            self.data[entry_id]["accessors"].append(accessor)
        self.save()

    def record_creation(self, entry_id: str, creator: str = "unknown"):
        """Record who created an entry."""
        if entry_id not in self.data:
            self.data[entry_id] = {
                "created_by": creator,
                "access_count": 0,
                "last_accessed": None,
                "accessors": [],
            }
        else:
            self.data[entry_id]["created_by"] = creator
        self.save()

    def get_provenance(self, entry_id: str) -> Optional[Dict]:
        return self.data.get(entry_id)

    def report(self) -> Dict[str, Any]:
        """Summary provenance report."""
        total = len(self.data)
        if total == 0:
            return {"total_tracked": 0, "most_accessed": [], "never_accessed": []}

        sorted_by_access = sorted(
            self.data.items(),
            key=lambda x: x[1].get("access_count", 0),
            reverse=True,
        )
        most_accessed = [
            {"id": k, "count": v.get("access_count", 0)}
            for k, v in sorted_by_access[:5]
        ]
        never_accessed = [k for k, v in self.data.items() if v.get("access_count", 0) == 0]

        return {
            "total_tracked": total,
            "most_accessed": most_accessed,
            "never_accessed_count": len(never_accessed),
        }


def quality_report(brain: BrainManager) -> str:
    """Generate a full quality report."""
    scorer = QualityScorer(brain)
    detector = DuplicateDetector(brain)

    scores = scorer.score_all()
    dupes = detector.find_duplicates()

    lines = ["=" * 60, "  BRAIN QUALITY REPORT", "=" * 60, ""]

    # Summary
    if scores:
        avg = sum(s["total"] for s in scores) / len(scores)
        grade_counts = defaultdict(int)
        for s in scores:
            grade_counts[s["grade"]] += 1

        lines.append(f"Total entries: {len(scores)}")
        lines.append(f"Average score: {avg:.1f}/100")
        lines.append(f"Grades: A={grade_counts['A']} B={grade_counts['B']} "
                     f"C={grade_counts['C']} D={grade_counts['D']} F={grade_counts['F']}")
        lines.append("")

        # Top 5
        lines.append("--- TOP 5 ---")
        for s in scores[:5]:
            lines.append(f"  [{s['grade']}] {s['total']:5.1f}  {s['title']}")
        lines.append("")

        # Bottom 5
        if len(scores) > 5:
            lines.append("--- BOTTOM 5 ---")
            for s in scores[-5:]:
                lines.append(f"  [{s['grade']}] {s['total']:5.1f}  {s['title']}")
            lines.append("")
    else:
        lines.append("No entries to score.")

    # Duplicates
    lines.append(f"--- DUPLICATES ({len(dupes)} found) ---")
    for d in dupes[:10]:
        lines.append(f"  {d['similarity']:.0%} match ({d['type']})")
        lines.append(f"    A: {d['content_a']}")
        lines.append(f"    B: {d['content_b']}")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Brain Quality & Dedupe Engine")
    parser.add_argument("command", choices=["score", "dedupe", "report", "prune"],
                       help="Command to run")
    parser.add_argument("--below", type=float, default=20,
                       help="Prune entries below this score (default: 20)")
    parser.add_argument("--threshold", type=float, default=0.75,
                       help="Similarity threshold for dedupe (default: 0.75)")
    parser.add_argument("--apply", action="store_true",
                       help="Actually apply changes (default: dry run)")
    args = parser.parse_args()

    brain = BrainManager()

    if args.command == "score":
        scorer = QualityScorer(brain)
        results = scorer.score_all()
        for r in results:
            print(f"[{r['grade']}] {r['total']:5.1f}  {r['title']}")

    elif args.command == "dedupe":
        detector = DuplicateDetector(brain)
        result = detector.dedupe(threshold=args.threshold, dry_run=not args.apply)
        print(json.dumps(result, indent=2))

    elif args.command == "report":
        print(quality_report(brain))

    elif args.command == "prune":
        scorer = QualityScorer(brain)
        results = scorer.score_all()
        to_prune = [r for r in results if r["total"] < args.below]
        print(f"Entries below {args.below}: {len(to_prune)}")
        for r in to_prune:
            print(f"  [{r['grade']}] {r['total']:5.1f}  {r['title']}")
        if args.apply and to_prune:
            for r in to_prune:
                if r["entry_id"] in brain.entries:
                    del brain.entries[r["entry_id"]]
            brain.save()
            print(f"Pruned {len(to_prune)} entries.")
        elif to_prune:
            print("(dry run — use --apply to prune)")


if __name__ == "__main__":
    main()
