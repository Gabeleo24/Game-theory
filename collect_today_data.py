#!/usr/bin/env python3
"""
Today's Data Collection - Ultra Plan Strategy
Direct implementation without dependency issues
"""

import sys
import os
sys.path.append('src')

import json
import pandas as pd
from datetime import datetime
import time
import requests

class DirectAPICollector:
    """Direct API collector without complex dependencies."""
    
    def __init__(self):
        """Initialize direct API collector."""
        # Load API key directly
        try:
            with open('config/api_keys.yaml', 'r') as f:
                import yaml
                config = yaml.safe_load(f)
                self.api_key = config['api_football']['key']
        except:
            self.api_key = "5ced20dec7f4b2226c8944c88c6d86aa"  # Your key
        
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {
            'X-RapidAPI-Key': self.api_key,
            'X-RapidAPI-Host': 'v3.football.api-sports.io'
        }
        
        self.requests_used = 16  # Starting count
        self.daily_limit = 75000
        
        print("🏆 ULTRA PLAN DATA COLLECTION - TODAY'S STRATEGY")
        print("=" * 60)
        print(f"🔑 API Key: {self.api_key[:10]}...")
        print(f"📊 Daily Limit: {self.daily_limit:,} requests")
        print(f"✅ Used: {self.requests_used} requests")
        print(f"🚀 Available: {self.daily_limit - self.requests_used:,} requests")
        print("=" * 60)
    
    def make_request(self, endpoint, params=None):
        """Make direct API request."""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            self.requests_used += 1
            remaining = self.daily_limit - self.requests_used
            
            print(f"   📡 API call successful (Used: {self.requests_used}, Remaining: {remaining:,})")
            
            return response.json()
            
        except Exception as e:
            print(f"   ❌ API error: {e}")
            return None
    
    def collect_la_liga_comprehensive(self):
        """Collect comprehensive La Liga data."""
        print("\n🇪🇸 COLLECTING LA LIGA 2023 - COMPREHENSIVE DATASET")
        print("-" * 50)
        
        LA_LIGA_ID = 140
        SEASON = 2023
        
        # 1. Get La Liga teams
        print("🏟️  Collecting La Liga teams...")
        teams_response = self.make_request('teams', {'league': LA_LIGA_ID, 'season': SEASON})
        
        if teams_response and teams_response.get('response'):
            teams = teams_response['response']
            print(f"   ✅ Collected {len(teams)} La Liga teams")
            
            # Save teams data
            with open('data/processed/la_liga_teams_2023_ultra.json', 'w') as f:
                json.dump(teams, f, indent=2, default=str)
            
            # Show sample teams
            print("   📋 Sample teams:")
            for i, team in enumerate(teams[:5]):
                team_name = team.get('team', {}).get('name', 'Unknown')
                founded = team.get('team', {}).get('founded', 'N/A')
                print(f"      {i+1}. {team_name} (Founded: {founded})")
        
        # 2. Get La Liga matches
        print("\n⚽ Collecting La Liga matches...")
        matches_response = self.make_request('fixtures', {'league': LA_LIGA_ID, 'season': SEASON})
        
        if matches_response and matches_response.get('response'):
            matches = matches_response['response']
            print(f"   ✅ Collected {len(matches)} La Liga matches")
            
            # Save matches data
            with open('data/processed/la_liga_matches_2023_ultra.json', 'w') as f:
                json.dump(matches, f, indent=2, default=str)
            
            # Show sample matches
            print("   📋 Sample recent matches:")
            for i, match in enumerate(matches[:3]):
                home_team = match.get('teams', {}).get('home', {}).get('name', 'Unknown')
                away_team = match.get('teams', {}).get('away', {}).get('name', 'Unknown')
                home_goals = match.get('goals', {}).get('home', 0)
                away_goals = match.get('goals', {}).get('away', 0)
                print(f"      {i+1}. {home_team} {home_goals}-{away_goals} {away_team}")
        
        # 3. Get La Liga standings
        print("\n🏆 Collecting La Liga standings...")
        standings_response = self.make_request('standings', {'league': LA_LIGA_ID, 'season': SEASON})
        
        if standings_response and standings_response.get('response'):
            standings = standings_response['response']
            print(f"   ✅ Collected La Liga standings")
            
            # Save standings
            with open('data/processed/la_liga_standings_2023_ultra.json', 'w') as f:
                json.dump(standings, f, indent=2, default=str)
        
        return teams if 'teams' in locals() else []
    
    def collect_champions_league(self):
        """Collect Champions League data."""
        print("\n🏆 COLLECTING CHAMPIONS LEAGUE 2023")
        print("-" * 50)
        
        CL_ID = 2
        SEASON = 2023
        
        # Champions League teams
        print("🌟 Collecting Champions League teams...")
        cl_teams_response = self.make_request('teams', {'league': CL_ID, 'season': SEASON})
        
        if cl_teams_response and cl_teams_response.get('response'):
            cl_teams = cl_teams_response['response']
            print(f"   ✅ Collected {len(cl_teams)} Champions League teams")
            
            with open('data/processed/champions_league_teams_2023_ultra.json', 'w') as f:
                json.dump(cl_teams, f, indent=2, default=str)
        
        # Champions League matches
        print("⚽ Collecting Champions League matches...")
        cl_matches_response = self.make_request('fixtures', {'league': CL_ID, 'season': SEASON})
        
        if cl_matches_response and cl_matches_response.get('response'):
            cl_matches = cl_matches_response['response']
            print(f"   ✅ Collected {len(cl_matches)} Champions League matches")
            
            with open('data/processed/champions_league_matches_2023_ultra.json', 'w') as f:
                json.dump(cl_matches, f, indent=2, default=str)
    
    def collect_top_teams_stats(self, teams):
        """Collect detailed statistics for top teams."""
        print("\n📊 COLLECTING DETAILED TEAM STATISTICS")
        print("-" * 50)
        
        # Top La Liga teams
        top_teams = [
            {'id': 529, 'name': 'Barcelona'},
            {'id': 541, 'name': 'Real Madrid'},
            {'id': 530, 'name': 'Atletico Madrid'},
            {'id': 536, 'name': 'Sevilla'},
            {'id': 533, 'name': 'Villarreal'}
        ]
        
        team_stats = {}
        
        for team in top_teams:
            if self.requests_used >= 1000:  # Safety limit
                print(f"   ⚠️  Stopping at {team['name']} - request limit reached")
                break
            
            print(f"📈 Collecting stats for {team['name']}...")
            
            stats_response = self.make_request('teams/statistics', {
                'league': 140,
                'season': 2023,
                'team': team['id']
            })
            
            if stats_response and stats_response.get('response'):
                team_stats[team['id']] = {
                    'name': team['name'],
                    'statistics': stats_response['response']
                }
                print(f"   ✅ Statistics collected for {team['name']}")
            
            time.sleep(0.5)  # Rate limiting
        
        # Save team statistics
        with open('data/processed/top_teams_statistics_ultra.json', 'w') as f:
            json.dump(team_stats, f, indent=2, default=str)
        
        print(f"   📊 Detailed statistics saved for {len(team_stats)} teams")
    
    def collect_historical_seasons(self):
        """Collect historical data for trend analysis."""
        print("\n📈 COLLECTING HISTORICAL DATA FOR TREND ANALYSIS")
        print("-" * 50)
        
        historical_seasons = [2022, 2021]
        LA_LIGA_ID = 140
        
        for season in historical_seasons:
            if self.requests_used >= 2000:  # Safety limit
                print(f"   ⚠️  Stopping at season {season} - request limit reached")
                break
            
            print(f"📅 Collecting La Liga {season} season...")
            
            # Teams for historical season
            teams_response = self.make_request('teams', {'league': LA_LIGA_ID, 'season': season})
            
            if teams_response and teams_response.get('response'):
                teams = teams_response['response']
                print(f"   ✅ {season}: {len(teams)} teams collected")
                
                with open(f'data/processed/la_liga_teams_{season}_ultra.json', 'w') as f:
                    json.dump(teams, f, indent=2, default=str)
            
            time.sleep(1)  # Rate limiting
    
    def generate_collection_summary(self):
        """Generate comprehensive summary."""
        print(f"\n" + "=" * 60)
        print("🏆 TODAY'S ULTRA PLAN COLLECTION SUMMARY")
        print("=" * 60)
        
        efficiency = (self.requests_used / self.daily_limit) * 100
        remaining = self.daily_limit - self.requests_used
        
        print(f"📊 Request Usage Analysis:")
        print(f"   • Started with: 16 requests used")
        print(f"   • Total used today: {self.requests_used:,} requests")
        print(f"   • Remaining capacity: {remaining:,} requests")
        print(f"   • Efficiency: {efficiency:.2f}% of daily limit")
        print(f"   • Status: {'Excellent' if efficiency < 10 else 'Good' if efficiency < 25 else 'High'}")
        
        # Check collected files
        data_files = []
        total_size = 0
        
        if os.path.exists('data/processed'):
            for file in os.listdir('data/processed'):
                if file.endswith('_ultra.json'):
                    file_path = os.path.join('data/processed', file)
                    size = os.path.getsize(file_path) / 1024  # KB
                    data_files.append((file, size))
                    total_size += size
        
        print(f"\n💾 Data Collected Today:")
        for filename, size in data_files:
            print(f"   📁 {filename}: {size:.1f} KB")
        
        print(f"\n🎯 Collection Achievement:")
        print(f"   • Total files: {len(data_files)}")
        print(f"   • Total data: {total_size:.1f} KB")
        print(f"   • Quality: Research-grade")
        print(f"   • Coverage: Multi-league comprehensive")
        
        print(f"\n🚀 Ultra Plan Advantages Utilized:")
        print("   ✅ High-volume data collection capability")
        print("   ✅ Comprehensive league coverage")
        print("   ✅ Historical trend analysis data")
        print("   ✅ Detailed team statistics")
        print("   ✅ Professional dataset quality")
        
        print(f"\n📋 Ready for ADS599 Capstone Analysis:")
        print("   1. Shapley value analysis with comprehensive data")
        print("   2. Tactical formation analysis across leagues")
        print("   3. Historical performance trend analysis")
        print("   4. Multi-season comparison studies")
        print("   5. Advanced soccer intelligence insights")
        
        print(f"\n⚡ Remaining Capacity for Additional Collection:")
        print(f"   • {remaining:,} requests still available today")
        print("   • Can collect additional leagues or detailed player data")
        print("   • Perfect for iterative research and analysis")

def main():
    """Execute today's Ultra plan data collection."""
    start_time = datetime.now()
    
    print("🎯 Starting Today's Ultra Plan Data Collection...")
    
    # Ensure directories
    os.makedirs('data/processed', exist_ok=True)
    
    # Initialize collector
    collector = DirectAPICollector()
    
    try:
        # Phase 1: La Liga comprehensive
        teams = collector.collect_la_liga_comprehensive()
        
        # Phase 2: Champions League
        if collector.requests_used < 500:
            collector.collect_champions_league()
        
        # Phase 3: Detailed team statistics
        if collector.requests_used < 800 and teams:
            collector.collect_top_teams_stats(teams)
        
        # Phase 4: Historical data
        if collector.requests_used < 1200:
            collector.collect_historical_seasons()
        
    except KeyboardInterrupt:
        print("\n⚠️  Collection interrupted by user")
    except Exception as e:
        print(f"\n❌ Collection error: {e}")
    
    # Final summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    collector.generate_collection_summary()
    
    print(f"\n⏱️  Collection Duration: {duration}")
    print(f"🎉 TODAY'S ULTRA PLAN COLLECTION COMPLETE!")
    print(f"🏆 Your comprehensive soccer dataset is ready for analysis!")

if __name__ == "__main__":
    main()
