#!/usr/bin/env python3
"""
Manchester City 2023-2024 Squad-Based Data Collector
Create comprehensive player statistics framework using available squad data
"""

import requests
import yaml
import json
import time
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ManchesterCitySquadCollector:
    """Collect Manchester City squad data and create comprehensive player framework."""
    
    def __init__(self):
        """Initialize with API configuration."""
        self.load_config()
        self.session = requests.Session()
        self.base_url = "https://api.sportmonks.com/v3/football"
        
        # Manchester City team ID
        self.man_city_id = 9
        
        # 2023-2024 Premier League season ID (confirmed working)
        self.season_2023_24 = 21646
        
        # Rate limiting
        self.rate_limit_delay = 1.2
        
        # Data storage
        self.squad_data = []
        self.player_details = {}
        self.season_framework = {}
        
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
                return {}
                
        except Exception as e:
            logger.error(f"❌ Exception for {endpoint}: {e}")
            return {}
    
    def get_squad_data(self):
        """Get Manchester City squad for 2023-24 season."""
        logger.info("👥 Getting Manchester City squad for 2023-24 season")
        
        squad_data = self.make_request(f"squads/seasons/{self.season_2023_24}/teams/{self.man_city_id}")
        
        if squad_data and 'data' in squad_data:
            self.squad_data = squad_data['data']
            logger.info(f"✅ Found {len(self.squad_data)} players in squad")
            return True
        
        logger.error("❌ Could not get squad data")
        return False
    
    def get_player_details(self, player_id: int):
        """Get detailed information for a specific player."""
        logger.info(f"👤 Getting details for player {player_id}")
        
        player_data = self.make_request(f"players/{player_id}")
        
        if player_data and 'data' in player_data:
            return player_data['data']
        
        return {}
    
    def collect_all_player_details(self):
        """Collect detailed information for all squad players."""
        logger.info("📊 Collecting detailed information for all squad players")
        
        for i, squad_player in enumerate(self.squad_data):
            player_id = squad_player.get('player_id')
            
            if player_id:
                logger.info(f"👤 Processing player {i+1}/{len(self.squad_data)}: ID {player_id}")
                
                player_details = self.get_player_details(player_id)
                if player_details:
                    # Combine squad info with player details
                    combined_info = {
                        **squad_player,
                        'player_details': player_details
                    }
                    self.player_details[player_id] = combined_info
                    
                    player_name = player_details.get('name', 'Unknown')
                    logger.info(f"✅ Collected details for: {player_name}")
        
        logger.info(f"✅ Collected details for {len(self.player_details)} players")
    
    def create_season_framework(self):
        """Create comprehensive season framework with player statistics template."""
        logger.info("🏗️ Creating comprehensive season framework")
        
        # Typical Premier League season has 38 matches
        # Plus cup competitions, estimate 50-60 total matches
        estimated_matches = 55
        
        self.season_framework = {
            'season_info': {
                'team': 'Manchester City',
                'season': '2023-2024',
                'season_id': self.season_2023_24,
                'estimated_total_matches': estimated_matches,
                'squad_size': len(self.player_details),
                'data_collection_date': datetime.now().isoformat()
            },
            'squad_overview': [],
            'player_season_templates': [],
            'competitions': {
                'Premier League': {
                    'estimated_matches': 38,
                    'description': 'English Premier League 2023-2024'
                },
                'UEFA Champions League': {
                    'estimated_matches': 8,
                    'description': 'UEFA Champions League 2023-2024'
                },
                'FA Cup': {
                    'estimated_matches': 6,
                    'description': 'FA Cup 2023-2024'
                },
                'EFL Cup': {
                    'estimated_matches': 5,
                    'description': 'EFL Cup 2023-2024'
                }
            }
        }
        
        # Create squad overview
        for player_id, player_info in self.player_details.items():
            player_details = player_info.get('player_details', {})
            
            squad_overview = {
                'player_id': player_id,
                'player_name': player_details.get('name', 'Unknown'),
                'common_name': player_details.get('common_name', ''),
                'jersey_number': player_info.get('jersey_number'),
                'position_id': player_details.get('position_id'),
                'height': player_details.get('height'),
                'weight': player_details.get('weight'),
                'date_of_birth': player_details.get('date_of_birth'),
                'nationality_id': player_details.get('nationality_id'),
                'country_id': player_details.get('country_id')
            }
            
            self.season_framework['squad_overview'].append(squad_overview)
        
        # Create player season templates (framework for match-by-match stats)
        for player_id, player_info in self.player_details.items():
            player_details = player_info.get('player_details', {})
            
            # Create template for each estimated match
            player_season_template = {
                'player_id': player_id,
                'player_name': player_details.get('name', 'Unknown'),
                'common_name': player_details.get('common_name', ''),
                'jersey_number': player_info.get('jersey_number'),
                'position_id': player_details.get('position_id'),
                'season_matches': []
            }
            
            # Create match templates
            for match_num in range(1, estimated_matches + 1):
                match_template = {
                    'match_number': match_num,
                    'match_id': f"TBD_{match_num}",
                    'match_date': 'TBD',
                    'opponent': 'TBD',
                    'competition': 'TBD',
                    'home_away': 'TBD',
                    'result': 'TBD',
                    
                    # Player performance metrics
                    'played': False,
                    'started': False,
                    'minutes_played': 0,
                    'goals': 0,
                    'assists': 0,
                    'shots': 0,
                    'shots_on_target': 0,
                    'passes': 0,
                    'passes_completed': 0,
                    'pass_accuracy_percent': 0,
                    'tackles': 0,
                    'interceptions': 0,
                    'clearances': 0,
                    'crosses': 0,
                    'dribbles': 0,
                    'dribbles_successful': 0,
                    'fouls_committed': 0,
                    'fouls_suffered': 0,
                    'yellow_cards': 0,
                    'red_cards': 0,
                    'offsides': 0,
                    'saves': 0,  # For goalkeepers
                    'goals_conceded': 0,  # For goalkeepers
                    'clean_sheet': False,  # For goalkeepers
                    'rating': 0.0,
                    'player_of_match': False
                }
                
                player_season_template['season_matches'].append(match_template)
            
            self.season_framework['player_season_templates'].append(player_season_template)
        
        logger.info("✅ Season framework created successfully")
    
    def save_comprehensive_data(self):
        """Save all collected data in multiple readable formats."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create directory
        os.makedirs('data/manchester_city_2023_24_framework', exist_ok=True)
        
        # Save complete framework as JSON
        framework_file = f"data/manchester_city_2023_24_framework/season_framework_{timestamp}.json"
        with open(framework_file, 'w') as f:
            json.dump(self.season_framework, f, indent=2, default=str)
        logger.info(f"✅ Season framework saved: {framework_file}")
        
        # Save squad overview as CSV
        squad_df = pd.DataFrame(self.season_framework['squad_overview'])
        squad_csv = f"data/manchester_city_2023_24_framework/squad_overview_{timestamp}.csv"
        squad_df.to_csv(squad_csv, index=False)
        logger.info(f"✅ Squad overview CSV saved: {squad_csv}")
        
        # Save player match templates as CSV (flattened)
        all_player_matches = []
        for player_template in self.season_framework['player_season_templates']:
            player_id = player_template['player_id']
            player_name = player_template['player_name']
            
            for match in player_template['season_matches']:
                match_record = {
                    'player_id': player_id,
                    'player_name': player_name,
                    'jersey_number': player_template['jersey_number'],
                    **match
                }
                all_player_matches.append(match_record)
        
        matches_df = pd.DataFrame(all_player_matches)
        matches_csv = f"data/manchester_city_2023_24_framework/player_match_templates_{timestamp}.csv"
        matches_df.to_csv(matches_csv, index=False)
        logger.info(f"✅ Player match templates CSV saved: {matches_csv}")
        
        # Save detailed player information
        detailed_players = []
        for player_id, player_info in self.player_details.items():
            player_details = player_info.get('player_details', {})
            detailed_record = {
                'player_id': player_id,
                'squad_id': player_info.get('id'),
                'team_id': player_info.get('team_id'),
                'season_id': player_info.get('season_id'),
                'jersey_number': player_info.get('jersey_number'),
                'position_id': player_info.get('position_id'),
                'has_values': player_info.get('has_values'),
                
                # Player details
                'name': player_details.get('name'),
                'common_name': player_details.get('common_name'),
                'firstname': player_details.get('firstname'),
                'lastname': player_details.get('lastname'),
                'display_name': player_details.get('display_name'),
                'height': player_details.get('height'),
                'weight': player_details.get('weight'),
                'date_of_birth': player_details.get('date_of_birth'),
                'gender': player_details.get('gender'),
                'nationality_id': player_details.get('nationality_id'),
                'country_id': player_details.get('country_id'),
                'city_id': player_details.get('city_id'),
                'detailed_position_id': player_details.get('detailed_position_id'),
                'type_id': player_details.get('type_id'),
                'image_path': player_details.get('image_path')
            }
            detailed_players.append(detailed_record)
        
        detailed_df = pd.DataFrame(detailed_players)
        detailed_csv = f"data/manchester_city_2023_24_framework/detailed_players_{timestamp}.csv"
        detailed_df.to_csv(detailed_csv, index=False)
        logger.info(f"✅ Detailed players CSV saved: {detailed_csv}")
        
        return framework_file, squad_csv, matches_csv, detailed_csv
    
    def run_collection(self):
        """Run complete data collection process."""
        logger.info("🚀 Starting Manchester City 2023-24 squad-based collection")
        
        # Get squad data
        if not self.get_squad_data():
            logger.error("❌ Cannot proceed without squad data")
            return
        
        # Get detailed player information
        self.collect_all_player_details()
        
        # Create comprehensive framework
        self.create_season_framework()
        
        # Save all data
        return self.save_comprehensive_data()

def main():
    """Main execution function."""
    collector = ManchesterCitySquadCollector()
    
    # Run collection
    framework_file, squad_csv, matches_csv, detailed_csv = collector.run_collection()
    
    # Print summary
    print("\n" + "="*80)
    print("🏆 MANCHESTER CITY 2023-2024 COMPREHENSIVE SQUAD DATA COLLECTION")
    print("="*80)
    
    framework = collector.season_framework
    season_info = framework.get('season_info', {})
    
    print(f"📊 Collection Summary:")
    print(f"   • Team: {season_info.get('team')}")
    print(f"   • Season: {season_info.get('season')}")
    print(f"   • Squad Size: {season_info.get('squad_size')} players")
    print(f"   • Estimated Total Matches: {season_info.get('estimated_total_matches')}")
    
    print(f"\n👥 Squad Overview:")
    for player in framework.get('squad_overview', [])[:10]:  # Show first 10 players
        print(f"   • #{player.get('jersey_number', 'N/A')} {player.get('player_name')} (ID: {player.get('player_id')})")
    
    if len(framework.get('squad_overview', [])) > 10:
        print(f"   • ... and {len(framework.get('squad_overview', [])) - 10} more players")
    
    print(f"\n🏆 Competitions Framework:")
    for comp_name, comp_info in framework.get('competitions', {}).items():
        print(f"   • {comp_name}: {comp_info.get('estimated_matches')} estimated matches")
    
    print(f"\n📁 Files Created:")
    print(f"   • Season Framework JSON: {framework_file}")
    print(f"   • Squad Overview CSV: {squad_csv}")
    print(f"   • Player Match Templates CSV: {matches_csv}")
    print(f"   • Detailed Players CSV: {detailed_csv}")
    
    print(f"\n📋 Data Structure:")
    print(f"   • Complete squad with detailed player information")
    print(f"   • Match-by-match template for every player")
    print(f"   • Ready for individual game statistics input")
    print(f"   • Comprehensive performance metrics framework")
    print(f"   • Compressed and readable format in data folder")
    print("="*80)

if __name__ == "__main__":
    main()
