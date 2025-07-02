#!/usr/bin/env python3
"""
Test FBref Collector

Simple test script to verify FBref data collection functionality
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.soccer_intelligence.data_collection.fbref import FBrefCollector


def test_basic_functionality():
    """Test basic FBref collector functionality"""
    print("Testing FBref Collector...")
    
    # Initialize collector
    collector = FBrefCollector(cache_dir="data/raw/fbref/test")
    
    try:
        # Test 1: Get available leagues
        print("\n1. Testing league discovery...")
        leagues = collector.get_available_leagues()
        
        if leagues:
            print(f"✓ Found {len(leagues)} leagues")
            print(f"Sample leagues: {[l['name'] for l in leagues[:3]]}")
        else:
            print("✗ No leagues found")
            return False
        
        # Test 2: Get Premier League table
        print("\n2. Testing Premier League table collection...")
        premier_league_url = "/en/comps/9/Premier-League-Stats"
        table_df = collector.get_league_table(premier_league_url)
        
        if table_df is not None and len(table_df) > 0:
            print(f"✓ Premier League table collected: {len(table_df)} teams")
            print(f"Columns: {list(table_df.columns)[:5]}...")
        else:
            print("✗ Failed to collect Premier League table")
            return False
        
        # Test 3: Get player stats
        print("\n3. Testing player stats collection...")
        player_stats = collector.get_player_stats(premier_league_url, "stats")
        
        if player_stats is not None and len(player_stats) > 0:
            print(f"✓ Player stats collected: {len(player_stats)} players")
            print(f"Columns: {list(player_stats.columns)[:5]}...")
        else:
            print("✗ Failed to collect player stats")
            return False
        
        print("\n✓ All tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        return False
    finally:
        collector.close()


if __name__ == "__main__":
    success = test_basic_functionality()
    if success:
        print("\nFBref collector is working correctly!")
    else:
        print("\nFBref collector test failed!")
        sys.exit(1)
