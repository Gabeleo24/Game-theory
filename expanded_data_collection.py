#!/usr/bin/env python3
"""
Expanded Data Collection Strategy - Maximize Ultra Plan
Collect comprehensive multi-year, multi-league dataset for ADS599 Capstone
"""

import sys
import os
sys.path.append('src')

import json
import pandas as pd
from datetime import datetime
import time
import requests

class ExpandedCollector:
    """Expanded data collector to maximize Ultra plan usage."""
    
    def __init__(self):
        """Initialize expanded collector."""
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
        
        self.requests_used = 28  # Current count after first collection
        self.daily_limit = 75000
        
        print("🚀 EXPANDED DATA COLLECTION - MAXIMIZE ULTRA PLAN")
        print("=" * 70)
        print(f"📊 Starting with: {self.requests_used} requests used")
        print(f"🎯 Available: {self.daily_limit - self.requests_used:,} requests")
        print(f"🏆 Target: Comprehensive multi-year, multi-league dataset")
        print("=" * 70)
    
    def make_request(self, endpoint, params=None, description="API call"):
        """Make API request with tracking."""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            self.requests_used += 1
            remaining = self.daily_limit - self.requests_used
            
            print(f"   📡 {description} (Used: {self.requests_used}, Remaining: {remaining:,})")
            
            return response.json()
            
        except Exception as e:
            print(f"   ❌ Error in {description}: {e}")
            return None
    
    def collect_major_leagues_multi_year(self):
        """Collect major European leagues for multiple years."""
        print("\n🌍 MAJOR EUROPEAN LEAGUES - MULTI-YEAR COLLECTION")
        print("-" * 60)
        
        leagues = {
            'La Liga': {'id': 140, 'country': 'Spain'},
            'Premier League': {'id': 39, 'country': 'England'},
            'Serie A': {'id': 135, 'country': 'Italy'},
            'Bundesliga': {'id': 78, 'country': 'Germany'},
            'Ligue 1': {'id': 61, 'country': 'France'},
            'Champions League': {'id': 2, 'country': 'World'},
            'Europa League': {'id': 3, 'country': 'World'}
        }
        
        seasons = [2023, 2022, 2021, 2020, 2019]  # 5 years of data
        
        for league_name, league_info in leagues.items():
            if self.requests_used >= 10000:  # Safety limit
                print(f"⚠️  Stopping at {league_name} - safety limit reached")
                break
                
            print(f"\n🏆 Collecting {league_name} - Multi-Year Dataset")
            
            for season in seasons:
                if self.requests_used >= 10000:
                    break
                    
                print(f"📅 {league_name} {season} season...")
                
                # Teams
                teams_response = self.make_request('teams', 
                    {'league': league_info['id'], 'season': season},
                    f"{league_name} {season} teams")
                
                if teams_response and teams_response.get('response'):
                    teams = teams_response['response']
                    
                    safe_name = league_name.lower().replace(' ', '_')
                    filename = f'data/processed/{safe_name}_teams_{season}_expanded.json'
                    with open(filename, 'w') as f:
                        json.dump(teams, f, indent=2, default=str)
                    
                    print(f"      ✅ {len(teams)} teams saved")
                
                # Matches
                matches_response = self.make_request('fixtures',
                    {'league': league_info['id'], 'season': season},
                    f"{league_name} {season} matches")
                
                if matches_response and matches_response.get('response'):
                    matches = matches_response['response']
                    
                    safe_name = league_name.lower().replace(' ', '_')
                    filename = f'data/processed/{safe_name}_matches_{season}_expanded.json'
                    with open(filename, 'w') as f:
                        json.dump(matches, f, indent=2, default=str)
                    
                    print(f"      ✅ {len(matches)} matches saved")
                
                # Standings
                standings_response = self.make_request('standings',
                    {'league': league_info['id'], 'season': season},
                    f"{league_name} {season} standings")
                
                if standings_response and standings_response.get('response'):
                    standings = standings_response['response']
                    
                    safe_name = league_name.lower().replace(' ', '_')
                    filename = f'data/processed/{safe_name}_standings_{season}_expanded.json'
                    with open(filename, 'w') as f:
                        json.dump(standings, f, indent=2, default=str)
                    
                    print(f"      ✅ Standings saved")
                
                time.sleep(0.2)  # Rate limiting
    
    def collect_detailed_team_statistics_expanded(self):
        """Collect detailed statistics for top teams across leagues."""
        print("\n📊 DETAILED TEAM STATISTICS - EXPANDED COLLECTION")
        print("-" * 60)
        
        # Top teams from major leagues
        top_teams = [
            # La Liga
            {'id': 529, 'name': 'Barcelona', 'league': 140},
            {'id': 541, 'name': 'Real Madrid', 'league': 140},
            {'id': 530, 'name': 'Atletico Madrid', 'league': 140},
            {'id': 536, 'name': 'Sevilla', 'league': 140},
            {'id': 533, 'name': 'Villarreal', 'league': 140},
            
            # Premier League
            {'id': 50, 'name': 'Manchester City', 'league': 39},
            {'id': 33, 'name': 'Manchester United', 'league': 39},
            {'id': 40, 'name': 'Liverpool', 'league': 39},
            {'id': 42, 'name': 'Arsenal', 'league': 39},
            {'id': 49, 'name': 'Chelsea', 'league': 39},
            
            # Serie A
            {'id': 496, 'name': 'Juventus', 'league': 135},
            {'id': 489, 'name': 'AC Milan', 'league': 135},
            {'id': 505, 'name': 'Inter', 'league': 135},
            {'id': 487, 'name': 'AS Roma', 'league': 135},
            {'id': 492, 'name': 'Napoli', 'league': 135},
            
            # Bundesliga
            {'id': 157, 'name': 'Bayern Munich', 'league': 78},
            {'id': 165, 'name': 'Borussia Dortmund', 'league': 78},
            {'id': 173, 'name': 'RB Leipzig', 'league': 78},
            {'id': 168, 'name': 'Bayer Leverkusen', 'league': 78},
            
            # Ligue 1
            {'id': 85, 'name': 'Paris Saint Germain', 'league': 61},
            {'id': 81, 'name': 'Marseille', 'league': 61},
            {'id': 80, 'name': 'Lyon', 'league': 61}
        ]
        
        seasons = [2023, 2022, 2021]  # 3 years of detailed stats
        
        for season in seasons:
            if self.requests_used >= 20000:  # Safety limit
                print(f"⚠️  Stopping at season {season} - safety limit reached")
                break
                
            print(f"\n📈 Collecting detailed stats for {season} season...")
            season_stats = {}
            
            for team in top_teams:
                if self.requests_used >= 20000:
                    break
                    
                stats_response = self.make_request('teams/statistics', {
                    'league': team['league'],
                    'season': season,
                    'team': team['id']
                }, f"{team['name']} {season} stats")
                
                if stats_response and stats_response.get('response'):
                    season_stats[team['id']] = {
                        'name': team['name'],
                        'league': team['league'],
                        'statistics': stats_response['response']
                    }
                
                time.sleep(0.1)  # Rate limiting
            
            # Save season statistics
            filename = f'data/processed/detailed_team_statistics_{season}_expanded.json'
            with open(filename, 'w') as f:
                json.dump(season_stats, f, indent=2, default=str)
            
            print(f"   ✅ Detailed statistics saved for {len(season_stats)} teams in {season}")
    
    def collect_match_statistics_sample(self):
        """Collect detailed match statistics for key games."""
        print("\n⚽ DETAILED MATCH STATISTICS - KEY GAMES")
        print("-" * 60)
        
        # Load some matches to get fixture IDs
        try:
            with open('data/processed/la_liga_matches_2023_ultra.json', 'r') as f:
                la_liga_matches = json.load(f)
            
            with open('data/processed/champions_league_matches_2023_ultra.json', 'r') as f:
                cl_matches = json.load(f)
        except:
            print("   ⚠️  Match files not found, skipping detailed match stats")
            return
        
        # Select important matches (El Clasico, big games, etc.)
        important_matches = []
        
        # Find El Clasico and other big La Liga matches
        for match in la_liga_matches:
            home_team = match.get('teams', {}).get('home', {}).get('name', '')
            away_team = match.get('teams', {}).get('away', {}).get('name', '')
            
            # Key matchups
            big_teams = ['Real Madrid', 'Barcelona', 'Atletico Madrid', 'Sevilla']
            if any(team in home_team for team in big_teams) and any(team in away_team for team in big_teams):
                important_matches.append(match)
        
        # Add Champions League knockout matches
        for match in cl_matches[:50]:  # Sample of CL matches
            important_matches.append(match)
        
        print(f"🎯 Collecting detailed stats for {len(important_matches[:100])} key matches...")
        
        match_stats = {}
        
        for i, match in enumerate(important_matches[:100]):  # Limit to 100 matches
            if self.requests_used >= 25000:  # Safety limit
                print(f"   ⚠️  Stopping at match {i} - safety limit reached")
                break
                
            fixture_id = match.get('fixture', {}).get('id')
            if fixture_id:
                stats_response = self.make_request('fixtures/statistics',
                    {'fixture': fixture_id},
                    f"Match {fixture_id} statistics")
                
                if stats_response and stats_response.get('response'):
                    match_stats[fixture_id] = {
                        'match_info': match,
                        'statistics': stats_response['response']
                    }
            
            if i % 10 == 0:  # Progress update
                print(f"      📊 Processed {i} matches...")
            
            time.sleep(0.1)
        
        # Save match statistics
        with open('data/processed/detailed_match_statistics_expanded.json', 'w') as f:
            json.dump(match_stats, f, indent=2, default=str)
        
        print(f"   ✅ Detailed match statistics saved for {len(match_stats)} matches")
    
    def collect_additional_competitions(self):
        """Collect data from additional competitions."""
        print("\n🏆 ADDITIONAL COMPETITIONS")
        print("-" * 60)
        
        additional_leagues = {
            'Copa del Rey': {'id': 143, 'country': 'Spain'},
            'FA Cup': {'id': 45, 'country': 'England'},
            'Coppa Italia': {'id': 137, 'country': 'Italy'},
            'DFB Pokal': {'id': 81, 'country': 'Germany'},
            'UEFA Nations League': {'id': 5, 'country': 'World'},
            'World Cup': {'id': 1, 'country': 'World'}
        }
        
        seasons = [2023, 2022]
        
        for comp_name, comp_info in additional_leagues.items():
            if self.requests_used >= 30000:  # Safety limit
                print(f"⚠️  Stopping at {comp_name} - safety limit reached")
                break
                
            print(f"\n🏅 Collecting {comp_name}...")
            
            for season in seasons:
                if self.requests_used >= 30000:
                    break
                
                # Teams
                teams_response = self.make_request('teams',
                    {'league': comp_info['id'], 'season': season},
                    f"{comp_name} {season} teams")
                
                if teams_response and teams_response.get('response'):
                    teams = teams_response['response']
                    safe_name = comp_name.lower().replace(' ', '_')
                    filename = f'data/processed/{safe_name}_teams_{season}.json'
                    with open(filename, 'w') as f:
                        json.dump(teams, f, indent=2, default=str)
                    print(f"      ✅ {len(teams)} teams")
                
                # Matches
                matches_response = self.make_request('fixtures',
                    {'league': comp_info['id'], 'season': season},
                    f"{comp_name} {season} matches")
                
                if matches_response and matches_response.get('response'):
                    matches = matches_response['response']
                    safe_name = comp_name.lower().replace(' ', '_')
                    filename = f'data/processed/{safe_name}_matches_{season}.json'
                    with open(filename, 'w') as f:
                        json.dump(matches, f, indent=2, default=str)
                    print(f"      ✅ {len(matches)} matches")
                
                time.sleep(0.3)
    
    def generate_expanded_summary(self):
        """Generate comprehensive summary of expanded collection."""
        print(f"\n" + "=" * 70)
        print("🚀 EXPANDED COLLECTION SUMMARY - ULTRA PLAN MAXIMIZED")
        print("=" * 70)
        
        efficiency = (self.requests_used / self.daily_limit) * 100
        remaining = self.daily_limit - self.requests_used
        
        print(f"📊 Ultra Plan Usage Analysis:")
        print(f"   • Total requests used: {self.requests_used:,}")
        print(f"   • Remaining capacity: {remaining:,}")
        print(f"   • Efficiency: {efficiency:.2f}% of daily limit")
        print(f"   • Status: {'Excellent' if efficiency < 50 else 'High Volume'}")
        
        # Count collected files
        data_files = []
        total_size = 0
        
        if os.path.exists('data/processed'):
            for file in os.listdir('data/processed'):
                if file.endswith('.json'):
                    file_path = os.path.join('data/processed', file)
                    size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                    data_files.append((file, size))
                    total_size += size
        
        print(f"\n💾 Comprehensive Dataset Collected:")
        print(f"   • Total files: {len(data_files)}")
        print(f"   • Total size: {total_size:.2f} MB")
        print(f"   • Coverage: Multi-league, multi-year, comprehensive")
        
        # Categorize files
        leagues_covered = set()
        years_covered = set()
        
        for filename, _ in data_files:
            if 'la_liga' in filename:
                leagues_covered.add('La Liga')
            elif 'premier_league' in filename:
                leagues_covered.add('Premier League')
            elif 'serie_a' in filename:
                leagues_covered.add('Serie A')
            elif 'bundesliga' in filename:
                leagues_covered.add('Bundesliga')
            elif 'champions_league' in filename:
                leagues_covered.add('Champions League')
            
            for year in ['2023', '2022', '2021', '2020', '2019']:
                if year in filename:
                    years_covered.add(year)
        
        print(f"\n🏆 Dataset Coverage:")
        print(f"   • Leagues: {', '.join(sorted(leagues_covered))}")
        print(f"   • Years: {', '.join(sorted(years_covered, reverse=True))}")
        print(f"   • Data types: Teams, Matches, Standings, Statistics")
        
        print(f"\n🎯 Research Capabilities Unlocked:")
        print("   ✅ Multi-league comparative analysis")
        print("   ✅ Historical trend analysis (5+ years)")
        print("   ✅ Cross-competition performance studies")
        print("   ✅ Detailed team and match statistics")
        print("   ✅ Comprehensive Shapley value analysis")
        print("   ✅ Advanced tactical intelligence")
        
        print(f"\n📋 Perfect for ADS599 Capstone Research:")
        print("   • Comprehensive European football dataset")
        print("   • Multi-year trend analysis capabilities")
        print("   • Cross-league performance comparisons")
        print("   • Advanced statistical modeling data")
        print("   • Professional-grade research dataset")

def main():
    """Execute expanded data collection strategy."""
    start_time = datetime.now()
    
    print("🎯 Starting Expanded Data Collection...")
    
    # Ensure directories
    os.makedirs('data/processed', exist_ok=True)
    
    # Initialize collector
    collector = ExpandedCollector()
    
    try:
        # Phase 1: Major leagues multi-year
        collector.collect_major_leagues_multi_year()
        
        # Phase 2: Detailed team statistics
        if collector.requests_used < 25000:
            collector.collect_detailed_team_statistics_expanded()
        
        # Phase 3: Match statistics
        if collector.requests_used < 35000:
            collector.collect_match_statistics_sample()
        
        # Phase 4: Additional competitions
        if collector.requests_used < 45000:
            collector.collect_additional_competitions()
        
    except KeyboardInterrupt:
        print("\n⚠️  Collection interrupted by user")
    except Exception as e:
        print(f"\n❌ Collection error: {e}")
    
    # Final summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    collector.generate_expanded_summary()
    
    print(f"\n⏱️  Total Collection Duration: {duration}")
    print(f"🎉 EXPANDED COLLECTION COMPLETE!")
    print(f"🏆 World-class soccer intelligence dataset ready for ADS599 Capstone!")

if __name__ == "__main__":
    main()
