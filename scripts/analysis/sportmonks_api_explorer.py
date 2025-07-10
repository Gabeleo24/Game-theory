#!/usr/bin/env python3
"""
SportMonks API Explorer - Comprehensive endpoint testing and data discovery
Explore what data we can pull from SportMonks API for database creation
"""

import requests
import yaml
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SportMonksAPIExplorer:
    """Explore SportMonks API endpoints and available data."""
    
    def __init__(self):
        """Initialize with API configuration."""
        self.load_config()
        self.session = requests.Session()
        self.base_url = "https://api.sportmonks.com/v3/football"
        
        # Manchester City team ID (need to find correct one)
        self.man_city_id = None
        
        # Common season IDs for testing
        self.test_seasons = {
            "2023-2024": 21646,
            "2022-2023": 19734,
            "2021-2022": 19686
        }
        
        # Common competition IDs
        self.competitions = {
            "Premier League": 8,
            "UEFA Champions League": 2,
            "FA Cup": 628,
            "EFL Cup": 12
        }
        
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
        """Make API request with error handling."""
        if params is None:
            params = {}
        
        params['api_token'] = self.api_token
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            logger.info(f"🔍 Testing endpoint: {endpoint}")
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Success: {endpoint}")
                return data
            else:
                logger.error(f"❌ Failed: {endpoint} - Status: {response.status_code}")
                logger.error(f"Response: {response.text[:200]}...")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Exception for {endpoint}: {e}")
            return {}
    
    def find_manchester_city_id(self) -> int:
        """Find Manchester City team ID by searching teams."""
        logger.info("🔍 Finding Manchester City team ID...")

        # Search for Manchester City
        teams_data = self.make_request("teams", {'search': 'Manchester City'})

        if teams_data and teams_data.get('data'):
            for team in teams_data['data']:
                if 'Manchester City' in team.get('name', ''):
                    logger.info(f"✅ Found Manchester City: ID {team['id']}")
                    return team['id']

        # Try alternative search
        teams_data = self.make_request("teams", {'search': 'Man City'})
        if teams_data and teams_data.get('data'):
            for team in teams_data['data']:
                if 'City' in team.get('name', '') and 'Manchester' in team.get('name', ''):
                    logger.info(f"✅ Found Manchester City: ID {team['id']}")
                    return team['id']

        # Try known ID from search results
        test_id = 9
        team_data = self.make_request(f"teams/{test_id}")
        if team_data and team_data.get('data'):
            team_name = team_data['data'].get('name', '')
            if 'Manchester City' in team_name or 'Man City' in team_name:
                logger.info(f"✅ Found Manchester City: ID {test_id}")
                return test_id

        logger.error("❌ Could not find Manchester City team ID")
        return None

    def explore_team_endpoints(self) -> Dict:
        """Explore team-related endpoints."""
        logger.info("🏟️ Exploring Team Endpoints")
        results = {}
        
        # Basic team info
        team_data = self.make_request(f"teams/{self.man_city_id}")
        if team_data:
            results['team_basic'] = {
                'endpoint': f"teams/{self.man_city_id}",
                'sample_data': team_data.get('data', {}),
                'description': 'Basic team information'
            }
        
        # Team with includes (test valid includes)
        team_detailed = self.make_request(
            f"teams/{self.man_city_id}",
            {'include': 'venue,country'}
        )
        if team_detailed:
            results['team_detailed'] = {
                'endpoint': f"teams/{self.man_city_id}",
                'params': {'include': 'venue,country,coach,transfers'},
                'sample_data': team_detailed.get('data', {}),
                'description': 'Detailed team information with venue, country, coach, transfers'
            }
        
        # Team squads (fix include parameters)
        squad_data = self.make_request(
            f"squads/seasons/{self.test_seasons['2023-2024']}/teams/{self.man_city_id}",
            {'include': 'player'}
        )
        if squad_data:
            results['team_squad'] = {
                'endpoint': f"squads/seasons/{self.test_seasons['2023-2024']}/teams/{self.man_city_id}",
                'params': {'include': 'player.position,player.nationality,player.person'},
                'sample_data': squad_data.get('data', []),
                'description': 'Team squad with player details'
            }
        
        return results
    
    def explore_match_endpoints(self) -> Dict:
        """Explore match-related endpoints."""
        logger.info("⚽ Exploring Match Endpoints")
        results = {}
        
        # Team fixtures for season - try different approaches
        # Method 1: Try fixtures by team and season
        fixtures = self.make_request(
            f"teams/{self.man_city_id}/fixtures",
            {'filters': f'seasonIds:{self.test_seasons["2023-2024"]}', 'include': 'participants,scores'}
        )

        # Method 2: If that fails, try general fixtures with team filter
        if not fixtures or not fixtures.get('data'):
            fixtures = self.make_request(
                "fixtures",
                {'filters': f'teamIds:{self.man_city_id};seasonIds:{self.test_seasons["2023-2024"]}', 'include': 'participants,scores'}
            )
        if fixtures:
            results['team_fixtures'] = {
                'endpoint': f"fixtures/between/{self.test_seasons['2023-2024']}/teams/{self.man_city_id}",
                'params': {'include': 'participants,scores,statistics'},
                'sample_data': fixtures.get('data', [])[:2],  # First 2 matches
                'description': 'Team fixtures for a season with basic stats'
            }
            
            # Get detailed match data for first fixture
            if fixtures.get('data') and len(fixtures['data']) > 0:
                match_id = fixtures['data'][0].get('id')
                if match_id:
                    match_detail = self.make_request(
                        f"fixtures/{match_id}",
                        {'include': 'lineups.player.person,lineups.player.position,lineups.statistics,events,substitutions,statistics'}
                    )
                    if match_detail:
                        results['match_detailed'] = {
                            'endpoint': f"fixtures/{match_id}",
                            'params': {'include': 'lineups.player.person,lineups.player.position,lineups.statistics,events,substitutions,statistics'},
                            'sample_data': match_detail.get('data', {}),
                            'description': 'Detailed match data with lineups, player stats, events'
                        }
        
        return results
    
    def explore_player_endpoints(self) -> Dict:
        """Explore player-related endpoints."""
        logger.info("👤 Exploring Player Endpoints")
        results = {}
        
        # Get a player ID from squad first
        squad_data = self.make_request(
            f"squads/seasons/{self.test_seasons['2023-2024']}/teams/{self.man_city_id}"
        )
        
        player_id = None
        if squad_data and squad_data.get('data'):
            for player_data in squad_data['data']:
                if player_data.get('player_id'):
                    player_id = player_data['player_id']
                    break
        
        if player_id:
            # Player basic info
            player_info = self.make_request(
                f"players/{player_id}",
                {'include': 'position,nationality,person,statistics'}
            )
            if player_info:
                results['player_info'] = {
                    'endpoint': f"players/{player_id}",
                    'params': {'include': 'position,nationality,person,statistics'},
                    'sample_data': player_info.get('data', {}),
                    'description': 'Player information with position, nationality, statistics'
                }
            
            # Player statistics for season
            player_stats = self.make_request(
                f"players/{player_id}/statistics/seasons/{self.test_seasons['2023-2024']}"
            )
            if player_stats:
                results['player_season_stats'] = {
                    'endpoint': f"players/{player_id}/statistics/seasons/{self.test_seasons['2023-2024']}",
                    'sample_data': player_stats.get('data', []),
                    'description': 'Player statistics for a specific season'
                }
        
        return results
    
    def explore_competition_endpoints(self) -> Dict:
        """Explore competition and season endpoints."""
        logger.info("🏆 Exploring Competition Endpoints")
        results = {}
        
        # Competitions list
        competitions = self.make_request("competitions")
        if competitions:
            results['competitions_list'] = {
                'endpoint': 'competitions',
                'sample_data': competitions.get('data', [])[:5],  # First 5
                'description': 'Available competitions'
            }
        
        # Seasons list
        seasons = self.make_request("seasons")
        if seasons:
            results['seasons_list'] = {
                'endpoint': 'seasons',
                'sample_data': seasons.get('data', [])[:5],  # First 5
                'description': 'Available seasons'
            }
        
        # Season details
        season_detail = self.make_request(
            f"seasons/{self.test_seasons['2023-2024']}",
            {'include': 'league,stages'}
        )
        if season_detail:
            results['season_detail'] = {
                'endpoint': f"seasons/{self.test_seasons['2023-2024']}",
                'params': {'include': 'league,stages'},
                'sample_data': season_detail.get('data', {}),
                'description': 'Season details with league and stages'
            }
        
        return results
    
    def explore_statistics_endpoints(self) -> Dict:
        """Explore statistics endpoints."""
        logger.info("📊 Exploring Statistics Endpoints")
        results = {}
        
        # Team statistics for season
        team_stats = self.make_request(
            f"teams/{self.man_city_id}/statistics/seasons/{self.test_seasons['2023-2024']}"
        )
        if team_stats:
            results['team_season_stats'] = {
                'endpoint': f"teams/{self.man_city_id}/statistics/seasons/{self.test_seasons['2023-2024']}",
                'sample_data': team_stats.get('data', []),
                'description': 'Team statistics for a season'
            }
        
        return results
    
    def run_full_exploration(self) -> Dict:
        """Run complete API exploration."""
        logger.info("🚀 Starting SportMonks API Exploration")

        # First find Manchester City team ID
        self.man_city_id = self.find_manchester_city_id()
        if not self.man_city_id:
            logger.error("❌ Cannot proceed without Manchester City team ID")
            return {}

        exploration_results = {
            'timestamp': datetime.now().isoformat(),
            'api_base_url': self.base_url,
            'test_team': f"Manchester City (ID: {self.man_city_id})",
            'test_season': f"2023-2024 (ID: {self.test_seasons['2023-2024']})",
            'endpoints': {}
        }
        
        # Explore different endpoint categories
        exploration_results['endpoints']['teams'] = self.explore_team_endpoints()
        time.sleep(2)  # Rate limiting
        
        exploration_results['endpoints']['matches'] = self.explore_match_endpoints()
        time.sleep(2)
        
        exploration_results['endpoints']['players'] = self.explore_player_endpoints()
        time.sleep(2)
        
        exploration_results['endpoints']['competitions'] = self.explore_competition_endpoints()
        time.sleep(2)
        
        exploration_results['endpoints']['statistics'] = self.explore_statistics_endpoints()
        
        return exploration_results
    
    def save_results(self, results: Dict, filename: str = None):
        """Save exploration results to file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"logs/sportmonks_api_exploration_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"✅ Results saved to: {filename}")
        except Exception as e:
            logger.error(f"❌ Failed to save results: {e}")

def main():
    """Main execution function."""
    explorer = SportMonksAPIExplorer()
    
    # Run exploration
    results = explorer.run_full_exploration()
    
    # Save results
    explorer.save_results(results)
    
    # Print summary
    print("\n" + "="*80)
    print("🔍 SPORTMONKS API EXPLORATION SUMMARY")
    print("="*80)
    
    for category, endpoints in results['endpoints'].items():
        print(f"\n📂 {category.upper()} ENDPOINTS:")
        for endpoint_name, endpoint_data in endpoints.items():
            print(f"  ✅ {endpoint_name}: {endpoint_data.get('description', 'No description')}")
    
    print(f"\n📄 Full results saved to logs/")
    print("="*80)

if __name__ == "__main__":
    main()
