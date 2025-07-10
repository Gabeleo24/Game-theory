#!/usr/bin/env python3
"""
Examine Real Data Structure from SportMonks API
Deep dive into the actual data structure to understand what we have
"""

import sqlite3
import pandas as pd
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def examine_real_data():
    """Examine the real data structure from SportMonks API."""
    db_path = "data/working_sportmonks_database/manchester_city_working_2023_24.db"
    
    conn = sqlite3.connect(db_path)
    
    print("="*100)
    print("🔍 DEEP DIVE: REAL SPORTMONKS DATA STRUCTURE")
    print("="*100)
    
    # Get all player data
    players_df = pd.read_sql_query("SELECT * FROM working_players LIMIT 3", conn)
    
    for i, player_row in players_df.iterrows():
        detailed_data = json.loads(player_row['detailed_data'])
        player_name = detailed_data.get('display_name', 'Unknown')
        
        print(f"\n👤 PLAYER {i+1}: {player_name}")
        print("-" * 60)
        
        # Show top-level structure
        print(f"Top-level keys: {list(detailed_data.keys())}")
        
        # Examine statistics structure
        if 'statistics' in detailed_data:
            stats = detailed_data['statistics']
            print(f"Statistics type: {type(stats)}")
            print(f"Statistics count: {len(stats) if isinstance(stats, list) else 'Not a list'}")
            
            if isinstance(stats, list) and stats:
                print(f"\nFirst statistic structure:")
                first_stat = stats[0]
                print(f"  Keys: {list(first_stat.keys())}")
                
                for key, value in first_stat.items():
                    if key == 'details' and isinstance(value, list):
                        print(f"  {key}: list with {len(value)} items")
                        if value:
                            print(f"    First detail: {value[0]}")
                    else:
                        print(f"  {key}: {value}")
                
                # Show a few more statistics
                print(f"\nSample of statistics (first 3):")
                for j, stat in enumerate(stats[:3]):
                    print(f"  Stat {j+1}:")
                    print(f"    Keys: {list(stat.keys())}")
                    if 'details' in stat and stat['details']:
                        details = stat['details']
                        print(f"    Details count: {len(details)}")
                        if details:
                            detail = details[0]
                            print(f"    First detail keys: {list(detail.keys())}")
                            print(f"    First detail: {detail}")
            
            # Look for patterns in all statistics
            print(f"\nAll statistics analysis:")
            all_type_ids = set()
            all_detail_keys = set()
            
            for stat in stats:
                if 'details' in stat and isinstance(stat['details'], list):
                    for detail in stat['details']:
                        if 'type_id' in detail:
                            all_type_ids.add(detail['type_id'])
                        all_detail_keys.update(detail.keys())
            
            print(f"  Unique type_ids found: {sorted(all_type_ids)}")
            print(f"  All detail keys found: {sorted(all_detail_keys)}")
        
        print("\n" + "="*60)
    
    # Check if there are any fixtures
    print(f"\n🏟️ FIXTURES DATA:")
    fixtures_df = pd.read_sql_query("SELECT COUNT(*) as count FROM working_fixtures", conn)
    print(f"Fixtures count: {fixtures_df.iloc[0]['count']}")
    
    # Check endpoints
    print(f"\n🔗 WORKING ENDPOINTS:")
    endpoints_df = pd.read_sql_query("SELECT * FROM working_endpoints", conn)
    for _, endpoint in endpoints_df.iterrows():
        sample_data = json.loads(endpoint['sample_data'])
        print(f"  {endpoint['endpoint_name']}: {endpoint['working']} - {sample_data}")
    
    conn.close()

def create_working_advanced_database():
    """Create a working advanced database with the actual data structure."""
    logger.info("🗄️ Creating working advanced database...")
    
    source_db = "data/working_sportmonks_database/manchester_city_working_2023_24.db"
    target_db = "data/real_working_advanced_stats/manchester_city_real_working_2023_24.db"
    
    import os
    os.makedirs(os.path.dirname(target_db), exist_ok=True)
    
    source_conn = sqlite3.connect(source_db)
    target_conn = sqlite3.connect(target_db)
    target_cursor = target_conn.cursor()
    
    # Create tables based on actual data structure
    target_cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_statistics_raw (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER,
            player_name TEXT,
            statistic_id INTEGER,
            season_id INTEGER,
            position_id INTEGER,
            jersey_number INTEGER,
            has_values BOOLEAN,
            detail_id INTEGER,
            type_id INTEGER,
            value_json TEXT,
            value_total INTEGER,
            value_home INTEGER,
            value_away INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    target_cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_summary_real (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER,
            player_name TEXT,
            total_statistics INTEGER,
            unique_type_ids TEXT,
            sample_statistics TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Process players
    players_df = pd.read_sql_query("SELECT * FROM working_players", source_conn)
    
    total_stats_processed = 0
    
    for _, player_row in players_df.iterrows():
        detailed_data = json.loads(player_row['detailed_data'])
        player_id = detailed_data.get('id')
        player_name = detailed_data.get('display_name', 'Unknown')
        
        if 'statistics' in detailed_data and detailed_data['statistics']:
            stats = detailed_data['statistics']
            
            unique_type_ids = set()
            sample_stats = []
            
            for stat in stats:
                stat_id = stat.get('id')
                season_id = stat.get('season_id')
                position_id = stat.get('position_id')
                jersey_number = stat.get('jersey_number')
                has_values = stat.get('has_values', False)
                
                if 'details' in stat and isinstance(stat['details'], list):
                    for detail in stat['details']:
                        detail_id = detail.get('id')
                        type_id = detail.get('type_id')
                        value = detail.get('value', {})
                        
                        unique_type_ids.add(type_id)
                        
                        # Extract values
                        value_total = 0
                        value_home = 0
                        value_away = 0
                        
                        if isinstance(value, dict):
                            value_total = value.get('total', 0) or 0
                            value_home = value.get('home', 0) or 0
                            value_away = value.get('away', 0) or 0
                        elif isinstance(value, (int, float)):
                            value_total = value
                        
                        # Store raw statistic
                        target_cursor.execute('''
                            INSERT INTO player_statistics_raw 
                            (player_id, player_name, statistic_id, season_id, position_id, 
                             jersey_number, has_values, detail_id, type_id, value_json,
                             value_total, value_home, value_away)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            player_id, player_name, stat_id, season_id, position_id,
                            jersey_number, has_values, detail_id, type_id, json.dumps(value),
                            value_total, value_home, value_away
                        ))
                        
                        total_stats_processed += 1
                        
                        # Collect sample for summary
                        if len(sample_stats) < 5:
                            sample_stats.append({
                                'type_id': type_id,
                                'value': value,
                                'detail_id': detail_id
                            })
            
            # Insert player summary
            target_cursor.execute('''
                INSERT INTO player_summary_real 
                (player_id, player_name, total_statistics, unique_type_ids, sample_statistics)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                player_id, player_name, len(stats),
                json.dumps(list(unique_type_ids)),
                json.dumps(sample_stats)
            ))
    
    target_conn.commit()
    source_conn.close()
    target_conn.close()
    
    logger.info(f"✅ Created working database with {total_stats_processed} statistics")
    logger.info(f"💾 Database location: {target_db}")
    
    return target_db

def analyze_working_database(db_path: str):
    """Analyze the working database."""
    logger.info("📊 Analyzing working database...")
    
    conn = sqlite3.connect(db_path)
    
    print(f"\n" + "="*100)
    print("⚽ WORKING ADVANCED STATISTICS DATABASE ANALYSIS")
    print("="*100)
    
    # Database summary
    total_stats = pd.read_sql_query("SELECT COUNT(*) as count FROM player_statistics_raw", conn).iloc[0]['count']
    total_players = pd.read_sql_query("SELECT COUNT(*) as count FROM player_summary_real", conn).iloc[0]['count']
    
    print(f"📊 Database Summary:")
    print(f"   • Total statistics records: {total_stats}")
    print(f"   • Total players: {total_players}")
    
    # Type ID analysis
    print(f"\n🔢 STATISTIC TYPE ANALYSIS:")
    type_analysis = pd.read_sql_query("""
        SELECT type_id, COUNT(*) as frequency, 
               SUM(value_total) as total_value,
               AVG(value_total) as avg_value,
               COUNT(DISTINCT player_id) as players_with_stat
        FROM player_statistics_raw 
        WHERE value_total > 0
        GROUP BY type_id 
        ORDER BY frequency DESC
        LIMIT 20
    """, conn)
    print(type_analysis.to_string(index=False))
    
    # Player performance
    print(f"\n🏆 PLAYER PERFORMANCE (Top Type IDs):")
    player_performance = pd.read_sql_query("""
        SELECT player_name, type_id, SUM(value_total) as total_value
        FROM player_statistics_raw 
        WHERE type_id IN (SELECT type_id FROM player_statistics_raw 
                         WHERE value_total > 0 
                         GROUP BY type_id 
                         ORDER BY COUNT(*) DESC 
                         LIMIT 5)
        AND value_total > 0
        GROUP BY player_name, type_id
        ORDER BY type_id, total_value DESC
    """, conn)
    print(player_performance.to_string(index=False))
    
    # Sample data for understanding
    print(f"\n📋 SAMPLE STATISTICS DATA:")
    sample_data = pd.read_sql_query("""
        SELECT player_name, type_id, value_total, value_home, value_away, value_json
        FROM player_statistics_raw 
        WHERE value_total > 0
        ORDER BY value_total DESC
        LIMIT 10
    """, conn)
    print(sample_data.to_string(index=False))
    
    print(f"\n🎯 REAL WORKING ADVANCED METRICS:")
    print("   • Raw player statistics with type IDs")
    print("   • Home/Away value breakdown")
    print("   • Player performance analysis")
    print("   • Frequency analysis of statistic types")
    print("   • SQL queryable with real SportMonks data")
    print("="*100)
    
    conn.close()

def main():
    """Main execution function."""
    # Examine the real data structure
    examine_real_data()
    
    # Create working advanced database
    working_db_path = create_working_advanced_database()
    
    # Analyze the working database
    analyze_working_database(working_db_path)
    
    logger.info("🎉 Real data structure analysis completed!")

if __name__ == "__main__":
    main()
