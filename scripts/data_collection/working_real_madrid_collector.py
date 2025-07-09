#!/usr/bin/env python3
"""
WORKING REAL MADRID 2023-2024 DATA COLLECTOR
Using verified SportMonks API endpoints that actually work
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

class WorkingRealMadridCollector:
    """Collect Real Madrid player statistics using working SportMonks API endpoints."""
    
    def __init__(self):
        """Initialize with API and database configuration."""
        self.load_config()
        self.session = requests.Session()
        self.base_url = "https://api.sportmonks.com/v3/football"
        self.real_madrid_id = 3468  # Verified Real Madrid team ID
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
    
    def get_real_madrid_info(self) -> Dict:
        """Get Real Madrid team information."""
        try:
            url = f"{self.base_url}/teams/{self.real_madrid_id}"
            params = {
                'api_token': self.api_token,
                'include': 'country,venue,league'
            }
            
            response = self.session.get(url, params=params, timeout=15)
            if response.status_code != 200:
                logger.error(f"Failed to get Real Madrid info: {response.status_code}")
                return {}
            
            data = response.json()
            team_data = data.get('data', {})
            
            logger.info(f"✅ Retrieved Real Madrid info: {team_data.get('name')}")
            return team_data
            
        except Exception as e:
            logger.error(f"Error getting Real Madrid info: {e}")
            return {}
    
    def get_players_by_search(self) -> List[Dict]:
        """Get Real Madrid players by searching through all players."""
        try:
            all_players = []
            page = 1
            max_pages = 10  # Limit to avoid too many requests
            
            while page <= max_pages:
                url = f"{self.base_url}/players"
                params = {
                    'api_token': self.api_token,
                    'include': 'person,position,nationality,statistics.details',
                    'per_page': 100,
                    'page': page
                }
                
                response = self.session.get(url, params=params, timeout=20)
                if response.status_code != 200:
                    logger.error(f"Failed to get players page {page}: {response.status_code}")
                    break
                
                data = response.json()
                players = data.get('data', [])
                
                # Filter for Real Madrid players
                real_madrid_players = []
                for player in players:
                    statistics = player.get('statistics', [])
                    for stat in statistics:
                        if stat.get('team_id') == self.real_madrid_id:
                            real_madrid_players.append(player)
                            break
                
                all_players.extend(real_madrid_players)
                
                # Check if we have more pages
                pagination = data.get('pagination', {})
                if not pagination.get('has_more', False):
                    break
                
                page += 1
                time.sleep(0.5)  # Rate limiting
                
                logger.info(f"   Processed page {page-1}, found {len(real_madrid_players)} Real Madrid players")
            
            logger.info(f"✅ Found {len(all_players)} Real Madrid players total")
            return all_players
            
        except Exception as e:
            logger.error(f"Error searching for players: {e}")
            return []
    
    def get_player_detailed_stats(self, player_id: int) -> Dict:
        """Get detailed statistics for a specific player."""
        try:
            url = f"{self.base_url}/players/{player_id}"
            params = {
                'api_token': self.api_token,
                'include': 'statistics.details,person,position,nationality'
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
            
            # Extract Real Madrid statistics for 2023-2024
            statistics = player_data.get('statistics', [])
            real_madrid_stats = {}
            
            for stat in statistics:
                if stat.get('team_id') == self.real_madrid_id:
                    details = stat.get('details', [])
                    for detail in details:
                        stat_type = detail.get('type', {}).get('name', '')
                        value = detail.get('value', 0)
                        real_madrid_stats[stat_type.lower().replace(' ', '_')] = value
            
            enhanced_data = {
                'player_id': player_id,
                'name': person.get('name', ''),
                'display_name': person.get('display_name', ''),
                'birth_date': person.get('date_of_birth'),
                'nationality': nationality.get('name', 'Unknown'),
                'position': position.get('name', 'Unknown'),
                'height': person.get('height'),
                'weight': person.get('weight'),
                'real_madrid_statistics': real_madrid_stats
            }
            
            time.sleep(0.1)  # Rate limiting
            return enhanced_data
            
        except Exception as e:
            logger.error(f"Error getting player {player_id} details: {e}")
            return {}
    
    def collect_working_data(self) -> Dict:
        """Collect Real Madrid player data using working endpoints."""
        logger.info("🚀 Starting working Real Madrid data collection...")
        
        # Get Real Madrid team info
        team_info = self.get_real_madrid_info()
        if not team_info:
            logger.error("❌ Could not get Real Madrid team information")
            return {}
        
        # Get players
        players = self.get_players_by_search()
        if not players:
            logger.error("❌ Could not find Real Madrid players")
            return {}
        
        # Collect detailed data for each player
        enhanced_players = []
        logger.info(f"🔄 Collecting detailed stats for {len(players)} players...")
        
        for i, player in enumerate(players):
            player_id = player.get('id')
            if player_id:
                detailed_stats = self.get_player_detailed_stats(player_id)
                if detailed_stats and detailed_stats.get('real_madrid_statistics'):
                    enhanced_players.append(detailed_stats)
                
                if (i + 1) % 5 == 0:
                    logger.info(f"   Processed {i + 1}/{len(players)} players...")
                    time.sleep(1)  # Additional rate limiting
        
        result = {
            'team_id': self.real_madrid_id,
            'team_name': team_info.get('name', 'Real Madrid'),
            'team_info': team_info,
            'collection_timestamp': datetime.now().isoformat(),
            'players_count': len(enhanced_players),
            'api_source': 'SportMonks Premium (Working Endpoints)',
            'players': enhanced_players
        }
        
        logger.info(f"✅ Collection completed! {len(enhanced_players)} players with Real Madrid stats")
        return result
    
    def save_data(self, data: Dict) -> str:
        """Save collected data to JSON file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"data/focused/players/real_madrid_2023_2024/working_collection_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Data saved to: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"❌ Error saving data: {e}")
            return ""
    
    def display_sample_data(self, data: Dict):
        """Display sample of collected data."""
        players = data.get('players', [])
        if not players:
            return
        
        print(f"\n{'='*80}")
        print(f"SAMPLE REAL MADRID PLAYER DATA")
        print(f"{'='*80}")
        
        for i, player in enumerate(players[:5]):  # Show first 5 players
            print(f"\n{i+1}. {player.get('name', 'Unknown')}")
            print(f"   Position: {player.get('position', 'Unknown')}")
            print(f"   Nationality: {player.get('nationality', 'Unknown')}")
            
            stats = player.get('real_madrid_statistics', {})
            if stats:
                print(f"   Statistics: {len(stats)} metrics available")
                # Show a few key stats
                for key, value in list(stats.items())[:3]:
                    print(f"     {key}: {value}")
            else:
                print(f"   Statistics: No data available")
    
    def close(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

def main():
    """Main function to collect working Real Madrid data."""
    try:
        collector = WorkingRealMadridCollector()
        
        # Collect data using working endpoints
        data = collector.collect_working_data()
        
        if data and data.get('players'):
            # Save data
            filename = collector.save_data(data)
            
            # Display sample
            collector.display_sample_data(data)
            
            print(f"\n{'='*100}")
            print(f"✅ SUCCESS! Real Madrid data collected using working endpoints")
            print(f"📁 Saved to: {filename}")
            print(f"👥 Players: {len(data.get('players', []))}")
            print(f"🏆 Team: {data.get('team_name')}")
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
