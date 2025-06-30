#!/usr/bin/env python3
"""
Comprehensive Soccer Data Collection - Ultra Plan Strategy
Maximizes your 75,000 daily API requests for ADS599 Capstone research
"""

import sys
import os
sys.path.append('src')

import json
import pandas as pd
from datetime import datetime, timedelta
import time

def setup_collection():
    """Initialize data collection with progress tracking."""
    print("COMPREHENSIVE SOCCER DATA COLLECTION")
    print("Ultra Plan Strategy - 75,000 Daily Requests")
    print("=" * 60)
    
    try:
        from soccer_intelligence.data_collection.api_football import APIFootballClient
        from soccer_intelligence.data_processing.data_cleaner import DataCleaner
        
        client = APIFootballClient()
        cleaner = DataCleaner()
        
        if not client.api_key:
            print("API key not configured")
            return None, None
        
        print(f"API Client initialized with key: {client.api_key[:10]}...")
        print(f"Starting with 16 requests used, 74,984 remaining")
        
        return client, cleaner
        
    except Exception as e:
        print(f"Setup error: {e}")
        return None, None

def collect_la_liga_comprehensive(client, cleaner):
    """Collect comprehensive La Liga 2023 data."""
    print("\nPHASE 1: LA LIGA 2023 COMPREHENSIVE COLLECTION")
    print("=" * 60)
    
    LA_LIGA_ID = 140
    SEASON = 2023
    requests_used = 0
    
    try:
        # 1. League Information
        print("Collecting league information...")
        leagues = client.get_leagues(country="Spain")
        requests_used += 1
        print(f"   Spanish leagues collected (Requests: {requests_used})")
        
        # 2. Teams Data
        print("Collecting La Liga teams...")
        teams_data = client.get_teams(LA_LIGA_ID, SEASON)
        requests_used += 1
        print(f"   {len(teams_data)} teams collected (Requests: {requests_used})")
        
        # Clean and save teams
        teams_df = cleaner.clean_team_data(teams_data)
        teams_df.to_json('data/processed/la_liga_teams_2023_comprehensive.json', 
                        orient='records', indent=2)
        
        # 3. All Matches
        print("Collecting all La Liga matches...")
        matches_data = client.get_matches(LA_LIGA_ID, SEASON)
        requests_used += 1
        print(f"   {len(matches_data)} matches collected (Requests: {requests_used})")
        
        # Clean and save matches
        matches_df = cleaner.clean_match_data(matches_data)
        matches_df.to_json('data/processed/la_liga_matches_2023_comprehensive.json', 
                          orient='records', indent=2)
        
        # 4. League Standings
        print("Collecting league standings...")
        standings_data = client.get_standings(LA_LIGA_ID, SEASON)
        requests_used += 1
        print(f"   Standings collected (Requests: {requests_used})")
        
        with open('data/processed/la_liga_standings_2023.json', 'w') as f:
            json.dump(standings_data, f, indent=2, default=str)
        
        # 5. Team Statistics for All Teams
        print("Collecting detailed team statistics...")
        team_stats = {}
        
        for team in teams_data[:10]:  # Top 10 teams to manage requests
            team_id = team['team']['id']
            team_name = team['team']['name']
            
            print(f"   Collecting stats for {team_name}...")
            stats = client.get_team_statistics(team_id, LA_LIGA_ID, SEASON)
            team_stats[team_id] = stats
            requests_used += 1
            
            # Rate limiting
            time.sleep(0.5)
        
        print(f"   Team statistics collected (Requests: {requests_used})")
        
        with open('data/processed/la_liga_team_stats_2023.json', 'w') as f:
            json.dump(team_stats, f, indent=2, default=str)
        
        print(f"\nLa Liga Phase Complete - Requests Used: {requests_used}")
        return requests_used, teams_data, matches_data
        
    except Exception as e:
        print(f"La Liga collection error: {e}")
        return requests_used, [], []

def collect_champions_league(client, cleaner, requests_used):
    """Collect Champions League 2023 data."""
    print(f"\nPHASE 2: CHAMPIONS LEAGUE 2023 COLLECTION")
    print("=" * 60)
    
    CL_ID = 2
    SEASON = 2023
    phase_requests = 0
    
    try:
        # 1. Champions League Teams
        print("Collecting Champions League teams...")
        cl_teams_data = client.get_teams(CL_ID, SEASON)
        phase_requests += 1
        print(f"   {len(cl_teams_data)} CL teams collected")
        
        # 2. Champions League Matches
        print("Collecting Champions League matches...")
        cl_matches_data = client.get_matches(CL_ID, SEASON)
        phase_requests += 1
        print(f"   {len(cl_matches_data)} CL matches collected")
        
        # Clean and save
        cl_teams_df = cleaner.clean_team_data(cl_teams_data)
        cl_matches_df = cleaner.clean_match_data(cl_matches_data)
        
        cl_teams_df.to_json('data/processed/champions_league_teams_2023.json', 
                           orient='records', indent=2)
        cl_matches_df.to_json('data/processed/champions_league_matches_2023.json', 
                             orient='records', indent=2)
        
        # 3. Champions League Standings
        print("Collecting CL standings...")
        cl_standings = client.get_standings(CL_ID, SEASON)
        phase_requests += 1
        
        with open('data/processed/champions_league_standings_2023.json', 'w') as f:
            json.dump(cl_standings, f, indent=2, default=str)
        
        total_requests = requests_used + phase_requests
        print(f"\nChampions League Phase Complete - Total Requests: {total_requests}")
        
        return total_requests, cl_teams_data, cl_matches_data
        
    except Exception as e:
        print(f"Champions League collection error: {e}")
        return requests_used + phase_requests, [], []

def collect_historical_data(client, cleaner, requests_used):
    """Collect historical data for trend analysis."""
    print(f"\nPHASE 3: HISTORICAL DATA COLLECTION")
    print("=" * 60)
    
    LA_LIGA_ID = 140
    historical_seasons = [2022, 2021]
    phase_requests = 0
    
    try:
        for season in historical_seasons:
            print(f"Collecting La Liga {season} season...")
            
            # Teams for historical season
            historical_teams = client.get_teams(LA_LIGA_ID, season)
            phase_requests += 1
            
            # Sample of matches (to manage requests)
            historical_matches = client.get_matches(LA_LIGA_ID, season)
            phase_requests += 1
            
            # Clean and save
            teams_df = cleaner.clean_team_data(historical_teams)
            matches_df = cleaner.clean_match_data(historical_matches)
            
            teams_df.to_json(f'data/processed/la_liga_teams_{season}.json', 
                            orient='records', indent=2)
            matches_df.to_json(f'data/processed/la_liga_matches_{season}.json', 
                              orient='records', indent=2)
            
            print(f"   {season} season: {len(historical_teams)} teams, {len(historical_matches)} matches")
            
            # Rate limiting
            time.sleep(1)
        
        total_requests = requests_used + phase_requests
        print(f"\nHistorical Data Phase Complete - Total Requests: {total_requests}")
        
        return total_requests
        
    except Exception as e:
        print(f"Historical data collection error: {e}")
        return requests_used + phase_requests

def collect_detailed_match_statistics(client, matches_data, requests_used):
    """Collect detailed statistics for key matches."""
    print(f"\nPHASE 4: DETAILED MATCH STATISTICS")
    print("=" * 60)
    
    phase_requests = 0
    match_stats = {}
    
    try:
        # Select important matches (El Clasico, Madrid Derby, etc.)
        important_matches = []
        
        for match in matches_data[:20]:  # Top 20 matches to manage requests
            home_team = match.get('teams', {}).get('home', {}).get('name', '')
            away_team = match.get('teams', {}).get('away', {}).get('name', '')
            
            # Identify key matches
            key_teams = ['Real Madrid', 'Barcelona', 'Atletico Madrid', 'Sevilla']
            if any(team in home_team for team in key_teams) or any(team in away_team for team in key_teams):
                important_matches.append(match)
        
        print(f"Collecting detailed stats for {len(important_matches)} key matches...")
        
        for match in important_matches[:15]:  # Limit to manage requests
            fixture_id = match.get('fixture', {}).get('id')
            if fixture_id:
                stats = client.get_match_statistics(fixture_id)
                match_stats[fixture_id] = stats
                phase_requests += 1
                
                # Rate limiting
                time.sleep(0.3)
        
        # Save detailed match statistics
        with open('data/processed/detailed_match_statistics.json', 'w') as f:
            json.dump(match_stats, f, indent=2, default=str)
        
        total_requests = requests_used + phase_requests
        print(f"   Detailed statistics for {len(match_stats)} matches collected")
        print(f"\nMatch Statistics Phase Complete - Total Requests: {total_requests}")
        
        return total_requests
        
    except Exception as e:
        print(f"Match statistics collection error: {e}")
        return requests_used + phase_requests

def generate_collection_summary(total_requests):
    """Generate summary of data collection."""
    print(f"\n" + "=" * 60)
    print("COMPREHENSIVE DATA COLLECTION SUMMARY")
    print("=" * 60)
    
    print(f"Total API Requests Used: {total_requests}")
    print(f"Remaining Requests Today: {75000 - total_requests:,}")
    print(f"Request Efficiency: {(total_requests/75000)*100:.2f}% of daily limit")
    
    print(f"\nData Collected:")
    
    # Check what files were created
    data_files = []
    for root, dirs, files in os.walk('data/processed'):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path) / 1024  # KB
                data_files.append((file, file_size))
    
    for filename, size in data_files:
        print(f"   {filename}: {size:.1f} KB")
    
    total_size = sum(size for _, size in data_files)
    print(f"\nTotal Data Collected: {total_size:.1f} KB")
    
    print(f"\nReady for Analysis:")
    print("   • La Liga 2023 comprehensive dataset")
    print("   • Champions League 2023 data")
    print("   • Historical data for trend analysis")
    print("   • Detailed match statistics for key games")
    print("   • Team performance metrics")
    
    print(f"\nNext Steps:")
    print("   1. Run Shapley value analysis on collected data")
    print("   2. Perform tactical formation analysis")
    print("   3. Generate performance intelligence reports")
    print("   4. Create visualizations and insights")
    print("   5. Develop ADS599 Capstone findings")

def main():
    """Execute comprehensive data collection strategy."""
    start_time = datetime.now()
    
    # Setup
    client, cleaner = setup_collection()
    if not client:
        return
    
    # Ensure directories exist
    os.makedirs('data/processed', exist_ok=True)
    
    total_requests = 16  # Starting with 16 used
    
    # Phase 1: La Liga Comprehensive
    requests_used, teams_data, matches_data = collect_la_liga_comprehensive(client, cleaner)
    total_requests += requests_used
    
    # Phase 2: Champions League
    if total_requests < 1000:  # Safety check
        total_requests, cl_teams, cl_matches = collect_champions_league(client, cleaner, total_requests)
    
    # Phase 3: Historical Data
    if total_requests < 2000:  # Safety check
        total_requests = collect_historical_data(client, cleaner, total_requests)
    
    # Phase 4: Detailed Match Statistics
    if total_requests < 5000 and matches_data:  # Safety check
        total_requests = collect_detailed_match_statistics(client, matches_data, total_requests)
    
    # Summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    generate_collection_summary(total_requests)
    
    print(f"\nCollection Duration: {duration}")
    print(f"COMPREHENSIVE DATA COLLECTION COMPLETE!")
    print(f"Your ADS599 Capstone dataset is ready for advanced analysis!")

if __name__ == "__main__":
    main()
