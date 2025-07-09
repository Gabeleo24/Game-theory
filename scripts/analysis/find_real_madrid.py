#!/usr/bin/env python3
"""
Find Real Madrid team ID in SportMonks API
"""

import requests
import yaml
import json

def find_real_madrid():
    """Find the correct Real Madrid team ID."""
    
    # Load API key
    try:
        with open('config/api_keys.yaml', 'r') as f:
            config = yaml.safe_load(f)
        api_token = config.get('sportmonks', {}).get('api_key')
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return
    
    print(f"🔍 SEARCHING FOR REAL MADRID IN SPORTMONKS")
    print(f"{'='*60}")
    
    # Search through multiple pages of teams
    found_teams = []
    
    for page in range(1, 6):  # Search first 5 pages
        print(f"\n🔄 Searching page {page}...")
        
        try:
            url = "https://api.sportmonks.com/v3/football/teams"
            params = {
                'api_token': api_token,
                'per_page': 50,
                'page': page
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                print(f"   ❌ Page {page} failed: {response.status_code}")
                continue
            
            data = response.json()
            teams = data.get('data', [])
            
            print(f"   📊 Checking {len(teams)} teams...")
            
            # Look for Real Madrid variations
            madrid_keywords = ['real madrid', 'madrid', 'real', 'merengues']
            
            for team in teams:
                team_name = team.get('name', '').lower()
                team_id = team.get('id')
                country_id = team.get('country_id')
                
                # Check if it matches Real Madrid
                for keyword in madrid_keywords:
                    if keyword in team_name:
                        found_teams.append({
                            'id': team_id,
                            'name': team.get('name'),
                            'country_id': country_id,
                            'founded': team.get('founded'),
                            'venue_id': team.get('venue_id')
                        })
                        print(f"   🎯 FOUND: {team.get('name')} (ID: {team_id}, Country: {country_id})")
                        break
            
        except Exception as e:
            print(f"   ❌ Error on page {page}: {e}")
    
    print(f"\n{'='*60}")
    print(f"🏆 SEARCH RESULTS: Found {len(found_teams)} potential matches")
    print(f"{'='*60}")
    
    # Display all found teams
    for i, team in enumerate(found_teams):
        print(f"{i+1}. {team['name']}")
        print(f"   ID: {team['id']}")
        print(f"   Country ID: {team['country_id']}")
        print(f"   Founded: {team['founded']}")
        print(f"   Venue ID: {team['venue_id']}")
        print()
    
    # Test the most likely candidates
    likely_candidates = [team for team in found_teams if 'real madrid' in team['name'].lower()]
    
    if likely_candidates:
        print(f"🎯 TESTING MOST LIKELY CANDIDATES:")
        print(f"{'='*60}")
        
        for candidate in likely_candidates:
            team_id = candidate['id']
            team_name = candidate['name']
            
            print(f"\n🔄 Testing {team_name} (ID: {team_id})...")
            
            try:
                # Test squad endpoint
                url = f"https://api.sportmonks.com/v3/football/squads/teams/{team_id}"
                params = {'api_token': api_token, 'per_page': 30}
                
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    squad = data.get('data', [])
                    
                    print(f"   ✅ Squad found: {len(squad)} players")
                    
                    # Show sample players
                    for j, player in enumerate(squad[:3]):
                        player_id = player.get('player_id')
                        jersey = player.get('jersey_number', 'N/A')
                        print(f"      Player {j+1}: ID={player_id}, Jersey={jersey}")
                    
                    # Save this candidate's data
                    filename = f'candidate_{team_name.replace(" ", "_").lower()}_{team_id}.json'
                    with open(filename, 'w') as f:
                        json.dump(data, f, indent=2)
                    print(f"   💾 Data saved to {filename}")
                    
                else:
                    print(f"   ❌ Squad test failed: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error testing {team_name}: {e}")
    
    # Save all found teams
    with open('all_madrid_teams_found.json', 'w') as f:
        json.dump(found_teams, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"✅ SEARCH COMPLETE!")
    print(f"📁 All results saved to all_madrid_teams_found.json")
    print(f"🎯 Check the candidate files to find the real Real Madrid")
    print(f"{'='*60}")

if __name__ == "__main__":
    find_real_madrid()
