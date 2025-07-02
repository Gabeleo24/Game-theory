#!/usr/bin/env python3
"""
Debug script to understand Champions League data structure
"""

import json
from pathlib import Path

def debug_standings_data():
    """Debug the standings data structure."""
    data_dir = Path('data/processed')
    standings_file = data_dir / 'champions_league_standings_2023_expanded.json'
    
    print("Debugging Champions League standings data...")
    
    if not standings_file.exists():
        print(f"File not found: {standings_file}")
        return
    
    with open(standings_file, 'r') as f:
        standings_data = json.load(f)
    
    print(f"Type of standings_data: {type(standings_data)}")
    print(f"Length: {len(standings_data)}")
    
    if standings_data:
        first_item = standings_data[0]
        print(f"\nFirst item keys: {first_item.keys()}")
        
        if 'league' in first_item:
            league = first_item['league']
            print(f"League keys: {league.keys()}")
            
            if 'standings' in league:
                standings = league['standings']
                print(f"Standings type: {type(standings)}")
                print(f"Standings length: {len(standings)}")
                
                if standings:
                    first_group = standings[0]
                    print(f"First group type: {type(first_group)}")
                    print(f"First group length: {len(first_group)}")
                    
                    if first_group:
                        first_team = first_group[0]
                        print(f"First team keys: {first_team.keys()}")
                        print(f"Team info: {first_team.get('team', {})}")
                        print(f"Group: {first_team.get('group', 'N/A')}")

def extract_teams_simple():
    """Simple extraction of teams from standings."""
    data_dir = Path('data/processed')
    teams_found = []
    
    for year in [2023, 2022, 2021]:
        standings_file = data_dir / f'champions_league_standings_{year}_expanded.json'
        
        if not standings_file.exists():
            print(f"File not found: {standings_file}")
            continue
            
        print(f"\nProcessing {year}...")
        
        with open(standings_file, 'r') as f:
            standings_data = json.load(f)
        
        for league_data in standings_data:
            if 'league' in league_data and 'standings' in league_data['league']:
                standings = league_data['league']['standings']
                
                for group in standings:
                    for team_standing in group:
                        if 'team' in team_standing and 'group' in team_standing:
                            team = team_standing['team']
                            group_name = team_standing['group']
                            
                            if 'Group' in str(group_name):
                                team_info = {
                                    'id': team['id'],
                                    'name': team['name'],
                                    'group': group_name,
                                    'year': year
                                }
                                teams_found.append(team_info)
                                print(f"   {team['name']} (ID: {team['id']}) - {group_name}")
    
    print(f"\nTotal teams found: {len(teams_found)}")
    
    # Count unique teams
    unique_teams = {}
    for team in teams_found:
        team_id = team['id']
        if team_id not in unique_teams:
            unique_teams[team_id] = team['name']
    
    print(f"Unique teams: {len(unique_teams)}")
    
    return teams_found, unique_teams

if __name__ == "__main__":
    debug_standings_data()
    print("\n" + "="*50)
    extract_teams_simple()
