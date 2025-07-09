#!/usr/bin/env python3
"""
Working SportMonks API Test - Use correct endpoints and structure
"""

import requests
import yaml
import json

def test_working_sportmonks():
    """Test SportMonks API with correct endpoints."""
    
    # Load API key
    try:
        with open('config/api_keys.yaml', 'r') as f:
            config = yaml.safe_load(f)
        api_token = config.get('sportmonks', {}).get('api_key')
        print(f"✅ API Key loaded: {api_token[:10]}...")
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return
    
    print(f"\n{'='*80}")
    print("🔄 WORKING SPORTMONKS API TEST")
    print(f"{'='*80}")
    
    # Test 1: Basic connectivity
    print(f"\n🔄 Test 1: Basic API connectivity")
    try:
        url = "https://api.sportmonks.com/v3/football/leagues"
        params = {'api_token': api_token, 'per_page': 3}
        
        response = requests.get(url, params=params, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            leagues = data.get('data', [])
            print(f"   ✅ SUCCESS! Found {len(leagues)} leagues")
            
            # Show rate limit info
            rate_limit = data.get('rate_limit', {})
            print(f"   🔄 Rate limit remaining: {rate_limit.get('remaining', 'Unknown')}")
            
            # Show subscription info if available
            subscription = data.get('subscription', [])
            if subscription:
                print(f"   📊 Subscription: {subscription}")
        else:
            print(f"   ❌ Failed: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return
    
    # Test 2: Find Real Madrid
    print(f"\n🔄 Test 2: Find Real Madrid")
    try:
        # Try browsing teams
        url = "https://api.sportmonks.com/v3/football/teams"
        params = {'api_token': api_token, 'per_page': 50}
        
        response = requests.get(url, params=params, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            teams = data.get('data', [])
            
            real_madrid_id = None
            for team in teams:
                team_name = team.get('name', '').lower()
                if 'real madrid' in team_name or 'madrid' in team_name:
                    real_madrid_id = team.get('id')
                    print(f"   ✅ Found: {team.get('name')} (ID: {real_madrid_id})")
                    break
            
            if not real_madrid_id:
                # Use known Real Madrid ID
                real_madrid_id = 496
                print(f"   Using known Real Madrid ID: {real_madrid_id}")
        else:
            print(f"   ❌ Failed: {response.text[:200]}")
            real_madrid_id = 496
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        real_madrid_id = 496
    
    # Test 3: Get Real Madrid basic info
    print(f"\n🔄 Test 3: Get Real Madrid team info")
    try:
        url = f"https://api.sportmonks.com/v3/football/teams/{real_madrid_id}"
        params = {'api_token': api_token}
        
        response = requests.get(url, params=params, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            team_data = data.get('data', {})
            
            print(f"   ✅ Team: {team_data.get('name', 'Unknown')}")
            print(f"   🏟️ Founded: {team_data.get('founded', 'Unknown')}")
            print(f"   🌍 Country ID: {team_data.get('country_id', 'Unknown')}")
            print(f"   🏟️ Venue ID: {team_data.get('venue_id', 'Unknown')}")
            
            # Save basic team data
            with open('working_real_madrid_basic.json', 'w') as f:
                json.dump(data, f, indent=2)
            print(f"   💾 Basic team data saved")
            
        else:
            print(f"   ❌ Failed: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 4: Try to get squad/players
    print(f"\n🔄 Test 4: Try squad endpoints")
    try:
        # Try different squad endpoints
        squad_endpoints = [
            f"https://api.sportmonks.com/v3/football/squads/teams/{real_madrid_id}",
            f"https://api.sportmonks.com/v3/football/teams/{real_madrid_id}/squad"
        ]
        
        for endpoint in squad_endpoints:
            print(f"   Trying: {endpoint}")
            params = {'api_token': api_token, 'per_page': 30}
            
            response = requests.get(endpoint, params=params, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                squad_data = data.get('data', [])
                
                print(f"   ✅ SUCCESS! Found {len(squad_data)} squad members")
                
                # Show sample players
                for i, member in enumerate(squad_data[:5]):
                    player_id = member.get('player_id', 'Unknown')
                    jersey = member.get('jersey_number', 'N/A')
                    position = member.get('position_id', 'Unknown')
                    
                    print(f"      Player {i+1}: ID={player_id}, Jersey={jersey}, Position={position}")
                
                # Save squad data
                filename = f'working_squad_{endpoint.split("/")[-1]}.json'
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                print(f"   💾 Squad data saved to {filename}")
                
                break  # Found working endpoint
                
            else:
                print(f"   ❌ Failed: {response.text[:150]}")
                
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 5: Try seasons
    print(f"\n🔄 Test 5: Get seasons")
    try:
        url = "https://api.sportmonks.com/v3/football/seasons"
        params = {'api_token': api_token, 'per_page': 10}
        
        response = requests.get(url, params=params, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            seasons = data.get('data', [])
            
            print(f"   ✅ Found {len(seasons)} seasons")
            
            # Look for recent seasons
            for season in seasons[:5]:
                season_name = season.get('name', 'Unknown')
                season_id = season.get('id', 'Unknown')
                print(f"      {season_name} (ID: {season_id})")
            
            # Save seasons data
            with open('working_seasons.json', 'w') as f:
                json.dump(data, f, indent=2)
            print(f"   💾 Seasons data saved")
            
        else:
            print(f"   ❌ Failed: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    print(f"\n{'='*80}")
    print("WORKING API TEST SUMMARY:")
    print("✅ Check JSON files to see what data is available")
    print("✅ We can work with the endpoints that return 200 status")
    print("✅ Ready to integrate working endpoints into Elche display")
    print(f"{'='*80}")

if __name__ == "__main__":
    test_working_sportmonks()
