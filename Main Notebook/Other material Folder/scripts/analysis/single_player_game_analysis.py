#!/usr/bin/env python3
"""
Single Player Game Statistical Analysis
Comprehensive statistical analysis for one player in a specific game
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Optional
import sys
import os

class SinglePlayerGameAnalysis:
    """Comprehensive statistical analysis for a single player in a specific game."""
    
    def __init__(self, db_path: str = "data/final_advanced_stats/manchester_city_final_advanced_2023_24.db"):
        """Initialize with database connection."""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        
    def get_available_players(self) -> pd.DataFrame:
        """Get list of all available players."""
        query = """
        SELECT DISTINCT player_name, COUNT(*) as games_played
        FROM advanced_match_statistics 
        GROUP BY player_name 
        ORDER BY games_played DESC
        """
        return pd.read_sql_query(query, self.conn)
    
    def get_player_games(self, player_name: str) -> pd.DataFrame:
        """Get all games for a specific player."""
        query = """
        SELECT match_number, opponent, competition, match_date, 
               goals, assists, rating, minutes_played
        FROM advanced_match_statistics 
        WHERE player_name = ?
        ORDER BY match_number
        """
        return pd.read_sql_query(query, self.conn, params=[player_name])
    
    def get_game_statistics(self, player_name: str, opponent: str) -> Dict[str, Any]:
        """Get comprehensive statistics for a player in a specific game."""
        query = """
        SELECT * FROM advanced_match_statistics 
        WHERE player_name = ? AND opponent = ?
        """
        result = pd.read_sql_query(query, self.conn, params=[player_name, opponent])
        
        if result.empty:
            return None
            
        return result.iloc[0].to_dict()
    
    def get_player_season_context(self, player_name: str) -> Dict[str, Any]:
        """Get player's season-long statistics for context."""
        query = """
        SELECT * FROM player_season_summary 
        WHERE player_name = ?
        """
        result = pd.read_sql_query(query, self.conn, params=[player_name])
        
        if result.empty:
            return None
            
        return result.iloc[0].to_dict()
    
    def calculate_performance_metrics(self, game_stats: Dict[str, Any], season_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate advanced performance metrics for the game."""
        metrics = {}
        
        # Basic performance
        metrics['minutes_played'] = game_stats.get('minutes_played', 0)
        metrics['goals'] = game_stats.get('goals', 0)
        metrics['assists'] = game_stats.get('assists', 0)
        metrics['rating'] = game_stats.get('rating', 0)
        
        # Shot efficiency
        shots_total = game_stats.get('shots_total', 0)
        shots_on_target = game_stats.get('shots_on_target', 0)
        metrics['shots_total'] = shots_total
        metrics['shots_on_target'] = shots_on_target
        metrics['shot_accuracy'] = (shots_on_target / shots_total * 100) if shots_total > 0 else 0
        metrics['conversion_rate'] = (metrics['goals'] / shots_total * 100) if shots_total > 0 else 0
        
        # Expected goals performance
        xg = game_stats.get('expected_goals', 0)
        xa = game_stats.get('expected_assists', 0)
        metrics['expected_goals'] = xg
        metrics['expected_assists'] = xa
        metrics['xg_performance'] = metrics['goals'] - xg
        metrics['xa_performance'] = metrics['assists'] - xa
        
        # Passing performance
        passes_total = game_stats.get('passes_total', 0)
        passes_completed = game_stats.get('passes_completed', 0)
        metrics['passes_total'] = passes_total
        metrics['passes_completed'] = passes_completed
        metrics['pass_accuracy'] = (passes_completed / passes_total * 100) if passes_total > 0 else 0
        metrics['key_passes'] = game_stats.get('key_passes', 0)
        
        # Defensive performance
        metrics['tackles_total'] = game_stats.get('tackles_total', 0)
        metrics['tackles_won'] = game_stats.get('tackles_won', 0)
        metrics['tackle_success_rate'] = game_stats.get('tackle_success_rate', 0)
        metrics['interceptions'] = game_stats.get('interceptions', 0)
        metrics['clearances'] = game_stats.get('clearances', 0)
        
        # Physical and duels
        metrics['duels_total'] = game_stats.get('duels_total', 0)
        metrics['duels_won'] = game_stats.get('duels_won', 0)
        metrics['duel_success_rate'] = (metrics['duels_won'] / metrics['duels_total'] * 100) if metrics['duels_total'] > 0 else 0
        metrics['aerial_duels_total'] = game_stats.get('aerial_duels_total', 0)
        metrics['aerial_duels_won'] = game_stats.get('aerial_duels_won', 0)
        
        # Disciplinary
        metrics['yellow_cards'] = game_stats.get('yellow_cards', 0)
        metrics['red_cards'] = game_stats.get('red_cards', 0)
        metrics['fouls_committed'] = game_stats.get('fouls_committed', 0)
        metrics['fouls_suffered'] = game_stats.get('fouls_suffered', 0)
        
        # Advanced metrics
        metrics['touches'] = game_stats.get('touches', 0)
        metrics['dribbles_attempted'] = game_stats.get('dribbles_attempted', 0)
        metrics['dribbles_successful'] = game_stats.get('dribbles_successful', 0)
        metrics['dribble_success_rate'] = game_stats.get('dribble_success_rate', 0)
        
        # Performance vs season average
        if season_stats:
            metrics['rating_vs_average'] = metrics['rating'] - season_stats.get('average_rating', 0)
            metrics['goals_vs_average'] = metrics['goals'] - (season_stats.get('goals', 0) / season_stats.get('matches_played', 1))
            metrics['assists_vs_average'] = metrics['assists'] - (season_stats.get('assists', 0) / season_stats.get('matches_played', 1))
        
        return metrics
    
    def generate_performance_report(self, player_name: str, opponent: str) -> str:
        """Generate a comprehensive performance report for a player in a specific game."""
        # Get data
        game_stats = self.get_game_statistics(player_name, opponent)
        season_stats = self.get_player_season_context(player_name)
        
        if not game_stats:
            return f"No data found for {player_name} vs {opponent}"
        
        # Calculate metrics
        metrics = self.calculate_performance_metrics(game_stats, season_stats)
        
        # Generate report
        report = []
        report.append("=" * 80)
        report.append(f"STATISTICAL ANALYSIS: {player_name.upper()} vs {opponent.upper()}")
        report.append("=" * 80)
        report.append(f"Competition: {game_stats.get('competition', 'N/A')}")
        report.append(f"Match Date: {game_stats.get('match_date', 'N/A')}")
        report.append(f"Match Number: {game_stats.get('match_number', 'N/A')}")
        report.append("")
        
        # Basic Performance
        report.append("📊 BASIC PERFORMANCE")
        report.append("-" * 40)
        report.append(f"Minutes Played: {metrics['minutes_played']}")
        report.append(f"Goals: {metrics['goals']}")
        report.append(f"Assists: {metrics['assists']}")
        report.append(f"Performance Rating: {metrics['rating']:.1f}")
        if season_stats:
            report.append(f"Rating vs Season Average: {metrics.get('rating_vs_average', 0):+.1f}")
        report.append("")
        
        # Attacking Performance
        report.append("⚽ ATTACKING PERFORMANCE")
        report.append("-" * 40)
        report.append(f"Shots Total: {metrics['shots_total']}")
        report.append(f"Shots on Target: {metrics['shots_on_target']}")
        report.append(f"Shot Accuracy: {metrics['shot_accuracy']:.1f}%")
        report.append(f"Conversion Rate: {metrics['conversion_rate']:.1f}%")
        report.append(f"Expected Goals (xG): {metrics['expected_goals']:.2f}")
        report.append(f"xG Performance: {metrics['xg_performance']:+.2f}")
        report.append(f"Expected Assists (xA): {metrics['expected_assists']:.2f}")
        report.append(f"xA Performance: {metrics['xa_performance']:+.2f}")
        report.append("")
        
        # Passing Performance
        report.append("🎯 PASSING PERFORMANCE")
        report.append("-" * 40)
        report.append(f"Passes Total: {metrics['passes_total']}")
        report.append(f"Passes Completed: {metrics['passes_completed']}")
        report.append(f"Pass Accuracy: {metrics['pass_accuracy']:.1f}%")
        report.append(f"Key Passes: {metrics['key_passes']}")
        report.append("")
        
        # Defensive Performance
        report.append("🛡️ DEFENSIVE PERFORMANCE")
        report.append("-" * 40)
        report.append(f"Tackles Total: {metrics['tackles_total']}")
        report.append(f"Tackles Won: {metrics['tackles_won']}")
        report.append(f"Tackle Success Rate: {metrics['tackle_success_rate']:.1f}%")
        report.append(f"Interceptions: {metrics['interceptions']}")
        report.append(f"Clearances: {metrics['clearances']}")
        report.append("")
        
        # Physical Performance
        report.append("💪 PHYSICAL PERFORMANCE")
        report.append("-" * 40)
        report.append(f"Duels Total: {metrics['duels_total']}")
        report.append(f"Duels Won: {metrics['duels_won']}")
        report.append(f"Duel Success Rate: {metrics['duel_success_rate']:.1f}%")
        report.append(f"Aerial Duels Total: {metrics['aerial_duels_total']}")
        report.append(f"Aerial Duels Won: {metrics['aerial_duels_won']}")
        report.append(f"Touches: {metrics['touches']}")
        report.append("")
        
        # Disciplinary
        report.append("⚠️ DISCIPLINARY")
        report.append("-" * 40)
        report.append(f"Yellow Cards: {metrics['yellow_cards']}")
        report.append(f"Red Cards: {metrics['red_cards']}")
        report.append(f"Fouls Committed: {metrics['fouls_committed']}")
        report.append(f"Fouls Suffered: {metrics['fouls_suffered']}")
        report.append("")
        
        # Season Context
        if season_stats:
            report.append("📈 SEASON CONTEXT")
            report.append("-" * 40)
            report.append(f"Season Matches Played: {season_stats.get('matches_played', 0)}")
            report.append(f"Season Goals: {season_stats.get('goals', 0)}")
            report.append(f"Season Assists: {season_stats.get('assists', 0)}")
            report.append(f"Season Average Rating: {season_stats.get('average_rating', 0):.1f}")
            report.append(f"Season Pass Accuracy: {season_stats.get('pass_accuracy', 0):.1f}%")
        
        report.append("=" * 80)
        
        return "\n".join(report)

    def create_performance_visualization(self, player_name: str, opponent: str) -> str:
        """Create performance visualization charts."""
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns

            # Get data
            game_stats = self.get_game_statistics(player_name, opponent)
            season_stats = self.get_player_season_context(player_name)

            if not game_stats or not season_stats:
                return "Insufficient data for visualization"

            # Calculate metrics
            metrics = self.calculate_performance_metrics(game_stats, season_stats)

            # Create figure with subplots
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle(f'{player_name} vs {opponent} - Performance Analysis', fontsize=16, fontweight='bold')

            # 1. Attacking Performance
            attacking_metrics = ['goals', 'assists', 'shots_total', 'shots_on_target']
            attacking_values = [metrics[m] for m in attacking_metrics]
            ax1.bar(attacking_metrics, attacking_values, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
            ax1.set_title('Attacking Performance')
            ax1.set_ylabel('Count')

            # 2. Passing vs Season Average
            pass_accuracy_game = metrics['pass_accuracy']
            pass_accuracy_season = season_stats.get('pass_accuracy', 0)
            ax2.bar(['Game', 'Season Avg'], [pass_accuracy_game, pass_accuracy_season],
                   color=['#FF6B6B', '#45B7D1'])
            ax2.set_title('Pass Accuracy Comparison')
            ax2.set_ylabel('Accuracy (%)')
            ax2.set_ylim(0, 100)

            # 3. Expected vs Actual Performance
            categories = ['Goals', 'Assists']
            actual = [metrics['goals'], metrics['assists']]
            expected = [metrics['expected_goals'], metrics['expected_assists']]

            x = np.arange(len(categories))
            width = 0.35
            ax3.bar(x - width/2, actual, width, label='Actual', color='#FF6B6B')
            ax3.bar(x + width/2, expected, width, label='Expected', color='#45B7D1')
            ax3.set_title('Expected vs Actual Performance')
            ax3.set_xticks(x)
            ax3.set_xticklabels(categories)
            ax3.legend()

            # 4. Defensive Performance
            defensive_metrics = ['tackles_total', 'interceptions', 'clearances']
            defensive_values = [metrics[m] for m in defensive_metrics]
            ax4.bar(defensive_metrics, defensive_values, color=['#96CEB4', '#FECA57', '#FF9FF3'])
            ax4.set_title('Defensive Performance')
            ax4.set_ylabel('Count')

            plt.tight_layout()

            # Save chart
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            chart_filename = f"logs/player_chart_{player_name.replace(' ', '_')}_{opponent.replace(' ', '_')}_{timestamp}.png"
            plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
            plt.close()

            return chart_filename

        except ImportError:
            return "Matplotlib not available for visualization"
        except Exception as e:
            return f"Error creating visualization: {e}"

def analyze_specific_player(player_name: str = "Jack Grealish", opponent: str = "Everton"):
    """Analyze a specific player's performance in a game."""
    analyzer = SinglePlayerGameAnalysis()

    print(f"🎯 Statistical Analysis: {player_name} vs {opponent}")
    print("=" * 60)

    # Generate and display report
    report = analyzer.generate_performance_report(player_name, opponent)
    print(report)

    # Create visualization
    chart_file = analyzer.create_performance_visualization(player_name, opponent)
    if chart_file.endswith('.png'):
        print(f"\n📊 Performance chart saved to: {chart_file}")
    else:
        print(f"\n⚠️ Visualization: {chart_file}")

    # Save report to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"logs/player_analysis_{player_name.replace(' ', '_')}_{opponent.replace(' ', '_')}_{timestamp}.txt"

    os.makedirs("logs", exist_ok=True)
    with open(filename, 'w') as f:
        f.write(report)

    print(f"📄 Report saved to: {filename}")

def main():
    """Interactive main function to analyze a player's game performance."""
    analyzer = SinglePlayerGameAnalysis()

    print("🎯 Single Player Game Statistical Analysis")
    print("=" * 50)

    # Show available players
    players = analyzer.get_available_players()
    print("\nAvailable Players:")
    print(players.head(10).to_string(index=False))

    # Get user input
    player_name = input("\nEnter player name: ").strip()

    # Show available games for the player
    games = analyzer.get_player_games(player_name)
    if games.empty:
        print(f"No games found for {player_name}")
        return

    print(f"\nAvailable games for {player_name}:")
    print(games.to_string(index=False))

    opponent = input("\nEnter opponent name: ").strip()

    # Generate and display report
    report = analyzer.generate_performance_report(player_name, opponent)
    print("\n" + report)

    # Create visualization
    chart_file = analyzer.create_performance_visualization(player_name, opponent)
    if chart_file.endswith('.png'):
        print(f"\n📊 Performance chart saved to: {chart_file}")
    else:
        print(f"\n⚠️ Visualization: {chart_file}")

    # Save report to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"logs/player_analysis_{player_name.replace(' ', '_')}_{opponent.replace(' ', '_')}_{timestamp}.txt"

    os.makedirs("logs", exist_ok=True)
    with open(filename, 'w') as f:
        f.write(report)

    print(f"\n📄 Report saved to: {filename}")

if __name__ == "__main__":
    # You can run a specific analysis or interactive mode
    if len(sys.argv) > 2:
        analyze_specific_player(sys.argv[1], sys.argv[2])
    else:
        main()
