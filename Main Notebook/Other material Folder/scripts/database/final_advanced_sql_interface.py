#!/usr/bin/env python3
"""
Final Advanced SQL Interface
Comprehensive SQL interface for querying Manchester City advanced statistics with expected goals
"""

import sqlite3
import pandas as pd
from datetime import datetime
import sys

class FinalAdvancedSQL:
    """Comprehensive SQL interface for final advanced statistics."""
    
    def __init__(self):
        """Initialize database connection."""
        self.db_path = "data/final_advanced_stats/manchester_city_final_advanced_2023_24.db"
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
    
    def show_advanced_queries(self):
        """Show comprehensive advanced statistics queries."""
        print("\n" + "="*100)
        print("🎯 ADVANCED STATISTICS QUERIES - MANCHESTER CITY 2023-24")
        print("="*100)
        
        queries = [
            {
                "title": "🥅 Expected Goals (xG) Analysis",
                "query": """
                SELECT 
                    player_name,
                    matches_played,
                    goals,
                    ROUND(expected_goals, 2) as xg,
                    ROUND(goals - expected_goals, 2) as goals_vs_xg,
                    ROUND(goals_per_90, 2) as goals_per_90,
                    ROUND(xg_per_90, 2) as xg_per_90,
                    ROUND(conversion_rate, 1) as conversion_rate
                FROM player_season_summary 
                WHERE matches_played >= 10
                ORDER BY expected_goals DESC
                LIMIT 15
                """
            },
            {
                "title": "🎯 Shot Efficiency and Expected Goals",
                "query": """
                SELECT 
                    player_name,
                    shots_total,
                    shots_on_target,
                    goals,
                    ROUND(expected_goals, 2) as xg,
                    ROUND(shot_accuracy, 1) as shot_accuracy,
                    ROUND(conversion_rate, 1) as conversion_rate,
                    ROUND((goals / expected_goals * 100), 1) as xg_efficiency
                FROM player_season_summary 
                WHERE shots_total >= 20
                ORDER BY xg_efficiency DESC
                """
            },
            {
                "title": "🅰️ Expected Assists (xA) Analysis",
                "query": """
                SELECT 
                    player_name,
                    assists,
                    ROUND(expected_assists, 2) as xa,
                    ROUND(assists - expected_assists, 2) as assists_vs_xa,
                    key_passes,
                    ROUND(key_passes_per_90, 2) as key_passes_per_90,
                    ROUND(assists_per_90, 2) as assists_per_90,
                    ROUND(xa_per_90, 2) as xa_per_90
                FROM player_season_summary 
                WHERE matches_played >= 10
                ORDER BY expected_assists DESC
                LIMIT 15
                """
            },
            {
                "title": "⚡ Performance vs Expectations",
                "query": """
                SELECT 
                    player_name,
                    goals + assists as goal_contributions,
                    ROUND(expected_goals + expected_assists, 2) as expected_contributions,
                    ROUND((goals + assists) - (expected_goals + expected_assists), 2) as overperformance,
                    ROUND(average_rating, 1) as avg_rating,
                    matches_played
                FROM player_season_summary 
                WHERE matches_played >= 15
                ORDER BY overperformance DESC
                """
            },
            {
                "title": "📊 Comprehensive Player Performance",
                "query": """
                SELECT 
                    player_name,
                    matches_played,
                    goals,
                    assists,
                    ROUND(expected_goals, 2) as xg,
                    ROUND(expected_assists, 2) as xa,
                    ROUND(pass_accuracy, 1) as pass_acc,
                    tackles_total,
                    interceptions,
                    ROUND(average_rating, 1) as rating
                FROM player_season_summary 
                ORDER BY average_rating DESC
                LIMIT 20
                """
            },
            {
                "title": "🏃 Physical and Defensive Metrics",
                "query": """
                SELECT 
                    player_name,
                    matches_played,
                    tackles_total,
                    tackles_won,
                    ROUND(tackle_success_rate, 1) as tackle_success,
                    interceptions,
                    clearances,
                    yellow_cards,
                    red_cards
                FROM player_season_summary 
                WHERE matches_played >= 10
                ORDER BY tackles_total DESC
                LIMIT 15
                """
            },
            {
                "title": "📈 Match-by-Match xG Progression (Top Scorer)",
                "query": """
                SELECT 
                    match_number,
                    opponent,
                    competition,
                    goals,
                    ROUND(expected_goals, 2) as xg,
                    shots_total,
                    shots_on_target,
                    ROUND(rating, 1) as rating
                FROM advanced_match_statistics 
                WHERE player_name = (
                    SELECT player_name 
                    FROM player_season_summary 
                    ORDER BY goals DESC 
                    LIMIT 1
                )
                AND minutes_played > 0
                ORDER BY match_number
                LIMIT 20
                """
            },
            {
                "title": "🎪 Big Chances and Clinical Finishing",
                "query": """
                SELECT 
                    player_name,
                    SUM(big_chances_created) as big_chances_created,
                    SUM(big_chances_missed) as big_chances_missed,
                    SUM(goals) as goals,
                    ROUND(SUM(expected_goals), 2) as total_xg,
                    ROUND(AVG(shot_accuracy), 1) as avg_shot_accuracy,
                    COUNT(*) as matches
                FROM advanced_match_statistics 
                WHERE minutes_played > 0
                GROUP BY player_name
                HAVING matches >= 10
                ORDER BY big_chances_created DESC
                LIMIT 15
                """
            }
        ]
        
        for i, query_info in enumerate(queries, 1):
            print(f"\n{i}. {query_info['title']}")
            print("-" * 80)
            self.execute_query(query_info['query'])
            
            if i < len(queries):
                input("\nPress Enter to continue to next query...")
    
    def interactive_mode(self):
        """Start interactive SQL mode."""
        print("\n" + "="*100)
        print("🔍 INTERACTIVE SQL MODE - Manchester City Final Advanced Statistics")
        print("="*100)
        print("Available tables:")
        print("  • comprehensive_players - Player information and details")
        print("  • advanced_match_statistics - Match-by-match player performance")
        print("  • player_season_summary - Aggregated season statistics")
        print("\nType 'help' for sample queries, 'tables' to see schemas, 'quit' to exit")
        print("-" * 100)
        
        while True:
            try:
                query = input("\nSQL> ").strip()
                
                if query.lower() == 'quit':
                    break
                elif query.lower() == 'help':
                    self.show_sample_interactive_queries()
                elif query.lower() == 'tables':
                    self.show_table_schemas()
                elif query:
                    self.execute_query(query)
                    
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except EOFError:
                break
    
    def show_sample_interactive_queries(self):
        """Show sample queries for interactive mode."""
        print("\n📋 SAMPLE INTERACTIVE QUERIES:")
        
        samples = [
            "-- Top xG performers",
            "SELECT player_name, goals, expected_goals FROM player_season_summary ORDER BY expected_goals DESC LIMIT 10;",
            "",
            "-- Players outperforming xG",
            "SELECT player_name, goals - expected_goals as overperformance FROM player_season_summary WHERE matches_played >= 10 ORDER BY overperformance DESC;",
            "",
            "-- Best passers",
            "SELECT player_name, pass_accuracy, passes_total FROM player_season_summary WHERE matches_played >= 15 ORDER BY pass_accuracy DESC;",
            "",
            "-- Defensive leaders",
            "SELECT player_name, tackles_total, interceptions, clearances FROM player_season_summary ORDER BY tackles_total DESC LIMIT 10;",
            "",
            "-- Match performance for specific player",
            "SELECT match_number, opponent, goals, expected_goals, rating FROM advanced_match_statistics WHERE player_name = 'Erling Haaland' ORDER BY match_number;"
        ]
        
        for sample in samples:
            print(sample)
    
    def show_table_schemas(self):
        """Show database table schemas."""
        print("\n📋 DATABASE SCHEMAS:")
        
        tables = [
            'comprehensive_players',
            'advanced_match_statistics', 
            'player_season_summary'
        ]
        
        for table in tables:
            print(f"\n🗄️ {table.upper()}:")
            try:
                schema_df = pd.read_sql_query(f"PRAGMA table_info({table})", self.conn)
                if not schema_df.empty:
                    print(schema_df[['name', 'type']].to_string(index=False))
                else:
                    print("Table not found")
            except Exception as e:
                print(f"Error: {e}")
    
    def run_specific_analysis(self, analysis_type: str):
        """Run specific analysis queries."""
        analyses = {
            'xg': {
                'title': '⚽ Expected Goals Deep Dive',
                'queries': [
                    {
                        'name': 'xG Leaders and Efficiency',
                        'query': """
                        SELECT 
                            player_name,
                            goals,
                            ROUND(expected_goals, 2) as xg,
                            ROUND(goals - expected_goals, 2) as overperformance,
                            ROUND(goals / expected_goals * 100, 1) as xg_efficiency,
                            shots_total,
                            ROUND(conversion_rate, 1) as conversion_rate
                        FROM player_season_summary 
                        WHERE expected_goals >= 1.0
                        ORDER BY expected_goals DESC
                        """
                    },
                    {
                        'name': 'xG vs Actual Goals by Match',
                        'query': """
                        SELECT 
                            player_name,
                            COUNT(*) as matches_with_xg,
                            SUM(goals) as total_goals,
                            ROUND(SUM(expected_goals), 2) as total_xg,
                            ROUND(AVG(expected_goals), 2) as avg_xg_per_match,
                            ROUND(SUM(goals) - SUM(expected_goals), 2) as total_overperformance
                        FROM advanced_match_statistics 
                        WHERE expected_goals > 0
                        GROUP BY player_name
                        ORDER BY total_xg DESC
                        LIMIT 15
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
                            ROUND(average_rating, 1) as avg_rating,
                            ROUND(best_rating, 1) as best_rating,
                            goals + assists as contributions,
                            ROUND(expected_goals + expected_assists, 2) as expected_contributions
                        FROM player_season_summary
                        WHERE matches_played >= 10
                        ORDER BY average_rating DESC
                        LIMIT 15
                        """
                    }
                ]
            },
            'assists': {
                'title': '🅰️ Expected Assists Analysis',
                'queries': [
                    {
                        'name': 'xA Leaders and Creativity',
                        'query': """
                        SELECT 
                            player_name,
                            assists,
                            ROUND(expected_assists, 2) as xa,
                            ROUND(assists - expected_assists, 2) as assist_overperformance,
                            key_passes,
                            ROUND(key_passes_per_90, 2) as key_passes_per_90
                        FROM player_season_summary 
                        WHERE expected_assists >= 0.5
                        ORDER BY expected_assists DESC
                        """
                    }
                ]
            }
        }
        
        if analysis_type in analyses:
            analysis = analyses[analysis_type]
            print(f"\n{analysis['title']}")
            print("="*80)
            
            for query_info in analysis['queries']:
                print(f"\n📈 {query_info['name']}:")
                print("-" * 60)
                self.execute_query(query_info['query'])
        else:
            print(f"❌ Analysis type '{analysis_type}' not found")
            print("Available analyses: xg, performance, assists")
    
    def close(self):
        """Close database connection."""
        self.conn.close()

def main():
    """Main execution function."""
    sql_interface = FinalAdvancedSQL()
    
    if len(sys.argv) > 1:
        analysis_type = sys.argv[1]
        sql_interface.run_specific_analysis(analysis_type)
    else:
        print("🎯 Manchester City Final Advanced Statistics Database")
        print("Choose an option:")
        print("1. View comprehensive advanced queries")
        print("2. Interactive SQL mode")
        print("3. Expected Goals analysis")
        print("4. Performance analysis")
        print("5. Expected Assists analysis")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '1':
            sql_interface.show_advanced_queries()
        elif choice == '2':
            sql_interface.interactive_mode()
        elif choice == '3':
            sql_interface.run_specific_analysis('xg')
        elif choice == '4':
            sql_interface.run_specific_analysis('performance')
        elif choice == '5':
            sql_interface.run_specific_analysis('assists')
        else:
            print("Invalid choice")
    
    sql_interface.close()

if __name__ == "__main__":
    main()
