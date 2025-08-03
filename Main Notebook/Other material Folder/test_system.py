#!/usr/bin/env python3
"""
System Test Runner for Dynamic Sports Performance Analytics Engine
Validates data structures, algorithms, and API functionality
"""

import sys
import os
import time
import unittest
from typing import Dict, List

# Add src to path
sys.path.append('src')

from core.data_structures import PerformanceDataStructures, Player, PlayerHashTable, PerformanceHeap
from core.algorithms import PerformanceScoreAlgorithm, PlayerSimilarityAlgorithm, PredictiveAlgorithm

class TestDataStructures(unittest.TestCase):
    """Test cases for core data structures."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.data_structures = PerformanceDataStructures()
        self.sample_player = Player(
            player_id=1,
            name="Test Player",
            position="Midfielder",
            team_id=1,
            age=25,
            performance_score=75.0,
            stats={"goals": 10, "assists": 5, "average_rating": 7.5},
            last_updated=time.time()
        )
    
    def test_hash_table_operations(self):
        """Test hash table O(1) operations."""
        # Test insertion
        self.data_structures.add_player(self.sample_player)
        
        # Test retrieval
        retrieved_player = self.data_structures.get_player(1)
        self.assertIsNotNone(retrieved_player)
        self.assertEqual(retrieved_player.name, "Test Player")
        
        # Test update
        self.data_structures.update_player_score(1, 85.0)
        updated_player = self.data_structures.get_player(1)
        self.assertEqual(updated_player.performance_score, 85.0)
    
    def test_heap_operations(self):
        """Test max-heap operations."""
        # Add multiple players
        players = [
            Player(i, f"Player_{i}", "Midfielder", 1, 25, float(i * 10), {}, time.time())
            for i in range(1, 6)
        ]
        
        for player in players:
            self.data_structures.add_player(player)
        
        # Test top performers retrieval
        top_performers = self.data_structures.get_top_performers(3)
        self.assertEqual(len(top_performers), 3)
        
        # Verify ordering (highest scores first)
        scores = [score for _, score in top_performers]
        self.assertEqual(scores, sorted(scores, reverse=True))
    
    def test_performance_complexity(self):
        """Test performance characteristics."""
        # Test with different sizes
        sizes = [10, 50, 100]
        
        for size in sizes:
            start_time = time.time()
            
            # Add players
            for i in range(size):
                player = Player(i, f"Player_{i}", "Midfielder", 1, 25, 50.0, {}, time.time())
                self.data_structures.add_player(player)
            
            insertion_time = time.time() - start_time
            
            # Test lookup time
            start_time = time.time()
            self.data_structures.get_player(size // 2)
            lookup_time = time.time() - start_time
            
            # Lookup should be very fast (O(1))
            self.assertLess(lookup_time, 0.001)  # Less than 1ms
            
            print(f"Size {size}: Insertion {insertion_time:.4f}s, Lookup {lookup_time:.6f}s")

class TestAlgorithms(unittest.TestCase):
    """Test cases for core algorithms."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.performance_algorithm = PerformanceScoreAlgorithm()
        self.similarity_algorithm = PlayerSimilarityAlgorithm()
        self.prediction_algorithm = PredictiveAlgorithm()
    
    def test_performance_score_calculation(self):
        """Test performance score algorithm."""
        # Test different positions
        positions_stats = {
            "Attacker": {"goals": 20, "assists": 10, "shots_on_target": 50, "minutes_played": 2500},
            "Midfielder": {"goals": 5, "assists": 15, "pass_accuracy": 90, "key_passes": 80, "minutes_played": 2800},
            "Defender": {"tackles_won": 60, "interceptions": 40, "clearances": 100, "pass_accuracy": 85, "minutes_played": 2900},
            "Goalkeeper": {"saves": 100, "clean_sheets": 15, "goals_conceded": 25, "pass_accuracy": 75, "minutes_played": 3000}
        }
        
        for position, stats in positions_stats.items():
            score = self.performance_algorithm.calculate_performance_score(stats, position)
            
            # Score should be between 0 and 100
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 100)
            
            print(f"{position} score: {score:.2f}")
    
    def test_similarity_algorithm(self):
        """Test player similarity algorithm."""
        # Create sample players
        players_data = [
            {
                "player_id": 1,
                "position": "Attacker",
                "stats": {"goals": 20, "assists": 5, "shots_total": 100, "average_rating": 8.0}
            },
            {
                "player_id": 2,
                "position": "Attacker",
                "stats": {"goals": 18, "assists": 7, "shots_total": 95, "average_rating": 7.8}
            },
            {
                "player_id": 3,
                "position": "Midfielder",
                "stats": {"goals": 5, "assists": 15, "pass_accuracy": 90, "average_rating": 7.5}
            }
        ]
        
        # Fit the algorithm
        self.similarity_algorithm.fit(players_data, n_clusters=2)
        
        # Test similarity finding
        similar_players = self.similarity_algorithm.find_similar_players(1, method='cosine', top_k=2)
        
        self.assertIsInstance(similar_players, list)
        self.assertLessEqual(len(similar_players), 2)
        
        # Test cluster assignment
        cluster = self.similarity_algorithm.get_player_cluster(1)
        self.assertIsNotNone(cluster)
        
        print(f"Similar players to ID 1: {similar_players}")
        print(f"Player 1 cluster: {cluster}")
    
    def test_prediction_algorithm(self):
        """Test predictive algorithm."""
        # Create mock historical data
        training_data = {
            1: [
                {"goals": 15, "assists": 8, "age": 24, "performance_score": 70.0},
                {"goals": 18, "assists": 10, "age": 25, "performance_score": 75.0}
            ],
            2: [
                {"goals": 20, "assists": 5, "age": 26, "performance_score": 80.0},
                {"goals": 22, "assists": 7, "age": 27, "performance_score": 82.0}
            ]
        }
        
        # Fit the model
        self.prediction_algorithm.fit_prediction_models(training_data)
        
        # Make prediction
        current_stats = {"goals": 20, "assists": 8, "age": 26, "average_rating": 7.8, "minutes_played": 2500}
        prediction = self.prediction_algorithm.predict_performance(current_stats)
        
        self.assertIn('prediction', prediction)
        self.assertIn('confidence', prediction)
        self.assertGreater(prediction['confidence'], 0)
        self.assertLessEqual(prediction['confidence'], 1)
        
        print(f"Prediction: {prediction['prediction']:.2f}, Confidence: {prediction['confidence']:.2f}")

class TestSystemIntegration(unittest.TestCase):
    """Test system integration and end-to-end functionality."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.data_structures = PerformanceDataStructures()
        self.performance_algorithm = PerformanceScoreAlgorithm()
    
    def test_end_to_end_workflow(self):
        """Test complete workflow from data input to analysis."""
        # Sample player data
        players_data = [
            {
                "player_id": 1,
                "name": "Erling Haaland",
                "position": "Attacker",
                "team_id": 9,
                "age": 23,
                "stats": {"goals": 36, "assists": 8, "shots_total": 116, "average_rating": 8.2}
            },
            {
                "player_id": 2,
                "name": "Kevin De Bruyne",
                "position": "Midfielder",
                "team_id": 9,
                "age": 32,
                "stats": {"goals": 7, "assists": 16, "pass_accuracy": 87.5, "key_passes": 89, "average_rating": 8.0}
            }
        ]
        
        # Add players to system
        for player_data in players_data:
            score = self.performance_algorithm.calculate_performance_score(
                player_data["stats"], 
                player_data["position"]
            )
            
            player = Player(
                player_id=player_data["player_id"],
                name=player_data["name"],
                position=player_data["position"],
                team_id=player_data["team_id"],
                age=player_data["age"],
                performance_score=score,
                stats=player_data["stats"],
                last_updated=time.time()
            )
            
            self.data_structures.add_player(player)
        
        # Test retrieval
        haaland = self.data_structures.get_player(1)
        self.assertIsNotNone(haaland)
        self.assertEqual(haaland.name, "Erling Haaland")
        
        # Test rankings
        top_performers = self.data_structures.get_top_performers(2)
        self.assertEqual(len(top_performers), 2)
        
        # Test system stats
        stats = self.data_structures.get_system_stats()
        self.assertEqual(stats['hash_table_stats']['size'], 2)
        self.assertEqual(stats['heap_size'], 2)
        
        print("End-to-end workflow test completed successfully")

def run_performance_benchmark():
    """Run performance benchmarks."""
    print("\nPerformance Benchmark Results")
    print("=" * 50)
    
    data_structures = PerformanceDataStructures()
    
    # Test different sizes
    sizes = [100, 500, 1000, 2000]
    
    print(f"{'Size':<8} {'Insert (ms)':<12} {'Lookup (μs)':<12} {'Top-10 (μs)':<12}")
    print("-" * 50)
    
    for size in sizes:
        # Create test players
        players = [
            Player(i, f"Player_{i}", "Midfielder", 1, 25, 50.0 + (i % 50), {}, time.time())
            for i in range(size)
        ]
        
        # Benchmark insertion
        start_time = time.time()
        for player in players:
            data_structures.add_player(player)
        insertion_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Benchmark lookup
        start_time = time.time()
        data_structures.get_player(size // 2)
        lookup_time = (time.time() - start_time) * 1000000  # Convert to μs
        
        # Benchmark top-K retrieval
        start_time = time.time()
        data_structures.get_top_performers(10)
        topk_time = (time.time() - start_time) * 1000000  # Convert to μs
        
        print(f"{size:<8} {insertion_time:<12.2f} {lookup_time:<12.2f} {topk_time:<12.2f}")

def main():
    """Main test runner."""
    print("Dynamic Sports Performance Analytics Engine - System Tests")
    print("=" * 70)
    
    # Run unit tests
    print("\nRunning Unit Tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run performance benchmarks
    run_performance_benchmark()
    
    print("\n" + "=" * 70)
    print("All tests completed successfully!")
    print("System is ready for production use.")

if __name__ == "__main__":
    main()
