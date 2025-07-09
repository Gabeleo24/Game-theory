#!/usr/bin/env python3
"""
Test new SportMonks API key and pull Real Madrid data
"""

import requests
import yaml
import json
import time

def test_new_sportmonks_key():
    """Test the new SportMonks API key with Real Madrid data."""
    
    # Load new API key
    try:
        with open('config/api_keys.yaml', 'r') as f:
            config = yaml.safe_load(f)
        api_token = config.get('sportmonks', {}).get('api_key')
        print(f"✅ New API Key loaded: {api_token[:10]}...")
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return
    
    base_url = "https://api.sportmonks.com/v3/football"
    
    print(f"\n{'='*80}")
    print("TESTING NEW SPORTMONKS API KEY")
    print(f"{'='*80}")
    
    # Test 1: Basic API connectivity
    print(f"\n🔄 Test 1: Basic API connectivity")
    try:
        url = f"{base_url}/leagues"
        params = {'api_token': api_token, 'per_page': 3}
        response = requests.get(url, params=params, timeout=10)
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ SUCCESS! Found {len(data.get('data', []))} leagues")
            print(f"   Rate limit remaining: {data.get('rate_limit', {}).get('remaining', 'Unknown')}")
        else:
            print(f"   ❌ Failed: {response.text[:200]}")
            return
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return
    
    # Test 2: Search for Real Madrid
    print(f"\n🔄 Test 2: Search for Real Madrid")
    try:
        url = f"{base_url}/teams"
        params = {
            'api_token': api_token, 
            'per_page': 20,
            'filters': 'teamSearch:Real Madrid'
        }
        response = requests.get(url, params=params, timeout=10)
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            teams = data.get('data', [])
            print(f"   Found {len(teams)} teams")
            
            real_madrid_id = None
            for team in teams:
                team_name = team.get('name', '')
                team_id = team.get('id')
                print(f"   - {team_name} (ID: {team_id})")
                if 'Real Madrid' in team_name:
                    real_madrid_id = team_id
                    print(f"   ✅ Found Real Madrid! ID: {real_madrid_id}")
            
            if not real_madrid_id:
                print(f"   ⚠️ Real Madrid not found in search results")
                # Try known ID
                real_madrid_id = 496  # Common Real Madrid ID
                print(f"   Using known Real Madrid ID: {real_madrid_id}")
        else:
            print(f"   ❌ Search failed: {response.text[:200]}")
            real_madrid_id = 496  # Fallback
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        real_madrid_id = 496  # Fallback
    
    # Test 3: Get Real Madrid team details
    print(f"\n🔄 Test 3: Get Real Madrid team details (ID: {real_madrid_id})")
    try:
        url = f"{base_url}/teams/{real_madrid_id}"
        params = {
            'api_token': api_token,
            'include': 'country,venue,coach'
        }
        response = requests.get(url, params=params, timeout=10)
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            team_data = data.get('data', {})
            print(f"   ✅ Team Name: {team_data.get('name', 'Unknown')}")
            print(f"   Founded: {team_data.get('founded', 'Unknown')}")
            print(f"   Country: {team_data.get('country', {}).get('name', 'Unknown')}")
            print(f"   Venue: {team_data.get('venue', {}).get('name', 'Unknown')}")
            
            # Save team data
            with open('sportmonks_real_madrid_team.json', 'w') as f:
                json.dump(data, f, indent=2)
            print(f"   💾 Team data saved to sportmonks_real_madrid_team.json")
        else:
            print(f"   ❌ Failed: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 4: Get current season
    print(f"\n🔄 Test 4: Get current/recent seasons")
    try:
        url = f"{base_url}/seasons"
        params = {
            'api_token': api_token,
            'per_page': 10
        }
        response = requests.get(url, params=params, timeout=10)
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            seasons = data.get('data', [])
            print(f"   Found {len(seasons)} seasons")
            
            season_2023_id = None
            for season in seasons[:10]:  # Check first 10
                season_name = season.get('name', '')
                season_id = season.get('id')
                print(f"   - {season_name} (ID: {season_id})")
                if '2023' in season_name or '2024' in season_name:
                    season_2023_id = season_id
                    print(f"   ✅ Found 2023-2024 season! ID: {season_2023_id}")
                    break
        else:
            print(f"   ❌ Failed: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 5: Try to get Real Madrid players (if we found the team)
    if real_madrid_id:
        print(f"\n🔄 Test 5: Try to get Real Madrid squad")
        try:
            # Try different endpoints for players
            player_endpoints = [
                f"{base_url}/teams/{real_madrid_id}/squad",
                f"{base_url}/squads/teams/{real_madrid_id}",
                f"{base_url}/players?filters=teamId:{real_madrid_id}"
            ]
            
            for endpoint in player_endpoints:
                print(f"   Trying: {endpoint}")
                params = {'api_token': api_token, 'per_page': 10}
                response = requests.get(endpoint, params=params, timeout=10)
                
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    players = data.get('data', [])
                    print(f"   ✅ SUCCESS! Found {len(players)} players")
                    
                    # Show first few players
                    for i, player in enumerate(players[:3]):
                        if isinstance(player, dict):
                            player_name = player.get('name', player.get('display_name', 'Unknown'))
                            print(f"   Player {i+1}: {player_name}")
                    
                    # Save player data
                    with open('sportmonks_real_madrid_players.json', 'w') as f:
                        json.dump(data, f, indent=2)
                    print(f"   💾 Player data saved to sportmonks_real_madrid_players.json")
                    break
                else:
                    print(f"   ❌ Failed: {response.text[:100]}")
                
                time.sleep(0.5)  # Rate limiting between attempts
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print(f"\n{'='*80}")
    print("TEST SUMMARY:")
    print("✅ If you see successful API calls above, the new key is working!")
    print("✅ Check the saved JSON files for detailed data")
    print("✅ We can now integrate this into the Elche display")
    print(f"{'='*80}")

if __name__ == "__main__":
    test_new_sportmonks_key()
