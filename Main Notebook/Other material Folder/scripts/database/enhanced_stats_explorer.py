#!/usr/bin/env python3
"""
Enhanced Statistics Explorer for SportMonks API
Explore advanced metrics like expected goals (xG), xA, xGChain, etc.
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

class EnhancedStatsExplorer:
    """Explore advanced statistics available in SportMonks API."""
    
    def __init__(self):
        """Initialize with API configuration."""
        self.load_config()
        self.session = requests.Session()
        self.base_url = "https://api.sportmonks.com/v3/football"
        
        # Manchester City team ID
        self.man_city_id = 9
        
        # 2023-2024 Premier League season ID
        self.season_2023_24 = 21646
        
        # Rate limiting
        self.rate_limit_delay = 1.2
        
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
            logger.info(f"🔍 Testing: {endpoint}")
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Success: {endpoint}")
                
                # Rate limiting
                time.sleep(self.rate_limit_delay)
                return data
            else:
                logger.error(f"❌ Failed: {endpoint} - Status: {response.status_code}")
                logger.error(f"Response: {response.text[:300]}...")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Exception for {endpoint}: {e}")
            return {}
    
    def explore_advanced_statistics_endpoints(self):
        """Explore endpoints that might contain advanced statistics."""
        logger.info("🔍 Exploring Advanced Statistics Endpoints")
        
        results = {}
        
        # Test different statistics endpoints
        endpoints_to_test = [
            ("statistics", {}),
            ("statistics/types", {}),
            ("statistics/periods", {}),
            ("fixtures/statistics", {}),
            ("players/statistics", {}),
            ("teams/statistics", {}),
            (f"teams/{self.man_city_id}/statistics", {}),
            (f"seasons/{self.season_2023_24}/statistics", {}),
        ]
        
        for endpoint, params in endpoints_to_test:
            data = self.make_request(endpoint, params)
            if data and 'data' in data:
                results[endpoint] = {
                    'working': True,
                    'sample_data': data['data'][:3] if isinstance(data['data'], list) else data['data'],
                    'description': f'Statistics from {endpoint}'
                }
            else:
                results[endpoint] = {
                    'working': False,
                    'description': f'No data from {endpoint}'
                }
        
        return results
    
    def explore_fixture_statistics(self):
        """Explore fixture-level statistics that might include xG."""
        logger.info("⚽ Exploring Fixture Statistics")
        
        results = {}
        
        # Get some fixtures first
        fixtures_data = self.make_request("fixtures", {"per_page": 5})
        
        if fixtures_data and 'data' in fixtures_data:
            for i, fixture in enumerate(fixtures_data['data'][:3]):
                fixture_id = fixture.get('id')
                
                # Test different includes for fixture statistics
                includes_to_test = [
                    "statistics",
                    "statistics.type",
                    "lineups.statistics",
                    "lineups.statistics.type",
                    "events.statistics",
                    "participants.statistics",
                    "xg",
                    "expected_goals"
                ]
                
                for include in includes_to_test:
                    endpoint = f"fixtures/{fixture_id}"
                    params = {"include": include}
                    
                    data = self.make_request(endpoint, params)
                    if data and 'data' in data:
                        key = f"fixture_{fixture_id}_{include}"
                        results[key] = {
                            'working': True,
                            'include': include,
                            'sample_data': data['data'],
                            'description': f'Fixture {fixture_id} with {include}'
                        }
        
        return results
    
    def explore_player_statistics_detailed(self):
        """Explore detailed player statistics."""
        logger.info("👤 Exploring Detailed Player Statistics")
        
        results = {}
        
        # Get a player ID
        squad_data = self.make_request(f"squads/seasons/{self.season_2023_24}/teams/{self.man_city_id}")
        
        if squad_data and 'data' in squad_data and squad_data['data']:
            player_id = squad_data['data'][0].get('player_id')
            
            if player_id:
                # Test different player statistics endpoints
                endpoints_to_test = [
                    (f"players/{player_id}/statistics", {}),
                    (f"players/{player_id}/statistics/seasons/{self.season_2023_24}", {}),
                    (f"players/{player_id}/statistics/detailed", {}),
                    (f"players/{player_id}", {"include": "statistics"}),
                    (f"players/{player_id}", {"include": "statistics.type"}),
                    (f"players/{player_id}", {"include": "statistics.details"}),
                ]
                
                for endpoint, params in endpoints_to_test:
                    data = self.make_request(endpoint, params)
                    if data and 'data' in data:
                        results[endpoint] = {
                            'working': True,
                            'sample_data': data['data'],
                            'description': f'Player statistics from {endpoint}'
                        }
        
        return results
    
    def explore_statistics_types(self):
        """Explore what types of statistics are available."""
        logger.info("📊 Exploring Statistics Types")
        
        # Try to get statistics types/categories
        endpoints_to_test = [
            "statistics/types",
            "statistics/categories", 
            "statistics/periods",
            "types",
            "types/statistics"
        ]
        
        results = {}
        
        for endpoint in endpoints_to_test:
            data = self.make_request(endpoint)
            if data and 'data' in data:
                results[endpoint] = {
                    'working': True,
                    'data': data['data'],
                    'description': f'Statistics types from {endpoint}'
                }
        
        return results
    
    def search_for_xg_data(self):
        """Search specifically for expected goals (xG) data."""
        logger.info("🎯 Searching for Expected Goals (xG) Data")
        
        results = {}
        
        # Get a recent fixture
        fixtures_data = self.make_request("fixtures", {"per_page": 10})
        
        if fixtures_data and 'data' in fixtures_data:
            for fixture in fixtures_data['data'][:5]:
                fixture_id = fixture.get('id')
                match_name = fixture.get('name', f'Match {fixture_id}')
                
                logger.info(f"🔍 Checking match: {match_name}")
                
                # Try various ways to get xG data
                xg_attempts = [
                    {"include": "statistics,lineups.statistics"},
                    {"include": "events,events.statistics"},
                    {"include": "participants.statistics"},
                    {"include": "xg,expected_goals"},
                    {"include": "statistics.type"},
                    {"include": "lineups.statistics.type"},
                ]
                
                for attempt in xg_attempts:
                    data = self.make_request(f"fixtures/{fixture_id}", attempt)
                    
                    if data and 'data' in data:
                        # Look for xG-related data in the response
                        data_str = json.dumps(data, default=str).lower()
                        
                        xg_indicators = [
                            'expected_goals', 'xg', 'expected', 'goal_expectancy',
                            'xgchain', 'xgbuildup', 'xa', 'expected_assists'
                        ]
                        
                        found_indicators = [ind for ind in xg_indicators if ind in data_str]
                        
                        if found_indicators:
                            results[f"fixture_{fixture_id}_xg_found"] = {
                                'match_name': match_name,
                                'include_params': attempt,
                                'found_indicators': found_indicators,
                                'sample_data': data['data'],
                                'description': f'Found xG indicators: {found_indicators}'
                            }
                            logger.info(f"✅ Found xG data in {match_name}: {found_indicators}")
                            break
        
        return results
    
    def run_comprehensive_exploration(self):
        """Run comprehensive exploration of advanced statistics."""
        logger.info("🚀 Starting Comprehensive Advanced Statistics Exploration")
        
        exploration_results = {
            'timestamp': datetime.now().isoformat(),
            'exploration_type': 'advanced_statistics',
            'results': {}
        }
        
        # 1. Explore general statistics endpoints
        logger.info("\n" + "="*50)
        logger.info("1. EXPLORING GENERAL STATISTICS ENDPOINTS")
        logger.info("="*50)
        exploration_results['results']['general_statistics'] = self.explore_advanced_statistics_endpoints()
        
        # 2. Explore fixture statistics
        logger.info("\n" + "="*50)
        logger.info("2. EXPLORING FIXTURE STATISTICS")
        logger.info("="*50)
        exploration_results['results']['fixture_statistics'] = self.explore_fixture_statistics()
        
        # 3. Explore player statistics
        logger.info("\n" + "="*50)
        logger.info("3. EXPLORING PLAYER STATISTICS")
        logger.info("="*50)
        exploration_results['results']['player_statistics'] = self.explore_player_statistics_detailed()
        
        # 4. Explore statistics types
        logger.info("\n" + "="*50)
        logger.info("4. EXPLORING STATISTICS TYPES")
        logger.info("="*50)
        exploration_results['results']['statistics_types'] = self.explore_statistics_types()
        
        # 5. Search for xG data specifically
        logger.info("\n" + "="*50)
        logger.info("5. SEARCHING FOR EXPECTED GOALS (xG) DATA")
        logger.info("="*50)
        exploration_results['results']['xg_search'] = self.search_for_xg_data()
        
        return exploration_results
    
    def save_results(self, results: Dict):
        """Save exploration results."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/advanced_stats_exploration_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"✅ Advanced statistics exploration saved to: {filename}")
        return filename

def main():
    """Main execution function."""
    import os
    os.makedirs('data', exist_ok=True)
    
    explorer = EnhancedStatsExplorer()
    
    # Run comprehensive exploration
    results = explorer.run_comprehensive_exploration()
    
    # Save results
    filename = explorer.save_results(results)
    
    # Print summary
    print("\n" + "="*80)
    print("🔍 ADVANCED STATISTICS EXPLORATION SUMMARY")
    print("="*80)
    
    for category, category_results in results.get('results', {}).items():
        print(f"\n📂 {category.upper().replace('_', ' ')}:")
        
        working_endpoints = 0
        total_endpoints = 0
        
        for endpoint_name, endpoint_data in category_results.items():
            total_endpoints += 1
            if endpoint_data.get('working', False):
                working_endpoints += 1
                print(f"  ✅ {endpoint_name}: {endpoint_data.get('description', 'Working')}")
            else:
                print(f"  ❌ {endpoint_name}: {endpoint_data.get('description', 'Not working')}")
        
        print(f"  📊 Success Rate: {working_endpoints}/{total_endpoints}")
    
    # Check for xG findings
    xg_results = results.get('results', {}).get('xg_search', {})
    if xg_results:
        print(f"\n🎯 EXPECTED GOALS (xG) FINDINGS:")
        for key, data in xg_results.items():
            if 'found_indicators' in data:
                print(f"  ✅ {data['match_name']}: Found {data['found_indicators']}")
    else:
        print(f"\n⚠️  No Expected Goals (xG) data found in current API responses")
    
    print(f"\n📄 Full results saved to: {filename}")
    print("="*80)

if __name__ == "__main__":
    main()
