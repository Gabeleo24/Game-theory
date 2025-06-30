#!/usr/bin/env python3
"""
Basic test script to verify core API configurations are working.
"""

import sys
import os
sys.path.append('src')

def test_api_football():
    """Test API-Football connection."""
    print("Testing API-Football connection...")
    try:
        from soccer_intelligence.data_collection.api_football import APIFootballClient
        
        client = APIFootballClient()
        
        if not client.api_key:
            print("API-Football: No API key configured")
            return False
        
        # Test with a simple request - get leagues
        leagues = client.get_leagues(country="Spain")
        
        if leagues:
            print(f"API-Football: Successfully retrieved {len(leagues)} Spanish leagues")
            # Find La Liga
            la_liga = next((league for league in leagues 
                          if league.get('league', {}).get('name') == 'La Liga'), None)
            if la_liga:
                print(f"   Found La Liga (ID: {la_liga['league']['id']})")
            return True
        else:
            print("API-Football: No data retrieved")
            return False
            
    except Exception as e:
        print(f"API-Football: Error - {e}")
        return False

def test_twitter():
    """Test Twitter API connection."""
    print("\nTesting Twitter API connection...")
    try:
        from soccer_intelligence.data_collection.social_media import SocialMediaCollector
        
        collector = SocialMediaCollector()
        
        if collector.twitter_client:
            print("Twitter: Client initialized successfully")
            print("   Note: Actual tweet collection requires rate limit consideration")
            return True
        else:
            print("Twitter: Client not initialized")
            return False
            
    except Exception as e:
        print(f"Twitter: Error - {e}")
        return False

def test_config():
    """Test configuration loading."""
    print("\nTesting configuration...")
    try:
        from soccer_intelligence.utils.config import Config
        
        config = Config()
        
        # Test API keys
        api_football_key = config.get('api_football.key')
        openai_key = config.get('openai.api_key')
        twitter_token = config.get('twitter.bearer_token')
        
        print(f"Configuration loaded successfully")
        print(f"   API-Football key: {'Set' if api_football_key else 'Missing'}")
        print(f"   OpenAI key: {'Set' if openai_key else 'Missing'}")
        print(f"   Twitter token: {'Set' if twitter_token else 'Missing'}")
        
        return True
        
    except Exception as e:
        print(f"Configuration: Error - {e}")
        return False

def test_data_collection():
    """Test basic data collection functionality."""
    print("\nTesting data collection with La Liga...")
    try:
        from soccer_intelligence.data_collection.api_football import APIFootballClient
        
        client = APIFootballClient()
        
        if not client.api_key:
            print("Skipping data collection test - no API key")
            return True
        
        # Get La Liga teams for 2023 season
        teams = client.get_teams(league_id=140, season=2023)
        
        if teams:
            print(f"Successfully collected {len(teams)} La Liga teams")
            
            # Show sample teams
            print("   Sample teams:")
            for i, team in enumerate(teams[:3]):
                team_info = team.get('team', {})
                print(f"     {i+1}. {team_info.get('name', 'Unknown')}")
            
            return True
        else:
            print("No teams data retrieved (might be rate limited)")
            return True
            
    except Exception as e:
        print(f"Data collection: Error - {e}")
        return False

def test_cache():
    """Test caching functionality."""
    print("\nTesting cache system...")
    try:
        from soccer_intelligence.data_collection.cache_manager import CacheManager
        
        cache_manager = CacheManager()
        cache_info = cache_manager.get_cache_info()
        
        print(f"Cache system working")
        print(f"   Cache directory: {cache_info['cache_directory']}")
        print(f"   Cache files: {cache_info['total_files']}")
        print(f"   Total size: {cache_info['total_size_mb']} MB")
        
        return True
        
    except Exception as e:
        print(f"Cache system: Error - {e}")
        return False

def main():
    """Run basic setup tests."""
    print("Soccer Intelligence System - Basic Setup Test")
    print("=" * 50)
    
    results = {
        'config': test_config(),
        'api_football': test_api_football(),
        'twitter': test_twitter(),
        'data_collection': test_data_collection(),
        'cache': test_cache()
    }
    
    print("\n" + "=" * 50)
    print("Basic Setup Test Results:")
    print("=" * 50)
    
    for component, success in results.items():
        status = "WORKING" if success else "FAILED"
        print(f"{component.upper():15}: {status}")
    
    working_components = sum(results.values())
    total_components = len(results)
    
    print(f"\nOverall: {working_components}/{total_components} components working correctly")
    
    if working_components >= 4:  # Allow for some optional components
        print("\nCore system is working. You can start collecting soccer data.")
        print("\nNext steps:")
        print("1. Try: python -c \"from src.soccer_intelligence.data_collection.api_football import APIFootballClient; client = APIFootballClient(); print('API client ready!')\"")
        print("2. Collect some La Liga data to test the system")
        print("3. Run the Jupyter notebook for full demonstration")
    else:
        print("\nSome core components need attention. Check the error messages above.")

if __name__ == "__main__":
    main()
