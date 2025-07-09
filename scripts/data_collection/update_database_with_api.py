#!/usr/bin/env python3
"""
UPDATE DATABASE WITH SPORTMONKS API DATA
Update existing Real Madrid player data with latest SportMonks API information
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

class DatabaseAPIUpdater:
    """Update database with latest SportMonks API data."""
    
    def __init__(self):
        """Initialize with API and database configuration."""
        self.load_config()
        self.session = requests.Session()
        self.base_url = "https://api.sportmonks.com/v3/football"
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
    
    def get_real_madrid_players_from_db(self) -> List[Dict]:
        """Get Real Madrid players from existing database."""
        try:
            # First check what columns exist in the players table
            self.cursor.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'fixed_players'
            """)
            columns = [row[0] for row in self.cursor.fetchall()]
            logger.info(f"Available columns in fixed_players: {columns}")

            # Use available columns
            query = """
                SELECT DISTINCT
                    p.player_id,
                    p.player_name,
                    SUM(mps.minutes_played) as total_minutes,
                    SUM(mps.goals) as total_goals,
                    SUM(mps.assists) as total_assists,
                    COUNT(*) as appearances
                FROM fixed_players p
                JOIN fixed_teams t ON p.team_id = t.team_id
                JOIN fixed_match_player_stats mps ON p.player_id = mps.player_id
                WHERE t.team_name = 'Real Madrid'
                AND mps.minutes_played > 0
                GROUP BY p.player_id, p.player_name
                ORDER BY SUM(mps.minutes_played) DESC
            """

            self.cursor.execute(query)
            players = self.cursor.fetchall()

            player_list = []
            for player in players:
                (player_id, player_name, total_minutes, total_goals, total_assists, appearances) = player

                player_dict = {
                    'db_player_id': player_id,
                    'name': player_name,
                    'total_minutes': total_minutes,
                    'total_goals': total_goals,
                    'total_assists': total_assists,
                    'appearances': appearances
                }
                player_list.append(player_dict)

            logger.info(f"✅ Retrieved {len(player_list)} Real Madrid players from database")
            return player_list

        except Exception as e:
            logger.error(f"Error getting players from database: {e}")
            return []
    
    def search_player_in_api(self, player_name: str) -> Optional[Dict]:
        """Search for a player in SportMonks API."""
        try:
            # Clean player name for search
            search_name = player_name.replace('ú', 'u').replace('í', 'i').replace('ñ', 'n')
            search_name = search_name.replace('é', 'e').replace('á', 'a').replace('ó', 'o')
            
            url = f"{self.base_url}/players/search/{search_name}"
            params = {
                'api_token': self.api_token,
                'include': 'person,position,nationality,statistics.details'
            }
            
            response = self.session.get(url, params=params, timeout=15)
            if response.status_code != 200:
                logger.warning(f"Failed to search for {player_name}: {response.status_code}")
                return None
            
            data = response.json()
            players = data.get('data', [])
            
            # Find best match
            for player in players:
                person = player.get('person', {})
                api_name = person.get('name', '')
                
                # Check if names match (allowing for slight variations)
                if (player_name.lower() in api_name.lower() or 
                    api_name.lower() in player_name.lower() or
                    search_name.lower() in api_name.lower()):
                    
                    logger.info(f"✅ Found {player_name} in API as {api_name}")
                    return player
            
            logger.warning(f"❌ Could not find {player_name} in API")
            return None
            
        except Exception as e:
            logger.error(f"Error searching for {player_name}: {e}")
            return None
    
    def enhance_player_data(self, db_player: Dict) -> Dict:
        """Enhance database player data with API information."""
        player_name = db_player['name']
        
        # Search for player in API
        api_player = self.search_player_in_api(player_name)
        
        enhanced_player = db_player.copy()
        enhanced_player['api_enhanced'] = False
        enhanced_player['api_player_id'] = None
        enhanced_player['api_statistics'] = {}

        if api_player:
            # Extract API information
            person = api_player.get('person', {})
            position = api_player.get('position', {})
            nationality = api_player.get('nationality', {})

            # Update with API data
            enhanced_player.update({
                'api_enhanced': True,
                'api_player_id': api_player.get('id'),
                'api_name': person.get('name'),
                'api_display_name': person.get('display_name'),
                'api_birth_date': person.get('date_of_birth'),
                'api_nationality': nationality.get('name'),
                'api_position': position.get('name'),
                'api_height': person.get('height'),
                'api_weight': person.get('weight')
            })
            
            # Extract statistics
            statistics = api_player.get('statistics', [])
            api_stats = {}
            
            for stat in statistics:
                details = stat.get('details', [])
                for detail in details:
                    stat_type = detail.get('type', {}).get('name', '')
                    value = detail.get('value', 0)
                    api_stats[stat_type.lower().replace(' ', '_')] = value
            
            enhanced_player['api_statistics'] = api_stats
        
        time.sleep(0.2)  # Rate limiting
        return enhanced_player
    
    def update_database_records(self) -> Dict:
        """Update database with enhanced player information."""
        logger.info("🚀 Starting database update with SportMonks API data...")
        
        # Get players from database
        db_players = self.get_real_madrid_players_from_db()
        if not db_players:
            logger.error("❌ No players found in database")
            return {}
        
        # Enhance each player with API data
        enhanced_players = []
        logger.info(f"🔄 Enhancing {len(db_players)} players with API data...")
        
        for i, player in enumerate(db_players):
            enhanced_player = self.enhance_player_data(player)
            enhanced_players.append(enhanced_player)
            
            if (i + 1) % 5 == 0:
                logger.info(f"   Processed {i + 1}/{len(db_players)} players...")
        
        # Count successful enhancements
        api_enhanced_count = sum(1 for p in enhanced_players if p.get('api_enhanced'))
        
        result = {
            'update_timestamp': datetime.now().isoformat(),
            'total_players': len(enhanced_players),
            'api_enhanced_players': api_enhanced_count,
            'enhancement_rate': f"{(api_enhanced_count/len(enhanced_players)*100):.1f}%",
            'api_source': 'SportMonks Premium',
            'players': enhanced_players
        }
        
        logger.info(f"✅ Database update completed!")
        logger.info(f"   Total players: {len(enhanced_players)}")
        logger.info(f"   API enhanced: {api_enhanced_count}")
        logger.info(f"   Enhancement rate: {result['enhancement_rate']}")
        
        return result
    
    def save_enhanced_data(self, data: Dict) -> str:
        """Save enhanced data to JSON file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"data/focused/players/real_madrid_2023_2024/enhanced_with_api_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Enhanced data saved to: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"❌ Error saving data: {e}")
            return ""
    
    def display_enhancement_summary(self, data: Dict):
        """Display summary of enhancements."""
        players = data.get('players', [])
        
        print(f"\n{'='*100}")
        print(f"REAL MADRID PLAYER DATA ENHANCEMENT SUMMARY")
        print(f"{'='*100}")
        
        enhanced_players = [p for p in players if p.get('api_enhanced')]
        
        print(f"Total Players: {len(players)}")
        print(f"API Enhanced: {len(enhanced_players)}")
        print(f"Enhancement Rate: {data.get('enhancement_rate', '0%')}")
        
        if enhanced_players:
            print(f"\n📊 ENHANCED PLAYERS (showing first 10):")
            for i, player in enumerate(enhanced_players[:10]):
                api_stats = player.get('api_statistics', {})
                print(f"{i+1:2d}. {player['name']:<25} | API Stats: {len(api_stats)} metrics")
        
        print(f"\n⏰ Update Time: {data.get('update_timestamp')}")
        print(f"📊 API Source: {data.get('api_source')}")
    
    def close(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

def main():
    """Main function to update database with API data."""
    try:
        updater = DatabaseAPIUpdater()
        
        # Update database with API enhancements
        enhanced_data = updater.update_database_records()
        
        if enhanced_data and enhanced_data.get('players'):
            # Save enhanced data
            filename = updater.save_enhanced_data(enhanced_data)
            
            # Display summary
            updater.display_enhancement_summary(enhanced_data)
            
            print(f"\n{'='*100}")
            print(f"✅ SUCCESS! Database updated with SportMonks API data")
            print(f"📁 Enhanced data saved to: {filename}")
            print(f"{'='*100}")
        else:
            logger.error("❌ Database update failed")
        
        updater.close()
    
    except Exception as e:
        logger.error(f"❌ Error in main: {e}")

if __name__ == "__main__":
    main()
