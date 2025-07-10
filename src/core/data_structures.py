#!/usr/bin/env python3
"""
Core Data Structures for Dynamic Sports Performance Analytics Engine
Optimized data structures for O(1) lookups, O(log n) rankings, and graph-based relationships
"""

import heapq
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict, deque
import json
import time

@dataclass
class Player:
    """Player data structure with comprehensive performance metrics."""
    player_id: int
    name: str
    position: str
    team_id: int
    age: int
    performance_score: float
    stats: Dict[str, float]
    last_updated: float
    
    def __hash__(self):
        return hash(self.player_id)
    
    def __eq__(self, other):
        return isinstance(other, Player) and self.player_id == other.player_id

class PlayerHashTable:
    """
    Hash table implementation for O(1) player data retrieval.
    Uses separate chaining for collision resolution.
    """
    
    def __init__(self, initial_capacity: int = 1000):
        self.capacity = initial_capacity
        self.size = 0
        self.buckets = [[] for _ in range(self.capacity)]
        self.load_factor_threshold = 0.75
    
    def _hash(self, player_id: int) -> int:
        """Hash function using division method with prime number."""
        return player_id % self.capacity
    
    def _resize(self):
        """Resize hash table when load factor exceeds threshold."""
        old_buckets = self.buckets
        self.capacity *= 2
        self.size = 0
        self.buckets = [[] for _ in range(self.capacity)]
        
        # Rehash all existing players
        for bucket in old_buckets:
            for player in bucket:
                self.insert(player)
    
    def insert(self, player: Player):
        """Insert player with O(1) average time complexity."""
        if self.size >= self.capacity * self.load_factor_threshold:
            self._resize()
        
        index = self._hash(player.player_id)
        bucket = self.buckets[index]
        
        # Update existing player
        for i, existing_player in enumerate(bucket):
            if existing_player.player_id == player.player_id:
                bucket[i] = player
                return
        
        # Insert new player
        bucket.append(player)
        self.size += 1
    
    def get(self, player_id: int) -> Optional[Player]:
        """Retrieve player with O(1) average time complexity."""
        index = self._hash(player_id)
        bucket = self.buckets[index]
        
        for player in bucket:
            if player.player_id == player_id:
                return player
        return None
    
    def delete(self, player_id: int) -> bool:
        """Delete player with O(1) average time complexity."""
        index = self._hash(player_id)
        bucket = self.buckets[index]
        
        for i, player in enumerate(bucket):
            if player.player_id == player_id:
                del bucket[i]
                self.size -= 1
                return True
        return False
    
    def get_all_players(self) -> List[Player]:
        """Return all players in the hash table."""
        players = []
        for bucket in self.buckets:
            players.extend(bucket)
        return players
    
    def get_stats(self) -> Dict[str, Any]:
        """Get hash table performance statistics."""
        bucket_sizes = [len(bucket) for bucket in self.buckets]
        return {
            'size': self.size,
            'capacity': self.capacity,
            'load_factor': self.size / self.capacity,
            'max_bucket_size': max(bucket_sizes) if bucket_sizes else 0,
            'avg_bucket_size': sum(bucket_sizes) / len(bucket_sizes) if bucket_sizes else 0
        }

class PerformanceHeap:
    """
    Max-heap implementation for maintaining top K player rankings.
    Provides O(log n) insertion and O(1) access to top performer.
    """
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.heap = []  # List of (-score, timestamp, player_id) tuples
        self.player_positions = {}  # Maps player_id to heap index
    
    def _parent(self, index: int) -> int:
        return (index - 1) // 2
    
    def _left_child(self, index: int) -> int:
        return 2 * index + 1
    
    def _right_child(self, index: int) -> int:
        return 2 * index + 2
    
    def _swap(self, i: int, j: int):
        """Swap elements and update position tracking."""
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
        
        # Update position tracking
        _, _, player_id_i = self.heap[i]
        _, _, player_id_j = self.heap[j]
        self.player_positions[player_id_i] = i
        self.player_positions[player_id_j] = j
    
    def _heapify_up(self, index: int):
        """Maintain heap property upward."""
        while index > 0:
            parent_index = self._parent(index)
            if self.heap[index][0] <= self.heap[parent_index][0]:
                break
            self._swap(index, parent_index)
            index = parent_index
    
    def _heapify_down(self, index: int):
        """Maintain heap property downward."""
        while True:
            largest = index
            left = self._left_child(index)
            right = self._right_child(index)
            
            if left < len(self.heap) and self.heap[left][0] > self.heap[largest][0]:
                largest = left
            
            if right < len(self.heap) and self.heap[right][0] > self.heap[largest][0]:
                largest = right
            
            if largest == index:
                break
            
            self._swap(index, largest)
            index = largest
    
    def insert_or_update(self, player_id: int, score: float):
        """Insert new player or update existing player's score."""
        timestamp = time.time()
        
        # Check if player already exists
        if player_id in self.player_positions:
            # Update existing player
            index = self.player_positions[player_id]
            old_score = -self.heap[index][0]
            self.heap[index] = (-score, timestamp, player_id)
            
            # Maintain heap property
            if score > old_score:
                self._heapify_up(index)
            else:
                self._heapify_down(index)
        else:
            # Insert new player
            if len(self.heap) < self.max_size:
                # Heap not full, just add
                self.heap.append((-score, timestamp, player_id))
                index = len(self.heap) - 1
                self.player_positions[player_id] = index
                self._heapify_up(index)
            else:
                # Heap full, check if new score is better than worst
                worst_score = -self.heap[0][0]
                if score > worst_score:
                    # Remove worst player
                    _, _, worst_player_id = self.heap[0]
                    del self.player_positions[worst_player_id]
                    
                    # Replace with new player
                    self.heap[0] = (-score, timestamp, player_id)
                    self.player_positions[player_id] = 0
                    self._heapify_down(0)
    
    def get_top_k(self, k: int) -> List[Tuple[int, float]]:
        """Get top K players as (player_id, score) tuples."""
        # Create a copy and sort to maintain heap structure
        heap_copy = [(-score, timestamp, player_id) for score, timestamp, player_id in self.heap]
        heap_copy.sort(reverse=True)  # Sort by score descending
        
        result = []
        for i in range(min(k, len(heap_copy))):
            score, _, player_id = heap_copy[i]
            result.append((player_id, -score))
        
        return result
    
    def get_player_rank(self, player_id: int) -> Optional[int]:
        """Get the rank of a specific player (1-indexed)."""
        if player_id not in self.player_positions:
            return None
        
        player_score = -self.heap[self.player_positions[player_id]][0]
        rank = 1
        
        for score, _, _ in self.heap:
            if -score > player_score:
                rank += 1
        
        return rank
    
    def size(self) -> int:
        """Return current heap size."""
        return len(self.heap)

class PlayerRelationshipGraph:
    """
    Graph data structure for modeling player and team relationships.
    Supports PageRank algorithm and shortest path calculations.
    """
    
    def __init__(self):
        self.adjacency_list = defaultdict(list)
        self.nodes = set()
        self.edge_weights = {}
    
    def add_node(self, node_id: int, node_type: str, metadata: Dict = None):
        """Add a node (player or team) to the graph."""
        self.nodes.add(node_id)
        if metadata:
            setattr(self, f"metadata_{node_id}", metadata)
    
    def add_edge(self, from_node: int, to_node: int, weight: float = 1.0, relationship_type: str = ""):
        """Add weighted edge between nodes."""
        self.adjacency_list[from_node].append(to_node)
        self.edge_weights[(from_node, to_node)] = weight
        
        if relationship_type:
            setattr(self, f"edge_type_{from_node}_{to_node}", relationship_type)
    
    def get_neighbors(self, node_id: int) -> List[int]:
        """Get all neighbors of a node."""
        return self.adjacency_list[node_id]
    
    def shortest_path(self, start: int, end: int) -> Optional[List[int]]:
        """Find shortest path between two nodes using BFS."""
        if start not in self.nodes or end not in self.nodes:
            return None
        
        if start == end:
            return [start]
        
        queue = deque([(start, [start])])
        visited = {start}
        
        while queue:
            current, path = queue.popleft()
            
            for neighbor in self.adjacency_list[current]:
                if neighbor == end:
                    return path + [neighbor]
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None  # No path found
    
    def pagerank(self, damping_factor: float = 0.85, max_iterations: int = 100, tolerance: float = 1e-6) -> Dict[int, float]:
        """
        Calculate PageRank scores for all nodes.
        Higher scores indicate more influential players/teams.
        """
        if not self.nodes:
            return {}
        
        # Initialize PageRank values
        num_nodes = len(self.nodes)
        pagerank_scores = {node: 1.0 / num_nodes for node in self.nodes}
        
        for iteration in range(max_iterations):
            new_scores = {}
            
            for node in self.nodes:
                # Base score from damping factor
                new_score = (1 - damping_factor) / num_nodes
                
                # Add contributions from incoming links
                for other_node in self.nodes:
                    if node in self.adjacency_list[other_node]:
                        out_degree = len(self.adjacency_list[other_node])
                        if out_degree > 0:
                            weight = self.edge_weights.get((other_node, node), 1.0)
                            new_score += damping_factor * (pagerank_scores[other_node] * weight) / out_degree
                
                new_scores[node] = new_score
            
            # Check for convergence
            max_change = max(abs(new_scores[node] - pagerank_scores[node]) for node in self.nodes)
            if max_change < tolerance:
                break
            
            pagerank_scores = new_scores
        
        return pagerank_scores
    
    def get_node_influence(self, node_id: int) -> float:
        """Get influence score for a specific node."""
        pagerank_scores = self.pagerank()
        return pagerank_scores.get(node_id, 0.0)
    
    def get_connection_strength(self, node1: int, node2: int) -> float:
        """Calculate connection strength between two nodes."""
        path = self.shortest_path(node1, node2)
        if not path:
            return 0.0
        
        # Shorter paths indicate stronger connections
        path_length = len(path) - 1
        return 1.0 / (path_length + 1) if path_length > 0 else 1.0

class PerformanceDataStructures:
    """
    Main container class that orchestrates all data structures.
    Provides unified interface for the analytics engine.
    """
    
    def __init__(self, hash_table_capacity: int = 1000, heap_size: int = 100):
        self.player_hash_table = PlayerHashTable(hash_table_capacity)
        self.performance_heap = PerformanceHeap(heap_size)
        self.relationship_graph = PlayerRelationshipGraph()
        self.last_update = time.time()
    
    def add_player(self, player: Player):
        """Add player to all relevant data structures."""
        self.player_hash_table.insert(player)
        self.performance_heap.insert_or_update(player.player_id, player.performance_score)
        self.relationship_graph.add_node(player.player_id, "player", {
            'name': player.name,
            'position': player.position,
            'team_id': player.team_id
        })
        self.last_update = time.time()
    
    def update_player_score(self, player_id: int, new_score: float):
        """Update player's performance score across all structures."""
        player = self.player_hash_table.get(player_id)
        if player:
            player.performance_score = new_score
            player.last_updated = time.time()
            self.performance_heap.insert_or_update(player_id, new_score)
            self.last_update = time.time()
    
    def get_player(self, player_id: int) -> Optional[Player]:
        """Get player data with O(1) lookup."""
        return self.player_hash_table.get(player_id)
    
    def get_top_performers(self, k: int) -> List[Tuple[Player, float]]:
        """Get top K performing players."""
        top_player_ids = self.performance_heap.get_top_k(k)
        result = []
        
        for player_id, score in top_player_ids:
            player = self.player_hash_table.get(player_id)
            if player:
                result.append((player, score))
        
        return result
    
    def add_player_relationship(self, player1_id: int, player2_id: int, relationship_type: str, weight: float = 1.0):
        """Add relationship between players in the graph."""
        self.relationship_graph.add_edge(player1_id, player2_id, weight, relationship_type)
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        return {
            'hash_table_stats': self.player_hash_table.get_stats(),
            'heap_size': self.performance_heap.size(),
            'graph_nodes': len(self.relationship_graph.nodes),
            'graph_edges': sum(len(neighbors) for neighbors in self.relationship_graph.adjacency_list.values()),
            'last_update': self.last_update
        }
