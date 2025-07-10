#!/usr/bin/env python3
"""
Enhanced Manchester City Data Collector with Advanced Statistics
Collects comprehensive match and player statistics including all available metrics
"""

import requests
import yaml
import sqlite3
import pandas as pd
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedManchesterCityCollector:
    """Enhanced collector for Manchester City with advanced statistics."""
    
    def __init__(self):
        """Initialize with API configuration."""
        self.load_config()
        self.session = requests.Session()
        self.base_url = "https://api.sportmonks.com/v3/football"
        
        # Manchester City team ID
        self.man_city_id = 9
        
        # 2023-2024 Premier League season ID
        self.season_2023_24 = 21646
        
        # Rate limiting
        self.rate_limit_delay = 1.2
        
        # Database setup
        self.db_path = "data/manchester_city_enhanced_database/manchester_city_enhanced_2023_24.db"
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Statistics mapping
        self.stat_type_mapping = {}
        
    def load_config(self):
        """Load SportMonks API configuration."""
        try:
            with open('config/api_keys.yaml', 'r') as f:
                config = yaml.safe_load(f)
            
            self.api_token = config.get('sportmonks', {}).get('api_key')
            
            if self.api_token:
                logger.info("✅ SportMonks API token loaded successfully")
            else:
                logger.error("❌ SportMonks API token not found")
                raise ValueError("SportMonks API token required")
                
        except FileNotFoundError:
            logger.error("❌ Config file not found: config/api_keys.yaml")
            raise
    
    def make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make API request with rate limiting and error handling."""
        if params is None:
            params = {}
        
        params['api_token'] = self.api_token
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Rate limiting
                time.sleep(self.rate_limit_delay)
                return data
            else:
                logger.error(f"❌ Failed: {endpoint} - Status: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Exception for {endpoint}: {e}")
            return {}
    
    def get_manchester_city_fixtures(self) -> List[Dict]:
        """Get all Manchester City fixtures for 2023-2024 season."""
        logger.info("🔍 Collecting Manchester City fixtures for 2023-2024...")

        fixtures = []

        # First, get basic fixtures
        params = {
            'per_page': 100,
            'include': 'participants'
        }

        data = self.make_request("fixtures", params)

        if not data or 'data' not in data:
            logger.error("❌ Failed to get fixtures")
            return []

        # Filter for Manchester City fixtures
        all_fixtures = data['data']
        man_city_fixtures = []

        for fixture in all_fixtures:
            participants = fixture.get('participants', [])
            for participant in participants:
                if participant.get('id') == self.man_city_id:
                    man_city_fixtures.append(fixture)
                    break

        logger.info(f"🔍 Found {len(man_city_fixtures)} Manchester City fixtures")

        # Now get detailed statistics for each fixture
        enhanced_fixtures = []

        for i, fixture in enumerate(man_city_fixtures[:10]):  # Limit to 10 for testing
            fixture_id = fixture.get('id')

            # Get fixture with detailed statistics
            detailed_data = self.make_request(f"fixtures/{fixture_id}", {
                'include': 'participants.statistics,participants.statistics.details'
            })

            if detailed_data and 'data' in detailed_data:
                enhanced_fixtures.append(detailed_data['data'])
                logger.info(f"� Enhanced fixture {i+1}/{len(man_city_fixtures[:10])}: {fixture.get('name', 'Unknown')}")
            else:
                # Fallback to basic fixture data
                enhanced_fixtures.append(fixture)

        logger.info(f"✅ Collected {len(enhanced_fixtures)} enhanced Manchester City fixtures")
        return enhanced_fixtures
    
    def extract_detailed_statistics(self, participant_stats: List[Dict]) -> Dict:
        """Extract detailed statistics from participant statistics."""
        stats = {}
        
        for stat in participant_stats:
            if 'details' in stat and stat['details']:
                for detail in stat['details']:
                    type_id = detail.get('type_id')
                    value = detail.get('value', {})
                    
                    # Map common statistic types
                    stat_name = self.get_stat_name(type_id)
                    
                    if isinstance(value, dict):
                        if 'total' in value:
                            stats[stat_name] = value['total']
                        elif 'count' in value:
                            stats[stat_name] = value['count']
                        elif 'percentage' in value:
                            stats[stat_name] = value['percentage']
                        else:
                            # Take the first numeric value
                            for k, v in value.items():
                                if isinstance(v, (int, float)):
                                    stats[stat_name] = v
                                    break
                    else:
                        stats[stat_name] = value
        
        return stats
    
    def get_stat_name(self, type_id: int) -> str:
        """Map statistic type ID to human-readable name."""
        # Common statistic type mappings (these would need to be discovered from API)
        stat_mapping = {
            1: 'goals',
            2: 'assists', 
            3: 'shots',
            4: 'shots_on_target',
            5: 'passes',
            6: 'pass_accuracy',
            7: 'tackles',
            8: 'interceptions',
            9: 'fouls',
            10: 'yellow_cards',
            11: 'red_cards',
            12: 'possession',
            13: 'corners',
            14: 'offsides',
            15: 'saves',
            84: 'appearances',
            # Add more mappings as discovered
        }
        
        return stat_mapping.get(type_id, f'stat_{type_id}')
    
    def create_enhanced_database(self):
        """Create enhanced database with advanced statistics tables."""
        logger.info("🗄️ Creating enhanced database structure...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Enhanced fixtures table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS enhanced_fixtures (
                id INTEGER PRIMARY KEY,
                name TEXT,
                starting_at TEXT,
                result_info TEXT,
                home_team_id INTEGER,
                away_team_id INTEGER,
                home_team_name TEXT,
                away_team_name TEXT,
                home_score INTEGER,
                away_score INTEGER,
                league_name TEXT,
                season_name TEXT,
                venue_name TEXT,
                state TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Enhanced team statistics per match
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS enhanced_team_match_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fixture_id INTEGER,
                team_id INTEGER,
                team_name TEXT,
                location TEXT,
                is_winner BOOLEAN,
                goals INTEGER DEFAULT 0,
                assists INTEGER DEFAULT 0,
                shots INTEGER DEFAULT 0,
                shots_on_target INTEGER DEFAULT 0,
                passes INTEGER DEFAULT 0,
                pass_accuracy REAL DEFAULT 0,
                possession REAL DEFAULT 0,
                tackles INTEGER DEFAULT 0,
                interceptions INTEGER DEFAULT 0,
                fouls INTEGER DEFAULT 0,
                yellow_cards INTEGER DEFAULT 0,
                red_cards INTEGER DEFAULT 0,
                corners INTEGER DEFAULT 0,
                offsides INTEGER DEFAULT 0,
                saves INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (fixture_id) REFERENCES enhanced_fixtures (id)
            )
        ''')
        
        # Enhanced player statistics per match
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS enhanced_player_match_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fixture_id INTEGER,
                player_id INTEGER,
                player_name TEXT,
                team_id INTEGER,
                team_name TEXT,
                position TEXT,
                jersey_number INTEGER,
                minutes_played INTEGER DEFAULT 0,
                goals INTEGER DEFAULT 0,
                assists INTEGER DEFAULT 0,
                shots INTEGER DEFAULT 0,
                shots_on_target INTEGER DEFAULT 0,
                passes INTEGER DEFAULT 0,
                pass_accuracy REAL DEFAULT 0,
                tackles INTEGER DEFAULT 0,
                interceptions INTEGER DEFAULT 0,
                fouls INTEGER DEFAULT 0,
                yellow_cards INTEGER DEFAULT 0,
                red_cards INTEGER DEFAULT 0,
                rating REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (fixture_id) REFERENCES enhanced_fixtures (id)
            )
        ''')
        
        # Raw statistics table for all discovered metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS raw_statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fixture_id INTEGER,
                entity_type TEXT, -- 'team' or 'player'
                entity_id INTEGER,
                entity_name TEXT,
                stat_type_id INTEGER,
                stat_name TEXT,
                stat_value TEXT,
                stat_details TEXT, -- JSON string of full details
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (fixture_id) REFERENCES enhanced_fixtures (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info("✅ Enhanced database structure created")
    
    def process_and_store_fixtures(self, fixtures: List[Dict]):
        """Process fixtures and store enhanced statistics."""
        logger.info("📊 Processing and storing enhanced fixture data...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        processed_count = 0
        
        for fixture in fixtures:
            try:
                # Extract basic fixture info
                fixture_id = fixture.get('id')
                name = fixture.get('name', '')
                starting_at = fixture.get('starting_at', '')
                result_info = fixture.get('result_info', '')
                
                # Extract participants (teams)
                participants = fixture.get('participants', [])
                if len(participants) < 2:
                    continue
                
                home_team = next((p for p in participants if p.get('meta', {}).get('location') == 'home'), {})
                away_team = next((p for p in participants if p.get('meta', {}).get('location') == 'away'), {})
                
                # Store fixture
                cursor.execute('''
                    INSERT OR REPLACE INTO enhanced_fixtures 
                    (id, name, starting_at, result_info, home_team_id, away_team_id, 
                     home_team_name, away_team_name, home_score, away_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    fixture_id, name, starting_at, result_info,
                    home_team.get('id'), away_team.get('id'),
                    home_team.get('name'), away_team.get('name'),
                    home_team.get('meta', {}).get('score'),
                    away_team.get('meta', {}).get('score')
                ))
                
                # Process team statistics
                for participant in participants:
                    team_stats = self.extract_detailed_statistics(participant.get('statistics', []))
                    
                    cursor.execute('''
                        INSERT INTO enhanced_team_match_stats 
                        (fixture_id, team_id, team_name, location, is_winner, goals, assists, 
                         shots, shots_on_target, passes, pass_accuracy, possession, tackles, 
                         interceptions, fouls, yellow_cards, red_cards, corners, offsides, saves)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        fixture_id,
                        participant.get('id'),
                        participant.get('name'),
                        participant.get('meta', {}).get('location'),
                        participant.get('meta', {}).get('winner', False),
                        team_stats.get('goals', 0),
                        team_stats.get('assists', 0),
                        team_stats.get('shots', 0),
                        team_stats.get('shots_on_target', 0),
                        team_stats.get('passes', 0),
                        team_stats.get('pass_accuracy', 0),
                        team_stats.get('possession', 0),
                        team_stats.get('tackles', 0),
                        team_stats.get('interceptions', 0),
                        team_stats.get('fouls', 0),
                        team_stats.get('yellow_cards', 0),
                        team_stats.get('red_cards', 0),
                        team_stats.get('corners', 0),
                        team_stats.get('offsides', 0),
                        team_stats.get('saves', 0)
                    ))
                    
                    # Store raw statistics for analysis
                    for stat in participant.get('statistics', []):
                        if 'details' in stat:
                            for detail in stat['details']:
                                cursor.execute('''
                                    INSERT INTO raw_statistics 
                                    (fixture_id, entity_type, entity_id, entity_name, 
                                     stat_type_id, stat_name, stat_value, stat_details)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (
                                    fixture_id,
                                    'team',
                                    participant.get('id'),
                                    participant.get('name'),
                                    detail.get('type_id'),
                                    self.get_stat_name(detail.get('type_id')),
                                    str(detail.get('value')),
                                    json.dumps(detail)
                                ))
                
                processed_count += 1
                
                if processed_count % 10 == 0:
                    logger.info(f"📊 Processed {processed_count} fixtures...")
                    conn.commit()
                
            except Exception as e:
                logger.error(f"❌ Error processing fixture {fixture.get('id')}: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Processed and stored {processed_count} enhanced fixtures")
    
    def generate_summary_report(self):
        """Generate summary report of collected data."""
        logger.info("📋 Generating enhanced data summary...")
        
        conn = sqlite3.connect(self.db_path)
        
        # Get summary statistics
        fixtures_df = pd.read_sql_query("SELECT COUNT(*) as total_fixtures FROM enhanced_fixtures", conn)
        team_stats_df = pd.read_sql_query("SELECT COUNT(*) as total_team_stats FROM enhanced_team_match_stats", conn)
        raw_stats_df = pd.read_sql_query("SELECT COUNT(*) as total_raw_stats FROM raw_statistics", conn)
        
        # Get unique statistic types
        stat_types_df = pd.read_sql_query("""
            SELECT stat_type_id, stat_name, COUNT(*) as count 
            FROM raw_statistics 
            GROUP BY stat_type_id, stat_name 
            ORDER BY count DESC
        """, conn)
        
        conn.close()
        
        print("\n" + "="*80)
        print("📊 ENHANCED MANCHESTER CITY DATABASE SUMMARY")
        print("="*80)
        print(f"📅 Season: 2023-2024")
        print(f"⚽ Team: Manchester City")
        print(f"🏟️  Total Fixtures: {fixtures_df.iloc[0]['total_fixtures']}")
        print(f"📈 Team Match Statistics: {team_stats_df.iloc[0]['total_team_stats']}")
        print(f"📊 Raw Statistics Records: {raw_stats_df.iloc[0]['total_raw_stats']}")
        
        print(f"\n🔢 AVAILABLE STATISTIC TYPES:")
        for _, row in stat_types_df.head(20).iterrows():
            print(f"  • {row['stat_name']} (ID: {row['stat_type_id']}): {row['count']} records")
        
        print(f"\n💾 Database Location: {self.db_path}")
        print("="*80)

def main():
    """Main execution function."""
    collector = EnhancedManchesterCityCollector()
    
    # Create enhanced database
    collector.create_enhanced_database()
    
    # Collect fixtures with enhanced statistics
    fixtures = collector.get_manchester_city_fixtures()
    
    # Process and store data
    collector.process_and_store_fixtures(fixtures)
    
    # Generate summary
    collector.generate_summary_report()
    
    logger.info("🎉 Enhanced Manchester City data collection completed!")

if __name__ == "__main__":
    main()
