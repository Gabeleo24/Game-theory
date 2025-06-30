#!/usr/bin/env python3
"""
Test script to verify all API configurations are working correctly.
"""

import sys
import os
sys.path.append('src')

from soccer_intelligence.data_collection import APIFootballClient, SocialMediaCollector
from soccer_intelligence.utils import setup_logger

def test_api_football():
    """Test API-Football connection."""
    print("Testing API-Football connection...")
    try:
        client = APIFootballClient()
        
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
        collector = SocialMediaCollector()
        
        if collector.twitter_client:
            # Test with a simple search
            tweets = collector.search_tweets("Real Madrid", max_results=5, days_back=1)
            
            if tweets:
                print(f"Twitter: Successfully retrieved {len(tweets)} tweets")
                print(f"   Sample tweet: {tweets[0].get('text', 'N/A')[:50]}...")
                return True
            else:
                print("Twitter: Connected but no tweets retrieved (might be rate limited)")
                return True
        else:
            print("Twitter: Client not initialized")
            return False
            
    except Exception as e:
        print(f"Twitter: Error - {e}")
        return False

def test_openai():
    """Test OpenAI API connection."""
    print("\nTesting OpenAI API connection...")
    try:
        import openai
        from soccer_intelligence.utils import Config
        
        config = Config()
        api_key = config.get('openai.api_key')
        
        if api_key:
            openai.api_key = api_key
            
            # Test with a simple completion
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello, this is a test."}],
                max_tokens=10
            )
            
            if response:
                print("OpenAI: API connection successful")
                return True
        else:
            print("OpenAI: API key not found")
            return False
            
    except Exception as e:
        print(f"OpenAI: Error - {e}")
        return False

def main():
    """Run all API tests."""
    print("Soccer Intelligence System - API Configuration Test")
    print("=" * 55)
    
    # Set up logging
    logger = setup_logger('api_test')
    
    results = {
        'api_football': test_api_football(),
        'twitter': test_twitter(),
        'openai': test_openai()
    }
    
    print("\n" + "=" * 55)
    print("API Test Results Summary:")
    print("=" * 55)
    
    for api, success in results.items():
        status = "WORKING" if success else "FAILED"
        print(f"{api.upper():12}: {status}")
    
    working_apis = sum(results.values())
    total_apis = len(results)
    
    print(f"\nOverall: {working_apis}/{total_apis} APIs working correctly")
    
    if working_apis == total_apis:
        print("\nAll APIs configured correctly. Your Soccer Intelligence System is ready.")
        print("\nNext steps:")
        print("1. Run: jupyter notebook notebooks/01_data_collection_demo.ipynb")
        print("2. Start collecting La Liga and Champions League data")
        print("3. Begin your ADS599 Capstone analysis")
    else:
        print("\nSome APIs need attention. Check the error messages above.")
        print("The system will still work with the functioning APIs.")

if __name__ == "__main__":
    main()
