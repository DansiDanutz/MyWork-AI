#!/usr/bin/env python3
"""
Brain Semantic Search — Phase 9: Brain Intelligence
====================================================
Adds embedding-based semantic search, deduplication, and quality scoring
to the Brain knowledge vault.

Uses TF-IDF + cosine similarity for zero-dependency semantic search.
No API keys needed — runs fully offline.

Usage:
    python brain_semantic.py search <query>         # Semantic search
    python brain_semantic.py dedupe [--dry-run]     # Find duplicates
    python brain_semantic.py score                  # Quality score all entries
    python brain_semantic.py provenance <id>        # Show entry provenance
    python brain_semantic.py reindex                # Rebuild search index
"""

import json
import math
import os
import re
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ─── Configuration ───────────────────────────────────────────────
try:
    from config import get_mywork_root
except ImportError:
    def get_mywork_root() -> Path:
        if env_root := os.environ.get("MYWORK_ROOT"):
            return Path(env_root)
        script_dir = Path(__file__).resolve().parent
        return script_dir.parent if script_dir.name == "tools" else Path.home() / "MyWork"

MYWORK_ROOT = get_mywork_root().resolve()
BRAIN_JSON = MYWORK_ROOT / ".planning" / "brain_data.json"
INDEX_FILE = MYWORK_ROOT / ".planning" / "brain_index.json"
PROVENANCE_FILE = MYWORK_ROOT / ".planning" / "brain_provenance.json"

# ─── Stop words (common English) ────────────────────────────────
STOP_WORDS = frozenset(
    "a an the is are was were be been being have has had do does did "
    "will would shall should can could may might must to of in for on "
    "with at by from as into through during before after above below "
    "between out off over under again further then once here there when "
    "where why how all both each few more most other some such no nor "
    "not only own same so than too very it its and but or if that this "
    "these those which what who whom".split()
)


# ─── TF-IDF Engine ──────────────────────────────────────────────
def tokenize(text: str) -> List[str]:
    """Tokenize text into lowercase words, removing stop words."""
    words = re.findall(r'[a-z0-9]+', text.lower())
    return [w for w in words if w not in STOP_WORDS and len(w) > 1]


def compute_tf(tokens: List[str]) -> Dict[str, float]:
    """Term frequency (normalized)."""
    counts = Counter(tokens)
    total = len(tokens) or 1
    return {word: count / total for word, count in counts.items()}


def compute_idf(documents: List[List[str]]) -> Dict[str, float]:
    """Inverse document frequency."""
    n_docs = len(documents) or 1
    df = Counter()
    for doc in documents:
        df.update(set(doc))
    return {word: math.log(n_docs / (count + 1)) + 1 for word, count in df.items()}


def tfidf_vector(tf: Dict[str, float], idf: Dict[str, float]) -> Dict[str, float]:
    """TF-IDF vector for a document."""
    return {word: tf_val * idf.get(word, 1.0) for word, tf_val in tf.items()}


def cosine_similarity(v1: Dict[str, float], v2: Dict[str, float]) -> float:
    """Cosine similarity between two sparse vectors."""
    common = set(v1.keys()) & set(v2.keys())
    if not common:
        return 0.0
    dot = sum(v1[k] * v2[k] for k in common)
    mag1 = math.sqrt(sum(v ** 2 for v in v1.values()))
    mag2 = math.sqrt(sum(v ** 2 for v in v2.values()))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot / (mag1 * mag2)


# ─── Brain Loader ────────────────────────────────────────────────
def load_brain_entries() -> List[dict]:
    """Load all brain entries from JSON."""
    if not BRAIN_JSON.exists():
        return []
    try:
        data = json.loads(BRAIN_JSON.read_text())
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and "entries" in data:
            return data["entries"]
        return []
    except (json.JSONDecodeError, KeyError):
        return []


def entry_text(entry: dict) -> str:
    """Combine entry fields into searchable text."""
    parts = [
        entry.get("content", ""),
        entry.get("context", ""),
        entry.get("type", ""),
        " ".join(entry.get("tags", [])),
    ]
    return " ".join(p for p in parts if p)


# ─── Search Index ────────────────────────────────────────────────
@dataclass
class SearchIndex:
    """TF-IDF search index for brain entries."""
    entries: List[dict] = field(default_factory=list)
    tokens: List[List[str]] = field(default_factory=list)
    idf: Dict[str, float] = field(default_factory=dict)
    vectors: List[Dict[str, float]] = field(default_factory=list)
    built_at: str = ""

    def build(self, entries: List[dict]):
        """Build index from entries."""
        self.entries = entries
        self.tokens = [tokenize(entry_text(e)) for e in entries]
        self.idf = compute_idf(self.tokens)
        self.vectors = [
            tfidf_vector(compute_tf(tok), self.idf) for tok in self.tokens
        ]
        self.built_at = datetime.now().isoformat()

    def search(self, query: str, top_k: int = 10, min_score: float = 0.05) -> List[Tuple[dict, float]]:
        """Search entries by semantic similarity."""
        q_tokens = tokenize(query)
        q_tf = compute_tf(q_tokens)
        q_vec = tfidf_vector(q_tf, self.idf)

        results = []
        for i, vec in enumerate(self.vectors):
            score = cosine_similarity(q_vec, vec)
            if score >= min_score:
                results.append((self.entries[i], score))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def find_duplicates(self, threshold: float = 0.85) -> List[Tuple[dict, dict, float]]:
        """Find duplicate/near-duplicate entries."""
        dupes = []
        n = len(self.vectors)
        for i in range(n):
            for j in range(i + 1, n):
                sim = cosine_similarity(self.vectors[i], self.vectors[j])
                if sim >= threshold:
                    dupes.append((self.entries[i], self.entries[j], sim))
        dupes.sort(key=lambda x: x[2], reverse=True)
        return dupes

    def save(self, path: Path = INDEX_FILE):
        """Save index metadata (not vectors, those are rebuilt)."""
        meta = {
            "built_at": self.built_at,
            "entry_count": len(self.entries),
            "vocab_size": len(self.idf),
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(meta, indent=2))


# ─── Quality Scoring ────────────────────────────────────────────
def quality_score(entry: dict) -> dict:
    """Score an entry's quality on multiple dimensions (0-100)."""
    scores = {}

    # Completeness: has content, context, tags
    content = entry.get("content", "")
    context = entry.get("context", "")
    tags = entry.get("tags", [])
    completeness = 0
    if content:
        completeness += 40
    if context:
        completeness += 30
    if tags:
        completeness += 20
    if len(content) > 50:
        completeness += 10
    scores["completeness"] = min(completeness, 100)

    # Freshness: how recent
    date_str = entry.get("date_updated", entry.get("date_added", ""))
    if date_str:
        try:
            updated = datetime.strptime(date_str[:10], "%Y-%m-%d")
            days_old = (datetime.now() - updated).days
            if days_old < 7:
                scores["freshness"] = 100
            elif days_old < 30:
                scores["freshness"] = 80
            elif days_old < 90:
                scores["freshness"] = 60
            elif days_old < 365:
                scores["freshness"] = 40
            else:
                scores["freshness"] = 20
        except ValueError:
            scores["freshness"] = 50
    else:
        scores["freshness"] = 50

    # Usage: reference count
    refs = entry.get("references", 0)
    if refs >= 10:
        scores["usage"] = 100
    elif refs >= 5:
        scores["usage"] = 80
    elif refs >= 2:
        scores["usage"] = 60
    elif refs >= 1:
        scores["usage"] = 40
    else:
        scores["usage"] = 20

    # Status bonus
    status = entry.get("status", "").upper()
    if status == "TESTED":
        scores["reliability"] = 90
    elif status == "EXPERIMENTAL":
        scores["reliability"] = 50
    elif status == "DEPRECATED":
        scores["reliability"] = 10
    else:
        scores["reliability"] = 50

    # Overall weighted score
    weights = {"completeness": 0.3, "freshness": 0.2, "usage": 0.25, "reliability": 0.25}
    scores["overall"] = sum(scores[k] * weights[k] for k in weights)

    return scores


# ─── Provenance Tracking ────────────────────────────────────────
def load_provenance() -> dict:
    """Load provenance data."""
    if PROVENANCE_FILE.exists():
        try:
            return json.loads(PROVENANCE_FILE.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def save_provenance(data: dict):
    """Save provenance data."""
    PROVENANCE_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROVENANCE_FILE.write_text(json.dumps(data, indent=2))


def track_provenance(entry_id: str, action: str, actor: str = "system", details: str = ""):
    """Record a provenance event for an entry."""
    prov = load_provenance()
    if entry_id not in prov:
        prov[entry_id] = {"events": []}
    prov[entry_id]["events"].append({
        "action": action,
        "actor": actor,
        "timestamp": datetime.now().isoformat(),
        "details": details,
    })
    save_provenance(prov)


def get_provenance(entry_id: str) -> List[dict]:
    """Get provenance history for an entry."""
    prov = load_provenance()
    return prov.get(entry_id, {}).get("events", [])


# ─── CLI ─────────────────────────────────────────────────────────
def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]
    entries = load_brain_entries()

    if cmd == "search":
        if len(sys.argv) < 3:
            print("Usage: brain_semantic.py search <query>")
            return
        query = " ".join(sys.argv[2:])
        idx = SearchIndex()
        idx.build(entries)
        results = idx.search(query)
        if not results:
            print("No results found.")
            return
        print(f"\n🔍 Semantic search: '{query}' ({len(results)} results)\n")
        for entry, score in results:
            eid = entry.get("id", "?")
            etype = entry.get("type", "?")
            content = entry.get("content", "")[:80]
            print(f"  [{score:.2f}] {eid} ({etype}): {content}")

    elif cmd == "dedupe":
        dry_run = "--dry-run" in sys.argv
        idx = SearchIndex()
        idx.build(entries)
        dupes = idx.find_duplicates()
        if not dupes:
            print("✅ No duplicates found.")
            return
        print(f"\n⚠️  Found {len(dupes)} potential duplicate pairs:\n")
        for e1, e2, sim in dupes:
            print(f"  [{sim:.2f}] {e1.get('id','?')} ↔ {e2.get('id','?')}")
            print(f"         A: {e1.get('content','')[:60]}")
            print(f"         B: {e2.get('content','')[:60]}")
            print()
        if dry_run:
            print("(dry run — no changes made)")

    elif cmd == "score":
        if not entries:
            print("No brain entries found.")
            return
        scored = [(e, quality_score(e)) for e in entries]
        scored.sort(key=lambda x: x[1]["overall"], reverse=True)
        print(f"\n📊 Quality Scores ({len(scored)} entries):\n")
        print(f"  {'ID':<15} {'Type':<13} {'Overall':>7}  {'Complete':>8}  {'Fresh':>5}  {'Usage':>5}  {'Reliable':>8}")
        print("  " + "─" * 75)
        for entry, sc in scored[:20]:
            eid = entry.get("id", "?")[:14]
            etype = entry.get("type", "?")[:12]
            print(f"  {eid:<15} {etype:<13} {sc['overall']:>6.1f}  {sc['completeness']:>7}  {sc['freshness']:>5}  {sc['usage']:>5}  {sc['reliability']:>7}")
        
        avg = sum(s["overall"] for _, s in scored) / len(scored)
        print(f"\n  Average quality: {avg:.1f}/100")
        low_quality = [e for e, s in scored if s["overall"] < 40]
        if low_quality:
            print(f"  ⚠️  {len(low_quality)} entries below quality threshold (40)")

    elif cmd == "provenance":
        if len(sys.argv) < 3:
            print("Usage: brain_semantic.py provenance <entry_id>")
            return
        entry_id = sys.argv[2]
        events = get_provenance(entry_id)
        if not events:
            print(f"No provenance data for {entry_id}")
            return
        print(f"\n📋 Provenance for {entry_id}:\n")
        for ev in events:
            print(f"  {ev['timestamp'][:19]}  {ev['action']:<12}  by {ev['actor']}  {ev.get('details','')}")

    elif cmd == "reindex":
        idx = SearchIndex()
        idx.build(entries)
        idx.save()
        print(f"✅ Index rebuilt: {len(entries)} entries, {len(idx.idf)} terms")

    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)


if __name__ == "__main__":
    main()
