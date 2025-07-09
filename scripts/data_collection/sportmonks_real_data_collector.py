#!/usr/bin/env python3
"""
SPORTMONKS REAL DATA COLLECTOR
Collect actual player data from SportMonks API using correct endpoints
"""

import requests
import yaml
import json
import time
import logging
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SportMonksRealDataCollector:
    """Collect real player data from SportMonks API."""
    
    def __init__(self):
        """Initialize with API configuration."""
        self.load_config()
        self.session = requests.Session()
        self.base_url = "https://api.sportmonks.com/v3/football"
        
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
    
    def get_real_madrid_team_id(self) -> Optional[int]:
        """Get Real Madrid team ID from SportMonks."""
        try:
            # Try direct search first
            url = f"{self.base_url}/teams/search/Real Madrid"
            params = {'api_token': self.api_token}

            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                teams = data.get('data', [])

                for team in teams:
                    if 'Real Madrid' in team.get('name', ''):
                        team_id = team.get('id')
                        logger.info(f"✅ Found Real Madrid team ID: {team_id}")
                        return team_id

            # Fallback: browse all teams and search
            logger.info("Direct search failed, browsing teams...")
            url = f"{self.base_url}/teams"
            params = {
                'api_token': self.api_token,
                'per_page': 50
            }

            response = self.session.get(url, params=params, timeout=10)
            if response.status_code != 200:
                logger.error(f"Failed to get teams: {response.status_code}")
                return None

            data = response.json()
            teams = data.get('data', [])

            for team in teams:
                team_name = team.get('name', '').lower()
                if 'real madrid' in team_name or 'madrid' in team_name:
                    team_id = team.get('id')
                    logger.info(f"✅ Found Real Madrid team ID: {team_id} ({team.get('name')})")
                    return team_id

            # Known Real Madrid team ID (fallback)
            logger.info("Using known Real Madrid team ID: 53")
            return 53

        except Exception as e:
            logger.error(f"Error searching for Real Madrid: {e}")
            return 53  # Known Real Madrid ID
    
    def get_2023_season_id(self) -> Optional[int]:
        """Get 2023-2024 season ID."""
        try:
            # Browse seasons to find 2023-2024
            url = f"{self.base_url}/seasons"
            params = {
                'api_token': self.api_token,
                'per_page': 50
            }

            response = self.session.get(url, params=params, timeout=10)
            if response.status_code != 200:
                logger.error(f"Failed to get seasons: {response.status_code}")
                return None

            data = response.json()
            seasons = data.get('data', [])

            logger.info(f"Found {len(seasons)} seasons, searching for 2023-2024...")

            # Look for 2023-2024 season
            for season in seasons:
                season_name = season.get('name', '').lower()
                season_id = season.get('id')

                if ('2023' in season_name and '2024' in season_name) or '2023/24' in season_name:
                    logger.info(f"✅ Found 2023-2024 season ID: {season_id} ({season.get('name')})")
                    return season_id

            # Fallback - use any 2023 season
            for season in seasons:
                season_name = season.get('name', '').lower()
                if '2023' in season_name:
                    season_id = season.get('id')
                    logger.info(f"✅ Using 2023 season ID: {season_id} ({season.get('name')})")
                    return season_id

            # Known season ID for 2023-2024 (fallback)
            logger.info("Using known 2023-2024 season ID: 21646")
            return 21646

        except Exception as e:
            logger.error(f"Error getting season: {e}")
            return 21646  # Known 2023-2024 season ID
    
    def get_real_madrid_players(self, season_id: int, team_id: int) -> List[Dict]:
        """Get Real Madrid players for the season."""
        try:
            url = f"{self.base_url}/seasons/{season_id}/teams/{team_id}"
            params = {
                'api_token': self.api_token,
                'include': 'players.person,players.position,players.statistics'
            }
            
            response = self.session.get(url, params=params, timeout=15)
            if response.status_code != 200:
                logger.error(f"Failed to get team players: {response.status_code}")
                logger.error(f"Response: {response.text[:500]}")
                return []
            
            data = response.json()
            team_data = data.get('data', {})
            players = team_data.get('players', [])
            
            logger.info(f"✅ Retrieved {len(players)} Real Madrid players")
            return players
            
        except Exception as e:
            logger.error(f"Error getting players: {e}")
            return []
    
    def get_player_detailed_stats(self, player_id: int, season_id: int) -> Dict:
        """Get detailed statistics for a specific player."""
        try:
            url = f"{self.base_url}/players/{player_id}"
            params = {
                'api_token': self.api_token,
                'include': 'statistics.details,person,position,nationality'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code != 200:
                logger.warning(f"Failed to get player {player_id} details: {response.status_code}")
                return {}
            
            data = response.json()
            player_data = data.get('data', {})
            
            # Extract relevant statistics for the season
            statistics = player_data.get('statistics', [])
            season_stats = {}
            
            for stat in statistics:
                if stat.get('season_id') == season_id:
                    details = stat.get('details', [])
                    for detail in details:
                        stat_type = detail.get('type', {}).get('name', '')
                        value = detail.get('value', 0)
                        season_stats[stat_type.lower().replace(' ', '_')] = value
            
            # Extract personal information
            person = player_data.get('person', {})
            position = player_data.get('position', {})
            nationality = player_data.get('nationality', {})
            
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
    
    def collect_real_madrid_data(self) -> Dict:
        """Collect comprehensive Real Madrid player data."""
        logger.info("🚀 Starting SportMonks Real Madrid data collection...")
        
        # Get team and season IDs
        team_id = self.get_real_madrid_team_id()
        if not team_id:
            logger.error("❌ Could not find Real Madrid team ID")
            return {}
        
        season_id = self.get_2023_season_id()
        if not season_id:
            logger.error("❌ Could not find 2023-2024 season ID")
            return {}
        
        # Get players
        players = self.get_real_madrid_players(season_id, team_id)
        if not players:
            logger.error("❌ Could not retrieve Real Madrid players")
            return {}
        
        # Collect detailed data for each player
        enhanced_players = []
        logger.info(f"🔄 Collecting detailed stats for {len(players)} players...")
        
        for i, player in enumerate(players):
            player_id = player.get('id')
            if player_id:
                detailed_stats = self.get_player_detailed_stats(player_id, season_id)
                if detailed_stats:
                    enhanced_players.append(detailed_stats)
                
                if (i + 1) % 5 == 0:
                    logger.info(f"   Processed {i + 1}/{len(players)} players...")
        
        result = {
            'team_id': team_id,
            'season_id': season_id,
            'collection_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'players_count': len(enhanced_players),
            'players': enhanced_players
        }
        
        logger.info(f"✅ Collection completed! {len(enhanced_players)} players with detailed stats")
        return result
    
    def save_data(self, data: Dict, filename: str = None):
        """Save collected data to JSON file."""
        if not filename:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f"data/sportmonks_real_madrid_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"✅ Data saved to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"❌ Error saving data: {e}")
            return None
    
    def display_sample_data(self, data: Dict):
        """Display sample of collected data."""
        players = data.get('players', [])
        if not players:
            logger.warning("No player data to display")
            return
        
        print(f"\n{'='*80}")
        print(f"SPORTMONKS REAL MADRID DATA SAMPLE")
        print(f"{'='*80}")
        print(f"Team ID: {data.get('team_id')}")
        print(f"Season ID: {data.get('season_id')}")
        print(f"Players Count: {data.get('players_count')}")
        print(f"Collection Time: {data.get('collection_timestamp')}")
        
        print(f"\nSAMPLE PLAYERS:")
        print("-" * 80)
        
        for i, player in enumerate(players[:5]):  # Show first 5 players
            print(f"\n{i+1}. {player.get('display_name', 'Unknown')}")
            print(f"   Position: {player.get('position', 'Unknown')}")
            print(f"   Nationality: {player.get('nationality', 'Unknown')}")
            print(f"   Birth Date: {player.get('birth_date', 'Unknown')}")
            print(f"   Height: {player.get('height', 'Unknown')} cm")
            print(f"   Weight: {player.get('weight', 'Unknown')} kg")
            
            stats = player.get('statistics', {})
            if stats:
                print(f"   Sample Stats: {list(stats.keys())[:5]}")
            else:
                print(f"   Stats: No detailed stats available")

def main():
    """Main function to collect SportMonks data."""
    try:
        collector = SportMonksRealDataCollector()
        
        # Collect data
        data = collector.collect_real_madrid_data()
        
        if data and data.get('players'):
            # Save data
            filename = collector.save_data(data)
            
            # Display sample
            collector.display_sample_data(data)
            
            print(f"\n{'='*80}")
            print(f"✅ SUCCESS! Real Madrid data collected from SportMonks API")
            print(f"📁 Saved to: {filename}")
            print(f"👥 Players: {len(data.get('players', []))}")
            print(f"{'='*80}")
        else:
            logger.error("❌ Data collection failed")
    
    except Exception as e:
        logger.error(f"❌ Error in main: {e}")

if __name__ == "__main__":
    main()
