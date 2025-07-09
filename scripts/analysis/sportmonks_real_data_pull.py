#!/usr/bin/env python3
"""
SportMonks Real Data Pull - Get actual Real Madrid player data
"""

import requests
import yaml
import json
import time
from typing import Dict, List

def load_api_key():
    """Load SportMonks API key."""
    try:
        with open('config/api_keys.yaml', 'r') as f:
            config = yaml.safe_load(f)
        return config.get('sportmonks', {}).get('api_key')
    except Exception as e:
        print(f"❌ Error loading API key: {e}")
        return None

def get_real_madrid_squad(api_token: str) -> List[Dict]:
    """Get Real Madrid squad with player details."""
    
    print("🔄 Getting Real Madrid squad...")
    
    # Get squad data
    url = "https://api.sportmonks.com/v3/football/squads/teams/496"
    params = {'api_token': api_token, 'per_page': 50}
    
    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code != 200:
            print(f"❌ Failed to get squad: {response.status_code}")
            return []
        
        data = response.json()
        squad_data = data.get('data', [])
        print(f"✅ Found {len(squad_data)} squad members")
        
        return squad_data
        
    except Exception as e:
        print(f"❌ Error getting squad: {e}")
        return []

def get_player_details(api_token: str, player_id: int) -> Dict:
    """Get detailed player information."""
    
    url = f"https://api.sportmonks.com/v3/football/players/{player_id}"
    params = {
        'api_token': api_token,
        'include': 'position,nationality'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('data', {})
        else:
            print(f"   ⚠️ Failed to get player {player_id}: {response.status_code}")
            return {}
    except Exception as e:
        print(f"   ❌ Error getting player {player_id}: {e}")
        return {}

def get_player_statistics(api_token: str, player_id: int, season_id: int = None) -> Dict:
    """Get player statistics for a season."""
    
    url = f"https://api.sportmonks.com/v3/football/players/{player_id}/statistics"
    params = {'api_token': api_token}
    
    if season_id:
        params['filters'] = f'seasonId:{season_id}'
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('data', [])
        else:
            return []
    except Exception as e:
        return []

def process_real_madrid_data():
    """Process Real Madrid data from SportMonks API."""
    
    api_token = load_api_key()
    if not api_token:
        return
    
    print(f"\n{'='*80}")
    print("SPORTMONKS REAL MADRID DATA PULL")
    print(f"{'='*80}")
    
    # Get squad
    squad_data = get_real_madrid_squad(api_token)
    if not squad_data:
        print("❌ Could not get squad data")
        return
    
    # Process each player
    enhanced_players = []
    print(f"\n🔄 Processing {len(squad_data)} players...")
    
    for i, squad_member in enumerate(squad_data):
        player_id = squad_member.get('player_id')
        jersey_number = squad_member.get('jersey_number')
        position_id = squad_member.get('position_id')
        
        if not player_id:
            continue
        
        print(f"   Processing player {i+1}/{len(squad_data)} (ID: {player_id})...")
        
        # Get player details
        player_details = get_player_details(api_token, player_id)
        
        if player_details:
            player_name = player_details.get('display_name', player_details.get('name', f'Player_{player_id}'))
            birth_date = player_details.get('date_of_birth')
            nationality = player_details.get('nationality', {}).get('name', 'Unknown')
            position = player_details.get('position', {}).get('name', 'Unknown')
            height = player_details.get('height')
            weight = player_details.get('weight')
            
            # Get statistics
            statistics = get_player_statistics(api_token, player_id)
            
            enhanced_player = {
                'player_id': player_id,
                'jersey_number': jersey_number,
                'name': player_name,
                'birth_date': birth_date,
                'nationality': nationality,
                'position': position,
                'height': height,
                'weight': weight,
                'position_id': position_id,
                'statistics': statistics,
                'squad_info': squad_member
            }
            
            enhanced_players.append(enhanced_player)
            print(f"   ✅ {player_name} ({nationality}, {position})")
        
        # Rate limiting
        time.sleep(0.2)
        
        # Stop after 10 players for testing
        if i >= 9:
            print(f"   🛑 Stopping after {i+1} players for testing...")
            break
    
    # Save results
    result = {
        'team': 'Real Madrid',
        'team_id': 496,
        'collection_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'players_count': len(enhanced_players),
        'players': enhanced_players
    }
    
    filename = 'sportmonks_real_madrid_enhanced.json'
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n{'='*80}")
    print("RESULTS:")
    print(f"✅ Processed {len(enhanced_players)} players")
    print(f"💾 Data saved to {filename}")
    print(f"{'='*80}")
    
    # Display sample
    print(f"\nSAMPLE PLAYERS:")
    print("-" * 80)
    for player in enhanced_players[:5]:
        name = player.get('name', 'Unknown')
        nationality = player.get('nationality', 'Unknown')
        position = player.get('position', 'Unknown')
        jersey = player.get('jersey_number', 'N/A')
        birth_date = player.get('birth_date', 'Unknown')
        
        print(f"#{jersey:<3} {name:<25} {nationality:<15} {position:<15} {birth_date}")
    
    print(f"\n🎉 SUCCESS! Real Madrid data pulled from SportMonks API")
    print(f"📊 This data can now be integrated into the Elche display")

if __name__ == "__main__":
    process_real_madrid_data()
