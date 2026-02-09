#!/usr/bin/env python3
"""
Brain Knowledge Graph and Connection Analysis
============================================
Analyzes and visualizes relationships between brain entries.

Usage:
    python brain_graph.py graph                    # Show ASCII knowledge graph
    python brain_graph.py related <entry_id>       # Find related entries
    python brain_graph.py cluster                  # Group similar knowledge
    python brain_graph.py connections <entry_id>   # Detailed connection analysis
    python brain_graph.py network-stats            # Network statistics
    python brain_graph.py export-graph             # Export graph as JSON

Features:
- Auto-detect relationships via shared tags and content similarity
- ASCII visualization of knowledge connections
- Clustering algorithm to group related knowledge
- Connection strength scoring
- Network analysis metrics
"""

import os
import sys
import re
import json
import math
from collections import defaultdict, Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from difflib import SequenceMatcher

# Import brain infrastructure
try:
    from brain import BrainManager, BrainEntry, ENTRY_TYPES
    from config import get_mywork_root
except ImportError:
    sys.path.append(str(Path(__file__).parent))
    from brain import BrainManager, BrainEntry, ENTRY_TYPES
    from config import get_mywork_root


class KnowledgeGraph:
    """Represents a knowledge graph of brain entries and their connections."""
    
    def __init__(self, brain_manager: BrainManager):
        self.brain = brain_manager
        self.nodes = {}  # entry_id -> entry
        self.edges = defaultdict(list)  # entry_id -> [(connected_id, strength)]
        self.connection_types = defaultdict(lambda: defaultdict(list))  # type -> type -> connections
        self._build_graph()
    
    def _calculate_content_similarity(self, entry1: BrainEntry, entry2: BrainEntry) -> float:
        """Calculate content similarity between two entries using token overlap."""
        def tokenize(text):
            return set(re.findall(r'\b[a-zA-Z0-9]+\b', text.lower()))
        
        # Get tokens from content and context
        tokens1 = tokenize(entry1.content + ' ' + (entry1.context or ''))
        tokens2 = tokenize(entry2.content + ' ' + (entry2.context or ''))
        
        if not tokens1 or not tokens2:
            return 0.0
        
        # Jaccard similarity
        intersection = tokens1 & tokens2
        union = tokens1 | tokens2
        
        jaccard = len(intersection) / len(union) if union else 0
        
        # Boost similarity if there's substantial word overlap
        if len(intersection) >= 3:  # 3+ shared meaningful words
            jaccard *= 1.5
        
        return min(jaccard, 1.0)
    
    def _calculate_tag_similarity(self, entry1: BrainEntry, entry2: BrainEntry) -> float:
        """Calculate tag similarity between entries."""
        tags1 = set(tag.lower() for tag in entry1.tags)
        tags2 = set(tag.lower() for tag in entry2.tags)
        
        if not tags1 or not tags2:
            return 0.0
        
        intersection = tags1 & tags2
        union = tags1 | tags2
        
        return len(intersection) / len(union) if union else 0
    
    def _calculate_type_affinity(self, entry1: BrainEntry, entry2: BrainEntry) -> float:
        """Calculate type-based relationship strength."""
        # Some types naturally connect more than others
        type_affinities = {
            ('pattern', 'lesson'): 0.7,      # Patterns often come from lessons
            ('lesson', 'antipattern'): 0.6,   # Lessons learn what NOT to do
            ('tip', 'pattern'): 0.5,         # Tips support patterns
            ('insight', 'pattern'): 0.8,     # Insights often reveal patterns
            ('experiment', 'lesson'): 0.9,   # Experiments become lessons
            ('experiment', 'pattern'): 0.7,  # Successful experiments become patterns
        }
        
        # Check both directions
        key1 = (entry1.type, entry2.type)
        key2 = (entry2.type, entry1.type)
        
        return type_affinities.get(key1, type_affinities.get(key2, 0.1))
    
    def _calculate_temporal_affinity(self, entry1: BrainEntry, entry2: BrainEntry) -> float:
        """Calculate temporal relationship (entries created around same time)."""
        try:
            date1 = datetime.strptime(entry1.date_added, '%Y-%m-%d')
            date2 = datetime.strptime(entry2.date_added, '%Y-%m-%d')
            
            days_apart = abs((date1 - date2).days)
            
            # Higher affinity for entries created close in time
            if days_apart <= 1:
                return 0.3
            elif days_apart <= 7:
                return 0.2
            elif days_apart <= 30:
                return 0.1
            else:
                return 0.0
        except:
            return 0.0
    
    def _build_graph(self):
        """Build the knowledge graph by analyzing all connections."""
        entries = list(self.brain.entries.values())
        
        # Initialize nodes
        for entry in entries:
            self.nodes[entry.id] = entry
        
        # Calculate connections between all pairs
        for i, entry1 in enumerate(entries):
            for entry2 in entries[i+1:]:  # Avoid duplicates and self-connections
                
                # Calculate different types of similarity
                content_sim = self._calculate_content_similarity(entry1, entry2)
                tag_sim = self._calculate_tag_similarity(entry1, entry2)
                type_affinity = self._calculate_type_affinity(entry1, entry2)
                temporal_affinity = self._calculate_temporal_affinity(entry1, entry2)
                
                # Weighted combination
                total_strength = (
                    content_sim * 0.4 +      # Content is most important
                    tag_sim * 0.3 +          # Tags are explicit connections
                    type_affinity * 0.2 +    # Type relationships matter
                    temporal_affinity * 0.1   # Time proximity is less important
                )
                
                # Only create edges above a threshold
                if total_strength >= 0.15:
                    connection_info = {
                        'strength': total_strength,
                        'content_sim': content_sim,
                        'tag_sim': tag_sim,
                        'type_affinity': type_affinity,
                        'temporal_affinity': temporal_affinity
                    }
                    
                    self.edges[entry1.id].append((entry2.id, connection_info))
                    self.edges[entry2.id].append((entry1.id, connection_info))
                    
                    # Track type connections
                    self.connection_types[entry1.type][entry2.type].append((entry1.id, entry2.id, total_strength))
                    self.connection_types[entry2.type][entry1.type].append((entry2.id, entry1.id, total_strength))
    
    def get_related_entries(self, entry_id: str, limit: int = 10) -> List[Tuple[str, Dict]]:
        """Get entries related to the given entry, sorted by connection strength."""
        if entry_id not in self.edges:
            return []
        
        connections = self.edges[entry_id]
        connections.sort(key=lambda x: x[1]['strength'], reverse=True)
        return connections[:limit]
    
    def get_clusters(self, min_cluster_size: int = 2) -> List[List[str]]:
        """Group related entries into clusters using a simple greedy algorithm."""
        visited = set()
        clusters = []
        
        for entry_id in self.nodes:
            if entry_id in visited:
                continue
            
            # Start a new cluster with this entry
            cluster = [entry_id]
            visited.add(entry_id)
            queue = [entry_id]
            
            # Expand cluster by adding connected entries
            while queue:
                current = queue.pop(0)
                
                for connected_id, connection_info in self.edges[current]:
                    if connected_id not in visited and connection_info['strength'] >= 0.25:
                        cluster.append(connected_id)
                        visited.add(connected_id)
                        queue.append(connected_id)
            
            if len(cluster) >= min_cluster_size:
                clusters.append(cluster)
            else:
                # Single-entry clusters for orphaned nodes
                clusters.append(cluster)
        
        # Sort clusters by size
        clusters.sort(key=len, reverse=True)
        return clusters
    
    def get_network_stats(self) -> Dict[str, Any]:
        """Calculate network statistics."""
        total_nodes = len(self.nodes)
        total_edges = sum(len(connections) for connections in self.edges.values()) // 2  # Undirected
        
        # Calculate degree distribution
        degrees = [len(connections) for connections in self.edges.values()]
        avg_degree = sum(degrees) / len(degrees) if degrees else 0
        max_degree = max(degrees) if degrees else 0
        
        # Find most connected entries
        most_connected = []
        for entry_id, connections in self.edges.items():
            degree = len(connections)
            if degree > 0:
                avg_strength = sum(conn[1]['strength'] for conn in connections) / degree
                most_connected.append((entry_id, degree, avg_strength))
        
        most_connected.sort(key=lambda x: (x[1], x[2]), reverse=True)
        
        # Calculate clustering coefficient (simplified)
        clusters = self.get_clusters()
        largest_cluster_size = max(len(cluster) for cluster in clusters) if clusters else 0
        
        return {
            'total_nodes': total_nodes,
            'total_edges': total_edges,
            'average_degree': avg_degree,
            'max_degree': max_degree,
            'density': (2 * total_edges) / (total_nodes * (total_nodes - 1)) if total_nodes > 1 else 0,
            'clusters': len(clusters),
            'largest_cluster_size': largest_cluster_size,
            'most_connected': most_connected[:5]
        }


def print_ascii_graph(graph: KnowledgeGraph, max_nodes: int = 20):
    """Print an ASCII representation of the knowledge graph."""
    # Color codes
    BOLD = '\033[1m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    
    print(f"\n{BOLD}{CYAN}{'═' * 80}{RESET}")
    print(f"{BOLD}{CYAN}🕸️  KNOWLEDGE GRAPH VISUALIZATION{RESET}")
    print(f"{BOLD}{CYAN}{'═' * 80}{RESET}")
    
    # Get clusters for organization
    clusters = graph.get_clusters()
    
    if not clusters:
        print(f"{RED}❌ No connections found in the knowledge graph{RESET}")
        return
    
    # Color map for different entry types
    type_colors = {
        'lesson': YELLOW,
        'pattern': GREEN,
        'antipattern': RED,
        'tip': BLUE,
        'insight': MAGENTA,
        'experiment': CYAN
    }
    
    print(f"{BLUE}Legend:{RESET}")
    for entry_type, color in type_colors.items():
        print(f"  {color}●{RESET} {entry_type}")
    
    nodes_shown = 0
    for i, cluster in enumerate(clusters):
        if nodes_shown >= max_nodes:
            remaining_clusters = len(clusters) - i
            remaining_nodes = sum(len(c) for c in clusters[i:])
            print(f"\n{CYAN}... and {remaining_clusters} more clusters with {remaining_nodes} nodes{RESET}")
            break
        
        print(f"\n{BOLD}Cluster {i+1} ({len(cluster)} entries):{RESET}")
        
        # Create a mini-graph for this cluster
        cluster_entries = {entry_id: graph.nodes[entry_id] for entry_id in cluster}
        
        # Simple layout: arrange in a rough circle or grid
        if len(cluster) <= 6:
            # Small cluster - show connections clearly
            for j, entry_id in enumerate(cluster):
                entry = cluster_entries[entry_id]
                color = type_colors.get(entry.type, RESET)
                
                # Show node
                content_preview = entry.content[:30] + '...' if len(entry.content) > 30 else entry.content
                print(f"    {color}●{RESET} {BLUE}{entry.id}{RESET} - {content_preview}")
                
                # Show connections to other nodes in this cluster
                connections = graph.get_related_entries(entry_id)
                cluster_connections = [(conn_id, info) for conn_id, info in connections if conn_id in cluster]
                
                if cluster_connections:
                    for conn_id, info in cluster_connections[:3]:  # Limit connections shown
                        strength = info['strength']
                        conn_entry = graph.nodes[conn_id]
                        conn_color = type_colors.get(conn_entry.type, RESET)
                        
                        # Connection visualization
                        if strength >= 0.5:
                            line = "━━━"
                        elif strength >= 0.3:
                            line = "───"
                        else:
                            line = "···"
                        
                        print(f"      ├{line}► {conn_color}●{RESET} {conn_id} (strength: {strength:.2f})")
        else:
            # Large cluster - show summary
            type_counts = Counter(cluster_entries[entry_id].type for entry_id in cluster)
            print(f"    {BLUE}Types:{RESET}", end=" ")
            for entry_type, count in type_counts.items():
                color = type_colors.get(entry_type, RESET)
                print(f"{color}{entry_type}({count}){RESET}", end="  ")
            print()
            
            # Show most connected nodes in cluster
            cluster_degrees = []
            for entry_id in cluster:
                connections = [conn_id for conn_id, _ in graph.edges[entry_id] if conn_id in cluster]
                cluster_degrees.append((entry_id, len(connections)))
            
            cluster_degrees.sort(key=lambda x: x[1], reverse=True)
            
            print(f"    {BLUE}Central nodes:{RESET}")
            for entry_id, degree in cluster_degrees[:3]:
                entry = cluster_entries[entry_id]
                color = type_colors.get(entry.type, RESET)
                content_preview = entry.content[:25] + '...' if len(entry.content) > 25 else entry.content
                print(f"      {color}●{RESET} {entry_id} - {content_preview} ({degree} connections)")
        
        nodes_shown += len(cluster)
    
    # Network statistics
    stats = graph.get_network_stats()
    print(f"\n{BOLD}{GREEN}📊 Network Statistics{RESET}")
    print(f"{CYAN}{'─' * 50}{RESET}")
    print(f"  Nodes: {stats['total_nodes']}")
    print(f"  Connections: {stats['total_edges']}")
    print(f"  Density: {stats['density']:.3f}")
    print(f"  Clusters: {stats['clusters']}")
    print(f"  Largest cluster: {stats['largest_cluster_size']} nodes")
    
    print(f"\n{BOLD}{CYAN}{'═' * 80}{RESET}")


def cmd_graph(args: List[str]):
    """Show ASCII knowledge graph visualization."""
    brain = BrainManager()
    graph = KnowledgeGraph(brain)
    
    max_nodes = 20
    if args and args[0].isdigit():
        max_nodes = int(args[0])
    
    print_ascii_graph(graph, max_nodes)


def cmd_related(args: List[str]):
    """Find entries related to a specific entry."""
    if not args:
        print("Usage: python brain_graph.py related <entry_id>")
        return
    
    entry_id = args[0]
    brain = BrainManager()
    
    if entry_id not in brain.entries:
        print(f"❌ Entry '{entry_id}' not found")
        return
    
    graph = KnowledgeGraph(brain)
    related = graph.get_related_entries(entry_id, limit=10)
    
    # Color codes
    BOLD = '\033[1m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    
    print(f"\n{BOLD}{CYAN}🔗 RELATED KNOWLEDGE{RESET}")
    print(f"{CYAN}{'═' * 60}{RESET}")
    
    source_entry = brain.entries[entry_id]
    print(f"{BOLD}Source:{RESET} {BLUE}{entry_id}{RESET} - {source_entry.content[:50]}...")
    
    if not related:
        print(f"\n{YELLOW}No related entries found. This entry is isolated.{RESET}")
        return
    
    print(f"\n{BOLD}Related entries (by relevance):{RESET}")
    
    for i, (related_id, connection_info) in enumerate(related, 1):
        related_entry = brain.entries[related_id]
        strength = connection_info['strength']
        
        # Strength visualization
        strength_bar = '█' * int(strength * 10) + '░' * (10 - int(strength * 10))
        
        print(f"\n{YELLOW}{i:2}.{RESET} {strength_bar} {GREEN}{strength:.3f}{RESET}")
        print(f"    {BLUE}{related_id}{RESET} - {related_entry.content[:60]}...")
        
        # Connection analysis
        reasons = []
        if connection_info['content_sim'] > 0.1:
            reasons.append(f"content similarity ({connection_info['content_sim']:.2f})")
        if connection_info['tag_sim'] > 0.1:
            reasons.append(f"shared tags ({connection_info['tag_sim']:.2f})")
        if connection_info['type_affinity'] > 0.1:
            reasons.append(f"type affinity ({connection_info['type_affinity']:.2f})")
        if connection_info['temporal_affinity'] > 0.1:
            reasons.append(f"temporal proximity ({connection_info['temporal_affinity']:.2f})")
        
        if reasons:
            print(f"    {CYAN}└─ Connected by: {', '.join(reasons)}{RESET}")


def cmd_cluster(args: List[str]):
    """Group similar knowledge into clusters."""
    brain = BrainManager()
    graph = KnowledgeGraph(brain)
    clusters = graph.get_clusters()
    
    # Color codes
    BOLD = '\033[1m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    RED = '\033[91m'
    RESET = '\033[0m'
    
    print(f"\n{BOLD}{CYAN}🗂️  KNOWLEDGE CLUSTERING{RESET}")
    print(f"{CYAN}{'═' * 60}{RESET}")
    
    if not clusters:
        print(f"{RED}❌ No clusters found{RESET}")
        return
    
    print(f"Found {BOLD}{len(clusters)}{RESET} clusters:")
    
    for i, cluster in enumerate(clusters, 1):
        cluster_entries = [brain.entries[entry_id] for entry_id in cluster]
        
        # Analyze cluster characteristics
        types = [entry.type for entry in cluster_entries]
        type_counts = Counter(types)
        dominant_type = type_counts.most_common(1)[0][0]
        
        # Common tags
        all_tags = []
        for entry in cluster_entries:
            all_tags.extend(entry.tags)
        common_tags = [tag for tag, count in Counter(all_tags).most_common(3)]
        
        # Size indicator
        if len(cluster) == 1:
            size_indicator = "📄"
            cluster_type = "Isolated"
        elif len(cluster) <= 3:
            size_indicator = "📊"
            cluster_type = "Small"
        elif len(cluster) <= 6:
            size_indicator = "📈"
            cluster_type = "Medium"
        else:
            size_indicator = "📋"
            cluster_type = "Large"
        
        print(f"\n{size_indicator} {BOLD}Cluster {i}{RESET} ({YELLOW}{cluster_type}{RESET} - {len(cluster)} entries)")
        print(f"    {BLUE}Dominant type:{RESET} {dominant_type}")
        if common_tags:
            print(f"    {BLUE}Common tags:{RESET} {', '.join(common_tags)}")
        
        print(f"    {GREEN}Entries:{RESET}")
        for entry_id in cluster:
            entry = brain.entries[entry_id]
            content_preview = entry.content[:40] + '...' if len(entry.content) > 40 else entry.content
            status_icon = {"TESTED": "✅", "EXPERIMENTAL": "🧪", "DEPRECATED": "❌"}.get(entry.status, "❓")
            print(f"      {status_icon} {BLUE}{entry_id}{RESET} - {content_preview}")


def cmd_connections(args: List[str]):
    """Detailed connection analysis for an entry."""
    if not args:
        print("Usage: python brain_graph.py connections <entry_id>")
        return
    
    entry_id = args[0]
    brain = BrainManager()
    
    if entry_id not in brain.entries:
        print(f"❌ Entry '{entry_id}' not found")
        return
    
    graph = KnowledgeGraph(brain)
    entry = brain.entries[entry_id]
    
    # Color codes  
    BOLD = '\033[1m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    
    print(f"\n{BOLD}{CYAN}🔍 DETAILED CONNECTION ANALYSIS{RESET}")
    print(f"{CYAN}{'═' * 70}{RESET}")
    
    print(f"{BOLD}Entry:{RESET} {BLUE}{entry_id}{RESET}")
    print(f"{BOLD}Type:{RESET} {entry.type}")
    print(f"{BOLD}Status:{RESET} {entry.status}")
    print(f"{BOLD}Content:{RESET} {entry.content}")
    if entry.context:
        print(f"{BOLD}Context:{RESET} {entry.context}")
    if entry.tags:
        print(f"{BOLD}Tags:{RESET} {', '.join(entry.tags)}")
    
    related = graph.get_related_entries(entry_id)
    
    if not related:
        print(f"\n{YELLOW}🏝️  This entry is isolated - no strong connections found{RESET}")
        
        # Suggest potential connections
        print(f"\n{CYAN}💡 Suggestions to improve connectivity:{RESET}")
        print(f"  • Add more descriptive tags")
        print(f"  • Include context that relates to other entries")
        print(f"  • Reference specific patterns or lessons")
        return
    
    print(f"\n{BOLD}{GREEN}Connected to {len(related)} entries:{RESET}")
    
    # Group connections by strength
    strong_connections = [(rid, info) for rid, info in related if info['strength'] >= 0.4]
    medium_connections = [(rid, info) for rid, info in related if 0.2 <= info['strength'] < 0.4]
    weak_connections = [(rid, info) for rid, info in related if info['strength'] < 0.2]
    
    for category, connections, icon in [
        ("Strong", strong_connections, "🔗"),
        ("Medium", medium_connections, "🔸"),
        ("Weak", weak_connections, "⚪")
    ]:
        if not connections:
            continue
        
        print(f"\n{icon} {BOLD}{category} Connections ({len(connections)}):{RESET}")
        
        for related_id, connection_info in connections:
            related_entry = brain.entries[related_id]
            strength = connection_info['strength']
            
            print(f"   {BLUE}{related_id}{RESET} - {related_entry.content[:45]}...")
            print(f"   └─ {GREEN}Strength: {strength:.3f}{RESET}")
            
            # Detailed breakdown
            details = []
            if connection_info['content_sim'] > 0.05:
                details.append(f"Content: {connection_info['content_sim']:.3f}")
            if connection_info['tag_sim'] > 0.05:
                details.append(f"Tags: {connection_info['tag_sim']:.3f}")
            if connection_info['type_affinity'] > 0.05:
                details.append(f"Type: {connection_info['type_affinity']:.3f}")
            if connection_info['temporal_affinity'] > 0.05:
                details.append(f"Time: {connection_info['temporal_affinity']:.3f}")
            
            if details:
                print(f"      {CYAN}{' • '.join(details)}{RESET}")
    
    # Network position analysis
    degree = len(related)
    avg_strength = sum(info['strength'] for _, info in related) / len(related)
    
    print(f"\n{BOLD}{YELLOW}📊 Network Position Analysis:{RESET}")
    print(f"  Connection degree: {degree}")
    print(f"  Average connection strength: {avg_strength:.3f}")
    
    if degree >= 5:
        print(f"  {GREEN}🌟 This is a highly connected hub entry{RESET}")
    elif degree >= 3:
        print(f"  {BLUE}🔗 This entry is well-connected{RESET}")
    elif degree >= 1:
        print(f"  {YELLOW}📎 This entry has some connections{RESET}")


def cmd_network_stats(args: List[str]):
    """Show detailed network statistics."""
    brain = BrainManager()
    graph = KnowledgeGraph(brain)
    stats = graph.get_network_stats()
    
    # Color codes
    BOLD = '\033[1m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    
    print(f"\n{BOLD}{CYAN}📈 KNOWLEDGE NETWORK STATISTICS{RESET}")
    print(f"{CYAN}{'═' * 60}{RESET}")
    
    print(f"{BOLD}Basic Metrics:{RESET}")
    print(f"  Total entries (nodes): {stats['total_nodes']}")
    print(f"  Total connections (edges): {stats['total_edges']}")
    print(f"  Average connections per entry: {stats['average_degree']:.1f}")
    print(f"  Max connections (highest degree): {stats['max_degree']}")
    print(f"  Network density: {stats['density']:.3f}")
    
    print(f"\n{BOLD}Clustering:{RESET}")
    print(f"  Number of clusters: {stats['clusters']}")
    print(f"  Largest cluster size: {stats['largest_cluster_size']}")
    
    if stats['most_connected']:
        print(f"\n{BOLD}{GREEN}🌟 Most Connected Entries:{RESET}")
        for i, (entry_id, degree, avg_strength) in enumerate(stats['most_connected'], 1):
            entry = brain.entries[entry_id]
            content_preview = entry.content[:40] + '...' if len(entry.content) > 40 else entry.content
            print(f"  {YELLOW}{i}.{RESET} {BLUE}{entry_id}{RESET} - {content_preview}")
            print(f"     {degree} connections, avg strength: {avg_strength:.3f}")
    
    # Type connectivity analysis
    print(f"\n{BOLD}{GREEN}🔗 Type Connectivity Matrix:{RESET}")
    type_connections = defaultdict(lambda: defaultdict(int))
    
    for entry1_id, connections in graph.edges.items():
        entry1 = graph.nodes[entry1_id]
        for entry2_id, connection_info in connections:
            entry2 = graph.nodes[entry2_id]
            type_connections[entry1.type][entry2.type] += 1
    
    # Show as a simple matrix
    types = list(ENTRY_TYPES.keys())
    print(f"  {'':<12}", end="")
    for t in types:
        print(f"{t[:8]:>8}", end="")
    print()
    
    for type1 in types:
        print(f"  {type1:<12}", end="")
        for type2 in types:
            count = type_connections[type1][type2]
            print(f"{count:>8}", end="")
        print()


def cmd_export_graph(args: List[str]):
    """Export the knowledge graph as JSON."""
    brain = BrainManager()
    graph = KnowledgeGraph(brain)
    
    # Prepare export data
    export_data = {
        'metadata': {
            'exported_at': datetime.now().isoformat(),
            'total_nodes': len(graph.nodes),
            'total_edges': sum(len(connections) for connections in graph.edges.values()) // 2,
        },
        'nodes': [],
        'edges': []
    }
    
    # Export nodes
    for entry_id, entry in graph.nodes.items():
        export_data['nodes'].append({
            'id': entry_id,
            'type': entry.type,
            'content': entry.content,
            'context': entry.context,
            'status': entry.status,
            'tags': entry.tags,
            'date_added': entry.date_added,
            'date_updated': entry.date_updated
        })
    
    # Export edges (avoid duplicates)
    processed_pairs = set()
    for entry_id, connections in graph.edges.items():
        for connected_id, connection_info in connections:
            # Create a sorted tuple to avoid duplicates
            pair = tuple(sorted([entry_id, connected_id]))
            if pair not in processed_pairs:
                processed_pairs.add(pair)
                export_data['edges'].append({
                    'source': pair[0],
                    'target': pair[1],
                    'strength': connection_info['strength'],
                    'content_similarity': connection_info['content_sim'],
                    'tag_similarity': connection_info['tag_sim'],
                    'type_affinity': connection_info['type_affinity'],
                    'temporal_affinity': connection_info['temporal_affinity']
                })
    
    # Write to file
    mywork_root = get_mywork_root()
    export_file = mywork_root / f"brain_graph_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(export_file, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    print(f"✅ Knowledge graph exported to: {export_file}")
    print(f"📊 Exported {export_data['metadata']['total_nodes']} nodes and {export_data['metadata']['total_edges']} edges")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    
    command = sys.argv[1].lower()
    args = sys.argv[2:]
    
    commands = {
        'graph': cmd_graph,
        'related': cmd_related,
        'cluster': cmd_cluster,
        'connections': cmd_connections,
        'network-stats': cmd_network_stats,
        'export-graph': cmd_export_graph,
    }
    
    if command in commands:
        commands[command](args)
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()