#!/usr/bin/env python3
"""
Collect sample soccer data to demonstrate the system capabilities.
"""

import sys
import os
sys.path.append('src')

import json
from datetime import datetime

def collect_la_liga_data():
    """Collect comprehensive La Liga data."""
    print("🏆 Collecting La Liga 2023 Season Data...")
    print("=" * 50)
    
    try:
        from soccer_intelligence.data_collection.api_football import APIFootballClient
        from soccer_intelligence.data_processing.data_cleaner import DataCleaner
        
        # Initialize client
        client = APIFootballClient()
        cleaner = DataCleaner()
        
        LA_LIGA_ID = 140
        SEASON = 2023
        
        # Collect teams
        print("📋 Collecting teams...")
        teams_data = client.get_teams(LA_LIGA_ID, SEASON)
        print(f"   ✅ Collected {len(teams_data)} teams")
        
        # Clean team data
        teams_df = cleaner.clean_team_data(teams_data)
        print(f"   🧹 Cleaned data: {len(teams_df)} valid teams")
        
        # Show sample teams
        print("\n📊 Sample La Liga Teams:")
        for _, team in teams_df.head(5).iterrows():
            print(f"   • {team['team_name']} (Founded: {team.get('team_founded', 'N/A')})")
        
        # Collect matches (limited sample)
        print("\n⚽ Collecting recent matches...")
        matches_data = client.get_matches(LA_LIGA_ID, SEASON)
        print(f"   ✅ Collected {len(matches_data)} matches")
        
        # Clean match data
        matches_df = cleaner.clean_match_data(matches_data)
        print(f"   🧹 Cleaned data: {len(matches_df)} valid matches")
        
        # Show sample matches
        print("\n📊 Sample Recent Matches:")
        for _, match in matches_df.head(3).iterrows():
            home_team = match['home_team_name']
            away_team = match['away_team_name']
            score = f"{match['home_goals']}-{match['away_goals']}"
            print(f"   • {home_team} vs {away_team}: {score}")
        
        # Collect standings
        print("\n🏆 Collecting league standings...")
        standings_data = client.get_standings(LA_LIGA_ID, SEASON)
        print(f"   ✅ Collected standings data")
        
        # Save processed data
        print("\n💾 Saving processed data...")
        
        # Save to JSON for easy access
        teams_df.to_json('data/processed/la_liga_teams_2023.json', orient='records', indent=2)
        matches_df.to_json('data/processed/la_liga_matches_2023.json', orient='records', indent=2)
        
        with open('data/processed/la_liga_standings_2023.json', 'w') as f:
            json.dump(standings_data, f, indent=2, default=str)
        
        print("   ✅ Data saved to data/processed/")
        
        return {
            'teams': teams_df,
            'matches': matches_df,
            'standings': standings_data
        }
        
    except Exception as e:
        print(f"❌ Error collecting La Liga data: {e}")
        return None

def collect_player_data():
    """Collect player statistics for top La Liga teams."""
    print("\n👥 Collecting Player Statistics...")
    print("=" * 50)
    
    try:
        from soccer_intelligence.data_collection.api_football import APIFootballClient
        from soccer_intelligence.data_processing.data_cleaner import DataCleaner
        
        client = APIFootballClient()
        cleaner = DataCleaner()
        
        # Top teams to collect player data for
        top_teams = [
            {'id': 529, 'name': 'Barcelona'},
            {'id': 530, 'name': 'Atletico Madrid'},
            {'id': 541, 'name': 'Real Madrid'}
        ]
        
        all_players = []
        
        for team in top_teams:
            print(f"\n📋 Collecting players for {team['name']}...")
            
            # Get team statistics (includes player data)
            team_stats = client.get_team_statistics(team['id'], 140, 2023)
            
            if team_stats:
                print(f"   ✅ Collected team statistics for {team['name']}")
                
                # Note: In a real implementation, you'd need to get individual player stats
                # For now, we'll create a sample structure
                sample_players = [
                    {
                        'player': {'id': f"{team['id']}_1", 'name': f"Player 1 ({team['name']})", 'age': 25},
                        'statistics': [{
                            'team': {'id': team['id'], 'name': team['name']},
                            'games': {'appearences': 20, 'minutes': 1800, 'rating': '7.5'},
                            'goals': {'total': 8, 'assists': 5},
                            'passes': {'total': 400, 'accuracy': 85}
                        }]
                    }
                ]
                
                all_players.extend(sample_players)
            
        # Clean player data
        if all_players:
            players_df = cleaner.clean_player_data(all_players)
            print(f"\n🧹 Cleaned player data: {len(players_df)} players")
            
            # Save player data
            players_df.to_json('data/processed/la_liga_players_2023.json', orient='records', indent=2)
            print("   ✅ Player data saved")
            
            return players_df
        
    except Exception as e:
        print(f"❌ Error collecting player data: {e}")
        return None

def collect_social_media_sample():
    """Collect sample social media data."""
    print("\n🐦 Collecting Social Media Data...")
    print("=" * 50)
    
    try:
        from soccer_intelligence.data_collection.social_media import SocialMediaCollector
        
        collector = SocialMediaCollector()
        
        if not collector.twitter_client:
            print("⚠️  Twitter client not available - skipping social media collection")
            return None
        
        # Collect mentions for top teams
        teams = ['Real Madrid', 'Barcelona', 'Atletico Madrid']
        social_data = {}
        
        for team in teams:
            print(f"📱 Collecting mentions for {team}...")
            try:
                mentions = collector.get_team_mentions(team, max_results=10)
                social_data[team] = mentions
                print(f"   ✅ Collected {len(mentions)} mentions")
            except Exception as e:
                print(f"   ⚠️  Rate limited or error for {team}: {e}")
                social_data[team] = []
        
        # Save social media data
        if any(social_data.values()):
            with open('data/processed/social_media_sample.json', 'w') as f:
                json.dump(social_data, f, indent=2, default=str)
            print("   ✅ Social media data saved")
        
        return social_data
        
    except Exception as e:
        print(f"❌ Error collecting social media data: {e}")
        return None

def generate_summary_report(data):
    """Generate a summary report of collected data."""
    print("\n📊 Data Collection Summary Report")
    print("=" * 50)
    
    if not data:
        print("❌ No data to summarize")
        return
    
    # Teams summary
    if 'teams' in data and data['teams'] is not None:
        teams_df = data['teams']
        print(f"🏟️  Teams: {len(teams_df)} La Liga teams collected")
        print(f"   • Average founding year: {teams_df['team_founded'].mean():.0f}")
        print(f"   • Teams with stadiums: {teams_df['venue_name'].notna().sum()}")
    
    # Matches summary
    if 'matches' in data and data['matches'] is not None:
        matches_df = data['matches']
        print(f"\n⚽ Matches: {len(matches_df)} matches collected")
        print(f"   • Total goals scored: {matches_df['total_goals'].sum()}")
        print(f"   • Average goals per match: {matches_df['total_goals'].mean():.2f}")
        print(f"   • High-scoring matches (>3 goals): {(matches_df['total_goals'] > 3).sum()}")
    
    # Cache summary
    try:
        from soccer_intelligence.data_collection.cache_manager import CacheManager
        cache_manager = CacheManager()
        cache_info = cache_manager.get_cache_info()
        
        print(f"\n💾 Cache: {cache_info['total_files']} files, {cache_info['total_size_mb']} MB")
        print("   • Automatic caching prevents repeated API calls")
        print("   • Data persisted for future analysis")
    except:
        pass
    
    print(f"\n✅ Data collection completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n🚀 Your Soccer Intelligence System is ready for analysis!")
    print("\nNext steps:")
    print("1. Run Shapley value analysis on the collected data")
    print("2. Use the RAG system for intelligent queries")
    print("3. Explore tactical analysis capabilities")
    print("4. Create visualizations and insights")

def main():
    """Main data collection workflow."""
    print("⚽ Soccer Intelligence System - Data Collection")
    print("=" * 60)
    print("Collecting comprehensive soccer data for analysis...")
    
    # Ensure directories exist
    os.makedirs('data/processed', exist_ok=True)
    
    # Collect all data
    data = {}
    
    # La Liga core data
    la_liga_data = collect_la_liga_data()
    if la_liga_data:
        data.update(la_liga_data)
    
    # Player data
    player_data = collect_player_data()
    if player_data is not None:
        data['players'] = player_data
    
    # Social media data
    social_data = collect_social_media_sample()
    if social_data:
        data['social_media'] = social_data
    
    # Generate summary
    generate_summary_report(data)

if __name__ == "__main__":
    main()
