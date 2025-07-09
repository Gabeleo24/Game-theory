#!/usr/bin/env python3
"""
FIND REAL MADRID TEAM ID
Search for the correct Real Madrid team ID in SportMonks API
"""

import requests
import json
import yaml
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealMadridFinder:
    """Find the correct Real Madrid team ID."""
    
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
    
    def check_team_id(self, team_id: int) -> dict:
        """Check what team a specific ID returns."""
        try:
            url = f"{self.base_url}/teams/{team_id}"
            params = {'api_token': self.api_token}
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                team_data = data.get('data', {})
                logger.info(f"Team ID {team_id}: {team_data.get('name', 'Unknown')} - {team_data.get('short_code', 'N/A')}")
                return team_data
            else:
                logger.error(f"Team ID {team_id}: Status {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Error checking team ID {team_id}: {e}")
            return {}
    
    def search_real_madrid(self):
        """Search for Real Madrid using different methods."""
        logger.info("🔍 Searching for Real Madrid...")
        
        # Method 1: Direct search
        try:
            url = f"{self.base_url}/teams/search/Real Madrid"
            params = {'api_token': self.api_token}
            
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                teams = data.get('data', [])
                
                logger.info(f"Found {len(teams)} teams matching 'Real Madrid':")
                for team in teams:
                    logger.info(f"  ID: {team.get('id')}, Name: {team.get('name')}, Short: {team.get('short_code')}")
                    
                    # Check if this is the main Real Madrid
                    if team.get('name') == 'Real Madrid' and team.get('short_code') in ['RMA', 'RM']:
                        logger.info(f"🎯 Main Real Madrid found: ID {team.get('id')}")
                        return team.get('id')
        
        except Exception as e:
            logger.error(f"Error in search: {e}")
        
        # Method 2: Check known IDs
        known_ids = [53, 3468, 496, 541]  # Common Real Madrid IDs
        logger.info("🔍 Checking known Real Madrid IDs...")
        
        for team_id in known_ids:
            team_data = self.check_team_id(team_id)
            if team_data and 'Real Madrid' in team_data.get('name', ''):
                logger.info(f"🎯 Real Madrid found at ID {team_id}")
                return team_id
        
        return None
    
    def get_team_with_includes(self, team_id: int):
        """Get team data with all possible includes."""
        try:
            url = f"{self.base_url}/teams/{team_id}"
            params = {
                'api_token': self.api_token,
                'include': 'country,venue,league,players,statistics'
            }
            
            response = self.session.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Team data retrieved with includes")
                
                # Save full response for analysis
                with open(f'real_madrid_team_{team_id}_full.json', 'w') as f:
                    json.dump(data, f, indent=2)
                
                logger.info(f"📁 Full data saved to real_madrid_team_{team_id}_full.json")
                return data
            else:
                logger.error(f"Failed to get team with includes: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting team with includes: {e}")
            return {}
    
    def find_players_alternative(self, team_id: int):
        """Try alternative methods to find players."""
        logger.info(f"🔍 Looking for alternative ways to get players for team {team_id}...")
        
        # Method 1: Search players by team
        try:
            url = f"{self.base_url}/players"
            params = {
                'api_token': self.api_token,
                'per_page': 50
            }
            
            response = self.session.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                players = data.get('data', [])
                
                real_madrid_players = []
                for player in players:
                    # Check if player has statistics for our team
                    statistics = player.get('statistics', [])
                    for stat in statistics:
                        if stat.get('team_id') == team_id:
                            real_madrid_players.append(player)
                            break
                
                logger.info(f"Found {len(real_madrid_players)} players for team {team_id}")
                
                if real_madrid_players:
                    # Show sample players
                    for i, player in enumerate(real_madrid_players[:5]):
                        person = player.get('person', {})
                        logger.info(f"  {i+1}. {person.get('name', 'Unknown')}")
                
                return real_madrid_players
                
        except Exception as e:
            logger.error(f"Error searching players: {e}")
        
        return []

def main():
    """Main function to find Real Madrid."""
    try:
        finder = RealMadridFinder()
        
        print("=" * 80)
        print("FINDING REAL MADRID TEAM ID")
        print("=" * 80)
        
        # Search for Real Madrid
        real_madrid_id = finder.search_real_madrid()
        
        if real_madrid_id:
            print(f"\n🎯 Real Madrid ID found: {real_madrid_id}")
            
            # Get full team data
            team_data = finder.get_team_with_includes(real_madrid_id)
            
            # Try to find players
            players = finder.find_players_alternative(real_madrid_id)
            
            print(f"\n✅ Summary:")
            print(f"   Real Madrid ID: {real_madrid_id}")
            print(f"   Team data available: {'Yes' if team_data else 'No'}")
            print(f"   Players found: {len(players)}")
            
        else:
            print("❌ Could not find Real Madrid team ID")
        
    except Exception as e:
        logger.error(f"❌ Error in main: {e}")

if __name__ == "__main__":
    main()
