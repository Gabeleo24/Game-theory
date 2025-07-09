#!/usr/bin/env python3
"""
Test SportMonks API connectivity and endpoints
"""

import requests
import yaml
import json

def test_sportmonks_api():
    """Test SportMonks API with different endpoints."""
    
    # Load API key
    try:
        with open('config/api_keys.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        api_key = config.get('sportmonks', {}).get('api_key')
        if not api_key:
            print("❌ No SportMonks API key found")
            return
        
        print(f"✅ API Key loaded: {api_key[:10]}...")
        
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return
    
    # Test different API endpoints and authentication methods
    test_endpoints = [
        {
            'name': 'V3 Football Leagues',
            'url': 'https://api.sportmonks.com/v3/football/leagues',
            'headers': {'Authorization': f'Bearer {api_key}'},
            'params': {'per_page': 5}
        },
        {
            'name': 'V3 Football Teams',
            'url': 'https://api.sportmonks.com/v3/football/teams',
            'headers': {'Authorization': f'Bearer {api_key}'},
            'params': {'per_page': 5}
        },
        {
            'name': 'V3 with API Token param',
            'url': 'https://api.sportmonks.com/v3/football/leagues',
            'headers': {},
            'params': {'api_token': api_key, 'per_page': 5}
        },
        {
            'name': 'V2 Legacy endpoint',
            'url': 'https://soccer.sportmonks.com/api/v2.0/leagues',
            'headers': {},
            'params': {'api_token': api_key}
        }
    ]
    
    for test in test_endpoints:
        print(f"\n🔄 Testing: {test['name']}")
        print(f"   URL: {test['url']}")
        
        try:
            response = requests.get(
                test['url'], 
                headers=test['headers'], 
                params=test['params'],
                timeout=10
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success! Data keys: {list(data.keys())}")
                if 'data' in data:
                    print(f"   📊 Records returned: {len(data['data'])}")
                break  # Found working endpoint
                
            elif response.status_code == 401:
                print(f"   ❌ Authentication failed")
            elif response.status_code == 400:
                print(f"   ❌ Bad request")
            elif response.status_code == 403:
                print(f"   ❌ Forbidden - check API permissions")
            else:
                print(f"   ❌ Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print(f"\n{'='*60}")
    print("RECOMMENDATION:")
    print("If all tests failed, the SportMonks API key might be:")
    print("1. Invalid or expired")
    print("2. For a different API version")
    print("3. Requires different authentication")
    print("4. Has usage limits exceeded")
    print("\nFor now, we'll use enhanced calculations with existing data.")

if __name__ == "__main__":
    test_sportmonks_api()
