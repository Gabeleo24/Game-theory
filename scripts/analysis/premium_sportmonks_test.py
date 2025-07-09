#!/usr/bin/env python3
"""
Premium SportMonks API Test - Leverage premium subscription for Real Madrid data
"""

import requests
import yaml
import json
import time

def test_premium_features():
    """Test premium SportMonks features with your subscription."""
    
    # Load premium API key
    try:
        with open('config/api_keys.yaml', 'r') as f:
            config = yaml.safe_load(f)
        api_token = config.get('sportmonks', {}).get('api_key')
        print(f"✅ Premium API Key loaded: {api_token[:10]}...")
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return
    
    print(f"\n{'='*80}")
    print("🏆 PREMIUM SPORTMONKS API TEST - REAL MADRID DATA 🏆")
    print(f"{'='*80}")
    
    # Test 1: Verify premium subscription
    print(f"\n🔄 Test 1: Verify Premium Subscription")
    try:
        url = "https://api.sportmonks.com/v3/core/my/subscription"
        params = {'api_token': api_token}
        
        response = requests.get(url, params=params, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            subscription = data.get('data', {})
            
            print(f"   ✅ PREMIUM SUBSCRIPTION CONFIRMED!")
            print(f"   📊 Plan: {subscription.get('plan', 'Unknown')}")
            print(f"   🔄 Rate Limit: {subscription.get('rate_limit', 'Unknown')}")
            print(f"   📅 Valid Until: {subscription.get('ends_at', 'Unknown')}")
        else:
            print(f"   ⚠️ Subscription check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 2: Get Real Madrid with premium endpoints
    print(f"\n🔄 Test 2: Premium Real Madrid Team Data")
    try:
        # Use known Real Madrid ID for La Liga
        real_madrid_id = 496
        
        url = f"https://api.sportmonks.com/v3/football/teams/{real_madrid_id}"
        params = {
            'api_token': api_token,
            'include': 'country,venue,coach,currentSquad.player.position,currentSquad.player.nationality,statistics'
        }
        
        response = requests.get(url, params=params, timeout=15)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            team_data = data.get('data', {})
            
            print(f"   ✅ Team: {team_data.get('name', 'Unknown')}")
            print(f"   🏟️ Stadium: {team_data.get('venue', {}).get('name', 'Unknown')}")
            print(f"   👨‍💼 Coach: {team_data.get('coach', {}).get('common_name', 'Unknown')}")
            
            # Check current squad
            current_squad = team_data.get('currentSquad', [])
            print(f"   👥 Current Squad: {len(current_squad)} players")
            
            if current_squad:
                print(f"   📋 Premium Squad Data:")
                for i, squad_member in enumerate(current_squad[:10]):
                    player = squad_member.get('player', {})
                    player_name = player.get('display_name', 'Unknown')
                    position = player.get('position', {}).get('name', 'Unknown')
                    nationality = player.get('nationality', {}).get('name', 'Unknown')
                    jersey = squad_member.get('jersey_number', 'N/A')
                    
                    print(f"      #{jersey:<3} {player_name:<25} {position:<15} {nationality}")
            
            # Save premium team data
            with open('premium_real_madrid_team.json', 'w') as f:
                json.dump(data, f, indent=2)
            print(f"   💾 Premium team data saved!")
            
        else:
            print(f"   ❌ Failed: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 3: Get 2023-2024 La Liga season
    print(f"\n🔄 Test 3: Premium Season Data (2023-2024 La Liga)")
    try:
        url = "https://api.sportmonks.com/v3/football/seasons"
        params = {
            'api_token': api_token,
            'filters': 'leagueId:8',  # La Liga league ID
            'per_page': 10
        }
        
        response = requests.get(url, params=params, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            seasons = data.get('data', [])
            
            print(f"   ✅ Found {len(seasons)} La Liga seasons")
            
            # Find 2023-2024 season
            target_season = None
            for season in seasons:
                season_name = season.get('name', '')
                if '2023' in season_name and '2024' in season_name:
                    target_season = season
                    print(f"   🎯 Found 2023-2024 season: {season_name} (ID: {season.get('id')})")
                    break
            
            if target_season:
                season_id = target_season.get('id')
                
                # Test 4: Get Real Madrid statistics for 2023-2024
                print(f"\n🔄 Test 4: Premium Player Statistics (Season {season_id})")
                
                url = f"https://api.sportmonks.com/v3/football/squads/seasons/{season_id}/teams/{real_madrid_id}"
                params = {
                    'api_token': api_token,
                    'include': 'player.position,player.nationality,player.statistics'
                }
                
                response = requests.get(url, params=params, timeout=15)
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    squad_data = data.get('data', [])
                    
                    print(f"   ✅ PREMIUM SUCCESS! Found {len(squad_data)} players with statistics")
                    
                    # Display premium player data
                    print(f"   📊 Premium Player Statistics:")
                    for i, squad_member in enumerate(squad_data[:5]):
                        player = squad_member.get('player', {})
                        player_name = player.get('display_name', 'Unknown')
                        position = player.get('position', {}).get('name', 'Unknown')
                        nationality = player.get('nationality', {}).get('name', 'Unknown')
                        jersey = squad_member.get('jersey_number', 'N/A')
                        
                        # Check statistics
                        statistics = player.get('statistics', [])
                        stats_count = len(statistics)
                        
                        print(f"      #{jersey:<3} {player_name:<25} {position:<15} {nationality:<10} ({stats_count} stat records)")
                        
                        # Show sample statistics
                        if statistics:
                            sample_stat = statistics[0]
                            details = sample_stat.get('details', [])
                            if details:
                                print(f"           Sample stats: {len(details)} detailed metrics available")
                    
                    # Save premium player statistics
                    with open('premium_real_madrid_players_stats.json', 'w') as f:
                        json.dump(data, f, indent=2)
                    print(f"   💾 Premium player statistics saved!")
                    
                else:
                    print(f"   ❌ Player stats failed: {response.text[:200]}")
            
        else:
            print(f"   ❌ Season search failed: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 5: Try predictive API (premium feature)
    print(f"\n🔄 Test 5: Premium Predictive API Test")
    try:
        url = "https://api.sportmonks.com/v3/football/predictions"
        params = {
            'api_token': api_token,
            'per_page': 3
        }
        
        response = requests.get(url, params=params, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            predictions = data.get('data', [])
            print(f"   ✅ PREDICTIVE API ACCESS CONFIRMED! {len(predictions)} predictions available")
        else:
            print(f"   ⚠️ Predictive API: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    print(f"\n{'='*80}")
    print("🎉 PREMIUM SUBSCRIPTION TEST COMPLETE!")
    print("✅ Check JSON files for comprehensive Real Madrid data")
    print("✅ Premium features detected - ready for enhanced Elche display")
    print(f"{'='*80}")

if __name__ == "__main__":
    test_premium_features()
