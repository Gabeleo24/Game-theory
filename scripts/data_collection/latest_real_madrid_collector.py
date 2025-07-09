#!/usr/bin/env python3
"""
LATEST REAL MADRID 2023-2024 DATA COLLECTOR
Comprehensive player statistics collection using SportMonks Premium API
"""

import requests
import json
import yaml
import time
import logging
import psycopg2
from datetime import datetime
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LatestRealMadridCollector:
    """Collect latest Real Madrid player statistics from SportMonks Premium API."""
    
    def __init__(self):
        """Initialize with API and database configuration."""
        self.load_config()
        self.session = requests.Session()
        self.base_url = "https://api.sportmonks.com/v3/football"
        self.real_madrid_id = 3468  # Correct Real Madrid team ID from API
        self.season_2023_id = None
        self.collected_data = {}
        
        # Connect to database
        self.connect_database()
        
    def load_config(self):
        """Load SportMonks API configuration."""
        try:
            with open('config/api_keys.yaml', 'r') as f:
                config = yaml.safe_load(f)
            
            self.api_token = config.get('sportmonks', {}).get('api_key')
            
            if self.api_token:
                logger.info("✅ SportMonks Premium API token loaded successfully")
            else:
                logger.error("❌ SportMonks API token not found")
                raise ValueError("SportMonks API token required")
                
        except FileNotFoundError:
            logger.error("❌ Config file not found: config/api_keys.yaml")
            raise
    
    def connect_database(self):
        """Connect to PostgreSQL database."""
        try:
            self.conn = psycopg2.connect(
                host='localhost', port=5432, database='soccer_intelligence', 
                user='soccerapp', password='soccerpass123'
            )
            self.cursor = self.conn.cursor()
            logger.info("✅ Database connected")
        except psycopg2.Error as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    def get_2023_season_id(self) -> Optional[int]:
        """Get 2023-2024 season ID."""
        try:
            url = f"{self.base_url}/seasons"
            params = {
                'api_token': self.api_token,
                'per_page': 50
            }
            
            response = self.session.get(url, params=params, timeout=15)
            if response.status_code != 200:
                logger.error(f"Failed to get seasons: {response.status_code}")
                return None
            
            data = response.json()
            seasons = data.get('data', [])
            
            for season in seasons:
                season_name = season.get('name', '').lower()
                if '2023' in season_name and '2024' in season_name:
                    season_id = season.get('id')
                    logger.info(f"✅ Found 2023-2024 season ID: {season_id}")
                    return season_id
            
            # Fallback to known season ID
            logger.info("Using known 2023-2024 season ID: 21646")
            return 21646
            
        except Exception as e:
            logger.error(f"Error getting season ID: {e}")
            return 21646
    
    def get_team_squad(self, season_id: int) -> List[Dict]:
        """Get Real Madrid squad for the 2023-2024 season."""
        try:
            # Try different API endpoints for team squad
            endpoints_to_try = [
                f"{self.base_url}/teams/{self.real_madrid_id}/squad",
                f"{self.base_url}/teams/{self.real_madrid_id}",
                f"{self.base_url}/squads/seasons/{season_id}/teams/{self.real_madrid_id}"
            ]

            for endpoint in endpoints_to_try:
                params = {
                    'api_token': self.api_token,
                    'include': 'players.person,players.position,players.statistics'
                }

                response = self.session.get(endpoint, params=params, timeout=20)
                if response.status_code == 200:
                    data = response.json()

                    # Handle different response structures
                    if 'data' in data:
                        team_data = data.get('data', {})
                        if isinstance(team_data, list):
                            players = team_data
                        else:
                            players = team_data.get('players', [])
                            if not players:
                                players = team_data.get('squad', [])

                        if players:
                            logger.info(f"✅ Retrieved {len(players)} Real Madrid players from {endpoint}")
                            return players

                logger.warning(f"Endpoint {endpoint} failed with status {response.status_code}")
                time.sleep(0.5)

            # Fallback: Get players from fixtures
            logger.info("Trying fallback method: getting players from recent fixtures...")
            return self.get_players_from_fixtures(season_id)

        except Exception as e:
            logger.error(f"Error getting team squad: {e}")
            return []

    def get_players_from_fixtures(self, season_id: int) -> List[Dict]:
        """Fallback method: Get players from recent Real Madrid fixtures."""
        try:
            url = f"{self.base_url}/fixtures"
            params = {
                'api_token': self.api_token,
                'filters': f'teamIds:{self.real_madrid_id};seasonIds:{season_id}',
                'include': 'lineups.player.person,lineups.player.position',
                'per_page': 10
            }

            response = self.session.get(url, params=params, timeout=20)
            if response.status_code != 200:
                logger.error(f"Failed to get fixtures: {response.status_code}")
                return []

            data = response.json()
            fixtures = data.get('data', [])

            players_dict = {}
            for fixture in fixtures:
                lineups = fixture.get('lineups', [])
                for lineup in lineups:
                    if lineup.get('team_id') == self.real_madrid_id:
                        lineup_players = lineup.get('players', [])
                        for player_data in lineup_players:
                            player = player_data.get('player', {})
                            player_id = player.get('id')
                            if player_id and player_id not in players_dict:
                                players_dict[player_id] = player

            players = list(players_dict.values())
            logger.info(f"✅ Retrieved {len(players)} Real Madrid players from fixtures")
            return players

        except Exception as e:
            logger.error(f"Error getting players from fixtures: {e}")
            return []
    
    def get_player_detailed_stats(self, player_id: int, season_id: int) -> Dict:
        """Get comprehensive player statistics."""
        try:
            url = f"{self.base_url}/players/{player_id}"
            params = {
                'api_token': self.api_token,
                'include': 'statistics.details,person,position,nationality,transfers'
            }
            
            response = self.session.get(url, params=params, timeout=15)
            if response.status_code != 200:
                logger.warning(f"Failed to get player {player_id} details: {response.status_code}")
                return {}
            
            data = response.json()
            player_data = data.get('data', {})
            
            # Extract player information
            person = player_data.get('person', {})
            position = player_data.get('position', {})
            nationality = player_data.get('nationality', {})
            
            # Extract statistics for the season
            statistics = player_data.get('statistics', [])
            season_stats = {}
            
            for stat in statistics:
                if stat.get('season_id') == season_id:
                    details = stat.get('details', [])
                    for detail in details:
                        stat_type = detail.get('type', {}).get('name', '')
                        value = detail.get('value', 0)
                        season_stats[stat_type.lower().replace(' ', '_')] = value
            
            enhanced_data = {
                'player_id': player_id,
                'name': person.get('name', ''),
                'display_name': person.get('display_name', ''),
                'birth_date': person.get('date_of_birth'),
                'nationality': nationality.get('name', 'Unknown'),
                'position': position.get('name', 'Unknown'),
                'height': person.get('height'),
                'weight': person.get('weight'),
                'statistics': season_stats
            }
            
            time.sleep(0.1)  # Rate limiting
            return enhanced_data
            
        except Exception as e:
            logger.error(f"Error getting player {player_id} details: {e}")
            return {}
    
    def get_match_level_stats(self, player_id: int, season_id: int) -> List[Dict]:
        """Get match-by-match player statistics."""
        try:
            url = f"{self.base_url}/players/{player_id}/statistics"
            params = {
                'api_token': self.api_token,
                'include': 'fixture,details',
                'filters': f'seasonIds:{season_id}'
            }
            
            response = self.session.get(url, params=params, timeout=15)
            if response.status_code != 200:
                logger.warning(f"Failed to get match stats for player {player_id}: {response.status_code}")
                return []
            
            data = response.json()
            match_stats = data.get('data', [])
            
            processed_matches = []
            for match_stat in match_stats:
                fixture = match_stat.get('fixture', {})
                details = match_stat.get('details', [])
                
                match_data = {
                    'match_id': fixture.get('id'),
                    'match_date': fixture.get('starting_at'),
                    'competition': fixture.get('league', {}).get('name', 'Unknown'),
                    'statistics': {}
                }
                
                # Process match statistics
                for detail in details:
                    stat_type = detail.get('type', {}).get('name', '')
                    value = detail.get('value', 0)
                    match_data['statistics'][stat_type.lower().replace(' ', '_')] = value
                
                processed_matches.append(match_data)
            
            time.sleep(0.1)  # Rate limiting
            return processed_matches
            
        except Exception as e:
            logger.error(f"Error getting match stats for player {player_id}: {e}")
            return []
    
    def collect_comprehensive_data(self) -> Dict:
        """Collect comprehensive Real Madrid player data."""
        logger.info("🚀 Starting comprehensive Real Madrid data collection...")
        
        # Get season ID
        season_id = self.get_2023_season_id()
        if not season_id:
            logger.error("❌ Could not find 2023-2024 season ID")
            return {}
        
        self.season_2023_id = season_id
        
        # Get team squad
        players = self.get_team_squad(season_id)
        if not players:
            logger.error("❌ Could not retrieve Real Madrid squad")
            return {}
        
        # Collect detailed data for each player
        enhanced_players = []
        logger.info(f"🔄 Collecting comprehensive stats for {len(players)} players...")
        
        for i, player in enumerate(players):
            player_id = player.get('id')
            if player_id:
                # Get detailed player stats
                detailed_stats = self.get_player_detailed_stats(player_id, season_id)
                
                # Get match-level stats
                match_stats = self.get_match_level_stats(player_id, season_id)
                
                if detailed_stats:
                    detailed_stats['match_statistics'] = match_stats
                    enhanced_players.append(detailed_stats)
                
                if (i + 1) % 3 == 0:
                    logger.info(f"   Processed {i + 1}/{len(players)} players...")
                    time.sleep(0.5)  # Additional rate limiting
        
        result = {
            'team_id': self.real_madrid_id,
            'team_name': 'Real Madrid',
            'season_id': season_id,
            'season_name': '2023-2024',
            'collection_timestamp': datetime.now().isoformat(),
            'players_count': len(enhanced_players),
            'api_source': 'SportMonks Premium',
            'players': enhanced_players
        }
        
        logger.info(f"✅ Collection completed! {len(enhanced_players)} players with comprehensive stats")
        return result
    
    def save_data(self, data: Dict) -> str:
        """Save collected data to JSON file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"data/focused/players/real_madrid_2023_2024/latest_comprehensive_collection_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Data saved to: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"❌ Error saving data: {e}")
            return ""
    
    def close(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

def main():
    """Main function to collect latest Real Madrid data."""
    try:
        collector = LatestRealMadridCollector()
        
        # Collect comprehensive data
        data = collector.collect_comprehensive_data()
        
        if data and data.get('players'):
            # Save data
            filename = collector.save_data(data)
            
            print(f"\n{'='*100}")
            print(f"✅ SUCCESS! Latest Real Madrid 2023-2024 data collected")
            print(f"📁 Saved to: {filename}")
            print(f"👥 Players: {len(data.get('players', []))}")
            print(f"🏆 Season: {data.get('season_name')}")
            print(f"📊 API Source: {data.get('api_source')}")
            print(f"⏰ Collection Time: {data.get('collection_timestamp')}")
            print(f"{'='*100}")
        else:
            logger.error("❌ Data collection failed")
        
        collector.close()
    
    except Exception as e:
        logger.error(f"❌ Error in main: {e}")

if __name__ == "__main__":
    main()
