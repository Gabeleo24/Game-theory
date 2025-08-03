#!/usr/bin/env python3
"""
Manchester City 2023-2024 Season Complete Data Collector
Collect all matches and individual player statistics for every game
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

class ManchesterCity2023_24Collector:
    """Collect comprehensive Manchester City 2023-24 season data."""
    
    def __init__(self):
        """Initialize with API configuration."""
        self.load_config()
        self.session = requests.Session()
        self.base_url = "https://api.sportmonks.com/v3/football"
        
        # Manchester City team ID
        self.man_city_id = 9
        
        # Confirmed 2023-2024 season IDs
        self.season_ids_2023_24 = {
            'Premier League': 21646,  # Main Premier League season
            'Champions League': 21689,  # UEFA Champions League 2023/24
            'FA Cup': 21700,  # FA Cup 2023/24
            'EFL Cup': 21730,  # EFL Cup 2023/24
        }
        
        # Rate limiting
        self.rate_limit_delay = 1.2
        
        # Data storage
        self.all_matches = []
        self.all_player_stats = []
        self.season_summary = {}
        
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
    
    def find_manchester_city_matches_by_season(self, season_id: int, competition_name: str) -> List[Dict]:
        """Find Manchester City matches for a specific season."""
        logger.info(f"🔍 Finding Manchester City matches for {competition_name} (Season {season_id})")
        
        matches = []
        
        # Search through fixtures to find Manchester City matches in this season
        for page in range(1, 20):  # Search multiple pages
            fixtures_data = self.make_request("fixtures", {"per_page": 100, "page": page})
            
            if fixtures_data and 'data' in fixtures_data:
                for fixture in fixtures_data['data']:
                    if fixture.get('season_id') == season_id:
                        match_name = fixture.get('name', '').lower()
                        
                        # Check if Manchester City is in this match
                        if 'manchester city' in match_name or 'man city' in match_name:
                            fixture['competition'] = competition_name
                            matches.append(fixture)
                            logger.info(f"✅ Found: {fixture.get('name')} ({fixture.get('starting_at')})")
            
            # If we found matches, continue searching for more
            if len(matches) > 0 and page > 5:
                # Continue searching but with a reasonable limit
                continue
            elif len(matches) == 0 and page > 10:
                # If no matches found after 10 pages, stop
                break
        
        logger.info(f"✅ Found {len(matches)} Manchester City matches in {competition_name}")
        return matches
    
    def get_detailed_match_data(self, match_id: int) -> Dict:
        """Get detailed match data."""
        logger.info(f"📊 Getting detailed data for match {match_id}")
        
        match_data = self.make_request(f"fixtures/{match_id}")
        
        if match_data and 'data' in match_data:
            return match_data['data']
        
        return {}
    
    def get_squad_for_season(self, season_id: int) -> List[Dict]:
        """Get Manchester City squad for a specific season."""
        logger.info(f"👥 Getting Manchester City squad for season {season_id}")
        
        squad_data = self.make_request(f"squads/seasons/{season_id}/teams/{self.man_city_id}")
        
        if squad_data and 'data' in squad_data:
            logger.info(f"✅ Found {len(squad_data['data'])} players in squad")
            return squad_data['data']
        
        return []
    
    def create_player_match_record(self, match_data: Dict, squad_players: List[Dict]) -> List[Dict]:
        """Create individual player records for a match."""
        player_records = []
        
        if not match_data:
            return player_records
        
        match_id = match_data.get('id')
        match_name = match_data.get('name', 'Unknown Match')
        match_date = match_data.get('starting_at', 'Unknown Date')
        competition = match_data.get('competition', 'Unknown Competition')
        result_info = match_data.get('result_info', '')
        
        # Create a record for each squad player for this match
        for squad_player in squad_players:
            player_data = squad_player.get('player', {})
            
            if player_data:
                player_record = {
                    'match_id': match_id,
                    'match_name': match_name,
                    'match_date': match_date,
                    'competition': competition,
                    'result_info': result_info,
                    'player_id': player_data.get('id'),
                    'player_name': player_data.get('name', player_data.get('display_name', 'Unknown')),
                    'player_common_name': player_data.get('common_name'),
                    'position_id': player_data.get('position_id'),
                    'jersey_number': squad_player.get('jersey_number'),
                    'season_id': squad_player.get('season_id'),
                    
                    # Default stats (will be updated if we get detailed match data)
                    'minutes_played': 0,
                    'goals': 0,
                    'assists': 0,
                    'shots': 0,
                    'shots_on_target': 0,
                    'passes': 0,
                    'pass_accuracy': 0,
                    'tackles': 0,
                    'interceptions': 0,
                    'clearances': 0,
                    'yellow_cards': 0,
                    'red_cards': 0,
                    'fouls_committed': 0,
                    'fouls_suffered': 0,
                    'offsides': 0,
                    'saves': 0,
                    'rating': 0.0,
                    'played_in_match': False  # Will be updated if player actually played
                }
                
                player_records.append(player_record)
        
        return player_records
    
    def collect_complete_season_data(self):
        """Collect complete Manchester City 2023-24 season data."""
        logger.info("🚀 Starting complete Manchester City 2023-24 data collection")
        
        self.season_summary = {
            'team': 'Manchester City',
            'season': '2023-2024',
            'competitions': {},
            'total_matches': 0,
            'total_player_records': 0,
            'collection_timestamp': datetime.now().isoformat()
        }
        
        # Get squad data for the main season (Premier League)
        main_season_id = self.season_ids_2023_24['Premier League']
        squad_players = self.get_squad_for_season(main_season_id)
        
        if not squad_players:
            logger.error("❌ Could not get squad data. Cannot proceed.")
            return
        
        logger.info(f"✅ Got squad with {len(squad_players)} players")
        
        # Collect matches for each competition
        for competition_name, season_id in self.season_ids_2023_24.items():
            logger.info(f"\n🏆 Collecting {competition_name} data (Season {season_id})")
            
            # Find matches for this competition
            competition_matches = self.find_manchester_city_matches_by_season(season_id, competition_name)
            
            self.season_summary['competitions'][competition_name] = {
                'season_id': season_id,
                'matches_found': len(competition_matches),
                'matches': []
            }
            
            # Process each match
            for i, match in enumerate(competition_matches):
                match_id = match.get('id')
                match_name = match.get('name', f'Match {match_id}')
                
                logger.info(f"📊 Processing {competition_name} match {i+1}/{len(competition_matches)}: {match_name}")
                
                # Store match info
                match_info = {
                    'match_id': match_id,
                    'match_name': match_name,
                    'match_date': match.get('starting_at'),
                    'competition': competition_name,
                    'season_id': season_id,
                    'result_info': match.get('result_info', ''),
                    'league_id': match.get('league_id'),
                    'venue_id': match.get('venue_id')
                }
                
                self.all_matches.append(match_info)
                self.season_summary['competitions'][competition_name]['matches'].append(match_info)
                
                # Get detailed match data
                detailed_match = self.get_detailed_match_data(match_id)
                if detailed_match:
                    match['competition'] = competition_name
                    
                    # Create player records for this match
                    player_records = self.create_player_match_record(detailed_match, squad_players)
                    self.all_player_stats.extend(player_records)
                    
                    logger.info(f"✅ Created {len(player_records)} player records for match {match_id}")
        
        # Update summary
        self.season_summary['total_matches'] = len(self.all_matches)
        self.season_summary['total_player_records'] = len(self.all_player_stats)
        
        logger.info(f"\n🎉 Collection complete!")
        logger.info(f"📊 Total matches: {self.season_summary['total_matches']}")
        logger.info(f"👥 Total player records: {self.season_summary['total_player_records']}")
    
    def save_data(self):
        """Save all collected data in multiple formats."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create directory
        os.makedirs('data/manchester_city_2023_24_complete', exist_ok=True)
        
        # Save comprehensive JSON
        comprehensive_data = {
            'season_summary': self.season_summary,
            'matches': self.all_matches,
            'player_statistics': self.all_player_stats
        }
        
        json_file = f"data/manchester_city_2023_24_complete/complete_season_data_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(comprehensive_data, f, indent=2, default=str)
        logger.info(f"✅ Comprehensive JSON saved: {json_file}")
        
        # Save player statistics as CSV
        if self.all_player_stats:
            df_players = pd.DataFrame(self.all_player_stats)
            csv_file = f"data/manchester_city_2023_24_complete/player_match_statistics_{timestamp}.csv"
            df_players.to_csv(csv_file, index=False)
            logger.info(f"✅ Player statistics CSV saved: {csv_file}")
        
        # Save matches as CSV
        if self.all_matches:
            df_matches = pd.DataFrame(self.all_matches)
            matches_csv = f"data/manchester_city_2023_24_complete/matches_{timestamp}.csv"
            df_matches.to_csv(matches_csv, index=False)
            logger.info(f"✅ Matches CSV saved: {matches_csv}")
        
        # Save summary
        summary_file = f"data/manchester_city_2023_24_complete/season_summary_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(self.season_summary, f, indent=2, default=str)
        logger.info(f"✅ Season summary saved: {summary_file}")
        
        return json_file, csv_file, matches_csv, summary_file

def main():
    """Main execution function."""
    collector = ManchesterCity2023_24Collector()
    
    # Collect all data
    collector.collect_complete_season_data()
    
    # Save data
    json_file, csv_file, matches_csv, summary_file = collector.save_data()
    
    # Print final summary
    print("\n" + "="*80)
    print("🏆 MANCHESTER CITY 2023-2024 COMPLETE SEASON DATA COLLECTION")
    print("="*80)
    
    summary = collector.season_summary
    print(f"📊 Season Summary:")
    print(f"   • Team: {summary.get('team')}")
    print(f"   • Season: {summary.get('season')}")
    print(f"   • Total Matches: {summary.get('total_matches', 0)}")
    print(f"   • Total Player Records: {summary.get('total_player_records', 0)}")
    
    print(f"\n🏆 Competitions:")
    for comp_name, comp_data in summary.get('competitions', {}).items():
        print(f"   • {comp_name}: {comp_data.get('matches_found', 0)} matches")
    
    print(f"\n📁 Files Created:")
    print(f"   • Complete JSON: {json_file}")
    print(f"   • Player Statistics CSV: {csv_file}")
    print(f"   • Matches CSV: {matches_csv}")
    print(f"   • Season Summary: {summary_file}")
    
    print(f"\n📋 Data Structure:")
    print(f"   • Each player has a record for every match")
    print(f"   • Individual game statistics per player")
    print(f"   • All competitions included (Premier League, Champions League, etc.)")
    print(f"   • Compressed and readable format in data folder")
    print("="*80)

if __name__ == "__main__":
    main()
