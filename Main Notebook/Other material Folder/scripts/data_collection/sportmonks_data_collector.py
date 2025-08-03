#!/usr/bin/env python3
"""
SportMonks Data Collector
Practical data collection script using working endpoints
"""

import requests
import yaml
import json
import time
import psycopg2
from datetime import datetime
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SportMonksDataCollector:
    """Collect data from SportMonks API using verified working endpoints."""
    
    def __init__(self):
        """Initialize with API and database configuration."""
        self.load_config()
        self.session = requests.Session()
        self.base_url = "https://api.sportmonks.com/v3/football"
        
        # Manchester City team ID (confirmed working)
        self.man_city_id = 9
        
        # Working season IDs for 2019-2024
        self.seasons = {
            "2023-2024": 21646,
            "2022-2023": 19734,
            "2021-2022": 19686,
            "2020-2021": 18378,
            "2019-2020": 17141
        }
        
        # Rate limiting
        self.rate_limit_delay = 1.2
        
        # Database connection
        self.db_conn = None
        self.db_cursor = None
        
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
    
    def connect_database(self):
        """Connect to PostgreSQL database."""
        try:
            self.db_conn = psycopg2.connect(
                host='localhost',
                port=5432,
                database='soccer_intelligence',
                user='soccerapp',
                password='soccerpass123'
            )
            self.db_cursor = self.db_conn.cursor()
            logger.info("✅ Database connected successfully")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    def make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make API request with rate limiting and error handling."""
        if params is None:
            params = {}
        
        params['api_token'] = self.api_token
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            logger.info(f"🔍 Requesting: {endpoint}")
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Success: {endpoint}")
                
                # Rate limiting
                time.sleep(self.rate_limit_delay)
                return data
            else:
                logger.error(f"❌ Failed: {endpoint} - Status: {response.status_code}")
                logger.error(f"Response: {response.text[:200]}...")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Exception for {endpoint}: {e}")
            return {}
    
    def collect_team_data(self) -> Dict:
        """Collect Manchester City team data."""
        logger.info("🏟️ Collecting Team Data")
        
        team_data = self.make_request(f"teams/{self.man_city_id}")
        
        if team_data and 'data' in team_data:
            team_info = team_data['data']
            logger.info(f"✅ Collected team data for: {team_info.get('name')}")
            return team_info
        
        logger.error("❌ Failed to collect team data")
        return {}
    
    def collect_seasons_data(self) -> List[Dict]:
        """Collect seasons data."""
        logger.info("🏆 Collecting Seasons Data")
        
        seasons_data = self.make_request("seasons")
        
        if seasons_data and 'data' in seasons_data:
            seasons = seasons_data['data']
            logger.info(f"✅ Collected {len(seasons)} seasons")
            return seasons
        
        logger.error("❌ Failed to collect seasons data")
        return []
    
    def collect_squad_data(self, season_id: int) -> List[Dict]:
        """Collect squad data for a specific season."""
        logger.info(f"👥 Collecting Squad Data for Season {season_id}")
        
        squad_data = self.make_request(f"squads/seasons/{season_id}/teams/{self.man_city_id}")
        
        if squad_data and 'data' in squad_data:
            squad = squad_data['data']
            logger.info(f"✅ Collected squad data: {len(squad)} players")
            return squad
        
        logger.error(f"❌ Failed to collect squad data for season {season_id}")
        return []
    
    def collect_player_data(self, player_id: int) -> Dict:
        """Collect individual player data."""
        logger.info(f"👤 Collecting Player Data for ID {player_id}")
        
        player_data = self.make_request(f"players/{player_id}")
        
        if player_data and 'data' in player_data:
            player_info = player_data['data']
            logger.info(f"✅ Collected player data for: {player_info.get('name')}")
            return player_info
        
        logger.error(f"❌ Failed to collect player data for ID {player_id}")
        return {}
    
    def collect_fixtures_data(self, limit: int = 50) -> List[Dict]:
        """Collect fixtures data."""
        logger.info("⚽ Collecting Fixtures Data")
        
        fixtures_data = self.make_request("fixtures", {"per_page": limit})
        
        if fixtures_data and 'data' in fixtures_data:
            fixtures = fixtures_data['data']
            logger.info(f"✅ Collected {len(fixtures)} fixtures")
            return fixtures
        
        logger.error("❌ Failed to collect fixtures data")
        return []
    
    def save_to_json(self, data: Dict, filename: str):
        """Save collected data to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"data/sportmonks_collected_{filename}_{timestamp}.json"
        
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            logger.info(f"✅ Data saved to: {filepath}")
        except Exception as e:
            logger.error(f"❌ Failed to save data: {e}")
    
    def run_data_collection(self):
        """Run complete data collection process."""
        logger.info("🚀 Starting SportMonks Data Collection")
        
        collection_results = {
            'timestamp': datetime.now().isoformat(),
            'team_id': self.man_city_id,
            'data': {}
        }
        
        # 1. Collect team data
        team_data = self.collect_team_data()
        if team_data:
            collection_results['data']['team'] = team_data
        
        # 2. Collect seasons data
        seasons_data = self.collect_seasons_data()
        if seasons_data:
            collection_results['data']['seasons'] = seasons_data[:10]  # First 10 seasons
        
        # 3. Collect squad data for recent seasons
        collection_results['data']['squads'] = {}
        for season_name, season_id in list(self.seasons.items())[:2]:  # Last 2 seasons
            squad_data = self.collect_squad_data(season_id)
            if squad_data:
                collection_results['data']['squads'][season_name] = squad_data
        
        # 4. Collect individual player data for a few players
        collection_results['data']['players'] = {}
        if 'squads' in collection_results['data']:
            for season_name, squad in collection_results['data']['squads'].items():
                for i, player_squad in enumerate(squad[:3]):  # First 3 players per season
                    player_id = player_squad.get('player_id')
                    if player_id:
                        player_data = self.collect_player_data(player_id)
                        if player_data:
                            collection_results['data']['players'][str(player_id)] = player_data
                        
                        if i >= 2:  # Limit to 3 players to avoid rate limits
                            break
        
        # 5. Collect some fixtures data
        fixtures_data = self.collect_fixtures_data(20)  # Limit to 20 fixtures
        if fixtures_data:
            collection_results['data']['fixtures'] = fixtures_data
        
        # Save results
        self.save_to_json(collection_results, 'complete')
        
        return collection_results
    
    def print_summary(self, results: Dict):
        """Print collection summary."""
        print("\n" + "="*80)
        print("📊 SPORTMONKS DATA COLLECTION SUMMARY")
        print("="*80)
        
        data = results.get('data', {})
        
        if 'team' in data:
            team = data['team']
            print(f"🏟️ Team: {team.get('name')} (ID: {team.get('id')})")
        
        if 'seasons' in data:
            print(f"🏆 Seasons collected: {len(data['seasons'])}")
        
        if 'squads' in data:
            total_squad_players = sum(len(squad) for squad in data['squads'].values())
            print(f"👥 Squad data: {len(data['squads'])} seasons, {total_squad_players} total entries")
        
        if 'players' in data:
            print(f"👤 Individual players: {len(data['players'])}")
        
        if 'fixtures' in data:
            print(f"⚽ Fixtures: {len(data['fixtures'])}")
        
        print(f"\n📄 Results saved to data/ directory")
        print("="*80)

def main():
    """Main execution function."""
    # Create data directory
    import os
    os.makedirs('data', exist_ok=True)
    
    collector = SportMonksDataCollector()
    
    # Run collection
    results = collector.run_data_collection()
    
    # Print summary
    collector.print_summary(results)

if __name__ == "__main__":
    main()
