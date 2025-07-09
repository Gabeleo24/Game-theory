#!/usr/bin/env python3
"""
Test Premium SportMonks API subscription for comprehensive Real Madrid data
"""

import requests
import yaml
import json
import time

def test_premium_sportmonks():
    """Test premium SportMonks API features and Real Madrid data access."""
    
    # Load premium API key
    try:
        with open('config/api_keys.yaml', 'r') as f:
            config = yaml.safe_load(f)
        api_token = config.get('sportmonks', {}).get('api_key')
        print(f"✅ Premium API Key loaded: {api_token[:10]}...")
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return
    
    base_url = "https://api.sportmonks.com/v3/football"
    
    print(f"\n{'='*100}")
    print("TESTING PREMIUM SPORTMONKS API SUBSCRIPTION")
    print(f"{'='*100}")
    
    # Test 1: Check subscription details
    print(f"\n🔄 Test 1: Check subscription and rate limits")
    try:
        url = f"{base_url}/leagues"
        params = {'api_token': api_token, 'per_page': 1}
        response = requests.get(url, params=params, timeout=10)
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            subscription = data.get('subscription', [{}])[0]
            rate_limit = data.get('rate_limit', {})
            
            print(f"   ✅ SUCCESS!")
            print(f"   📊 Subscription Plans: {[plan.get('plan') for plan in subscription.get('plans', [])]}")
            print(f"   🔄 Rate Limit Remaining: {rate_limit.get('remaining', 'Unknown')}")
            print(f"   ⏰ Resets in: {rate_limit.get('resets_in_seconds', 'Unknown')} seconds")
        else:
            print(f"   ❌ Failed: {response.text[:200]}")
            return
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return
    
    # Test 2: Find Real Madrid with premium search
    print(f"\n🔄 Test 2: Premium team search for Real Madrid")
    try:
        # Try multiple search approaches
        search_methods = [
            (f"{base_url}/teams/search/Real Madrid", "Direct search"),
            (f"{base_url}/teams", "Browse teams with filter")
        ]
        
        real_madrid_id = None
        for url, method in search_methods:
            print(f"   Trying {method}...")
            params = {'api_token': api_token, 'per_page': 20}
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                teams = data.get('data', [])
                
                for team in teams:
                    team_name = team.get('name', '').lower()
                    if 'real madrid' in team_name:
                        real_madrid_id = team.get('id')
                        print(f"   ✅ Found Real Madrid! ID: {real_madrid_id}, Name: {team.get('name')}")
                        break
                
                if real_madrid_id:
                    break
            else:
                print(f"   ⚠️ {method} failed: {response.status_code}")
        
        if not real_madrid_id:
            real_madrid_id = 496  # Known fallback
            print(f"   Using known Real Madrid ID: {real_madrid_id}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        real_madrid_id = 496
    
    # Test 3: Get premium team details with includes
    print(f"\n🔄 Test 3: Premium team details with comprehensive includes")
    try:
        url = f"{base_url}/teams/{real_madrid_id}"
        params = {
            'api_token': api_token,
            'include': 'country,venue,coach,players,statistics'
        }
        
        response = requests.get(url, params=params, timeout=15)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            team_data = data.get('data', {})
            
            print(f"   ✅ Team: {team_data.get('name', 'Unknown')}")
            print(f"   🏟️ Venue: {team_data.get('venue', {}).get('name', 'Unknown')}")
            print(f"   🌍 Country: {team_data.get('country', {}).get('name', 'Unknown')}")
            print(f"   👨‍💼 Coach: {team_data.get('coach', {}).get('name', 'Unknown')}")
            
            players = team_data.get('players', [])
            print(f"   👥 Players found: {len(players)}")
            
            if players:
                print(f"   📋 Sample players:")
                for i, player in enumerate(players[:5]):
                    player_name = player.get('display_name', player.get('name', 'Unknown'))
                    position = player.get('position', {}).get('name', 'Unknown')
                    print(f"      {i+1}. {player_name} ({position})")
            
            # Save comprehensive team data
            with open('premium_real_madrid_full.json', 'w') as f:
                json.dump(data, f, indent=2)
            print(f"   💾 Full team data saved to premium_real_madrid_full.json")
            
        else:
            print(f"   ❌ Failed: {response.text[:300]}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 4: Get current season with premium access
    print(f"\n🔄 Test 4: Premium season data")
    try:
        url = f"{base_url}/seasons"
        params = {
            'api_token': api_token,
            'per_page': 20,
            'include': 'league'
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            seasons = data.get('data', [])
            
            print(f"   ✅ Found {len(seasons)} seasons")
            
            # Look for 2023-2024 La Liga season
            target_season = None
            for season in seasons:
                season_name = season.get('name', '').lower()
                league = season.get('league', {})
                league_name = league.get('name', '').lower()
                
                if ('2023' in season_name or '2024' in season_name) and ('la liga' in league_name or 'primera' in league_name):
                    target_season = season
                    print(f"   🎯 Found target season: {season.get('name')} - {league.get('name')} (ID: {season.get('id')})")
                    break
            
            if not target_season:
                print(f"   ⚠️ 2023-2024 La Liga season not found in first {len(seasons)} results")
                
        else:
            print(f"   ❌ Failed: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 5: Try premium player statistics endpoints
    if real_madrid_id:
        print(f"\n🔄 Test 5: Premium player statistics")
        try:
            # Try different player endpoints
            player_endpoints = [
                (f"{base_url}/teams/{real_madrid_id}/players", "Team players"),
                (f"{base_url}/squads/teams/{real_madrid_id}", "Team squad"),
                (f"{base_url}/players", "All players with team filter")
            ]
            
            for endpoint_url, description in player_endpoints:
                print(f"   Testing {description}...")
                
                params = {
                    'api_token': api_token,
                    'per_page': 10,
                    'include': 'position,nationality,statistics'
                }
                
                if 'players' in endpoint_url and endpoint_url.endswith('players'):
                    params['filters'] = f'teamId:{real_madrid_id}'
                
                response = requests.get(endpoint_url, params=params, timeout=15)
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    players = data.get('data', [])
                    
                    print(f"   ✅ SUCCESS! Found {len(players)} players")
                    
                    # Show detailed player info
                    for i, player in enumerate(players[:3]):
                        if isinstance(player, dict):
                            name = player.get('display_name', player.get('name', 'Unknown'))
                            nationality = player.get('nationality', {}).get('name', 'Unknown')
                            position = player.get('position', {}).get('name', 'Unknown')
                            birth_date = player.get('date_of_birth', 'Unknown')
                            
                            print(f"      {i+1}. {name} ({nationality}, {position}, Born: {birth_date})")
                            
                            # Check for statistics
                            stats = player.get('statistics', [])
                            if stats:
                                print(f"         📊 Has {len(stats)} statistical records")
                    
                    # Save player data
                    filename = f'premium_players_{description.replace(" ", "_").lower()}.json'
                    with open(filename, 'w') as f:
                        json.dump(data, f, indent=2)
                    print(f"   💾 Player data saved to {filename}")
                    
                    break  # Found working endpoint
                    
                else:
                    print(f"   ❌ Failed: {response.text[:150]}")
                
                time.sleep(0.5)  # Rate limiting
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print(f"\n{'='*100}")
    print("PREMIUM SUBSCRIPTION TEST SUMMARY:")
    print("✅ Check saved JSON files for detailed premium data")
    print("✅ If player statistics were found, we can enhance the Elche display")
    print("✅ Premium subscription should provide more comprehensive data")
    print(f"{'='*100}")

if __name__ == "__main__":
    test_premium_sportmonks()
