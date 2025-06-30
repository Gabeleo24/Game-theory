#!/usr/bin/env python3
"""
Clean Data Collection Strategy - No Emojis
Professional soccer data collection for ADS599 Capstone research
"""

import sys
import os
sys.path.append('src')

import json
import pandas as pd
from datetime import datetime
import time
import requests

class CleanCollector:
    """Professional data collector without emoji characters."""
    
    def __init__(self):
        """Initialize clean collector."""
        # Load API key
        try:
            with open('config/api_keys.yaml', 'r') as f:
                import yaml
                config = yaml.safe_load(f)
                self.api_key = config['api_football']['key']
        except:
            self.api_key = "5ced20dec7f4b2226c8944c88c6d86aa"
        
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {
            'X-RapidAPI-Key': self.api_key,
            'X-RapidAPI-Host': 'v3.football.api-sports.io'
        }
        
        self.requests_used = 285  # Current count after expanded collection
        self.daily_limit = 75000
        
        print("PROFESSIONAL SOCCER DATA COLLECTION")
        print("=" * 60)
        print(f"API Key: {self.api_key[:10]}...")
        print(f"Daily Limit: {self.daily_limit:,} requests")
        print(f"Used: {self.requests_used} requests")
        print(f"Available: {self.daily_limit - self.requests_used:,} requests")
        print("=" * 60)
    
    def make_request(self, endpoint, params=None, description="API call"):
        """Make API request with tracking."""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            self.requests_used += 1
            remaining = self.daily_limit - self.requests_used
            
            print(f"   API call: {description} (Used: {self.requests_used}, Remaining: {remaining:,})")
            
            return response.json()
            
        except Exception as e:
            print(f"   Error in {description}: {e}")
            return None
    
    def collect_player_statistics(self):
        """Collect detailed player statistics for top teams."""
        print("\nCOLLECTING PLAYER STATISTICS")
        print("-" * 50)
        
        # Top teams for player data collection
        top_teams = [
            {'id': 529, 'name': 'Barcelona', 'league': 140},
            {'id': 541, 'name': 'Real Madrid', 'league': 140},
            {'id': 530, 'name': 'Atletico Madrid', 'league': 140},
            {'id': 50, 'name': 'Manchester City', 'league': 39},
            {'id': 40, 'name': 'Liverpool', 'league': 39},
            {'id': 157, 'name': 'Bayern Munich', 'league': 78},
            {'id': 496, 'name': 'Juventus', 'league': 135},
            {'id': 85, 'name': 'Paris Saint Germain', 'league': 61}
        ]
        
        seasons = [2023, 2022]
        all_player_data = {}
        
        for season in seasons:
            if self.requests_used >= 5000:  # Safety limit
                print(f"   Stopping at season {season} - safety limit reached")
                break
                
            print(f"\nCollecting player data for {season} season...")
            season_players = {}
            
            for team in top_teams:
                if self.requests_used >= 5000:
                    break
                    
                print(f"   Collecting players for {team['name']}...")
                
                # Get team squad
                squad_response = self.make_request('players/squads', {
                    'team': team['id']
                }, f"{team['name']} squad")
                
                if squad_response and squad_response.get('response'):
                    squad = squad_response['response']
                    
                    # Get player statistics for the season
                    players_response = self.make_request('players', {
                        'team': team['id'],
                        'season': season,
                        'league': team['league']
                    }, f"{team['name']} {season} players")
                    
                    if players_response and players_response.get('response'):
                        players = players_response['response']
                        season_players[team['id']] = {
                            'team_name': team['name'],
                            'squad': squad,
                            'player_stats': players
                        }
                        print(f"      Collected {len(players)} player records")
                
                time.sleep(0.2)  # Rate limiting
            
            # Save season player data
            all_player_data[season] = season_players
            filename = f'data/processed/player_statistics_{season}_clean.json'
            with open(filename, 'w') as f:
                json.dump(season_players, f, indent=2, default=str)
            
            print(f"   Player data saved for {len(season_players)} teams in {season}")
        
        return all_player_data
    
    def collect_additional_leagues(self):
        """Collect data from additional leagues."""
        print("\nCOLLECTING ADDITIONAL LEAGUES")
        print("-" * 50)
        
        additional_leagues = {
            'Primeira Liga': {'id': 94, 'country': 'Portugal'},
            'Eredivisie': {'id': 88, 'country': 'Netherlands'},
            'Belgian Pro League': {'id': 144, 'country': 'Belgium'},
            'Scottish Premiership': {'id': 179, 'country': 'Scotland'},
            'MLS': {'id': 253, 'country': 'USA'},
            'Brazilian Serie A': {'id': 71, 'country': 'Brazil'}
        }
        
        seasons = [2023, 2022]
        
        for league_name, league_info in additional_leagues.items():
            if self.requests_used >= 10000:  # Safety limit
                print(f"   Stopping at {league_name} - safety limit reached")
                break
                
            print(f"\nCollecting {league_name}...")
            
            for season in seasons:
                if self.requests_used >= 10000:
                    break
                
                # Teams
                teams_response = self.make_request('teams',
                    {'league': league_info['id'], 'season': season},
                    f"{league_name} {season} teams")
                
                if teams_response and teams_response.get('response'):
                    teams = teams_response['response']
                    safe_name = league_name.lower().replace(' ', '_')
                    filename = f'data/processed/{safe_name}_teams_{season}_clean.json'
                    with open(filename, 'w') as f:
                        json.dump(teams, f, indent=2, default=str)
                    print(f"      {len(teams)} teams saved")
                
                # Matches
                matches_response = self.make_request('fixtures',
                    {'league': league_info['id'], 'season': season},
                    f"{league_name} {season} matches")
                
                if matches_response and matches_response.get('response'):
                    matches = matches_response['response']
                    safe_name = league_name.lower().replace(' ', '_')
                    filename = f'data/processed/{safe_name}_matches_{season}_clean.json'
                    with open(filename, 'w') as f:
                        json.dump(matches, f, indent=2, default=str)
                    print(f"      {len(matches)} matches saved")
                
                time.sleep(0.3)
    
    def collect_injury_data(self):
        """Collect injury data for analysis."""
        print("\nCOLLECTING INJURY DATA")
        print("-" * 50)
        
        # Major leagues for injury data
        leagues = [140, 39, 135, 78, 61]  # La Liga, Premier League, Serie A, Bundesliga, Ligue 1
        
        for league_id in leagues:
            if self.requests_used >= 15000:  # Safety limit
                print(f"   Stopping at league {league_id} - safety limit reached")
                break
                
            print(f"   Collecting injuries for league {league_id}...")
            
            injuries_response = self.make_request('injuries', {
                'league': league_id,
                'season': 2023
            }, f"League {league_id} injuries")
            
            if injuries_response and injuries_response.get('response'):
                injuries = injuries_response['response']
                filename = f'data/processed/injuries_league_{league_id}_2023_clean.json'
                with open(filename, 'w') as f:
                    json.dump(injuries, f, indent=2, default=str)
                print(f"      {len(injuries)} injury records saved")
            
            time.sleep(0.5)
    
    def collect_transfer_data(self):
        """Collect transfer market data."""
        print("\nCOLLECTING TRANSFER DATA")
        print("-" * 50)
        
        # Top teams for transfer data
        top_teams = [529, 541, 530, 50, 40, 33, 157, 496, 85]  # Major European clubs
        
        for team_id in top_teams:
            if self.requests_used >= 20000:  # Safety limit
                print(f"   Stopping at team {team_id} - safety limit reached")
                break
                
            print(f"   Collecting transfers for team {team_id}...")
            
            transfers_response = self.make_request('transfers', {
                'team': team_id
            }, f"Team {team_id} transfers")
            
            if transfers_response and transfers_response.get('response'):
                transfers = transfers_response['response']
                filename = f'data/processed/transfers_team_{team_id}_clean.json'
                with open(filename, 'w') as f:
                    json.dump(transfers, f, indent=2, default=str)
                print(f"      {len(transfers)} transfer records saved")
            
            time.sleep(0.3)
    
    def generate_clean_summary(self):
        """Generate professional summary without emojis."""
        print(f"\n" + "=" * 70)
        print("PROFESSIONAL DATA COLLECTION SUMMARY")
        print("=" * 70)
        
        efficiency = (self.requests_used / self.daily_limit) * 100
        remaining = self.daily_limit - self.requests_used
        
        print(f"Ultra Plan Usage Analysis:")
        print(f"   Total requests used: {self.requests_used:,}")
        print(f"   Remaining capacity: {remaining:,}")
        print(f"   Efficiency: {efficiency:.2f}% of daily limit")
        print(f"   Status: {'Excellent' if efficiency < 50 else 'High Volume'}")
        
        # Count collected files
        data_files = []
        total_size = 0
        
        if os.path.exists('data/processed'):
            for file in os.listdir('data/processed'):
                if file.endswith('_clean.json'):
                    file_path = os.path.join('data/processed', file)
                    size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                    data_files.append((file, size))
                    total_size += size
        
        print(f"\nAdditional Clean Dataset:")
        print(f"   New files: {len(data_files)}")
        print(f"   Additional data: {total_size:.2f} MB")
        print(f"   Quality: Professional grade, no emoji characters")
        
        print(f"\nDataset Enhancement:")
        print("   - Player statistics for top teams")
        print("   - Additional league coverage")
        print("   - Injury data for analysis")
        print("   - Transfer market information")
        print("   - Clean, professional formatting")
        
        print(f"\nResearch Capabilities:")
        print("   - Comprehensive player performance analysis")
        print("   - Cross-league comparative studies")
        print("   - Injury impact on team performance")
        print("   - Transfer market analysis")
        print("   - Professional academic research quality")
        
        print(f"\nRemaining Capacity:")
        print(f"   {remaining:,} requests still available today")
        print("   Sufficient for additional specialized data collection")
        print("   Perfect for iterative research and analysis")

def main():
    """Execute clean data collection strategy."""
    start_time = datetime.now()
    
    print("Starting Professional Data Collection...")
    
    # Ensure directories
    os.makedirs('data/processed', exist_ok=True)
    
    # Initialize collector
    collector = CleanCollector()
    
    try:
        # Phase 1: Player statistics
        if collector.requests_used < 5000:
            collector.collect_player_statistics()
        
        # Phase 2: Additional leagues
        if collector.requests_used < 10000:
            collector.collect_additional_leagues()
        
        # Phase 3: Injury data
        if collector.requests_used < 15000:
            collector.collect_injury_data()
        
        # Phase 4: Transfer data
        if collector.requests_used < 20000:
            collector.collect_transfer_data()
        
    except KeyboardInterrupt:
        print("\nCollection interrupted by user")
    except Exception as e:
        print(f"\nCollection error: {e}")
    
    # Final summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    collector.generate_clean_summary()
    
    print(f"\nCollection Duration: {duration}")
    print("PROFESSIONAL DATA COLLECTION COMPLETE")
    print("Clean dataset ready for ADS599 Capstone analysis")

if __name__ == "__main__":
    main()
