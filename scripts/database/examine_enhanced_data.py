#!/usr/bin/env python3
"""
Examine Enhanced Database Data
Check what data was collected and what statistics are available
"""

import sqlite3
import pandas as pd
import json
from datetime import datetime

def examine_database():
    """Examine the enhanced database content."""
    db_path = "data/manchester_city_enhanced_database/manchester_city_enhanced_2023_24.db"
    
    try:
        conn = sqlite3.connect(db_path)
        
        print("="*80)
        print("🔍 ENHANCED DATABASE EXAMINATION")
        print("="*80)
        
        # Check fixtures
        print("\n📅 FIXTURES:")
        fixtures_df = pd.read_sql_query("SELECT * FROM enhanced_fixtures", conn)
        print(fixtures_df.to_string(index=False))
        
        # Check team statistics
        print("\n📊 TEAM MATCH STATISTICS:")
        team_stats_df = pd.read_sql_query("SELECT * FROM enhanced_team_match_stats", conn)
        print(team_stats_df.to_string(index=False))
        
        # Check player statistics
        print("\n👤 PLAYER MATCH STATISTICS:")
        player_stats_df = pd.read_sql_query("SELECT * FROM enhanced_player_match_stats", conn)
        if not player_stats_df.empty:
            print(player_stats_df.to_string(index=False))
        else:
            print("No player statistics found")
        
        # Check raw statistics
        print("\n📈 RAW STATISTICS:")
        raw_stats_df = pd.read_sql_query("SELECT * FROM raw_statistics", conn)
        if not raw_stats_df.empty:
            print(raw_stats_df.to_string(index=False))
        else:
            print("No raw statistics found")
        
        # Check table schemas
        print("\n🗄️ TABLE SCHEMAS:")
        tables = ['enhanced_fixtures', 'enhanced_team_match_stats', 'enhanced_player_match_stats', 'raw_statistics']
        
        for table in tables:
            print(f"\n{table.upper()}:")
            schema_df = pd.read_sql_query(f"PRAGMA table_info({table})", conn)
            print(schema_df[['name', 'type', 'notnull', 'dflt_value']].to_string(index=False))
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error examining database: {e}")

def main():
    """Main execution function."""
    examine_database()

if __name__ == "__main__":
    main()
