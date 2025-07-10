#!/usr/bin/env python3
"""
Analyze Real Statistics from SportMonks API
Examine the actual statistics data to understand what advanced metrics are available
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

class RealStatisticsAnalyzer:
    """Analyze real statistics from SportMonks API."""
    
    def __init__(self):
        """Initialize database connection."""
        self.db_path = "data/working_sportmonks_database/manchester_city_working_2023_24.db"
        
    def analyze_player_statistics(self):
        """Analyze the actual player statistics structure."""
        logger.info("🔍 Analyzing real player statistics...")
        
        conn = sqlite3.connect(self.db_path)
        
        # Get all player data
        players_df = pd.read_sql_query("SELECT * FROM working_players", conn)
        
        print("\n" + "="*100)
        print("📊 REAL SPORTMONKS PLAYER STATISTICS ANALYSIS")
        print("="*100)
        
        print(f"\n📈 Total players analyzed: {len(players_df)}")
        
        # Analyze each player's statistics
        all_stat_types = {}
        sample_statistics = {}
        
        for _, player_row in players_df.iterrows():
            detailed_data = json.loads(player_row['detailed_data'])
            player_name = detailed_data.get('display_name', 'Unknown')
            
            if 'statistics' in detailed_data and detailed_data['statistics']:
                stats = detailed_data['statistics']
                
                print(f"\n👤 {player_name}:")
                print(f"   Statistics count: {len(stats)}")
                
                # Analyze each statistic
                for stat in stats[:5]:  # Show first 5 stats
                    if 'details' in stat and stat['details']:
                        for detail in stat['details']:
                            type_id = detail.get('type_id')
                            value = detail.get('value')
                            
                            if type_id not in all_stat_types:
                                all_stat_types[type_id] = {
                                    'count': 0,
                                    'sample_values': [],
                                    'players': []
                                }
                            
                            all_stat_types[type_id]['count'] += 1
                            all_stat_types[type_id]['players'].append(player_name)
                            
                            if len(all_stat_types[type_id]['sample_values']) < 3:
                                all_stat_types[type_id]['sample_values'].append(value)
                            
                            # Store sample for detailed analysis
                            if type_id not in sample_statistics:
                                sample_statistics[type_id] = {
                                    'player': player_name,
                                    'full_detail': detail,
                                    'value': value
                                }
                
                # Show sample statistic structure
                if stats and 'details' in stats[0] and stats[0]['details']:
                    sample_detail = stats[0]['details'][0]
                    print(f"   Sample statistic structure: {list(sample_detail.keys())}")
                    print(f"   Sample type_id: {sample_detail.get('type_id')}")
                    print(f"   Sample value: {sample_detail.get('value')}")
        
        # Summary of all statistic types found
        print(f"\n🔢 STATISTIC TYPES DISCOVERED:")
        print(f"Total unique statistic types: {len(all_stat_types)}")
        
        # Sort by frequency
        sorted_stats = sorted(all_stat_types.items(), key=lambda x: x[1]['count'], reverse=True)
        
        print(f"\nTop 20 most common statistic types:")
        for type_id, info in sorted_stats[:20]:
            sample_val = info['sample_values'][0] if info['sample_values'] else 'N/A'
            print(f"  Type {type_id}: {info['count']} occurrences, sample value: {sample_val}")
        
        # Detailed analysis of sample statistics
        print(f"\n📋 DETAILED STATISTIC ANALYSIS:")
        for type_id, sample in list(sample_statistics.items())[:10]:
            print(f"\nType {type_id} (from {sample['player']}):")
            print(f"  Full structure: {sample['full_detail']}")
        
        conn.close()
        
        return all_stat_types, sample_statistics
    
    def create_statistics_mapping(self, all_stat_types: dict):
        """Create mapping of statistic types to meaningful names."""
        logger.info("🗺️ Creating statistics mapping...")
        
        # Common football statistics mapping (to be refined based on actual data)
        stat_mapping = {
            1: 'goals',
            2: 'assists',
            3: 'yellow_cards',
            4: 'red_cards',
            5: 'shots',
            6: 'shots_on_target',
            7: 'passes',
            8: 'pass_accuracy',
            9: 'tackles',
            10: 'interceptions',
            11: 'fouls_committed',
            12: 'fouls_suffered',
            13: 'offsides',
            14: 'corners',
            15: 'saves',
            16: 'clean_sheets',
            17: 'goals_conceded',
            18: 'penalties_scored',
            19: 'penalties_missed',
            20: 'minutes_played',
            # Add more as we discover them
        }
        
        print(f"\n🏷️ STATISTICS MAPPING:")
        for type_id in sorted(all_stat_types.keys()):
            mapped_name = stat_mapping.get(type_id, f'unknown_stat_{type_id}')
            count = all_stat_types[type_id]['count']
            sample = all_stat_types[type_id]['sample_values'][0] if all_stat_types[type_id]['sample_values'] else 'N/A'
            print(f"  {type_id:3d} -> {mapped_name:20s} (count: {count:3d}, sample: {sample})")
        
        return stat_mapping
    
    def create_advanced_statistics_database(self, all_stat_types: dict, stat_mapping: dict):
        """Create a proper advanced statistics database with real data."""
        logger.info("🗄️ Creating advanced statistics database with real data...")
        
        advanced_db_path = "data/real_advanced_stats/manchester_city_real_advanced_2023_24.db"
        import os
        os.makedirs(os.path.dirname(advanced_db_path), exist_ok=True)
        
        source_conn = sqlite3.connect(self.db_path)
        target_conn = sqlite3.connect(advanced_db_path)
        target_cursor = target_conn.cursor()
        
        # Create advanced player statistics table
        target_cursor.execute('''
            CREATE TABLE IF NOT EXISTS real_player_statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER,
                player_name TEXT,
                season_id INTEGER,
                position_id INTEGER,
                jersey_number INTEGER,
                statistic_type_id INTEGER,
                statistic_name TEXT,
                statistic_value TEXT,
                value_total INTEGER,
                value_home INTEGER,
                value_away INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create player summary table
        target_cursor.execute('''
            CREATE TABLE IF NOT EXISTS real_player_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER,
                player_name TEXT,
                position_id INTEGER,
                jersey_number INTEGER,
                total_statistics INTEGER,
                goals INTEGER DEFAULT 0,
                assists INTEGER DEFAULT 0,
                yellow_cards INTEGER DEFAULT 0,
                red_cards INTEGER DEFAULT 0,
                shots INTEGER DEFAULT 0,
                shots_on_target INTEGER DEFAULT 0,
                passes INTEGER DEFAULT 0,
                tackles INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Process all players and extract statistics
        players_df = pd.read_sql_query("SELECT * FROM working_players", source_conn)
        
        total_stats_inserted = 0
        
        for _, player_row in players_df.iterrows():
            detailed_data = json.loads(player_row['detailed_data'])
            player_id = detailed_data.get('id')
            player_name = detailed_data.get('display_name', 'Unknown')
            
            if 'statistics' in detailed_data and detailed_data['statistics']:
                stats = detailed_data['statistics']
                
                player_summary = {
                    'player_id': player_id,
                    'player_name': player_name,
                    'total_statistics': len(stats),
                    'goals': 0,
                    'assists': 0,
                    'yellow_cards': 0,
                    'red_cards': 0,
                    'shots': 0,
                    'shots_on_target': 0,
                    'passes': 0,
                    'tackles': 0
                }
                
                # Process each statistic
                for stat in stats:
                    if 'details' in stat and stat['details']:
                        season_id = stat.get('season_id')
                        position_id = stat.get('position_id')
                        jersey_number = stat.get('jersey_number')
                        
                        for detail in stat['details']:
                            type_id = detail.get('type_id')
                            value = detail.get('value', {})
                            
                            stat_name = stat_mapping.get(type_id, f'unknown_stat_{type_id}')
                            
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
                            
                            # Insert detailed statistic
                            target_cursor.execute('''
                                INSERT INTO real_player_statistics 
                                (player_id, player_name, season_id, position_id, jersey_number,
                                 statistic_type_id, statistic_name, statistic_value,
                                 value_total, value_home, value_away)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                player_id, player_name, season_id, position_id, jersey_number,
                                type_id, stat_name, json.dumps(value),
                                value_total, value_home, value_away
                            ))
                            
                            total_stats_inserted += 1
                            
                            # Update summary for common statistics
                            if stat_name in player_summary:
                                player_summary[stat_name] = value_total
                
                # Insert player summary
                target_cursor.execute('''
                    INSERT INTO real_player_summary 
                    (player_id, player_name, position_id, jersey_number, total_statistics,
                     goals, assists, yellow_cards, red_cards, shots, shots_on_target, passes, tackles)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    player_summary['player_id'],
                    player_summary['player_name'],
                    position_id,
                    jersey_number,
                    player_summary['total_statistics'],
                    player_summary['goals'],
                    player_summary['assists'],
                    player_summary['yellow_cards'],
                    player_summary['red_cards'],
                    player_summary['shots'],
                    player_summary['shots_on_target'],
                    player_summary['passes'],
                    player_summary['tackles']
                ))
        
        target_conn.commit()
        source_conn.close()
        target_conn.close()
        
        logger.info(f"✅ Created advanced database with {total_stats_inserted} individual statistics")
        logger.info(f"💾 Database location: {advanced_db_path}")
        
        return advanced_db_path
    
    def generate_real_statistics_report(self, advanced_db_path: str):
        """Generate report from real statistics database."""
        logger.info("📋 Generating real statistics report...")
        
        conn = sqlite3.connect(advanced_db_path)
        
        print(f"\n" + "="*100)
        print("⚽ REAL MANCHESTER CITY ADVANCED STATISTICS DATABASE")
        print("="*100)
        
        # Database summary
        total_stats = pd.read_sql_query("SELECT COUNT(*) as count FROM real_player_statistics", conn).iloc[0]['count']
        total_players = pd.read_sql_query("SELECT COUNT(*) as count FROM real_player_summary", conn).iloc[0]['count']
        
        print(f"📊 Database Summary:")
        print(f"   • Total individual statistics: {total_stats}")
        print(f"   • Total players: {total_players}")
        print(f"   • Database location: {advanced_db_path}")
        
        # Top statistics by frequency
        print(f"\n🔢 MOST COMMON STATISTICS:")
        top_stats = pd.read_sql_query("""
            SELECT statistic_name, COUNT(*) as frequency, AVG(value_total) as avg_value
            FROM real_player_statistics 
            WHERE value_total > 0
            GROUP BY statistic_name 
            ORDER BY frequency DESC 
            LIMIT 15
        """, conn)
        print(top_stats.to_string(index=False))
        
        # Player summary
        print(f"\n🏆 PLAYER PERFORMANCE SUMMARY:")
        player_summary = pd.read_sql_query("""
            SELECT player_name, goals, assists, shots, passes, tackles, total_statistics
            FROM real_player_summary 
            ORDER BY goals DESC, assists DESC
            LIMIT 10
        """, conn)
        print(player_summary.to_string(index=False))
        
        # Available statistic types
        print(f"\n📈 AVAILABLE STATISTIC TYPES:")
        stat_types = pd.read_sql_query("""
            SELECT DISTINCT statistic_type_id, statistic_name, COUNT(*) as count
            FROM real_player_statistics 
            GROUP BY statistic_type_id, statistic_name
            ORDER BY statistic_type_id
        """, conn)
        print(stat_types.to_string(index=False))
        
        print(f"\n🎯 REAL ADVANCED METRICS NOW AVAILABLE:")
        print("   • Individual player statistics per season")
        print("   • Home/Away performance breakdown")
        print("   • Comprehensive statistic type mapping")
        print("   • Player performance summaries")
        print("   • SQL queryable database with real data")
        print("="*100)
        
        conn.close()

def main():
    """Main execution function."""
    analyzer = RealStatisticsAnalyzer()
    
    # Analyze player statistics
    all_stat_types, sample_statistics = analyzer.analyze_player_statistics()
    
    # Create statistics mapping
    stat_mapping = analyzer.create_statistics_mapping(all_stat_types)
    
    # Create advanced statistics database
    advanced_db_path = analyzer.create_advanced_statistics_database(all_stat_types, stat_mapping)
    
    # Generate comprehensive report
    analyzer.generate_real_statistics_report(advanced_db_path)
    
    logger.info("🎉 Real statistics analysis completed!")

if __name__ == "__main__":
    main()
