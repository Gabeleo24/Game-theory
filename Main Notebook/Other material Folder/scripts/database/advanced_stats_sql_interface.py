#!/usr/bin/env python3
"""
Advanced Statistics SQL Interface
Interactive SQL interface for querying Manchester City advanced statistics
"""

import sqlite3
import pandas as pd
from datetime import datetime
import sys

class AdvancedStatsSQL:
    """Interactive SQL interface for advanced statistics."""
    
    def __init__(self):
        """Initialize database connection."""
        self.db_path = "data/manchester_city_advanced_stats/manchester_city_advanced_2023_24.db"
        self.conn = sqlite3.connect(self.db_path)
        
    def execute_query(self, query: str, params=None):
        """Execute SQL query and return formatted results."""
        try:
            if params:
                df = pd.read_sql_query(query, self.conn, params=params)
            else:
                df = pd.read_sql_query(query, self.conn)
            
            if df.empty:
                print("No results found.")
                return
            
            # Format numeric columns
            for col in df.columns:
                if df[col].dtype in ['float64', 'float32']:
                    df[col] = df[col].round(2)
            
            print(df.to_string(index=False))
            print(f"\n📊 {len(df)} rows returned")
            
        except Exception as e:
            print(f"❌ Error executing query: {e}")
    
    def show_sample_queries(self):
        """Show sample queries for advanced statistics."""
        print("\n" + "="*80)
        print("🎯 ADVANCED STATISTICS - SAMPLE QUERIES")
        print("="*80)
        
        queries = [
            {
                "title": "🏆 Top Goal Scorers with Expected Goals",
                "query": """
                SELECT 
                    player_name,
                    total_goals,
                    total_xg,
                    ROUND(total_goals - total_xg, 2) as goals_vs_xg,
                    matches_played,
                    ROUND(total_goals * 90.0 / SUM(minutes_played), 2) as goals_per_90
                FROM player_season_summary 
                ORDER BY total_goals DESC 
                LIMIT 10
                """
            },
            {
                "title": "⚽ Expected Goals Analysis by Match",
                "query": """
                SELECT 
                    match_date,
                    opponent,
                    goals_for,
                    expected_goals as xg,
                    ROUND(goals_for - expected_goals, 2) as goals_vs_xg,
                    possession_percentage,
                    shots_total,
                    shot_accuracy
                FROM advanced_fixtures 
                ORDER BY match_date DESC 
                LIMIT 15
                """
            },
            {
                "title": "🎯 Shot Conversion Analysis",
                "query": """
                SELECT 
                    player_name,
                    SUM(goals) as goals,
                    SUM(shots_total) as shots,
                    ROUND(AVG(shot_accuracy), 1) as avg_shot_accuracy,
                    ROUND(SUM(goals) * 100.0 / SUM(shots_total), 1) as conversion_rate,
                    SUM(expected_goals) as xg
                FROM advanced_player_match_stats 
                WHERE shots_total > 0
                GROUP BY player_name
                HAVING SUM(shots_total) >= 10
                ORDER BY conversion_rate DESC
                """
            },
            {
                "title": "📊 Passing Statistics Leaders",
                "query": """
                SELECT 
                    player_name,
                    matches_played,
                    ROUND(AVG(pass_accuracy), 1) as avg_pass_accuracy,
                    ROUND(SUM(passes_total) / matches_played, 0) as avg_passes_per_match,
                    SUM(assists) as assists,
                    SUM(expected_assists) as xa
                FROM player_season_summary
                WHERE matches_played >= 10
                ORDER BY avg_pass_accuracy DESC
                LIMIT 10
                """
            },
            {
                "title": "🛡️ Defensive Performance",
                "query": """
                SELECT 
                    player_name,
                    matches_played,
                    SUM(tackles_total) as total_tackles,
                    SUM(interceptions) as total_interceptions,
                    ROUND(SUM(tackles_total) / matches_played, 1) as tackles_per_match,
                    ROUND(SUM(interceptions) / matches_played, 1) as interceptions_per_match
                FROM advanced_player_match_stats
                WHERE minutes_played > 0
                GROUP BY player_name
                HAVING matches_played >= 10
                ORDER BY total_tackles DESC
                LIMIT 10
                """
            },
            {
                "title": "📈 Team Performance vs Expected Goals",
                "query": """
                SELECT 
                    'Season Total' as metric,
                    SUM(goals_for) as actual_goals,
                    ROUND(SUM(expected_goals), 2) as expected_goals,
                    ROUND(SUM(goals_for) - SUM(expected_goals), 2) as overperformance,
                    ROUND(AVG(possession_percentage), 1) as avg_possession,
                    COUNT(*) as matches
                FROM advanced_fixtures
                UNION ALL
                SELECT 
                    'Home Matches' as metric,
                    SUM(goals_for) as actual_goals,
                    ROUND(SUM(expected_goals), 2) as expected_goals,
                    ROUND(SUM(goals_for) - SUM(expected_goals), 2) as overperformance,
                    ROUND(AVG(possession_percentage), 1) as avg_possession,
                    COUNT(*) as matches
                FROM advanced_fixtures
                WHERE home_away = 'home'
                """
            }
        ]
        
        for i, query_info in enumerate(queries, 1):
            print(f"\n{i}. {query_info['title']}")
            print("-" * 60)
            self.execute_query(query_info['query'])
            
            if i < len(queries):
                input("\nPress Enter to continue to next query...")
    
    def interactive_mode(self):
        """Start interactive SQL mode."""
        print("\n" + "="*80)
        print("🔍 INTERACTIVE SQL MODE - Manchester City Advanced Statistics")
        print("="*80)
        print("Available tables:")
        print("  • advanced_fixtures - Match-level team statistics")
        print("  • advanced_player_match_stats - Player performance per match")
        print("  • player_season_summary - Aggregated player statistics (VIEW)")
        print("  • team_match_summary - Team performance summary (VIEW)")
        print("\nType 'help' for sample queries, 'tables' to see table schemas, 'quit' to exit")
        print("-" * 80)
        
        while True:
            try:
                query = input("\nSQL> ").strip()
                
                if query.lower() == 'quit':
                    break
                elif query.lower() == 'help':
                    self.show_sample_queries()
                elif query.lower() == 'tables':
                    self.show_table_schemas()
                elif query:
                    self.execute_query(query)
                    
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except EOFError:
                break
    
    def show_table_schemas(self):
        """Show database table schemas."""
        print("\n📋 DATABASE SCHEMAS:")
        
        tables = [
            'advanced_fixtures',
            'advanced_player_match_stats',
            'player_season_stats'
        ]
        
        for table in tables:
            print(f"\n🗄️ {table.upper()}:")
            schema_df = pd.read_sql_query(f"PRAGMA table_info({table})", self.conn)
            if not schema_df.empty:
                print(schema_df[['name', 'type']].to_string(index=False))
            else:
                print("Table not found")
    
    def run_specific_analysis(self, analysis_type: str):
        """Run specific analysis queries."""
        analyses = {
            'xg': {
                'title': '⚽ Expected Goals Analysis',
                'queries': [
                    {
                        'name': 'Team xG Performance',
                        'query': """
                        SELECT 
                            'Overall' as period,
                            COUNT(*) as matches,
                            SUM(goals_for) as goals,
                            ROUND(SUM(expected_goals), 2) as xg,
                            ROUND(SUM(goals_for) - SUM(expected_goals), 2) as difference,
                            ROUND((SUM(goals_for) - SUM(expected_goals)) / COUNT(*), 2) as diff_per_match
                        FROM advanced_fixtures
                        """
                    },
                    {
                        'name': 'Player xG Leaders',
                        'query': """
                        SELECT 
                            player_name,
                            SUM(goals) as goals,
                            ROUND(SUM(expected_goals), 2) as xg,
                            ROUND(SUM(goals) - SUM(expected_goals), 2) as overperformance,
                            COUNT(*) as matches
                        FROM advanced_player_match_stats
                        WHERE expected_goals > 0
                        GROUP BY player_name
                        ORDER BY xg DESC
                        LIMIT 10
                        """
                    }
                ]
            },
            'performance': {
                'title': '📊 Performance Analysis',
                'queries': [
                    {
                        'name': 'Top Rated Players',
                        'query': """
                        SELECT 
                            player_name,
                            matches_played,
                            avg_rating,
                            total_goals,
                            total_assists,
                            ROUND((total_goals + total_assists) / matches_played, 2) as contributions_per_match
                        FROM player_season_summary
                        WHERE matches_played >= 10
                        ORDER BY avg_rating DESC
                        LIMIT 10
                        """
                    }
                ]
            }
        }
        
        if analysis_type in analyses:
            analysis = analyses[analysis_type]
            print(f"\n{analysis['title']}")
            print("="*60)
            
            for query_info in analysis['queries']:
                print(f"\n📈 {query_info['name']}:")
                print("-" * 40)
                self.execute_query(query_info['query'])
        else:
            print(f"❌ Analysis type '{analysis_type}' not found")
            print("Available analyses: xg, performance")
    
    def close(self):
        """Close database connection."""
        self.conn.close()

def main():
    """Main execution function."""
    sql_interface = AdvancedStatsSQL()
    
    if len(sys.argv) > 1:
        analysis_type = sys.argv[1]
        sql_interface.run_specific_analysis(analysis_type)
    else:
        print("🎯 Manchester City Advanced Statistics Database")
        print("Choose an option:")
        print("1. View sample queries")
        print("2. Interactive SQL mode")
        print("3. Expected Goals analysis")
        print("4. Performance analysis")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == '1':
            sql_interface.show_sample_queries()
        elif choice == '2':
            sql_interface.interactive_mode()
        elif choice == '3':
            sql_interface.run_specific_analysis('xg')
        elif choice == '4':
            sql_interface.run_specific_analysis('performance')
        else:
            print("Invalid choice")
    
    sql_interface.close()

if __name__ == "__main__":
    main()
