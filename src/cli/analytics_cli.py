#!/usr/bin/env python3
"""
Command Line Interface for Dynamic Sports Performance Analytics Engine
Professional CLI for data structures, algorithms, and API operations
"""

import argparse
import json
import sys
import os
import time
import requests
from typing import Dict, List, Optional

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.data_structures import PerformanceDataStructures, Player
from core.algorithms import PerformanceScoreAlgorithm, PlayerSimilarityAlgorithm, PredictiveAlgorithm

class AnalyticsCLI:
    """Command line interface for the analytics engine."""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.data_structures = PerformanceDataStructures()
        self.performance_algorithm = PerformanceScoreAlgorithm()
        self.similarity_algorithm = PlayerSimilarityAlgorithm()
        self.prediction_algorithm = PredictiveAlgorithm()
    
    def check_api_connection(self) -> bool:
        """Check if API server is running."""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def calculate_performance_score(self, args):
        """Calculate performance score for given stats."""
        stats = {
            'goals': args.goals,
            'assists': args.assists,
            'pass_accuracy': args.pass_accuracy,
            'shots_total': args.shots_total,
            'tackles_won': args.tackles_won,
            'interceptions': args.interceptions,
            'key_passes': args.key_passes,
            'minutes_played': args.minutes_played,
            'average_rating': args.average_rating
        }
        
        score = self.performance_algorithm.calculate_performance_score(stats, args.position)
        
        print(f"Performance Score Calculation")
        print(f"Position: {args.position}")
        print(f"Calculated Score: {score:.2f}/100")
        
        if args.verbose:
            print(f"\nInput Statistics:")
            for stat, value in stats.items():
                print(f"  {stat}: {value}")
    
    def benchmark_data_structures(self, args):
        """Benchmark data structure performance."""
        print("Data Structure Performance Benchmark")
        print("=" * 50)
        
        sizes = [100, 500, 1000, 5000] if not args.quick else [100, 500]
        
        for size in sizes:
            print(f"\nTesting with {size} players:")
            
            # Create test data
            test_players = []
            for i in range(size):
                player = Player(
                    player_id=i,
                    name=f"Player_{i}",
                    position="Midfielder",
                    team_id=1,
                    age=25,
                    performance_score=50.0 + (i % 50),
                    stats={"goals": i % 20, "assists": i % 15, "average_rating": 6.0 + (i % 4)},
                    last_updated=time.time()
                )
                test_players.append(player)
            
            # Benchmark hash table operations
            start_time = time.time()
            for player in test_players:
                self.data_structures.add_player(player)
            insertion_time = time.time() - start_time
            
            # Benchmark lookup
            start_time = time.time()
            self.data_structures.get_player(size // 2)
            lookup_time = time.time() - start_time
            
            # Benchmark heap operations
            start_time = time.time()
            top_players = self.data_structures.get_top_performers(10)
            heap_time = time.time() - start_time
            
            print(f"  Hash Table Insertion: {insertion_time:.4f}s ({insertion_time/size*1000:.2f}ms per player)")
            print(f"  Hash Table Lookup: {lookup_time:.6f}s")
            print(f"  Heap Top-10 Retrieval: {heap_time:.6f}s")
            
            # Memory usage
            stats = self.data_structures.get_system_stats()
            print(f"  Load Factor: {stats['hash_table_stats']['load_factor']:.3f}")
            print(f"  Heap Size: {stats['heap_size']}")
    
    def analyze_similarity(self, args):
        """Perform similarity analysis."""
        if not self.check_api_connection():
            print("Error: API server not running. Start with: cd src/api && python main.py")
            return
        
        try:
            # Get similar players from API
            response = requests.get(
                f"{self.api_url}/players/{args.player_id}/similar",
                params={"method": args.method, "top_k": args.top_k}
            )
            
            if response.status_code == 200:
                similar_players = response.json()
                
                print(f"Players similar to Player ID {args.player_id}")
                print(f"Method: {args.method}")
                print("-" * 50)
                
                for i, player in enumerate(similar_players, 1):
                    name = player.get('player_details', {}).get('name', 'Unknown') if player.get('player_details') else 'Unknown'
                    score = player['similarity_score']
                    print(f"{i:2d}. {name} (Similarity: {score:.3f})")
                
                if args.export:
                    with open(f"similarity_analysis_{args.player_id}.json", 'w') as f:
                        json.dump(similar_players, f, indent=2)
                    print(f"\nResults exported to similarity_analysis_{args.player_id}.json")
            
            else:
                print(f"Error: {response.status_code} - {response.text}")
        
        except Exception as e:
            print(f"Error performing similarity analysis: {e}")
    
    def predict_performance(self, args):
        """Predict future performance."""
        if not self.check_api_connection():
            print("Error: API server not running. Start with: cd src/api && python main.py")
            return
        
        try:
            response = requests.get(
                f"{self.api_url}/players/{args.player_id}/predict",
                params={"model": args.model}
            )
            
            if response.status_code == 200:
                prediction = response.json()
                
                print(f"Performance Prediction for Player ID {args.player_id}")
                print("-" * 50)
                print(f"Predicted Score: {prediction['prediction']:.2f}")
                print(f"Confidence: {prediction['confidence']:.1%}")
                print(f"Model Used: {prediction['model_used']}")
                print(f"Prediction Date: {prediction['prediction_date']}")
                
                if args.export:
                    with open(f"prediction_{args.player_id}.json", 'w') as f:
                        json.dump(prediction, f, indent=2)
                    print(f"\nResults exported to prediction_{args.player_id}.json")
            
            else:
                print(f"Error: {response.status_code} - {response.text}")
        
        except Exception as e:
            print(f"Error making prediction: {e}")
    
    def get_rankings(self, args):
        """Get player rankings."""
        if not self.check_api_connection():
            print("Error: API server not running. Start with: cd src/api && python main.py")
            return
        
        try:
            response = requests.get(f"{self.api_url}/rankings/top/{args.count}")
            
            if response.status_code == 200:
                rankings = response.json()
                
                print(f"Top {args.count} Player Rankings")
                print("=" * 60)
                print(f"{'Rank':<4} {'Name':<20} {'Position':<12} {'Score':<8} {'Age':<4}")
                print("-" * 60)
                
                for player in rankings:
                    rank = player['rank']
                    name = player['player']['name'][:19]
                    position = player['player']['position'][:11]
                    score = player['score']
                    age = player['player']['age']
                    
                    print(f"{rank:<4} {name:<20} {position:<12} {score:<8.2f} {age:<4}")
                
                if args.export:
                    with open(f"rankings_top_{args.count}.json", 'w') as f:
                        json.dump(rankings, f, indent=2)
                    print(f"\nResults exported to rankings_top_{args.count}.json")
            
            else:
                print(f"Error: {response.status_code} - {response.text}")
        
        except Exception as e:
            print(f"Error getting rankings: {e}")
    
    def get_player_info(self, args):
        """Get detailed player information."""
        if not self.check_api_connection():
            print("Error: API server not running. Start with: cd src/api && python main.py")
            return
        
        try:
            response = requests.get(f"{self.api_url}/players/{args.player_id}")
            
            if response.status_code == 200:
                player = response.json()
                
                print(f"Player Information")
                print("=" * 50)
                print(f"ID: {player['player_id']}")
                print(f"Name: {player['name']}")
                print(f"Position: {player['position']}")
                print(f"Team ID: {player['team_id']}")
                print(f"Age: {player['age']}")
                print(f"Performance Score: {player['performance_score']:.2f}")
                print(f"Last Updated: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(player['last_updated']))}")
                
                print(f"\nDetailed Statistics:")
                print("-" * 30)
                for stat, value in player['stats'].items():
                    print(f"{stat.replace('_', ' ').title()}: {value}")
                
                if args.export:
                    with open(f"player_{args.player_id}.json", 'w') as f:
                        json.dump(player, f, indent=2)
                    print(f"\nPlayer data exported to player_{args.player_id}.json")
            
            else:
                print(f"Error: {response.status_code} - {response.text}")
        
        except Exception as e:
            print(f"Error getting player info: {e}")
    
    def system_status(self, args):
        """Get system status and statistics."""
        if not self.check_api_connection():
            print("API Server: OFFLINE")
            print("Start with: cd src/api && python main.py")
            return
        
        try:
            # Get system stats
            response = requests.get(f"{self.api_url}/system/stats")
            
            if response.status_code == 200:
                stats = response.json()
                
                print("System Status")
                print("=" * 40)
                print("API Server: ONLINE")
                print(f"Total Players: {stats['total_players']}")
                print(f"Hash Table Load Factor: {stats['hash_table_load_factor']:.3f}")
                print(f"Heap Size: {stats['heap_size']}")
                print(f"Graph Nodes: {stats['graph_nodes']}")
                print(f"Graph Edges: {stats['graph_edges']}")
                print(f"Last Update: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stats['last_update']))}")
                print(f"API Version: {stats['api_version']}")
                
                # Get health status
                health_response = requests.get(f"{self.api_url}/health")
                if health_response.status_code == 200:
                    health = health_response.json()
                    print(f"\nHealth Status: {health['status'].upper()}")
                    print("Components:")
                    for component, status in health['components'].items():
                        print(f"  {component}: {status}")
            
            else:
                print(f"Error getting system stats: {response.status_code}")
        
        except Exception as e:
            print(f"Error checking system status: {e}")

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Dynamic Sports Performance Analytics Engine CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Performance score calculation
    score_parser = subparsers.add_parser('score', help='Calculate performance score')
    score_parser.add_argument('position', choices=['Goalkeeper', 'Defender', 'Midfielder', 'Attacker'])
    score_parser.add_argument('--goals', type=float, default=0, help='Goals scored')
    score_parser.add_argument('--assists', type=float, default=0, help='Assists')
    score_parser.add_argument('--pass-accuracy', type=float, default=80, help='Pass accuracy percentage')
    score_parser.add_argument('--shots-total', type=float, default=0, help='Total shots')
    score_parser.add_argument('--tackles-won', type=float, default=0, help='Tackles won')
    score_parser.add_argument('--interceptions', type=float, default=0, help='Interceptions')
    score_parser.add_argument('--key-passes', type=float, default=0, help='Key passes')
    score_parser.add_argument('--minutes-played', type=float, default=0, help='Minutes played')
    score_parser.add_argument('--average-rating', type=float, default=6.0, help='Average rating')
    score_parser.add_argument('--verbose', action='store_true', help='Show detailed output')
    
    # Benchmarking
    bench_parser = subparsers.add_parser('benchmark', help='Benchmark data structures')
    bench_parser.add_argument('--quick', action='store_true', help='Quick benchmark with fewer data points')
    
    # Similarity analysis
    sim_parser = subparsers.add_parser('similarity', help='Analyze player similarity')
    sim_parser.add_argument('player_id', type=int, help='Player ID to find similar players for')
    sim_parser.add_argument('--method', choices=['cosine', 'euclidean', 'cluster'], default='cosine')
    sim_parser.add_argument('--top-k', type=int, default=10, help='Number of similar players to return')
    sim_parser.add_argument('--export', action='store_true', help='Export results to JSON file')
    
    # Performance prediction
    pred_parser = subparsers.add_parser('predict', help='Predict future performance')
    pred_parser.add_argument('player_id', type=int, help='Player ID to predict performance for')
    pred_parser.add_argument('--model', choices=['linear_regression', 'random_forest'], default='random_forest')
    pred_parser.add_argument('--export', action='store_true', help='Export results to JSON file')
    
    # Rankings
    rank_parser = subparsers.add_parser('rankings', help='Get player rankings')
    rank_parser.add_argument('--count', type=int, default=20, help='Number of top players to show')
    rank_parser.add_argument('--export', action='store_true', help='Export results to JSON file')
    
    # Player info
    info_parser = subparsers.add_parser('player', help='Get player information')
    info_parser.add_argument('player_id', type=int, help='Player ID to get information for')
    info_parser.add_argument('--export', action='store_true', help='Export results to JSON file')
    
    # System status
    status_parser = subparsers.add_parser('status', help='Get system status')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = AnalyticsCLI()
    
    # Route to appropriate command
    if args.command == 'score':
        cli.calculate_performance_score(args)
    elif args.command == 'benchmark':
        cli.benchmark_data_structures(args)
    elif args.command == 'similarity':
        cli.analyze_similarity(args)
    elif args.command == 'predict':
        cli.predict_performance(args)
    elif args.command == 'rankings':
        cli.get_rankings(args)
    elif args.command == 'player':
        cli.get_player_info(args)
    elif args.command == 'status':
        cli.system_status(args)

if __name__ == "__main__":
    main()
