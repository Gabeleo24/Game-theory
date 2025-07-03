#!/usr/bin/env python3
"""
Multi-Season Comparative Analysis for ADS599 Capstone
Analyzes player and team performance trends across 2019-2025 seasons
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

class MultiSeasonAnalyzer:
    """Comparative analysis across multiple seasons"""
    
    def __init__(self, data_dir: str = "data/focused/players"):
        self.data_dir = Path(data_dir)
        self.individual_stats_dir = self.data_dir / "individual_stats"
        self.seasons = [2019, 2020, 2021, 2022, 2023, 2024]
        
        # Key teams for focused analysis
        self.key_teams = {
            541: "Real Madrid",
            529: "Barcelona", 
            50: "Manchester City",
            33: "Manchester United",
            157: "Bayern Munich",
            40: "Liverpool",
            165: "Borussia Dortmund",
            85: "Paris Saint-Germain"
        }
    
    def load_player_data_all_seasons(self, team_id: int) -> Dict[int, List[Dict]]:
        """Load player data for all available seasons for a team"""
        team_data = {}
        team_dir = self.individual_stats_dir / f"team_{team_id}"
        
        if not team_dir.exists():
            return {}
        
        for season in self.seasons:
            season_dir = team_dir / str(season)
            if season_dir.exists():
                players = []
                for player_file in season_dir.glob("*.json"):
                    try:
                        with open(player_file, 'r') as f:
                            player_data = json.load(f)
                            players.append(player_data)
                    except Exception as e:
                        print(f"Error loading {player_file}: {e}")
                team_data[season] = players
        
        return team_data
    
    def extract_team_metrics(self, players_data: List[Dict]) -> Dict:
        """Extract team-level metrics from player data"""
        if not players_data:
            return {}
        
        total_goals = sum(p.get('aggregated_stats', {}).get('total_goals', 0) for p in players_data)
        total_assists = sum(p.get('aggregated_stats', {}).get('total_assists', 0) for p in players_data)
        total_minutes = sum(p.get('aggregated_stats', {}).get('total_minutes', 0) for p in players_data)
        
        # Calculate average rating weighted by minutes
        weighted_ratings = []
        total_weighted_minutes = 0
        for player in players_data:
            agg_stats = player.get('aggregated_stats', {})
            rating = agg_stats.get('average_rating', 0)
            minutes = agg_stats.get('total_minutes', 0)
            if rating and minutes:
                weighted_ratings.append(rating * minutes)
                total_weighted_minutes += minutes
        
        avg_rating = sum(weighted_ratings) / total_weighted_minutes if total_weighted_minutes > 0 else 0
        
        return {
            'total_goals': total_goals,
            'total_assists': total_assists,
            'total_minutes': total_minutes,
            'total_players': len(players_data),
            'avg_team_rating': avg_rating,
            'goals_per_90': (total_goals / (total_minutes / 90)) if total_minutes > 0 else 0,
            'assists_per_90': (total_assists / (total_minutes / 90)) if total_minutes > 0 else 0
        }
    
    def analyze_team_evolution(self, team_id: int) -> Dict[str, Any]:
        """Analyze how a team evolved across seasons"""
        team_name = self.key_teams.get(team_id, f"Team {team_id}")
        print(f"\nAnalyzing {team_name} Evolution (2019-2024)")
        print("=" * 60)
        
        team_data = self.load_player_data_all_seasons(team_id)
        
        if not team_data:
            print(f"No data found for {team_name}")
            return {}
        
        season_metrics = {}
        for season, players in team_data.items():
            metrics = self.extract_team_metrics(players)
            if metrics:
                season_metrics[season] = metrics
                print(f"{season}: {metrics['total_goals']} goals, {metrics['avg_team_rating']:.2f} avg rating")
        
        # Calculate trends
        trends = self.calculate_trends(season_metrics)
        
        return {
            'team_id': team_id,
            'team_name': team_name,
            'season_metrics': season_metrics,
            'trends': trends,
            'seasons_analyzed': list(season_metrics.keys())
        }
    
    def calculate_trends(self, season_metrics: Dict[int, Dict]) -> Dict[str, Any]:
        """Calculate performance trends across seasons"""
        if len(season_metrics) < 2:
            return {}
        
        seasons = sorted(season_metrics.keys())
        
        # Extract time series data
        goals_trend = [season_metrics[s]['total_goals'] for s in seasons]
        rating_trend = [season_metrics[s]['avg_team_rating'] for s in seasons]
        
        # Calculate simple trends (percentage change from first to last)
        goals_change = ((goals_trend[-1] - goals_trend[0]) / goals_trend[0] * 100) if goals_trend[0] > 0 else 0
        rating_change = ((rating_trend[-1] - rating_trend[0]) / rating_trend[0] * 100) if rating_trend[0] > 0 else 0
        
        return {
            'goals_trend_pct': goals_change,
            'rating_trend_pct': rating_change,
            'best_season_goals': seasons[goals_trend.index(max(goals_trend))],
            'best_season_rating': seasons[rating_trend.index(max(rating_trend))],
            'consistency_score': 100 - (np.std(rating_trend) / np.mean(rating_trend) * 100) if rating_trend else 0
        }
    
    def identify_top_performers_across_seasons(self) -> Dict[str, Any]:
        """Identify players who performed consistently well across multiple seasons"""
        print("\nIdentifying Top Performers Across Seasons")
        print("=" * 50)
        
        player_performance = {}
        
        for team_id in self.key_teams.keys():
            team_data = self.load_player_data_all_seasons(team_id)
            
            for season, players in team_data.items():
                for player in players:
                    player_info = player.get('player_info', {})
                    agg_stats = player.get('aggregated_stats', {})
                    
                    player_id = player_info.get('id')
                    player_name = player_info.get('name')
                    
                    if not player_id or not player_name:
                        continue
                    
                    # Only consider players with significant minutes
                    minutes = agg_stats.get('total_minutes', 0)
                    if minutes < 900:  # Less than 10 full games
                        continue
                    
                    if player_id not in player_performance:
                        player_performance[player_id] = {
                            'name': player_name,
                            'seasons': [],
                            'total_goals': 0,
                            'total_assists': 0,
                            'total_minutes': 0,
                            'avg_rating': 0,
                            'teams_played': set()
                        }
                    
                    perf = player_performance[player_id]
                    perf['seasons'].append(season)
                    perf['total_goals'] += agg_stats.get('total_goals', 0)
                    perf['total_assists'] += agg_stats.get('total_assists', 0)
                    perf['total_minutes'] += minutes
                    perf['teams_played'].add(team_id)
        
        # Calculate averages and filter for multi-season players
        top_performers = []
        for player_id, perf in player_performance.items():
            if len(perf['seasons']) >= 3:  # At least 3 seasons
                perf['avg_rating'] = perf['total_minutes'] / len(perf['seasons']) / 90  # Rough proxy
                perf['goals_per_season'] = perf['total_goals'] / len(perf['seasons'])
                perf['assists_per_season'] = perf['total_assists'] / len(perf['seasons'])
                perf['seasons_count'] = len(perf['seasons'])
                perf['teams_count'] = len(perf['teams_played'])
                top_performers.append(perf)
        
        # Sort by total contribution
        top_performers.sort(key=lambda x: x['total_goals'] + x['total_assists'], reverse=True)
        
        return {
            'top_performers': top_performers[:20],
            'analysis_summary': {
                'total_players_analyzed': len(player_performance),
                'multi_season_players': len(top_performers),
                'seasons_covered': self.seasons
            }
        }
    
    def generate_comparative_report(self) -> Dict[str, Any]:
        """Generate comprehensive comparative analysis report"""
        print("\nGenerating Multi-Season Comparative Analysis Report")
        print("=" * 60)
        
        report = {
            'analysis_timestamp': datetime.now().isoformat(),
            'seasons_analyzed': self.seasons,
            'teams_analyzed': self.key_teams,
            'team_evolution': {},
            'top_performers': {},
            'league_trends': {}
        }
        
        # Analyze each key team
        for team_id in self.key_teams.keys():
            try:
                team_analysis = self.analyze_team_evolution(team_id)
                if team_analysis:
                    report['team_evolution'][team_id] = team_analysis
            except Exception as e:
                print(f"Error analyzing team {team_id}: {e}")
        
        # Identify top performers
        try:
            top_performers = self.identify_top_performers_across_seasons()
            report['top_performers'] = top_performers
        except Exception as e:
            print(f"Error identifying top performers: {e}")
        
        return report
    
    def print_summary_report(self, report: Dict[str, Any]):
        """Print formatted summary of the analysis"""
        print(f"\n{'='*80}")
        print("MULTI-SEASON COMPARATIVE ANALYSIS SUMMARY")
        print(f"{'='*80}")
        
        print(f"Analysis Period: {min(self.seasons)}-{max(self.seasons)}")
        print(f"Teams Analyzed: {len(report['team_evolution'])}")
        
        # Team Evolution Summary
        print(f"\nTEAM EVOLUTION HIGHLIGHTS:")
        print("-" * 40)
        for team_id, analysis in report['team_evolution'].items():
            team_name = analysis['team_name']
            trends = analysis.get('trends', {})
            
            goals_trend = trends.get('goals_trend_pct', 0)
            rating_trend = trends.get('rating_trend_pct', 0)
            
            print(f"{team_name}:")
            print(f"  Goals Trend: {goals_trend:+.1f}%")
            print(f"  Rating Trend: {rating_trend:+.1f}%")
            print(f"  Seasons: {len(analysis['seasons_analyzed'])}")
        
        # Top Performers Summary
        if 'top_performers' in report and report['top_performers']:
            top_performers = report['top_performers']['top_performers']
            print(f"\nTOP MULTI-SEASON PERFORMERS:")
            print("-" * 40)
            print(f"{'Player':<20} {'Seasons':<8} {'Goals':<6} {'Assists':<8} {'Teams':<6}")
            print("-" * 60)
            
            for player in top_performers[:10]:
                print(f"{player['name'][:19]:<20} "
                      f"{player['seasons_count']:<8} "
                      f"{player['total_goals']:<6} "
                      f"{player['total_assists']:<8} "
                      f"{player['teams_count']:<6}")

def main():
    """Main analysis function"""
    analyzer = MultiSeasonAnalyzer()
    
    # Generate comprehensive report
    report = analyzer.generate_comparative_report()
    
    # Print summary
    analyzer.print_summary_report(report)
    
    # Save detailed report
    report_path = Path("data/analysis/multi_season_comparative_analysis.json")
    report_path.parent.mkdir(exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\nDetailed report saved to: {report_path}")
    print("Analysis complete!")

if __name__ == "__main__":
    main()
