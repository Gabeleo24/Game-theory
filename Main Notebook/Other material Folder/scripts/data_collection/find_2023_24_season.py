#!/usr/bin/env python3
"""
Find 2023-2024 Season Data
Comprehensive search for the correct 2023-2024 season ID and Manchester City matches
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

class Season2023_24Finder:
    """Find the correct 2023-2024 season and Manchester City matches."""
    
    def __init__(self):
        """Initialize with API configuration."""
        self.load_config()
        self.session = requests.Session()
        self.base_url = "https://api.sportmonks.com/v3/football"
        
        # Manchester City team ID
        self.man_city_id = 9
        
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
                logger.error(f"Response: {response.text[:300]}...")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Exception for {endpoint}: {e}")
            return {}
    
    def search_all_seasons_thoroughly(self):
        """Search through ALL seasons to find 2023-2024."""
        logger.info("🔍 Searching ALL seasons for 2023-2024")
        
        all_seasons = []
        page = 1
        
        while True:
            seasons_data = self.make_request("seasons", {"per_page": 100, "page": page})
            
            if seasons_data and 'data' in seasons_data and seasons_data['data']:
                page_seasons = seasons_data['data']
                all_seasons.extend(page_seasons)
                logger.info(f"📄 Page {page}: Found {len(page_seasons)} seasons")
                
                # Check for 2023-2024 patterns in this page
                for season in page_seasons:
                    season_name = season.get('name', '').lower()
                    starting_at = season.get('starting_at', '')
                    ending_at = season.get('ending_at', '')
                    
                    # Look for 2023-2024 patterns
                    if ('2023' in season_name and '2024' in season_name) or \
                       ('2023' in starting_at) or \
                       ('2024' in ending_at and '2023' in starting_at):
                        logger.info(f"🎯 FOUND 2023-24 CANDIDATE: {season}")
                
                page += 1
                
                # Safety limit
                if page > 20:
                    break
            else:
                break
        
        logger.info(f"✅ Total seasons found: {len(all_seasons)}")
        
        # Filter for potential 2023-24 seasons
        candidates_2023_24 = []
        for season in all_seasons:
            season_name = season.get('name', '').lower()
            starting_at = season.get('starting_at', '')
            ending_at = season.get('ending_at', '')
            
            # Multiple patterns to catch 2023-24
            if any([
                '2023' in season_name and '2024' in season_name,
                '2023/24' in season_name,
                '2023-24' in season_name,
                '2023' in starting_at and ('2024' in ending_at or '2024' in starting_at),
                starting_at.startswith('2023'),
                ending_at.startswith('2024')
            ]):
                candidates_2023_24.append(season)
        
        logger.info(f"🎯 Found {len(candidates_2023_24)} potential 2023-24 seasons")
        
        return all_seasons, candidates_2023_24
    
    def search_recent_fixtures(self):
        """Search for recent fixtures (2023-2024 timeframe)."""
        logger.info("🔍 Searching for recent fixtures (2023-2024)")
        
        recent_fixtures = []
        manchester_city_recent = []
        
        # Search through many pages to find recent data
        for page in range(1, 50):  # Increased search range
            fixtures_data = self.make_request("fixtures", {"per_page": 100, "page": page})
            
            if fixtures_data and 'data' in fixtures_data:
                for fixture in fixtures_data['data']:
                    starting_at = fixture.get('starting_at', '')
                    match_name = fixture.get('name', '').lower()
                    
                    # Look for 2023 or 2024 dates
                    if '2023' in starting_at or '2024' in starting_at:
                        recent_fixtures.append(fixture)
                        
                        # Check if it's Manchester City
                        if 'manchester city' in match_name or 'man city' in match_name:
                            manchester_city_recent.append(fixture)
                            logger.info(f"🎯 FOUND RECENT MAN CITY MATCH: {fixture.get('name')} ({starting_at})")
            
            # Log progress
            if page % 10 == 0:
                logger.info(f"📄 Searched {page} pages, found {len(recent_fixtures)} recent fixtures")
            
            # If we found some recent data, continue searching
            if len(recent_fixtures) > 100:
                logger.info(f"✅ Found sufficient recent data, stopping search")
                break
        
        logger.info(f"✅ Found {len(recent_fixtures)} recent fixtures (2023-2024)")
        logger.info(f"✅ Found {len(manchester_city_recent)} recent Manchester City matches")
        
        return recent_fixtures, manchester_city_recent
    
    def test_specific_season_ids(self):
        """Test specific season IDs that might be 2023-24."""
        logger.info("🔍 Testing specific season IDs for 2023-24")
        
        # Common season ID patterns for 2023-24
        potential_season_ids = [
            21646,  # Original guess
            23087,  # From config file
            24644,  # From config file (2024-25)
            22000, 22001, 22002, 22003, 22004, 22005,  # Range around potential IDs
            23000, 23001, 23002, 23003, 23004, 23005,
            23080, 23081, 23082, 23083, 23084, 23085, 23086, 23087, 23088, 23089, 23090
        ]
        
        working_seasons = []
        
        for season_id in potential_season_ids:
            season_data = self.make_request(f"seasons/{season_id}")
            
            if season_data and 'data' in season_data:
                season_info = season_data['data']
                season_name = season_info.get('name', '')
                starting_at = season_info.get('starting_at', '')
                
                logger.info(f"✅ Season {season_id}: {season_name} ({starting_at})")
                working_seasons.append(season_info)
                
                # Check if this looks like 2023-24
                if ('2023' in season_name and '2024' in season_name) or \
                   ('2023' in starting_at):
                    logger.info(f"🎯 POTENTIAL 2023-24 SEASON FOUND: {season_id}")
        
        return working_seasons
    
    def comprehensive_search(self):
        """Run comprehensive search for 2023-2024 season."""
        logger.info("🚀 Starting comprehensive search for 2023-2024 season")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'search_results': {}
        }
        
        # 1. Search all seasons
        logger.info("\n" + "="*50)
        logger.info("1. SEARCHING ALL SEASONS")
        logger.info("="*50)
        all_seasons, candidates_2023_24 = self.search_all_seasons_thoroughly()
        results['search_results']['all_seasons'] = {
            'total_count': len(all_seasons),
            'candidates_2023_24': candidates_2023_24,
            'all_seasons': all_seasons
        }
        
        # 2. Search recent fixtures
        logger.info("\n" + "="*50)
        logger.info("2. SEARCHING RECENT FIXTURES")
        logger.info("="*50)
        recent_fixtures, man_city_recent = self.search_recent_fixtures()
        results['search_results']['recent_fixtures'] = {
            'total_recent': len(recent_fixtures),
            'man_city_recent': len(man_city_recent),
            'man_city_matches': man_city_recent,
            'sample_recent': recent_fixtures[:10]
        }
        
        # 3. Test specific season IDs
        logger.info("\n" + "="*50)
        logger.info("3. TESTING SPECIFIC SEASON IDS")
        logger.info("="*50)
        working_seasons = self.test_specific_season_ids()
        results['search_results']['tested_seasons'] = working_seasons
        
        return results
    
    def save_results(self, results):
        """Save comprehensive search results."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/comprehensive_2023_24_search_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"✅ Comprehensive search results saved to: {filename}")
        return filename

def main():
    """Main execution function."""
    import os
    os.makedirs('data', exist_ok=True)
    
    finder = Season2023_24Finder()
    
    # Run comprehensive search
    results = finder.comprehensive_search()
    
    # Save results
    filename = finder.save_results(results)
    
    # Print summary
    print("\n" + "="*80)
    print("🔍 COMPREHENSIVE 2023-2024 SEASON SEARCH RESULTS")
    print("="*80)
    
    search_results = results.get('search_results', {})
    
    # All seasons summary
    all_seasons = search_results.get('all_seasons', {})
    print(f"📊 Total seasons in database: {all_seasons.get('total_count', 0)}")
    
    candidates = all_seasons.get('candidates_2023_24', [])
    print(f"🎯 2023-24 season candidates found: {len(candidates)}")
    
    if candidates:
        print("\n🏆 2023-24 Season Candidates:")
        for candidate in candidates:
            print(f"  • Season {candidate.get('id')}: {candidate.get('name')} ({candidate.get('starting_at')} - {candidate.get('ending_at')})")
    
    # Recent fixtures summary
    recent_fixtures = search_results.get('recent_fixtures', {})
    print(f"\n⚽ Recent fixtures (2023-2024): {recent_fixtures.get('total_recent', 0)}")
    print(f"🏟️ Manchester City recent matches: {recent_fixtures.get('man_city_recent', 0)}")
    
    man_city_matches = recent_fixtures.get('man_city_matches', [])
    if man_city_matches:
        print("\n🎯 Recent Manchester City matches found:")
        for match in man_city_matches[:10]:  # Show first 10
            print(f"  • {match.get('name')} ({match.get('starting_at')}) - Season {match.get('season_id')}")
    
    # Tested seasons summary
    tested_seasons = search_results.get('tested_seasons', [])
    print(f"\n🔍 Working season IDs tested: {len(tested_seasons)}")
    
    if tested_seasons:
        print("\n📋 Working seasons found:")
        for season in tested_seasons:
            season_name = season.get('name', 'Unknown')
            season_id = season.get('id', 'Unknown')
            starting_at = season.get('starting_at', 'Unknown')
            print(f"  • Season {season_id}: {season_name} ({starting_at})")
    
    print(f"\n📄 Full results saved to: {filename}")
    print("="*80)
    
    # Provide next steps
    if candidates or man_city_matches:
        print("\n🎯 NEXT STEPS:")
        if candidates:
            print("✅ Found 2023-24 season candidates - use these season IDs for data collection")
        if man_city_matches:
            print("✅ Found recent Manchester City matches - can collect detailed match data")
        print("🔄 Run detailed match collection with the found season IDs")
    else:
        print("\n⚠️  NO 2023-24 DATA FOUND:")
        print("❌ The SportMonks API might not have 2023-24 season data available")
        print("🔄 Consider checking API subscription level or data availability")

if __name__ == "__main__":
    main()
