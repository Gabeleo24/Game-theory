#!/usr/bin/env python3
"""
Demonstration Script for Dynamic Sports Performance Analytics Engine
Shows the core data structures, algorithms, and API functionality
"""

import sys
import os
import time
import asyncio
from typing import Dict, List

# Add src to path
sys.path.append('src')

from core.data_structures import PerformanceDataStructures, Player
from core.algorithms import PerformanceScoreAlgorithm, PlayerSimilarityAlgorithm, PredictiveAlgorithm

def create_sample_players() -> List[Dict]:
    """Create sample player data for demonstration."""
    return [
        {
            "player_id": 1,
            "name": "Erling Haaland",
            "position": "Attacker",
            "team_id": 9,
            "age": 23,
            "stats": {
                "goals": 36,
                "assists": 8,
                "shots_total": 116,
                "shots_on_target": 68,
                "key_passes": 23,
                "dribbles_successful": 45,
                "minutes_played": 2769,
                "average_rating": 8.2
            }
        },
        {
            "player_id": 2,
            "name": "Kevin De Bruyne",
            "position": "Midfielder",
            "team_id": 9,
            "age": 32,
            "stats": {
                "goals": 7,
                "assists": 16,
                "pass_accuracy": 87.5,
                "key_passes": 89,
                "tackles_won": 34,
                "minutes_played": 2156,
                "average_rating": 8.0
            }
        },
        {
            "player_id": 3,
            "name": "Ruben Dias",
            "position": "Defender",
            "team_id": 9,
            "age": 26,
            "stats": {
                "goals": 2,
                "assists": 1,
                "pass_accuracy": 91.2,
                "tackles_won": 45,
                "interceptions": 52,
                "clearances": 89,
                "minutes_played": 2890,
                "average_rating": 7.8
            }
        },
        {
            "player_id": 4,
            "name": "Ederson",
            "position": "Goalkeeper",
            "team_id": 9,
            "age": 30,
            "stats": {
                "goals": 0,
                "assists": 1,
                "saves": 78,
                "clean_sheets": 18,
                "goals_conceded": 31,
                "pass_accuracy": 84.5,
                "minutes_played": 3060,
                "average_rating": 7.5
            }
        },
        {
            "player_id": 5,
            "name": "Phil Foden",
            "position": "Midfielder",
            "team_id": 9,
            "age": 23,
            "stats": {
                "goals": 11,
                "assists": 8,
                "pass_accuracy": 85.3,
                "key_passes": 67,
                "tackles_won": 28,
                "minutes_played": 2234,
                "average_rating": 7.6
            }
        },
        {
            "player_id": 6,
            "name": "Jack Grealish",
            "position": "Attacker",
            "team_id": 9,
            "age": 28,
            "stats": {
                "goals": 5,
                "assists": 7,
                "shots_total": 45,
                "shots_on_target": 18,
                "key_passes": 34,
                "dribbles_successful": 67,
                "minutes_played": 1876,
                "average_rating": 7.2
            }
        }
    ]

def demonstrate_data_structures():
    """Demonstrate the core data structures and their performance."""
    print("=" * 80)
    print("DATA STRUCTURES DEMONSTRATION")
    print("=" * 80)
    
    # Initialize data structures
    data_structures = PerformanceDataStructures(hash_table_capacity=100, heap_size=10)
    performance_algorithm = PerformanceScoreAlgorithm()
    
    # Create sample players
    sample_players = create_sample_players()
    
    print("\n1. HASH TABLE OPERATIONS (O(1) complexity)")
    print("-" * 50)
    
    # Add players and measure time
    start_time = time.time()
    
    for player_data in sample_players:
        # Calculate performance score
        score = performance_algorithm.calculate_performance_score(
            player_data["stats"], 
            player_data["position"]
        )
        
        # Create player object
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
        
        # Add to data structures
        data_structures.add_player(player)
        print(f"Added: {player.name} (Score: {score:.2f})")
    
    insertion_time = time.time() - start_time
    print(f"\nInsertion time for {len(sample_players)} players: {insertion_time:.4f} seconds")
    
    # Demonstrate O(1) lookup
    print("\n2. PLAYER LOOKUP (O(1) complexity)")
    print("-" * 50)
    
    start_time = time.time()
    player = data_structures.get_player(1)  # Get Haaland
    lookup_time = time.time() - start_time
    
    if player:
        print(f"Found: {player.name} - Performance Score: {player.performance_score:.2f}")
        print(f"Lookup time: {lookup_time:.6f} seconds")
    
    # Demonstrate heap operations
    print("\n3. MAX-HEAP RANKINGS (O(log n) updates, O(1) top access)")
    print("-" * 50)
    
    top_performers = data_structures.get_top_performers(5)
    print("Top 5 Performers:")
    for rank, (player, score) in enumerate(top_performers, 1):
        print(f"  {rank}. {player.name} ({player.position}) - {score:.2f}")
    
    # Update a player's score and show heap update
    print("\nUpdating Phil Foden's performance...")
    start_time = time.time()
    data_structures.update_player_score(5, 85.0)  # Phil Foden
    update_time = time.time() - start_time
    print(f"Heap update time: {update_time:.6f} seconds")
    
    # Show updated rankings
    updated_top = data_structures.get_top_performers(5)
    print("\nUpdated Top 5 Performers:")
    for rank, (player, score) in enumerate(updated_top, 1):
        print(f"  {rank}. {player.name} ({player.position}) - {score:.2f}")
    
    # Show system statistics
    print("\n4. SYSTEM STATISTICS")
    print("-" * 50)
    stats = data_structures.get_system_stats()
    print(f"Hash Table Load Factor: {stats['hash_table_stats']['load_factor']:.3f}")
    print(f"Heap Size: {stats['heap_size']}")
    print(f"Graph Nodes: {stats['graph_nodes']}")
    print(f"Total Players: {stats['hash_table_stats']['size']}")

def demonstrate_algorithms():
    """Demonstrate the custom algorithms."""
    print("\n" + "=" * 80)
    print("ALGORITHMS DEMONSTRATION")
    print("=" * 80)
    
    # Initialize algorithms
    performance_algorithm = PerformanceScoreAlgorithm()
    similarity_algorithm = PlayerSimilarityAlgorithm()
    prediction_algorithm = PredictiveAlgorithm()
    
    sample_players = create_sample_players()
    
    print("\n1. PERFORMANCE SCORE ALGORITHM")
    print("-" * 50)
    
    for player_data in sample_players:
        score = performance_algorithm.calculate_performance_score(
            player_data["stats"], 
            player_data["position"]
        )
        print(f"{player_data['name']} ({player_data['position']}): {score:.2f}")
    
    print("\n2. PLAYER SIMILARITY ALGORITHM")
    print("-" * 50)
    
    # Fit the similarity algorithm
    similarity_algorithm.fit(sample_players, n_clusters=3)
    
    # Find similar players to Haaland
    similar_to_haaland = similarity_algorithm.find_similar_players(1, method='cosine', top_k=3)
    print(f"Players similar to Haaland:")
    for player_id, similarity_score in similar_to_haaland:
        player_name = next(p['name'] for p in sample_players if p['player_id'] == player_id)
        print(f"  {player_name}: {similarity_score:.3f}")
    
    # Show cluster assignments
    print(f"\nCluster assignments:")
    for player_data in sample_players:
        cluster = similarity_algorithm.get_player_cluster(player_data['player_id'])
        print(f"  {player_data['name']}: Cluster {cluster}")
    
    print("\n3. PREDICTIVE ALGORITHM")
    print("-" * 50)
    
    # Create mock historical data for training
    training_data = {}
    for player_data in sample_players:
        # Create 2 seasons of mock data
        training_data[player_data['player_id']] = [
            {**player_data['stats'], 'age': player_data['age'] - 1, 'performance_score': 70.0},
            {**player_data['stats'], 'age': player_data['age'], 'performance_score': 75.0}
        ]
    
    # Fit prediction models
    prediction_algorithm.fit_prediction_models(training_data)
    
    # Make predictions for each player
    for player_data in sample_players:
        current_stats = {**player_data['stats'], 'age': player_data['age']}
        prediction = prediction_algorithm.predict_performance(current_stats)
        print(f"{player_data['name']}: Predicted score {prediction['prediction']:.2f} "
              f"(Confidence: {prediction['confidence']:.1%})")

def demonstrate_complexity_analysis():
    """Demonstrate time complexity with different data sizes."""
    print("\n" + "=" * 80)
    print("COMPLEXITY ANALYSIS DEMONSTRATION")
    print("=" * 80)
    
    data_structures = PerformanceDataStructures()
    performance_algorithm = PerformanceScoreAlgorithm()
    
    # Test with different numbers of players
    test_sizes = [10, 50, 100, 500]
    
    print("\nHash Table Performance (O(1) expected):")
    print("Players\tInsertion Time\tLookup Time")
    print("-" * 40)
    
    for size in test_sizes:
        # Create test players
        test_players = []
        for i in range(size):
            player = Player(
                player_id=i,
                name=f"Player_{i}",
                position="Midfielder",
                team_id=1,
                age=25,
                performance_score=50.0,
                stats={"goals": 5, "assists": 3, "average_rating": 7.0},
                last_updated=time.time()
            )
            test_players.append(player)
        
        # Measure insertion time
        start_time = time.time()
        for player in test_players:
            data_structures.add_player(player)
        insertion_time = time.time() - start_time
        
        # Measure lookup time
        start_time = time.time()
        data_structures.get_player(size // 2)  # Lookup middle player
        lookup_time = time.time() - start_time
        
        print(f"{size}\t{insertion_time:.6f}s\t{lookup_time:.6f}s")
    
    print("\nHeap Performance (O(log n) expected for updates):")
    print("Players\tUpdate Time")
    print("-" * 25)
    
    for size in test_sizes:
        if size <= data_structures.player_hash_table.size:
            start_time = time.time()
            data_structures.update_player_score(size // 2, 85.0)
            update_time = time.time() - start_time
            print(f"{size}\t{update_time:.6f}s")

def main():
    """Main demonstration function."""
    print("DYNAMIC SPORTS PERFORMANCE ANALYTICS ENGINE")
    print("Data Structures, Algorithms, and API Demonstration")
    print("=" * 80)
    
    try:
        # Demonstrate core components
        demonstrate_data_structures()
        demonstrate_algorithms()
        demonstrate_complexity_analysis()
        
        print("\n" + "=" * 80)
        print("DEMONSTRATION COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print("\nNext Steps:")
        print("1. Start the API server: cd src/api && python main.py")
        print("2. Visit http://localhost:8000/docs for API documentation")
        print("3. Test API endpoints with curl or Python requests")
        print("4. Run data ingestion: cd src/ingestion && python data_pipeline.py")
        
    except Exception as e:
        print(f"\nError during demonstration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
