#!/usr/bin/env python3
"""
FBref Data Collection Demo

Demonstrates how to collect data from FBref.com for the Soccer Intelligence System.
This script shows various data collection capabilities including:
- League tables
- Player statistics
- Team statistics
- Available leagues discovery
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.soccer_intelligence.data_collection.fbref import FBrefCollector
import pandas as pd
import time


def demo_league_discovery():
    """Demonstrate discovering available leagues"""
    print("=== FBref League Discovery Demo ===")
    
    collector = FBrefCollector(cache_dir="data/raw/fbref")
    
    try:
        print("Discovering available leagues...")
        leagues = collector.get_available_leagues()
        
        if leagues:
            print(f"\nFound {len(leagues)} leagues:")
            for i, league in enumerate(leagues[:10]):  # Show first 10
                print(f"{i+1:2d}. {league['name']} - {league['url']}")
            
            if len(leagues) > 10:
                print(f"... and {len(leagues) - 10} more leagues")
                
            # Save leagues list
            leagues_df = pd.DataFrame(leagues)
            collector.save_data(leagues_df, "available_leagues.csv")
            print(f"\nSaved leagues list to data/raw/fbref/available_leagues.csv")
            
        else:
            print("No leagues found")
            
    except Exception as e:
        print(f"Error in league discovery: {e}")
    finally:
        collector.close()


def demo_premier_league_data():
    """Demonstrate collecting Premier League data"""
    print("\n=== Premier League Data Collection Demo ===")
    
    collector = FBrefCollector(cache_dir="data/raw/fbref")
    premier_league_url = "/en/comps/9/Premier-League-Stats"
    
    try:
        # Get league table
        print("Collecting Premier League table...")
        table_df = collector.get_league_table(premier_league_url)
        
        if table_df is not None:
            print(f"League table collected: {len(table_df)} teams")
            print("\nTop 5 teams:")
            print(table_df.head()[['Squad', 'MP', 'W', 'D', 'L', 'Pts']].to_string(index=False))
            
            # Save league table
            collector.save_data(table_df, "premier_league_table_2024_25.csv")
            print("\nSaved league table to data/raw/fbref/premier_league_table_2024_25.csv")
        
        # Get player statistics
        print("\nCollecting Premier League player stats...")
        player_stats = collector.get_player_stats(premier_league_url, "stats")
        
        if player_stats is not None:
            print(f"Player stats collected: {len(player_stats)} players")
            
            # Show top scorers
            if 'Gls' in player_stats.columns:
                top_scorers = player_stats.nlargest(5, 'Gls')[['Player', 'Squad', 'Gls']]
                print("\nTop 5 scorers:")
                print(top_scorers.to_string(index=False))
            
            # Save player stats
            collector.save_data(player_stats, "premier_league_player_stats_2024_25.csv")
            print("\nSaved player stats to data/raw/fbref/premier_league_player_stats_2024_25.csv")
        
        # Get team statistics
        print("\nCollecting Premier League team stats...")
        team_stats = collector.get_team_stats(premier_league_url, "stats")
        
        if team_stats is not None:
            print(f"Team stats collected: {len(team_stats)} teams")
            
            # Save team stats
            collector.save_data(team_stats, "premier_league_team_stats_2024_25.csv")
            print("\nSaved team stats to data/raw/fbref/premier_league_team_stats_2024_25.csv")
            
    except Exception as e:
        print(f"Error in Premier League data collection: {e}")
    finally:
        collector.close()


def demo_la_liga_data():
    """Demonstrate collecting La Liga data"""
    print("\n=== La Liga Data Collection Demo ===")
    
    collector = FBrefCollector(cache_dir="data/raw/fbref")
    la_liga_url = "/en/comps/12/La-Liga-Stats"
    
    try:
        # Get league table
        print("Collecting La Liga table...")
        table_df = collector.get_league_table(la_liga_url)
        
        if table_df is not None:
            print(f"League table collected: {len(table_df)} teams")
            print("\nTop 5 teams:")
            print(table_df.head()[['Squad', 'MP', 'W', 'D', 'L', 'Pts']].to_string(index=False))
            
            # Save league table
            collector.save_data(table_df, "la_liga_table_2024_25.csv")
            print("\nSaved league table to data/raw/fbref/la_liga_table_2024_25.csv")
        
        # Get shooting statistics (more detailed stats)
        print("\nCollecting La Liga shooting stats...")
        shooting_stats = collector.get_player_stats(la_liga_url, "shooting")
        
        if shooting_stats is not None:
            print(f"Shooting stats collected: {len(shooting_stats)} players")
            
            # Save shooting stats
            collector.save_data(shooting_stats, "la_liga_shooting_stats_2024_25.csv")
            print("\nSaved shooting stats to data/raw/fbref/la_liga_shooting_stats_2024_25.csv")
            
    except Exception as e:
        print(f"Error in La Liga data collection: {e}")
    finally:
        collector.close()


def demo_multiple_stat_types():
    """Demonstrate collecting multiple types of statistics"""
    print("\n=== Multiple Statistics Types Demo ===")
    
    collector = FBrefCollector(cache_dir="data/raw/fbref")
    premier_league_url = "/en/comps/9/Premier-League-Stats"
    
    stat_types = ["stats", "shooting", "passing", "defense", "possession"]
    
    try:
        for stat_type in stat_types:
            print(f"\nCollecting {stat_type} statistics...")
            
            # Add delay between different stat types
            if stat_type != "stats":
                time.sleep(3)  # Extra delay between different stat types
            
            stats_df = collector.get_player_stats(premier_league_url, stat_type)
            
            if stats_df is not None:
                print(f"{stat_type.capitalize()} stats collected: {len(stats_df)} players")
                
                # Save stats
                filename = f"premier_league_{stat_type}_stats_2024_25.csv"
                collector.save_data(stats_df, filename)
                print(f"Saved to data/raw/fbref/{filename}")
            else:
                print(f"Failed to collect {stat_type} statistics")
                
    except Exception as e:
        print(f"Error in multiple stats collection: {e}")
    finally:
        collector.close()


def main():
    """Run all demos"""
    print("FBref Data Collection Demonstration")
    print("=" * 50)
    print("This demo will collect various types of football data from FBref.com")
    print("Data will be cached locally to avoid repeated requests")
    print("Please be patient as we respect FBref's servers with appropriate delays")
    print()
    
    # Create cache directory
    cache_dir = Path("data/raw/fbref")
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Run demos
        demo_league_discovery()
        demo_premier_league_data()
        demo_la_liga_data()
        demo_multiple_stat_types()
        
        print("\n" + "=" * 50)
        print("Demo completed successfully!")
        print(f"Check the data/raw/fbref/ directory for collected data files")
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo failed with error: {e}")


if __name__ == "__main__":
    main()
