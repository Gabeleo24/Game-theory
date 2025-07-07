#!/usr/bin/env python3
"""
Data Analysis Starter Script
Demonstrates how to access and analyze soccer data from PostgreSQL and JSON files
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
import json
from pathlib import Path
import logging
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

class SoccerDataAnalyzer:
    def __init__(self, db_config=None):
        """Initialize the data analyzer."""
        self.db_config = db_config or {
            'host': 'localhost',
            'port': 5432,
            'database': 'soccer_intelligence',
            'user': 'soccerapp',
            'password': 'soccerpass123'
        }
        
        self.data_dir = Path('data')
        self.focused_dir = self.data_dir / 'focused'
        self.engine = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Setup plotting
        plt.style.use('default')
        sns.set_palette("husl")
    
    def connect_db(self):
        """Connect to PostgreSQL database."""
        try:
            connection_string = f"postgresql://{self.db_config['user']}:{self.db_config['password']}@{self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}"
            self.engine = create_engine(connection_string)
            
            # Test connection
            with self.engine.connect() as conn:
                result = conn.execute("SELECT COUNT(*) FROM teams")
                team_count = result.fetchone()[0]
                self.logger.info(f"Connected to database. Found {team_count} teams.")
            
            return True
            
        except Exception as e:
            self.logger.warning(f"Database connection failed: {e}")
            self.logger.info("Will use JSON files for analysis instead.")
            return False
    
    def get_database_overview(self):
        """Get overview of data in the database."""
        if not self.engine:
            return None
        
        try:
            overview = {}
            
            # Count records in each table
            tables = ['teams', 'players', 'matches', 'player_statistics', 'team_statistics', 'competitions']
            
            for table in tables:
                try:
                    result = pd.read_sql(f"SELECT COUNT(*) as count FROM {table}", self.engine)
                    overview[table] = result['count'].iloc[0]
                except:
                    overview[table] = 0
            
            return overview
            
        except Exception as e:
            self.logger.error(f"Error getting database overview: {e}")
            return None
    
    def analyze_team_performance(self, season_year=2023):
        """Analyze team performance across competitions."""
        if self.engine:
            # Database analysis
            query = """
            SELECT t.team_name, t.country, ts.competition_id, c.competition_name,
                   ts.matches_played, ts.wins, ts.draws, ts.losses,
                   ts.goals_for, ts.goals_against, ts.goal_difference, ts.points,
                   ROUND(ts.wins::numeric / NULLIF(ts.matches_played, 0) * 100, 2) as win_percentage
            FROM team_statistics ts
            JOIN teams t ON ts.team_id = t.team_id
            JOIN competitions c ON ts.competition_id = c.competition_id
            WHERE ts.season_year = %s AND ts.matches_played > 0
            ORDER BY ts.points DESC, ts.goal_difference DESC
            """
            
            try:
                df = pd.read_sql(query, self.engine, params=[season_year])
                self.logger.info(f"Loaded team performance data for {len(df)} team-competition records")
                return df
            except Exception as e:
                self.logger.error(f"Database query failed: {e}")
        
        # Fallback to JSON analysis
        return self.analyze_team_performance_from_json(season_year)
    
    def analyze_team_performance_from_json(self, season_year=2023):
        """Analyze team performance from JSON files."""
        self.logger.info("Analyzing team performance from JSON files...")
        
        team_data = []
        
        # Look for team statistics files
        for json_file in self.focused_dir.glob(f'*teams*{season_year}*.json'):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and 'team' in item:
                            team = item['team']
                            team_data.append({
                                'team_name': team.get('name'),
                                'country': team.get('country'),
                                'founded': team.get('founded'),
                                'venue': team.get('venue', {}).get('name') if team.get('venue') else None
                            })
                
            except Exception as e:
                self.logger.error(f"Error processing {json_file}: {e}")
        
        if team_data:
            df = pd.DataFrame(team_data)
            self.logger.info(f"Loaded {len(df)} teams from JSON files")
            return df
        
        return pd.DataFrame()
    
    def analyze_player_performance(self, season_year=2023, min_minutes=500):
        """Analyze top player performances."""
        if self.engine:
            query = """
            SELECT p.player_name, p.nationality, t.team_name, t.country as team_country,
                   ps.goals, ps.assists, ps.minutes_played, ps.rating,
                   ps.shots_total, ps.passes_total, ps.tackles_total,
                   ROUND(ps.goals::numeric / NULLIF(ps.minutes_played, 0) * 90, 3) as goals_per_90,
                   ROUND(ps.assists::numeric / NULLIF(ps.minutes_played, 0) * 90, 3) as assists_per_90,
                   (ps.goals + ps.assists) as goal_contributions
            FROM player_statistics ps
            JOIN players p ON ps.player_id = p.player_id
            JOIN teams t ON ps.team_id = t.team_id
            WHERE ps.season_year = %s AND ps.minutes_played >= %s
            ORDER BY ps.rating DESC, goal_contributions DESC
            """
            
            try:
                df = pd.read_sql(query, self.engine, params=[season_year, min_minutes])
                self.logger.info(f"Loaded player performance data for {len(df)} players")
                return df
            except Exception as e:
                self.logger.error(f"Database query failed: {e}")
        
        # Fallback message
        self.logger.info("Player performance analysis requires database connection")
        return pd.DataFrame()
    
    def create_visualizations(self, team_df, player_df):
        """Create visualizations for the analysis."""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Soccer Performance Analysis', fontsize=16, fontweight='bold')
        
        # 1. Teams by country
        if not team_df.empty and 'country' in team_df.columns:
            country_counts = team_df['country'].value_counts().head(10)
            axes[0, 0].bar(range(len(country_counts)), country_counts.values)
            axes[0, 0].set_xticks(range(len(country_counts)))
            axes[0, 0].set_xticklabels(country_counts.index, rotation=45, ha='right')
            axes[0, 0].set_title('Teams by Country')
            axes[0, 0].set_ylabel('Number of Teams')
        else:
            axes[0, 0].text(0.5, 0.5, 'No team data available', ha='center', va='center', transform=axes[0, 0].transAxes)
            axes[0, 0].set_title('Teams by Country')
        
        # 2. Win percentage distribution (if available)
        if not team_df.empty and 'win_percentage' in team_df.columns:
            axes[0, 1].hist(team_df['win_percentage'].dropna(), bins=15, alpha=0.7, edgecolor='black')
            axes[0, 1].set_title('Win Percentage Distribution')
            axes[0, 1].set_xlabel('Win Percentage')
            axes[0, 1].set_ylabel('Frequency')
        else:
            axes[0, 1].text(0.5, 0.5, 'No win percentage data', ha='center', va='center', transform=axes[0, 1].transAxes)
            axes[0, 1].set_title('Win Percentage Distribution')
        
        # 3. Player goals vs assists (if available)
        if not player_df.empty and 'goals' in player_df.columns and 'assists' in player_df.columns:
            scatter = axes[1, 0].scatter(player_df['goals'], player_df['assists'], 
                                       c=player_df['rating'] if 'rating' in player_df.columns else 'blue',
                                       alpha=0.6, cmap='viridis')
            axes[1, 0].set_title('Goals vs Assists')
            axes[1, 0].set_xlabel('Goals')
            axes[1, 0].set_ylabel('Assists')
            if 'rating' in player_df.columns:
                plt.colorbar(scatter, ax=axes[1, 0], label='Rating')
        else:
            axes[1, 0].text(0.5, 0.5, 'No player data available', ha='center', va='center', transform=axes[1, 0].transAxes)
            axes[1, 0].set_title('Goals vs Assists')
        
        # 4. Top performers (if available)
        if not player_df.empty and 'rating' in player_df.columns:
            top_players = player_df.nlargest(10, 'rating')
            y_pos = range(len(top_players))
            axes[1, 1].barh(y_pos, top_players['rating'])
            axes[1, 1].set_yticks(y_pos)
            axes[1, 1].set_yticklabels(top_players['player_name'], fontsize=8)
            axes[1, 1].set_title('Top 10 Players by Rating')
            axes[1, 1].set_xlabel('Rating')
        else:
            axes[1, 1].text(0.5, 0.5, 'No rating data available', ha='center', va='center', transform=axes[1, 1].transAxes)
            axes[1, 1].set_title('Top 10 Players by Rating')
        
        plt.tight_layout()
        
        # Save the plot
        output_dir = Path('data/analysis')
        output_dir.mkdir(exist_ok=True)
        plt.savefig(output_dir / 'soccer_analysis_overview.png', dpi=300, bbox_inches='tight')
        self.logger.info(f"Visualization saved to {output_dir / 'soccer_analysis_overview.png'}")
        
        return fig
    
    def generate_summary_report(self, team_df, player_df):
        """Generate a summary report of the analysis."""
        report = {
            'analysis_timestamp': pd.Timestamp.now().isoformat(),
            'data_summary': {
                'teams_analyzed': len(team_df),
                'players_analyzed': len(player_df),
                'data_source': 'database' if self.engine else 'json_files'
            }
        }
        
        if not team_df.empty:
            report['team_analysis'] = {
                'total_teams': len(team_df),
                'countries_represented': team_df['country'].nunique() if 'country' in team_df.columns else 0,
                'top_countries': team_df['country'].value_counts().head(5).to_dict() if 'country' in team_df.columns else {}
            }
            
            if 'win_percentage' in team_df.columns:
                report['team_analysis']['avg_win_percentage'] = float(team_df['win_percentage'].mean())
                report['team_analysis']['best_team'] = team_df.loc[team_df['win_percentage'].idxmax(), 'team_name']
        
        if not player_df.empty:
            report['player_analysis'] = {
                'total_players': len(player_df),
                'avg_goals': float(player_df['goals'].mean()) if 'goals' in player_df.columns else 0,
                'avg_assists': float(player_df['assists'].mean()) if 'assists' in player_df.columns else 0,
                'avg_rating': float(player_df['rating'].mean()) if 'rating' in player_df.columns else 0
            }
            
            if 'rating' in player_df.columns:
                top_player = player_df.loc[player_df['rating'].idxmax()]
                report['player_analysis']['top_player'] = {
                    'name': top_player['player_name'],
                    'rating': float(top_player['rating']),
                    'team': top_player['team_name'] if 'team_name' in player_df.columns else 'Unknown'
                }
        
        # Save report
        output_dir = Path('data/analysis')
        output_dir.mkdir(exist_ok=True)
        
        with open(output_dir / 'analysis_summary_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"Summary report saved to {output_dir / 'analysis_summary_report.json'}")
        return report
    
    def run_complete_analysis(self, season_year=2023):
        """Run complete data analysis."""
        self.logger.info(f"Starting complete analysis for season {season_year}")
        
        # Try to connect to database
        db_connected = self.connect_db()
        
        if db_connected:
            overview = self.get_database_overview()
            if overview:
                self.logger.info("Database overview:")
                for table, count in overview.items():
                    self.logger.info(f"  {table}: {count} records")
        
        # Analyze team performance
        team_df = self.analyze_team_performance(season_year)
        
        # Analyze player performance
        player_df = self.analyze_player_performance(season_year)
        
        # Create visualizations
        if not team_df.empty or not player_df.empty:
            fig = self.create_visualizations(team_df, player_df)
            plt.show()
        
        # Generate summary report
        report = self.generate_summary_report(team_df, player_df)
        
        # Print summary
        print("\n" + "="*50)
        print("📊 SOCCER DATA ANALYSIS SUMMARY")
        print("="*50)
        print(f"Analysis Date: {report['analysis_timestamp']}")
        print(f"Data Source: {report['data_summary']['data_source'].upper()}")
        print(f"Teams Analyzed: {report['data_summary']['teams_analyzed']}")
        print(f"Players Analyzed: {report['data_summary']['players_analyzed']}")
        
        if 'team_analysis' in report:
            print(f"\n🏆 Team Analysis:")
            print(f"  Countries Represented: {report['team_analysis']['countries_represented']}")
            if 'avg_win_percentage' in report['team_analysis']:
                print(f"  Average Win Rate: {report['team_analysis']['avg_win_percentage']:.1f}%")
        
        if 'player_analysis' in report:
            print(f"\n⚽ Player Analysis:")
            print(f"  Average Goals: {report['player_analysis']['avg_goals']:.1f}")
            print(f"  Average Assists: {report['player_analysis']['avg_assists']:.1f}")
            if 'top_player' in report['player_analysis']:
                top = report['player_analysis']['top_player']
                print(f"  Top Player: {top['name']} (Rating: {top['rating']:.1f})")
        
        print("\n📁 Output Files:")
        print("  - Visualization: data/analysis/soccer_analysis_overview.png")
        print("  - Summary Report: data/analysis/analysis_summary_report.json")
        print("="*50)
        
        return report

def main():
    """Main function to run the analysis."""
    print("🚀 Starting Soccer Data Analysis...")
    print("📊 This will analyze your soccer intelligence data")
    print()
    
    analyzer = SoccerDataAnalyzer()
    
    try:
        report = analyzer.run_complete_analysis(season_year=2023)
        print("\n✅ Analysis completed successfully!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
