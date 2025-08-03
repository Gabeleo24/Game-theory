#!/usr/bin/env python3
"""
Working SportMonks Advanced Statistics Collector
Real implementation that works with actual SportMonks API endpoints
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

class WorkingSportMonksCollector:
    """Working collector for SportMonks API with real advanced statistics."""
    
    def __init__(self):
        """Initialize with API configuration."""
        self.load_config()
        self.session = requests.Session()
        self.base_url = "https://api.sportmonks.com/v3/football"
        
        # Manchester City team ID
        self.man_city_id = 9
        
        # Working season IDs
        self.seasons = {
            "2023-2024": 21646,
            "2022-2023": 19734,
            "2021-2022": 19686
        }
        
        # Rate limiting
        self.rate_limit_delay = 1.2
        
        # Database setup
        self.db_path = "data/working_sportmonks_database/manchester_city_working_2023_24.db"
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
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
                time.sleep(self.rate_limit_delay)
                return data
            else:
                logger.error(f"❌ Failed: {endpoint} - Status: {response.status_code}")
                if response.status_code == 422:
                    logger.error(f"Response: {response.text[:300]}")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Exception for {endpoint}: {e}")
            return {}
    
    def discover_working_endpoints(self):
        """Discover which endpoints actually work for getting statistics."""
        logger.info("🔍 Discovering working endpoints for advanced statistics...")
        
        working_endpoints = {}
        
        # Test team fixtures endpoint
        team_fixtures = self.make_request(f"teams/{self.man_city_id}/fixtures", {
            'seasons': self.seasons['2023-2024'],
            'per_page': 5
        })
        
        if team_fixtures and 'data' in team_fixtures:
            working_endpoints['team_fixtures'] = {
                'endpoint': f"teams/{self.man_city_id}/fixtures",
                'working': True,
                'sample_count': len(team_fixtures['data'])
            }
            logger.info(f"✅ Team fixtures endpoint working: {len(team_fixtures['data'])} fixtures")
        
        # Test squad endpoint
        squad_data = self.make_request(f"squads/seasons/{self.seasons['2023-2024']}/teams/{self.man_city_id}")
        
        if squad_data and 'data' in squad_data:
            working_endpoints['squad'] = {
                'endpoint': f"squads/seasons/{self.seasons['2023-2024']}/teams/{self.man_city_id}",
                'working': True,
                'sample_count': len(squad_data['data'])
            }
            logger.info(f"✅ Squad endpoint working: {len(squad_data['data'])} players")
            
            # Test individual player endpoint
            if squad_data['data']:
                player_id = squad_data['data'][0].get('player_id')
                if player_id:
                    player_data = self.make_request(f"players/{player_id}", {
                        'include': 'statistics'
                    })
                    
                    if player_data and 'data' in player_data:
                        working_endpoints['player_with_stats'] = {
                            'endpoint': f"players/{player_id}",
                            'working': True,
                            'has_statistics': 'statistics' in player_data['data']
                        }
                        logger.info(f"✅ Player with statistics endpoint working")
        
        # Test fixture with includes
        if 'team_fixtures' in working_endpoints and team_fixtures['data']:
            fixture_id = team_fixtures['data'][0].get('id')
            
            includes_to_test = [
                'participants',
                'lineups',
                'events',
                'statistics',
                'participants.statistics'
            ]
            
            for include in includes_to_test:
                fixture_data = self.make_request(f"fixtures/{fixture_id}", {
                    'include': include
                })
                
                if fixture_data and 'data' in fixture_data:
                    working_endpoints[f'fixture_with_{include.replace(".", "_")}'] = {
                        'endpoint': f"fixtures/{fixture_id}",
                        'include': include,
                        'working': True
                    }
                    logger.info(f"✅ Fixture with {include} working")
        
        return working_endpoints
    
    def collect_comprehensive_data(self):
        """Collect comprehensive data using working endpoints."""
        logger.info("📊 Collecting comprehensive Manchester City data...")
        
        # Discover working endpoints first
        working_endpoints = self.discover_working_endpoints()
        
        # Collect team fixtures
        fixtures_data = self.collect_team_fixtures()
        
        # Collect squad and player data
        squad_data = self.collect_squad_data()
        
        # Collect detailed fixture data with statistics
        enhanced_fixtures = self.collect_enhanced_fixtures(fixtures_data)
        
        # Collect player statistics
        player_stats = self.collect_player_statistics(squad_data)
        
        return {
            'working_endpoints': working_endpoints,
            'fixtures': enhanced_fixtures,
            'squad': squad_data,
            'player_statistics': player_stats
        }
    
    def collect_team_fixtures(self) -> List[Dict]:
        """Collect team fixtures using working endpoint."""
        logger.info("⚽ Collecting team fixtures...")
        
        fixtures = []
        
        # Use team fixtures endpoint
        team_fixtures = self.make_request(f"teams/{self.man_city_id}/fixtures", {
            'seasons': self.seasons['2023-2024'],
            'per_page': 100
        })
        
        if team_fixtures and 'data' in team_fixtures:
            fixtures = team_fixtures['data']
            logger.info(f"✅ Collected {len(fixtures)} team fixtures")
        
        return fixtures
    
    def collect_squad_data(self) -> List[Dict]:
        """Collect squad data."""
        logger.info("👥 Collecting squad data...")
        
        squad_data = self.make_request(f"squads/seasons/{self.seasons['2023-2024']}/teams/{self.man_city_id}")
        
        if squad_data and 'data' in squad_data:
            logger.info(f"✅ Collected squad data for {len(squad_data['data'])} players")
            return squad_data['data']
        
        return []
    
    def collect_enhanced_fixtures(self, fixtures: List[Dict]) -> List[Dict]:
        """Collect enhanced fixture data with all available statistics."""
        logger.info("📈 Collecting enhanced fixture data...")
        
        enhanced_fixtures = []
        
        for i, fixture in enumerate(fixtures[:15]):  # Process first 15 fixtures
            fixture_id = fixture.get('id')
            
            enhanced_fixture = {
                'basic_data': fixture,
                'participants': None,
                'lineups': None,
                'events': None,
                'statistics': None
            }
            
            # Get participants
            participants_data = self.make_request(f"fixtures/{fixture_id}", {
                'include': 'participants'
            })
            
            if participants_data and 'data' in participants_data:
                enhanced_fixture['participants'] = participants_data['data'].get('participants', [])
            
            # Get lineups (might contain player statistics)
            lineups_data = self.make_request(f"fixtures/{fixture_id}", {
                'include': 'lineups'
            })
            
            if lineups_data and 'data' in lineups_data:
                enhanced_fixture['lineups'] = lineups_data['data'].get('lineups', [])
            
            # Get events (goals, assists, cards, etc.)
            events_data = self.make_request(f"fixtures/{fixture_id}", {
                'include': 'events'
            })
            
            if events_data and 'data' in events_data:
                enhanced_fixture['events'] = events_data['data'].get('events', [])
            
            enhanced_fixtures.append(enhanced_fixture)
            
            logger.info(f"📊 Enhanced fixture {i+1}/{min(len(fixtures), 15)}: {fixture.get('name', 'Unknown')}")
        
        logger.info(f"✅ Collected {len(enhanced_fixtures)} enhanced fixtures")
        return enhanced_fixtures
    
    def collect_player_statistics(self, squad: List[Dict]) -> List[Dict]:
        """Collect individual player statistics."""
        logger.info("👤 Collecting player statistics...")
        
        player_stats = []
        
        for i, player in enumerate(squad[:10]):  # Process first 10 players
            player_id = player.get('player_id')
            
            if player_id:
                # Get player with statistics
                player_data = self.make_request(f"players/{player_id}", {
                    'include': 'statistics'
                })
                
                if player_data and 'data' in player_data:
                    player_stats.append({
                        'squad_info': player,
                        'detailed_data': player_data['data']
                    })
                    
                    logger.info(f"📊 Player {i+1}/{min(len(squad), 10)}: {player_data['data'].get('display_name', 'Unknown')}")
        
        logger.info(f"✅ Collected statistics for {len(player_stats)} players")
        return player_stats
    
    def create_working_database(self, collected_data: Dict):
        """Create database with all collected data."""
        logger.info("🗄️ Creating working database...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables for collected data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS working_fixtures (
                id INTEGER PRIMARY KEY,
                fixture_data TEXT,
                participants_data TEXT,
                lineups_data TEXT,
                events_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS working_players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER,
                squad_data TEXT,
                detailed_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS working_endpoints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                endpoint_name TEXT,
                endpoint_url TEXT,
                working BOOLEAN,
                sample_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert fixture data
        for fixture in collected_data['fixtures']:
            cursor.execute('''
                INSERT INTO working_fixtures 
                (id, fixture_data, participants_data, lineups_data, events_data)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                fixture['basic_data'].get('id'),
                json.dumps(fixture['basic_data']),
                json.dumps(fixture['participants']),
                json.dumps(fixture['lineups']),
                json.dumps(fixture['events'])
            ))
        
        # Insert player data
        for player in collected_data['player_statistics']:
            cursor.execute('''
                INSERT INTO working_players 
                (player_id, squad_data, detailed_data)
                VALUES (?, ?, ?)
            ''', (
                player['squad_info'].get('player_id'),
                json.dumps(player['squad_info']),
                json.dumps(player['detailed_data'])
            ))
        
        # Insert endpoint information
        for endpoint_name, endpoint_info in collected_data['working_endpoints'].items():
            cursor.execute('''
                INSERT INTO working_endpoints 
                (endpoint_name, endpoint_url, working, sample_data)
                VALUES (?, ?, ?, ?)
            ''', (
                endpoint_name,
                endpoint_info.get('endpoint', ''),
                endpoint_info.get('working', False),
                json.dumps(endpoint_info)
            ))
        
        conn.commit()
        conn.close()
        
        logger.info("✅ Working database created successfully")
    
    def generate_comprehensive_report(self, collected_data: Dict):
        """Generate comprehensive report of collected data."""
        logger.info("📋 Generating comprehensive report...")
        
        print("\n" + "="*100)
        print("🔍 WORKING SPORTMONKS API DATA COLLECTION REPORT")
        print("="*100)
        
        # Working endpoints summary
        print(f"\n🔗 WORKING ENDPOINTS:")
        for endpoint_name, endpoint_info in collected_data['working_endpoints'].items():
            status = "✅ Working" if endpoint_info.get('working') else "❌ Not working"
            print(f"  • {endpoint_name}: {status}")
            if 'sample_count' in endpoint_info:
                print(f"    Sample count: {endpoint_info['sample_count']}")
        
        # Data collection summary
        print(f"\n📊 DATA COLLECTION SUMMARY:")
        print(f"  • Fixtures collected: {len(collected_data['fixtures'])}")
        print(f"  • Squad members: {len(collected_data['squad'])}")
        print(f"  • Player statistics: {len(collected_data['player_statistics'])}")
        
        # Sample data analysis
        if collected_data['fixtures']:
            sample_fixture = collected_data['fixtures'][0]
            print(f"\n⚽ SAMPLE FIXTURE DATA:")
            print(f"  • Basic data keys: {list(sample_fixture['basic_data'].keys())}")
            if sample_fixture['participants']:
                print(f"  • Participants count: {len(sample_fixture['participants'])}")
            if sample_fixture['events']:
                print(f"  • Events count: {len(sample_fixture['events'])}")
        
        if collected_data['player_statistics']:
            sample_player = collected_data['player_statistics'][0]
            print(f"\n👤 SAMPLE PLAYER DATA:")
            print(f"  • Squad info keys: {list(sample_player['squad_info'].keys())}")
            print(f"  • Detailed data keys: {list(sample_player['detailed_data'].keys())}")
            if 'statistics' in sample_player['detailed_data']:
                stats = sample_player['detailed_data']['statistics']
                print(f"  • Statistics available: {len(stats) if isinstance(stats, list) else 'Yes' if stats else 'No'}")
        
        print(f"\n💾 Database Location: {self.db_path}")
        print("="*100)

def main():
    """Main execution function."""
    collector = WorkingSportMonksCollector()
    
    # Collect comprehensive data
    collected_data = collector.collect_comprehensive_data()
    
    # Create working database
    collector.create_working_database(collected_data)
    
    # Generate comprehensive report
    collector.generate_comprehensive_report(collected_data)
    
    logger.info("🎉 Working SportMonks data collection completed!")

if __name__ == "__main__":
    main()
