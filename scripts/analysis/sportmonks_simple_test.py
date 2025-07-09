#!/usr/bin/env python3
"""
Simple SportMonks API test to understand the correct endpoints
"""

import requests
import yaml
import json

def test_sportmonks_endpoints():
    """Test various SportMonks endpoints to find the right structure."""
    
    # Load API key
    try:
        with open('config/api_keys.yaml', 'r') as f:
            config = yaml.safe_load(f)
        api_token = config.get('sportmonks', {}).get('api_key')
    except:
        print("❌ Could not load API key")
        return
    
    base_url = "https://api.sportmonks.com/v3/football"
    
    # Test endpoints
    endpoints = [
        f"{base_url}/teams/53",  # Real Madrid direct
        f"{base_url}/teams/53/players",  # Real Madrid players
        f"{base_url}/seasons/21644/teams/53",  # Season team
        f"{base_url}/players",  # All players
        f"{base_url}/fixtures",  # Fixtures
    ]
    
    for endpoint in endpoints:
        print(f"\n🔄 Testing: {endpoint}")
        
        try:
            params = {'api_token': api_token, 'per_page': 5}
            response = requests.get(endpoint, params=params, timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success! Keys: {list(data.keys())}")
                
                if 'data' in data:
                    data_content = data['data']
                    if isinstance(data_content, list):
                        print(f"   📊 Records: {len(data_content)}")
                        if data_content:
                            print(f"   🔍 Sample keys: {list(data_content[0].keys())[:5]}")
                    elif isinstance(data_content, dict):
                        print(f"   🔍 Data keys: {list(data_content.keys())[:5]}")
                
                # Save successful response for analysis
                if endpoint.endswith('/53'):  # Real Madrid team
                    with open('sportmonks_real_madrid_sample.json', 'w') as f:
                        json.dump(data, f, indent=2)
                    print(f"   💾 Saved sample to sportmonks_real_madrid_sample.json")
                
            else:
                print(f"   ❌ Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    test_sportmonks_endpoints()
