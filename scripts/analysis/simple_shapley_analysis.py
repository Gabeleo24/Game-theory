#!/usr/bin/env python3
"""
Simple Shapley Value Analysis for Player Contributions
Analyzes player contributions using the collected 2024-2025 data
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any
import itertools
from datetime import datetime

class SimpleShapleyAnalyzer:
    """Simple Shapley value analyzer for player contributions"""
    
    def __init__(self, data_dir: str = "data/focused/players"):
        self.data_dir = Path(data_dir)
        self.individual_stats_dir = self.data_dir / "individual_stats"
        
    def load_team_players(self, team_id: int, season: int) -> List[Dict]:
        """Load all players for a specific team and season"""
        team_dir = self.individual_stats_dir / f"team_{team_id}" / str(season)
        
        if not team_dir.exists():
            print(f"No data found for team {team_id} in season {season}")
            return []
        
        players = []
        for player_file in team_dir.glob("*.json"):
            try:
                with open(player_file, 'r') as f:
                    player_data = json.load(f)
                    players.append(player_data)
            except Exception as e:
                print(f"Error loading {player_file}: {e}")
        
        return players
    
    def extract_key_metrics(self, player_data: Dict) -> Dict:
        """Extract key performance metrics from player data"""
        agg_stats = player_data.get('aggregated_stats', {})
        
        # Normalize per 90 minutes
        minutes = agg_stats.get('total_minutes', 1)
        minutes_90 = max(minutes / 90, 0.1)  # Avoid division by zero
        
        return {
            'player_id': player_data['player_info']['id'],
            'player_name': player_data['player_info']['name'],
            'position': player_data.get('season_summary', {}).get('primary_position', 'Unknown'),
            'appearances': agg_stats.get('total_appearances', 0),
            'minutes': minutes,
            'goals': agg_stats.get('total_goals', 0),
            'assists': agg_stats.get('total_assists', 0),
            'rating': agg_stats.get('average_rating', 0),
            # Per 90 minute metrics
            'goals_per_90': agg_stats.get('goals_per_90', 0),
            'assists_per_90': agg_stats.get('assists_per_90', 0),
            'goal_contributions_per_90': (agg_stats.get('total_goals', 0) + agg_stats.get('total_assists', 0)) / minutes_90,
            'rating_weighted': agg_stats.get('average_rating', 0) * (minutes / 90) if minutes > 0 else 0
        }
    
    def calculate_team_performance(self, players_metrics: List[Dict]) -> float:
        """Calculate overall team performance score"""
        if not players_metrics:
            return 0.0
        
        # Weight by minutes played and performance
        total_weighted_rating = sum(p['rating_weighted'] for p in players_metrics)
        total_goal_contributions = sum(p['goals'] + p['assists'] for p in players_metrics)
        total_minutes = sum(p['minutes'] for p in players_metrics)
        
        # Normalize team performance (0-100 scale)
        avg_rating = total_weighted_rating / max(total_minutes / 90, 1)
        goal_contribution_rate = total_goal_contributions / max(total_minutes / 90, 1)
        
        return (avg_rating * 10) + (goal_contribution_rate * 20)
    
    def calculate_marginal_contributions(self, players_metrics: List[Dict]) -> Dict[int, float]:
        """Calculate marginal contribution of each player using Shapley values"""
        if len(players_metrics) < 2:
            return {p['player_id']: 100.0 for p in players_metrics}
        
        player_ids = [p['player_id'] for p in players_metrics]
        contributions = {}
        
        # Calculate baseline team performance
        full_team_performance = self.calculate_team_performance(players_metrics)
        
        for player_id in player_ids:
            # Calculate team performance without this player
            other_players = [p for p in players_metrics if p['player_id'] != player_id]
            performance_without = self.calculate_team_performance(other_players)
            
            # Marginal contribution
            marginal_contribution = full_team_performance - performance_without
            contributions[player_id] = marginal_contribution
        
        # Normalize contributions to percentages
        total_contribution = sum(contributions.values())
        if total_contribution > 0:
            contributions = {pid: (contrib / total_contribution) * 100 
                           for pid, contrib in contributions.items()}
        
        return contributions
    
    def analyze_team_season(self, team_id: int, season: int) -> Dict[str, Any]:
        """Analyze a specific team's season using Shapley values"""
        print(f"\nAnalyzing Team {team_id} - Season {season}")
        print("=" * 50)
        
        # Load player data
        players_data = self.load_team_players(team_id, season)
        if not players_data:
            return {}
        
        # Extract metrics
        players_metrics = [self.extract_key_metrics(p) for p in players_data]
        
        # Filter players with significant minutes (>= 90 minutes)
        significant_players = [p for p in players_metrics if p['minutes'] >= 90]
        
        print(f"Total players: {len(players_metrics)}")
        print(f"Players with significant minutes: {len(significant_players)}")
        
        if not significant_players:
            return {}
        
        # Calculate Shapley contributions
        contributions = self.calculate_marginal_contributions(significant_players)
        
        # Create results
        results = []
        for player in significant_players:
            player_id = player['player_id']
            contribution = contributions.get(player_id, 0)
            
            results.append({
                'player_id': player_id,
                'player_name': player['player_name'],
                'position': player['position'],
                'appearances': player['appearances'],
                'minutes': player['minutes'],
                'goals': player['goals'],
                'assists': player['assists'],
                'rating': player['rating'],
                'goals_per_90': player['goals_per_90'],
                'assists_per_90': player['assists_per_90'],
                'shapley_contribution': contribution,
                'contribution_rank': 0  # Will be set after sorting
            })
        
        # Sort by contribution and assign ranks
        results.sort(key=lambda x: x['shapley_contribution'], reverse=True)
        for i, player in enumerate(results):
            player['contribution_rank'] = i + 1
        
        # Team summary
        team_performance = self.calculate_team_performance(significant_players)
        
        analysis_result = {
            'team_id': team_id,
            'season': season,
            'team_performance_score': team_performance,
            'total_players_analyzed': len(significant_players),
            'player_contributions': results,
            'top_contributors': results[:5],
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        return analysis_result
    
    def print_analysis_results(self, results: Dict[str, Any]):
        """Print formatted analysis results"""
        if not results:
            print("No results to display")
            return
        
        print(f"\nTeam Performance Score: {results['team_performance_score']:.2f}")
        print(f"Players Analyzed: {results['total_players_analyzed']}")
        
        print(f"\nTop 10 Contributors:")
        print("-" * 100)
        print(f"{'Rank':<4} {'Player':<20} {'Position':<12} {'Apps':<4} {'Goals':<5} {'Assists':<7} {'Rating':<6} {'Contribution':<12}")
        print("-" * 100)
        
        for player in results['player_contributions'][:10]:
            print(f"{player['contribution_rank']:<4} "
                  f"{player['player_name'][:19]:<20} "
                  f"{player['position'][:11]:<12} "
                  f"{player['appearances']:<4} "
                  f"{player['goals']:<5} "
                  f"{player['assists']:<7} "
                  f"{player['rating']:.2f}{'':>2} "
                  f"{player['shapley_contribution']:.2f}%")

def main():
    """Main analysis function"""
    analyzer = SimpleShapleyAnalyzer()
    
    # Analyze some key teams for 2024 season
    key_teams = [
        (541, 2024),  # Real Madrid
        (529, 2024),  # Barcelona  
        (50, 2024),   # Manchester City
        (33, 2024),   # Manchester United
        (157, 2024),  # Bayern Munich
    ]
    
    print("SHAPLEY VALUE ANALYSIS - 2024 SEASON")
    print("=" * 60)
    
    all_results = []
    
    for team_id, season in key_teams:
        try:
            results = analyzer.analyze_team_season(team_id, season)
            if results:
                analyzer.print_analysis_results(results)
                all_results.append(results)
        except Exception as e:
            print(f"Error analyzing team {team_id}: {e}")
    
    print(f"\n\nAnalysis completed for {len(all_results)} teams")
    print("Results show player contributions using Shapley value methodology")

if __name__ == "__main__":
    main()
