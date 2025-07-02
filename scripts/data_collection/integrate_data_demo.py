#!/usr/bin/env python3
"""
Data Integration Demo

Demonstrates how to integrate FBref and API-Football data for comprehensive analysis
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.soccer_intelligence.data_processing.data_integrator import DataIntegrator
import pandas as pd


def demo_premier_league_integration():
    """Demonstrate Premier League data integration"""
    print("=== Premier League Data Integration Demo ===")
    
    integrator = DataIntegrator(cache_dir="data/processed/integrated")
    
    try:
        # Integrate Premier League data
        print("Integrating Premier League data from API-Football and FBref...")
        integrated_data = integrator.integrate_league_data("Premier League", season=2024)
        
        if integrated_data:
            print(f"✓ Integration successful!")
            
            # Display team data
            if 'teams' in integrated_data:
                teams_df = integrated_data['teams']
                print(f"\nTeam data: {len(teams_df)} teams")
                print("Columns:", list(teams_df.columns))
                
                # Show top 5 teams with integrated data
                print("\nTop 5 teams with integrated data:")
                display_cols = ['Rk', 'Squad', 'Pts', 'xG', 'xGA', 'api_football_team_id', 'venue_name']
                available_cols = [col for col in display_cols if col in teams_df.columns]
                print(teams_df.head()[available_cols].to_string(index=False))
            
            # Display player data
            if 'players' in integrated_data:
                players_df = integrated_data['players']
                print(f"\nPlayer data: {len(players_df)} players")
                print("Columns:", list(players_df.columns)[:10], "...")
                
                # Show top scorers with enhanced metrics
                if 'goal_contribution' in players_df.columns:
                    top_contributors = players_df.nlargest(5, 'goal_contribution')
                    display_cols = ['Player', 'Squad', 'Gls', 'Ast', 'goal_contribution', 'xG', 'xAG']
                    available_cols = [col for col in display_cols if col in top_contributors.columns]
                    print(f"\nTop 5 goal contributors:")
                    print(top_contributors[available_cols].to_string(index=False))
            
            # Display metadata
            if 'metadata' in integrated_data:
                metadata = integrated_data['metadata']
                print(f"\nIntegration metadata:")
                print(f"  League: {metadata.get('league')}")
                print(f"  Season: {metadata.get('season')}")
                print(f"  Sources: {metadata.get('sources')}")
                print(f"  Integration date: {metadata.get('integration_date')}")
        
        else:
            print("✗ Integration failed")
            
    except Exception as e:
        print(f"✗ Integration error: {e}")


def demo_multiple_leagues():
    """Demonstrate integration for multiple leagues"""
    print("\n=== Multiple Leagues Integration Demo ===")
    
    integrator = DataIntegrator(cache_dir="data/processed/integrated")
    
    leagues = ["Premier League", "La Liga"]  # Start with 2 leagues for demo
    
    for league in leagues:
        print(f"\nIntegrating {league}...")
        try:
            integrated_data = integrator.integrate_league_data(league, season=2024)
            
            if integrated_data and 'teams' in integrated_data:
                teams_count = len(integrated_data['teams'])
                players_count = len(integrated_data['players']) if 'players' in integrated_data else 0
                print(f"✓ {league}: {teams_count} teams, {players_count} players")
            else:
                print(f"✗ {league}: Integration failed")
                
        except Exception as e:
            print(f"✗ {league}: Error - {e}")


def demo_load_integrated_data():
    """Demonstrate loading previously integrated data"""
    print("\n=== Loading Integrated Data Demo ===")
    
    integrator = DataIntegrator(cache_dir="data/processed/integrated")
    
    try:
        # Try to load Premier League data
        print("Loading previously integrated Premier League data...")
        data = integrator.get_integrated_data("Premier League", season=2024)
        
        if data:
            print("✓ Successfully loaded integrated data")
            
            for key, df in data.items():
                if isinstance(df, pd.DataFrame):
                    print(f"  {key}: {len(df)} records")
                else:
                    print(f"  {key}: metadata")
        else:
            print("✗ No previously integrated data found")
            
    except Exception as e:
        print(f"✗ Error loading data: {e}")


def analyze_integration_quality():
    """Analyze the quality of integrated data"""
    print("\n=== Integration Quality Analysis ===")
    
    integrator = DataIntegrator(cache_dir="data/processed/integrated")
    
    try:
        data = integrator.get_integrated_data("Premier League", season=2024)
        
        if not data or 'teams' not in data:
            print("✗ No team data available for analysis")
            return
        
        teams_df = data['teams']
        
        print("Data quality metrics:")
        print(f"  Total teams: {len(teams_df)}")
        print(f"  Teams with API-Football ID: {teams_df['api_football_team_id'].notna().sum()}")
        print(f"  Teams with venue info: {teams_df['venue_name'].notna().sum()}")
        print(f"  Teams with xG data: {teams_df['xG'].notna().sum()}")
        
        # Check for missing data
        missing_data = teams_df.isnull().sum()
        print(f"\nMissing data by column:")
        for col, missing_count in missing_data.items():
            if missing_count > 0:
                print(f"  {col}: {missing_count} missing values")
        
        # Data completeness score
        total_cells = len(teams_df) * len(teams_df.columns)
        missing_cells = missing_data.sum()
        completeness = ((total_cells - missing_cells) / total_cells) * 100
        print(f"\nData completeness: {completeness:.1f}%")
        
    except Exception as e:
        print(f"✗ Error analyzing integration quality: {e}")


def main():
    """Run all integration demos"""
    print("Data Integration Demonstration")
    print("=" * 50)
    print("This demo shows how to integrate FBref and API-Football data")
    print("Note: Requires valid API-Football API key in config")
    print()
    
    try:
        # Run demos
        demo_premier_league_integration()
        demo_multiple_leagues()
        demo_load_integrated_data()
        analyze_integration_quality()
        
        print("\n" + "=" * 50)
        print("Integration demo completed!")
        print("Check data/processed/integrated/ for integrated datasets")
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo failed with error: {e}")


if __name__ == "__main__":
    main()
