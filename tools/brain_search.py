#!/usr/bin/env python3
"""
Brain Semantic Search Engine
============================
Advanced search capabilities for the MyWork-AI Brain using TF-IDF and fuzzy matching.

Usage:
    python brain_search.py "deployment patterns" --type pattern --status TESTED
    python brain_search.py "api" --fuzzy --limit 5
    python brain_search.py --tags python,docker --since 2026-01-01
    python brain_search.py --interactive

Features:
- TF-IDF scoring for semantic relevance
- Fuzzy matching for typos and partial matches
- Search by content, tags, type, date range, status
- Interactive search mode
- Relevance ranking and scoring
- Search result caching for performance
"""

import os
import sys
import re
import json
import math
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import defaultdict, Counter
from difflib import SequenceMatcher

# Import brain infrastructure
try:
    from brain import BrainManager, BrainEntry, ENTRY_TYPES
    from config import get_mywork_root
except ImportError:
    sys.path.append(str(Path(__file__).parent))
    from brain import BrainManager, BrainEntry, ENTRY_TYPES
    from config import get_mywork_root

class TFIDFSearchEngine:
    """TF-IDF based search engine for brain entries."""
    
    def __init__(self, brain_manager: BrainManager):
        self.brain = brain_manager
        self.documents = {}  # id -> text
        self.vocabulary = set()
        self.tf_scores = {}  # doc_id -> {term: tf_score}
        self.idf_scores = {}  # term -> idf_score
        self.doc_lengths = {}  # doc_id -> length
        self._build_index()
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into searchable terms."""
        # Convert to lowercase, split on non-alphanumeric, filter short words
        words = re.findall(r'\b[a-zA-Z0-9]+\b', text.lower())
        return [word for word in words if len(word) >= 2]
    
    def _build_index(self):
        """Build TF-IDF index from all brain entries."""
        # Collect all documents
        for entry in self.brain.entries.values():
            # Combine content, context, and tags for searchable text
            text_parts = [entry.content]
            if entry.context:
                text_parts.append(entry.context)
            if entry.tags:
                text_parts.extend(entry.tags)
            
            full_text = ' '.join(text_parts)
            self.documents[entry.id] = full_text
            
            # Tokenize and build vocabulary
            tokens = self._tokenize(full_text)
            self.vocabulary.update(tokens)
            
            # Calculate TF scores
            token_counts = Counter(tokens)
            total_tokens = len(tokens)
            
            self.tf_scores[entry.id] = {}
            for token, count in token_counts.items():
                # Use log-normalized TF
                self.tf_scores[entry.id][token] = 1 + math.log(count) if count > 0 else 0
            
            self.doc_lengths[entry.id] = math.sqrt(sum(score ** 2 for score in self.tf_scores[entry.id].values()))
        
        # Calculate IDF scores
        num_docs = len(self.documents)
        for term in self.vocabulary:
            docs_with_term = sum(1 for doc_id in self.documents 
                               if term in self.tf_scores[doc_id])
            # Use smooth IDF to avoid division by zero
            self.idf_scores[term] = math.log(num_docs / (1 + docs_with_term))
    
    def search(self, query: str, limit: int = 20) -> List[Tuple[float, BrainEntry]]:
        """Search using TF-IDF scoring."""
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []
        
        # Calculate query TF scores
        query_counts = Counter(query_tokens)
        query_tf = {}
        for token, count in query_counts.items():
            query_tf[token] = 1 + math.log(count) if count > 0 else 0
        
        # Calculate query length
        query_length = math.sqrt(sum(score ** 2 for score in query_tf.values()))
        
        # Score each document
        scores = []
        for doc_id, entry in self.brain.entries.items():
            if doc_id not in self.tf_scores:
                continue
            
            # Calculate cosine similarity
            dot_product = 0
            for token in query_tokens:
                if token in self.tf_scores[doc_id] and token in self.idf_scores:
                    tf_idf_doc = self.tf_scores[doc_id][token] * self.idf_scores[token]
                    tf_idf_query = query_tf.get(token, 0) * self.idf_scores[token]
                    dot_product += tf_idf_doc * tf_idf_query
            
            if dot_product > 0 and self.doc_lengths[doc_id] > 0:
                cosine_similarity = dot_product / (self.doc_lengths[doc_id] * query_length)
                scores.append((cosine_similarity, entry))
        
        # Sort by score and return top results
        scores.sort(key=lambda x: x[0], reverse=True)
        return scores[:limit]


class FuzzyMatcher:
    """Fuzzy string matching for handling typos and partial matches."""
    
    @staticmethod
    def similarity_ratio(a: str, b: str) -> float:
        """Calculate similarity ratio between two strings."""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    @classmethod
    def fuzzy_search(cls, query: str, entries: List[BrainEntry], threshold: float = 0.6) -> List[Tuple[float, BrainEntry]]:
        """Fuzzy search across all entry text."""
        results = []
        query_lower = query.lower()
        
        for entry in entries:
            # Check content
            content_score = cls.similarity_ratio(query, entry.content)
            
            # Check tags
            tag_scores = [cls.similarity_ratio(query, tag) for tag in entry.tags]
            max_tag_score = max(tag_scores) if tag_scores else 0
            
            # Check context
            context_score = cls.similarity_ratio(query, entry.context) if entry.context else 0
            
            # Take the maximum score
            best_score = max(content_score, max_tag_score, context_score)
            
            if best_score >= threshold:
                results.append((best_score, entry))
        
        results.sort(key=lambda x: x[0], reverse=True)
        return results


class AdvancedBrainSearch:
    """Advanced search engine combining multiple search strategies."""
    
    def __init__(self):
        self.brain = BrainManager()
        self.tfidf_engine = TFIDFSearchEngine(self.brain)
        self.fuzzy_matcher = FuzzyMatcher()
    
    def search(self, 
               query: Optional[str] = None,
               entry_type: Optional[str] = None,
               status: Optional[str] = None,
               tags: Optional[List[str]] = None,
               since: Optional[str] = None,
               until: Optional[str] = None,
               fuzzy: bool = False,
               limit: int = 20) -> List[Tuple[float, BrainEntry]]:
        """Advanced search with multiple filters and ranking."""
        
        # Start with all entries
        candidates = list(self.brain.entries.values())
        
        # Apply filters first to narrow down candidates
        if entry_type:
            candidates = [e for e in candidates if e.type == entry_type]
        
        if status:
            candidates = [e for e in candidates if e.status.upper() == status.upper()]
        
        if tags:
            tag_set = set(tag.lower() for tag in tags)
            candidates = [e for e in candidates 
                         if any(tag.lower() in tag_set for tag in e.tags)]
        
        # Date filtering
        if since:
            since_date = datetime.strptime(since, '%Y-%m-%d').date()
            candidates = [e for e in candidates 
                         if datetime.strptime(e.date_added, '%Y-%m-%d').date() >= since_date]
        
        if until:
            until_date = datetime.strptime(until, '%Y-%m-%d').date()
            candidates = [e for e in candidates 
                         if datetime.strptime(e.date_added, '%Y-%m-%d').date() <= until_date]
        
        # If no query, return filtered results sorted by date
        if not query:
            results = [(1.0, entry) for entry in candidates]
            results.sort(key=lambda x: x[1].date_updated, reverse=True)
            return results[:limit]
        
        # Apply text search
        if fuzzy:
            results = self.fuzzy_matcher.fuzzy_search(query, candidates)
        else:
            # Filter candidates to only those in our filtered set
            temp_brain = BrainManager()
            temp_brain.entries = {e.id: e for e in candidates}
            temp_tfidf = TFIDFSearchEngine(temp_brain)
            results = temp_tfidf.search(query, limit)
        
        return results[:limit]
    
    def get_search_suggestions(self, partial_query: str) -> List[str]:
        """Get search suggestions based on partial query."""
        suggestions = set()
        partial_lower = partial_query.lower()
        
        # Collect words from content and tags
        for entry in self.brain.entries.values():
            # Words from content
            words = re.findall(r'\b[a-zA-Z0-9]+\b', entry.content.lower())
            for word in words:
                if word.startswith(partial_lower) and len(word) > len(partial_lower):
                    suggestions.add(word)
            
            # Tags
            for tag in entry.tags:
                if tag.lower().startswith(partial_lower) and len(tag) > len(partial_lower):
                    suggestions.add(tag.lower())
        
        return sorted(list(suggestions))[:10]


def print_search_results(results: List[Tuple[float, BrainEntry]], query: str, show_scores: bool = False):
    """Print search results with improved formatting."""
    # Color codes
    BOLD = '\033[1m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

    if not results:
        print(f"\n{RED}❌ No entries found matching '{YELLOW}{query}{RESET}{RED}'{RESET}")
        return

    # Search results header
    print(f"\n{BOLD}{CYAN}{'═' * 80}{RESET}")
    print(f"{BOLD}{CYAN}🔍 SEMANTIC SEARCH RESULTS{RESET}")
    print(f"{BOLD}{CYAN}{'═' * 80}{RESET}")
    print(f"{GREEN}Query:{RESET} '{YELLOW}{query}{RESET}' • {GREEN}Found:{RESET} {BOLD}{len(results)}{RESET} entries")
    
    # Show relevance scores distribution
    if show_scores and results:
        scores = [score for score, _ in results]
        avg_score = sum(scores) / len(scores)
        max_score = max(scores)
        print(f"{BLUE}📊 Relevance: Max={max_score:.3f} • Avg={avg_score:.3f}{RESET}")
    
    print(f"\n{BOLD}{CYAN}{'─' * 80}{RESET}")
    
    # Show results
    for i, (score, entry) in enumerate(results, 1):
        relevance_bar = '█' * int(score * 10) + '░' * (10 - int(score * 10))
        score_text = f" ({score:.3f})" if show_scores else ""
        
        print(f"\n{BOLD}{YELLOW}[{i}/{len(results)}]{RESET} {GREEN}{relevance_bar}{RESET}{score_text}")
        
        # Entry details
        status_icons = {"TESTED": "✅", "EXPERIMENTAL": "🧪", "DEPRECATED": "❌"}
        icon = status_icons.get(entry.status, "❓")
        
        print(f"{CYAN}╭─ {icon} {BOLD}{entry.type.upper()}{RESET}{CYAN} [{entry.id}]{'─' * max(0, 50 - len(entry.id) - len(entry.type))}╮{RESET}")
        
        # Content (truncated)
        content_preview = entry.content[:70] + '...' if len(entry.content) > 70 else entry.content
        print(f"{CYAN}│ {RESET}{content_preview:<70}{CYAN} │{RESET}")
        
        # Metadata
        metadata = f"📅 {entry.date_added} • 🏷️ {entry.status}"
        if entry.tags:
            metadata += f" • 🔖 {', '.join(entry.tags[:3])}"
        print(f"{CYAN}├─{BLUE} {metadata:<68} {CYAN}─┤{RESET}")
        
        print(f"{CYAN}╰{'─' * 72}╯{RESET}")
    
    print(f"\n{BOLD}{CYAN}{'═' * 80}{RESET}")


def interactive_search():
    """Interactive search mode with live suggestions."""
    print("\n🧠 Brain Interactive Search")
    print("=" * 50)
    print("Enter search queries (empty to exit)")
    print("Commands: :type <type>, :status <status>, :tags <tag1,tag2>, :fuzzy, :help")
    
    searcher = AdvancedBrainSearch()
    
    # Search state
    filters = {
        'entry_type': None,
        'status': None,
        'tags': None,
        'fuzzy': False,
        'limit': 10
    }
    
    while True:
        try:
            # Show current filters
            active_filters = []
            for key, value in filters.items():
                if value and key != 'limit':
                    if key == 'tags' and isinstance(value, list):
                        active_filters.append(f"{key}={','.join(value)}")
                    elif key == 'fuzzy' and value:
                        active_filters.append("fuzzy=on")
                    elif value and key != 'fuzzy':
                        active_filters.append(f"{key}={value}")
            
            filter_text = f" [{', '.join(active_filters)}]" if active_filters else ""
            
            query = input(f"\n🔍 Search{filter_text}: ").strip()
            
            if not query:
                break
            
            # Handle commands
            if query.startswith(':'):
                cmd_parts = query[1:].split()
                if not cmd_parts:
                    continue
                
                cmd = cmd_parts[0]
                if cmd == 'help':
                    print("\nCommands:")
                    print("  :type <type>     - Filter by entry type")
                    print("  :status <status> - Filter by status")
                    print("  :tags <tag1,tag2> - Filter by tags")
                    print("  :fuzzy          - Toggle fuzzy search")
                    print("  :clear          - Clear all filters")
                    print("  :stats          - Show brain stats")
                elif cmd == 'type' and len(cmd_parts) > 1:
                    entry_type = cmd_parts[1]
                    if entry_type in ENTRY_TYPES:
                        filters['entry_type'] = entry_type
                        print(f"✅ Filter by type: {entry_type}")
                    else:
                        print(f"❌ Invalid type. Valid: {', '.join(ENTRY_TYPES.keys())}")
                elif cmd == 'status' and len(cmd_parts) > 1:
                    filters['status'] = cmd_parts[1].upper()
                    print(f"✅ Filter by status: {filters['status']}")
                elif cmd == 'tags' and len(cmd_parts) > 1:
                    filters['tags'] = [tag.strip() for tag in ' '.join(cmd_parts[1:]).split(',')]
                    print(f"✅ Filter by tags: {', '.join(filters['tags'])}")
                elif cmd == 'fuzzy':
                    filters['fuzzy'] = not filters['fuzzy']
                    print(f"✅ Fuzzy search: {'on' if filters['fuzzy'] else 'off'}")
                elif cmd == 'clear':
                    filters = {k: None if k != 'limit' and k != 'fuzzy' else (10 if k == 'limit' else False) for k in filters}
                    print("✅ All filters cleared")
                elif cmd == 'stats':
                    stats = searcher.brain.get_stats()
                    print(f"\n📊 Total entries: {stats['total_entries']}")
                    print(f"   By type: {dict(stats['by_type'])}")
                    print(f"   By status: {dict(stats['by_status'])}")
                continue
            
            # Perform search
            results = searcher.search(
                query=query,
                entry_type=filters['entry_type'],
                status=filters['status'],
                tags=filters['tags'],
                fuzzy=filters['fuzzy'],
                limit=filters['limit']
            )
            
            print_search_results(results, query, show_scores=True)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n👋 Interactive search ended")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Advanced Brain Search Engine')
    parser.add_argument('query', nargs='?', help='Search query')
    parser.add_argument('--type', dest='entry_type', choices=list(ENTRY_TYPES.keys()),
                       help='Filter by entry type')
    parser.add_argument('--status', choices=['TESTED', 'EXPERIMENTAL', 'DEPRECATED'],
                       help='Filter by status')
    parser.add_argument('--tags', help='Filter by tags (comma-separated)')
    parser.add_argument('--since', help='Filter entries since date (YYYY-MM-DD)')
    parser.add_argument('--until', help='Filter entries until date (YYYY-MM-DD)')
    parser.add_argument('--fuzzy', action='store_true', help='Enable fuzzy matching')
    parser.add_argument('--limit', type=int, default=20, help='Maximum results to return')
    parser.add_argument('--scores', action='store_true', help='Show relevance scores')
    parser.add_argument('--interactive', action='store_true', help='Interactive search mode')
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_search()
        return
    
    if not args.query:
        print("Usage: python brain_search.py <query> [options]")
        print("   or: python brain_search.py --interactive")
        parser.print_help()
        return
    
    # Parse tags
    tags = None
    if args.tags:
        tags = [tag.strip() for tag in args.tags.split(',')]
    
    # Perform search
    searcher = AdvancedBrainSearch()
    results = searcher.search(
        query=args.query,
        entry_type=args.entry_type,
        status=args.status,
        tags=tags,
        since=args.since,
        until=args.until,
        fuzzy=args.fuzzy,
        limit=args.limit
    )
    
    print_search_results(results, args.query, show_scores=args.scores)
    
    # Show search suggestions if no results
    if not results:
        suggestions = searcher.get_search_suggestions(args.query)
        if suggestions:
            print(f"\n💡 Suggestions: {', '.join(suggestions[:5])}")


if __name__ == "__main__":
    main()